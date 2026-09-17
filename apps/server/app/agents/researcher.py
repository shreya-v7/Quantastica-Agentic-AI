"""Researcher agent: pure code, no LLM.

Computes total value, per-holding weights, sector and asset class allocation, top
positions, and cost basis vs current value from repository data.
"""

from __future__ import annotations

from collections import defaultdict

from app.agents.base import PipelineContext
from app.schemas.entities import (
    AllocationSlice,
    Holding,
    PortfolioMetrics,
    PositionMetric,
)

TOP_N = 5


def _position(holding: Holding, total_value: float) -> PositionMetric:
    value = holding.quantity * holding.current_price
    cost = holding.quantity * holding.cost_basis
    gain = value - cost
    gain_pct = (gain / cost) if cost else 0.0
    weight = (value / total_value) if total_value else 0.0
    return PositionMetric(
        symbol=holding.symbol,
        name=holding.name,
        value=round(value, 2),
        weight=round(weight, 6),
        cost_basis=round(cost, 2),
        unrealized_gain=round(gain, 2),
        unrealized_gain_pct=round(gain_pct, 6),
    )


def _allocation(holdings: list[Holding], key, total_value: float) -> list[AllocationSlice]:
    grouped: dict[str, float] = defaultdict(float)
    for h in holdings:
        grouped[key(h)] += h.quantity * h.current_price
    slices = [
        AllocationSlice(
            key=name,
            value=round(value, 2),
            weight=round((value / total_value) if total_value else 0.0, 6),
        )
        for name, value in grouped.items()
    ]
    return sorted(slices, key=lambda s: s.value, reverse=True)


def compute_metrics(portfolio_id: str, holdings: list[Holding]) -> PortfolioMetrics:
    total_value = sum(h.quantity * h.current_price for h in holdings)
    total_cost = sum(h.quantity * h.cost_basis for h in holdings)
    positions = [_position(h, total_value) for h in holdings]
    positions.sort(key=lambda p: p.value, reverse=True)
    gain = total_value - total_cost
    return PortfolioMetrics(
        portfolio_id=portfolio_id,
        total_value=round(total_value, 2),
        total_cost_basis=round(total_cost, 2),
        unrealized_gain=round(gain, 2),
        unrealized_gain_pct=round((gain / total_cost) if total_cost else 0.0, 6),
        positions=positions,
        sector_allocation=_allocation(holdings, lambda h: h.sector, total_value),
        asset_class_allocation=_allocation(
            holdings, lambda h: h.asset_class.value, total_value
        ),
        top_positions=positions[:TOP_N],
    )


class ResearcherAgent:
    name = "researcher"

    def input_summary(self, ctx: PipelineContext) -> str:
        return f"{len(ctx.holdings)} holdings, {len(ctx.transactions)} transactions"

    async def run(self, ctx: PipelineContext) -> str:
        if not ctx.holdings:
            raise ValueError("Portfolio has no holdings to analyze")
        ctx.metrics = compute_metrics(ctx.portfolio.id, ctx.holdings)
        return (
            f"total value {ctx.metrics.total_value}, "
            f"{len(ctx.metrics.positions)} positions, "
            f"{len(ctx.metrics.sector_allocation)} sectors"
        )
