# MCP-Workshop: ein Jahr später

Praktische Materialien für das ScaDS.AI Meetup zum [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction). Der Workshop verbindet einen niedrigschwelligen Einstieg mit Langflow mit vertiefenden Python-Tracks zu Tool Discovery, Programmatic Tool Calling und eigenen MCP-Servern.

Die Dramaturgie, Agenda und Lernziele stehen in [Programm.md](Programm.md). Dieses README ist der Einstieg in die Workshop-Materialien.

## Workshop-Tracks

### Beginner: MCP mit Langflow

Keine Programmiererfahrung erforderlich. Arbeite die Übungen in dieser verbindlichen Reihenfolge durch:

1. [Obsidian: Notizen sicher lesen und zusammenfassen](beginners_track/01_obsidian_mcp/README.md)
2. [Blender: modulare Würfelinstallation aufbauen](beginners_track/02_blender_mcp/README.md)
3. [Strudel: einen Beat starten, verändern und stoppen](beginners_track/03_strudel_mcp/README.md)

Der gemeinsame Einstieg, die Langflow-Grundbedienung und die vorbereiteten Flow-Exporte stehen in [beginners_track/README.md](beginners_track/README.md).

### Advanced: große Tool-Landschaften verstehen

- [Progressive Disclosure](advanced_track/01_mcp-progressive_disclosure-demo/README.md): Vergleiche vollständige Tool-Exposition mit dynamischer Tool-Auswahl und beobachte Schema-Tokens.
- [FastMCP](advanced_track/02_fastmcp/README.md): Entwickle einen Server schrittweise von Transport und Tools bis zu Resources, Templates und Prompts.
- [Programmatic Tool Calling](advanced_track/03_programmatic_tool_calling/README.md): Untersuche, wie ein Modell viele Tools programmatisch orchestrieren kann und wo die Sicherheitsgrenzen liegen.

## Vorbereitung

- Für vorbereitete Workshop-Rechner genügt der jeweilige Track-Einstieg.
- Für eigene Geräte beschreibt jeder Track seine Abhängigkeiten und Befehle. Python-Projekte werden immer im jeweiligen Track-Verzeichnis ausgeführt.
- Die gemeinsame Vorlage für credential-abhängige Advanced-Demos ist [.env.example](.env.example). Lege persönliche Zugangsdaten nur in der Root-`.env` ab, niemals in Flow-Exporten, Notizen oder Unterprojekten.
- Starte keine Live-Demo mit persönlichem Zugang ohne zu prüfen, welche Daten an den konfigurierten Endpoint gesendet werden.

## Sicherheitsgrundsätze

- MCP-Server und ihre Toolausgaben sind nicht automatisch vertrauenswürdig.
- Beginne mit Lesezugriffen und gib schreibende oder Code-ausführende Tools nur in einer kontrollierten Übungsumgebung frei.
- Verwende Testdaten, einen separaten Obsidian-Vault und unkritische Blender-Dateien.
- Beende lokale Server, Browser und Audio-Wiedergabe nach den Übungen.

## Verifikation

Die Python-Tracks enthalten jeweils einen Offline-Prüfpfad mit `uv run pytest` und `uv run ruff check .`. Der Beginner-Track benötigt eine manuelle Abnahme in Langflow 1.11.3, weil seine Flow-Exporte aus einer älteren Langflow-Version stammen.
