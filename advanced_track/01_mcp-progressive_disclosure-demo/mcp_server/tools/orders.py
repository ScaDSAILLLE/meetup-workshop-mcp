"""Simulierte Bestellwerkzeuge von Anlage bis Statushistorie."""

from mcp_server.server import mcp


@mcp.tool
def create_order(customer_id: int, items: list[dict]) -> dict:
    """
    Create a new order for a customer.

    Use this tool when the user wants to place a new order.
    Each item in the list should have product_id, quantity, and price.

    Args:
        customer_id: ID of the customer placing the order.
        items: List of order items, each with product_id, quantity, and price.

    Returns:
        The created order with order ID and total.
    """
    total = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)
    return {
        "order_id": 3001,
        "customer_id": customer_id,
        "items": items,
        "total": total,
        "status": "pending",
        "created_at": "2026-08-19",
    }


@mcp.tool
def get_order(order_id: int) -> dict:
    """
    Retrieve detailed information about a specific order.

    Use this tool when the user knows the order ID and wants
    full order details including items, total, and status.

    Args:
        order_id: Unique numeric identifier of the order.

    Returns:
        Complete order record.
    """
    return {
        "order_id": order_id,
        "customer_id": 42,
        "items": [
            {"product_id": "P100", "name": "Widget", "quantity": 2, "price": 29.99},
        ],
        "total": 59.98,
        "status": "delivered",
        "created_at": "2024-03-15",
        "shipped_at": "2024-03-17",
        "delivered_at": "2024-03-19",
    }


@mcp.tool
def list_orders(status: str | None = None, limit: int = 20) -> list[dict]:
    """
    List orders with optional status filtering.

    Use this tool when the user wants to see multiple orders,
    optionally filtered by status (pending, shipped, delivered, cancelled).

    Args:
        status: Filter orders by status (optional).
        limit: Maximum number of orders to return (default 20).

    Returns:
        List of order records matching the filter.
    """
    return [
        {
            "order_id": 3001,
            "customer_id": 42,
            "total": 59.98,
            "status": "delivered",
            "date": "2024-03-15",
        }
    ]


@mcp.tool
def cancel_order(order_id: int, reason: str = "customer_request") -> dict:
    """
    Cancel an existing order.

    Use this tool when the user wants to cancel an order.
    A reason must be provided for audit purposes.

    Args:
        order_id: Unique numeric identifier of the order to cancel.
        reason: Cancellation reason (default: customer_request).

    Returns:
        Confirmation of order cancellation.
    """
    return {
        "order_id": order_id,
        "status": "cancelled",
        "reason": reason,
        "cancelled_at": "2026-08-19",
    }


@mcp.tool
def update_order(order_id: int, items: list[dict] | None = None, status: str | None = None) -> dict:
    """
    Update an existing order's items or status.

    Use this tool when the user wants to modify an order,
    such as changing quantities, adding/removing items, or updating status.

    Args:
        order_id: Unique numeric identifier of the order.
        items: Updated list of order items (optional).
        status: New order status (optional).

    Returns:
        The updated order record.
    """
    return {
        "order_id": order_id,
        "status": status or "updated",
        "items": items or [],
        "updated_at": "2026-08-19",
    }


@mcp.tool
def get_order_status(order_id: int) -> dict:
    """
    Get the current status of an order.

    Use this tool when the user wants a quick status check
    without needing full order details.

    Args:
        order_id: Unique numeric identifier of the order.

    Returns:
        Order ID and current status.
    """
    return {
        "order_id": order_id,
        "status": "delivered",
        "last_updated": "2024-03-19",
    }


@mcp.tool
def get_order_tracking(order_id: int) -> dict:
    """
    Get tracking information for an order.

    Use this tool when the user wants to track a shipment,
    including carrier, tracking number, and estimated delivery.

    Args:
        order_id: Unique numeric identifier of the order.

    Returns:
        Tracking information for the order.
    """
    return {
        "order_id": order_id,
        "carrier": "DHL",
        "tracking_number": "JD123456789",
        "status": "in_transit",
        "estimated_delivery": "2024-03-19",
        "current_location": "Leipzig Distribution Center",
    }


@mcp.tool
def add_order_item(order_id: int, product_id: str, quantity: int, price: float) -> dict:
    """
    Add a new item to an existing order.

    Use this tool when the user wants to add a product
    to an order that has already been created.

    Args:
        order_id: Unique numeric identifier of the order.
        product_id: Product identifier to add.
        quantity: Quantity of the product to add.
        price: Unit price of the product.

    Returns:
        Updated order with the new item added.
    """
    return {
        "order_id": order_id,
        "status": "updated",
        "new_item": {
            "product_id": product_id,
            "quantity": quantity,
            "price": price,
        },
        "message": "Item added to order.",
    }


@mcp.tool
def remove_order_item(order_id: int, product_id: str) -> dict:
    """
    Remove an item from an existing order.

    Use this tool when the user wants to remove a product
    from an order that has already been created.

    Args:
        order_id: Unique numeric identifier of the order.
        product_id: Product identifier to remove.

    Returns:
        Updated order with the item removed.
    """
    return {
        "order_id": order_id,
        "status": "updated",
        "removed_product_id": product_id,
        "message": "Item removed from order.",
    }


@mcp.tool
def get_order_invoice(order_id: int) -> dict:
    """
    Get the invoice associated with an order.

    Use this tool when the user wants billing information
    for a specific order, including invoice number and payment status.

    Args:
        order_id: Unique numeric identifier of the order.

    Returns:
        Invoice information for the order.
    """
    return {
        "order_id": order_id,
        "invoice_id": 2001,
        "amount": 59.98,
        "tax": 11.40,
        "total": 71.38,
        "payment_status": "paid",
        "invoice_date": "2024-03-15",
    }


@mcp.tool
def ship_order(order_id: int, carrier: str = "DHL", address: str | None = None) -> dict:
    """
    Ship an order to the customer.

    Use this tool when the user wants to mark an order as shipped
    and generate tracking information.

    Args:
        order_id: Unique numeric identifier of the order to ship.
        carrier: Shipping carrier (default: DHL).
        address: Shipping address (optional, uses customer default if not provided).

    Returns:
        Shipping confirmation with tracking details.
    """
    return {
        "order_id": order_id,
        "status": "shipped",
        "carrier": carrier,
        "tracking_number": "JD123456789",
        "shipped_at": "2026-08-19",
    }


@mcp.tool
def get_order_history(order_id: int) -> list[dict]:
    """
    Get the complete status history for an order.

    Use this tool when the user wants to see all status changes
    and timestamps for a particular order.

    Args:
        order_id: Unique numeric identifier of the order.

    Returns:
        List of status change records with timestamps.
    """
    return [
        {"order_id": order_id, "status": "created", "timestamp": "2024-03-15T10:00:00Z"},
        {"order_id": order_id, "status": "paid", "timestamp": "2024-03-15T10:05:00Z"},
        {"order_id": order_id, "status": "shipped", "timestamp": "2024-03-17T08:00:00Z"},
        {"order_id": order_id, "status": "delivered", "timestamp": "2024-03-19T14:00:00Z"},
    ]
