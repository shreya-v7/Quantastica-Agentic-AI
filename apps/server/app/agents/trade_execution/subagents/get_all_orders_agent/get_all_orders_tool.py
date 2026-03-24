from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus
from ..alpaca_client import get_trading_client


def get_all_orders_for_symbol(symbol: str):
    """Retrieve all orders for a given symbol."""
    client = get_trading_client()
    req = GetOrdersRequest(status=QueryOrderStatus.ALL, symbols=[symbol])
    orders = client.get_orders(req)
    return orders
