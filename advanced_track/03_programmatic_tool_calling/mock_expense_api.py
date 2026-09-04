"""Deterministic, read-only tools used by the workshop demo.

The records intentionally contain more metadata than the analysis needs. This
makes the context cost of traditional tool calling visible without requiring an
external business system or transmitting real personal data.
"""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

TEAM_MEMBERS = [
    {"id": "ENG001", "name": "Alice Chen", "role": "Staff Engineer", "level": "staff"},
    {"id": "ENG002", "name": "Ben Fischer", "role": "Backend Engineer", "level": "mid"},
    {"id": "ENG003", "name": "Carol White", "role": "Engineering Manager", "level": "senior"},
    {"id": "ENG004", "name": "Diego Martin", "role": "Developer Advocate", "level": "senior"},
    {"id": "ENG005", "name": "Eva Novak", "role": "Frontend Engineer", "level": "junior"},
    {"id": "ENG006", "name": "Fatima Saleh", "role": "Principal Engineer", "level": "principal"},
]

# Approved Q3 travel spend and actual budget form the independent ground truth.
TRAVEL_TOTALS = {
    "ENG001": 7200.0,
    "ENG002": 4100.0,
    "ENG003": 6800.0,
    "ENG004": 5200.0,
    "ENG005": 3500.0,
    "ENG006": 8900.0,
}

BUDGETS = {
    "ENG001": {"travel_budget": 8000.0, "reason": "Frequent customer visits"},
    "ENG004": {"travel_budget": 6500.0, "reason": "Conference representation"},
    "ENG006": {"travel_budget": 7500.0, "reason": "Architecture program"},
}


def _make_expenses(employee_id: str) -> list[dict[str, Any]]:
    """Build a stable, metadata-heavy expense report for one employee."""
    total = TRAVEL_TOTALS[employee_id]
    # Twelve entries make the payload large enough to illustrate context growth.
    amounts = [round(total / 12, 2)] * 11
    amounts.append(round(total - sum(amounts), 2))
    expenses: list[dict[str, Any]] = []

    for index, amount in enumerate(amounts, start=1):
        expenses.append(
            {
                "expense_id": f"{employee_id}_Q3_TRAVEL_{index:03d}",
                "employee_id": employee_id,
                "quarter": "Q3",
                "date": f"2026-{7 + (index - 1) // 4:02d}-{3 + index:02d}",
                "category": "travel",
                "description": f"Project travel leg {index}",
                "amount": amount,
                "currency": "USD",
                "status": "approved",
                "merchant": {"name": f"Mobility Partner {index}", "country": "DE"},
                "receipt_url": f"https://expenses.example.invalid/{employee_id}/{index}",
                "approval_chain": ["team-lead", "cost-center-owner", "finance"],
                "payment_method": "corporate_card",
                "project_code": f"MCP-{100 + index}",
                "audit_metadata": {
                    "import_source": "workshop-fixture",
                    "reviewed": True,
                    "tags": ["q3", "travel", "demo", employee_id.lower()],
                },
            }
        )

    # These records are distractors: wrong status or wrong category.
    expenses.extend(
        [
            {
                "expense_id": f"{employee_id}_Q3_REJECTED",
                "employee_id": employee_id,
                "quarter": "Q3",
                "date": "2026-08-20",
                "category": "travel",
                "description": "Rejected upgrade",
                "amount": 2400.0,
                "currency": "USD",
                "status": "rejected",
                "merchant": {"name": "Example Air", "country": "DE"},
                "receipt_url": "https://expenses.example.invalid/rejected",
                "approval_chain": ["team-lead", "finance"],
                "payment_method": "corporate_card",
                "project_code": "MCP-REJECTED",
                "audit_metadata": {"reviewed": True, "tags": ["do-not-count"]},
            },
            {
                "expense_id": f"{employee_id}_Q3_SOFTWARE",
                "employee_id": employee_id,
                "quarter": "Q3",
                "date": "2026-09-10",
                "category": "software",
                "description": "Developer tooling subscription",
                "amount": 3200.0,
                "currency": "USD",
                "status": "approved",
                "merchant": {"name": "Dev Tools Inc.", "country": "US"},
                "receipt_url": "https://expenses.example.invalid/software",
                "approval_chain": ["team-lead", "procurement"],
                "payment_method": "invoice",
                "project_code": "MCP-SOFTWARE",
                "audit_metadata": {"reviewed": True, "tags": ["do-not-count"]},
            },
        ]
    )
    return expenses


EXPENSES = {member["id"]: _make_expenses(member["id"]) for member in TEAM_MEMBERS}


@dataclass
class ToolRuntime:
    """Expose allowlisted tools and keep observable invocation metrics."""

    max_calls: int = 30
    calls: list[dict[str, Any]] = field(default_factory=list)

    def _record(self, name: str, arguments: dict[str, Any], result: Any) -> None:
        if len(self.calls) >= self.max_calls:
            raise RuntimeError(f"Tool-call limit of {self.max_calls} exceeded")
        result_items = len(result) if isinstance(result, list) else 1
        result_bytes = len(
            json.dumps(result, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        )
        self.calls.append(
            {
                "name": name,
                "arguments": arguments,
                "result_items": result_items,
                "result_bytes": result_bytes,
            }
        )

    def get_team_members(self, department: str) -> list[dict[str, Any]]:
        """Return members of the requested department."""
        if department.lower() != "engineering":
            raise ValueError("This workshop fixture only contains the engineering department")
        result = deepcopy(TEAM_MEMBERS)
        self._record("get_team_members", {"department": department}, result)
        return result

    def get_expenses(self, employee_id: str, quarter: str) -> list[dict[str, Any]]:
        """Return the verbose expense report for an employee and quarter."""
        if quarter.upper() != "Q3":
            raise ValueError("This workshop fixture only contains Q3")
        if employee_id not in EXPENSES:
            raise ValueError(f"Unknown employee ID: {employee_id}")
        result = deepcopy(EXPENSES[employee_id])
        self._record("get_expenses", {"employee_id": employee_id, "quarter": quarter}, result)
        return result

    def get_custom_budget(self, user_id: str) -> dict[str, Any]:
        """Return a custom limit or the standard 5,000 USD limit."""
        if user_id not in TRAVEL_TOTALS:
            raise ValueError(f"Unknown employee ID: {user_id}")
        custom = BUDGETS.get(user_id)
        if custom:
            result = {
                "user_id": user_id,
                "has_custom_budget": True,
                **deepcopy(custom),
                "currency": "USD",
            }
        else:
            result = {
                "user_id": user_id,
                "has_custom_budget": False,
                "travel_budget": 5000.0,
                "reason": "Standard quarterly limit",
                "currency": "USD",
            }
        self._record("get_custom_budget", {"user_id": user_id}, result)
        return result


def expected_over_budget() -> list[dict[str, Any]]:
    """Return the fixture's ground truth independently of any model."""
    result = []
    for member in TEAM_MEMBERS:
        employee_id = member["id"]
        spent = TRAVEL_TOTALS[employee_id]
        limit = BUDGETS.get(employee_id, {"travel_budget": 5000.0})["travel_budget"]
        if spent > limit:
            result.append(
                {
                    "employee_id": employee_id,
                    "name": member["name"],
                    "approved_travel_spend": spent,
                    "budget": limit,
                    "over_by": spent - limit,
                }
            )
    return result
