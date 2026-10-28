import os
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from mcp.server.fastmcp import FastMCP

BASE_URL = os.getenv("OXIONAI_BASE_URL", "https://www.oxionai.com/v1").rstrip("/")
API_KEY = os.getenv("OXIONAI_API_KEY", "")
MCP_ACCESS_TOKEN = os.getenv("MCP_ACCESS_TOKEN", "")

mcp = FastMCP("Oxion AI", stateless_http=True, json_response=True)

@mcp.tool()
async def list_models() -> dict:
    """List models available through the configured Oxion AI API key."""
    if not API_KEY:
        return {"error": "Server is missing OXIONAI_API_KEY. Add it in Render Environment settings."}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            f"{BASE_URL}/models",
            headers={"Authorization": f"Bearer {API_KEY}"},
        )
        response.raise_for_status()
        return response.json()

@mcp.tool()
async def chat_completion(message: str, model: str = "auto", system_prompt: str = "You are a helpful assistant.") -> dict:
    """Send a text prompt to Oxion AI. Use model='auto' to let the provider choose a model."""
    if not API_KEY:
        return {"error": "Server is missing OXIONAI_API_KEY. Add it in Render Environment settings."}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ],
    }
    async with httpx.AsyncClient(timeout=90) as client:
        response = await client.post(
            f"{BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json=payload,
        )
        response.raise_for_status()
        return response.json()

mcp_app = mcp.streamable_http_app()
app = FastAPI()

@app.get("/")
async def root():
    return {"name": "Oxion AI MCP bridge", "status": "running", "mcp_endpoint": "/mcp"}

@app.get("/health")
async def health():
    return {"ok": True, "api_key_configured": bool(API_KEY), "access_token_configured": bool(MCP_ACCESS_TOKEN)}

@app.middleware("http")
async def require_access_token(request: Request, call_next):
    if request.url.path in ("/", "/health"):
        return await call_next(request)
    if not MCP_ACCESS_TOKEN:
        return JSONResponse({"error": "Server not configured securely: set MCP_ACCESS_TOKEN."}, status_code=503)
    auth = request.headers.get("authorization", "")
    if auth != f"Bearer {MCP_ACCESS_TOKEN}":
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    return await call_next(request)

app.mount("/", mcp_app)
