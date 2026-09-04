"""HTTP-Client und Parser für den OpenAI-kompatiblen Chat-Endpoint."""

import json

import httpx

from backend.config import get_settings


async def chat_completion(
    messages: list[dict],
    tools: list[dict] | None = None,
    model: str | None = None,
    tool_choice: str | None = None,
) -> dict:
    """Sendet eine Chat Completion mit optionalen Function-Schemas."""
    settings = get_settings()
    headers = {
        "Authorization": f"Bearer {settings.scads_api_key}",
        "Content-Type": "application/json",
    }

    payload: dict = {
        "model": model or settings.scads_model,
        "messages": messages,
    }

    if tools:
        payload["tools"] = [
            {"type": "function", "function": t} for t in tools
        ]
        if tool_choice:
            payload["tool_choice"] = tool_choice

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{settings.scads_base_url.rstrip('/')}/chat/completions",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        return response.json()


def extract_tool_call(response: dict) -> dict | None:
    """Liest den ersten Tool-Aufruf, sofern einer vorhanden ist."""
    choices = response.get("choices", [])
    if not choices:
        return None

    message = choices[0].get("message", {})
    tool_calls = message.get("tool_calls", [])

    if not tool_calls:
        return None

    tc = tool_calls[0]
    function = tc.get("function", {})
    raw_arguments = function.get("arguments", "{}")
    try:
        arguments = json.loads(raw_arguments)
    except (json.JSONDecodeError, TypeError):
        arguments = {}
    return {
        "id": tc.get("id"),
        "name": function.get("name"),
        "arguments": arguments,
    }


def extract_content(response: dict) -> str:
    """Liest die Textantwort aus der ersten Auswahl."""
    choices = response.get("choices", [])
    if not choices:
        return ""
    return choices[0].get("message", {}).get("content") or ""


def extract_usage(response: dict) -> tuple[int | None, int | None]:
    """Liest Endpoint-Input- und Output-Tokens ohne Werte zu schätzen."""
    usage = response.get("usage") or {}
    input_tokens = usage.get("prompt_tokens", usage.get("input_tokens"))
    output_tokens = usage.get("completion_tokens", usage.get("output_tokens"))
    return input_tokens, output_tokens
