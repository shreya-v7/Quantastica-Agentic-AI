"""Lazy Alpaca TradingClient - avoid import-time failure when paper keys are unset (local dev)."""

from functools import lru_cache

from alpaca.trading.client import TradingClient

from .config import API_KEY, SECRET_KEY


def alpaca_configured() -> bool:
    k = (API_KEY or "").strip()
    s = (SECRET_KEY or "").strip()
    return bool(k and s)


@lru_cache(maxsize=1)
def get_trading_client() -> TradingClient:
    if not alpaca_configured():
        raise RuntimeError(
            "Alpaca is not configured. Set ALPACA_API_KEY and ALPACA_SECRET_KEY in apps/server/.env "
            "(paper trading keys from https://alpaca.markets)."
        )
    return TradingClient(api_key=API_KEY, secret_key=SECRET_KEY, paper=True)
