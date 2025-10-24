# Blender MCP

Original Repository for the Blender MCP Server: [https://github.com/ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp)

The following setup instructions are from its README file. For up-to-date information go to the original repository.

## Installation

### Prerequisites

- Blender 3.0 or newer
- Python 3.10 or newer
- uv package manager: 

**If you're on Mac, please install uv as**
```bash
brew install uv
```
**On Windows**
```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex" 
```
and then
```bash
set Path=C:\Users\nntra\.local\bin;%Path%
```

Otherwise installation instructions are on their website: [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

**⚠️ Do not proceed before installing UV**

### Installing the Blender Addon

1. Download the `addon.py` file from this repo
1. Open Blender
2. Go to Edit > Preferences > Add-ons
3. Click "Install..." and select the `addon.py` file
4. Enable the addon by checking the box next to "Interface: Blender MCP"

### Environment Variables

The following environment variables can be used to configure the Blender connection:

- `BLENDER_HOST`: Host address for Blender socket server (default: "localhost")
- `BLENDER_PORT`: Port number for Blender socket server (default: 9876)

Example:
```bash
export BLENDER_HOST='host.docker.internal'
export BLENDER_PORT=9876
```

### Claude for Desktop Integration

[Watch the setup instruction video](https://www.youtube.com/watch?v=neoK_WMq92g) (Assuming you have already installed uv)

Go to Claude > Settings > Developer > Edit Config > claude_desktop_config.json to include the following:

```json
{
    "mcpServers": {
        "blender": {
            "command": "uvx",
            "args": [
                "blender-mcp"
            ]
        }
    }
}
```

### Cursor integration

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/install-mcp?name=blender&config=eyJjb21tYW5kIjoidXZ4IGJsZW5kZXItbWNwIn0%3D)

For Mac users, go to Settings > MCP and paste the following 

- To use as a global server, use "add new global MCP server" button and paste
- To use as a project specific server, create `.cursor/mcp.json` in the root of the project and paste


```json
{
    "mcpServers": {
        "blender": {
            "command": "uvx",
            "args": [
                "blender-mcp"
            ]
        }
    }
}
```

For Windows users, go to Settings > MCP > Add Server, add a new server with the following settings:

```json
{
    "mcpServers": {
        "blender": {
            "command": "cmd",
            "args": [
                "/c",
                "uvx",
                "blender-mcp"
            ]
        }
    }
}
```

[Cursor setup video](https://www.youtube.com/watch?v=wgWsJshecac)

**⚠️ Only run one instance of the MCP server (either on Cursor or Claude Desktop), not both**

---

### LMStudio Integration: Connect Blender MCP to LM Studio (Windows)

#### 1. Requirements

Make sure you have:

* **Blender** installed and open
* **UV (uvx)** installed and on your `PATH` (`uvx --version` works in `cmd`)
* **LM Studio** installed

#### 2. Install and enable the Blender MCP add-on

1. In Blender go to **Edit → Preferences → Add-ons → Install…**
   Select the Blender MCP add-on from the workshop repository.
2. Enable the add-on and make sure the panel shows
   **“Running on port 9876.”**
   (That’s the default communication port.)

#### 3. Install the MCP server once (so LM Studio doesn’t need `uvx`)

Open **Command Prompt (cmd.exe)** and run:

```bat
uv tool install blender-mcp
```

Then verify where it was installed:

```bat
where blender-mcp
```

You should get something like:
`C:\Users\<YOURNAME>\AppData\Roaming\uv\tools\blender-mcp.exe` but could be something else of course!

#### 4. (Optional) Test manually

Run this just to confirm the server connects:

```bat
blender-mcp --blender-host 127.0.0.1 --blender-port 9876
```

If you see logs like
`Connected to Blender at localhost:9876`,
everything works.
Press **Ctrl + C** to stop it.

#### 5. Configure `mcp.json` in LM Studio

Open LM Studio → **Settings → Open mcp.json**,
or open the file manually and insert:

```json
{
  "mcpServers": {
    "blender": {
      "command": "C:\\Users\\<YOURNAME>\\AppData\\Roaming\\uv\\tools\\blender-mcp.exe",
      "args": ["--blender-host", "localhost", "--blender-port", "9876"],
      "env": {
        "PYTHONUTF8": "1",
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

> ⚠️ Replace `<YOURNAME>` with your actual Windows user folder or with the path you got when using `where blender-mcp`

This tells LM Studio to start the installed `blender-mcp.exe` directly (no `uvx`), which avoids startup output on `stdout` that would otherwise break the JSON handshake.

### 6. Quick functionality test

Ask your model something like:

> “Create a cube in Blender and scale it to 2.”

If the connection works, you’ll see Blender respond and perform the action. If not, restart LM Studio or see 8. for troubleshooting. If nothing helps, ask a friend or a (local) LLM :)

### 8. Common issues & fixes

| Problem                               | Cause                                    | Fix                                                                                   |
| ------------------------------------- | ---------------------------------------- | ------------------------------------------------------------------------------------- |
| `MCP error -32000: Connection closed` | `uvx` printed text before JSON handshake | Use the installed `blender-mcp.exe` as above                                          |
| LM Studio says `command not found`    | LM Studio doesn’t inherit your PATH      | Use the full absolute path to `blender-mcp.exe`                                       |
| Port 9876 blocked                     | Firewall or another process using it     | Allow Blender in Windows Firewall or pick another port in both Blender and `mcp.json` |

✅ **That’s it!**
From now on, LM Studio will launch Blender MCP directly and communicate smoothly with your running Blender instance.

---

### Visual Studio Code Integration

_Prerequisites_: Make sure you have [Visual Studio Code](https://code.visualstudio.com/) installed before proceeding.

[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_blender--mcp_server-0098FF?style=flat-square&logo=visualstudiocode&logoColor=ffffff)](vscode:mcp/install?%7B%22name%22%3A%22blender-mcp%22%2C%22type%22%3A%22stdio%22%2C%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22blender-mcp%22%5D%7D)
