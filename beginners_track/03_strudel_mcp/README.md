# Strudel über MCP mit Langflow steuern

In dieser Übung startet ein lokaler MCP-Server über Playwright einen sichtbaren Chromium-Browser mit [Strudel](https://strudel.cc/). Der Agent erzeugt einen Beat, verändert ihn und stoppt die Wiedergabe.
So kannst du mittels einer Musik-Skriptsprache Beats oder ganze Songs erzeugen, Inspiration gefällig: [DJ_Dave auf YouTube](https://www.youtube.com/watch?v=ZCcpWzhekEY)

# A. Aufgabe

0. Vorab: **Lautstärke** sicher einstellen

1. Start: Sende jeden Prompt einzeln und beobachte Agent Steps sowie das sichtbare Strudel-Fenster.

    ```text
    Initialisiere Strudel. Erzeuge einen einfachen Techno-Beat mit 120 BPM aus Kick, Clap und leiser Hi-Hat und starte ihn. Verwende keine externen KI-Dienste.
    ```

2. Erwartet: Chromium öffnet Strudel, Pattern-Code erscheint und ein gleichmäßiger Beat ist leise hörbar.

3. Änderung:

    ```text
    Lies zuerst das aktuelle Pattern. Ergänze dann jede vierte Runde um eine kleine Variation und reduziere die Hi-Hat-Lautstärke. Starte das geänderte Pattern erneut.
    ```

4. Erwartet: Der Grundpuls bleibt erkennbar, die Variation ist periodisch hörbar und der Code im Editor ändert sich.

5. Stopp:

    ```text
    Stoppe jetzt die Wiedergabe und bestätige den Zustand mit dem passenden Playback-Tool. Verändere das Pattern nicht weiter.
    ```

6. Erwartet: Die Wiedergabe endet unmittelbar. Der Pattern-Code bleibt sichtbar.

7. **Beobachtungsfragen:** Welcher Toolaufruf öffnet den Browser? Welche Änderung existiert außerhalb des Chatverlaufs? Warum beendet eine neue Playground-Session weder automatisch den Ton noch den Node-Prozess?

## Prozess sauber beenden

Stoppe zuerst per `playback` mit Aktion `stop`. Schließe anschließend das von Playwright geöffnete Browserfenster und beende beziehungsweise entferne den MCP-Server über Langflows MCP-Verwaltung. Prüfe, dass kein Ton mehr läuft.

# B. Setup (für alle, die es auf ihrem System aufsetzen und testen wollen)

## Voraussetzungen

- Langflow 1.11.3 (Desktop Variante) oder Node.js und Chromium sind auch im Container verfügbar.
- Installiere eine aktuelle [Node.js-LTS-Version](https://nodejs.org/), laut Upstream Node.js 22 oder neuer. `npm` und `npx` sind enthalten.
- Prüfe mit `node --version` und `npx --version`, dass Langflow dieselben Programme über seinen PATH finden kann.


## 1. Strudel MCP & Playwright Chromium vorbereiten

Installiere den Strudel MCP:
```bash
npm install -g @williamzujkowski/live-coding-music-mcp
```

Installiere einmalig den von Playwright verwendeten Browser:

```bash
npx -y playwright install chromium
```

## 2. MCP-Server in Langflow registrieren

Öffne **Settings > MCP Servers > Add MCP Server**, wähle **JSON** und trage ein:

```json
{
    "mcpServers": {
        "strudel": {
        "command": "npx",
        "args": ["-y", "@williamzujkowski/strudel-mcp-server"]
        }
    }
}
```

Wechsle danach zurück zum Projekt/Flow `03_Strudel_Code_Music_MCP.json` (die Registrierung eben lief über die Settings-Seite, nicht im Flow-Editor), ziehe `strudel-local` aus der **MCP sidebar** auf die Arbeitsfläche, aktiviere **Tool Mode** und verbinde **Toolset > Agent Tools**. Gib für diese Übung nur die benötigten Tools frei: `init`, `compose`, `get_pattern`, `edit_pattern`, `playback` und optional `set_tempo`. Öffne anschließend rechts oben den **Playground**, um mit dem Agenten zu chatten.

## Sicherheit

Allgemeine Sicherheitsgrundsätze stehen im [Track-README](../README.md#sicherheit). Für diese Übung gilt zusätzlich:

- `npx -y` bestätigt die Paketausführung automatisch. Verwende nur das geprüfte Paket und in streng kontrollierten Umgebungen eine freigegebene, gepinnte Version.
- Der Server automatisiert einen echten Browser und greift auf `strudel.cc` zu. Behandle Browserinhalte als nicht vertrauenswürdige Daten.
- Aktiviere keine optionalen KI-Dienste und hinterlege dafür keine Schlüssel. Verwende keine MIDI- oder Exportpfade mit persönlichen Daten.
- Beachte Lautstärke, andere Teilnehmende und mögliche Audio-Latenz. Stoppe die Wiedergabe immer vor dem Prozessende.

## Troubleshooting

- **`npx` nicht gefunden:** Installiere Node.js LTS, starte Langflow neu und prüfe den PATH der Langflow-Umgebung.
- **Chromium fehlt:** Führe `npx -y playwright install chromium` mit demselben Benutzer aus, der Langflow startet.
- **Browser öffnet nicht:** Prüfe, ob eine Sicherheitssoftware den Download oder Browserstart blockiert. Verwende keinen Headless-Modus für diese Beobachtungsübung.
- **Kein Ton:** Entsperre Audio im sichtbaren Browser durch einen Klick, prüfe Ausgabegerät und Lautstärkemixer und bitte den Agenten anschließend erneut um `playback` mit Aktion `play`.
- **Ton läuft weiter:** Rufe `playback` mit Aktion `stop` auf. Falls Langflow nicht mehr reagiert, schließe das Playwright-Browserfenster und beende den zugehörigen Node-Prozess kontrolliert.
- **Erster Start dauert:** `npx` lädt das Paket und Playwright startet Chromium. Warte kurz und vermeide parallele Startversuche.
- **Toolnamen weichen ab:** Das Paket ist in aktiver Entwicklung. Öffne die aktuelle Toolliste in Langflow und gleiche sie mit der Upstream-Dokumentation ab.


## Quellen

- [live-coding-music-mcp](https://github.com/williamzujkowski/live-coding-music-mcp)
- [Strudel](https://strudel.cc/)
- [Playwright](https://playwright.dev/docs/browsers)
- [Langflow 1.11: MCP-Client](https://docs.langflow.org/1.11.0/mcp-client)
