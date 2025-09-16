# FastMCP Workshop

Diese Sammlung enthält verschiedene FastMCP-Beispiele und -Tutorials zum Erstellen eigener MCP-Server.

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
Führe eines der Python-Skripte aus. Im Terminal wird die Server-URL angezeigt (z.B. `http://localhost:8764/sse`).

### 2. In Langflow konfigurieren
1. **MCP-Komponente hinzufügen** in Langflow
2. **"Server hinzufügen"** klicken
3. **"SSE"** als Transport auswählen
4. **Namen vergeben** (beliebig)
5. **Server-URL einfügen** aus dem Terminal (wichtig: auf `/sse` am Ende achten!)
6. **Kurz warten** bis Verbindung hergestellt ist
7. **Schalter oben rechts auf "tool" setzen**
8. **Per Drag & Drop mit Agent verbinden**

## Weitere Informationen

Ausführliche Anleitungen zur MCP-Konfiguration und Integration findest du im Obsidian Vault dieses Repositories.