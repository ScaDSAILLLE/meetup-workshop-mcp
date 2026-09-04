"""Schritt 01: Ein erstes, ausschließlich lesendes Tool."""

from fastmcp import FastMCP

mcp = FastMCP("Workshop 01 - Erstes Tool")


@mcp.tool(name="begruesse", annotations={"readOnlyHint": True, "openWorldHint": False})
def begrüsse(name: str) -> str:
    """Begrüße eine Person, ohne Daten zu speichern oder externe Systeme aufzurufen."""
    bereinigter_name = name.strip()
    if not bereinigter_name:
        raise ValueError("Der Name darf nicht leer sein.")
    if len(bereinigter_name) > 80:
        raise ValueError("Der Name darf höchstens 80 Zeichen lang sein.")
    return f"Hallo, {bereinigter_name}! Willkommen beim FastMCP-Workshop."


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8001, path="/mcp")
