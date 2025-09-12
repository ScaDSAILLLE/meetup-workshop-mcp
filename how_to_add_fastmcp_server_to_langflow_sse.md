# Minimal FastMCP Greeting Server für Langflow

Dieses Beispiel zeigt, wie man einen **minimalen FastMCP-Server** mit einem einfachen `greet`-Tool baut und ihn in **Langflow Desktop** einbindet.

---

## 1. Server-Code

Datei: `00_greeting_mcp.py`

```python
from fastmcp import FastMCP

mcp = FastMCP("Greeting Server")

@mcp.tool
def greet(name: str) -> str:
    "Return a short greeting."
    return f"Hello, {name}!"

if __name__ == "__main__":
    # HTTP-Transport (Netzwerk)
    mcp.run(transport="sse", host="127.0.0.1", port=8765)
```

---

## 2. Einbindung über SSE (Netzwerk)

Hierbei läuft der MCP-Server separat, und Langflow verbindet sich über HTTP-SSE.

Zur Sicherheit hier alles in Gänze:

1. Clone Repo:

   ```bash
   git clone https://github.com/ScaDSAILLLE/meetup-workshop-mcp.git
   cd meetup-workshop-mcp
   ```

2. uv Umgebung bauen:
   ```bash
   uv sync
   ```

3. `cd fastmcp`

4. Starte ihn manuell im Terminal:

   ```bash
   uv run 00_greeting_mcp.py
   ```

5. Langflow Desktop starten

6. In Langflow: siehe mcp_sse_fastmcp.json (od. neuen flow (blank))
   In neuem flow:
   - **Add MCP Server → Tab „SSE“**
   - Felder ausfüllen:

     - **Name:** `Greeting (SSE)`
     - **URL:**  
       ```
       http://127.0.0.1:8765/sse
       ```

7. **Add Server** klicken und im MCP-Node **Refresh** → Tool `greet` erscheint.

---

## 4. Test in einem Flow

- Füge eine **Agent**-Komponente hinzu.  
- Verbinde sie mit der **MCP Tools**-Komponente.  
- Test im Chatfenster:

  ```
  Ruf das Tool 'greet' mit name="Hans Meiser" auf. (Anfrage kann ähnlich oder auch allgemeiner sein.)
  ```

→ Antwort: `Hello, Hans Meiser!`

---

## 5. Troubleshooting

- **Keine Verbindung zum Server od. keine Tools sichtbar**  
  → Prüfen, ob der Server im richtigen Modus läuft (`sse`, wird beim Start im Terminal auch alles sauber angezeigt, wie die URL ist usw.).  
  → Sicherstellen, dass `fastmcp` im gleichen venv wie das angegebene `python.exe` installiert ist.

---
