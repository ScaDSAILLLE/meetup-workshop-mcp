# Obsidian über MCP mit Langflow verbinden

In dieser Übung liest ein Langflow-Agent Notizen aus einem separaten Demo-Vault. Verwendet wird direkt der eingebaute **Streamable-HTTP-MCP-Endpunkt** des Obsidian-Plug-ins **Local REST API with MCP 5.1.0**. Eine zusätzliche `mcp-obsidian`-Bridge ist weder nötig noch vorgesehen.

## Lernziele

- einen authentifizierten Streamable-HTTP-MCP-Server registrieren,
- einen Bearer-Token als Langflow-Credential referenzieren,
- nur Lese-Tools freigeben,
- Suchaufruf, Dateizugriff und Agentenantwort in Agent Steps unterscheiden.

## Voraussetzungen

- Langflow 1.11.3 läuft.
- Obsidian Desktop ist installiert.
- `demo_vault` wurde in Obsidian als Vault geöffnet.
- Community-Plug-ins dürfen in deiner Umgebung installiert werden.

## 1. Demo-Vault öffnen

1. Öffne Obsidian und wähle **Open folder as vault**.
2. Wähle den Ordner `beginners-track/01_obsidian_mcp/demo_vault`.
3. Öffne `00_Workshop-Start.md` und prüfe, dass `MeetingNotes` drei Monatsnotizen enthält.

## 2. Plug-in installieren und prüfen

1. Öffne **Settings > Community plugins**, aktiviere Community-Plug-ins und suche nach **Local REST API with MCP**.
2. Installiere und aktiviere Version **5.1.0**. Prüfe die Quelle und Berechtigungen vor der Installation.
3. Öffne **Settings > Local REST API**. Dort erzeugt deine lokale Installation einen eigenen API-Schlüssel. Teile oder dokumentiere ihn nicht.
4. Der MCP-Endpunkt lautet:

```text
https://127.0.0.1:27124/mcp/
```

Obsidian muss während der Übung geöffnet bleiben.

## 3. TLS-Vertrauen einrichten

Der bevorzugte Weg ist HTTPS mit geprüfter Verbindung:

1. Lade die lokale Zertifizierungsstelle des Plug-ins über `https://127.0.0.1:27124/obsidian-local-rest-api.crt` herunter.
2. Prüfe, dass die Datei wirklich von deiner lokalen Plug-in-Instanz stammt.
3. Importiere sie in den Zertifikatsspeicher des Betriebssystems beziehungsweise in den Trust Store der Umgebung, in der Langflow läuft.
4. Starte Langflow nach dem Import neu und lasse TLS-Prüfung aktiviert.

Die Zertifizierungsstelle ist auf lokale Namen beschränkt. Trotzdem soll sie nur auf deinem eigenen Rechner installiert werden.

**Transparenter lokaler Fallback:** Falls die Workshop-Umgebung die lokale Zertifizierungsstelle nicht übernehmen kann, aktiviere vorübergehend in Obsidian **Enable HTTP server** und verwende ausschließlich lokal `http://127.0.0.1:27123/mcp/`. HTTP schützt den Token nicht auf dem Transportweg. Nutze diesen Weg nur auf einem kontrollierten Rechner, binde den Server nie an eine externe Schnittstelle und deaktiviere HTTP danach wieder. Das pauschale Abschalten der TLS-Prüfung ist nicht der bevorzugte Weg.

## 4. Credential in Langflow anlegen

1. Kopiere deinen API-Schlüssel aus **Settings > Local REST API** nur in die Zwischenablage.
2. Öffne in Langflow **Settings > Global Variables**.
3. Erstelle eine Variable vom Typ **Credential** mit dem Namen `OBSIDIAN_AUTHORIZATION`.
4. Trage als Wert `Bearer ` gefolgt von deinem lokalen API-Schlüssel ein und speichere die Variable.
5. Entferne den Schlüssel wieder aus der Zwischenablage, sofern dein Betriebssystem das unterstützt.

Der Variablenwert darf weder in Markdown noch direkt in einen Flow-Export geschrieben werden.

## 5. MCP-Server registrieren

1. Öffne **Settings > MCP Servers > Add MCP Server**.
2. Wähle **HTTP/SSE**.
3. Setze den Namen auf `obsidian-local`.
4. Setze die Streamable-HTTP/SSE-URL auf `https://127.0.0.1:27124/mcp/` oder ausschließlich für den beschriebenen Fallback auf die lokale HTTP-URL.
5. Füge einen Header mit Schlüssel `Authorization` hinzu. Als Wert trägst du exakt den Variablennamen `OBSIDIAN_AUTHORIZATION` ein, nicht den geheimen Wert.
6. Speichere. Langflow sollte die verfügbaren Tools anzeigen.

## 6. Nur Lese-Tools verbinden

1. Öffne `MCP Spielwiese.json` über **Projects > Upload a flow** oder verwende einen Flow aus Chat Input, Agent und Chat Output.
2. Ziehe `obsidian-local` aus der **MCP sidebar** auf die Arbeitsfläche.
3. Aktiviere ausschließlich diese Tools, soweit sie in 5.1.0 angezeigt werden: `vault_list`, `vault_read`, `vault_get_document_map`, `search_simple`, `search_query`, `tag_list` und `active_file_get_path`.
4. Deaktiviere insbesondere `vault_write`, `vault_write_binary`, `vault_append`, `vault_patch`, `vault_delete`, `vault_move`, `vault_copy`, `command_execute` und `open_file`.
5. Aktiviere **Tool Mode** und verbinde **Toolset > Agent Tools**.

## 7. Aufgabe

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

## Erfolgskriterien

- Die HTTPS-Verbindung ist vertrauenswürdig oder der lokale HTTP-Fallback ist bewusst dokumentiert und zeitlich begrenzt.
- Das Authorization-Credential wird nur per Variablenname referenziert.
- Agent Steps zeigen ausschließlich Lesezugriffe.
- Die Antwort nennt die passenden Monate, Zahlen und Quelldateien.

## Troubleshooting

- **Zertifikatsfehler:** Prüfe den Trust Store der tatsächlich laufenden Langflow-Umgebung. Browser-Vertrauen allein reicht bei einem separaten Python-Prozess möglicherweise nicht.
- **401/403:** Das Credential muss den vollständigen Wert mit `Bearer ` enthalten; im Headerfeld steht nur `OBSIDIAN_AUTHORIZATION`.
- **Verbindung abgelehnt:** Obsidian und das Plug-in müssen laufen. Prüfe URL, abschließenden Slash und Port.
- **Keine Tools:** Entferne den Servereintrag, registriere ihn neu und prüfe Plug-in-Version 5.1.0.
- **Leere Suche:** Öffne den richtigen `demo_vault` und prüfe `MeetingNotes`.

## Sicherheit

Der API-Schlüssel gewährt je nach freigegebenem Tool weitreichenden Zugriff auf den Vault. Verwende einen Demo-Vault, gib nur benötigte Tools frei, rotiere einen versehentlich veröffentlichten Schlüssel in den Plug-in-Einstellungen und entferne den Langflow-Server sowie das Credential nach der Übung auf gemeinsam genutzten Rechnern.

## Quellen

- [Local REST API with MCP](https://github.com/coddingtonbear/obsidian-local-rest-api)
- [Langflow 1.11: MCP-Client](https://docs.langflow.org/1.11.0/mcp-client)
- [Langflow: globale Variablen](https://docs.langflow.org/configuration-global-variables)
