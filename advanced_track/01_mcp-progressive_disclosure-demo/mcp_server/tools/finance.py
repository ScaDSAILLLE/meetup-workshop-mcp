"""Simulierte Finanzwerkzeuge für Rechnungen, Zahlungen und Berichte."""

from mcp_server.server import mcp


@mcp.tool
def get_invoice(invoice_id: int) -> dict:
    """
    Retrieve detailed information about a specific invoice.

    Use this tool when the user knows the invoice ID and wants
    full billing details including line items, tax, and payment status.

    Args:
        invoice_id: Unique numeric identifier of the invoice.

    Returns:
        Complete invoice record.
    """
    return {
        "invoice_id": invoice_id,
        "customer_id": 42,
        "items": [
            {"description": "Widget Pro", "quantity": 2, "unit_price": 29.99, "total": 59.98},
        ],
        "subtotal": 59.98,
        "tax_rate": 0.19,
        "tax_amount": 11.40,
        "total": 71.38,
        "status": "paid",
        "issue_date": "2024-03-15",
        "due_date": "2024-04-14",
        "paid_date": "2024-03-16",
    }


@mcp.tool
def create_invoice(customer_id: int, items: list[dict]) -> dict:
    """
    Create a new invoice for a customer.

    Use this tool when the user wants to generate a billing invoice.
    Each item should have description, quantity, and unit_price.

    Args:
        customer_id: ID of the customer being invoiced.
        items: List of invoice items, each with description, quantity, and unit_price.

    Returns:
        The created invoice with assigned invoice ID and calculated totals.
    """
    subtotal = sum(item.get("unit_price", 0) * item.get("quantity", 1) for item in items)
    tax = round(subtotal * 0.19, 2)
    return {
        "invoice_id": 3001,
        "customer_id": customer_id,
        "items": items,
        "subtotal": subtotal,
        "tax_amount": tax,
        "total": subtotal + tax,
        "status": "pending",
        "issue_date": "2026-08-19",
        "due_date": "2026-09-18",
    }


@mcp.tool
def calculate_tax(amount: float, region: str = "DE") -> dict:
    """
    Calculate tax for a given amount and region.

    Use this tool when the user wants to compute VAT/sales tax
    for a specific monetary amount and jurisdiction.

    Args:
        amount: The monetary amount before tax.
        region: Tax region code (default: DE for Germany).

    Returns:
        Tax breakdown including rate, tax amount, and total.
    """
    rates = {"DE": 0.19, "AT": 0.20, "CH": 0.077, "US": 0.08}
    rate = rates.get(region, 0.19)
    tax = round(amount * rate, 2)
    return {
        "amount": amount,
        "region": region,
        "tax_rate": rate,
        "tax_amount": tax,
        "total": amount + tax,
    }


@mcp.tool
def process_payment(invoice_id: int, amount: float, method: str = "credit_card") -> dict:
    """
    Process a payment for an invoice.

    Use this tool when the user wants to pay an invoice.
    Supported methods: credit_card, bank_transfer, paypal.

    Args:
        invoice_id: ID of the invoice to pay.
        amount: Payment amount.
        method: Payment method (default: credit_card).

    Returns:
        Payment confirmation with transaction ID.
    """
    return {
        "payment_id": 8001,
        "invoice_id": invoice_id,
        "amount": amount,
        "method": method,
        "status": "completed",
        "transaction_id": "TXN-2026-8001",
        "processed_at": "2026-08-19",
    }


@mcp.tool
def get_payment_status(payment_id: int) -> dict:
    """
    Check the status of a payment.

    Use this tool when the user wants to verify whether a payment
    has been processed, is pending, or has failed.

    Args:
        payment_id: Unique numeric identifier of the payment.

    Returns:
        Payment status information.
    """
    return {
        "payment_id": payment_id,
        "status": "completed",
        "amount": 71.38,
        "method": "credit_card",
        "processed_at": "2024-03-16",
    }


@mcp.tool
def get_financial_report(start_date: str, end_date: str) -> dict:
    """
    Generate a financial report for a date range.

    Use this tool when the user wants an overview of revenue, expenses,
    and profit for a specific time period.

    Args:
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.

    Returns:
        Financial summary including revenue, expenses, and net profit.
    """
    return {
        "period": f"{start_date} to {end_date}",
        "revenue": 125000.00,
        "expenses": 87000.00,
        "gross_profit": 38000.00,
        "net_profit": 28000.00,
        "profit_margin": 22.4,
    }


@mcp.tool
def get_balance_sheet(date: str) -> dict:
    """
    Retrieve the balance sheet for a specific date.

    Use this tool when the user wants to see assets, liabilities,
    and equity as of a particular date.

    Args:
        date: Balance sheet date in YYYY-MM-DD format.

    Returns:
        Balance sheet with assets, liabilities, and equity.
    """
    return {
        "date": date,
        "assets": {
            "current": 45000.00,
            "fixed": 120000.00,
            "total": 165000.00,
        },
        "liabilities": {
            "current": 18000.00,
            "long_term": 50000.00,
            "total": 68000.00,
        },
        "equity": 97000.00,
    }


@mcp.tool
def get_income_statement(start_date: str, end_date: str) -> dict:
    """
    Generate an income statement for a date range.

    Use this tool when the user wants a profit and loss statement
    showing revenue, cost of goods sold, and operating expenses.

    Args:
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.

    Returns:
        Income statement with revenue, expenses, and net income.
    """
    return {
        "period": f"{start_date} to {end_date}",
        "revenue": 125000.00,
        "cost_of_goods_sold": 52000.00,
        "gross_profit": 73000.00,
        "operating_expenses": 45000.00,
        "operating_income": 28000.00,
        "net_income": 22000.00,
    }


@mcp.tool
def get_cash_flow(start_date: str, end_date: str) -> dict:
    """
    Generate a cash flow statement for a date range.

    Use this tool when the user wants to see cash inflows and outflows
    from operating, investing, and financing activities.

    Args:
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.

    Returns:
        Cash flow statement with operating, investing, and financing sections.
    """
    return {
        "period": f"{start_date} to {end_date}",
        "operating": {
            "net_income": 22000.00,
            "depreciation": 5000.00,
            "changes_in_working_capital": -3000.00,
            "total": 24000.00,
        },
        "investing": {
            "equipment_purchase": -15000.00,
            "total": -15000.00,
        },
        "financing": {
            "loan_repayment": -5000.00,
            "total": -5000.00,
        },
        "net_cash_flow": 4000.00,
    }


@mcp.tool
def create_budget(name: str, amount: float, period: str = "monthly") -> dict:
    """
    Create a new budget for tracking expenses.

    Use this tool when the user wants to set up a budget
    for a department, project, or category.

    Args:
        name: Name of the budget (e.g., 'Marketing Q1').
        amount: Total budget amount.
        period: Budget period - monthly, quarterly, or annual (default: monthly).

    Returns:
        The created budget with assigned budget ID.
    """
    return {
        "budget_id": 9001,
        "name": name,
        "amount": amount,
        "period": period,
        "spent": 0.00,
        "remaining": amount,
        "status": "active",
        "created_at": "2026-08-19",
    }


@mcp.tool
def get_budget_status(budget_id: int) -> dict:
    """
    Check the current status of a budget.

    Use this tool when the user wants to see how much of a budget
    has been spent, what remains, and the utilization percentage.

    Args:
        budget_id: Unique numeric identifier of the budget.

    Returns:
        Budget status with spent, remaining, and utilization.
    """
    return {
        "budget_id": budget_id,
        "name": "Marketing Q1",
        "amount": 50000.00,
        "spent": 32000.00,
        "remaining": 18000.00,
        "utilization_percent": 64.0,
        "status": "active",
    }


@mcp.tool
def get_expenses(start_date: str, end_date: str, category: str | None = None) -> list[dict]:
    """
    Retrieve expense records for a date range, optionally filtered by category.

    Use this tool when the user wants to see itemized expenses
    for accounting or reporting purposes.

    Args:
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        category: Expense category to filter by (optional).

    Returns:
        List of expense records matching the criteria.
    """
    return [
        {
            "expense_id": 10001,
            "date": "2024-03-01",
            "category": "office_supplies",
            "description": "Printer ink and paper",
            "amount": 145.50,
            "vendor": "Office Depot",
        },
        {
            "expense_id": 10002,
            "date": "2024-03-05",
            "category": "travel",
            "description": "Client meeting travel",
            "amount": 320.00,
            "vendor": "Deutsche Bahn",
        },
    ]
