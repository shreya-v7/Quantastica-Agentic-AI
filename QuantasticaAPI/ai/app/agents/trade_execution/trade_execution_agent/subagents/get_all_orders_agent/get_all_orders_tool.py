from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus
from ..config import API_KEY, SECRET_KEY

trade_api_url = None
trade_api_wss = None
data_api_url = None
stream_data_wss = None

client = TradingClient(api_key=API_KEY, secret_key=SECRET_KEY, paper=True, url_override=trade_api_url)


def get_all_orders_for_symbol(symbol: str):
    req = GetOrdersRequest(status=QueryOrderStatus.ALL,symbols=[symbol])
    orders = client.get_orders(req)
    for order in orders:
        print(order)
    return orders
