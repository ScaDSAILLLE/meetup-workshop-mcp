"""Schritt 02: Mehrere klar beschriebene, lesende Tools."""

from fastmcp import FastMCP

mcp = FastMCP(
    "Workshop 02 - Weitere Tools",
    instructions="Nutze die Tools für kleine, deterministische Aufgaben.",
)


@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": False})
def addiere(a: float, b: float) -> float:
    """Addiere zwei Zahlen."""
    return a + b


@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": False})
def celsius_in_fahrenheit(celsius: float) -> float:
    """Rechne eine Temperatur von Grad Celsius in Grad Fahrenheit um."""
    return round(celsius * 9 / 5 + 32, 2)


@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": False})
def workshop_empfehlung(erfahrung: str) -> str:
    """Empfehle anhand von Anfänger, Fortgeschritten oder Profi den nächsten Lernschritt."""
    empfehlungen = {
        "anfänger": "Starte mit Tools und achte auf Namen, Typen und Docstrings.",
        "fortgeschritten": "Vergleiche Tools, Resources und Resource Templates.",
        "profi": "Untersuche Berechtigungen, Lebenszyklen und produktive Deployments.",
    }
    stufe = erfahrung.strip().lower()
    if stufe not in empfehlungen:
        raise ValueError("Erlaubt sind: Anfänger, Fortgeschritten, Profi.")
    return empfehlungen[stufe]


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8002, path="/mcp")
