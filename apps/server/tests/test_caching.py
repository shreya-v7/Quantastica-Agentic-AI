"""Phase K caching tests: ETag 304 round-trips and deterministic LLM response cache."""

from __future__ import annotations

import respx
from app.infra.llm.cache import CachingLLM
from httpx import Response

_YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart"


def _chart_series() -> dict:
    return {
        "chart": {
            "result": [
                {
                    "meta": {"regularMarketPrice": 2500.0, "currency": "INR"},
                    "timestamp": [1718000000, 1718086400],
                    "indicators": {"quote": [{"open": [2400, 2450], "high": [2500, 2520],
                                              "low": [2390, 2440], "close": [2480, 2500],
                                              "volume": [1000, 1200]}]},
                }
            ],
            "error": None,
        }
    }


async def test_portfolio_etag_returns_304(client):
    first = await client.get("/api/portfolios")
    pid = first.json()["data"][0]["id"]

    res = await client.get(f"/api/portfolios/{pid}")
    assert res.status_code == 200
    etag = res.headers["etag"]
    assert etag

    again = await client.get(f"/api/portfolios/{pid}", headers={"If-None-Match": etag})
    assert again.status_code == 304
    assert again.content == b""


@respx.mock
async def test_candle_etag_returns_304(client):
    respx.get(url__startswith=_YAHOO).mock(return_value=Response(200, json=_chart_series()))
    res = await client.get("/api/market/RELIANCE.NS/candles?range=1mo")
    assert res.status_code == 200
    etag = res.headers["etag"]
    again = await client.get(
        "/api/market/RELIANCE.NS/candles?range=1mo", headers={"If-None-Match": etag}
    )
    assert again.status_code == 304


class _CountingLLM:
    def __init__(self):
        self.calls = 0

    async def complete(self, system, user, json_schema=None):
        self.calls += 1
        return {"value": 42}


async def test_llm_cache_hits_on_repeat(container):
    inner = _CountingLLM()
    cached = CachingLLM(inner, container.cache)
    schema = {"type": "object", "properties": {"value": {"type": "integer"}}}

    a = await cached.complete("sys", "user", schema)
    b = await cached.complete("sys", "user", schema)
    assert a == b == {"value": 42}
    assert inner.calls == 1  # second call served from cache


async def test_llm_cache_skips_freeform(container):
    inner = _CountingLLM()
    cached = CachingLLM(inner, container.cache)
    await cached.complete("sys", "user", None)
    await cached.complete("sys", "user", None)
    assert inner.calls == 2  # no schema => never cached
