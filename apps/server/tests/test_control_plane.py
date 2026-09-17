"""Phases 3-13 local shims: bus, team, gateway, SLO, OLAP, FDE, catalog."""
import pytest
from app.bus import Envelope, LocalBus
from app.core.errors import RateLimitedError
from app.fde import health, layout_for
from app.gateway import FailoverLLM, TokenMeter
from app.olap import aggregate, export_events
from app.slo import alert
from app.speech.provider import MockSpeech, timed_speak
from app.team import QuantasticaTeam
from evals.catalog import run_catalog

from tests.fakes import FakeLLM


async def test_bus_exactly_once_and_dlq_and_order():
    bus = LocalBus(max_redeliveries=1)
    seen: list[str] = []

    async def ok(env: Envelope) -> None:
        seen.append(env.event_id)

    await bus.publish_ordered(Envelope("e1", "hh_a", "household.recompute", {"n": 1}))
    await bus.publish_ordered(Envelope("e2", "hh_a", "household.recompute", {"n": 2}))
    await bus.publish_ordered(Envelope("e3", "hh_b", "household.recompute", {"n": 3}))
    await bus.drain("recompute", ok)
    await bus.drain("recompute", ok)
    assert seen == ["e1", "e2", "e3"]

    async def boom(env: Envelope) -> None:
        raise RuntimeError("fail")

    bus2 = LocalBus(max_redeliveries=0)
    await bus2.publish_ordered(Envelope("bad", "hh_a", "x", {}))
    await bus2.drain("recompute", boom)
    assert bus2.dlq_depth() == 1


def test_team_trajectory_and_verifier():
    team = QuantasticaTeam()
    state = team.run({
        "route": "ingest",
        "kind": "form16",
        "answer": "Basic salary is Rs 3600000",
        "allowed_amounts": [3_600_000],
        "source_quotes": ["Basic Salary 3600000"],
    })
    assert "orchestrator" in state["trace"]
    assert "guard" in state["trace"]
    assert state["verify"]["ok"] is True
    poisoned = team.run({
        "route": "ingest",
        "kind": "form16",
        "vlm_override": {
            "kind": "form16",
            "employer": "X",
            "pan_masked": "ABCDE****F",
            "basic_salary": {"amount": 1, "source_quote": "Basic Salary 3600000", "page": 1},
            "confidence": 0.9,
        },
        "answer": "Rs 1",
        "allowed_amounts": [3_600_000],
    })
    assert poisoned["verify"]["ok"] is False
    assert poisoned.get("needs_review") is True


def test_catalog_meets_pilot_gates():
    report = run_catalog()
    assert report["gates"]["goldenRupee"] is True
    assert report["metrics"]["extractionF1"] >= 0.9
    assert report["metrics"]["verifierCatch"] >= 0.95
    assert report["metrics"]["ece"] <= 0.05
    assert report["metrics"]["guardUngroundedFn"] == 0.0
    assert report["metrics"]["replayDeterminism"] == 1.0
    assert report["metrics"]["asrNumberAccuracy"] == 1.0
    assert report["metrics"]["trajectory"] >= 0.9
    assert report["metrics"]["adviceDetection"] == 1.0


async def test_gateway_failover_and_rate_limit():
    class Boom(FakeLLM):
        async def complete(self, system, user, json_schema=None):
            raise RuntimeError("primary down")

    meter = TokenMeter()
    gw = FailoverLLM(Boom(), FakeLLM(), meter, tenant="t1", limit=3)
    text = await gw.complete("sys", "hello")
    assert isinstance(text, str)
    assert meter.failovers == 1
    assert meter.spans[0]["attributes"]["gen_ai.system"]
    with pytest.raises(RateLimitedError):
        await gw.complete("sys", "a")
        await gw.complete("sys", "b")
        await gw.complete("sys", "c")


def test_slo_page_on_synthetic_incident():
    fired = alert(0.02, 0.03)
    assert fired is not None
    assert fired.severity == "page"


def test_olap_and_fde_and_voice_budget(tmp_path):
    path = export_events([{"household_id": "hh_mehta", "seq": 1}], tmp_path)
    assert path.exists()
    stats = aggregate([{"household_id": "hh_mehta"}, {"household_id": "hh_rao"}])
    assert stats["households"] == 2
    pack = layout_for("Northstar Labs Pvt Ltd")
    assert "basic_salary" in pack["fields"]
    view = health(1.0, 10, 1000, 10, 0.0, 1.0)
    assert view["score"] >= 0.8
    timed = timed_speak(MockSpeech(), "hello")
    assert timed["ttfa_ms"] <= 1500
    assert timed["e2e_ms"] <= 1500


async def test_control_http_evals_dashboards_trust_and_dsr(client):
    evals = await client.get("/api/control/evals")
    assert evals.status_code == 200
    assert evals.json()["data"]["gates"]["goldenRupee"] is True
    dash = await client.get("/api/control/dashboards")
    assert dash.status_code == 200
    assert dash.json()["data"]["aiQuality"]["goldenRupee"] == 1.0
    trust = await client.get("/api/control/trust")
    assert trust.json()["data"]["cmek"] is False
    access = await client.post("/api/control/dsr/access", json={"household_id": "hh_mehta"})
    assert access.status_code == 200
    erased = await client.post("/api/control/dsr/erasure", json={"household_id": "hh_mehta"})
    assert erased.status_code == 403
    incident = await client.get("/api/control/slo/synthetic-incident")
    assert incident.json()["data"]["expected"] == "page"
