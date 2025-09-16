
![[obsidian.png]]

1. In Obsidian unten links aufs Zahnrad klicken ![[settings.png]]
2. Unten bei Community Plugins "Local REST API" anklicken ![[restapi.png]]
3. API Key kopieren ![[copy.png]]
4. API Key hier 👇 bei "OBSIDIAN_API_KEY" einfügen und den gesamten JSON-Text kopieren
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



5. In Langflow in der "MCP Tools"-Komponente auf "Select a server" klicken ![[selectserver.png]]
6. JSON Tab auswählen, Text einfügen und auf "Add Server" klicken ![[JSONtab.png]]
7. Für die Komponente den Tool Modus aktivieren ![[toolmode.png]]
8. Toolset mit Tools Schnittstelle des Agenten verbinden ![[connecttool.png]]




9. Oben rechts den Playground öffnen und im Chat ausprobieren 🚀


