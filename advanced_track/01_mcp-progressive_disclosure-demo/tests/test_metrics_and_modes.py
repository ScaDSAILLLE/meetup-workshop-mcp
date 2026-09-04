"""Offline-Prüfungen der kumulativen Metriken und stabilen Schrittstruktur."""

from unittest.mock import AsyncMock

import pytest

from backend.metrics import RunMetrics
from backend.progressive_mode import SEARCH_TOOL_SCHEMA, run_progressive_mode
from backend.token_counter import count_schema_tokens


def response(*, tool_name=None, arguments="{}", content="", input_tokens=10, output_tokens=2):
    message = {"content": content}
    if tool_name:
        message["tool_calls"] = [
            {
                "id": f"call-{tool_name}",
                "function": {"name": tool_name, "arguments": arguments},
            }
        ]
    return {
        "choices": [{"message": message}],
        "usage": {"prompt_tokens": input_tokens, "completion_tokens": output_tokens},
    }


def test_metrics_sum_every_llm_request_and_endpoint_usage():
    tools = [{"name": "a", "description": "A", "parameters": {}}]
    metrics = RunMetrics()
    metrics.record(tools, response(input_tokens=11, output_tokens=3))
    metrics.record(tools, response(input_tokens=17, output_tokens=5))
    assert metrics.as_dict() == {
        "llm_calls": 2,
        "schema_tokens_sent": 2 * count_schema_tokens(tools),
        "endpoint_input_tokens": 28,
        "endpoint_output_tokens": 8,
    }


def test_metrics_do_not_invent_missing_endpoint_usage():
    metrics = RunMetrics()
    metrics.record([], {"choices": []})
    assert metrics.as_dict()["endpoint_input_tokens"] is None
    assert metrics.as_dict()["endpoint_output_tokens"] is None


@pytest.mark.asyncio
async def test_progressive_mode_counts_candidate_schemas_for_both_calls(monkeypatch):
    tools = [
        {"name": "get_weather", "description": "weather", "parameters": {}},
        {"name": "get_forecast", "description": "weather forecast", "parameters": {}},
    ]
    completions = AsyncMock(
        side_effect=[
            response(tool_name="search_tools", arguments='{"query":"weather"}'),
            response(tool_name="get_weather", arguments='{"city":"Leipzig"}'),
            response(content="Sonnig."),
        ]
    )
    monkeypatch.setattr("backend.progressive_mode.list_all_tools", AsyncMock(return_value=tools))
    monkeypatch.setattr("backend.progressive_mode.chat_completion", completions)
    monkeypatch.setattr("backend.progressive_mode.call_tool", AsyncMock(return_value={"temp": 21}))

    result = await run_progressive_mode("Wie ist das Wetter?")

    expected = count_schema_tokens([SEARCH_TOOL_SCHEMA]) + 2 * count_schema_tokens(tools)
    assert result["metrics"]["schema_tokens_sent"] == expected
    assert result["metrics"]["llm_calls"] == 3
    assert result["selected_candidate_count"] == 2
    assert [step["type"] for step in result["steps"]] == [
        "catalog_loaded",
        "schemas_sent",
        "candidates_selected",
        "phase_reset",
        "schemas_sent",
        "tool_called",
        "schemas_sent",
        "answer_generated",
    ]


@pytest.mark.asyncio
async def test_progressive_mode_stops_after_zero_candidates(monkeypatch):
    completions = AsyncMock(
        return_value=response(tool_name="search_tools", arguments='{"query":"Quantenlyrik"}')
    )
    monkeypatch.setattr(
        "backend.progressive_mode.list_all_tools",
        AsyncMock(
            return_value=[{"name": "get_weather", "description": "weather", "parameters": {}}]
        ),
    )
    monkeypatch.setattr("backend.progressive_mode.chat_completion", completions)

    result = await run_progressive_mode("Quantenlyrik")

    assert result["selected_candidate_count"] == 0
    assert result["metrics"]["llm_calls"] == 1
    assert result["steps"][-1]["type"] == "no_candidates"
