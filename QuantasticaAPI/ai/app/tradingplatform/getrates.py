from fastapi import FastAPI, WebSocket
import asyncio
import yfinance as yf

app = FastAPI()

@app.websocket("/ws/stream/{symbol}")
async def stream_prices(websocket: WebSocket, symbol: str):
    await websocket.accept()
    while True:
        ticker = yf.Ticker(symbol + ".NS")
        data = ticker.history(period="1d", interval="1m")
        if not data.empty:
            latest = data.iloc[-1]
            price = latest["Close"]
            await websocket.send_json({"symbol": symbol, "price": price})
        await asyncio.sleep(2)
