from alpaca.trading.client import TradingClient
from ..config import API_KEY, SECRET_KEY
from ..get_all_orders_agent.get_all_orders_tool import get_all_orders_for_symbol

trade_api_url = None
trade_api_wss = None
data_api_url = None
stream_data_wss = None

client = TradingClient(api_key=API_KEY, secret_key=SECRET_KEY, paper=True, url_override=trade_api_url)

def cancel_order_flow(symbol: str = None, order_id: str = None, user_confirmed: bool = False):
    """
    Handles order cancellation flow with clarification and explicit confirmation.

    Args:
        symbol (str, optional): Symbol to filter orders (e.g., 'MSFT').
        order_id (str, optional): Order ID to cancel.
        user_confirmed (bool): Set to True only if user already confirmed cancellation.

    Returns:
        dict: {
            status: "awaiting_confirmation" | "multiple_orders" | "cancelled" | "no_orders" | "error" | "clarify_input",
            message: str,
            order_id: (optional) str,
            orders: (optional) list of dicts
        }
    """
    # If neither symbol nor order_id is given, clarify with the user.
    if not symbol and not order_id:
        return {
            "status": "clarify_input",
            "message": "To cancel an order, please specify either the order ID or the symbol of the order you'd like to cancel."
        }

    # If order_id is specified, attempt cancellation after confirmation
    if order_id:
        try:
            order = client.get_order_by_id(order_id)
        except Exception:
            return {
                "status": "error",
                "message": f"No order found with ID {order_id}."
            }
        if not user_confirmed:
            return {
                "status": "awaiting_confirmation",
                "message": (
                    f"You're about to cancel order {order.id}: "
                    f"{order.side.value} {order.qty} {order.symbol} ({order.type.value}), placed at {order.created_at}. Shall I proceed?"
                ),
                "order_id": order.id
            }
        # User confirmed
        client.cancel_order_by_id(order.id)
        return {
            "status": "cancelled",
            "message": f"Order {order.id} has been cancelled."
        }

    # If symbol is specified, find all open orders for that symbol
    if symbol:
        orders = get_all_orders_for_symbol(symbol)
        open_orders = [order for order in orders if order.status.value in ["new", "partially_filled", "accepted", "pending_new"]]
        if not open_orders:
            return {
                "status": "no_orders",
                "message": f"You have no open {symbol} orders to cancel."
            }
        if len(open_orders) == 1:
            order = open_orders[0]
            if not user_confirmed:
                return {
                    "status": "awaiting_confirmation",
                    "message": (
                        f"You have one open {symbol} order (ID {order.id}): "
                        f"{order.side.value} {order.qty} {order.symbol} ({order.type.value}), placed at {order.created_at}. Shall I cancel it?"
                    ),
                    "order_id": order.id
                }
            client.cancel_order_by_id(order.id)
            return {
                "status": "cancelled",
                "message": f"Order {order.id} has been cancelled."
            }
        # Multiple open orders: List and ask user to pick
        order_summaries = []
        for o in open_orders:
            summary = {
                "id": o.id,
                "side": o.side.value,
                "qty": o.qty,
                "symbol": o.symbol,
                "type": o.type.value,
                "created_at": str(o.created_at),
                "status": o.status.value
            }
            order_summaries.append(summary)
        orders_list_for_message = "\n".join(
            [f"ID: {o['id']} | {o['side']} {o['qty']} {o['symbol']} | {o['type']} | Placed: {o['created_at']} | Status: {o['status']}" for o in order_summaries]
        )
        return {
            "status": "multiple_orders",
            "message": (
                f"You have multiple open {symbol} orders:\n" +
                orders_list_for_message +
                "\nWhich one would you like to cancel? Please provide the order ID."
            ),
            "orders": order_summaries
        }