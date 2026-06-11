"""Shared pipeline context and agent protocol."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.infra.llm.base import LLMClient
from app.schemas.agents import Finding, Plan, RiskMetric
from app.schemas.entities import Holding, PortfolioMetrics, Transaction
from app.schemas.entities import Portfolio as PortfolioModel


@dataclass
class PipelineContext:
    run_id: str
    query: str
    portfolio: PortfolioModel
    holdings: list[Holding]
    transactions: list[Transaction]
    llm: LLMClient
    plan: Plan | None = None
    metrics: PortfolioMetrics | None = None
    risk_metrics: list[RiskMetric] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    answer: str | None = None
