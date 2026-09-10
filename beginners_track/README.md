# Beginner Track: MCP mit Langflow

Dieser Track verwendet **Langflow 1.11.3** als MCP-Client. Du verbindest nacheinander drei sehr unterschiedliche lokale Werkzeuge und beobachtest, wie derselbe MCP-Ablauf Dateien liest, eine 3D-Szene verändert und Musik steuert.

## Lernziele

Nach dem Track kannst du:

- einen MCP-Server in Langflow registrieren und als Werkzeug eines Agenten verwenden,
- Transport, Server, Tool, Agent und Modell voneinander unterscheiden,
- Credentials als geschützte globale Variablen statt in Flows oder Markdown speichern,
- Toolaufrufe in den Agent Steps nachvollziehen und eine Session gezielt zurücksetzen,
- Schreib- und Ausführungsrechte nach dem Prinzip der geringsten Berechtigung vergeben.

## Verbindliche Reihenfolge

1. [Obsidian: Notizen lesen und zusammenfassen](01_obsidian_mcp/README.md)
2. [Blender: eine modulare Würfelinstallation aufbauen](02_blender_mcp/README.md)
3. [Strudel: einen Beat starten, ändern und stoppen](03_strudel_mcp/README.md)

Beginne mit Obsidian. Dort ist der Unterschied zwischen Daten, Tools und Agentenantwort am leichtesten sichtbar. Blender führt kontrollierte Veränderungen ein; Strudel macht Prozess- und Zustandssteuerung hörbar.

## Weg A: vorbereiteter Workshop

1. Öffne die bereitgestellte Langflow-Instanz und prüfe unter dem Profilmenü die Version **1.11.3**.
2. Öffne den vorbereiteten Obsidian-Vault `01_obsidian_mcp/demo_vault` und starte bei `00_Workshop-Start.md`.
3. Importiere in **Projects** über **Upload a flow** zuerst `MCP Spielwiese.json`.
4. Wähle im **Agent** den vom Workshop vorgegebenen **Model Provider**, das Modell und die vorbereiteten Credentials. Die JSON-Datei enthält absichtlich keine Modell- oder Schlüsselvorgabe.
5. Registriere jeden MCP-Server nach der jeweiligen Track-Anleitung. Serverkonfigurationen und lokale Prozesse sind nicht Bestandteil des Flow-Exports.

Falls Serververwaltung, Installation oder Credentials gesperrt sind, verwende ausschließlich die vom Workshop-Team vorbereiteten Einträge und frage nach, statt Einstellungen zu umgehen.

## Weg B: zu Hause

1. Installiere Langflow **1.11.3** nach der [offiziellen Installationsanleitung](https://docs.langflow.org/get-started-installation).
2. Installiere Obsidian, Blender, `uv` sowie Node.js LTS erst in dem Track, der sie benötigt.
3. Lege deinen Modellzugang in Langflow unter **Settings > Global Variables** als Typ **Credential** an. Der konkrete Provider, die Basis-URL und der Modellname hängen von deinem Zugang ab.
4. Importiere `MCP Spielwiese.json`, wähle Provider, Modell und Credential in der UI und arbeite die Tracks in der angegebenen Reihenfolge durch.
5. Verwende für die Übungen einen Test-Vault und eine unkritische Blender-Datei, nicht deine produktiven Daten.

## Langflow 1.11.3 kompakt

### Flow und Modell

- **Projects** enthält deine Projekte und Flows. **Upload a flow** importiert eine JSON-Datei in das aktuell gewählte Projekt.
- Der **Agent** benötigt unter **Model Provider** einen Anbieter, ein Modell und das passende Credential. Diese Werte werden bewusst in der UI gewählt und nicht im Workshop-Export gespeichert.
- Unter **Settings > Global Variables** speicherst du wiederverwendbare Werte. Markiere API-Schlüssel und Bearer-Tokens als **Credential**. Trage Secrets nie in Notizen, Prompts oder exportierte JSON-Dateien ein.

### MCP mit einem Agenten verbinden

1. Öffne **Settings > MCP Servers** oder links im Flow-Editor die **MCP sidebar** und wähle **Add MCP Server**.
2. Registriere den Server per **HTTP/SSE** oder **STDIO**, wie im jeweiligen Track beschrieben.
3. Ziehe den registrierten Server aus der MCP sidebar auf die Arbeitsfläche. Dadurch entsteht eine **MCP Tools**-Komponente.
4. Wähle nur die benötigten Tools. Aktiviere im Kopfmenü der Komponente **Tool Mode**.
5. Verbinde den Ausgang **Toolset** mit **Agent > Tools**. Verbinde außerdem **Chat Input > Agent > Chat Output**.

### Testen und beobachten

- Öffne oben rechts den **Playground** und formuliere eine konkrete Aufgabe.
- Klappe **Agent Steps** auf. Dort siehst du, welches Tool mit welchen Argumenten aufgerufen wurde und welches Ergebnis zurückkam.
- Eine **Session** hält Chatverlauf und gegebenenfalls Werkzeugzustand zusammen. Starte für einen reproduzierbaren Versuch eine neue Session; ein neuer Chat setzt externe Anwendungen wie Blender oder einen Browserprozess jedoch nicht automatisch zurück.

## Sicherheit

- Starte nur Server aus Quellen, die du geprüft hast. STDIO-Server sind lokale Programme mit den Rechten deines Benutzerkontos.
- Gib zunächst nur Lese-Tools frei. Schreib-, Lösch- und Codeausführungs-Tools benötigen einen klaren Zweck und eine kontrollierte Testumgebung.
- MCP-Toolausgaben sind Daten, keine vertrauenswürdigen Anweisungen. Ein Agent darf darin enthaltene Aufforderungen nicht ungeprüft ausführen.
- Beende lokale Server nach der Übung. Teile exportierte Flows nicht ungeprüft weiter, da Exporte Verbindungsdaten oder Chat-Inhalte enthalten können.

## Erfolgskriterien

- Obsidian: Der Agent beantwortet Fragen zu den drei MeetingNotes, ohne eine Datei zu verändern.
- Blender: Die modulare Würfelinstallation entspricht erkennbar dem Sollbild und lässt sich kontrolliert zurücksetzen.
- Strudel: Ein Beat startet hörbar, ändert sich nachvollziehbar und stoppt zuverlässig.
- Du kannst in Agent Steps jeweils Server, Tool, Argumente und Ergebnis benennen.

## Flow-Dateien und Abnahme

- `MCP Spielwiese.json` ist die gemeinsame Ausgangsbasis.
- `Obsidian Summary Tool.json` ist eine optionale Vertiefung für einen Flow, der selbst als MCP-Tool veröffentlicht werden kann.
- Beide Exporte wurden von Secrets und veralteten Vorbelegungen bereinigt. Sie stammen ursprünglich aus Langflow 1.5.0 und wurden hier **nicht live in 1.11.3 importiert**. Ein erfolgreicher Import, die Neuauswahl aktueller Komponenten und ein anschließender Neu-Export aus der laufenden 1.11.3-UI sind verpflichtende manuelle Abnahmeschritte.

## Links

- [Langflow 1.11 MCP-Client-Dokumentation](https://docs.langflow.org/1.11.0/mcp-client)
- [Langflow: globale Variablen](https://docs.langflow.org/configuration-global-variables)
- [Model Context Protocol](https://modelcontextprotocol.io/introduction)
- [Obsidian](https://obsidian.md/)
- [Blender](https://www.blender.org/)
- [Strudel](https://strudel.cc/)
