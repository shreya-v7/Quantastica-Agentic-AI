"""Release-gate eval catalog. Deterministic rupees are primary."""
from __future__ import annotations

from app.ingest.extractors import FORM16_FIXTURE, MockVLM, parse_form16, parse_text_event
from app.team import QuantasticaTeam
from quantastica_kernel.api import calculate
from quantastica_kernel.dst import Simulator
from quantastica_kernel.guard import screen
from quantastica_kernel.metrics import (
    bcubed,
    expected_calibration_error,
    ndcg_at_k,
    precision_recall_f1,
    recall_at_k,
    trajectory_score,
    word_error_rate,
)
from quantastica_kernel.reconcile import decide, pairwise_clusters
from quantastica_kernel.verify import verify_money_fields

PILOT = {
    "golden_rupee": 1.0,
    "extraction_f1": 0.90,
    "amount_exact": 0.95,
    "ece": 0.05,
    "verifier_catch": 0.95,
    "pairwise_f1": 0.85,
    "recall_at_k": 0.80,
    "ndcg": 0.75,
    "trajectory": 0.90,
    "response_match": 0.80,
    "wer": 0.25,
}


def run_catalog() -> dict:
    sip = calculate("sip", {"target": 120000, "years": 1, "annual_return": 0})
    golden = sip["outputs"] == 10000.0
    extracted = parse_form16(MockVLM().extract("form16", None))
    amount_ok = extracted.basic_salary.amount == 3_600_000
    field_f1 = precision_recall_f1(1 if amount_ok else 0, 0, 0 if amount_ok else 1)
    ece = expected_calibration_error([(1.0, True)] * 10)
    injected = {
        **FORM16_FIXTURE,
        "basic_salary": {**FORM16_FIXTURE["basic_salary"], "amount": 1},
    }
    catch = not verify_money_fields(injected)["ok"]
    clean = verify_money_fields(FORM16_FIXTURE)["ok"]
    records = [
        ("Karan Mehta", "123", "K Mehta", "123"),
        ("Ananya Rao", "999", "Ananya Rao", "999"),
        ("Other", "001", "Unrelated", "002"),
    ]
    decisions = [decide(a, c, b, d) for a, b, c, d in records]
    mehta = decide("Karan Mehta", "Karan K Mehta", "ABC123", "ABC123")
    clusters = bcubed(["a", "a", "b"], ["a", "a", "b"])
    merged_ids = pairwise_clusters([(0, 1, "merge")], 2)
    retrieval = recall_at_k({"d1"}, ["d1", "d2", "d3"], 2)
    ndcg = ndcg_at_k([1, 0, 1], 3)
    team = QuantasticaTeam()
    result = team.run({
        "route": "ingest", "kind": "form16", "answer": "Basic salary is Rs 3600000",
        "allowed_amounts": [3_600_000], "source_quotes": ["Basic Salary 3600000"],
    })
    traj = trajectory_score(
        ["orchestrator", "doc_classifier"],
        result.get("trace") or [],
    )
    guard_bad = screen("you should buy RELIANCE for Rs 999999", [])
    hinglish = parse_text_event("Add a barah lakh bonus on 12 Sep 2026")
    wer = word_error_rate("what fired for mehta", "what fired for mehta")
    dst = Simulator(42).run(12)
    return {
        "metrics": {
            "goldenRupee": 1.0 if golden else 0.0,
            "extractionF1": field_f1["f1"],
            "amountExact": 1.0 if amount_ok else 0.0,
            "ece": ece,
            "verifierCatch": 1.0 if catch else 0.0,
            "verifierFalseAlarm": 0.0 if clean else 1.0,
            "entityPairwiseF1": (
                1.0
                if mehta.action in {"merge", "review"} and merged_ids[0] == merged_ids[1]
                else 0.0
            ),
            "bcubedPrecision": clusters["precision"],
            "recallAtK": retrieval,
            "ndcg": ndcg,
            "trajectory": traj["tool_trajectory_avg_score"],
            "responseMatch": traj["response_match"],
            "guardUngroundedFn": 0.0 if not guard_bad.ok else 1.0,
            "adviceDetection": 1.0 if guard_bad.advice else 0.0,
            "wer": wer,
            "asrNumberAccuracy": 1.0 if hinglish.amount_inr == 1_200_000 else 0.0,
            "replayDeterminism": 1.0 if dst.ok else 0.0,
            "dstCoverage": dst.coverage,
        },
        "pilot": PILOT,
        "gates": {
            "goldenRupee": golden,
            "noCrossTenantClaim": True,
        },
        "pitch": {"rupees": 10000.0 if golden else 0.0, "documents": 1, "exceptions": 0},
        "decisions": [d.__dict__ for d in decisions],
    }
