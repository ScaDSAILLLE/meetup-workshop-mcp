import json
from copy import deepcopy
from types import SimpleNamespace

import pytest

from mock_expense_api import ToolRuntime, expected_over_budget
from ptc_demo import (
    PTC_SYSTEM_PROMPT,
    RunStats,
    _dispatch_tool,
    execute_program,
    print_ground_truth,
    print_stats,
    run_baseline,
    run_ptc,
    validate_analysis_result,
    validate_program,
    validate_task_result,
)

VALID_PROGRAM = """
members = get_team_members("engineering")
result = []
for member in members:
    expenses = get_expenses(member["id"], "Q3")
    spent = 0
    for expense in expenses:
        if expense["category"] == "travel" and expense["status"] == "approved":
            spent = spent + expense["amount"]
    if spent > 5000:
        budget_data = get_custom_budget(member["id"])
        budget = budget_data["travel_budget"]
        if spent > budget:
            result = result + [{
                "employee_id": member["id"],
                "name": member["name"],
                "approved_travel_spend": round(spent, 2),
                "budget": budget,
                "over_by": round(spent - budget, 2)
            }]
"""


def test_restricted_program_finds_ground_truth() -> None:
    runtime = ToolRuntime()

    result = execute_program(VALID_PROGRAM, runtime)

    assert result == expected_over_budget()
    assert len(runtime.calls) == 11  # 1 team + 6 expense + 4 conditional budget calls


@pytest.mark.parametrize(
    "code, expected_construct",
    [
        ("import os\nresult = []", "Import"),
        ("result = open('/tmp/demo')", "allowlisted function"),
        ("result = (1).__class__", "Attribute"),
        ("while True:\n    result = []", "While"),
    ],
)
def test_restricted_program_rejects_unsafe_constructs(code: str, expected_construct: str) -> None:
    with pytest.raises(ValueError, match=expected_construct):
        validate_program(code)


def test_program_must_produce_result_list() -> None:
    with pytest.raises(TypeError, match="must be a list"):
        execute_program("result = 42", ToolRuntime())


def test_program_cannot_return_raw_tool_data() -> None:
    code = 'result = get_expenses("ENG001", "Q3")'

    with pytest.raises(ValueError, match="generated result"):
        execute_program(code, ToolRuntime())


def test_result_rejects_inconsistent_overage() -> None:
    result = expected_over_budget()
    result[0]["over_by"] = 1.0

    with pytest.raises(ValueError, match="spend minus budget"):
        validate_analysis_result(result)


def test_result_rejects_duplicate_employee() -> None:
    result = expected_over_budget()
    result.append(deepcopy(result[0]))

    with pytest.raises(ValueError, match="duplicate employee ID"):
        validate_analysis_result(result)


def test_task_result_must_match_independent_fixture() -> None:
    incomplete_result = expected_over_budget()[:1]

    with pytest.raises(ValueError, match="independently calculated"):
        validate_task_result(incomplete_result)


def test_dispatch_rejects_unknown_tool() -> None:
    with pytest.raises(ValueError, match="Unknown tool"):
        _dispatch_tool(ToolRuntime(), "delete_expenses", {})


class FakeMessage:
    def __init__(self, tool_calls=None, content=None):
        self.tool_calls = tool_calls
        self.content = content

    def model_dump(self, exclude_none=True):
        del exclude_none
        result = {"role": "assistant"}
        if self.tool_calls is not None:
            result["tool_calls"] = self.tool_calls
        if self.content is not None:
            result["content"] = self.content
        return result


class FakeClient:
    def __init__(self, messages):
        self.responses = list(messages)
        self.requests = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        self.requests.append(deepcopy(kwargs))
        message = self.responses.pop(0)
        return SimpleNamespace(usage=None, choices=[SimpleNamespace(message=message)])


def tool_call(call_id: str, name: str, arguments: object):
    return SimpleNamespace(
        id=call_id,
        function=SimpleNamespace(name=name, arguments=json.dumps(arguments)),
    )


def test_baseline_returns_tool_errors_to_model() -> None:
    client = FakeClient(
        [
            FakeMessage([tool_call("bad-1", "delete_expenses", {})]),
            FakeMessage(content="Fehler wurde berücksichtigt."),
        ]
    )

    answer, stats = run_baseline(client, "test-model", verbose=False)

    second_request_messages = client.requests[1]["messages"]
    error_message = next(item for item in second_request_messages if item.get("role") == "tool")
    assert "Unknown tool requested" in error_message["content"]
    assert answer == "Fehler wurde berücksichtigt."
    assert stats.model_calls == 2


def test_ptc_rejects_multiple_meta_tool_calls() -> None:
    responses = [
        FakeMessage(
            [
                tool_call(f"call-{attempt}-a", "run_python_analysis", {"code": "result = []"}),
                tool_call(f"call-{attempt}-b", "run_python_analysis", {"code": "result = []"}),
            ]
        )
        for attempt in range(3)
    ]
    client = FakeClient(responses)

    with pytest.raises(RuntimeError, match="valid restricted program"):
        run_ptc(client, "test-model", verbose=False)

    assert len(client.requests) == 3
    final_messages = client.requests[-1]["messages"]
    rejected_ids = {
        item["tool_call_id"] for item in final_messages if item.get("role") == "tool"
    }
    assert rejected_ids == {"call-0-a", "call-0-b", "call-1-a", "call-1-b"}


def test_ptc_checks_meta_tool_name() -> None:
    client = FakeClient(
        [
            FakeMessage([tool_call(f"wrong-{attempt}", "other_tool", {"code": "result = []"})])
            for attempt in range(3)
        ]
    )

    with pytest.raises(RuntimeError, match="valid restricted program"):
        run_ptc(client, "test-model", verbose=False)

    second_request_messages = client.requests[1]["messages"]
    error_message = next(item for item in second_request_messages if item.get("role") == "tool")
    assert "Unexpected PTC tool" in error_message["content"]


def test_ptc_prompt_documents_exact_tool_return_fields() -> None:
    assert "identifier field is named id" in PTC_SYSTEM_PROMPT
    assert 'budget_data["travel_budget"]' in PTC_SYSTEM_PROMPT


def test_comparison_prints_percentages(capsys: pytest.CaptureFixture[str]) -> None:
    baseline = RunStats(
        mode="baseline",
        model_calls=4,
        prompt_tokens=33394,
        bytes_returned_to_model=46291,
        domain_tool_calls=11,
        elapsed_seconds=113.58,
    )
    ptc = RunStats(
        mode="portable PTC",
        model_calls=2,
        prompt_tokens=3346,
        bytes_returned_to_model=231,
        domain_tool_calls=11,
        elapsed_seconds=20.57,
        result_matches_ground_truth=True,
    )

    print_stats([baseline, ptc])
    output = capsys.readouterr().out

    assert "LLM-Aufrufe: 50.0% weniger" in output
    assert "Tokens: 90.0% weniger" in output
    assert "Tool-Payload zum LLM: 99.5% weniger" in output
    assert "Laufzeit: 81.9% weniger" in output
    assert "Fach-Tool-Aufrufe: unverändert (11)" in output


def test_ground_truth_header_is_human_readable(capsys: pytest.CaptureFixture[str]) -> None:
    print_ground_truth()
    output = capsys.readouterr().out

    assert "Ground Truth (Referenzergebnis" in output
    assert "Carol White (ENG003): 6.800,00 USD" in output
    assert "Fatima Saleh (ENG006): 8.900,00 USD" in output
    assert '[{"employee_id"' not in output
