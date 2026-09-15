# Optional: Langflow-Flow als MCP-Tool

Ein Langflow-Projekt kann seine Flows wiederum als MCP-Tools anbieten. Verwende dafür optional `Obsidian Summary Tool.json`.

## Aufgabe

1. Importiere den Flow über **Projects > Upload a flow**.
2. Wähle Model Provider: vLLM > Modell z.B. Qwen3.8:27B
3. Verbinde den zuvor registrierten MCP-Server `obsidian` (optional aktiviere ausschließlich Lese-Tools).
4. Teste den Flow im Playground (Spielplatz) mit einer Frage zu `MeetingNotes`.
5. Öffne in der Projektansicht die MCP-Server-Informationen des Projekts und registriere dessen Streamable-HTTP-Endpunkt als neuen Server in einem zweiten Test-Flow.
6. Rufe den Summary-Flow aus dem zweiten Agenten auf.

## Erwartetes Ergebnis

In den Agent Steps sind zwei Ebenen sichtbar: Der äußere Agent ruft den Langflow-Flow als Tool auf; der innere Flow sucht und liest Obsidian-Notizen.

## Beobachtungsfragen

- Welche Beschreibung hilft dem äußeren Agenten bei der Toolwahl?
- In welcher Ebene liegt das Obsidian-Credential?
- Welche zusätzliche Fehler- und Vertrauensgrenze entsteht durch die Verschachtelung?

