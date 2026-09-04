"""Gemeinsame Metrikerfassung für mehrere LLM-Aufrufe eines Demo-Laufs."""

from dataclasses import dataclass

from backend.llm_client import extract_usage
from backend.token_counter import count_schema_tokens


@dataclass
class RunMetrics:
    """Summiert gesendete Schemas und vom Endpoint gemeldete Tokenwerte."""

    llm_calls: int = 0
    schema_tokens_sent: int = 0
    endpoint_input_tokens: int = 0
    endpoint_output_tokens: int = 0
    endpoint_usage_complete: bool = True

    def record(self, tools: list[dict], response: dict) -> None:
        """Erfasst genau einen abgeschlossenen LLM-Aufruf."""
        self.llm_calls += 1
        self.schema_tokens_sent += count_schema_tokens(tools)
        input_tokens, output_tokens = extract_usage(response)
        if input_tokens is None or output_tokens is None:
            self.endpoint_usage_complete = False
        else:
            self.endpoint_input_tokens += input_tokens
            self.endpoint_output_tokens += output_tokens

    def as_dict(self) -> dict:
        """Gibt die API-Darstellung zurück; unbekannte Endpoint-Werte bleiben ``None``."""
        return {
            "llm_calls": self.llm_calls,
            "schema_tokens_sent": self.schema_tokens_sent,
            "endpoint_input_tokens": (
                self.endpoint_input_tokens if self.endpoint_usage_complete else None
            ),
            "endpoint_output_tokens": (
                self.endpoint_output_tokens if self.endpoint_usage_complete else None
            ),
        }
