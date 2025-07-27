from flask import Flask, request
from twilio.rest import Client
from flask_cors import CORS
from twilio.twiml.messaging_response import MessagingResponse
import requests
import os

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, StopOrderRequest, StopLimitOrderRequest
from alpaca.trading.enums import OrderSide
trade_api_url = None
trade_api_wss = None
data_api_url = None
stream_data_wss = None
API_KEY = "PKZOVU9ALX3TVHPNVTMM"
SECRET_KEY = "0dCfYkvq4iuba3DUmeVian5bKLvZm13POrmslUYC"
alpaca_client = TradingClient(api_key=API_KEY, secret_key=SECRET_KEY, paper=True, url_override=trade_api_url)


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

    res = alpaca_client.submit_order(req)
    return f"Order placed: {res.id}"

app = Flask(__name__)
CORS(app)

# Use environment variables for security (recommended)
TWILIO_ACCOUNT_SID = 'AC085fe07b1be21eb42fe86dd1b82d75b4'
TWILIO_AUTH_TOKEN = 'a31e7368c28eefc27f697d46a162daa6'
FROM_WHATSAPP = 'whatsapp:+14155238886'
TO_WHATSAPP = 'whatsapp:+918451920618'

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Global dictionary to keep the last trade sent
last_trade = {}

@app.route('/send_alert', methods=['POST'])
def send_trade_alert():
    data = request.json
    last_trade['symbol'] = data['symbol']
    last_trade['price'] = data['price']
    last_trade['quantity'] = data['quantity']
    last_trade['order'] = data['order']
    message = f"""
📢 *Trade Alert: {data['symbol']}*
Price: ${data['price']}
Quantity: {data['quantity']} shares
Action suggested: {data['order']}
Reply *yes* to confirm execution.
"""

    client.messages.create(
        from_=FROM_WHATSAPP,
        to=TO_WHATSAPP,
        body=message
    )
    return {"status": "success", "message": "Alert sent successfully"}, 200

@app.route("/webhook", methods=["POST"])
def receive_reply():
    incoming_msg = request.form.get("Body")         # User's message text
    sender = request.form.get("From")               # WhatsApp number that sent it
    recipient = request.form.get("To")              # Your Twilio number
    message_sid = request.form.get("MessageSid")    # Unique ID for message

    print(f"Incoming message: {incoming_msg} from {sender}")

    if incoming_msg == 'yes':
        # Simulate API call or trade execution
        # place_order(
        #     "symbol": last_trade['symbol'],
        #     "qty": last_trade['quantity'],
        #     "side": last_trade['order'],
        #     "order_type": "market",
        # )
        place_order(symbol=last_trade['symbol'], qty=last_trade['quantity'], side=OrderSide.BUY.value, order_type="market")
    return {}, 200

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000, debug=True)