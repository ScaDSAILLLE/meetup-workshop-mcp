"""Simulierte Kundenwerkzeuge für Suche, Stammdaten und Kommunikation."""

from mcp_server.server import mcp


@mcp.tool
def search_customers(query: str) -> list[dict]:
    """
    Search the customer database by name, email, or company.

    Use this tool when the user wants to find one or more customers
    based on a search term. Returns matching customer records.

    Args:
        query: Search term used to find matching customers.

    Returns:
        List of matching customer records.
    """
    return [
        {
            "id": 42,
            "name": "Max Mustermann",
            "email": "max@example.com",
            "company": "Example GmbH",
            "status": "active",
        }
    ]


@mcp.tool
def get_customer(customer_id: int) -> dict:
    """
    Retrieve detailed information about a specific customer.

    Use this tool when the user knows the customer ID and wants
    full profile information including contact details and status.

    Args:
        customer_id: Unique numeric identifier of the customer.

    Returns:
        Complete customer record.
    """
    return {
        "id": customer_id,
        "name": "Max Mustermann",
        "email": "max@example.com",
        "phone": "+49 341 1234567",
        "company": "Example GmbH",
        "address": "Augustusplatz 10, 04109 Leipzig",
        "status": "active",
        "created_at": "2023-01-15",
    }


@mcp.tool
def create_customer(name: str, email: str, company: str) -> dict:
    """
    Create a new customer record in the database.

    Use this tool when the user wants to register a new customer.
    All fields are required.

    Args:
        name: Full name of the customer.
        email: Email address of the customer.
        company: Company name of the customer.

    Returns:
        The created customer record with assigned ID.
    """
    return {
        "id": 100,
        "name": name,
        "email": email,
        "company": company,
        "status": "active",
        "created_at": "2026-08-19",
    }


@mcp.tool
def update_customer(customer_id: int, name: str | None = None, email: str | None = None) -> dict:
    """
    Update an existing customer's information.

    Use this tool when the user wants to modify customer details.
    Only provided fields will be updated.

    Args:
        customer_id: Unique numeric identifier of the customer.
        name: New name for the customer (optional).
        email: New email address (optional).

    Returns:
        The updated customer record.
    """
    return {
        "id": customer_id,
        "name": name or "Max Mustermann",
        "email": email or "max@example.com",
        "status": "updated",
    }


@mcp.tool
def delete_customer(customer_id: int) -> dict:
    """
    Delete a customer record from the database.

    Use this tool when the user wants to remove a customer.
    This action is irreversible.

    Args:
        customer_id: Unique numeric identifier of the customer.

    Returns:
        Confirmation of deletion.
    """
    return {
        "id": customer_id,
        "status": "deleted",
        "message": f"Customer {customer_id} has been deleted.",
    }


@mcp.tool
def get_customer_orders(customer_id: int) -> list[dict]:
    """
    Retrieve all orders associated with a specific customer.

    Use this tool when the user wants to see the order history
    for a particular customer.

    Args:
        customer_id: Unique numeric identifier of the customer.

    Returns:
        List of order records for the customer.
    """
    return [
        {
            "order_id": 1001,
            "customer_id": customer_id,
            "total": 299.99,
            "status": "delivered",
            "date": "2024-03-15",
        },
        {
            "order_id": 1002,
            "customer_id": customer_id,
            "total": 49.99,
            "status": "shipped",
            "date": "2024-06-22",
        },
    ]


@mcp.tool
def get_customer_invoices(customer_id: int) -> list[dict]:
    """
    Retrieve all invoices associated with a specific customer.

    Use this tool when the user wants to see billing information
    or invoice history for a particular customer.

    Args:
        customer_id: Unique numeric identifier of the customer.

    Returns:
        List of invoice records for the customer.
    """
    return [
        {
            "invoice_id": 2001,
            "customer_id": customer_id,
            "amount": 299.99,
            "status": "paid",
            "date": "2024-03-15",
        }
    ]


@mcp.tool
def create_support_ticket(
    customer_id: int,
    title: str,
    description: str,
    priority: str = "normal",
) -> dict:
    """
    Create a new customer support ticket.

    Use this tool when a user wants to report an issue, request
    assistance, or create a support case for a customer.

    Args:
        customer_id: Customer associated with the ticket.
        title: Short title of the problem.
        description: Detailed description of the issue.
        priority: Ticket priority such as low, normal, or high.

    Returns:
        The created support ticket with assigned ID.
    """
    return {
        "ticket_id": 5001,
        "customer_id": customer_id,
        "title": title,
        "description": description,
        "priority": priority,
        "status": "open",
        "created_at": "2026-08-19",
    }


@mcp.tool
def get_customer_history(customer_id: int) -> dict:
    """
    Retrieve the complete interaction history for a customer.

    Use this tool when the user wants to see all past interactions,
    including orders, support tickets, and communications.

    Args:
        customer_id: Unique numeric identifier of the customer.

    Returns:
        Customer history with orders, tickets, and communications.
    """
    return {
        "customer_id": customer_id,
        "total_orders": 2,
        "total_tickets": 1,
        "last_interaction": "2024-06-22",
        "lifetime_value": 349.98,
    }


@mcp.tool
def get_customer_statistics(customer_id: int) -> dict:
    """
    Retrieve statistical summaries for a specific customer.

    Use this tool when the user wants analytics data such as
    total spending, average order value, or purchase frequency.

    Args:
        customer_id: Unique numeric identifier of the customer.

    Returns:
        Statistical summary for the customer.
    """
    return {
        "customer_id": customer_id,
        "total_spent": 349.98,
        "average_order_value": 174.99,
        "order_frequency_days": 99,
        "customer_segment": "regular",
    }


@mcp.tool
def merge_customers(primary_id: int, secondary_id: int) -> dict:
    """
    Merge two customer records into one.

    Use this tool when the user wants to combine duplicate customer
    accounts. All data from the secondary customer is transferred
    to the primary customer.

    Args:
        primary_id: Customer ID to keep (the primary account).
        secondary_id: Customer ID to merge and deactivate.

    Returns:
        Confirmation of the merge operation.
    """
    return {
        "primary_id": primary_id,
        "secondary_id": secondary_id,
        "status": "merged",
        "message": f"Customer {secondary_id} merged into {primary_id}.",
    }


@mcp.tool
def get_customer_communications(customer_id: int) -> list[dict]:
    """
    Retrieve all communications (emails, calls, notes) for a customer.

    Use this tool when the user wants to see the communication
    history or contact log for a particular customer.

    Args:
        customer_id: Unique numeric identifier of the customer.

    Returns:
        List of communication records.
    """
    return [
        {
            "communication_id": 7001,
            "customer_id": customer_id,
            "type": "email",
            "subject": "Order confirmation",
            "date": "2024-03-15",
        },
        {
            "communication_id": 7002,
            "customer_id": customer_id,
            "type": "call",
            "subject": "Support follow-up",
            "date": "2024-03-20",
        },
    ]
