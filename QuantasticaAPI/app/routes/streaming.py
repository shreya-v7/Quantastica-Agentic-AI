"""
WebSocket route for real-time Indian stock price streaming.

Moved from app/tradingplatform/getrates.py and integrated into the main app.
"""

from fastapi import APIRouter, WebSocket
import asyncio
import yfinance as yf

router = APIRouter()


@router.websocket("/ws/stream/{symbol}")
async def stream_prices(websocket: WebSocket, symbol: str):
    """Stream real-time prices for an Indian stock (appends .NS suffix)."""
    await websocket.accept()
    try:
        while True:
            ticker = yf.Ticker(symbol + ".NS")
            data = ticker.history(period="1d", interval="1m")
            if not data.empty:
                latest = data.iloc[-1]
                price = float(latest["Close"])
                await websocket.send_json({"symbol": symbol, "price": price})
            await asyncio.sleep(2)
    except Exception:
        await websocket.close()
