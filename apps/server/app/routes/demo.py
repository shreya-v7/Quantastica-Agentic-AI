"""Demo payloads  - all metrics from server-side snapshot + insight engine (no UI math)."""

from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException

from app.contracts.models import (
    ChartPoint,
    DashboardPayload,
    FinancialSummary,
    InsightHighlight,
    InsightHighlightsResponse,
)
from app.contracts.version import CONTRACT_VERSION
from app.financial_intelligence.core.insight import generate_insights
from app.financial_intelligence.core.types import FinancialSnapshot, Investment, Liability

router = APIRouter(prefix="/demo", tags=["Demo"])


def _env_demo_enabled() -> bool:
    return os.getenv("FI_DEMO", "true").lower() in ("1", "true", "yes", "on")


def _demo_snapshot() -> FinancialSnapshot:
    return FinancialSnapshot(
        user_id="demo",
        balance=28_400.0,
        investments=[
            Investment(symbol="VTI", value=60_000.0),
            Investment(symbol="VXUS", value=52_200.0),
        ],
        liabilities=[
            Liability(type="loan", amount=16_280.0, rate=5.5),
        ],
    )


@router.get("/dashboard", response_model=DashboardPayload)
def demo_dashboard() -> DashboardPayload:
    if not _env_demo_enabled():
        raise HTTPException(status_code=404, detail="Demo mode disabled")

    snap = _demo_snapshot()
    raw = generate_insights(snap)
    summary = FinancialSummary(
        net_worth=raw["net_worth"],
        risk_exposure=float(raw["risk_exposure"]),
        debt_load=raw["debt_load"],
    )
    inv_total = sum(i.value for i in snap.investments)
    debt_total = sum(li.amount for li in snap.liabilities)

    chart = [
        ChartPoint(name="Jan", value=98_000.0),
        ChartPoint(name="Feb", value=101_200.0),
        ChartPoint(name="Mar", value=105_400.0),
        ChartPoint(name="Apr", value=108_900.0),
        ChartPoint(name="May", value=115_100.0),
        ChartPoint(name="Jun", value=118_600.0),
        ChartPoint(name="Jul", value=raw["net_worth"]),
    ]

    insight_summary = (
        "Debt is moderate relative to assets; diversification across holdings reduces single-name risk."
    )

    show_refinance_cta = debt_total > 12_000.0

    return DashboardPayload(
        version=CONTRACT_VERSION,
        summary=summary,
        cash=snap.balance,
        investments_total=inv_total,
        debt_total=debt_total,
        chart=chart,
        insight_summary=insight_summary,
        show_refinance_cta=show_refinance_cta,
    )


@router.get("/insight-highlights", response_model=InsightHighlightsResponse)
def demo_insight_highlights() -> InsightHighlightsResponse:
    if not _env_demo_enabled():
        raise HTTPException(status_code=404, detail="Demo mode disabled")
    return InsightHighlightsResponse(
        version=CONTRACT_VERSION,
        highlights=[
            InsightHighlight(
                id="1",
                severity="watch",
                title="Debt load vs. income",
                body=(
                    "Your liabilities are elevated relative to typical benchmarks for your net worth tier. "
                    "Consider accelerating payoff on the highest-rate line first."
                ),
                action_label="View payoff plan",
            ),
            InsightHighlight(
                id="2",
                severity="info",
                title="Concentration",
                body=(
                    "Technology exposure represents a meaningful share of investable assets. "
                    "Rebalancing could reduce volatility without sacrificing long-term growth."
                ),
            ),
            InsightHighlight(
                id="3",
                severity="action",
                title="Cash buffer",
                body=(
                    "Liquid reserves cover roughly 4 months of estimated spend  - within a healthy range."
                ),
                action_label="Adjust target",
            ),
        ],
    )
