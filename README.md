# 🚀 MCP Workshop - Model Context Protocol Integration Guide

> Ein umfassender Workshop zur Integration von MCP (Model Context Protocol) in verschiedene Tools und Anwendungen
> 
> **Entwickelt von ScadsAI Leipzig/Dresden**

## 📋 Übersicht

Dieses Repository enthält praktische Beispiele und Tutorials für die Arbeit mit dem Model Context Protocol (MCP). Sie lernen, wie Sie MCP-Server erstellen und in verschiedene Tools wie Obsidian, Blender, Langflow und andere Anwendungen integrieren.

**Keine Vorkenntnisse erforderlich** - Alle MCP-Anbindungen sind Low-Code/No-Code!

## 🎯 Was Sie lernen werden

- **MCP-Grundlagen**: Verstehen des Model Context Protocol
- **Tool-Integration**: MCP in bestehende Workflows einbinden (Low-Code)
- **Server-Entwicklung**: Eigene MCP-Server mit FastMCP erstellen (für Interessierte)
- **Praktische Anwendungen**: Reale Use Cases und Beispiele

## 🛠️ Setup (keine Gewähr, ihr installiert Software auf euren Endgeräten)

### Ihr braucht:

**Für alle Workshop-Teilnehmer:**
- **Langflow (Desktop)** - [Download](https://www.langflow.org/) 
  - Flows hierfür liegen als .json in `/langflow`
- **Blender** - [Download](https://www.blender.org/)
  - Hier bitte dieser Anleitung zum Hinzufügen des MCP-Server folgen: [Anleitung](https://github.com/ahujasid/blender-mcp)
- **Obsidian** - [Download](https://obsidian.md/)
  - Hier bitte die Community-Plugins in Settings aktivieren & "Local REST API" hinzufügen: [Anleitung](https://github.com/coddingtonbear/obsidian-local-rest-api)

**Zusätzlich für FastMCP (optional - für Server-Entwicklung):**
- **UV (Python Package Manager)** - [Installation](https://docs.astral.sh/uv/)
- **IDE eurer Wahl** (wir haben VSCode verwendet)
- **Setup:**
  1. Klont das Repo, öffnet einen Terminal im Projekt-Ordner
  2. Gebt ein: `uv sync`
  3. Geht die Beispiel-Python-Skripte Schritt für Schritt durch

## 🏗️ Repository-Struktur

```
📂 meetup-workshop-mcp/
├── 📂 obsidian_mcp/     # 🎯 START HIER - Obsidian Integration
├── 📂 blender/          # Blender MCP Integration  
├── 📂 langflow/         # Langflow Integration & Flows
├── 📂 fastmcp/          # Python MCP-Server Beispiele (optional)
├── 📂 dashboard_mcp/    # 👨‍🏫 Für Workshop-Leiter
└── 📄 README.md         # Diese Datei
```

## 📚 Workshop-Module

### 🎯 Empfohlener Ablauf

**1. Obsidian MCP** → **2. Blender & Deutsche Bahn** → **3. Eigene Server (FastMCP)**

---

### 1. 📝 Obsidian MCP - Der perfekte Einstieg
**🎯 HIER STARTEN - Verstehen Sie MCP-Grundlagen**

- **Pfad**: [`obsidian_mcp/`](./obsidian_mcp/)
- **Schwierigkeit**: ⭐ Beginner
- **Dauer**: 30-45 Minuten
- **Voraussetzungen**: Keine

**Was Sie lernen:**
- MCP-Grundkonzepte verstehen
- Obsidian Vault Setup
- Local REST API Konfiguration
- Erste MCP-Integration

➡️ [Obsidian Integration starten](./obsidian_mcp/demo_vault/Obsidian%20MCP%20in%20Langflow%20einbinden.md)

---

### 2a. 🎨 Blender MCP - 3D trifft AI
**Kreative MCP-Anwendungen**

- **Pfad**: [`blender/`](./blender/)
- **Schwierigkeit**: ⭐⭐ Beginner-Intermediate
- **Dauer**: 45-60 Minuten
- **Voraussetzungen**: Obsidian MCP abgeschlossen

**Was Sie lernen:**
- Blender Addon Installation
- 3D-Objekt Manipulation via MCP
- Integration in AI-Workflows

➡️ [Blender Integration starten](./blender/README.md)

---

### 2b. 🚂 Deutsche Bahn & Mehr
**Echte APIs über MCP nutzen**

- **Pfad**: [`obsidian_mcp/demo_vault/`](./obsidian_mcp/demo_vault/)
- **Schwierigkeit**: ⭐ Beginner  
- **Dauer**: 20-30 Minuten
- **Voraussetzungen**: Obsidian MCP abgeschlossen

**Was Sie lernen:**
- Externe APIs über MCP einbinden
- Deutsche Bahn Reiseinformationen
- MCP-Server-Verzeichnis erkunden

➡️ [DB Integration & mehr](./obsidian_mcp/demo_vault/Deutsche%20Bahn%20und%20Mehr!.md)

---

### 3. 🐍 FastMCP - Eigene Server entwickeln
**Für alle, die tiefer einsteigen wollen**

- **Pfad**: [`fastmcp/`](./fastmcp/)
- **Schwierigkeit**: ⭐⭐⭐ Intermediate-Advanced
- **Dauer**: 1-2 Stunden
- **Voraussetzungen**: Python-Grundkenntnisse hilfreich

**Was Sie lernen:**
- Eigene MCP-Server mit Python erstellen
- Von einfachen Funktionen bis zum persönlichen Assistenten
- Server-Architektur und Best Practices

➡️ [FastMCP Tutorial starten](./fastmcp/ReadME.md)

---

### 4. 🔄 Langflow - Visuelle AI-Integration
**Durchgängig in allen Modulen verwendet**

- **Pfad**: [`langflow/`](./langflow/)
- **Schwierigkeit**: ⭐ Beginner
- **Verwendung**: In allen anderen Modulen integriert

**Was Sie nutzen:**
- Vorgefertigte Flows für alle Workshop-Module
- MCP-Tools in visuellen Workflows
- Eigene Flows als MCP-Tools erstellen

➡️ [Langflow Flows & Dokumentation](./langflow/ReadME.md)

---

### 👨‍🏫 Dashboard MCP - Für Workshop-Leiter
**Web-Interface für MCP-Demos**

- **Pfad**: [`dashboard_mcp/`](./dashboard_mcp/)
- **Schwierigkeit**: ⭐⭐⭐ Intermediate
- **Zielgruppe**: Workshop-Organisatoren
- **Nutzen**: Demonstration und Code-Inspiration

**Für Interessierte:**
- FastAPI Server Setup
- MCP-Web Integration  
- Netzwerk-Konfiguration

➡️ [Dashboard Code erkunden](./dashboard_mcp/ReadMe.md)

## 🎓 Empfohlener Lernpfad

### Für Workshop-Teilnehmer:
```
1. Obsidian MCP (Grundlagen) 
    ↓
2a. Blender MCP (3D-Integration)
2b. Deutsche Bahn API (Externe Services)
    ↓  
3. FastMCP (Eigene Server) - Optional
```

### Für Schnell-Erkunder:
```
1. Obsidian MCP (15 min Setup)
    ↓
2. Deutsche Bahn (5 min Test)  
    ↓
3. Blender MCP (wenn 3D interessiert)
```

### Für Entwickler:
```
1. Obsidian MCP (Konzepte verstehen)
    ↓
2. FastMCP (Vollständige Server-Entwicklung)
    ↓
3. Dashboard MCP (Web-Integration studieren)
```

## 🔧 Troubleshooting

### Häufige Probleme:

**UV nicht gefunden (nur für FastMCP):**
```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Mac  
brew install uv

# Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Port-Konflikte:**
- Prüfen Sie, ob die verwendeten Ports (8082, 9876, 27124, etc.) verfügbar sind
- Verwenden Sie `netstat -an` zur Überprüfung

**Langflow-Verbindungsprobleme:**
- Überprüfen Sie, ob alle MCP-Server richtig gestartet sind
- Verwenden Sie die korrekten URLs aus den Tutorials

**Obsidian Local REST API:**
- Community Plugins müssen aktiviert sein
- API-Key korrekt kopiert und eingefügt
- Port 27124 muss verfügbar sein

## 🌐 Weiterführende Ressourcen

- **Mehr MCP-Server**: [MCP Directory](https://mcp.so/)
- **MCP-Dokumentation**: [Anthropic MCP Docs](https://modelcontextprotocol.io/)
- **Community**: [GitHub Discussions](https://github.com/ScaDSAILLLL/meetup-workshop-mcp/discussions)

## 🤝 Support & Community

- **Issues**: [GitHub Issues](https://github.com/ScaDSAILLLL/meetup-workshop-mcp/issues)
- **Workshop-Fragen**: Direkt an die ScadsAI-Trainer wenden
- **Verbesserungsvorschläge**: Pull Requests willkommen!

## 🏛️ Über ScadsAI

Dieser Workshop wurde vom **ScadsAI Leipzig/Dresden** entwickelt - einem Forschungsinstitut für skalierbare Datenanalyse und künstliche Intelligenz.

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Weitere Informationen finden Sie in der LICENSE-Datei.

---

## 🎉 Los geht's!

**Empfehlung:** Starten Sie mit [Obsidian MCP](./obsidian_mcp/demo_vault/Obsidian%20MCP%20in%20Langflow%20einbinden.md) - das ist der perfekte Einstieg, um MCP zu verstehen!

**Happy Learning! 🚀**