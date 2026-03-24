"""Pydantic API models — mirror `packages/types` (camelCase JSON)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        ser_json_by_alias=True,
    )


class FinancialSummary(CamelModel):
    net_worth: float = Field(..., description="From insight engine only")
    risk_exposure: float = Field(..., description="e.g. position count; server-defined")
    debt_load: float


class ChartPoint(CamelModel):
    name: str
    value: float


class FeatureFlags(CamelModel):
    cloud: Literal["aws", "azure", "gcp"]
    ai: bool
    insights: bool


class DemoFlags(CamelModel):
    enabled: bool


class ConfigResponse(CamelModel):
    version: str
    flags: FeatureFlags
    demo: DemoFlags


class DashboardPayload(CamelModel):
    version: str
    summary: FinancialSummary
    cash: float
    investments_total: float
    debt_total: float
    chart: list[ChartPoint]
    insight_summary: str
    show_refinance_cta: bool = Field(
        ...,
        description="Product rule evaluated server-side; UI must not re-derive.",
    )


class SummarySyncResponse(CamelModel):
    user_id: str
    summary: FinancialSummary


class InsightsGetResponse(CamelModel):
    user_id: str
    insights: FinancialSummary


class AskResponse(CamelModel):
    user_id: str
    answer: str


class InsightHighlight(CamelModel):
    id: str
    severity: Literal["info", "watch", "action"]
    title: str
    body: str
    action_label: str | None = None


class InsightHighlightsResponse(CamelModel):
    version: str
    highlights: list[InsightHighlight]
