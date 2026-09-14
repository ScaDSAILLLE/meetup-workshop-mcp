# Progressive Disclosure mit MCP

Ein MCP-Client kann einen großen Toolkatalog anbinden, ohne jedes Schema sofort an ein Sprachmodell
zu senden. Diese Demo vergleicht einen vollständigen Modus mit einer progressiven Auswahl. Beide
Modi greifen per FastMCP auf denselben Katalog zu. Die Weboberfläche zeigt den konkreten Ablauf und
beobachtete Metriken eines einzelnen Laufs, nicht die Genauigkeit des Modells und keinen Benchmark.

## Lernziele

Nach dem Track kannst du:

- Progressive Disclosure von einer vollständigen Tool-Exposition unterscheiden,
- initial sichtbare Tools und später ausgewählte Kandidaten getrennt benennen,
- eine lokale Katalogsuche und dynamische Schema-Auswahl nachvollziehen,
- kumulativ gesendete Schema-Tokens von Endpoint-Input- und Output-Tokens unterscheiden,
- den getrennten Selektions- und Ausführungsdialog dieser Demo erklären,
- Nulltreffer, mutierende Tools und Prompt Injection als relevante Grenzen erkennen.

## Architektur

```text
Browser  -- POST /api/demo -->  Starlette-Backend  -->  ScaDS Chat Completions
                                  |
                                  +-- FastMCP Client (In-Memory)
                                          |
                                          +-- MCP-Toolkatalog
```

Der echte Einstieg ist ausschließlich:

```bash
uv run python -m backend.main
```

Frontend, API und MCP-Server laufen dabei in einem Prozess. Es ist kein separater MCP-Server nötig.
Die Toolzahl wird bei jedem Lauf mit `list_tools()` vom Server gelesen und nicht im Frontend
festgeschrieben.

# A. Aufgabe

### Schritt 1: Vollständigen Katalog beobachten

Verwende als ersten Prompt:

```text
Wie ist das Wetter in Leipzig?
```

Erwartete Beobachtungen:

- Beide Panels melden dieselbe dynamisch geladene Kataloggröße.
- Im vollständigen Modus entspricht „Initial sichtbar“ der Kataloggröße.
- Der vollständige Modus sendet den ganzen Katalog erneut, wenn nach dem Tool-Ergebnis eine weitere
  LLM-Antwort angefordert wird.
- Der progressive Modus zeigt zunächst genau `search_tools` und danach Wetter-Kandidaten.
- Die konkreten Tool-Auswahl- und Tokenwerte können vom Modell und Endpoint abhängen.

Öffne parallel `backend/naive_mode.py`. Der Dialog aus Systemnachricht, Nutzeranfrage,
Assistant-Tool-Call und Tool-Ergebnis wird für die abschließende Antwort fortgeführt.

### Schritt 2: Getrennte Selektionsphase nachvollziehen

Verwende:

```text
Zeige mir den Status der Bestellung 3001.
```

Erwartete Beobachtungen:

- Der erste progressive LLM-Aufruf sieht nur das Such-Tool.
- Die lokale Suche übersetzt „Bestellung“ zu `order` und liefert höchstens fünf Kandidaten.
- Der Schritt „Neuer Dialog für die Ausführungsphase“ macht die bewusste Trennung sichtbar.
- Der Suchdialog wird nicht an die Ausführungsphase angehängt. Die Nutzeranfrage wird in einen neuen
  Dialog kopiert, der nur die Kandidaten-Schemas sieht.
- „Schema-Tokens kumulativ“ enthält das Such-Schema einmal und Kandidaten-Schemas für jeden
  anschließenden LLM-Aufruf.

Diese Trennung ist eine konkrete Architekturentscheidung der Demo. Sie spart nicht automatisch
Nachrichten-Tokens und ist kein fortlaufender Tool-Calling-Dialog über beide Phasen. Innerhalb der
Ausführungsphase bleibt der Dialog bis zur Antwort dagegen nachvollziehbar fortlaufend.

### Schritt 3: Fachgebiet wechseln

Verwende:

```text
Berechne die Steuer für 120 Euro in Deutschland.
```

Erwartete Beobachtungen:

- Statt Wetter- oder Bestelltools erscheinen Finanz-Kandidaten.
- „Kandidaten ausgewählt“ ist eine eigene Metrik und nicht mit „Initial sichtbar“ identisch.
- Endpoint-Input und -Output werden nur angezeigt, wenn der Endpoint beide Usage-Werte liefert.
- Lokal gezählte Schema-Tokens und Endpoint-Input-Tokens sind verschiedene Messgrößen.

### Schritt 4: Nulltreffer untersuchen

Verwende beispielsweise:

```text
Schreibe ein Sonett über Quantenlyrik.
```

Erwartete Beobachtungen:

- Wenn die vom Modell erzeugten Suchbegriffe keinen Katalogbegriff treffen, liefert die Suche eine
  leere Liste statt willkürlicher Tools.
- Der progressive Ablauf endet dann ohne Fach-Tool-Aufruf mit einem transparenten Hinweis.
- Abhängig von den gewählten Suchbegriffen kann das Modell dennoch einen allgemeinen Begriff aus
  dem Katalog treffen. Das ist eine Beobachtung des Laufs, keine zugesicherte Klassifikation.

## Wissensteil

### Was Progressive Disclosure hier bedeutet

Der vollständige Modus übergibt bei jedem LLM-Aufruf alle registrierten Schemas. Der progressive
Modus exponiert zuerst nur dieses Meta-Tool:

```text
search_tools(query) -> bis zu fünf passende Tool-Schemas
```

Die Suche in `backend/tool_search.py` ist deterministisch: Sie zerlegt Text in Wörter, ergänzt
deutsche Begriffe um englische Entsprechungen, bewertet Namens- und Beschreibungstreffer und
sortiert reproduzierbar. Sie ist keine semantische Vektorsuche und verwendet selbst kein LLM.

Progressive Disclosure ist hier Anwendungscode oberhalb von MCP. MCP liefert und beschreibt die
Tools; die Anwendung entscheidet, welche Schemas der jeweilige Modellaufruf sehen darf. Der
MCP-Standard schreibt diese konkrete Suchstrategie nicht vor.

### Bedeutung der Metriken

| Anzeige | Bedeutung |
|---|---|
| Tools im Katalog | Aktuell per MCP `list_tools()` geladene Toolzahl |
| Initial sichtbar | Schemas im ersten LLM-Aufruf des Modus |
| Kandidaten ausgewählt | Treffer der lokalen Suche; im vollständigen Modus nicht verwendet |
| Schema-Tokens kumulativ | Summe der lokal tokenisierten Tool-Schemas über alle LLM-Aufrufe |
| Endpoint Input / Output | Kumulierte `usage`-Werte des Endpoints, nur soweit vollständig vorhanden |
| LLM-Aufrufe | Tatsächlich ausgeführte Chat-Completions-Requests |

Die lokale Schema-Zählung serialisiert die Schemas als JSON und verwendet TikTokens
`cl100k_base`. Das ist eine konsistente Vergleichsgröße, aber nicht zwingend der interne Tokenizer
des konfigurierten Modells. Endpoint-Input-Tokens umfassen neben Schemas auch Nachrichten und
anbieterabhängigen Overhead. Fehlt `usage` in nur einem Request, zeigt die Demo für die jeweilige
Endpoint-Summe „nicht gemeldet“, statt eine unvollständige Summe als vollständig auszugeben.

Die Balken vergleichen nur kumulierte Schema-Tokens dieses einen Laufs. Warteschlangen, Caching,
Modellverhalten und Promptwahl werden nicht kontrolliert. Aus der Anzeige folgen keine Aussagen zu
Qualität, Latenz oder allgemeiner Effizienz.

### Was ist real und was simuliert?

| Bestandteil | Einordnung |
|---|---|
| LLM-Aufrufe über den konfigurierten ScaDS-Endpoint | real |
| MCP-Protokollaufrufe per FastMCP In-Memory-Transport | real |
| Katalogsuche und Schemaauswahl im Backend | real |
| Kumulative Metrikerfassung | real für diesen Lauf |
| Wetter-, Kunden-, Bestell- und Finanzdaten | simulierte feste Daten |
| Schreibende Toolnamen wie Löschen, Bezahlen oder Deployen | simuliert; keine externen Systeme werden verändert |

Die Demo beweist damit den Kontrollfluss und die Schemaexposition, nicht die Eignung der
simulierten Fachtools für Produktion.

## Übungen

1. Setze in `run_progressive_mode()` `top_k` von fünf auf drei und vergleiche Kandidaten sowie
   kumulierte Schema-Tokens für alle Pflichtprompts.
2. Ergänze einen deutschen Suchbegriff in `KEYWORD_MAP` und schreibe zuerst einen fehlschlagenden
   Offline-Test.
3. Entferne testweise die Kandidaten-Schemas aus dem finalen Antwortaufruf. Diskutiere, ob dein
   Endpoint Tool-Calls ohne erneut übergebene Schemas akzeptiert und wie die Metrik zu interpretieren
   wäre.
4. Ersetze die Stichwortsuche konzeptionell durch Embeddings. Definiere Schwellenwert, Nulltreffer,
   Berechtigungsfilter und Messgrößen, bevor du Code schreibst.
5. Teile Tools in read-only und mutierend ein. Entwirf eine Policy, die mutierende Kandidaten erst
   nach expliziter Nutzerbestätigung freigibt.

# B. Setup (für alle, die es auf ihrem System aufsetzen und testen wollen)

### 1. Root-Konfiguration prüfen

Es gibt genau eine `.env.example` und eine persönliche `.env`, beide in der Repository-Wurzel. Lege
keine Env-Datei in diesem Track an. Die gemeinsame Vorlage verwendet:

```dotenv
SCADS_API_KEY=dein-persönlicher-key
SCADS_BASE_URL=https://llm.scads.ai/v1
SCADS_MODEL=Qwen/Qwen3.8-27B
```

`backend/config.py` bestimmt die Repository-Wurzel relativ zur eigenen Datei. Es gibt keine
Legacy-Variablen und keinen Fallback auf eine lokale Env-Datei. Teile oder committe den Key nicht.

### 2. Abhängigkeiten installieren

Wechsle in diesen Track:

```bash
cd advanced_track/01_mcp-progressive_disclosure-demo
uv sync --link-mode copy
```

`--link-mode copy` vermeidet bekannte Hardlink-Probleme unter WSL in `/mnt/c`. Auf nativen Linux-,
macOS- oder Windows-Dateisystemen genügt normalerweise auch `uv sync`.

### 3. Offline prüfen

Diese Befehle brauchen keinen API-Key und starten keine Demo:

```bash
uv run pytest
uv run ruff check .
```

### 4. Live-Anwendung starten

Ein Live-Lauf ist credential-abhängig und sendet den eingegebenen Prompt sowie Tool-Schemas und
Tool-Ergebnisse an den konfigurierten Endpoint.

```bash
uv run python -m backend.main
```

Öffne anschließend <http://127.0.0.1:8080>.

### API

`POST /api/demo` erwartet:

```json
{"message": "Wie ist das Wetter in Leipzig?"}
```

Die Antwort besitzt die Modi `normal` und `progressiv`. Jeder Modus enthält dynamische Toolzahlen,
Metriken und typisierte Schritte:

```json
{
  "normal": {
    "available_tool_count": 101,
    "initial_visible_tool_count": 101,
    "selected_candidate_count": 0,
    "metrics": {
      "schema_tokens_sent": 12345,
      "endpoint_input_tokens": 13000,
      "endpoint_output_tokens": 80,
      "llm_calls": 2
    },
    "steps": [{"type": "catalog_loaded", "tool_count": 101}]
  }
}
```

Die Zahlen sind nur ein Formbeispiel. Die Anwendung ermittelt Toolzahl und Messwerte zur Laufzeit.
Fehlende Endpoint-Usage-Werte werden als `null` ausgegeben.

## Sicherheitsgrenzen

- Die lokale Suche ist keine Autorisierung. Kandidaten müssen zusätzlich nach Nutzer, Mandant und
  Berechtigung gefiltert werden.
- Toolbeschreibungen und Toolresultate können Prompt Injection enthalten und sind nicht
  vertrauenswürdig.
- Schemaauswahl ersetzt keine serverseitige Argumentvalidierung oder Fachprüfung.
- Mutierende und irreversible Tools brauchen Bestätigung, Idempotenz, Audit-Logs und Least
  Privilege. Die Demo simuliert solche Operationen nur.
- Nutzertext, ausgewählte Schemas und Tool-Ergebnisse verlassen beim Live-Lauf den Rechner in
  Richtung des konfigurierten Endpoints. Datenschutz, Aufbewahrung und Verträge sind vor echten
  Daten zu prüfen.
- API-Keys gehören ausschließlich in die Root-`.env`, nie in Quelltext, Browser oder Logs.
- Das Backend bindet absichtlich nur an `127.0.0.1`. Es enthält keine Nutzeranmeldung und ist nicht
  für eine öffentliche Bereitstellung gedacht.

## Troubleshooting

**`SCADS_API_KEY`, `SCADS_BASE_URL` oder `SCADS_MODEL` fehlt**

Prüfe die einzige `.env` in der Repository-Wurzel anhand der dortigen `.env.example`. Lege keinen
Fallback in diesem Track an. Die Offline-Tests benötigen diese Werte nicht.

**HTTP 401 oder 403**

Prüfe persönlichen Key und Berechtigung. Teile den Key nicht in Screenshots oder Ausgaben.

**HTTP 429**

Der Endpoint begrenzt Requests. Ein Vergleich kann pro Modus mehrere LLM-Aufrufe erzeugen. Warte
kurz und starte nicht mehrere Vergleiche parallel.

**Das Modell ist nicht verfügbar oder unterstützt keine Tools**

Prüfe Modellname, [Modellstatus](https://llm.scads.ai/status/) und dokumentierte Tool-Unterstützung.
Die Demo besitzt keinen stillen Modell-Fallback.

**Die progressive Auswahl findet nichts**

Prüfe in der Oberfläche den vom Modell erzeugten Suchbegriff. Ergänze nur fachlich passende
Synonyme in `KEYWORD_MAP`; gib bei Nulltreffern nicht pauschal beliebige Tools frei.

**Endpoint-Tokens zeigen „nicht gemeldet“**

Mindestens eine Antwort enthielt keine vollständigen Input- und Output-Usage-Werte. Die lokal
gezählten Schema-Tokens bleiben davon unabhängig verfügbar.

**Port 8080 ist belegt**

Beende den belegenden lokalen Prozess. Der Workshop verwendet bewusst einen festen Startbefehl und
Port, damit Anleitung und Oberfläche für alle Teilnehmenden gleich bleiben.

**`uv sync` meldet unter WSL einen Hardlink-Fehler**

Verwende `uv sync --link-mode copy` im Track-Verzeichnis.

## Quellen

- [Model Context Protocol: Architektur](https://modelcontextprotocol.io/docs/learn/architecture)
- [Model Context Protocol: Tools](https://modelcontextprotocol.io/docs/concepts/tools)
- [FastMCP-Dokumentation](https://gofastmcp.com/)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [TUD:AI API-Dokumentation](https://llm.scads.ai/docs/usage/api/)
- [TUD:AI Modellstatus](https://llm.scads.ai/status/)
- [TikToken](https://github.com/openai/tiktoken)
