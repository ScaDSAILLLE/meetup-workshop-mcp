"""Schritt 03: Statische Resources als lesbarer Kontext."""

import json

from fastmcp import FastMCP

mcp = FastMCP("Workshop 03 - Statische Resources")

WORKSHOP_INFO = {
    "titel": "FastMCP in der Praxis",
    "datum": "2026-09-03",
    "ort": "Fiktives Workshop-Labor",
    "dauer_minuten": 120,
}


@mcp.resource("workshop://info", mime_type="application/json")
def workshop_info() -> str:
    """Liefere die unveränderlichen Eckdaten des Workshops als JSON."""
    return json.dumps(WORKSHOP_INFO, ensure_ascii=False)


@mcp.resource("workshop://agenda", mime_type="text/markdown")
def workshop_agenda() -> str:
    """Liefere die statische Kurzagenda des Workshops."""
    return "# Agenda\n\n1. Tools\n2. Resources\n3. Resource Templates\n4. Prompts\n"


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8003, path="/mcp")
