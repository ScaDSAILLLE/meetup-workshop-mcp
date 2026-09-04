"""Schritt 04: Parametrisierte Resources mit URI-Templates."""

import json

from fastmcp import FastMCP

mcp = FastMCP("Workshop 04 - Resource Templates")

# Sämtliche Personen und Inhalte in diesem Beispiel sind frei erfunden.
NOTIZEN = {
    "mira": {
        "vorbereitung": "Inspector installieren und Transport prüfen.",
        "übung": "Ein eigenes lesendes Tool ergänzen.",
    },
    "jonas": {
        "vorbereitung": "Python und uv installieren.",
        "übung": "Eine Resource mit eigener URI ergänzen.",
    },
}


@mcp.resource("notizen://{person}/{thema}", mime_type="application/json")
def notiz(person: str, thema: str) -> str:
    """Liefere eine fiktive Notiz für eine Person und ein Thema."""
    person_key = person.strip().lower()
    thema_key = thema.strip().lower()
    inhalt = NOTIZEN.get(person_key, {}).get(thema_key)
    ergebnis = {"person": person_key, "thema": thema_key, "inhalt": inhalt}
    return json.dumps(ergebnis, ensure_ascii=False)


@mcp.resource("termine://2026-09/{tag}", mime_type="application/json")
def workshop_termin(tag: str) -> str:
    """Liefere für einen Tag im September 2026 einen fiktiven Workshop-Termin."""
    if not tag.isdigit() or not 1 <= int(tag) <= 30:
        raise ValueError("Der Tag muss zwischen 1 und 30 liegen.")
    termin = {"datum": f"2026-09-{int(tag):02d}", "status": "fiktive Demo"}
    return json.dumps(termin, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8004, path="/mcp")
