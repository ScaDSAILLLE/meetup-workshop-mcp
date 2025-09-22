# MCP Workshop - Model Context Protocol Integration

> Workshop zur Integration von MCP (Model Context Protocol) in verschiedene Tools  
> Entwickelt von ScadsAI Leipzig/Dresden

## Übersicht

Praktische Beispiele und Tutorials für die Arbeit mit dem Model Context Protocol (MCP). Integration von MCP-Servern in Obsidian, Blender, Langflow und eigene Server-Entwicklung mit FastMCP.

Keine Vorkenntnisse erforderlich - alle MCP-Anbindungen sind Low-Code.

## Setup (keine Gewähr bei Software-Installation)

**Benötigte Software:**
- **Langflow (Desktop)** - [Download](https://www.langflow.org/) 
- **Blender** - [Download](https://www.blender.org/) + [MCP-Server Anleitung](https://github.com/ahujasid/blender-mcp)
- **Obsidian** - [Download](https://obsidian.md/) + [Local REST API Plugin](https://github.com/coddingtonbear/obsidian-local-rest-api)

**Zusätzlich für FastMCP:**
- **UV Package Manager** - [Installation](https://docs.astral.sh/uv/)
- Repository klonen und `uv sync` ausführen

## Repository-Struktur

```
📂 meetup-workshop-mcp/
├── 📂 obsidian_mcp/     # START HIER - Obsidian Integration
├── 📂 blender/          # Blender MCP Integration  
├── 📂 langflow/         # Langflow Flows & Dokumentation
├── 📂 fastmcp/          # Python MCP-Server Beispiele
├── 📂 workshop_slides/  # Für Workshop-Leiter
└── 📂 dashboard_mcp/    # Für Workshop-Leiter
```

## Workshop-Module

**Empfohlener Ablauf:** Obsidian → Blender/Deutsche Bahn → FastMCP (optional)

### 1. Obsidian MCP 
**Einstieg und MCP-Grundlagen**

Setup von Obsidian mit MCP-Integration. Local REST API Konfiguration und erste MCP-Nutzung.

- **Dauer:** 10-15 Minuten
- **Anleitung:** [Obsidian MCP Setup](./obsidian_mcp/demo_vault/Obsidian%20MCP%20in%20Langflow%20einbinden.md)

### 2. Blender MCP
**3D-Integration über MCP**

Blender Addon Installation und 3D-Objekt Manipulation via MCP-Protokoll.

- **Dauer:** 10-15 Minuten  
- **Anleitung:** [Blender Integration](./blender/README.md)

### 3. Deutsche Bahn & weitere APIs
**Externe Services über MCP**

Integration der Deutsche Bahn API und Exploration weiterer MCP-Server.

- **Dauer:** 5-10 Minuten
- **Anleitung:** [DB Integration](./obsidian_mcp/demo_vault/Deutsche%20Bahn%20und%20Mehr!.md)

### 4. FastMCP (Optional)
**Eigene MCP-Server entwickeln**

Python-basierte MCP-Server erstellen - von einfachen Funktionen bis zum persönlichen Assistenten.

- **Dauer:** 30-60 Minuten
- **Anleitung:** [FastMCP Tutorial](./fastmcp/ReadME.md)

### 5. Langflow Integration
**Visuelle Workflow-Integration**

Vorgefertigte Flows für alle Workshop-Module. Wird durchgängig in den anderen Modulen verwendet.

- **Flows:** [Langflow Dokumentation](./langflow/ReadME.md)

### Dashboard MCP
**Für Workshop-Leiter**

FastAPI-basiertes Web-Interface für MCP-Demos und Code-Inspiration.

- **Code:** [Dashboard Setup](./dashboard_mcp/ReadMe.md)

## Troubleshooting

**UV Installation:**
```bash
# Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# Mac: brew install uv  
# Linux: curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Port-Konflikte:** Ports 8082, 9876, 27124 müssen verfügbar sein (`netstat -an` prüft Verfügbarkeit)

**Obsidian REST API:** Community Plugins aktivieren, API-Key korrekt einfügen

## Ressourcen

- **Weitere MCP-Server:** [mcp.so](https://mcp.so/)
- **MCP-Dokumentation:** [modelcontextprotocol.io](https://modelcontextprotocol.io/)
- **Support:** [GitHub Issues](https://github.com/ScaDSAILLLL/meetup-workshop-mcp/issues)

## Lizenz

MIT-Lizenz - siehe LICENSE-Datei.

---

**Start:** [Obsidian MCP Setup](./obsidian_mcp/demo_vault/Obsidian%20MCP%20in%20Langflow%20einbinden.md)