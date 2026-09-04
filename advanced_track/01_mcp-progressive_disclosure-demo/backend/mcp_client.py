"""In-Memory-MCP-Client für Katalogabfrage und Tool-Ausführung."""

from fastmcp import Client

from mcp_server.server import mcp


def _tool_to_dict(tool) -> dict:
    """Überführt ein FastMCP-Tool in das Schemaformat des LLM-Clients."""
    return {
        "name": tool.name,
        "description": tool.description or "",
        "parameters": tool.inputSchema if hasattr(tool, "inputSchema") else {},
    }


async def list_all_tools() -> list[dict]:
    """Liest alle aktuell registrierten Tools dynamisch vom MCP-Server."""
    client = Client(mcp)
    async with client:
        tools = await client.list_tools()
        return [_tool_to_dict(t) for t in tools]


async def call_tool(name: str, arguments: dict) -> dict:
    """Ruft ein MCP-Tool auf und normalisiert dessen strukturiertes Ergebnis."""
    client = Client(mcp)
    async with client:
        result = await client.call_tool(name, arguments)
        if hasattr(result, "structured_content") and result.structured_content:
            return result.structured_content
        if hasattr(result, "content") and result.content:
            for block in result.content:
                if hasattr(block, "text"):
                    return {"text": block.text}
        return {}
