"""Risk agent: pure code, deterministic, unit tested.

Computes the Herfindahl-Hirschman concentration index, top-5 weight share, sector
concentration, a diversification score, and a simple volatility proxy from transaction
history. Each metric returns value, threshold, and a low/medium/high rating.
"""

from __future__ import annotations

from collections import defaultdict

from app.agents.base import PipelineContext
from app.schemas.agents import RiskMetric
from app.schemas.common import Rating
from app.schemas.entities import PortfolioMetrics, Transaction


def _band(value: float, low: float, high: float, higher_is_worse: bool) -> Rating:
    if higher_is_worse:
        if value < low:
            return Rating.low
        if value < high:
            return Rating.medium
        return Rating.high
    if value >= high:
        return Rating.low
    if value >= low:
        return Rating.medium
    return Rating.high


def herfindahl_index(weights: list[float]) -> float:
    return sum(w * w for w in weights)


def top_n_share(weights: list[float], n: int) -> float:
    return sum(sorted(weights, reverse=True)[:n])


def _stdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    return variance**0.5


def _symbol_returns(transactions: list[Transaction]) -> dict[str, list[float]]:
    by_symbol: dict[str, list[Transaction]] = defaultdict(list)
    for tx in transactions:
        by_symbol[tx.symbol].append(tx)
    returns: dict[str, list[float]] = {}
    for symbol, txs in by_symbol.items():
        prices = [t.price for t in sorted(txs, key=lambda t: t.timestamp)]
        rets = [
            prices[i] / prices[i - 1] - 1.0
            for i in range(1, len(prices))
            if prices[i - 1]
        ]
        if rets:
            returns[symbol] = rets
    return returns


def volatility_proxy(
    metrics: PortfolioMetrics, transactions: list[Transaction]
) -> float:
    weight_by_symbol = {p.symbol: p.weight for p in metrics.positions}
    returns = _symbol_returns(transactions)
    return sum(weight_by_symbol.get(sym, 0.0) * _stdev(rets) for sym, rets in returns.items())


def compute_risk_metrics(
    metrics: PortfolioMetrics, transactions: list[Transaction]
) -> list[RiskMetric]:
    weights = [p.weight for p in metrics.positions]
    hhi = herfindahl_index(weights)
    top5 = top_n_share(weights, 5)
    sector_max = max((s.weight for s in metrics.sector_allocation), default=0.0)
    diversification = 1.0 - hhi
    volatility = volatility_proxy(metrics, transactions)

    return [
        RiskMetric(
            id="hhi",
            label="Herfindahl-Hirschman concentration index",
            value=round(hhi, 6),
            threshold=0.25,
            rating=_band(hhi, 0.15, 0.25, higher_is_worse=True),
            explanation="Sum of squared position weights. Higher means more concentrated.",
        ),
        RiskMetric(
            id="top5_weight",
            label="Top 5 position weight share",
            value=round(top5, 6),
            threshold=0.70,
            rating=_band(top5, 0.50, 0.70, higher_is_worse=True),
            explanation="Share of portfolio value held in the five largest positions.",
        ),
        RiskMetric(
            id="sector_concentration",
            label="Largest sector weight",
            value=round(sector_max, 6),
            threshold=0.50,
            rating=_band(sector_max, 0.30, 0.50, higher_is_worse=True),
            explanation="Weight of the single most heavily weighted sector.",
        ),
        RiskMetric(
            id="diversification",
            label="Diversification score",
            value=round(diversification, 6),
            threshold=0.60,
            rating=_band(diversification, 0.60, 0.80, higher_is_worse=False),
            explanation="One minus HHI. Higher means better diversified (lower risk).",
        ),
        RiskMetric(
            id="volatility",
            label="Transaction volatility proxy",
            value=round(volatility, 6),
            threshold=0.20,
            rating=_band(volatility, 0.10, 0.20, higher_is_worse=True),
            explanation="Weighted standard deviation of price moves between transactions.",
        ),
    ]


class RiskAgent:
    name = "risk"

    def input_summary(self, ctx: PipelineContext) -> str:
        positions = len(ctx.metrics.positions) if ctx.metrics else 0
        return f"{positions} positions, {len(ctx.transactions)} transactions"

    async def run(self, ctx: PipelineContext) -> str:
        if ctx.metrics is None:
            raise ValueError("Risk agent requires researcher metrics")
        ctx.risk_metrics = compute_risk_metrics(ctx.metrics, ctx.transactions)
        ratings = {m.id: m.rating.value for m in ctx.risk_metrics}
        return f"computed {len(ctx.risk_metrics)} risk metrics: {ratings}"
