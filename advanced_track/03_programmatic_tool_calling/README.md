# Programmatic Tool Calling (PTC) mit einem OpenAI-kompatiblen Endpoint

Beim klassischen Tool Calling entscheidet ein Sprachmodell schrittweise, welches Tool aufgerufen
wird. Die Anwendung führt den Aufruf aus und sendet das Ergebnis zurück an das Modell. Bei vielen
oder sehr großen Ergebnissen entstehen dadurch mehrere Modell-Round-Trips und ein schnell
wachsender Kontext.

Programmatic Tool Calling (PTC) verschiebt einen Teil dieser Orchestrierung in ein vom Modell
erzeugtes Programm. Dieses Programm kann Tools in Schleifen aufrufen, Ergebnisse filtern, rechnen
und nur ein kompaktes Resultat an das Modell weitergeben. Der Track demonstriert den Unterschied an
einer fiktiven Reisekostenanalyse und verwendet ausschließlich den OpenAI-kompatiblen Endpoint
`https://llm.scads.ai/v1` mit `Qwen/Qwen3.8-27B`.

Wichtig: Sowohl Anthropic als auch OpenAI stellen inzwischen natives, serverseitiges PTC bereit.
Anthropic verwendet Code-Execution-Container mit Python, OpenAI die Responses API mit einer
isolierten V8-JavaScript-Runtime. Ein OpenAI-kompatibler Endpoint unterstützt solche gehosteten
OpenAI-Tools aber nicht automatisch. ScaDS dokumentiert für Qwen reguläres Function Calling,
nicht die OpenAI-V8-Runtime. Dieses Projekt zeigt deshalb eine **portable PTC-Annäherung**: Qwen
erzeugt Python-Code per Function Call, die Anwendung prüft und führt ihn lokal aus und gibt nur
das verdichtete Ergebnis zurück. Das Architekturprinzip ist vergleichbar, API, Isolation und
Laufzeiteigenschaften sind es nicht.

## Lernziele

Nach diesem Track kannst du:

- klassisches Tool Calling und Programmatic Tool Calling unterscheiden,
- einen OpenAI-kompatiblen Tool-Calling-Loop in Python nachvollziehen,
- erkennen, warum große Tool-Resultate Modellkontext verbrauchen,
- vom Modell erzeugten Analysecode und dessen Tool-Aufrufe untersuchen,
- PTC und MCP korrekt einordnen und miteinander kombinieren,
- Sicherheitsgrenzen von Code Execution benennen.

# A. Aufgabe

Die Schritte 1 bis 4 bilden den Hauptteil des PTC Workshop-Tracks. Führe die Demo einmal im Modus `both`
aus; die Transferaufgaben und der Wissenstrack danach sind optionale Vertiefung.

### Schritt 1: Das Szenario verstehen

Öffne `mock_expense_api.py`. Die fiktive API bietet drei read-only Tools:

| Tool | Aufgabe |
|---|---|
| `get_team_members(department)` | Liefert Personen einer Abteilung |
| `get_expenses(employee_id, quarter)` | Liefert umfangreiche Einzelbuchungen |
| `get_custom_budget(user_id)` | Liefert Standard- oder Sonderbudget |

Die Datensätze enthalten bewusst irrelevante Metadaten, abgelehnte Reiseausgaben und genehmigte
Softwareausgaben. Für die Aufgabe zählen nur Einträge mit `category == "travel"` und
`status == "approved"`.

Das unabhängig vom Modell berechnete Ground-Truth-Ergebnis lautet:

| Person | Genehmigte Reiseausgaben | Tatsächliches Budget | Überschreitung |
|---|---:|---:|---:|
| Carol White (`ENG003`) | 6.800 USD | 5.000 USD | 1.800 USD |
| Fatima Saleh (`ENG006`) | 8.900 USD | 7.500 USD | 1.400 USD |

Alice und Diego liegen zwar über dem Standardlimit, aber innerhalb ihrer Sonderbudgets. Deshalb
muss das Programm deren Budgets prüfen, darf sie aber nicht als finale Überschreitungen melden.

**Beobachtungsfragen**

- Welche Datensätze sind fachlich irrelevant, obwohl die Tools sie zurückgeben?
- Warum benötigen Alice und Diego einen Budgetaufruf, erscheinen aber nicht im Ergebnis?

### Schritt 2: Beide Varianten ausführen und die Baseline beobachten

> Neuen Terminal in diesem Ordner öffnen und WSL Instanz starten.

``` bash
wsl

uv run python ptc_demo.py --mode both
```

Was passiert:

1. Die Anwendung sendet Frage und drei JSON-Tool-Schemas an Qwen.
2. Qwen fordert `get_team_members` an.
3. Die Anwendung führt das Tool aus und sendet die vollständige Antwort an Qwen.
4. Qwen fordert für die Personen Expense-Reports und danach notwendige Budgets an.
5. Jeder umfangreiche Report wird als `role="tool"` in die Conversation eingefügt.
6. Qwen filtert, addiert und formuliert die Antwort.

Der entscheidende Code steht in `run_baseline()` in `ptc_demo.py`. Beachte besonders:

```python
result = _dispatch_tool(runtime, tool_call.function.name, arguments)
content = _json(result)
messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": content})
```

Die Anwendung muss Tool-Ergebnisse an das Modell zurückgeben, damit es weiterarbeiten kann. Werden
diese Ergebnisse groß, wachsen die folgenden Requests und damit die kumulierten Input-Tokens.

**Beobachtungsfragen**

- Wie viele Modellrunden und Fach-Tool-Aufrufe meldet die Baseline?
- Welche vollständigen Payloads wandern nach einem Tool-Aufruf zurück in den Modellkontext?

### Schritt 3: Im selben Lauf die portable PTC-Variante untersuchen

Was passiert:

1. Die Anwendung beschreibt eine kleine, erlaubte Python-Teilmenge.
2. Qwen ruft nur das Meta-Tool `run_python_analysis` auf und übergibt selbst erzeugten Python-Code.
3. Das Skript druckt diesen Code aus. Lies ihn, bevor du das Ergebnis betrachtest.
4. `validate_program()` zerlegt den Code als Abstract Syntax Tree und prüft alle Konstrukte.
5. `execute_program()` stellt nur drei read-only Fach-Tools und wenige Built-ins bereit.
6. Der erzeugte Code ruft lokal alle Fach-Tools auf, filtert Datensätze und berechnet Summen.
7. Nur die kleine Variable `result` geht als Tool-Ergebnis zurück an Qwen.
8. Qwen formuliert daraus die Antwort.

Der zentrale Unterschied liegt an dieser Grenze:

```text
Verbose Team- und Expense-Daten
            |
            v
   lokaler Analysecode  ---->  kompaktes result  ---->  Modell
```

Die Expense-Datensätze existieren in der portablen PTC-Variante im lokalen Python-Prozess. Sie
werden nicht als Tool Messages an das Modell gesendet.

Falls Qwen beim ersten Versuch ein nicht erlaubtes Sprachkonstrukt erzeugt, bekommt es nur die
Validierungsfehlermeldung und darf den Code korrigieren. Nach drei fehlerhaften Versuchen bricht die
Demo nachvollziehbar ab.

**Beobachtungsfragen**

- Welche Schleifen, Bedingungen und Tool-Aufrufe stehen im erzeugten Programm?
- Welche Rohdaten bleiben lokal, und welche Struktur wird tatsächlich an Qwen zurückgegeben?
- Wird ein Reparaturversuch sichtbar, und welche Regel hat den ersten Versuch abgelehnt?

### Schritt 4: Metriken und Ergebnisqualität vergleichen

Am Ende erscheint beispielsweise folgende Tabelle, wobei die konkreten Werte pro Lauf variieren:

```text
=== Beobachtete Metriken (ein Lauf, kein Benchmark) ===
Modus             LLM   Tools     Tokens   Bytes->LLM   Sekunden
----------------------------------------------------------------
baseline            ...     ...        ...          ...        ...
portable PTC        ...     ...        ...          ...        ...
```

Die Spalten bedeuten:

| Spalte | Bedeutung |
|---|---|
| `LLM` | Anzahl der Requests an den Chat-Completions-Endpoint |
| `Tools` | Tatsächlich ausgeführte Fach-Tool-Aufrufe |
| `Tokens` | Vom Endpoint gemeldete Summe aus Input- und Output-Tokens |
| `Bytes->LLM` | Größe der zurückgesendeten Tool-Payloads, nicht deren Tokenzahl |
| `Sekunden` | Gesamtdauer des einzelnen Live-Laufs |

Ein einzelner Lauf ist kein belastbarer Benchmark. Modell-Warteschlange, Netz, Caching und erzeugte
Tool-Strategie können die Zahlen beeinflussen. Erwartbar ist vor allem ein deutlicher Unterschied
bei `Bytes->LLM`; geringere Latenz oder weniger LLM-Requests sind nicht garantiert.

Das Skript berechnet nach einem `both`-Lauf automatisch die prozentuale Änderung bei LLM-Aufrufen,
Tokens, Tool-Payload und Laufzeit. Es ordnet außerdem ein, ob gleich viele Fach-Tools ausgeführt
wurden und ob das strukturierte PTC-Ergebnis mit der Ground Truth übereinstimmt.

Für den oben beispielhaft gezeigten Lauf könnte die Einordnung so aussehen:

```text
=== Einordnung dieses Laufs ===
- LLM-Aufrufe: 50.0% weniger (4 -> 2).
- Fach-Tool-Aufrufe: unverändert (11).
- Tokens: 90.0% weniger (33,394 -> 3,346).
- Tool-Payload zum LLM: 99.5% weniger (46,291 -> 231 Bytes).
- Laufzeit: 81.9% weniger (113.58 -> 20.57 Sekunden).
- PTC-Ergebnis gegen Ground Truth: korrekt.
```

Die unveränderten elf Fach-Tool-Aufrufe sind wichtig: PTC erledigt dieselbe Datenbeschaffung. Der
Unterschied entsteht dadurch, wo die 46 KB Rohdaten verarbeitet werden und wie oft das Modell
zwischen den Schritten aufgerufen wird.

**Beobachtungsfragen**

- Welche Metrik zeigt die verschobene Datenverarbeitung am direktesten?
- Stimmt das strukturierte PTC-Ergebnis mit der unabhängigen Ground Truth überein?
- Welche Werte sind Architekturfolgen, und welche können durch Netz oder Modellstrategie schwanken?

Mit `--quiet` lassen sich die erklärenden Fortschrittsmeldungen ausblenden:

```bash
uv run python ptc_demo.py --mode both --quiet
```

## Optionale Vertiefung

### Transfer auf einen eigenen Use Case

Ein zweites fertiges Skript würde denselben Ablauf lediglich mit anderen Daten wiederholen. Nutze
stattdessen `ptc_demo.py` als Referenz und ersetze die Bausteine bewusst in dieser Reihenfolge:

1. Implementiere eigene, möglichst read-only Fach-Tools wie die Funktionen in
   `mock_expense_api.py`.
2. Dokumentiere für jedes Tool Eingaben, Rückgabefelder, Datentypen und Fehlerfälle exakt.
3. Passe das Meta-Tool `PTC_TOOL` an, über das das Modell sein Analyseprogramm liefert.
4. Formuliere in `PTC_SYSTEM_PROMPT` den begrenzten Auftrag, die Tool-Verträge und das gewünschte
   Ergebnis-Schema.
5. Erweitere `ALLOWED_CALLS` nur um Funktionen, die der generierte Code tatsächlich benötigt.
6. Passe `validate_analysis_result()` an das neue kompakte Ergebnis an.
7. Registriere die Fach-Tools in `execute_program()` und im Dispatcher.
8. Teste die fachliche Ground Truth unabhängig vom Modell, bevor du Effizienzwerte vergleichst.

Die entscheidende Designfrage lautet dabei nicht nur „Kann das Modell diesen Code schreiben?“,
sondern „Welche minimale, sichere Tool- und Sprachoberfläche benötigt es dafür?“. Entferne keine
Sicherheitsgrenze nur deshalb, weil ein generiertes Programm abgelehnt wird.

Für eine native Implementierung sollten anschließend die offiziellen Beispiele verwendet werden:
Anthropic zeigt Python in einem Code-Execution-Container, OpenAI JavaScript in einer gehosteten
V8-Runtime. Die Links stehen unter [Weitere Quellen](#weitere-quellen).

### Übungen

1. Ändere die Expense-Frage so, dass nur Ausgaben eines bestimmten Monats berücksichtigt werden.
2. Ergänze ein Tool `get_project_budget(employee_id)` und dokumentiere seinen Output-Vertrag.
3. Vergleiche `baseline` und `ptc` dreimal und dokumentiere die Streuung der Metriken.
4. Entferne ein erlaubtes AST-Konstrukt und beobachte den Reparaturversuch des Modells.
5. Ersetze eine lokale Funktion durch einen Aufruf an einen read-only MCP-Server.
6. Diskutiere, welche Freigaben ein mutierendes Tool wie `approve_expense()` benötigen würde.

## Optionaler Wissenstrack

### Wie die Codeausführung funktioniert

`PTC_SYSTEM_PROMPT` beschreibt die erlaubten APIs und die Aufgabe. Das Modell schreibt ein Programm,
das in etwa diese Form annimmt:

```python
members = get_team_members("engineering")
result = []
for member in members:
    expenses = get_expenses(member["id"], "Q3")
    # filtern, summieren und bedingt das Budget abrufen
    # nur finale Überschreitungen zu result hinzufügen
```

Der Prompt dokumentiert auch die exakten Rückgabeformen: Teammitglieder verwenden das Feld `id`,
und `get_custom_budget()` liefert ein Objekt, dessen numerischer Grenzwert in `travel_budget` steht.
Ohne solche Output-Verträge kann ein Modell syntaktisch plausiblen, aber fachlich nicht
ausführbaren Code erzeugen. OpenAIs natives PTC besitzt dafür explizit `output_schema`; in dieser
portablen Variante stehen dieselben Informationen im Prompt und werden am Ergebnis validiert.

`validate_program()` erlaubt nur eine kleine AST-Allowlist. Imports, Attribute, Funktionsdefinitionen,
unbekannte Funktionsaufrufe und unbeschränkte `while`-Schleifen sind nicht Teil dieser Sprache.
`ToolRuntime` begrenzt außerdem die Gesamtzahl der Fach-Tool-Aufrufe.

Eine zusätzliche Ergebnisprüfung erlaubt höchstens sechs Einträge mit exakt den fünf erwarteten
Skalarfeldern. Sie weist außerdem leere oder doppelte Personen, nicht endliche Zahlen, rechnerisch
falsche Überschreitungen und Abweichungen von der unabhängig berechneten Workshop-Ground-Truth ab,
bevor das Ergebnis an das Modell geht. Dadurch kann ein syntaktisch gültiges Programm weder
versehentlich komplette Expense-Records noch ein fachlich falsches `result` weiterreichen.

Diese Maßnahmen machen den Workshop kontrollierbarer, aber **nicht sicher für fremden oder
produktiven Code**.

#### Wo wird der generierte Code in diesem Workshop ausgeführt?

Die Ausführung ist real, aber lokal: `execute_program()` parst den von Qwen gelieferten String mit
`ast.parse()`, prüft den Syntaxbaum, kompiliert ihn ausschließlich im Arbeitsspeicher mit
`compile()` und führt das Ergebnis mit `exec()` **im selben Python-Prozess wie `ptc_demo.py`** aus.
Es wird keine temporäre `.py`-Datei geschrieben und kein separates Skript oder Subprozess gestartet.

Die Runtime stellt dem Code nur eingeschränkte Built-ins und drei freigegebene read-only Funktionen
zur Verfügung. Imports, Attribute, unbekannte Funktionen und `while`-Schleifen werden vorab
abgewiesen; Tool-Aufrufe und Ergebnisgröße sind zusätzlich begrenzt. Die Expense-Daten sind
simulierte Workshop-Daten, die Ausführung des erzeugten Programms selbst ist jedoch nicht simuliert.

Diese AST-Allowlist ist **keine echte Sandbox und keine Sicherheitsgrenze für Produktionscode**.
Python-`exec()` läuft weiterhin mit den Rechten des Workshop-Prozesses. Eine produktive Lösung
braucht Prozess- oder Container-Isolation sowie CPU-, Speicher-, Zeit-, Netzwerk- und
Dateisystemgrenzen. Anthropic und OpenAI stellen diese Isolation in ihren nativen PTC-Runtimes
serverseitig bereit; die ScaDS-kompatible Demo bildet sie bewusst nicht vor.

### Was ist real, simuliert und emuliert?

| Bestandteil | Einordnung | Bedeutung |
|---|---|---|
| Qwen-Aufrufe über ScaDS | real | Das Modell wird tatsächlich über die API aufgerufen. |
| Modellgeneriertes Python | real | Qwen erzeugt den Code für den jeweiligen Lauf. |
| `compile()` und `exec()` | real | Der erzeugte Code wird tatsächlich lokal ausgeführt. |
| Fach-Tool-Aufrufe und Metriken | real | Das Programm ruft Tools auf; Aufrufe, Bytes, Tokens und Zeit werden gemessen. |
| Expense-System und Datensätze | simuliert | Feste Daten ersetzen eine echte Datenbank oder Unternehmens-API. |
| PTC-Plattform | emuliert | `ptc_demo.py` übernimmt lokal die Orchestrierung, die bei nativem PTC der Anbieter bereitstellt. |
| Sandbox | nicht vorhanden | AST-Allowlist und reduzierte Built-ins begrenzen Python, isolieren den Prozess aber nicht. |

Es handelt sich damit nicht um eine vorbereitete Ergebnisattrappe: Das Modell schreibt ein Programm,
und dieses Programm verarbeitet die simulierten Geschäftsdaten tatsächlich. Emuliert wird die
anbieterabhängige PTC-Infrastruktur, nicht die Programmausführung.

In der lokalen PTC-Variante bleiben die Rohdaten aus `mock_expense_api.py` auf dem Workshop-Rechner.
Qwen erhält den Auftrag und später nur das validierte, kompakte Ergebnis. In der Baseline werden die
Tool-Ergebnisse dagegen als Nachrichten an den ScaDS-Endpunkt zurückgesendet. Mit echten Daten muss
daher auch für den verwendeten ScaDS-Dienst geprüft werden, welche Vertrags-, Datenschutz- und
Aufbewahrungsregeln gelten.

### Natives PTC bei Anthropic und OpenAI

Das referenzierte Anthropic-Cookbook verwendet anbieterspezifische Funktionen:

- `client.beta.messages.create(...)`
- Beta `advanced-tool-use-2025-11-20`
- `allowed_callers: ["code_execution_20250825"]`
- das serverseitige Tool `code_execution_20250825`
- zustandsbehaftete Code-Execution-Container
- besonderes Routing von Tool-Ergebnissen in den Container statt in den Modellkontext

Die Versionskennung `code_execution_20250825` stammt aus dem verlinkten Cookbook. Die aktuelle
Anthropic-Dokumentation verlangt inzwischen `code_execution_20260120` oder neuer. Das Grundprinzip
und die Anbieterbindung bleiben gleich; Versionskennungen sollten nicht ungeprüft aus alten
Beispielen übernommen werden.

In der nativen Variante schreibt Claude Code in einem Anthropic-Container. Aus diesem Code
entstehende Tool Calls werden vom Client ausgeführt und ihre Resultate zurück in den Container
geroutet. Der Container verarbeitet die Rohdaten; Claude erhält die verdichtete Ausgabe.

OpenAI bietet inzwischen ein direktes Pendant in der Responses API:

- gehostetes Tool `{ "type": "programmatic_tool_calling" }`,
- `allowed_callers: ["programmatic"]` pro aufrufbarem Tool,
- `output_schema` für strukturierte Tool-Rückgaben,
- isolierte V8-Runtime mit JavaScript und Top-Level-`await`,
- keine Node.js-Pakete, direkten Netzwerkzugriffe, allgemeinen Dateizugriffe oder Subprozesse,
- `program`, verschachtelte `function_call`- und abschließende `program_output`-Items.

Die Anwendung führt weiterhin ihre eigenen Functions aus. OpenAI führt dagegen den erzeugten
JavaScript-Orchestrierungscode aus und hält dessen Zwischenergebnisse in der gehosteten Runtime.

| Aspekt | Anthropic-natives PTC | OpenAI-natives PTC | Dieser Workshop |
|---|---|---|---|
| API | Messages API | Responses API | Chat Completions |
| Programm | Python | JavaScript | Python |
| Code Runtime | Anthropic-Container | OpenAI V8-Runtime | lokaler Prozess |
| Tool-Freigabe | `allowed_callers` mit Code-Version | `allowed_callers: ["programmatic"]` | Host-Allowlist |
| Output-Vertrag | Tool-Beschreibung/JSON | `output_schema` | Prompt und Ergebnisvalidator |
| Isolation | verwaltete Code Execution | isolierte V8-Runtime | didaktische AST-Allowlist |

Beide nativen Varianten können direkt über die jeweilige API implementiert werden. Bei Anthropic
wird dafür das Code-Execution-Tool in der Messages API aktiviert. Bei OpenAI wird
`programmatic_tool_calling` in der Responses API registriert. Die Anwendung stellt weiterhin ihre
eigenen Fach-Tools bereit und kontrolliert deren Berechtigungen.

### Firmendaten in proprietären PTC-Runtimes

Eine Sandbox beantwortet zunächst die Frage **„Was darf generierter Code tun?“**. Sie beantwortet
nicht automatisch die andere Frage **„Wer kann die verarbeiteten Daten sehen und wie lange werden
sie gespeichert?“**. „Nicht im Modellkontext“ bedeutet bei nativem PTC insbesondere nicht „nicht
beim Anbieter“:

1. Die Anwendung führt ein eigenes Tool aus, beispielsweise eine Datenbankabfrage.
2. Das Tool-Ergebnis wird über die Anbieter-API an das wartende Programm zurückgegeben.
3. Die Rohdaten werden in der gehosteten Runtime gefiltert oder aggregiert.
4. Nur die verdichtete Programmausgabe gelangt anschließend in den Modellkontext.

Damit erreichen die Tool-Ergebnisse den Server und die Runtime des Anbieters, auch wenn das Modell
nicht jeden Rohdatensatz als Kontexttoken sieht. Transportverschlüsselung und Sandbox-Isolation
schützen Übertragung und Ausführung, ersetzen aber keine datenschutzrechtliche Freigabe.

#### Anthropic

- Anthropic beschreibt eine sichere, isolierte Linux-Container-Runtime ohne Internetzugriff und mit
  begrenztem Datei-, CPU-, Speicher- und Zeitbudget.
- Ein neuer Container wird pro Request angelegt, sofern keine vorhandene Container-ID wiederverwendet
  wird. Zustand und Dateien können bei Wiederverwendung erhalten bleiben.
- Container werden nach Inaktivität checkpointed und können laut aktueller Dokumentation bis zu 30
  Tage nach ihrer Erstellung wiederverwendet werden. Code-Execution- und PTC-Daten können bis zu 30
  Tage aufbewahrt werden; die Funktion ist aktuell **nicht Zero-Data-Retention-fähig**.
- Eingaben und Ausgaben kommerzieller Anthropic-Produkte werden standardmäßig nicht zum Training
  verwendet, sofern der Kunde dies nicht ausdrücklich erlaubt oder Feedback übermittelt.

Der Anthropic-Container ist deshalb nicht einfach unmittelbar nach dem einzelnen Lauf garantiert
gelöscht. Für vertrauliche Daten sind die konkrete Produktversion, der Vertrag und die aktuelle
Feature-Eignung maßgeblich.

#### OpenAI

- OpenAI führt jedes PTC-Programm in einer frischen, isolierten V8-Runtime aus. Sie bietet weder
  Node.js noch direkten Netzwerkzugriff, ein allgemeines Dateisystem oder Subprozesse.
- Zwischen einzelnen Programmausführungen besteht kein persistenter JavaScript-Zustand. OpenAI
  beschreibt PTC als ZDR-fähig, sofern ZDR für Organisation oder Projekt freigeschaltet ist und auch
  alle verwendeten Modelle, Tools und Drittdienste dafür geeignet sind.
- `store: false` verhindert gespeicherte Response-Zustände, aktiviert aber allein noch kein ZDR.
  Ohne besondere Aufbewahrungskontrollen können API-Inhalte standardmäßig bis zu 30 Tage in
  Abuse-Monitoring-Logs liegen; gespeicherte Responses besitzen zusätzlich Application State.
- API-Daten werden standardmäßig nicht zum Training verwendet, sofern der Kunde nicht ausdrücklich
  opt-in aktiviert.

OpenAIs PTC-V8-Runtime darf nicht mit dem separaten Python Code Interpreter verwechselt werden. Ein
Code-Interpreter-Container kann Dateien und Zustand halten und verfällt derzeit nach 20 Minuten
Inaktivität; dann werden seine Daten verworfen. PTC selbst benötigt laut OpenAI keinen persistenten
Code-Execution-Container.

#### Entscheidung für Unternehmensdaten

Vor produktivem Einsatz sollten mindestens Datenklassifikation, Zweckbindung, Datenminimierung,
Pseudonymisierung, Auftragsverarbeitungsvertrag beziehungsweise DPA, Unterauftragsverarbeiter,
Verarbeitungsregion, Löschfristen, Auditierbarkeit und regulatorische Anforderungen geprüft werden.
Zusätzlich gelten Least Privilege, read-only Tools, serverseitige Autorisierung bei jedem Aufruf und
explizite Freigaben für Schreiboperationen.

Für besonders sensible oder regulatorisch eingeschränkte Daten kann eine lokale oder selbst
betriebene isolierte Runtime geeigneter sein. Eine weitere Möglichkeit ist, proprietäres PTC nur mit
pseudonymisierten Daten oder bereits intern aggregierten Resultaten zu versorgen. Die Entscheidung
ist damit keine reine Architekturfrage, sondern eine gemeinsame Freigabe durch Fachbereich,
Informationssicherheit, Datenschutz und gegebenenfalls Rechtsabteilung.

#### Warum verwendet der Workshop nicht OpenAIs natives PTC?

`https://llm.scads.ai/v1` ist OpenAI-kompatibel und besitzt über LiteLLM auch einen Responses-Pfad.
Das beweist jedoch nur API-Übersetzung, nicht die Verfügbarkeit proprietärer OpenAI-Hosted-Tools.
Die ScaDS-Dokumentation, Modellstatusseite und Beispiele weisen für `Qwen/Qwen3.8-27B` reguläres
Tool Calling aus, aber keine gehostete V8-Runtime oder `programmatic_tool_calling`-Unterstützung.

"OpenAI-kompatibel" bedeutet deshalb nicht "alle OpenAI-Platform-Features vorhanden". Für die
Vorgabe ScaDS + Qwen emuliert der Workshop den PTC-Kern mit einem Meta-Function-Call und lokaler
Runtime. Mit einem OpenAI API-Key und einem dort explizit unterstützten Modell wäre stattdessen die
native Responses-API-Variante sinnvoll.

Die Demo beansprucht keine API-Kompatibilität mit Anthropic- oder OpenAI-PTC. Sie isoliert das
gemeinsame Architekturprinzip: **Das Modell erzeugt ein Programm, das mehrere Tools aufruft und
Rohdaten vor dem nächsten Modellkontakt reduziert.**

### Klassisches Tool Calling, parallele Calls und PTC

| Ansatz | Wer steuert die Abfolge? | Wo werden Daten verarbeitet? | Geeignet für |
|---|---|---|---|
| Direkter Tool Call | Modell pro Schritt | meist Modellkontext | einzelne Abfragen |
| Parallele Tool Calls | Modell pro Runde | meist Modellkontext | unabhängige Abfragen |
| Fester Workflow | Anwendungscode | Anwendung | stabile, bekannte Prozesse |
| PTC | modellgenerierter Code | Code Runtime | dynamische Schleifen, Filter und Abhängigkeiten |

Parallele Tool Calls sind noch kein PTC: Das Modell fordert lediglich mehrere direkte Calls in einer
Antwort an. Bei PTC werden Schleifen, Bedingungen, Aggregation und gegebenenfalls Parallelisierung
innerhalb eines erzeugten Programms ausgedrückt.

Ein fester Python-Workflow wäre für diese konkrete Reisekostenregel einfacher und sicherer. PTC
wird interessant, wenn Nutzerfragen unterschiedliche Filter, Berechnungen oder Aufrufgraphen
erfordern und nicht jede Kombination vorprogrammiert werden soll.

### Vorteile von PTC

- Große oder irrelevante Tool-Resultate können vor dem Modellkontakt reduziert werden.
- Schleifen, Verzweigungen und Aggregationen sind in Code präziser als in freiem Modelltext.
- Bedingte Aufrufe vermeiden unnötige Tools, hier etwa Budgetabfragen unter 5.000 USD.
- Unabhängige Aufrufe können in einer geeigneten Runtime parallelisiert werden.
- Numerische Berechnungen sind reproduzierbarer als manuelles Addieren durch das Modell.
- Drittanbieter-Tools müssen für die Datenreduktion nicht zwingend verändert werden.

### Nachteile und Grenzen

- Modellgenerierter Code vergrößert die Angriffs- und Fehleroberfläche (auch Prompt Injection kann ein Problem sein!).
- Sandbox, Ressourcenlimits, Autorisierung und Auditierung verursachen Infrastrukturaufwand.
- Falscher Code kann Daten auslassen, Tools zu oft aufrufen oder fachliche Regeln verletzen.
- Mutierende Tools können in Schleifen unbeabsichtigt mehrfach ausgeführt werden.
- Debugging umfasst Prompt, erzeugten Code, Runtime, Tool-Routing und Fachsysteme.
- Kleine Aufgaben können mit PTC komplizierter und langsamer als direkte Tool Calls werden.
- Native PTC-Funktionen und ihre Semantik sind derzeit anbieterspezifisch.

### PTC und MCP: Konkurrenz oder Kombination?

PTC und das Model Context Protocol lösen auf der konzeptionellen Ebene unterschiedliche Probleme:

| MCP | PTC |
|---|---|
| standardisiert Bereitstellung und Beschreibung von Tools, Resources und Prompts | beschreibt eine Strategie zur Orchestrierung mehrerer Tools durch erzeugten Code |
| definiert Client-Server-Kommunikation und Transporte | definiert keinen universellen Tool-Transport |
| hilft Tools zu entdecken und zwischen Anwendungen wiederzuverwenden | hilft dynamische Aufrufabfolgen und Datenverarbeitung auszudrücken |

PTC ist daher kein Protokollersatz für MCP. Eine sinnvolle Kombination sieht so aus:

```text
MCP-Server A ----\
MCP-Server B ----- MCP-Client/Tool-Proxy <---- PTC-Code-Runtime <---- Modell
MCP-Server C ----/
```

MCP stellt standardisierte Tools bereit. Eine PTC-Runtime gibt eine bewusst ausgewählte Teilmenge
dieser Tools für modellgenerierten Code frei. Dabei muss die Runtime MCP-Tool-Schemas,
Authentifizierung, Berechtigungen und Resultate in ihre sichere Ausführungsumgebung übertragen.

Vorteile der Kombination sind wiederverwendbare MCP-Server, dynamische PTC-Orchestrierung und lokale
Datenverdichtung. Nachteile sind eine zusätzliche Policy-Grenze, schwierigere Ende-zu-Ende-Traces
und das Risiko, dass sehr mächtige MCP-Tools automatisiert oder wiederholt aufgerufen werden.

#### Warum wirkt PTC trotzdem wie ein konkurrierender Ansatz?

Auf der **modellseitigen Architektur-Ebene** kann PTC durchaus etwas ersetzen: Statt dem Modell
hunderte MCP-Tool-Schemas direkt zu exponieren und nach jedem Ergebnis erneut zu inferieren, sieht
es eine programmierbare Umgebung, die diese Tools effizient verwendet. Ersetzt werden dann die
direkte Tool-Exposition und der schrittweise Aufrufmodus, nicht zwingend MCP als darunterliegende
Integrationsschnittstelle.

Auch Function Calling und MCP können auf der Integrationsschicht konkurrieren: Eine Anwendung kann
ein externes System als proprietäre Function oder als standardisierten MCP-Server anbinden. Das ist
aber die Entscheidung **Function-Schnittstelle versus MCP-Schnittstelle**, nicht **PTC versus MCP**.

OpenAIs natives PTC macht die Orthogonalität besonders sichtbar, weil es `mcp` ausdrücklich als
programmatic aufrufbaren Tool-Typ aufführt. Bei Anthropic können die aktuell vom nativen MCP
Connector gelieferten Tools laut Dokumentation noch nicht direkt programmatic aufgerufen werden;
ein eigener MCP-Client/Proxy kann sie dennoch in eine PTC-Runtime einspeisen. Das ist eine konkrete
Anbietergrenze, kein konzeptioneller Widerspruch.

Die präzise Kurzfassung lautet daher:

```text
MCP = Woher kommen Tools, und wie werden sie standardisiert angebunden?
PTC = Wie orchestriert und verarbeitet erzeugter Code mehrere Tools effizient?
```

## Projektstruktur

```text
<repository-root>/
├── .env.example                              # Gemeinsame Konfigurationsvorlage
├── .env                                      # Persönlicher Key, nicht committen
└── advanced_track/03_programmatic_tool_calling/
    ├── README.md                              # Anleitung und Wissenstrack
    ├── ptc_demo.py                            # Baseline, PTC und Metriken
    ├── workshop_config.py                     # Lädt die Root-.env
    ├── mock_expense_api.py                    # Deterministische read-only Tools
    ├── tests/test_ptc_demo.py                 # Fach- und Sicherheitsprüfungen
    ├── pyproject.toml                         # UV-Projekt
    └── uv.lock                                # Reproduzierbare Versionen
```

## Voraussetzungen

- Python 3.12 oder neuer
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
- ein persönlicher ScaDS/TUD:AI API-Key **oder** für den privaten Gebrauch einen **OpenAI-compatible Endpoint** sowie einen **API-Key** (lokale Lösungen, wie LMStudio geht natürlich auch!)
- grundlegende Python-Kenntnisse
- grundlegendes Verständnis von LLM Tool Calling

API-Keys können berechtigte TU-Dresden-Beschäftigte über das
[Self-Service-Portal](https://selfservice.tu-dresden.de/services/scads-llm-api/) beziehen. Weitere
berechtigte Personen finden die Kontaktinformationen in der
[TUD:AI API-Dokumentation](https://llm.scads.ai/docs/usage/api/). Ein persönlicher Key darf nicht
geteilt oder committet werden.

Der Modellstatus ist unter <https://llm.scads.ai/status/> sichtbar. Zum Zeitpunkt der Erstellung
unterstützte `Qwen/Qwen3.8-27B` Reasoning, Vision und Tools bei einer maximalen Kontextlänge von
262.144 Tokens.

# B. Setup (für alle, die es auf ihrem System aufsetzen und testen wollen)

### 1. Gemeinsame Root-Konfiguration anlegen

Wechsle in die Repository-Wurzel. Dort liegen `.env.example`, `advanced_track/` und die weiteren
Tracks. Lege genau dort die gemeinsame `.env` an.

Linux, macOS oder Git Bash:

```bash
cp .env.example .env
```

PowerShell:

```powershell
Copy-Item .env.example .env
```

Trage den persönlichen Key mit den gemeinsamen `SCADS_*`-Variablen in die Root-`.env` ein:

```dotenv
SCADS_API_KEY=dein-persönlicher-key
SCADS_BASE_URL=https://llm.scads.ai/v1
SCADS_MODEL=Qwen/Qwen3.8-27B
```

Alternativ kannst du deine Einträge auch ändern und umbenennen oder diese mit deinen URLs, Modelnames & Keys verwenden.

Lege keine weitere `.env` im Track an. Das Skript bestimmt die Root-Datei relativ zu seinem eigenen
Pfad und ist deshalb nicht vom aktuellen Terminal-Arbeitsverzeichnis abhängig.

### 2. UV-Projekt vorbereiten

```bash
cd advanced_track/03_programmatic_tool_calling
uv sync --link-mode copy
```

`--link-mode copy` funktioniert auch unter WSL in Windows-Verzeichnissen, in denen Hardlinks häufig
abgelehnt werden.

### 3. Lokale Selbsttests ausführen

Diese Tests brauchen keinen API-Key:

```bash
uv run pytest
uv run ruff check .
```

Die Tests prüfen das fachliche Ergebnis, das Tool-Routing und die Sicherheitsgrenzen. Unter anderem
weisen sie Imports, Dateioperationen, Attributzugriffe und `while`-Schleifen im generierten Programm
ab.

### Sicherheitskontext

Für produktive PTC-Systeme sind mindestens folgende Kontrollen relevant:

- echte Sandbox oder isolierter kurzlebiger Container,
- Allowlist statt automatischer Freigabe aller vorhandenen Tools,
- Least-Privilege-Credentials pro Tool und Nutzer,
- Schema- und Fachvalidierung unabhängig vom Modell,
- Limits für Laufzeit, CPU, Speicher, Output, Parallelität und Tool Calls,
- Netzwerk- und Dateisystemzugriff standardmäßig deaktivieren,
- Idempotenz und explizite Freigaben für mutierende oder irreversible Aktionen,
- Audit-Logs für erzeugten Code, Caller, Parameter und Resultatgrößen,
- Redaction von Secrets und personenbezogenen Daten,
- Schutz vor Prompt Injection in Tool-Resultaten,
- Abbruch- und Recovery-Strategien für teilweise ausgeführte Programme.

Read-only Mock-Tools ohne reale Secrets machen diese Demo workshopgeeignet. Sie belegen nicht, dass
derselbe Executor für Produktionsdaten sicher wäre.

## Weitere Quellen

- [Anthropic Cookbook: Programmatic Tool Calling](https://github.com/anthropics/claude-cookbooks/blob/main/tool_use/programmatic_tool_calling_ptc.ipynb)
- [Anthropic-Dokumentation zu Programmatic Tool Calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling)
- [Anthropic-Dokumentation zu Code Execution und Containern](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool)
- [Anthropic: API und Data Retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention)
- [OpenAI-Dokumentation zu Programmatic Tool Calling](https://developers.openai.com/api/docs/guides/tools-programmatic-tool-calling)
- [OpenAI: Data Controls](https://developers.openai.com/api/docs/guides/your-data)
- [OpenAI: Code Interpreter und Container-Lebenszyklus](https://developers.openai.com/api/docs/guides/tools-code-interpreter)
- [TUD:AI API-Dokumentation](https://llm.scads.ai/docs/usage/api/)
- [TUD:AI Modellstatus](https://llm.scads.ai/status/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [OpenAI Function Calling](https://developers.openai.com/api/docs/guides/function-calling)

## Troubleshooting

**`(SCADS_)API_KEY` fehlt**

Prüfe, ob `.env` in der Repository-Wurzel liegt und die Zeile kein zusätzliches
Anführungszeichen enthält. Alternativ kann die Variable in der aktuellen Shell exportiert werden.

**HTTP 401 oder 403**

Prüfe den API-Key und die Zugangsberechtigung. Teile den Key nicht in Screenshots oder Logs.

**HTTP 429**

Der persönliche Key hat ein Request-Limit. Warte kurz und führe nur einen Modus aus. Die
TUD:AI-Dokumentation beschreibt die Rate-Limit-Regeln.

**Das Modell ist nicht verfügbar**

Prüfe <https://llm.scads.ai/status/> oder deinen entsprechenden Endpoint. Die Demo setzt `disable_fallbacks`, damit die Messung nicht
unbemerkt auf einem anderen Modell erfolgt. Für einen bewussten Modellwechsel nutze beispielsweise:

```bash
uv run python ptc_demo.py --mode ptc --model alias-code
```

**Das generierte Programm wird abgelehnt**

Das ist ein sichtbarer Bestandteil der Demo. Qwen erhält die Validierungsfehlermeldung und kann den
Code bis zu zweimal korrigieren. Bleiben alle drei Versuche ungültig, starte erneut und untersuche
die ausgegebenen Programme. Nicht die Allowlist vorschnell für Imports oder Attribute öffnen.

**`uv sync` meldet unter WSL einen Hardlink- oder I/O-Fehler**

```bash
uv sync --link-mode copy
```

