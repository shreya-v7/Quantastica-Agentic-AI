from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus
from ..config import API_KEY, SECRET_KEY

client = TradingClient(api_key=API_KEY, secret_key=SECRET_KEY, paper=True)


def get_all_orders_for_symbol(symbol: str):
    """Retrieve all orders for a given symbol."""
    req = GetOrdersRequest(status=QueryOrderStatus.ALL, symbols=[symbol])
    orders = client.get_orders(req)
    return orders
