# Oxion AI ChatGPT MCP bridge

A small private MCP bridge for Oxion AI's OpenAI-compatible API.

## Render environment variables
- `OXIONAI_API_KEY`: secret key from Oxion AI dashboard (never commit this).
- `OXIONAI_BASE_URL`: `https://www.oxionai.com/v1`
- `MCP_ACCESS_TOKEN`: separate long random secret used as Bearer token to protect the MCP endpoint.

## Endpoint
- Health: `/health`
- MCP Streamable HTTP: `/mcp`

The MCP client must send `Authorization: Bearer <MCP_ACCESS_TOKEN>`. Never put the Oxion AI key in the MCP client.
