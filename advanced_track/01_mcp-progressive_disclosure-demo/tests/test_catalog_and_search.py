"""Offline-Prüfungen für MCP-Katalog und deterministische Suche."""

from backend.mcp_client import list_all_tools
from backend.tool_search import search


async def test_catalog_count_is_loaded_from_mcp_server():
    tools = await list_all_tools()
    assert len(tools) == 101
    assert len({tool["name"] for tool in tools}) == len(tools)


def test_german_search_finds_weather_tools():
    tools = [
        {"name": "get_weather", "description": "Current weather", "parameters": {}},
        {"name": "get_invoice", "description": "Invoice details", "parameters": {}},
    ]
    assert [tool["name"] for tool in search("Wetter in Leipzig", tools)] == ["get_weather"]


def test_search_returns_empty_list_for_no_match():
    tools = [{"name": "get_weather", "description": "Current weather", "parameters": {}}]
    assert search("Quantenlyrik", tools) == []
