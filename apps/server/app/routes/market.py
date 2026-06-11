"""Market data, mutual fund NAV, and sentiment endpoints (Phase B).

Candles are Redis-cached: 60 s intraday during NSE market hours, 1 h for daily ranges.
Sentiment is cached 15 minutes per symbol. Market prices are never seeded or fabricated;
an unreachable provider returns a typed PROVIDER_UNAVAILABLE."""

from __future__ import annotations

import contextlib
import json

from fastapi import APIRouter, Depends, Query

from app.agents.sentiment import run_sentiment
from app.core.dependencies import current_user_id, get_container
from app.core.envelope import success
from app.india.market_hours import is_market_open
from app.infra.factory import Container
from app.providers.marketdata.base import MarketDataProvider, validate_symbol
from app.providers.mfdata.base import MfDataProvider
from app.providers.news.newsapi import NewsProvider
from app.schemas.base import Contract

router = APIRouter()

DISCLAIMER = (
    "Not investment advice. For informational purposes only. Consult a SEBI registered "
    "investment adviser before acting."
)


async def _cached(container: Container, key: str, ttl: int, producer) -> dict | list:
    try:
        cached = await container.cache.get(key)
        if cached:
            return json.loads(cached)
    except Exception:
        cached = None
    value = await producer()
    with contextlib.suppress(Exception):
        await container.cache.set(key, json.dumps(value), ex=ttl)
    return value


@router.get("/market/{symbol}/candles")
async def candles(
    symbol: str,
    range_: str = Query(default="1mo", alias="range"),
    _: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    symbol = validate_symbol(symbol)
    marketdata: MarketDataProvider = container.provider("marketdata")  # type: ignore[assignment]
    ttl = 60 if range_ in ("1d", "5d") and is_market_open() else 3600

    async def produce() -> list:
        data = await marketdata.candles(symbol, range_)
        return [c.model_dump() for c in data]

    return success(await _cached(container, f"candles:{symbol}:{range_}", ttl, produce))


@router.get("/market/{symbol}/quote")
async def quote(
    symbol: str,
    _: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    marketdata: MarketDataProvider = container.provider("marketdata")  # type: ignore[assignment]
    result = await marketdata.quote(validate_symbol(symbol))
    return success(result.model_dump())


@router.get("/mf/{scheme_code}/nav")
async def mf_nav(
    scheme_code: str,
    _: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    mfdata: MfDataProvider = container.provider("mfdata")  # type: ignore[assignment]

    async def produce() -> dict:
        nav = await mfdata.latest_nav(scheme_code)
        return nav.model_dump()

    return success(await _cached(container, f"mfnav:{scheme_code}", 3600, produce))


class SentimentRequest(Contract):
    symbol: str


@router.post("/sentiment")
async def sentiment(
    body: SentimentRequest,
    _: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    symbol = validate_symbol(body.symbol)
    news: NewsProvider = container.provider("news")  # type: ignore[assignment]

    async def produce() -> dict:
        items = await news.search(symbol.split(".")[0], limit=10)
        result = await run_sentiment(
            container.llm, symbol, items, container.settings.llm_retries
        )
        payload = result.model_dump(by_alias=True)
        payload["disclaimer"] = DISCLAIMER
        return payload

    return success(await _cached(container, f"sentiment:{symbol}", 900, produce))
