"""Schritt 06: Tools, Resources, Templates und Prompts in einem Server."""

import json
from copy import deepcopy
from datetime import date

from fastmcp import FastMCP

mcp = FastMCP(
    "Workshop 06 - Kombinierter Assistent",
    instructions=(
        "Alle Daten sind fiktiv. Schreiboperationen verändern nur den flüchtigen "
        "Arbeitsspeicher und gehen beim Neustart verloren."
    ),
)

START_AUFGABEN = [
    {
        "id": 1,
        "titel": "Resource Template ausprobieren",
        "status": "offen",
        "deadline": "2026-09-04",
    },
    {
        "id": 2,
        "titel": "Workshop-Notizen ordnen",
        "status": "erledigt",
        "deadline": "2026-09-03",
    },
]
AUFGABEN = deepcopy(START_AUFGABEN)


def _gültiges_datum(wert: str) -> str:
    try:
        return date.fromisoformat(wert).isoformat()
    except ValueError as exc:
        raise ValueError("Das Datum muss dem Format YYYY-MM-DD entsprechen.") from exc


@mcp.resource("assistent://hinweise", mime_type="text/markdown")
def hinweise() -> str:
    """Beschreibe Herkunft, Fiktionalität und Lebensdauer der Demo-Daten."""
    return (
        "# Demo-Hinweise\n\nAlle Namen und Aufgaben sind fiktiv. Änderungen werden nicht "
        "persistiert und sind nach dem Neustart verworfen."
    )


@mcp.resource("aufgaben://{status}", mime_type="application/json")
def aufgaben_nach_status(status: str) -> str:
    """Liefere fiktive Aufgaben mit dem Status offen oder erledigt."""
    status_key = status.strip().lower()
    if status_key not in {"offen", "erledigt"}:
        raise ValueError("Der Status muss offen oder erledigt sein.")
    treffer = [aufgabe for aufgabe in AUFGABEN if aufgabe["status"] == status_key]
    return json.dumps(treffer, ensure_ascii=False)


@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": False})
def suche_aufgaben(suchbegriff: str) -> list[dict[str, int | str]]:
    """Durchsuche die fiktiven Aufgaben, ohne Daten zu verändern."""
    begriff = suchbegriff.strip().lower()
    if not begriff:
        raise ValueError("Der Suchbegriff darf nicht leer sein.")
    return [deepcopy(aufgabe) for aufgabe in AUFGABEN if begriff in str(aufgabe["titel"]).lower()]


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    }
)
def neue_aufgabe(titel: str, deadline: str) -> dict[str, int | str]:
    """Lege nach Validierung eine nicht persistente, fiktive Aufgabe im Speicher an."""
    bereinigter_titel = titel.strip()
    if not bereinigter_titel or len(bereinigter_titel) > 120:
        raise ValueError("Der Titel muss zwischen 1 und 120 Zeichen lang sein.")
    aufgabe = {
        "id": max((int(a["id"]) for a in AUFGABEN), default=0) + 1,
        "titel": bereinigter_titel,
        "status": "offen",
        "deadline": _gültiges_datum(deadline),
    }
    AUFGABEN.append(aufgabe)
    return deepcopy(aufgabe)


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def aufgabe_erledigen(aufgaben_id: int, bestätigen: bool = False) -> dict[str, int | str]:
    """Markiere eine flüchtige Aufgabe erst nach expliziter Bestätigung als erledigt."""
    if not bestätigen:
        raise ValueError("Die Änderung erfordert bestätigen=true.")
    for aufgabe in AUFGABEN:
        if aufgabe["id"] == aufgaben_id:
            aufgabe["status"] = "erledigt"
            return deepcopy(aufgabe)
    raise ValueError(f"Keine Aufgabe mit ID {aufgaben_id} gefunden.")


@mcp.prompt
def tagesplanung(datum: str) -> str:
    """Erzeuge einen Planungsauftrag für die fiktiven offenen Aufgaben."""
    gültiges_datum = _gültiges_datum(datum)
    offene_titel = [str(a["titel"]) for a in AUFGABEN if a["status"] == "offen"]
    return (
        f"Erstelle für {gültiges_datum} einen realistischen Plan für diese fiktiven Aufgaben: "
        f"{', '.join(offene_titel) or 'keine'}. Plane Pausen ein und markiere Annahmen."
    )


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8006, path="/mcp")
