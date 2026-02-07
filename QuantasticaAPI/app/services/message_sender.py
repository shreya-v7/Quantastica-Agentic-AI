"""
WhatsApp Trade Alert Service (Twilio).

Standalone Flask microservice for sending trade alerts via WhatsApp
and receiving confirmation replies to execute orders.

Run with: python -m app.services.message_sender
"""

from flask import Flask, request
from flask_cors import CORS
from twilio.rest import Client

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType
from alpaca.trading.requests import MarketOrderRequest

from app.config import settings

app = Flask(__name__)
CORS(app)

twilio_client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
alpaca_client = TradingClient(
    api_key=settings.alpaca_api_key,
    secret_key=settings.alpaca_secret_key,
    paper=True,
)

# Holds the most recent trade alert for confirmation flow
_pending_trade: dict = {}


@app.route('/send_alert', methods=['POST'])
def send_trade_alert():
    """Send a trade alert via WhatsApp and store the trade for confirmation."""
    data = request.json
    _pending_trade.update({
        "symbol": data["symbol"],
        "price": data["price"],
        "quantity": data["quantity"],
        "order": data["order"],
    })

    message = (
        f"Trade Alert: {data['symbol']}\n"
        f"Price: ${data['price']}\n"
        f"Quantity: {data['quantity']} shares\n"
        f"Action suggested: {data['order']}\n"
        f"Reply 'yes' to confirm execution."
    )

    twilio_client.messages.create(
        from_=settings.twilio_from_whatsapp,
        to=settings.twilio_to_whatsapp,
        body=message,
    )
    return {"status": "success", "message": "Alert sent"}, 200


@app.route("/webhook", methods=["POST"])
def receive_reply():
    """Twilio webhook -- execute the pending trade if user replies 'yes'."""
    incoming_msg = request.form.get("Body", "").strip().lower()
    sender = request.form.get("From")
    print(f"Incoming: '{incoming_msg}' from {sender}")

    if incoming_msg == "yes" and _pending_trade:
        req = MarketOrderRequest(
            symbol=_pending_trade["symbol"],
            qty=_pending_trade["quantity"],
            side=OrderSide.BUY,
            type=OrderType.MARKET,
            time_in_force=TimeInForce.DAY,
        )
        res = alpaca_client.submit_order(req)
        print(f"Order placed: {res.id}")

    return {}, 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
