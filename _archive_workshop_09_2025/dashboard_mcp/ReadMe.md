# 🚀 Dashboard MCP Setup Guide

> **A complete guide to get your Dashboard MCP server up and running**

---

## 📋 Prerequisites

- Python with `uv` package manager installed
- Network access between your devices
- LLM Client that supports MCP servers

---

## 🛠️ Quick Start

### Step 1: Launch the Dashboard Server
Open your first terminal and run:

```bash
uv run dashboard_server.py
```

**✅ Expected result:** Dashboard server starts and displays the web interface

---

### Step 2: Start the MCP Server
Open a **second terminal** and run:

```bash
uv run mcp_server.py
```

**✅ Expected result:** MCP server starts and listens for connections

---

### Step 3: Configure Your LLM Client

Add the following configuration to your LLM Client settings:

```json
{
  "mcpServers": {
    "workshop-assistant": {
      "url": "http://{mcp_server_network_ip}:8082/mcp"
    }
  }
}
```

> 💡 **Tip:** Replace `{mcp_server_network_ip}` with the actual IP address of your MCP server

---

## 🌐 Network Access

This configuration allows access from **any device** on your network:
- **Local access:** Use `localhost` or `127.0.0.1`
- **Network access:** Use your machine's local IP (e.g., `192.168.1.100`)
- **Find your IP:** Run `ipconfig` (Windows) or `ifconfig` (Mac/Linux)

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Port conflicts** | Check if ports 8082 is available |
| **Network access denied** | Verify firewall settings |
| **Connection timeout** | Confirm IP address and network connectivity |
| **MCP not recognized** | Ensure LLM Client supports MCP protocol |

---

## 📞 Support

Need help? Check the logs in both terminals for detailed error messages and debugging information.

**Happy coding! 🎉**