"""Prüft API-Vertrag, Eingabevalidierung und sichere Frontend-Ausgabe."""

from pathlib import Path
from unittest.mock import AsyncMock

from starlette.testclient import TestClient

from backend.main import app

TRACK_ROOT = Path(__file__).resolve().parents[1]


def mode_result(mode):
    return {
        "mode": mode,
        "available_tool_count": 101,
        "initial_visible_tool_count": 1,
        "selected_candidate_count": 0,
        "selected_candidate_names": [],
        "metrics": {
            "llm_calls": 1,
            "schema_tokens_sent": 10,
            "endpoint_input_tokens": 20,
            "endpoint_output_tokens": 3,
        },
        "answer": "Test",
        "steps": [{"type": "answer_generated"}],
    }


def test_api_rejects_empty_message_without_running_demo():
    response = TestClient(app).post("/api/demo", json={"message": "  "})
    assert response.status_code == 400
    assert "error" in response.json()


def test_api_has_stable_mode_and_step_structure(monkeypatch):
    monkeypatch.setattr(
        "backend.main.run_naive_mode", AsyncMock(return_value=mode_result("normal"))
    )
    monkeypatch.setattr(
        "backend.main.run_progressive_mode", AsyncMock(return_value=mode_result("progressiv"))
    )
    payload = TestClient(app).post("/api/demo", json={"message": "Test"}).json()
    assert set(payload) == {"normal", "progressiv"}
    assert payload["progressiv"]["steps"][0]["type"] == "answer_generated"


def test_frontend_uses_step_types_and_no_inner_html():
    javascript = (TRACK_ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
    html = (TRACK_ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
    assert "switch (step.type)" in javascript
    assert "innerHTML" not in javascript
    assert ">100<" not in html
