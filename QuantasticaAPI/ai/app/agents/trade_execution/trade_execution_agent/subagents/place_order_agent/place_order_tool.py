from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, StopOrderRequest, StopLimitOrderRequest
from ..config import API_KEY, SECRET_KEY

trade_api_url = None
trade_api_wss = None
data_api_url = None
stream_data_wss = None

client = TradingClient(api_key=API_KEY, secret_key=SECRET_KEY, paper=True, url_override=trade_api_url)


def place_order(symbol: str, qty: float, side: str, order_type: str, limit_price: float =0.0, stop_price: float = 0.0):
    """
    Places an order based on the specified parameters.

    Args:
        symbol (str): The stock symbol to trade.
        qty (float): The quantity to trade.
        side (str): 'buy' or 'sell'.
        order_type (str): 'market', 'limit', 'stop', or 'stop_limit'.
        limit_price (float, optional): The limit price for limit or stop_limit orders.
        stop_price (float, optional): The stop price for stop or stop_limit orders.

    Returns:
        str: Confirmation message for the placed order.
    """
    if order_type == "market":
        req = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide(side),
            type=OrderType.MARKET,
            time_in_force=TimeInForce.DAY
        )
    elif order_type == "limit":
        req = LimitOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide(side),
            type=OrderType.LIMIT,
            time_in_force=TimeInForce.DAY,
            limit_price=limit_price
        )
    elif order_type == "stop":
        req = StopOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide(side),
            time_in_force=TimeInForce.DAY,
            stop_price=stop_price
        )
    elif order_type == "stop_limit":
        req = StopLimitOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide(side),
            time_in_force=TimeInForce.DAY,
            limit_price=limit_price,
            stop_price=stop_price
        )
    else:
        raise ValueError("Invalid order type")

    res = client.submit_order(req)
    return f"Order placed: {res.id}"