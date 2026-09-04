"""Zählt lokal Schema-Tokens mit der dokumentierten ``cl100k_base``-Kodierung.

Die Werte messen serialisierte Tool-Schemas und sind nicht mit den vom Endpoint
gemeldeten gesamten Input-Tokens gleichzusetzen.
"""

import json

import tiktoken

_ENCODER = tiktoken.get_encoding("cl100k_base")


def _count_tokens(text: str) -> int:
    """Zählt Tokens in einem Text."""
    return len(_ENCODER.encode(text))


def count_schema_tokens(tools: list[dict]) -> int:
    """Zählt die Tokens aller als JSON serialisierten Tool-Schemas.

    Args:
        tools: Tool-Schemas, die einzeln serialisiert und gezählt werden.

    Returns:
        Summe der Tokenzahlen aller Tool-Schemas.
    """
    total = 0
    for tool in tools:
        tool_json = json.dumps(tool, ensure_ascii=False)
        total += _count_tokens(tool_json)
    return total


def count_message_tokens(messages: list[dict]) -> int:
    """Zählt die Tokens aller als JSON serialisierten Nachrichten.

    Args:
        messages: Nachrichten, die einzeln serialisiert und gezählt werden.

    Returns:
        Summe der Tokenzahlen aller Nachrichten.
    """
    total = 0
    for msg in messages:
        msg_json = json.dumps(msg, ensure_ascii=False)
        total += _count_tokens(msg_json)
    return total


def count_tokens(text: str) -> int:
    """Zählt Tokens in einem beliebigen Text."""
    return _count_tokens(text)
