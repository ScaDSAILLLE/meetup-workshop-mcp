"""Schritt 05: Wiederverwendbare MCP-Prompts."""

from fastmcp import FastMCP

mcp = FastMCP("Workshop 05 - Prompts")


@mcp.prompt
def tool_review(tool_name: str, ziel: str) -> str:
    """Erzeuge einen Prüfauftrag für das Design eines MCP-Tools."""
    return f"""Prüfe das MCP-Tool „{tool_name}“ mit dem Ziel „{ziel}“.

Bewerte in dieser Reihenfolge:
1. eindeutiger Name und verständliche Beschreibung,
2. präzise Ein- und Ausgabetypen,
3. minimale Berechtigungen und passende Tool-Annotationen,
4. Validierung, Fehlerfälle und Datenschutz.

Nenne zuerst konkrete Risiken und danach höchstens drei Verbesserungen."""


@mcp.prompt
def lernreflexion(schritt: str, beobachtung: str) -> str:
    """Erzeuge eine kurze Reflexion zu einem Workshop-Schritt."""
    return (
        f"Im Workshop-Schritt „{schritt}“ wurde Folgendes beobachtet: {beobachtung}\n\n"
        "Erkläre, welches MCP-Konzept sichtbar wurde, und formuliere eine Anschlussfrage."
    )


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8005, path="/mcp")
