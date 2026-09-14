# Blender über MCP mit Langflow steuern

In dieser Übung steuert ein Langflow-Agent eine lokale Blender-Szene. Das Blender-Add-on stellt einen Socket auf `localhost:9876` bereit; der per `uvx` gestartete MCP-Server übersetzt MCP-Toolaufrufe in Blender-Befehle.
Oder einfach gesagt: interagiere selbst mit komplexen open source Tools, wie Blender und bediene sie in natürlicher Sprache, um deine 3D-Szene, Objekte oder gar Animationen zu erstellen.  

# A. Aufgabe

## Würfelinstallation bauen

Führe jeden Prompt einzeln aus und prüfe Blender nach jedem Schritt. Erlaube keine Downloads externer Assets.

1. Bestandsaufnahme:

    ```text
    Lies die aktuelle Blender-Szene aus. Verändere noch nichts und nenne vorhandene Objekte.
    ```

2. Erwartet: Kamera, Licht und der Standardwürfel werden genannt.

3. Sockel:

    ```text
    Lösche nur den Standardwürfel. Erzeuge neun gleich große Würfel mit Kantenlänge 1 als lückenlosen 3-mal-3-Sockel auf dem Boden. Die Mittelpunkte liegen bei X=-1, 0, 1 und Y=-1, 0, 1 jeweils auf Z=0,5. Benenne sie von vorne nach hinten und je Reihe von links nach rechts als Workshop-Würfel-01 bis Workshop-Würfel-09. Verändere Kamera und Licht noch nicht.
    ```

Erwartet: eine quadratische Grundfläche aus neun sauber ausgerichteten Würfeln; jede Unterseite liegt auf Z=0.

4. Aufbau und Material:

    ```text
    Ergänze auf dem hinteren und mittleren Bereich vier weitere Würfel als zweite Ebene: über Workshop-Würfel-07, Workshop-Würfel-08 und Workshop-Würfel-09 sowie über Workshop-Würfel-05. Jeder neue Würfel hat Kantenlänge 1 und Mittelpunkt Z=1,5. Gib allen Würfeln eine mittlere Rauheit. Jede Oberseite soll goldfarben sein; die senkrechten Flächen sollen abwechselnd anthrazit und silbern wirken. Weise die Materialien pro Fläche zu und verwende keine externen Assets.
    ```

5. Erwartet: Eine kompakte, gestufte Installation aus 13 Würfeln mit goldenen Oberseiten und dunklen beziehungsweise silbernen Seitenflächen erscheint in der Materialvorschau.

6. Präsentation:

    ```text
    Richte Kamera und vorhandenes Licht so aus, dass die gesamte Workshop-Würfelinstallation aus einer leicht erhöhten Dreiviertelansicht vollständig sichtbar ist. Verwende einen neutralen hellen Hintergrund und rendere ein Vorschaubild.
    ```

7. Vergleiche das Ergebnis mit [generated-image.png](generated-image.png). Perspektive und Beleuchtung dürfen leicht abweichen; die gestufte Würfelanordnung, goldenen Oberseiten, dunklen und silbernen Seitenflächen sowie die vollständige Sichtbarkeit müssen erkennbar übereinstimmen.

8. **Beobachtungsfragen:** Welches Tool liest nur? Bei welchem Schritt wird `execute_code` oder `execute_blender_code` verwendet? Welche Änderung bleibt in Blender erhalten, auch wenn du eine neue Langflow-Session beginnst?

9. Der sicherste Reset ist **File > New > General** und **Don't Save** für die Übungsdatei. Alternativ bitte den Agenten ausdrücklich, nur `Workshop-Quader` und sein Workshop-Material zu löschen und anschließend die Standardszene nicht weiter zu verändern. Prüfe das Ergebnis selbst; ein neuer Playground-Chat setzt Blender nicht zurück.

# B. Setup (für alle, die es auf ihrem System aufsetzen und testen wollen)

## Voraussetzungen

- Langflow (wir nutzen 1.11.x), [Blender](https://www.blender.org/download/) 4.5.3 oder neuer und [uv](https://docs.astral.sh/uv/getting-started/installation/) sind installiert.
- Speichere offene Blender-Arbeiten. Verwende für die Übung eine neue, unkritische Datei.

## 1. Add-on installieren

Bevorzugt installierst du die aktuelle Upstream-Version:

```bash
uvx blender-mcp install-addon
```

Öffne anschließend **Edit > Preferences > Add-ons**, suche nach **MCP for Blender** beziehungsweise **Blender MCP** und aktiviere das Add-on. Falls die automatische Installation nicht möglich ist, kannst du `blender_setup/addon.py` manuell über **Install...** wählen. Diese lokale Datei ist eine bereinigte Workshop-Quellkopie, keine zugesicherte aktuelle Upstream-Version.

## 2. Blender-Server starten

1. Öffne eine neue Blender-Datei mit der Standardszene.
2. Drücke im 3D-Viewport `N` und öffne den Reiter **MCP for Blender** beziehungsweise **BlenderMCP**.
3. Lasse externe Asset-Dienste wie Poly Haven, Hyper3D und Sketchfab deaktiviert.
4. Prüfe Port `9876` und klicke **Start MCP Server**, **Connect to MCP server** oder die entsprechende Schaltfläche deiner Add-on-Version.
5. Lass Blender geöffnet. Starte nicht parallel einen zweiten Blender-MCP-Client.

## 3. Server in Langflow registrieren

Öffne **Settings > MCP Servers > Add MCP Server** und wähle **JSON** und trage ein:

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

Unter Windows kann bei einem nicht gefundenen `uvx` stattdessen `cmd` mit den Argumenten `/c`, `uvx`, `blender-mcp` nötig sein. Verwende keinen persönlichen absoluten Pfad in einer geteilten Konfiguration.

Wechsle danach zurück zum Projekt/Flow `02_Blender_MCP.json` (die Registrierung eben lief über die Settings-Seite, nicht im Flow-Editor), ziehe `blender-mcp` aus der **MCP sidebar** auf die Arbeitsfläche, aktiviere **Tool Mode** und verbinde **Toolset > Agent Tools**. Öffne anschließend rechts oben den **Playground**, um mit dem Agenten zu chatten.

## Sicherheit

Allgemeine Sicherheitsgrundsätze stehen im [Track-README](../README.md#sicherheit). Für diese Übung gilt zusätzlich:

- `execute_code` beziehungsweise `execute_blender_code` kann beliebigen Python-Code im Blender-Prozess ausführen und damit auch Dateien, Prozesse und Netzwerkzugriffe erreichen. Safe Mode reduziert Risiken, ist aber keine Sandbox.
- Verwende nur unkritische Dateien, speichere vorher und prüfe die vorgeschlagenen Schritte. Gib dem Server keine Aufgabe, beliebige Pfade zu lesen oder Programme zu installieren.
- Externe Dienste laden Inhalte aus dem Internet und können eigene Schlüssel, Bedingungen, Telemetrie und Lizenzpflichten haben. Sie bleiben in dieser Übung deaktiviert.
- Der Socket soll an `localhost` gebunden bleiben.

## Troubleshooting

- **Add-on fehlt:** Starte Blender nach der Installation neu oder installiere `addon.py` manuell und aktiviere das Kontrollkästchen.
- **Connection refused:** Starte zuerst den Add-on-Server in Blender und prüfe Port 9876.
- **`uvx` nicht gefunden:** Öffne Langflow aus einer Umgebung mit korrektem PATH oder nutze unter Windows den beschriebenen `cmd`-Wrapper.
- **Port belegt:** Beende andere Blender-MCP-Instanzen; betreibe nicht mehrere Clients gleichzeitig.
- **Keine sichtbare Farbe:** Wechsle im Viewport zu **Material Preview** oder rendere erneut.
- **Timeout:** Teile die Aufgabe in Geometrie, Material, Kamera und Render auf.


## Quellen

- [Blender MCP Upstream](https://github.com/ahujasid/blender-mcp)
- [Langflow 1.11: MCP-Client](https://docs.langflow.org/1.11.0/mcp-client)
