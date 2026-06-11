from typing import Literal

from pydantic import Field

from app.schemas.base import Contract
from app.schemas.common import Rating, RunStatus, Severity, StepStatus


class RiskMetric(Contract):
    id: str
    label: str
    value: float
    threshold: float
    rating: Rating
    explanation: str


class PlanStep(Contract):
    analysis: Literal["research", "risk", "insight"]
    reason: str


class Plan(Contract):
    steps: list[PlanStep] = Field(min_length=1)


class Finding(Contract):
    id: str
    portfolio_id: str
    run_id: str
    title: str
    body: str
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    metric_ids: list[str]
    created_at: str
    seed: bool = False


class AgentStep(Contract):
    name: str
    status: StepStatus
    input_summary: str
    output_summary: str
    duration_ms: float
    error: str | None = None


class AgentRun(Contract):
    id: str
    portfolio_id: str
    query: str
    status: RunStatus
    steps: list[AgentStep]
    findings: list[Finding]
    metrics: list[RiskMetric]
    answer: str | None = None
    error: str | None = None
    created_at: str
    completed_at: str | None = None


class RunRequest(Contract):
    query: str = Field(min_length=1)
    portfolio_id: str = Field(min_length=1)


class ExportResult(Contract):
    run_id: str
    location: str
    content_type: str
