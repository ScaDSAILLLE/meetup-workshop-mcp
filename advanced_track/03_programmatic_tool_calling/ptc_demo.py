#!/usr/bin/env python3
"""Compare classic tool calling with a portable PTC approximation.

Run `uv run python ptc_demo.py --mode both` and follow the German README.
The generated code executor in this file is intentionally small and educational;
it is not a replacement for an operating-system or container sandbox.
"""

from __future__ import annotations

import argparse
import ast
import json
import math
import time
from dataclasses import dataclass
from typing import Any

from openai import OpenAI

from mock_expense_api import ToolRuntime, expected_over_budget
from workshop_config import load_scads_config

# =============================================================================
# 1. Workshop-Aufgabe und Standardkonfiguration
#
# Der sichtbare Workshop-Text ist deutsch. Der präzise interne Auftrag bleibt
# englisch, weil er zugleich die Fachregeln für die Modellaufrufe festlegt.
# =============================================================================

DEFAULT_BASE_URL = "https://llm.scads.ai/v1"
DEFAULT_MODEL = "Qwen/Qwen3.8-27B"
STANDARD_BUDGET = 5000.0
QUESTION = """Which engineering team members exceeded their approved Q3 travel budget?
The standard quarterly travel budget is 5,000 USD. Only for people above that
standard threshold, check whether they have a custom budget. Use the actual
limit to decide who truly exceeded their budget. Include spend, limit, and overage."""
QUESTION_DE = """Welche Mitglieder des Engineering-Teams haben ihr genehmigtes Reisebudget im
dritten Quartal überschritten? Das Standardbudget beträgt 5.000 USD. Nur bei Personen, deren
genehmigte Reiseausgaben zunächst über diesem Schwellenwert liegen, soll ein mögliches
Sonderbudget abgefragt werden. Für die endgültige Entscheidung zählen das tatsächliche Budget
und ausschließlich genehmigte Ausgaben der Kategorie „travel“."""


# =============================================================================
# 2. Tool-Verträge für die klassische Baseline
#
# Diese OpenAI-kompatiblen Schemas sagen dem Modell, welche Fach-Tools es direkt
# aufrufen darf. Die Implementierungen und Mock-Daten liegen separat in
# mock_expense_api.py.
# =============================================================================

BASELINE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_team_members",
            "description": "Return all members of a department with ID, name, role, and level.",
            "parameters": {
                "type": "object",
                "properties": {"department": {"type": "string"}},
                "required": ["department"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_expenses",
            "description": (
                "Return all verbose expense records for one employee and quarter. Only approved "
                "travel records count toward the travel budget."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string"},
                    "quarter": {"type": "string", "enum": ["Q3"]},
                },
                "required": ["employee_id", "quarter"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_custom_budget",
            "description": "Return the actual quarterly travel budget for one employee.",
            "parameters": {
                "type": "object",
                "properties": {"user_id": {"type": "string"}},
                "required": ["user_id"],
                "additionalProperties": False,
            },
        },
    },
]


# =============================================================================
# 3. Vertrag für das portable Programmatic Tool Calling
#
# Anders als die Baseline erhält Qwen nur ein Meta-Tool. Es schreibt Python in
# dessen `code`-Argument; der Host führt das Programm später nahe an den Daten
# aus und sendet ausschließlich die Variable `result` an das Modell zurück.
# =============================================================================

PTC_TOOL = {
    "type": "function",
    "function": {
        "name": "run_python_analysis",
        "description": "Execute a restricted Python program that can call the expense tools.",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Restricted Python source code. It must assign the final list to result.",
                }
            },
            "required": ["code"],
            "additionalProperties": False,
        },
    },
}


PTC_SYSTEM_PROMPT = f"""You are writing a small data-analysis program, not doing the arithmetic yourself.
Call run_python_analysis exactly once with Python code that answers the user question.

The program may use only:
- get_team_members(department)
- get_expenses(employee_id, quarter)
- get_custom_budget(user_id)
- round(number, digits), len(value), sum(values)

Exact tool return contracts:
- get_team_members returns a list of objects with: id, name, role, level.
  The employee identifier field is named id, never employee_id.
- get_expenses returns a list of objects. Relevant fields are: category, status, amount.
- get_custom_budget always returns an object with: user_id, has_custom_budget,
  travel_budget, reason, currency. The numeric limit is budget_data["travel_budget"].
  Never compare the complete budget object with a number and never check it for None.

Rules for the restricted language:
- Use assignments, for loops, if statements, lists, dictionaries, subscripts, and comparisons.
- Do not import anything, define functions, use attributes/methods such as .get(), or use while loops.
- Since methods are unavailable, add an item with: result = result + [{{"key": value}}]
- First fetch engineering members, then each member's Q3 expenses.
- Count only records whose category is "travel" and status is "approved".
- Call get_custom_budget only when approved travel spend is above {STANDARD_BUDGET:.0f}.
- Assign a list of dictionaries to a variable named result. Each final dictionary must contain
  employee_id, name, approved_travel_spend, budget, and over_by.
- Do not put raw expense records in result.
"""


# =============================================================================
# 4. Messwerte und gemeinsame Ausgabehelfer
#
# Beide Modi erfassen dieselben beobachtbaren Größen. Dadurch bleibt der
# spätere Vergleich unabhängig von der jeweiligen Orchestrierung.
# =============================================================================

@dataclass
class RunStats:
    """Metrics that are observable through the compatible API and local host."""

    mode: str
    model_calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    bytes_returned_to_model: int = 0
    domain_tool_calls: int = 0
    domain_result_bytes: int = 0
    elapsed_seconds: float = 0.0
    result_matches_ground_truth: bool | None = None

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


def _record_usage(stats: RunStats, response: Any) -> None:
    stats.model_calls += 1
    if response.usage:
        stats.prompt_tokens += response.usage.prompt_tokens or 0
        stats.completion_tokens += response.usage.completion_tokens or 0


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _status(enabled: bool, label: str, message: str) -> None:
    """Print progress before potentially slow API and tool phases."""
    if enabled:
        print(f"\n[{label}] {message}", flush=True)


def _format_number_de(value: float) -> str:
    """Format a number with German thousands and decimal separators."""
    return f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def print_ground_truth() -> None:
    """Show the deterministic reference result in a workshop-friendly form."""
    print("\nGround Truth (Referenzergebnis der festen Workshop-Daten):")
    for entry in expected_over_budget():
        print(
            f"  - {entry['name']} ({entry['employee_id']}): "
            f"{_format_number_de(entry['approved_travel_spend'])} USD Ausgaben, "
            f"{_format_number_de(entry['budget'])} USD Budget, "
            f"{_format_number_de(entry['over_by'])} USD darüber"
        )


def _summarize_calls(calls: list[dict[str, Any]]) -> str:
    counts: dict[str, int] = {}
    for call in calls:
        counts[call["name"]] = counts.get(call["name"], 0) + 1
    return ", ".join(f"{count}x {name}" for name, count in counts.items())


def _dispatch_tool(runtime: ToolRuntime, name: str, arguments: dict[str, Any]) -> Any:
    """Dispatch only explicitly allowlisted domain tools."""
    functions = {
        "get_team_members": runtime.get_team_members,
        "get_expenses": runtime.get_expenses,
        "get_custom_budget": runtime.get_custom_budget,
    }
    if name not in functions:
        raise ValueError(f"Unknown tool requested: {name}")
    return functions[name](**arguments)


# =============================================================================
# 5. Klassisches Tool Calling
#
# Qwen entscheidet in jeder Runde über den nächsten Tool-Aufruf. Jedes
# vollständige Tool-Ergebnis wird als Nachricht in den Modellkontext eingefügt.
# =============================================================================

def run_baseline(client: OpenAI, model: str, verbose: bool = True) -> tuple[str, RunStats]:
    """Run the normal model -> tool -> model loop with full tool payloads."""
    runtime = ToolRuntime()
    stats = RunStats(mode="baseline")
    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "Use the available tools to solve the task. Never guess records or totals. "
                "Fetch expenses for every team member and follow the stated budget-check order. "
                "Write the final answer in German."
            ),
        },
        {"role": "user", "content": QUESTION},
    ]
    started = time.perf_counter()

    _status(
        verbose,
        "Baseline",
        "Das Modell steuert die Analyse Runde für Runde. Vollständige Tool-Ergebnisse "
        "werden jeweils in seinen Kontext aufgenommen.",
    )

    for request_number in range(1, 9):
        _status(
            verbose,
            f"Baseline | LLM {request_number}",
            "Sende bisherigen Verlauf an Qwen und warte auf Tool-Auswahl oder Abschlussantwort ...",
        )
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=BASELINE_TOOLS,
            tool_choice="auto",
            extra_body={"disable_fallbacks": True},
        )
        _record_usage(stats, response)
        message = response.choices[0].message
        messages.append(message.model_dump(exclude_none=True))

        if not message.tool_calls:
            stats.domain_tool_calls = len(runtime.calls)
            stats.domain_result_bytes = sum(call["result_bytes"] for call in runtime.calls)
            stats.elapsed_seconds = time.perf_counter() - started
            _status(
                verbose,
                "Baseline | Fertig",
                "Qwen hat die Rohdaten selbst ausgewertet und eine Antwort formuliert.",
            )
            return message.content or "", stats

        # Compatible APIs can request several independent tools in one response.
        calls_before = len(runtime.calls)
        batch_bytes = 0
        batch_items = 0
        for tool_call in message.tool_calls:
            result: Any = None
            try:
                arguments = json.loads(tool_call.function.arguments)
                if not isinstance(arguments, dict):
                    raise TypeError("Tool arguments must be a JSON object")
                result = _dispatch_tool(runtime, tool_call.function.name, arguments)
                content = _json(result)
            except (TypeError, ValueError, RuntimeError, json.JSONDecodeError) as error:
                content = _json({"error": str(error)})
            result_bytes = len(content.encode("utf-8"))
            batch_bytes += result_bytes
            batch_items += len(result) if isinstance(result, list) else 1
            stats.bytes_returned_to_model += result_bytes
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": content,
                }
            )
        _status(
            verbose,
            "Baseline | Tools",
            f"Ausgeführt: {_summarize_calls(runtime.calls[calls_before:])}. "
            f"{batch_items} Ergebnisobjekte mit {batch_bytes:,} Bytes gehen jetzt zurück "
            "in den Modellkontext.",
        )

    raise RuntimeError("Baseline stopped after 8 model calls without a final answer")


# =============================================================================
# 6. Erlaubter Python-Teilumfang und AST-Sicherheitsprüfung
#
# Die Allowlist demonstriert eine Policy-Grenze: Nur die für die Analyse nötigen
# Syntaxelemente und Funktionsaufrufe sind zulässig. Das ist keine Prozess-
# isolation und ersetzt keine produktive Sandbox mit Ressourcenlimits.
# =============================================================================

ALLOWED_AST_NODES = {
    ast.Module,
    ast.Assign,
    ast.AugAssign,
    ast.For,
    ast.If,
    ast.Expr,
    ast.Name,
    ast.Load,
    ast.Store,
    ast.Constant,
    ast.List,
    ast.Dict,
    ast.Subscript,
    ast.Call,
    ast.keyword,
    ast.Compare,
    ast.Eq,
    ast.NotEq,
    ast.Gt,
    ast.GtE,
    ast.Lt,
    ast.LtE,
    ast.BoolOp,
    ast.And,
    ast.Or,
    ast.BinOp,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.UnaryOp,
    ast.USub,
}
ALLOWED_CALLS = {
    "get_team_members",
    "get_expenses",
    "get_custom_budget",
    "round",
    "len",
    "sum",
}


def validate_program(code: str) -> ast.Module:
    """Parse generated code and reject syntax outside the workshop subset."""
    if len(code) > 8000:
        raise ValueError("Generated program is too long (maximum: 8,000 characters)")
    try:
        tree = ast.parse(code, mode="exec")
    except SyntaxError as error:
        raise ValueError(f"Invalid Python syntax: {error.msg}") from error

    nodes = list(ast.walk(tree))
    if len(nodes) > 500:
        raise ValueError("Generated program is too complex (maximum: 500 AST nodes)")

    for node in nodes:
        if type(node) not in ALLOWED_AST_NODES:
            raise ValueError(f"Disallowed Python construct: {type(node).__name__}")
        if isinstance(node, ast.Name) and node.id.startswith("__"):
            raise ValueError("Dunder names are not allowed")
        if isinstance(node, ast.Call) and (
            not isinstance(node.func, ast.Name) or node.func.id not in ALLOWED_CALLS
        ):
            raise ValueError("Only explicitly allowlisted function calls are allowed")
    return tree


# =============================================================================
# 7. Lokale Ausführung und Ergebnisgrenze
#
# Erst wird der Syntaxbaum validiert, dann läuft der Code mit reduzierten
# Built-ins und drei read-only Fach-Tools. Eine zweite Prüfung verhindert, dass
# umfangreiche Rohdaten über `result` zurück in den Modellkontext gelangen.
# =============================================================================

def execute_program(code: str, runtime: ToolRuntime) -> Any:
    """Execute validated generated code with only read-only workshop tools."""
    tree = validate_program(code)
    safe_globals: dict[str, Any] = {
        "__builtins__": {"len": len, "round": round, "sum": sum},
        "get_team_members": runtime.get_team_members,
        "get_expenses": runtime.get_expenses,
        "get_custom_budget": runtime.get_custom_budget,
    }
    local_state: dict[str, Any] = {}
    exec(compile(tree, "<generated-ptc-program>", "exec"), safe_globals, local_state)  # noqa: S102
    if "result" not in local_state:
        raise ValueError("The generated program did not assign a variable named 'result'")
    result = local_state["result"]
    if not isinstance(result, list):
        raise TypeError("The generated program's result must be a list")
    validate_analysis_result(result)
    return result


def validate_analysis_result(result: list[Any]) -> None:
    """Keep verbose or malformed data from crossing the PTC context boundary."""
    expected_keys = {
        "employee_id",
        "name",
        "approved_travel_spend",
        "budget",
        "over_by",
    }
    if len(result) > 6:
        raise ValueError("The generated result contains too many entries")
    employee_ids: set[str] = set()
    for entry in result:
        if not isinstance(entry, dict) or set(entry) != expected_keys:
            raise ValueError("Every result entry must contain exactly the five requested fields")
        if not isinstance(entry["employee_id"], str) or not isinstance(entry["name"], str):
            raise TypeError("Employee ID and name must be strings")
        if not entry["employee_id"].strip() or not entry["name"].strip():
            raise ValueError("Employee ID and name must not be empty")
        if entry["employee_id"] in employee_ids:
            raise ValueError("The generated result contains a duplicate employee ID")
        employee_ids.add(entry["employee_id"])
        for field in ("approved_travel_spend", "budget", "over_by"):
            value = entry[field]
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"Result field '{field}' must be numeric")
            if not math.isfinite(value):
                raise ValueError(f"Result field '{field}' must be finite")
        if entry["approved_travel_spend"] <= entry["budget"] or entry["over_by"] <= 0:
            raise ValueError("Every result entry must describe an actual budget overrun")
        calculated_overage = entry["approved_travel_spend"] - entry["budget"]
        if not math.isclose(entry["over_by"], calculated_overage, abs_tol=0.01):
            raise ValueError("Result field 'over_by' does not match spend minus budget")


def validate_task_result(result: list[dict[str, Any]]) -> None:
    """Check the model-generated analysis against the independent workshop fixture."""
    if sorted(result, key=lambda entry: entry["employee_id"]) != sorted(
        expected_over_budget(), key=lambda entry: entry["employee_id"]
    ):
        raise ValueError("The generated result does not match the independently calculated result")


# =============================================================================
# 8. Portables Programmatic Tool Calling
#
# Qwen erzeugt zunächst ein Analyseprogramm. Dieses ruft lokal mehrere Tools
# auf, filtert deren Ergebnisse und liefert nur eine kompakte Liste zurück. Bei
# ungültigem Code darf das Modell anhand einer knappen Fehlermeldung reparieren.
# =============================================================================

def run_ptc(client: OpenAI, model: str, verbose: bool = True) -> tuple[str, RunStats]:
    """Ask the model for code, execute near the data, and return only its result."""
    stats = RunStats(mode="portable PTC")
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": PTC_SYSTEM_PROMPT},
        {"role": "user", "content": QUESTION},
    ]
    started = time.perf_counter()

    _status(
        verbose,
        "PTC",
        "Qwen soll einmalig ein Analyseprogramm schreiben. Die umfangreichen Fachresultate "
        "werden danach lokal verarbeitet.",
    )

    # Invalid generated code is returned as a tool error so the model gets two
    # opportunities to repair it. Domain data is not included in these errors.
    for attempt in range(1, 4):
        # Failed attempts use a fresh read-only runtime and cannot exhaust the
        # successful attempt's tool budget.
        runtime = ToolRuntime()
        _status(
            verbose,
            f"PTC | Codegenerierung {attempt}",
            "Sende Tool-Verträge und Aufgabe an Qwen; warte auf generierten Python-Code ...",
        )
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=[PTC_TOOL],
            tool_choice={"type": "function", "function": {"name": "run_python_analysis"}},
            extra_body={"disable_fallbacks": True},
        )
        _record_usage(stats, response)
        message = response.choices[0].message
        messages.append(message.model_dump(exclude_none=True))

        if not message.tool_calls:
            raise RuntimeError("Model did not call run_python_analysis")

        if len(message.tool_calls) != 1:
            error_payload = _json({"error": "Call run_python_analysis exactly once per response"})
            for rejected_call in message.tool_calls:
                messages.append(
                    {"role": "tool", "tool_call_id": rejected_call.id, "content": error_payload}
                )
                stats.bytes_returned_to_model += len(error_payload.encode("utf-8"))
            messages.append(
                {"role": "user", "content": "Call run_python_analysis exactly once."}
            )
            continue

        tool_call = message.tool_calls[0]
        try:
            if tool_call.function.name != PTC_TOOL["function"]["name"]:
                raise ValueError(f"Unexpected PTC tool: {tool_call.function.name}")
            arguments = json.loads(tool_call.function.arguments)
            if not isinstance(arguments, dict):
                raise TypeError("Tool arguments must be a JSON object")
            code = arguments["code"]
            if not isinstance(code, str):
                raise TypeError("Tool argument 'code' must be a string")
            print(f"\n--- Vom Modell erzeugtes Programm (Versuch {attempt}) ---")
            print(code)
            print("--- Ende des Programms ---")
            _status(
                verbose,
                "PTC | Sicherheitsgrenze",
                "Prüfe Syntax, AST-Allowlist, erlaubte Funktionen und Ergebnisgrenzen; "
                "führe das Programm danach lokal aus ...",
            )
            compact_result = execute_program(code, runtime)
            validate_task_result(compact_result)
        except (KeyError, TypeError, ValueError, RuntimeError, json.JSONDecodeError) as error:
            print(f"Abgelehnt: {error}")
            error_payload = _json({"error": str(error)})
            stats.bytes_returned_to_model += len(error_payload.encode("utf-8"))
            messages.append(
                {"role": "tool", "tool_call_id": tool_call.id, "content": error_payload}
            )
            messages.append(
                {
                    "role": "user",
                    "content": "Correct the program. Follow the restricted-language rules exactly.",
                }
            )
            continue

        expense_calls = [call for call in runtime.calls if call["name"] == "get_expenses"]
        budget_calls = [call for call in runtime.calls if call["name"] == "get_custom_budget"]
        expense_records = sum(call["result_items"] for call in expense_calls)
        local_bytes = sum(call["result_bytes"] for call in runtime.calls)
        _status(
            verbose,
            "PTC | Lokale Auswertung",
            f"Erfolgreich: {len(expense_calls)} Expense-Reports mit {expense_records} Buchungen "
            f"und {len(budget_calls)} bedingte Budgetprüfungen. {local_bytes:,} Bytes "
            "Fachdaten blieben in der lokalen Runtime.",
        )

        # This compact payload is the crucial PTC boundary: verbose expense
        # records stayed in the local runtime and never entered model context.
        compact_payload = _json({"result": compact_result})
        stats.bytes_returned_to_model += len(compact_payload.encode("utf-8"))
        messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": compact_payload})
        messages.append(
            {
                "role": "user",
                "content": (
                    "Present only the supplied result in German. Do not infer missing facts or "
                    "reasons. State that no one exceeded the budget if the result list is empty."
                ),
            }
        )

        _status(
            verbose,
            "PTC | Verdichtung",
            f"Nur {len(compact_result)} Ergebniszeilen mit "
            f"{len(compact_payload.encode('utf-8')):,} Bytes gehen an Qwen. "
            "Warte auf die sprachliche Abschlussantwort ...",
        )

        final_response = client.chat.completions.create(
            model=model,
            messages=messages,
            extra_body={"disable_fallbacks": True},
        )
        _record_usage(stats, final_response)
        stats.domain_tool_calls = len(runtime.calls)
        stats.domain_result_bytes = local_bytes
        stats.elapsed_seconds = time.perf_counter() - started
        stats.result_matches_ground_truth = sorted(
            compact_result, key=lambda entry: entry["employee_id"]
        ) == sorted(expected_over_budget(), key=lambda entry: entry["employee_id"])
        return final_response.choices[0].message.content or "", stats

    raise RuntimeError("Model did not produce a valid restricted program after 3 attempts")


# =============================================================================
# 9. Gemeinsamer Metrikvergleich
#
# Die Ausgabe beschreibt genau diesen Live-Lauf und vermeidet bewusst eine
# Benchmark-Aussage aus einer einzelnen Messung.
# =============================================================================

def print_stats(stats: list[RunStats]) -> None:
    """Print measurements without claiming that one live run is a benchmark."""
    print("\n=== Beobachtete Metriken (ein Lauf, kein Benchmark) ===")
    header = (
        f"{'Modus':<15} {'LLM':>5} {'Tools':>7} {'Tokens':>10} {'Bytes->LLM':>12} {'Sekunden':>10}"
    )
    print(header)
    print("-" * len(header))
    for item in stats:
        print(
            f"{item.mode:<15} {item.model_calls:>5} {item.domain_tool_calls:>7} "
            f"{item.total_tokens:>10} {item.bytes_returned_to_model:>12} "
            f"{item.elapsed_seconds:>10.2f}"
        )

    if len(stats) != 2:
        return

    baseline = next((item for item in stats if item.mode == "baseline"), None)
    ptc = next((item for item in stats if item.mode == "portable PTC"), None)
    if not baseline or not ptc:
        return

    def comparison(before: float, after: float) -> str:
        if not before:
            return "nicht vergleichbar"
        percentage = abs(after - before) / before * 100
        if after < before:
            return f"{percentage:.1f}% weniger"
        if after > before:
            return f"{percentage:.1f}% mehr"
        return "unverändert"

    print("\n=== Einordnung dieses Laufs ===")
    print(
        f"- LLM-Aufrufe: {comparison(baseline.model_calls, ptc.model_calls)} "
        f"({baseline.model_calls} -> {ptc.model_calls})."
    )
    if baseline.domain_tool_calls == ptc.domain_tool_calls:
        print(
            f"- Fach-Tool-Aufrufe: unverändert ({ptc.domain_tool_calls}). PTC beschafft also "
            "dieselben Daten, verarbeitet sie aber an einem anderen Ort."
        )
    else:
        print(
            f"- Fach-Tool-Aufrufe: {comparison(baseline.domain_tool_calls, ptc.domain_tool_calls)} "
            f"({baseline.domain_tool_calls} -> {ptc.domain_tool_calls})."
        )
    print(
        f"- Tokens: {comparison(baseline.total_tokens, ptc.total_tokens)} "
        f"({baseline.total_tokens:,} -> {ptc.total_tokens:,})."
    )
    print(
        f"- Tool-Payload zum LLM: "
        f"{comparison(baseline.bytes_returned_to_model, ptc.bytes_returned_to_model)} "
        f"({baseline.bytes_returned_to_model:,} -> {ptc.bytes_returned_to_model:,} Bytes)."
    )
    print(
        f"- Laufzeit: {comparison(baseline.elapsed_seconds, ptc.elapsed_seconds)} "
        f"({baseline.elapsed_seconds:.2f} -> {ptc.elapsed_seconds:.2f} Sekunden)."
    )
    print(
        "- PTC-Ergebnis gegen Ground Truth: "
        + ("korrekt." if ptc.result_matches_ground_truth else "ABWEICHUNG - Programm prüfen.")
    )
    print(
        "- Aussagekraft: einzelner Live-Lauf, kein Benchmark; Netz, Warteschlange und "
        "Modellstrategie können schwanken."
    )


# =============================================================================
# 10. Kommandozeile und Programmstart
#
# main() lädt die gemeinsame Workshop-Konfiguration, startet den gewählten
# Modus und führt beide Ergebnisse in derselben Metrikdarstellung zusammen.
# =============================================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("baseline", "ptc", "both"),
        default="both",
        help="Demo mode to run (default: both)",
    )
    parser.add_argument("--model", help=f"Model ID (default: {DEFAULT_MODEL})")
    parser.add_argument(
        "--base-url", help=f"OpenAI-compatible API URL (default: {DEFAULT_BASE_URL})"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Hide explanatory progress messages",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_scads_config(DEFAULT_BASE_URL, DEFAULT_MODEL)
    model = args.model or config.model
    base_url = args.base_url or config.base_url
    client = OpenAI(api_key=config.api_key, base_url=base_url, timeout=120.0, max_retries=1)

    print(f"Endpoint: {base_url}")
    print(f"Model:    {model}")
    print_ground_truth()
    if not args.quiet:
        print("\nWorkshop-Aufgabe:")
        print(QUESTION_DE)
        print(
            "\nDie Ground Truth ist vorab bekannt und dient nach dem Lauf zur fachlichen "
            "Kontrolle beider Ansätze."
        )

    all_stats: list[RunStats] = []
    if args.mode in {"baseline", "both"}:
        print("\n=== Klassisches Tool Calling ===")
        answer, stats = run_baseline(client, model, verbose=not args.quiet)
        print(answer)
        all_stats.append(stats)
    if args.mode in {"ptc", "both"}:
        print("\n=== Portable Programmatic Tool Calling ===")
        answer, stats = run_ptc(client, model, verbose=not args.quiet)
        print(answer)
        all_stats.append(stats)

    print_stats(all_stats)


if __name__ == "__main__":
    main()
