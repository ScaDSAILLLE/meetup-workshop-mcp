"""Offline-Tests für Registrierung und Kernfunktionen der Workshop-Server."""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest
from fastmcp import Client

ROOT = Path(__file__).parents[1]


def lade_schritt(dateiname: str) -> ModuleType:
    """Importiere ein nummeriertes Workshop-Skript, ohne seinen Server zu starten."""
    pfad = ROOT / dateiname
    spec = importlib.util.spec_from_file_location(pfad.stem, pfad)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Kann {dateiname} nicht laden.")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("dateiname", "tools", "resources", "templates", "prompts"),
    [
        ("00_minimaler_server.py", set(), set(), set(), set()),
        ("01_erstes_tool.py", {"begruesse"}, set(), set(), set()),
        (
            "02_weitere_tools.py",
            {"addiere", "celsius_in_fahrenheit", "workshop_empfehlung"},
            set(),
            set(),
            set(),
        ),
        (
            "03_statische_resources.py",
            set(),
            {"workshop://info", "workshop://agenda"},
            set(),
            set(),
        ),
        (
            "04_resource_templates.py",
            set(),
            set(),
            {"notizen://{person}/{thema}", "termine://2026-09/{tag}"},
            set(),
        ),
        ("05_prompts.py", set(), set(), set(), {"tool_review", "lernreflexion"}),
        (
            "06_kombinierter_assistent.py",
            {"suche_aufgaben", "neue_aufgabe", "aufgabe_erledigen"},
            {"assistent://hinweise"},
            {"aufgaben://{status}"},
            {"tagesplanung"},
        ),
    ],
)
async def test_registrierte_komponenten(
    dateiname: str,
    tools: set[str],
    resources: set[str],
    templates: set[str],
    prompts: set[str],
) -> None:
    modul = lade_schritt(dateiname)
    async with Client(modul.mcp) as client:
        assert {tool.name for tool in await client.list_tools()} == tools
        assert {str(resource.uri) for resource in await client.list_resources()} == resources
        assert {
            template.uriTemplate for template in await client.list_resource_templates()
        } == templates
        assert {prompt.name for prompt in await client.list_prompts()} == prompts


def test_tool_kernfunktionen() -> None:
    erstes_tool = lade_schritt("01_erstes_tool.py")
    weitere_tools = lade_schritt("02_weitere_tools.py")

    assert erstes_tool.begrüsse.fn(" Mira ").startswith("Hallo, Mira!")
    with pytest.raises(ValueError, match="darf nicht leer"):
        erstes_tool.begrüsse.fn("  ")
    assert weitere_tools.addiere.fn(20, 22) == 42
    assert weitere_tools.celsius_in_fahrenheit.fn(20) == 68
    assert "Resources" in weitere_tools.workshop_empfehlung.fn("Fortgeschritten")


def test_resource_kernfunktionen() -> None:
    statisch = lade_schritt("03_statische_resources.py")
    templates = lade_schritt("04_resource_templates.py")

    assert "2026-09-03" in statisch.workshop_info.fn()
    assert "Resource Templates" in statisch.workshop_agenda.fn()
    assert "Ein eigenes lesendes Tool" in templates.notiz.fn("Mira", "Übung")
    assert "2026-09-03" in templates.workshop_termin.fn("3")
    with pytest.raises(ValueError, match="zwischen 1 und 30"):
        templates.workshop_termin.fn("31")


def test_schreibtools_sind_validiert_und_nicht_persistent() -> None:
    assistent = lade_schritt("06_kombinierter_assistent.py")
    startanzahl = len(assistent.AUFGABEN)

    neu = assistent.neue_aufgabe.fn(" Tests dokumentieren ", "2026-09-05")
    assert len(assistent.AUFGABEN) == startanzahl + 1
    assert neu["titel"] == "Tests dokumentieren"
    with pytest.raises(ValueError, match="bestätigen=true"):
        assistent.aufgabe_erledigen.fn(neu["id"])
    erledigt = assistent.aufgabe_erledigen.fn(neu["id"], bestätigen=True)
    assert erledigt["status"] == "erledigt"

    frisch_importiert = lade_schritt("06_kombinierter_assistent.py")
    assert frisch_importiert.AUFGABEN == frisch_importiert.START_AUFGABEN
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        frisch_importiert.neue_aufgabe.fn("Ungültiges Datum", "05.09.2026")
