"""Progressiver Modus mit getrennter Tool-Suche und kleiner Ausführungsphase.

Die erste Conversation dient ausschließlich der Katalogsuche. Danach beginnt
bewusst ein neuer Dialog mit den gefundenen Kandidaten. Dieser Phasenwechsel
ist Teil der API-Schritte und der Workshop-Dokumentation.
"""

import json

from backend.llm_client import chat_completion, extract_content, extract_tool_call
from backend.mcp_client import call_tool, list_all_tools
from backend.metrics import RunMetrics
from backend.tool_search import search

SEARCH_TOOL_SCHEMA = {
    "name": "search_tools",
    "description": "Durchsuche den Toolkatalog nach Werkzeugen für die Nutzeranfrage.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Kurze Suchbegriffe aus der Nutzeranfrage.",
            }
        },
        "required": ["query"],
    },
}
SEARCH_SYSTEM_PROMPT = (
    "Du siehst zunächst nur search_tools. Rufe dieses Tool zwingend mit passenden "
    "Suchbegriffen auf. Beantworte die Fachfrage in dieser Phase noch nicht."
)
EXECUTE_SYSTEM_PROMPT = (
    "Du siehst eine kleine Auswahl relevanter Tools. Rufe das passendste Tool auf "
    "und beantworte die Anfrage anschließend auf Deutsch."
)


async def run_progressive_mode(user_message: str) -> dict:
    """Sucht Kandidaten und führt sie in einer transparent getrennten Conversation aus."""
    all_tools = await list_all_tools()
    search_tools = [SEARCH_TOOL_SCHEMA]
    metrics = RunMetrics()
    steps = [
        {"type": "catalog_loaded", "tool_count": len(all_tools)},
        {"type": "schemas_sent", "tool_count": 1, "phase": "Suche"},
    ]
    search_messages = [
        {"role": "system", "content": SEARCH_SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]
    response = await chat_completion(search_messages, tools=search_tools, tool_choice="required")
    metrics.record(search_tools, response)
    search_call = extract_tool_call(response)

    if not search_call or search_call["name"] != "search_tools":
        answer = "Die verpflichtende Tool-Suche wurde vom Modell nicht aufgerufen."
        steps.append({"type": "selection_failed"})
        return _result(all_tools, [], metrics, answer, steps)

    query = search_call["arguments"].get("query") or user_message
    candidates = search(query, all_tools, top_k=5)
    steps.append(
        {
            "type": "candidates_selected",
            "search_query": query,
            "candidate_names": [tool["name"] for tool in candidates],
        }
    )
    if not candidates:
        answer = "Für diese Anfrage wurde kein passendes Tool im Katalog gefunden."
        steps.append({"type": "no_candidates"})
        return _result(all_tools, candidates, metrics, answer, steps)

    steps.extend(
        [
            {"type": "phase_reset"},
            {"type": "schemas_sent", "tool_count": len(candidates), "phase": "Ausführung"},
        ]
    )
    messages = [
        {"role": "system", "content": EXECUTE_SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]
    response = await chat_completion(messages, tools=candidates, tool_choice="required")
    metrics.record(candidates, response)
    tool_call = extract_tool_call(response)

    if tool_call and tool_call["name"] in {tool["name"] for tool in candidates}:
        tool_result = await call_tool(tool_call["name"], tool_call["arguments"])
        messages.extend(
            [
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": tool_call["id"],
                            "type": "function",
                            "function": {
                                "name": tool_call["name"],
                                "arguments": json.dumps(tool_call["arguments"]),
                            },
                        }
                    ],
                },
                {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(tool_result, ensure_ascii=False),
                },
            ]
        )
        steps.append(
            {
                "type": "tool_called",
                "tool_name": tool_call["name"],
                "tool_arguments": tool_call["arguments"],
            }
        )
        steps.append(
            {"type": "schemas_sent", "tool_count": len(candidates), "phase": "Antwort"}
        )
        response = await chat_completion(messages, tools=candidates)
        metrics.record(candidates, response)

    answer = extract_content(response)
    steps.append({"type": "answer_generated"})
    return _result(all_tools, candidates, metrics, answer, steps)


def _result(
    all_tools: list[dict],
    candidates: list[dict],
    metrics: RunMetrics,
    answer: str,
    steps: list[dict],
) -> dict:
    """Baut die einheitliche API-Antwort des progressiven Modus."""
    return {
        "mode": "progressiv",
        "available_tool_count": len(all_tools),
        "initial_visible_tool_count": 1,
        "selected_candidate_count": len(candidates),
        "selected_candidate_names": [tool["name"] for tool in candidates],
        "metrics": metrics.as_dict(),
        "answer": answer,
        "steps": steps,
    }
