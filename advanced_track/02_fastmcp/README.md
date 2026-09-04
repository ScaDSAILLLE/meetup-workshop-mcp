# FastMCP: vom leeren Server zum kombinierten Assistenten

Dieser Workshop entwickelt in sieben kleinen Schritten einen MCP-Server mit FastMCP. Jeder Schritt ist eigenständig startbar. Die Beispiele verwenden Streamable HTTP und sind bewusst ohne API-Key, Datenbank oder externen Dienst ausführbar.

> **Datenschutzhinweis:** Alle Namen, Kontakte, Termine und Aufgaben in diesem Track sind frei erfunden. Verwende im Workshop keine echten persönlichen, vertraulichen oder produktiven Daten.

## Rahmen

- **Dauer:** 120 Minuten plus optionale Übungen
- **Zielgruppe:** Python-Entwicklerinnen und -Entwickler mit ersten MCP-Grundkenntnissen
- **Format:** geführtes Coding mit Beobachtungsaufträgen
- **Referenz:** Python 3.12 oder 3.13, FastMCP 2.x, Langflow 1.11.3

## Lernziele

Nach dem Workshop kannst du:

- einen FastMCP-Server erstellen und per Streamable HTTP bereitstellen,
- Tools mit Typen, Docstrings, Validierung und Sicherheitsannotation registrieren,
- statische Resources von parametrisierten Resource Templates unterscheiden,
- wiederverwendbare Prompts anbieten,
- Tools, Resources, Templates und Prompts sinnvoll kombinieren,
- einen MCP-Server in Langflow und optional im MCP Inspector untersuchen,
- die Grenzen einer nicht persistenten Workshop-Demo benennen.

## Voraussetzungen

- Python 3.12 oder 3.13
- [`uv`](https://docs.astral.sh/uv/) installiert
- ein Terminal im Verzeichnis `advanced_track/02_fastmcp`
- für die Client-Übung: Langflow **1.11.3**
- optional: Node.js und npm für den MCP Inspector

Für diesen Track werden keine Zugangsdaten und keine `.env`-Datei benötigt.

## Setup

Installiere die exakt in `uv.lock` aufgelösten Abhängigkeiten:

```bash
uv sync --link-mode copy
```

Prüfe die Installation vollständig offline, nachdem die Pakete installiert sind:

```bash
uv run pytest
uv run ruff check .
```

Alle Server binden nur an `127.0.0.1`. Die vollständige MCP-URL lautet immer `http://127.0.0.1:<PORT>/mcp`. Beende einen laufenden Server mit `Strg+C`, bevor du zum nächsten Schritt wechselst.

## Lernpfad

| Schritt | Datei | Port | Neue MCP-Komponente |
|---|---|---:|---|
| 00 | `00_minimaler_server.py` | 8000 | Server und Transport |
| 01 | `01_erstes_tool.py` | 8001 | erstes read-only Tool |
| 02 | `02_weitere_tools.py` | 8002 | mehrere Tools und Schemas |
| 03 | `03_statische_resources.py` | 8003 | statische Resources |
| 04 | `04_resource_templates.py` | 8004 | Resource Templates |
| 05 | `05_prompts.py` | 8005 | Prompts |
| 06 | `06_kombinierter_assistent.py` | 8006 | Kombination und Schreibgrenzen |

## Schritt 00: Minimaler Server

**Start**

```bash
uv run python 00_minimaler_server.py
```

**Aufgabe:** Verbinde einen MCP-Client mit `http://127.0.0.1:8000/mcp` und frage die Fähigkeiten des Servers ab.

**Erwartetes Ergebnis:** Die Verbindung und MCP-Initialisierung funktionieren. Es werden noch keine Tools, Resources oder Prompts angeboten.

**Beobachtungsfrage:** Welche Informationen handeln Client und Server aus, obwohl noch keine fachliche Funktion registriert ist?

**MCP-Konzept:** FastMCP übernimmt Protokollserver, Capability Negotiation und Streamable-HTTP-Transport. `mcp.run()` blockiert absichtlich bis zum Abbruch; ausführbarer Code gehört deshalb nicht dahinter.

## Schritt 01: Erstes read-only Tool

**Start**

```bash
uv run python 01_erstes_tool.py
```

**Aufgabe:** Lass den Client das technische Tool `begruesse` zuerst mit deinem Vornamen und danach mit einer leeren Zeichenkette aufrufen. Der ASCII-Name hält den Toolbezeichner mit dem MCP-Namensschema kompatibel; die sichtbaren Texte verwenden weiterhin korrekte Umlaute.

**Erwartetes Ergebnis:** Der erste Aufruf liefert eine Begrüßung. Der zweite wird mit einer verständlichen Validierungsfehlermeldung abgewiesen. Der Client erkennt `name` als erforderlichen String-Parameter.

**Beobachtungsfrage:** Welche Teile von Name, Docstring, Type Hint und Annotation werden dem Modell als Tool-Metadaten sichtbar?

**MCP-Konzept:** Ein Tool ist eine vom Modell aufrufbare Aktion. `readOnlyHint` und `openWorldHint` beschreiben seine Wirkung; sie ersetzen keine serverseitige Zugriffskontrolle.

## Schritt 02: Weitere Tools

**Start**

```bash
uv run python 02_weitere_tools.py
```

**Aufgabe:** Berechne `21 + 21`, konvertiere `20 °C` und fordere eine Empfehlung für `Fortgeschritten` an. Probiere anschließend einen unbekannten Erfahrungswert.

**Erwartetes Ergebnis:** Der Client sieht drei getrennte Tools mit unterschiedlichen Eingabeschemas. Ergebnisse sind deterministisch; ungültige Kategorien werden abgewiesen.

**Beobachtungsfrage:** Wann sind mehrere kleine, klar benannte Tools besser als ein universelles Tool mit vielen optionalen Parametern?

**MCP-Konzept:** JSON-Schemas entstehen aus Python-Typen. Kleine Tool-Schnittstellen erleichtern Auswahl, Validierung und Least Privilege.

## Schritt 03: Statische Resources

**Start**

```bash
uv run python 03_statische_resources.py
```

**Aufgabe:** Liste die Resources auf und lies `workshop://info` sowie `workshop://agenda`.

**Erwartetes Ergebnis:** Beide festen URIs sind auffindbar. Die erste Resource liefert JSON, die zweite Markdown; kein Tool-Aufruf ist nötig.

**Beobachtungsfrage:** Warum ist eine Resource für referenzierbaren Kontext geeigneter als ein Tool ohne Parameter?

**MCP-Konzept:** Resources stellen adressierbaren, lesbaren Kontext bereit. URI und MIME-Typ helfen dem Client bei Identifikation und Darstellung.

## Schritt 04: Resource Templates

**Start**

```bash
uv run python 04_resource_templates.py
```

**Aufgabe:** Liste die Resource Templates auf. Lies danach `notizen://mira/übung` und `termine://2026-09/3`. Teste auch einen ungültigen Tag.

**Erwartetes Ergebnis:** Der Client erkennt URI-Platzhalter. Konkrete URIs liefern fiktive JSON-Daten; Tage außerhalb des Septembers werden abgewiesen.

**Beobachtungsfrage:** Welche Validierung muss der Server trotz eines syntaktisch passenden URI-Templates selbst durchführen?

**MCP-Konzept:** Resource Templates verbinden adressierbare Resources mit URI-Parametern. Die Parameter stammen aus der URI und werden von FastMCP an die Funktion übergeben.

## Schritt 05: Prompts

**Start**

```bash
uv run python 05_prompts.py
```

**Aufgabe:** Liste die Prompts auf und rufe `tool_review` mit einem erfundenen Tool-Namen und Ziel ab. Vergleiche das Ergebnis mit `lernreflexion`.

**Erwartetes Ergebnis:** Der Client erhält wiederverwendbare, parametrisierte Nachrichtenentwürfe. Es wird weder ein Tool ausgeführt noch automatisch ein Sprachmodell aufgerufen.

**Beobachtungsfrage:** Wer entscheidet bei einem MCP-Prompt, ob und mit welchem Modell der erzeugte Text weiterverarbeitet wird?

**MCP-Konzept:** Prompts sind vom Client auswählbare Vorlagen. Der Server liefert Nachrichteninhalt, nicht die Modellantwort.

## Schritt 06: Kombinierter Assistent

**Start**

```bash
uv run python 06_kombinierter_assistent.py
```

**Aufgabe:** Lies zuerst `assistent://hinweise`, dann `aufgaben://offen`. Suche mit `suche_aufgaben`, lege eine Demo-Aufgabe an und markiere sie erst nach expliziter Bestätigung als erledigt. Erzeuge abschließend den Prompt `tagesplanung`.

**Erwartetes Ergebnis:** Lesende und schreibende Fähigkeiten sind getrennt. Ohne `bestätigen=true` scheitert das Erledigen. Änderungen sind im laufenden Prozess sichtbar, verschwinden aber nach einem Neustart.

**Beobachtungsfrage:** Welche Information ist technisch erzwungen und welche ist lediglich ein Hinweis an Client oder Modell?

**MCP-Konzept:** Ein Server kann alle MCP-Primitiven kombinieren. Sicherheitsannotation, Bestätigungsparameter und Validierung reduzieren Risiken, ersetzen aber weder Authentifizierung noch Autorisierung und Persistenzkonzepte.

## Langflow 1.11.3 anbinden

1. Starte genau einen Workshop-Server und notiere seine vollständige URL, beispielsweise `http://127.0.0.1:8002/mcp`.
2. Öffne in Langflow 1.11.3 einen Flow und füge die Komponente **MCP Tools** hinzu.
3. Füge in der Komponente einen MCP-Server hinzu und wähle **Streamable HTTP** als Transport.
4. Trage einen frei gewählten Namen und die vollständige URL einschließlich `/mcp` ein.
5. Aktualisiere die Komponentenliste. Wähle ein angebotenes Tool aus und verbinde den Tool-Ausgang mit einem Agenten.
6. Starte einen Lauf und kontrolliere im Trace, welches Tool mit welchen Argumenten aufgerufen wurde.

Läuft Langflow selbst in Docker, zeigt `127.0.0.1` in der Containerperspektive auf den Container. Verwende auf Docker Desktop stattdessen häufig `http://host.docker.internal:<PORT>/mcp`. In nativen oder abweichenden Docker-Setups muss die Host-Adresse passend konfiguriert werden; dafür müsste der Workshop-Server bewusst an eine erreichbare Schnittstelle gebunden und durch Firewall-Regeln geschützt werden.

Langflow stellt primär Tools für Agenten bereit. Resources und Prompts lassen sich je nach Komponente und Client-Unterstützung nicht in derselben Oberfläche untersuchen. Nutze dafür optional den MCP Inspector.

## Optional: MCP Inspector

Starte zuerst einen Workshop-Server. Rufe dann den Inspector über eine von dir geprüfte Node.js/npm-Installation auf:

```bash
npx @modelcontextprotocol/inspector
```

Wähle **Streamable HTTP**, trage die jeweilige URL mit `/mcp` ein und untersuche nacheinander Tools, Resources, Resource Templates und Prompts. `npx` kann beim ersten Aufruf Pakete aus dem Internet laden; in eingeschränkten Umgebungen muss die Installation vorab freigegeben werden.

## Übungen

1. Ergänze in Schritt 02 ein read-only Tool `minuten_in_stunden(minuten: int)` mit Validierung gegen negative Werte und einem passenden Test.
2. Ergänze in Schritt 03 die statische Resource `workshop://lernziele` mit dem MIME-Typ `application/json`.
3. Erweitere Schritt 04 um `material://{kapitel}` und definiere das Verhalten für unbekannte Kapitel.
4. Ergänze Schritt 05 um einen Prompt, der aus einer Beobachtung eine Hypothese und ein überprüfbares Experiment formuliert.
5. Entwirf für Schritt 06 persistente Speicherung auf Papier: Datenmodell, konkurrierende Zugriffe, Authentifizierung, Autorisierung, Audit-Log und Löschkonzept. Implementiere sie im Workshop nicht ungeprüft.

## Sicherheit und Grenzen

- Die Server lauschen absichtlich nur auf `127.0.0.1` und besitzen keine Authentifizierung.
- Veröffentliche sie nicht im Netzwerk oder Internet. Für Produktion sind TLS, Authentifizierung, Autorisierung, Rate Limits, Logging und eine restriktive Netzwerkkonfiguration erforderlich.
- Tool-Annotationen sind Hinweise für Clients. Ein bösartiger oder fehlerhafter Client kann sie ignorieren.
- Behandle alle Tool-Argumente als nicht vertrauenswürdig. Die Beispiele validieren relevante Werte, sind aber kein vollständiges Policy-System.
- Schreibtools in Schritt 06 sind **nicht persistent**. Sie verändern nur eine In-Memory-Liste und verlieren alle Änderungen beim Neustart.
- `aufgabe_erledigen` verlangt eine explizite Bestätigung. Bei realen irreversiblen Aktionen wären zusätzlich Benutzeridentität, Berechtigungsprüfung, Vorschau und Audit-Trail nötig.
- Resources können sensible Daten preisgeben. Verwende hier ausschließlich die enthaltenen fiktiven Demo-Daten.
- Keines der Beispiele startet ein Sprachmodell oder sendet Daten an externe Dienste.

## Troubleshooting

**`uv sync` meldet eine unpassende Python-Version**

Installiere Python 3.12 oder 3.13 und wähle die Version beispielsweise mit `uv python pin 3.12`. Python 3.14 ist für diesen Track bewusst noch nicht freigegeben.

**Adresse oder Port ist bereits belegt**

Beende den alten Prozess mit `Strg+C`. Alternativ ändere den Port im betreffenden Skript und übernimm ihn auch in der Client-URL.

**404 oder keine MCP-Verbindung**

Prüfe Transport und vollständigen Pfad. Korrekt ist beispielsweise `http://127.0.0.1:8003/mcp`, nicht nur die Host-Adresse und nicht der frühere SSE-Pfad `/sse`.

**Langflow erreicht den lokalen Server nicht**

Prüfe, ob Langflow nativ oder in einem Container läuft. `127.0.0.1` bezeichnet immer das System beziehungsweise den Container des aufrufenden Prozesses. Beachte die Docker-Hinweise im Langflow-Abschnitt.

**Ein Schritt zeigt die falschen Komponenten**

Kontrolliere Port und laufenden Prozess, entferne veraltete Client-Konfigurationen und aktualisiere die Komponentenliste. Jeder Schritt ist ein eigener Server.

**Eine Änderung aus Schritt 06 ist verschwunden**

Das ist beabsichtigt: Die Schreibtools arbeiten ausschließlich im flüchtigen Speicher. Beim Neustart wird der fiktive Ausgangszustand geladen.

**Umlaute in einer Resource-URI funktionieren nicht**

Clients können nicht-ASCII-Zeichen prozentkodieren. Wähle das Template über die Client-Oberfläche oder verwende die vom Client korrekt kodierte URI.

## Quellen

- [Model Context Protocol: Architektur](https://modelcontextprotocol.io/docs/learn/architecture)
- [Model Context Protocol: Server-Konzepte](https://modelcontextprotocol.io/docs/learn/server-concepts)
- [FastMCP-Dokumentation](https://gofastmcp.com/)
- [FastMCP: HTTP-Deployment](https://gofastmcp.com/deployment/http)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
- [Langflow-Dokumentation: MCP](https://docs.langflow.org/mcp-server)
- [uv-Dokumentation](https://docs.astral.sh/uv/)

Die Abhängigkeitsgrenzen stehen in `pyproject.toml`; die konkret geprüften Versionen hält `uv.lock` fest.
