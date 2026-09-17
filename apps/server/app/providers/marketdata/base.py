"""Market data provider interface for Indian equities and indices.

Symbols are exchange-qualified everywhere: RELIANCE.NS, TCS.BO, or an index symbol
like ^NSEI. Bare symbols are rejected at this boundary.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod

from pydantic import BaseModel

from app.core.errors import ValidationError

_SYMBOL_RE = re.compile(r"^([A-Z0-9&\-]{1,20}\.(NS|BO)|\^[A-Z0-9]{1,12})$")

VALID_RANGES = ("1d", "5d", "1mo", "6mo", "1y", "5y")


def validate_symbol(symbol: str) -> str:
    candidate = symbol.strip().upper()
    if not _SYMBOL_RE.match(candidate):
        raise ValidationError(
            f"Symbol '{symbol}' must be exchange qualified (.NS or .BO), "
            "for example RELIANCE.NS or TCS.BO."
        )
    return candidate


class Quote(BaseModel):
    symbol: str
    price: float
    currency: str
    timestamp: str
    previous_close: float | None = None


class Candle(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class MarketDataProvider(ABC):
    @abstractmethod
    async def quote(self, symbol: str) -> Quote: ...

    @abstractmethod
    async def candles(self, symbol: str, range_: str) -> list[Candle]: ...
