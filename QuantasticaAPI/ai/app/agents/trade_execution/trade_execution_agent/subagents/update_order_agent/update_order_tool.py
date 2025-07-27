from alpaca.trading.client import TradingClient

from ..config import API_KEY, SECRET_KEY
from ..get_all_orders_agent.get_all_orders_tool import get_all_orders_for_symbol
from ..place_order_agent.place_order_tool import place_order

trade_api_url = None
trade_api_wss = None
data_api_url = None
stream_data_wss = None

client = TradingClient(api_key=API_KEY, secret_key=SECRET_KEY, paper=True, url_override=trade_api_url)


def update_order(symbol: str, new_qty: float, new_price: float = 0.0, order_type:str="market"):
    """
    Updates an existing open order.

    Args:
        symbol (str): The stock symbol of the order to update.
        new_qty (float): The new quantity for the order.
        new_price (float, optional): The new price for limit or stop_limit orders.
        order_type (str): The type of order ('market', 'limit', etc.). Default is 'market'.

    Returns:
        str: Confirmation message for the updated order.
    """
    orders = get_all_orders_for_symbol(symbol=symbol)
    #orders = client.get_orders(req)
    updated = False
    for order in orders:
        if order.symbol == symbol:
            updated = False
            client.cancel_order_by_id(order.id)
            place_order(
                symbol=symbol,
                qty=new_qty,
                side=order.side.value,
                order_type=order_type,
                limit_price=new_price if order_type in ["limit", "stop_limit"] else 0.0,
                stop_price=new_price if order_type in ["stop", "stop_limit"] else 0.0
            )
            updated = True
    if updated:
        return f"✅ Order for {symbol.upper()} has been updated to quantity {new_qty} successfully."
    else:
        return f"⚠️ No open order found for {symbol.upper()} to update."