"""Schritt 00: Ein minimaler FastMCP-Server ohne Komponenten."""

from fastmcp import FastMCP

mcp = FastMCP(
    "Workshop 00 - Minimaler Server",
    instructions="Dieser Server demonstriert zunächst nur Protokoll und Transport.",
)


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000, path="/mcp")
