# FastMCP Workshop

Diese Sammlung enthält verschiedene FastMCP-Beispiele und -Tutorials zum Erstellen eigener MCP-Server.

## Setup

1. **Repository klonen:**
   ```bash
   git clone https://github.com/ScaDSAILLLL/meetup-workshop-mcp.git
   cd meetup-workshop-mcp
   ```

2. **Umgebung einrichten:**
   ```bash
   uv sync
   ```

3. **In den FastMCP-Ordner wechseln:**
   ```bash
   cd fastmcp
   ```

## Verfügbare Skripte

- `00_greeting_mcp.py` - Einfacher Begrüßungsserver
- `01_hello_fastmcp.py` - Hello World Beispiel
- `02_erste_funktion.py` - Erste eigene Funktion
- `03_persönliche_daten.py` - Umgang mit persönlichen Daten
- `04_dynamische_resources.py` - Dynamische Ressourcen
- `05_intelligente_prompts.py` - Intelligente Prompt-Verarbeitung
- `06_persönlicher_assistent.py` - Vollständiger persönlicher Assistent

## MCP-Server in Langflow einbinden

### 1. Server starten
Führe eines der Python-Skripte aus:
```bash
uv run 00_greeting_mcp.py
```
Im Terminal wird die Server-URL angezeigt (z.B. `http://localhost:8764/sse`).

### 2. In Langflow konfigurieren
1. **MCP-Komponente hinzufügen** in Langflow
2. **"Server hinzufügen"** klicken
3. **"SSE"** als Transport auswählen
4. **Namen vergeben** (beliebig)
5. **Server-URL einfügen** aus dem Terminal (wichtig: auf `/sse` am Ende achten!)
6. **Kurz warten** bis Verbindung hergestellt ist
7. **Schalter oben rechts auf "tool" setzen**
8. **Per Drag & Drop mit Agent verbinden**

## Beispiel: Einfacher Greeting Server

```python
from fastmcp import FastMCP

mcp = FastMCP("Greeting Server")

@mcp.tool
def greet(name: str) -> str:
    "Return a short greeting."
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8765)
```

## Troubleshooting

- **Keine Verbindung zum Server oder keine Tools sichtbar:**
  - Prüfen, ob der Server im richtigen Modus läuft (`sse`)
  - Server-URL korrekt kopiert (mit `/sse` am Ende)
  - Bei MCP-Komponente "Refresh" klicken

## Weitere Informationen

Ausführliche Anleitungen zur MCP-Konfiguration und Integration findest du im Obsidian Vault dieses Repositories.