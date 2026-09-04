# Deutsche Bahn und Mehr!

## Deutsche Bahn
(https://github.com/PaulvonBerg/db-mcp-server)
- Den gesamten JSON-Text kopieren und in Langflow MCP-Tool einfügen
```
{
  "mcpServers": {
    "deutschebahn": {
      "command": "npx",
      "args": [
        "-y", "mcp-remote",
        "https://db-mcp.datamonkey.tech/mcp",
        "--transport", "http-only"
      ]
    }
  }
}
```

## Andere MCPs
Hier gibt es viele Beispiele: https://mcp.so/
