"""Exact independent vectors, compatibility and replay integrity checks."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

from quantastica_kernel.api import calculate, canonical, replay
from quantastica_kernel.calculators.planning import monte_carlo_sip


class KernelTests(unittest.TestCase):
    def test_exact_golden_rupees(self):
        # Hand-computable zero-rate/zero-volatility vectors, to the paisa.
        cases = [
            ("sip", {"target": 120000, "years": 1, "annual_return": 0}, 10000.0),
            ("emi", {"principal": 120000, "years": 1, "annual_rate": 0}, 10000.0),
            ("step_up_sip", {"target": 252000, "years": 2, "annual_return": 0,
                             "annual_step_up": 0.1}, 10000.0),
        ]
        for kind, inputs, expected in cases:
            with self.subTest(kind=kind):
                receipt = calculate(kind, inputs)
                self.assertEqual(receipt["outputs"], expected)
                self.assertEqual(replay(receipt), receipt)
        tax = calculate("tax", {"basic_salary": 1500000})["outputs"]
        self.assertEqual(tax["new_regime"]["total_tax"], 130000.0)
        self.assertEqual(tax["old_regime"]["total_tax"], 257400.0)
        self.assertEqual(tax["saving_inr"], 127400.0)
        mc = calculate("monte_carlo", {"monthly_sip": 1000, "years": 1,
                       "annual_return": 0, "annual_volatility": 0, "paths": 10})
        self.assertEqual(mc["outputs"]["p50"], 12000.0)
        cg = calculate("capital_gains", {"lots": [{"quantity": 1000, "buy_price": 50,
                       "sell_price": 400, "buy_date": "2016-01-01",
                       "sell_date": "2025-06-01", "fmv_2018_01_31": 200}]})
        self.assertEqual(cg["outputs"]["ltcg"], 200000.0)
        self.assertEqual(cg["outputs"]["total_tax"], 9375.0)

    def test_receipts_reject_tampering_and_unknown_versions(self):
        receipt = calculate("sip", {"target": 120000, "years": 1, "annual_return": 0})
        for field, value in [("outputs", 1), ("version", "future"), ("content_hash", "x")]:
            changed = copy.deepcopy(receipt)
            changed[field] = value
            with self.assertRaises(ValueError):
                replay(changed)
        with self.assertRaises(ValueError):
            calculate("sip", {"target": float("nan"), "years": 1, "annual_return": 0})

    def test_defaults_and_random_state(self):
        args = {"monthly_sip": 1000, "years": 1, "annual_return": .12, "annual_volatility": .18}
        self.assertEqual(monte_carlo_sip(**args), monte_carlo_sip(**args))
        with self.assertRaises(ValueError):
            monte_carlo_sip(**args, rng_seed=None)
        r = calculate("monte_carlo", args)
        self.assertEqual(r["inputs"]["rng_seed"], 0)
        self.assertEqual(replay(r), r)

    def test_fresh_process_replay(self):
        code = ('from quantastica_kernel.api import calculate,canonical;'
                'print(canonical(calculate("monte_carlo",dict(monthly_sip=1000,years=1,'
                'annual_return=.12,annual_volatility=.18,paths=10,rng_seed=42))))')
        a = subprocess.check_output([sys.executable, "-c", code])
        b = subprocess.check_output([sys.executable, "-c", code])
        self.assertEqual(a, b)
        self.assertEqual(canonical(replay(json.loads(a))), a.decode().strip())

    def test_no_application_imports(self):
        import ast
        root = Path(__file__).resolve().parents[1] / "quantastica_kernel"
        for path in root.rglob("*.py"):
            if any(part in {"build", "__pycache__"} or part.endswith(".egg-info")
                   for part in path.parts):
                continue
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node, ast.ImportFrom):
                    self.assertFalse((node.module or "").startswith("app."), str(path))
                if isinstance(node, ast.Import):
                    self.assertFalse(any(n.name.startswith("app.") for n in node.names))

    def test_affordability_exact_vector(self):
        result = calculate("affordability", {
            "purchase_cost": 120000, "down_payment": 120000, "loan_rate": .1,
            "loan_years": 1, "monthly_income": 10000, "existing_emi": 1000,
            "liquid_savings": 180000, "monthly_expenses": 4000,
        })
        self.assertEqual(result["outputs"], {
            "new_emi": 0.0, "total_emi": 1000.0, "foir": .1, "foir_band_ok": True,
            "cash_buffer_after_purchase": 60000.0, "emergency_fund_months": 12.0,
            "affordable": True,
        })
        self.assertEqual(replay(result), result)

    def test_rule_golden_vectors(self):
        receipt = calculate("exceptions", {"book": {
            "household_id": "golden", "household_name": "Golden", "as_of": "2026-09-16",
            "lots": [{"id": "one", "symbol": "TEST", "name": "Synthetic",
                      "asset_class": "equity", "sector": "Test", "quantity": 100,
                      "cost": 100, "price": 200, "acquired_on": "2025-10-01"}],
            "tax": {"basic_salary": 1200000, "hra_received": 400000,
                    "rent_paid": 360000, "deduction_80c": 50000,
                    "home_loan_interest": 200000},
        }})
        hits = receipt["outputs"]
        concentration = [h["rupee_delta"] for h in hits
                         if h["rule_id"] == "concentration_tripwire"]
        self.assertEqual(concentration, [17000.0, 12000.0])
        self.assertEqual(next(h["rupee_delta"] for h in hits
                              if h["rule_id"] == "lot_clock"), 2000.0)
        self.assertEqual(next(h["rupee_delta"] for h in hits
                              if h["rule_id"] == "deduction_headroom"), 150000.0)
        self.assertTrue(any(h["rule_id"] == "regime_watch" for h in hits))
        self.assertFalse(any(h["rule_id"] == "ais_mismatch" for h in hits))
        self.assertEqual(replay(receipt), receipt)
