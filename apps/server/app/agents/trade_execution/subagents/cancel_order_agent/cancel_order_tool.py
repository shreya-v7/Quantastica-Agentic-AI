from ..alpaca_client import get_trading_client
from ..get_all_orders_agent.get_all_orders_tool import get_all_orders_for_symbol


def cancel_order_flow(symbol: str = None, order_id: str = None, user_confirmed: bool = False):
    """
    Handles order cancellation flow with clarification and explicit confirmation.

    Args:
        symbol: Symbol to filter orders (e.g., 'MSFT').
        order_id: Order ID to cancel.
        user_confirmed: Set to True only if user already confirmed cancellation.

    Returns:
        Dict with status, message, and optional order details.
    """
    try:
        client = get_trading_client()
    except RuntimeError as e:
        return {"status": "error", "message": str(e)}

    if not symbol and not order_id:
        return {
            "status": "clarify_input",
            "message": "To cancel an order, please specify either the order ID or the symbol.",
        }

    if order_id:
        try:
            order = client.get_order_by_id(order_id)
        except Exception:
            return {"status": "error", "message": f"No order found with ID {order_id}."}

        if not user_confirmed:
            return {
                "status": "awaiting_confirmation",
                "message": (
                    f"You are about to cancel order {order.id}: "
                    f"{order.side.value} {order.qty} {order.symbol} ({order.type.value}), "
                    f"placed at {order.created_at}. Shall I proceed?"
                ),
                "order_id": order.id,
            }
        client.cancel_order_by_id(order.id)
        return {"status": "cancelled", "message": f"Order {order.id} has been cancelled."}

    if symbol:
        orders = get_all_orders_for_symbol(symbol)
        open_orders = [
            o for o in orders
            if o.status.value in ["new", "partially_filled", "accepted", "pending_new"]
        ]

        if not open_orders:
            return {"status": "no_orders", "message": f"You have no open {symbol} orders to cancel."}

        if len(open_orders) == 1:
            order = open_orders[0]
            if not user_confirmed:
                return {
                    "status": "awaiting_confirmation",
                    "message": (
                        f"You have one open {symbol} order (ID {order.id}): "
                        f"{order.side.value} {order.qty} {order.symbol} ({order.type.value}), "
                        f"placed at {order.created_at}. Shall I cancel it?"
                    ),
                    "order_id": order.id,
                }
            client.cancel_order_by_id(order.id)
            return {"status": "cancelled", "message": f"Order {order.id} has been cancelled."}

        # Multiple open orders
        summaries = []
        for o in open_orders:
            summaries.append({
                "id": o.id, "side": o.side.value, "qty": o.qty,
                "symbol": o.symbol, "type": o.type.value,
                "created_at": str(o.created_at), "status": o.status.value,
            })
        listing = "\n".join(
            f"  ID: {s['id']} | {s['side']} {s['qty']} {s['symbol']} | {s['type']} | {s['created_at']}"
            for s in summaries
        )
        return {
            "status": "multiple_orders",
            "message": f"You have multiple open {symbol} orders:\n{listing}\nWhich one would you like to cancel? Provide the order ID.",
            "orders": summaries,
        }
