# Strudel über MCP mit Langflow steuern

In dieser Übung startet ein lokaler MCP-Server über Playwright einen sichtbaren Chromium-Browser mit [Strudel](https://strudel.cc/). Der Agent erzeugt einen Beat, verändert ihn und stoppt die Wiedergabe.

## Lernziele

- einen per `npx` gestarteten STDIO-MCP-Server registrieren,
- Browser- und Audiozustand von der Langflow-Session unterscheiden,
- Start, Änderung und Stopp als getrennte Toolaufrufe beobachten.

## Voraussetzungen

- Langflow 1.11.3 läuft außerhalb eines Containers oder Node.js und Chromium sind auch im Container verfügbar.
- Installiere eine aktuelle [Node.js-LTS-Version](https://nodejs.org/), laut Upstream Node.js 22 oder neuer. `npm` und `npx` sind enthalten.
- Prüfe mit `node --version` und `npx --version`, dass Langflow dieselben Programme über seinen PATH finden kann.

Eine globale Installation des MCP-Pakets ist nicht nötig. `npx -y` lädt und startet das Paket bei Bedarf. Das bedeutet zugleich, dass beim ersten Start Code aus dem npm-Registry ausgeführt und Netzwerkzugriff benötigt wird.

## 1. Playwright Chromium vorbereiten

Installiere einmalig den von Playwright verwendeten Browser:

```bash
npx -y playwright install chromium
```

Auf verwalteten Workshop-Rechnern kann dieser Schritt bereits vorbereitet sein. Installiere keine zusätzlichen Systemabhängigkeiten ohne Freigabe.

## 2. MCP-Server in Langflow registrieren

Öffne **Settings > MCP Servers > Add MCP Server**, wähle **STDIO** und trage ein:

- Name: `strudel-local`
- Command: `npx`
- Arguments: `-y` und `@williamzujkowski/live-coding-music-mcp`

Ziehe `strudel-local` aus der **MCP sidebar** in `MCP Spielwiese`, aktiviere **Tool Mode** und verbinde **Toolset > Agent Tools**. Gib für diese Übung nur die benötigten Tools frei: `init`, `compose`, `get_pattern`, `edit_pattern`, `playback` und optional `set_tempo`.

## 3. Lautstärke sicher einstellen

1. Stelle die Systemlautstärke vor dem ersten Ton sehr niedrig ein.
2. Nutze möglichst Kopfhörer nicht gemeinsam und setze sie erst nach einem leisen Funktionstest auf.
3. Halte die Stummtaste bereit. Unerwartet laute oder verzerrte Wiedergabe sofort stoppen.

## 4. Beat-Aufgabe

Sende jeden Prompt einzeln und beobachte Agent Steps sowie das sichtbare Strudel-Fenster.

1. Start:

```text
Initialisiere Strudel. Erzeuge einen einfachen Techno-Beat mit 120 BPM aus Kick, Clap und leiser Hi-Hat und starte ihn. Verwende keine externen KI-Dienste.
```

Erwartet: Chromium öffnet Strudel, Pattern-Code erscheint und ein gleichmäßiger Beat ist leise hörbar.

2. Änderung:

```text
Lies zuerst das aktuelle Pattern. Ergänze dann jede vierte Runde um eine kleine Variation und reduziere die Hi-Hat-Lautstärke. Starte das geänderte Pattern erneut.
```

Erwartet: Der Grundpuls bleibt erkennbar, die Variation ist periodisch hörbar und der Code im Editor ändert sich.

3. Stopp:

```text
Stoppe jetzt die Wiedergabe und bestätige den Zustand mit dem passenden Playback-Tool. Verändere das Pattern nicht weiter.
```

Erwartet: Die Wiedergabe endet unmittelbar. Der Pattern-Code bleibt sichtbar.

**Beobachtungsfragen:** Welcher Toolaufruf öffnet den Browser? Welche Änderung existiert außerhalb des Chatverlaufs? Warum beendet eine neue Playground-Session weder automatisch den Ton noch den Node-Prozess?

## Prozess sauber beenden

Stoppe zuerst per `playback` mit Aktion `stop`. Schließe anschließend das von Playwright geöffnete Browserfenster und beende beziehungsweise entferne den MCP-Server über Langflows MCP-Verwaltung. Prüfe, dass kein Ton mehr läuft.

## Troubleshooting

- **`npx` nicht gefunden:** Installiere Node.js LTS, starte Langflow neu und prüfe den PATH der Langflow-Umgebung.
- **Chromium fehlt:** Führe `npx -y playwright install chromium` mit demselben Benutzer aus, der Langflow startet.
- **Browser öffnet nicht:** Prüfe, ob eine Sicherheitssoftware den Download oder Browserstart blockiert. Verwende keinen Headless-Modus für diese Beobachtungsübung.
- **Kein Ton:** Entsperre Audio im sichtbaren Browser durch einen Klick, prüfe Ausgabegerät und Lautstärkemixer und bitte den Agenten anschließend erneut um `playback` mit Aktion `play`.
- **Ton läuft weiter:** Rufe `playback` mit Aktion `stop` auf. Falls Langflow nicht mehr reagiert, schließe das Playwright-Browserfenster und beende den zugehörigen Node-Prozess kontrolliert.
- **Erster Start dauert:** `npx` lädt das Paket und Playwright startet Chromium. Warte kurz und vermeide parallele Startversuche.
- **Toolnamen weichen ab:** Das Paket ist in aktiver Entwicklung. Öffne die aktuelle Toolliste in Langflow und gleiche sie mit der Upstream-Dokumentation ab.

## Sicherheit

Allgemeine Sicherheitsgrundsätze stehen im [Track-README](../README.md#sicherheit). Für diese Übung gilt zusätzlich:

- `npx -y` bestätigt die Paketausführung automatisch. Verwende nur das geprüfte Paket und in streng kontrollierten Umgebungen eine freigegebene, gepinnte Version.
- Der Server automatisiert einen echten Browser und greift auf `strudel.cc` zu. Behandle Browserinhalte als nicht vertrauenswürdige Daten.
- Aktiviere keine optionalen KI-Dienste und hinterlege dafür keine Schlüssel. Verwende keine MIDI- oder Exportpfade mit persönlichen Daten.
- Beachte Lautstärke, andere Teilnehmende und mögliche Audio-Latenz. Stoppe die Wiedergabe immer vor dem Prozessende.

## Erfolgskriterien

- Langflow listet die ausgewählten Strudel-Tools.
- Ein sichtbares Pattern startet, ändert sich nachvollziehbar und stoppt zuverlässig.
- Agent Steps zeigen getrennte Aufrufe für Initialisierung, Bearbeitung und Playback.
- Browser und Node-Prozess sind nach der Übung beendet.

## Quellen

- [live-coding-music-mcp](https://github.com/williamzujkowski/live-coding-music-mcp)
- [Strudel](https://strudel.cc/)
- [Playwright](https://playwright.dev/docs/browsers)
- [Langflow 1.11: MCP-Client](https://docs.langflow.org/1.11.0/mcp-client)
