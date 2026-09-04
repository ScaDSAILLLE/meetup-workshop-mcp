# Setup und Ausführung

Diese Kurzreferenz ergänzt den geführten Workshop in [README.md](README.md).

## Voraussetzungen

- Python 3.14 oder neuer
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
- Browser
- für den Live-Lauf: persönlicher ScaDS/TUD:AI API-Key

## Konfiguration

Verwende ausschließlich die `.env` in der Repository-Wurzel. Die ebenfalls dort liegende
`.env.example` dokumentiert diese drei Variablen:

```dotenv
SCADS_API_KEY=dein-persönlicher-key
SCADS_BASE_URL=https://llm.scads.ai/v1
SCADS_MODEL=Qwen/Qwen3.8-27B
```

Es gibt keine track-lokale Env-Datei und keine alten Variablennamen als Fallback.

## Installation und Offline-Prüfung

Führe alle Befehle in `advanced_track/01_mcp-progressive_disclosure-demo/` aus:

```bash
uv sync --link-mode copy
uv run pytest
uv run ruff check .
```

Die Tests lesen keine Zugangsdaten und rufen keinen externen Endpoint auf.

## Live-Start

Der folgende Schritt verwendet die Root-Konfiguration und ist credential-abhängig:

```bash
uv run python -m backend.main
```

Öffne <http://127.0.0.1:8080>. Das Backend liefert Frontend und API aus und bindet den FastMCP-
Server im selben Prozess ein. Ein zweites Terminal oder separater MCP-Server ist nicht erforderlich.

## API

`POST /api/demo` erwartet:

```json
{"message": "Wie ist das Wetter in Leipzig?"}
```

Die Antwort besitzt die Modi `normal` und `progressiv`. Jeder Modus enthält dynamische Toolzahlen,
Metriken und typisierte Schritte:

```json
{
  "normal": {
    "available_tool_count": 101,
    "initial_visible_tool_count": 101,
    "selected_candidate_count": 0,
    "metrics": {
      "schema_tokens_sent": 12345,
      "endpoint_input_tokens": 13000,
      "endpoint_output_tokens": 80,
      "llm_calls": 2
    },
    "steps": [{"type": "catalog_loaded", "tool_count": 101}]
  }
}
```

Die Zahlen sind nur ein Formbeispiel. Die Anwendung ermittelt Toolzahl und Messwerte zur Laufzeit.
Fehlende Endpoint-Usage-Werte werden als `null` ausgegeben.

## Häufige Fehler

**Root-Konfiguration fehlt:** Prüfe die Root-`.env` anhand der Root-`.env.example`.

**HTTP 401/403:** Prüfe Key und Berechtigung, ohne den Key auszugeben.

**HTTP 429:** Warte auf das Ende des Rate-Limit-Zeitfensters und starte keine parallelen Läufe.

**Port 8080 belegt:** Beende den anderen lokalen Prozess und starte das Backend erneut.

**Hardlink-Fehler unter WSL:** Verwende `uv sync --link-mode copy`.
