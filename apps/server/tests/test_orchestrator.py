from app.agents.orchestrator import Orchestrator
from app.infra.events.inprocess import InProcessEventPublisher
from app.infra.repo.base import SeedBundle
from app.schemas.common import RunStatus, StepStatus
from app.schemas.entities import Portfolio

from tests.conftest import make_settings  # noqa: F401  (fixtures come from conftest)
from tests.fakes import FakeLLM

USER = "usr_seed_arjun"


async def test_happy_path_completes_with_grounded_findings(container):
    repo = container.repository
    llm = FakeLLM()
    events = InProcessEventPublisher()
    orch = Orchestrator(repo, llm, events, retries=1)

    portfolio = await repo.get_portfolio(USER, "pf_tech_heavy")
    run = await orch.run(
        USER,
        portfolio,
        await repo.holdings_for(USER, "pf_tech_heavy"),
        await repo.transactions_for(USER, "pf_tech_heavy"),
        "How concentrated is my AI portfolio?",
    )

    assert run.status == RunStatus.completed
    assert [s.name for s in run.steps] == [
        "planner",
        "researcher",
        "risk",
        "insight",
        "summarizer",
    ]
    assert all(s.status == StepStatus.completed for s in run.steps)
    assert len(run.metrics) == 5
    assert run.findings
    # bogus metric id must be filtered out; only real metric ids remain
    assert run.findings[0].metric_ids == ["hhi", "top5_weight"]
    assert run.answer

    persisted = await repo.list_insights(USER, portfolio_id="pf_tech_heavy")
    assert len(persisted) == len(run.findings)

    event_types = [e["type"] for e in events.events]
    assert event_types[0] == "run.started"
    assert event_types[-1] == "run.completed"


async def test_planner_invalid_json_retries_then_fails(container):
    repo = container.repository
    llm = FakeLLM(invalid_plan=True)
    orch = Orchestrator(repo, llm, InProcessEventPublisher(), retries=1)

    portfolio = await repo.get_portfolio(USER, "pf_tech_heavy")
    run = await orch.run(
        USER, portfolio, await repo.holdings_for(USER, "pf_tech_heavy"), [], "q"
    )

    assert run.status == RunStatus.failed
    assert run.steps[0].name == "planner"
    assert run.steps[0].status == StepStatus.failed
    assert "planner" in run.error
    # initial attempt plus exactly one retry
    plan_calls = [c for c in llm.calls if c["schema"] and "steps" in c["schema"]["properties"]]
    assert len(plan_calls) == 2


async def test_mid_pipeline_failure_marks_run_failed(container):
    repo = container.repository
    empty = Portfolio(
        id="pf_empty", name="Empty", base_currency="INR", created_at="2024-01-01", seed=True
    )
    await repo.load_seed(
        SeedBundle(
            users=[{
                "id": "usr_empty", "email": "empty@example.in", "role": "user",
                "phone": None, "phoneVerified": False,
                "createdAt": "2024-01-01T00:00:00+05:30", "seed": True,
            }],
            portfolios=[empty],
            holdings=[],
            transactions=[],
            owner_by_portfolio={"pf_empty": "usr_empty"},
        )
    )
    orch = Orchestrator(repo, FakeLLM(), InProcessEventPublisher(), retries=1)

    portfolio = await repo.get_portfolio("usr_empty", "pf_empty")
    run = await orch.run("usr_empty", portfolio, [], [], "q")

    assert run.status == RunStatus.failed
    assert run.steps[0].name == "planner"
    assert run.steps[0].status == StepStatus.completed
    assert run.steps[1].name == "researcher"
    assert run.steps[1].status == StepStatus.failed
    assert "researcher" in run.error
