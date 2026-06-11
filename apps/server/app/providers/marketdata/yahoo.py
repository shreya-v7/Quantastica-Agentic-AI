"""Yahoo Finance chart API provider, the free default for NSE/BSE quotes and candles.

Upstox or Zerodha Kite market feed can be swapped in behind the same interface as the
upgrade path. Symbols carry their exchange suffix (.NS/.BO) end to end.
"""

from __future__ import annotations

from datetime import UTC, datetime

import httpx

from app.core.errors import ProviderUnavailableError, ValidationError
from app.providers.marketdata.base import (
    VALID_RANGES,
    Candle,
    MarketDataProvider,
    Quote,
    validate_symbol,
)

_BASE = "https://query1.finance.yahoo.com/v8/finance/chart"
_INTERVALS = {"1d": "5m", "5d": "15m", "1mo": "1d", "6mo": "1d", "1y": "1d", "5y": "1wk"}
_HEADERS = {"User-Agent": "Mozilla/5.0 (Quantastica)"}


class YahooMarketData(MarketDataProvider):
    def __init__(self, timeout_seconds: float = 10.0):
        self._timeout = timeout_seconds

    async def _chart(self, symbol: str, range_: str, interval: str) -> dict:
        url = f"{_BASE}/{symbol}"
        params = {"range": range_, "interval": interval}
        try:
            async with httpx.AsyncClient(timeout=self._timeout, headers=_HEADERS) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPError as exc:
            raise ProviderUnavailableError("marketdata", str(exc)) from exc

        chart = payload.get("chart", {})
        if chart.get("error"):
            raise ProviderUnavailableError("marketdata", str(chart["error"]))
        results = chart.get("result") or []
        if not results:
            raise ProviderUnavailableError("marketdata", f"No data for {symbol}")
        return results[0]

    async def quote(self, symbol: str) -> Quote:
        symbol = validate_symbol(symbol)
        result = await self._chart(symbol, "1d", "5m")
        meta = result["meta"]
        price = meta.get("regularMarketPrice")
        if price is None:
            raise ProviderUnavailableError("marketdata", f"No live price for {symbol}")
        ts = meta.get("regularMarketTime")
        timestamp = (
            datetime.fromtimestamp(ts, tz=UTC).isoformat()
            if ts
            else datetime.now(UTC).isoformat()
        )
        return Quote(
            symbol=symbol,
            price=float(price),
            currency=meta.get("currency", "INR"),
            timestamp=timestamp,
        )

    async def candles(self, symbol: str, range_: str) -> list[Candle]:
        symbol = validate_symbol(symbol)
        if range_ not in VALID_RANGES:
            raise ValidationError(
                f"range must be one of {', '.join(VALID_RANGES)}, got '{range_}'"
            )
        result = await self._chart(symbol, range_, _INTERVALS[range_])
        timestamps = result.get("timestamp") or []
        quote = (result.get("indicators", {}).get("quote") or [{}])[0]
        candles: list[Candle] = []
        for i, ts in enumerate(timestamps):
            values = {
                key: (quote.get(key) or [None])[i] if i < len(quote.get(key) or []) else None
                for key in ("open", "high", "low", "close", "volume")
            }
            if values["close"] is None:
                continue
            candles.append(
                Candle(
                    timestamp=datetime.fromtimestamp(ts, tz=UTC).isoformat(),
                    open=float(values["open"] or values["close"]),
                    high=float(values["high"] or values["close"]),
                    low=float(values["low"] or values["close"]),
                    close=float(values["close"]),
                    volume=int(values["volume"] or 0),
                )
            )
        return candles
