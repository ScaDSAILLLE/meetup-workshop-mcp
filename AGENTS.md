# Repository Instructions

## Ziel und Sprache

- Dieses Repository wird zu einem vollständigen, praxisnahen MCP-Workshop ausgebaut. `Programm.md` ist die Quelle für Dramaturgie, Tracks und Lernziele; das Root-`README.md` ist der allgemeine Einstieg.
- Teilnehmertexte, UI-Texte und Anleitungen auf Deutsch verfassen. Umlaute immer als `ä`, `ö`, `ü` und `ß` schreiben, nicht als `ae`, `oe`, `ue` oder `ss`, sofern kein technischer Bezeichner betroffen ist.
- `advanced_track/03_programmatic_tool_calling/README.md` ist das Qualitätsvorbild: Lernziele, exakte Vorbereitung, geführte Schritte mit Beobachtungsaufträgen, Konzeptteil, Übungen, Troubleshooting, Sicherheitsgrenzen und Quellen gehören zu einem fertigen Track.
- Der Beginner Track folgt verbindlich dieser Reihenfolge: Obsidian als niedrigschwelliger Einstieg, danach Blender, danach Strudel. Nicht nur Installation erklären, sondern konkrete Aufgaben, erwartete Ergebnisse und die jeweils sichtbar werdenden MCP-Konzepte.

## Secrets und Konfiguration

- Es darf genau eine `.env` und eine `.env.example` geben, beide im Repository-Root. Unterprojekte dürfen eigene `pyproject.toml`, `uv.lock` und `.venv` besitzen, aber keine eigenen Env-Dateien oder Env-Vorlagen.
- Die Root-`.env` niemals öffnen, lesen, ausgeben, durchsuchen oder verändern. Wenn ihr Inhalt für eine Aufgabe nötig erscheint, vorher den Benutzer fragen. Statt selbst zu editieren, die benötigten Variablennamen und Änderungen anhand von `.env.example` nennen; der Benutzer führt sie aus.
- Keine credential-abhängige Demo starten, ohne vorher zu fragen, da der Prozess die Root-`.env` laden kann. Offline-Tests dürfen ohne API-Key laufen.
- Die gemeinsame Vorlage verwendet `SCADS_API_KEY`, `SCADS_BASE_URL` und `SCADS_MODEL`. `advanced_track/03_programmatic_tool_calling/workshop_config.py` lädt diese Datei root-relativ und ist das Referenzmuster.
- `Setup/workshop_install_setup.bat` nicht ausführen: Es enthält einen hart codierten, echt aussehenden API-Key und setzt ihn mit `setx /M` systemweit. Solche Werte nicht zitieren oder weiterverwenden; beim Aufräumen durch Platzhalter ersetzen und dem Benutzer Rotation empfehlen.

## Aktive Bereiche

- `beginners_track/`: Langflow 1.11.3 ist die getestete Referenz. Obsidian wird direkt über den Streamable-HTTP-MCP-Endpunkt des Plug-ins „Local REST API with MCP“ angebunden, nicht über eine zusätzliche `mcp-obsidian`-Bridge. Die Reihenfolge ist Obsidian, Blender, Strudel.
- `advanced_track/01_mcp-progressive_disclosure-demo/`: Python 3.14, FastMCP in-memory, Starlette-Backend und statisches HTML/CSS/JS ohne Frontend-Build. Der echte Einstieg ist `uv run python -m backend.main` auf Port 8080; Frontend, API und MCP-Server laufen dabei zusammen in einem Prozess.
- `advanced_track/03_programmatic_tool_calling/`: Python 3.12, eigenständiges uv-Projekt mit automatisierter Test-/Lint-Suite. Die lokale `exec()`-Variante ist bewusst keine Produktions-Sandbox; diese Grenze in Code und Dokumentation nicht abschwächen.
- `advanced_track/02_fastmcp/`: aufeinander aufbauende Einzelserver zum Erlernen von Server, Tools, Resources, Resource Templates und Prompts.
- `_archive_workshop_09_2025/` ist ausschließlich historische Referenz. Nie verändern oder dort neue Inhalte ablegen.
- `Setup/`, `Shared/` und `Slides/` nur nach ausdrücklicher Aufforderung verändern.

## Befehle und Verifikation

- Befehle immer im jeweiligen Projektordner ausführen; im Root gibt es kein gemeinsames `pyproject.toml` und keinen repo-weiten Build.
- Auf WSL unter `/mnt/c` für Installationen bevorzugt `uv sync --link-mode copy` verwenden, da Hardlinks dort fehlschlagen können.
- Programmatic Tool Calling: `uv sync --link-mode copy`, danach offline `uv run pytest` und `uv run ruff check .`; fokussiert: `uv run pytest tests/test_ptc_demo.py -k <name>`. Live-Demo erst nach Env-Rueckfrage mit `uv run python ptc_demo.py --mode baseline|ptc|both`.
- Progressive Disclosure: `uv sync --link-mode copy`, danach offline `uv run pytest` und `uv run ruff check .`; die kombinierte UI/API/MCP-App startet credential-abhängig mit `uv run python -m backend.main` auf Port 8080. Die API ist `POST /api/demo`.
- FastMCP: `uv sync --link-mode copy`, danach offline `uv run pytest` und `uv run ruff check .`; einen Schritt beispielsweise mit `uv run python 00_minimaler_server.py` starten und die in README und Skript dokumentierte Transport-URL vollständig übernehmen.
