# Beginner Track: MCP mit Langflow

Dieser Track verwendet **Langflow** als MCP-Client und beginnerfreundliches User Interface. Du hast noch nie etwas mit MCP gemacht, du stehst vielleicht relativ am Anfang bzgl. Programmieren lernen oder willst einfach mal etwas Neues ausprobieren? Perfekt! Hier verbindest Du nacheinander drei sehr unterschiedliche lokale Werkzeuge und beobachtest, wie derselbe MCP-Ablauf Dateien liest, eine 3D-Szene verändert und Musik steuert. Alles in natürlicher Sprache: du chattest mit einem KI-Agenten und gibst Anweisungen, was getan werden soll. Viel Spaß!

## Lernziele

Nach dem Track kannst du:

- einen MCP-Server in Langflow registrieren und als Werkzeug eines Agenten verwenden,
- Transport, Server, Tool, Agent und Modell voneinander unterscheiden,
- Toolaufrufe in den Agent Steps nachvollziehen und eine Session gezielt zurücksetzen,
- nachvollziehen, wie man lokale Software oder externe Dienste mit KI-Modellen, wie LLMs, bedienen kann.

## Vorgeschlagene Reihenfolge

1. [Obsidian: Notizen lesen und zusammenfassen](01_obsidian_mcp/README.md)
2. [Blender: eine modulare Würfelinstallation aufbauen](02_blender_mcp/README.md)
3. [Strudel: einen Beat starten, ändern und stoppen](03_strudel_mcp/README.md)

Beginne mit Obsidian. Dort ist der Unterschied zwischen Daten, Tools und Agentenantwort am leichtesten sichtbar. Blender als 3D-Designsoftware zeigt dir, wie mächtig die Kopplung zwischen Sprachmodellen und umfangreichen Tools sein kann- bediene Blender in natürlicher Sprache und lerne, wie die Software funktioniert; Strudel ist ein Musik-Skripting Tool: tob dich hier kreativ aus, erstelle Beats oder vollwertige Songs zusammen mit dem KI-Agenten.

## A: vorbereiteter Workshop

1. Öffne die bereitgestellte Langflow-Instanz. 
2. Öffne den vorbereiteten Obsidian-Vault `01_obsidian_mcp/demo_vault` und starte bei `00_Workshop-Start.md`.
3. Importiere in **Projects** über **Upload a flow** zuerst `MCP Spielwiese.json`.
4. Wähle im **Agent** den vom Workshop vorgegebenen **Model Provider**, das Modell und die vorbereiteten Credentials. Die JSON-Datei enthält absichtlich keine Modell- oder Schlüsselvorgabe.
5. Registriere jeden MCP-Server nach der jeweiligen Track-Anleitung. Serverkonfigurationen und lokale Prozesse sind nicht Bestandteil des Flow-Exports.

Falls Serververwaltung, Installation oder Credentials gesperrt sind, verwende ausschließlich die vom Workshop-Team vorbereiteten Einträge und frage nach, statt Einstellungen zu umgehen.

## B: auf eigener Hardware oder für *zu Hause*

1. Installiere Langflow nach der [offiziellen Installationsanleitung](https://docs.langflow.org/get-started-installation).
2. Installiere Obsidian, Blender, `uv` sowie Node.js LTS.
3. Lege deinen Modellzugang in Langflow unter **Settings > Modelprovider** an. Der konkrete Provider, die Basis-URL und der Modellname hängen von deinem Zugang ab.
4. Importiere `langflow_flows`, wähle Provider und Modell (ggf. Credential/API-Key) in der UI und arbeite die Tracks in der angegebenen Reihenfolge durch.
5. Verwende für die Übungen den [`demo_vault`](./01_obsidian_mcp/demo_vault), falls vorhanden eine eigene (hoffentlich unkritishche) Blender-Datei, du kannst aber auch alles "from scratch" beginnen. Empfehlung: Nutze bis zum sicheren Umgang mit MCP keine wichtigen oder produktiv-Daten. Sowieso gilt wie immer: teile keine privaten oder sensiblen Infos mit den Sprachmodellprovidern- probier doch mal lokale Sprachmodelle aus, z.B. mit [llama.cpp](https://llama.app/), [lmstudio](https://lmstudio.ai/) oder ähnliche Tools.

## Langflow kurz & kompakt

### Flow und Modell

- **Projects** enthält deine Projekte und Flows. **Upload a flow** importiert eine JSON-Datei in das aktuell gewählte Projekt.
- Der **Agent** benötigt unter **Model Provider** einen Anbieter, ein Modell und das passende Credential. Diese Werte werden bewusst in der UI gewählt und nicht im Workshop-Export gespeichert.
- Unter **Settings > Global Variables** speicherst du wiederverwendbare Werte. Markiere API-Schlüssel und Bearer-Tokens als **Credential**. Trage Secrets nie in Notizen, Prompts oder exportierte JSON-Dateien ein.

### MCP mit einem Agenten verbinden

1. Öffne **Settings > MCP Servers** oder links im Flow-Editor die **MCP sidebar** und wähle **Add MCP Server**.
2. Registriere den Server per **JSON** oder den weiteren angebotenen Inputs, wie im jeweiligen Track beschrieben.
3. Ziehe den registrierten Server aus der MCP sidebar auf die Arbeitsfläche. Dadurch entsteht eine **MCP**-Komponente.
4. Wähle nur die benötigten Tools. Aktiviere im Kopfmenü der Komponente **Tool Mode**.
5. Verbinde den Ausgang **Toolset** mit **Agent > Tools**. Verbinde außerdem **Chat Input > Agent > Chat Output**.

### Testen und beobachten

- Öffne oben rechts den **Playground** ("Spielplatz") und formuliere eine konkrete Aufgabe.
- Klappe **Agent Steps** auf. Dort siehst du, welches Tool mit welchen Argumenten aufgerufen wurde und welches Ergebnis zurückkam.
- Eine **Session** hält Chatverlauf und gegebenenfalls Werkzeugzustand zusammen. Starte für einen reproduzierbaren Versuch eine neue Session; ein neuer Chat setzt externe Anwendungen wie Blender oder einen Browserprozess jedoch nicht automatisch zurück.

## Sicherheit

Allgemeine Sicherheitsgrundsätze stehen im [Haupt-README](../README.md#sicherheitsgrundsätze). Für den Langflow-Track gilt zusätzlich:

- Starte nur Server aus Quellen, die du geprüft hast. STDIO-Server sind lokale Programme mit den Rechten deines Benutzerkontos.
- Teile exportierte Flows nicht ungeprüft weiter, da Exporte Verbindungsdaten oder Chat-Inhalte oder API-Keys usw. enthalten können.


## Links

- [Langflow Dokumentation](https://docs.langflow.org/)
- [Model Context Protocol](https://modelcontextprotocol.io/introduction)
- [Obsidian](https://obsidian.md/)
- [Blender](https://www.blender.org/)
- [Strudel](https://strudel.cc/)
