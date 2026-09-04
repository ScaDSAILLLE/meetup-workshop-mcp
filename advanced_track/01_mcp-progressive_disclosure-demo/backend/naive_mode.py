"""Referenzmodus: Bei jedem LLM-Aufruf sind sämtliche MCP-Tools sichtbar."""

import json

from backend.llm_client import chat_completion, extract_content, extract_tool_call
from backend.mcp_client import call_tool, list_all_tools
from backend.metrics import RunMetrics

SYSTEM_PROMPT = (
    "Du bist eine hilfreiche Assistenz. Wähle bei Bedarf das passendste Tool, "
    "verwende dessen Ergebnis und antworte auf Deutsch."
)


async def run_naive_mode(user_message: str) -> dict:
    """Führt einen fortlaufenden Tool-Calling-Dialog mit dem vollständigen Katalog aus."""
    all_tools = await list_all_tools()
    metrics = RunMetrics()
    steps = [
        {"type": "catalog_loaded", "tool_count": len(all_tools)},
        {"type": "schemas_sent", "tool_count": len(all_tools), "phase": "Auswahl"},
    ]
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    response = await chat_completion(messages, tools=all_tools)
    metrics.record(all_tools, response)
    tool_call = extract_tool_call(response)

    if tool_call:
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
        steps.append({"type": "schemas_sent", "tool_count": len(all_tools), "phase": "Antwort"})
        response = await chat_completion(messages, tools=all_tools)
        metrics.record(all_tools, response)

    answer = extract_content(response)
    steps.append({"type": "answer_generated"})
    return {
        "mode": "normal",
        "available_tool_count": len(all_tools),
        "initial_visible_tool_count": len(all_tools),
        "selected_candidate_count": 0,
        "selected_candidate_names": [],
        "metrics": metrics.as_dict(),
        "answer": answer,
        "steps": steps,
    }
