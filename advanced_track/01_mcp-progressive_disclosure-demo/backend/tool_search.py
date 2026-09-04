"""Deterministische Stichwortsuche für die progressive Tool-Auswahl.

Deutsche Suchwörter werden um englische Katalogbegriffe ergänzt. Nur Treffer
mit positiver Punktzahl werden nach Punktzahl und Toolname sortiert; eine
unbekannte Anfrage liefert daher keine beliebigen Tools zurück.
"""

import re

STOP_WORDS = {
    "am",
    "an",
    "auf",
    "der",
    "die",
    "das",
    "ein",
    "eine",
    "für",
    "im",
    "in",
    "ist",
    "mir",
    "und",
    "von",
    "wie",
    "zu",
}


# Brücke zwischen deutschen Anfragen und den technischen Toolnamen.
KEYWORD_MAP: dict[str, list[str]] = {
    "wetter": ["weather"],
    "kunde": ["customer"],
    "kunden": ["customer"],
    "bestellung": ["order"],
    "bestellungen": ["order"],
    "auftrag": ["order"],
    "rechnung": ["invoice"],
    "abrechnung": ["invoice"],
    "finanzen": ["finance"],
    "finanziell": ["finance"],
    "temperatur": ["temperature"],
    "luftfeuchtigkeit": ["humidity"],
    "regen": ["precipitation", "rain"],
    "prognose": ["forecast"],
    "steuer": ["tax"],
    "zahlung": ["payment"],
    "bilanz": ["balance"],
    "einkommen": ["income"],
    "ausgaben": ["expenses"],
    "cashflow": ["cash_flow"],
    "datenbank": ["database"],
    "speicher": ["storage"],
    "speicherplatz": ["storage"],
    "warteschlange": ["queue"],
    "dokument": ["document"],
    "benachrichtigung": ["notify"],
    "verschlüsseln": ["encrypt"],
    "entschlüsseln": ["decrypt"],
    "importieren": ["import"],
    "exportieren": ["export"],
    "metriken": ["metrics"],
    "alarm": ["alert"],
    "warnung": ["alert"],
    "warnungen": ["alert"],
    "suche": ["search"],
    "bericht": ["report"],
    "analyse": ["analyze"],
    "erstellen": ["create"],
    "löschen": ["delete"],
    "aktualisieren": ["update"],
    "lieferung": ["deliver", "ship"],
    "stornieren": ["cancel"],
    "qualität": ["quality"],
    "konfiguration": ["config"],
    "neustarten": ["restart"],
    "anhalten": ["pause"],
    "fortsetzen": ["resume"],
    "überwachen": ["monitor"],
    "prüfen": ["check"],
    "validieren": ["validate"],
    "synchronisieren": ["sync"],
    "bereitstellen": ["deploy"],
    "optimieren": ["optimize"],
    "komprimieren": ["compress"],
    "bereinigen": ["clean"],
    "rotieren": ["rotate"],
    "verschmelzen": ["merge"],
    "kommunikation": ["communication"],
    "historie": ["history"],
    "statistiken": ["statistics"],
    "produktpalette": ["inventory"],
}


def _tokenize(text: str) -> list[str]:
    """Zerlegt Text in relevante kleingeschriebene Wörter."""
    return [
        token
        for token in re.findall(r"[a-zäöüß0-9]+", text.lower())
        if token not in STOP_WORDS
    ]


def _expand_tokens(tokens: list[str]) -> list[str]:
    """Ergänzt deutsche Wörter um passende englische Katalogbegriffe."""
    expanded = list(tokens)
    for token in tokens:
        if token in KEYWORD_MAP:
            expanded.extend(KEYWORD_MAP[token])
    return expanded


def search(
    query: str,
    tools: list[dict],
    top_k: int = 5,
) -> list[dict]:
    """Liefert bis zu ``top_k`` Katalogtreffer mit positiver Punktzahl."""
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    query_tokens = _expand_tokens(query_tokens)

    tool_map = {t["name"]: t for t in tools}
    scores: dict[str, float] = {}

    for qt in query_tokens:
        for tool_name in _get_matching_tools(qt, tools):
            scores[tool_name] = scores.get(tool_name, 0) + 1

    ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    return [tool_map[name] for name, _ in ranked[:top_k]]


def _get_matching_tools(query_token: str, tools: list[dict]) -> list[str]:
    """Liefert Toolnamen, in deren Name oder Beschreibung das Wort vorkommt."""
    matches = []
    for tool in tools:
        name = tool.get("name", "").lower()
        desc = tool.get("description", "").lower()
        if query_token in name or query_token in desc:
            matches.append(tool["name"])
    return matches
