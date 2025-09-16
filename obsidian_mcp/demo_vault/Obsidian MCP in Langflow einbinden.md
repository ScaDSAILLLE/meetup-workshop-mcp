# Obsidian MCP in Langflow einbinden

![[obsidian.png]]

0. Obsidian öffnen
1. Vorhandenen Vault öffnen > Demo_Vault auswählen
2. In Obsidian unten links aufs Zahnrad klicken ![[settings.png]]
3. Einstellungen > Community Plugins > Turn On Community-Plugins
4. Community Plugins durchsuchen: Local REST API
5. Local REST API installieren und aktivieren
6. Local REST API Optionen öffnen oder falls schon installiert unten bei Community Plugins "Local REST API" anklicken ![[restapi.png]]
7. API Key kopieren ![[copy.png]]
8. API Key hier 👇 bei "OBSIDIAN_API_KEY" einfügen und den gesamten JSON-Text kopieren
```
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
```
9. In Langflow in der "MCP Tools"-Komponente auf "Select a server" klicken ![[selectserver.png]]
10. JSON Tab auswählen, Text einfügen und auf "Add Server" klicken ![[JSONtab.png]]
11. Für die Komponente den Tool Modus aktivieren ![[toolmode.png]]
12. Toolset mit Tools Schnittstelle des Agenten verbinden ![[connecttool.png]]
13. Oben rechts den Playground öffnen und im Chat ausprobieren 🚀


