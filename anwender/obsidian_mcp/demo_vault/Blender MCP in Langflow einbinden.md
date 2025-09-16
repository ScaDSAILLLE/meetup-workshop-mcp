
![[blender.png]]
1. Blender starten (Icon auf dem Desktop) 
2. Den gesamten JSON-Text kopieren und dann genau wie beim Obsidian-MCP in Langflow einfügen
```
{
  "mcpServers": {
    "mcp-obsidian": {
      "command": "uvx",
      "args": [
        "mcp-obsidian"
      ],
      "env": {
        "OBSIDIAN_API_KEY": "4770d1bad45e030c04e83f4bbc645811b2d3ff1f676e79469d56ce90ca2fb477",
        "OBSIDIAN_HOST": "127.0.0.1",
        "OBSIDIAN_PORT": "27124"
      }
    }
  }
} 
```


**💡 Ab hier ist es genauso wie bei Obsidian!**

3. In Langflow in der "MCP Tools"-Komponente auf "Select a server" klicken ![[selectserver.png]]
4. JSON Tab auswählen, Text einfügen und auf "Add Server" klicken ![[JSONtab.png]]
5. Für die Komponente den Tool Modus aktivieren ![[toolmode.png]]
6. Toolset mit Tools Schnittstelle des Agenten verbinden ![[connecttool.png]]



7. Oben rechts den Playground öffnen und im Chat ausprobieren 🚀