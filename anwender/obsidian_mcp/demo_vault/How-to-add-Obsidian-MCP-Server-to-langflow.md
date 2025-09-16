# How to add Obsidian MCP Server to Langflow

### Step-by-Step Guide

1. Obsidian öffnen
2. Vorhandenen Vault öffnen > Demo_Vault auswählen
3. Einstellungen > Community Plugins > Turn On Community-Plugins
4. Community Plugins durchsuchen: Local REST API
5. Local REST API installieren und aktivieren
6. Local REST API Optionen öffnen
7. API Key notieren
8. Langflow öffnen
9. MCP Server Komponente hinzufügen
10. Server auswählen
11. MCP Server hinzufügen auswählen
12. Folgendes in die json config kopieren:

{
  "mcpServers": {
    "mcp-obsidian": {
      "command": "uvx",
      "args": [
        "mcp-obsidian"
      ],
      "env": {
        "OBSIDIAN_API_KEY": "<YOUR_Local_REST_API_API_KEY>",
        "OBSIDIAN_HOST": "127.0.0.1",
        "OBSIDIAN_PORT": "27124"
      }
    }
  }
} 

13. Local REST API Key einfügen
14. Server hinzufügen klicken
15. Für die Komponente den Tool Modus aktivieren
16. Toolset mit Tools Schnittstelle des Agenten verbinden
17. Oben rechts den Playground öffnen und im Chat ausprovieren:

Fasse die letzten drei Meetings in ein paar Sätzen zusammen