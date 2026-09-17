"""Offline eval runner. Golden India cases hit calculators. FinanceBench sample checks retrieval.

This is the CI gate. LLM-as-judge and RAGAS live behind optional extras and are never
required to merge. Run: python -m app.evals
"""

from __future__ import annotations

import json
from pathlib import Path

from app.calculators.planning import AffordabilityInput, affordability, required_monthly_sip
from app.calculators.tax import TaxInput, compare_regimes

EVAL_DIR = Path(__file__).resolve().parent


def load_json(name: str) -> dict:
    return json.loads((EVAL_DIR / name).read_text(encoding="utf-8"))


def run_golden_india() -> list[dict]:
    suite = load_json("golden_india.json")
    results = []
    for case in suite["cases"]:
        got = _execute(case)
        ok, detail = _check(case, got)
        results.append({"id": case["id"], "ok": ok, "detail": detail, "got": got})
    return results


def _execute(case: dict) -> dict:
    kind = case["kind"]
    data = case["input"]
    if kind == "tax":
        result = compare_regimes(
            TaxInput(
                basic_salary=data["basicSalary"],
                hra_received=data.get("hraReceived", 0),
                rent_paid=data.get("rentPaid", 0),
                deduction_80c=data.get("deduction80c", 0),
            )
        )
        return {
            "recommended": result.recommended,
            "newRegimeTotalTax": result.new_regime.total_tax,
            "oldRegimeTotalTax": result.old_regime.total_tax,
        }
    if kind == "sip":
        sip = required_monthly_sip(data["targetInr"], data["years"], data["annualReturn"])
        return {"monthlySip": round(sip, 2)}
    if kind == "affordability":
        result = affordability(
            AffordabilityInput(
                purchase_cost=data["purchaseCost"],
                down_payment=data["downPayment"],
                loan_rate=data["loanRate"],
                loan_years=data["loanYears"],
                monthly_income=data["monthlyIncome"],
                liquid_savings=data["liquidSavings"],
            )
        )
        return {"affordable": result.affordable, "foir": result.foir}
    raise ValueError(f"unknown kind {kind}")


def _check(case: dict, got: dict) -> tuple[bool, str]:
    expect = case["expect"]
    if "recommended" in expect and got.get("recommended") != expect["recommended"]:
        return False, f"recommended {got.get('recommended')} != {expect['recommended']}"
    expected_tax = expect.get("newRegimeTotalTax")
    if expected_tax is not None and got.get("newRegimeTotalTax") != expected_tax:
        return False, f"tax {got.get('newRegimeTotalTax')} != {expected_tax}"
    if "monthlySip" in expect:
        tol = float(expect.get("tolerance", 0.5))
        if abs(float(got["monthlySip"]) - float(expect["monthlySip"])) > tol:
            return False, f"sip {got['monthlySip']} not within {tol} of {expect['monthlySip']}"
    if "affordable" in expect and got.get("affordable") is not expect["affordable"]:
        return False, f"affordable {got.get('affordable')} != {expect['affordable']}"
    return True, "ok"


def ragas_available() -> bool:
    try:
        import ragas  # noqa: F401

        return True
    except ImportError:
        return False


def main() -> int:
    results = run_golden_india()
    failed = [r for r in results if not r["ok"]]
    for row in results:
        mark = "PASS" if row["ok"] else "FAIL"
        print(f"{mark} {row['id']}: {row['detail']}")
    print(f"{len(results) - len(failed)}/{len(results)} golden cases passed")
    if ragas_available():
        print("RAGAS installed; run evals/ragas_eval.py with an LLM key for faithfulness.")
    else:
        print("RAGAS not installed; skipped (optional extra).")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
