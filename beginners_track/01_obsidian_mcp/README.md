# Obsidian über MCP mit Langflow verbinden

In dieser Übung liest ein Langflow-Agent Notizen aus einem separaten Demo-Vault. Verwendet wird direkt der eingebaute **Streamable-HTTP(s)-MCP-Endpunkt** des Obsidian-Plug-ins **Local REST API with MCP 5.1.0**. 

## A. Aufgabe

Folge gerne den Anweisungen im `demo_vault` für die jeweiligen Tracks oder lass es dir über den KI-Agenten und die Obsidian-MCP-Anbindung erklären, was zu tun ist.
Sieh den Agenten bswp. als einen hilfreichen Tutor, der dich durch den Beginner-Track des Workshops lotst.

Ansonsten kannst du auch direkt folgendes ausprobieren:

Stelle im Playground nacheinander diese Fragen:

```text
Welche MeetingNotes gibt es? Nenne nur Dateiname und Monat.
```

```text
Fasse die Entwicklung von Honey for Heroes über alle MeetingNotes zusammen. Nenne Zahlen mit Monat und belege jede Aussage mit dem Dateinamen.
```

```text
Welche offenen Aufgaben betreffen Verteilung oder Nachhaltigkeit? Gruppiere sie nach Monat.
```

**Erwartetes Ergebnis:** Der Agent findet die drei Dateien unter `MeetingNotes`, liest relevante Inhalte und liefert eine deutschsprachige, nachvollziehbare Zusammenfassung. Keine Datei erhält einen neuen Änderungszeitpunkt oder Inhalt.

**Beobachtungsfragen:**

- Welcher Aufruf sucht und welcher liest den vollständigen Inhalt?
- Welche Argumente hat das Modell selbst gewählt?
- Enthält die Toolantwort Rohdaten, während erst der Agent daraus Sprache erzeugt?
- Was verhindert technisch, dass der Agent Notizen verändert?

# Setup (für alle, die es auf ihrem System aufsetzen und testen wollen)

## Voraussetzungen

- Langflow läuft.
- Obsidian Desktop ist installiert.
- `demo_vault` wurde in Obsidian als Vault geöffnet.
- Community-Plug-ins dürfen in deiner Umgebung installiert werden. 

## 1. Demo-Vault öffnen

1. Öffne Obsidian und wähle **Open folder as vault**.
2. Wähle den Ordner `beginners_track/01_obsidian_mcp/demo_vault`.
3. Öffne `00_Workshop-Start.md` und prüfe, dass `MeetingNotes` drei Monatsnotizen enthält.

## 2. Plug-in installieren und prüfen

1. Öffne **Settings > Community plugins**, aktiviere Community-Plug-ins und suche nach **Local REST API with MCP**.
2. Installiere und aktiviere Version **5.1.0**. Prüfe die Quelle und Berechtigungen vor der Installation.
3. Ablauf konkret: **Settings (Zahnrad-Icon unten im Vault-Bereich) > Externe Erweiterungen > Community Plugins / ganz unten bereits installiertes "Local REST API with MCP" installieren / wählen > Optionen (HTTP enablen, ACHTUNG: nur bei rein lokalem Gebrauch!) > "How to access via MCP" klicken > Config hieraus mit den korrekten Werten übernehmen.** 
4. Der MCP-Endpunkt lautet:

```text
https://127.0.0.1:27124/mcp/

oder für HTTP:
http://127.0.0.1:27123/mcp/
```

Obsidian muss während der Übung geöffnet bleiben.

ACHTUNG: du musst das Plugin für jeden Vault installieren und aktivieren! Prüfe das, wenn du deinen Vault wechselst.

## 3. TLS-Vertrauen einrichten

**Kurzfassung:** Bevorzuge HTTPS mit importiertem Zertifikat; das lokale HTTP ist nur eine Notlösung für den eigenen Rechner, darf nie extern erreichbar sein und muss danach wieder deaktiviert werden.

Der bevorzugte Weg ist HTTPS mit geprüfter Verbindung:

1. Lade die lokale Zertifizierungsstelle des Plug-ins über `https://127.0.0.1:27124/obsidian-local-rest-api.crt` herunter.
2. Prüfe, dass die Datei wirklich von deiner lokalen Plug-in-Instanz stammt.
3. Importiere sie in den Zertifikatsspeicher des Betriebssystems beziehungsweise in den Trust Store der Umgebung, in der Langflow läuft.
4. Starte Langflow nach dem Import neu und lasse TLS-Prüfung aktiviert.

Die Zertifizierungsstelle ist auf lokale Namen beschränkt. Trotzdem soll sie nur auf deinem eigenen Rechner installiert werden.

**Lokaler Fallback:** Falls die Workshop-Umgebung die lokale Zertifizierungsstelle nicht übernehmen kann, aktiviere vorübergehend in Obsidian **Enable HTTP server** und verwende ausschließlich lokal `http://127.0.0.1:27123/mcp/`. HTTP schützt den Token nicht auf dem Transportweg. Nutze diesen Weg nur auf einem kontrollierten Rechner, binde den Server nie an eine externe Schnittstelle und deaktiviere HTTP danach wieder. Das pauschale Abschalten der TLS-Prüfung ist nicht der bevorzugte Weg.

## 4. MCP Server in Langflow anlegen

1. Kopiere deinen API-Schlüssel aus **Settings > Local REST API > Optionen > "How to access via MCP"** in die Zwischenablage. 
2. Öffne in Langflow **Settings > MCP Servers**.
3. Füge einen neuen MCP Server hinzu.
4. Die Config hierfür erhältst du als `JSON` aus den `Optionen` des Obsidian Plugins und es sollte in etwa so aussehen:

```json
{
  "mcpServers": {
    "obsidian": {
      "type": "http",
      "url": "https://127.0.0.1:27124/mcp/",
      "headers": {
        "Authorization": "Bearer HIER_STEHT_DEIN_TOKEN"
      }
    }
  }
}

oder HTTP:

{
  "mcpServers": {
    "obsidian": {
      "type": "http",
      "url": "http://127.0.0.1:27123/mcp/",
      "headers": {
        "Authorization": "Bearer HIER_STEHT_DEIN_TOKEN"
      }
    }
  }
}
```

Herzlichen Glückwunsch, du hast dein erstes externes Tool über MCP angebunden. Nun kannst du mittels natürlicher Sprache und KI-Agent mit dem Tool interagieren!

## Troubleshooting

- **Zertifikatsfehler:** Prüfe den Trust Store der tatsächlich laufenden Langflow-Umgebung. Browser-Vertrauen allein reicht bei einem separaten Python-Prozess möglicherweise nicht.
- **401/403:** Das Credential muss den vollständigen Wert mit `Bearer ` enthalten; im Headerfeld steht nur `OBSIDIAN_AUTHORIZATION`. Häufige Ursache ist ein versehentlich doppeltes `Bearer`-Präfix, wenn der aus der Plug-in-Seite kopierte Wert bereits `Bearer` enthielt.
- **Verbindung abgelehnt:** Obsidian und das Plug-in müssen laufen. Prüfe URL, abschließenden Slash und Port.
- **Keine Tools:** Entferne den Servereintrag, registriere ihn neu und prüfe Plug-in-Version 5.1.0.
- **Leere Suche:** Öffne den richtigen `demo_vault` und prüfe `MeetingNotes`.

## Sicherheit

Allgemeine Sicherheitsgrundsätze stehen im [Track-README](../README.md#sicherheit). Für diese Übung gilt zusätzlich: Der API-Schlüssel gewährt je nach freigegebenem Tool weitreichenden Zugriff auf den Vault. Verwende einen Demo-Vault, gib nur benötigte Tools frei, rotiere einen versehentlich veröffentlichten Schlüssel in den Plug-in-Einstellungen und entferne den Langflow-Server sowie das Credential nach der Übung auf gemeinsam genutzten Rechnern.

## Quellen

- [Local REST API with MCP](https://github.com/coddingtonbear/obsidian-local-rest-api)
- [Langflow 1.11: MCP-Client](https://docs.langflow.org/1.11.0/mcp-client)
