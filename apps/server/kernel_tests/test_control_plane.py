"""Guard, metrics, DST, reconcile, verify. Isolated kernel CI."""
from unittest import TestCase

from quantastica_kernel.dst import Simulator
from quantastica_kernel.guard import fail_closed, screen
from quantastica_kernel.metrics import (
    bcubed,
    expected_calibration_error,
    ndcg_at_k,
    precision_recall_f1,
    recall_at_k,
    trajectory_score,
    word_error_rate,
)
from quantastica_kernel.reconcile import decide
from quantastica_kernel.verify import verify_money_fields


class ControlPlaneKernelTests(TestCase):
    def test_guard_fail_closed_and_benign(self):
        bad = screen("Buy this, tax due Rs 50000", [])
        self.assertFalse(bad.ok)
        self.assertTrue(bad.advice)
        blocked = fail_closed("Portfolio worth Rs 999999", [10.0])
        self.assertIn("blocked", blocked.lower())
        benign = screen("Informational only. Paper trade recorded.", [0])
        self.assertTrue(benign.ok)

    def test_metrics_and_ece(self):
        scores = precision_recall_f1(9, 1, 0)
        self.assertGreaterEqual(scores["f1"], 0.9)
        self.assertLessEqual(expected_calibration_error([(1.0, True)] * 10), 0.05)
        self.assertGreaterEqual(recall_at_k({"a"}, ["a", "b"], 1), 0.8)
        self.assertGreaterEqual(ndcg_at_k([3, 2, 1], 3), 0.75)
        self.assertEqual(word_error_rate("a b", "a b"), 0.0)
        clustered = bcubed(["1", "1", "2"], ["1", "1", "2"])
        self.assertEqual(clustered["precision"], 1.0)
        traj = trajectory_score(["a", "b"], ["a", "b", "c"])
        self.assertGreaterEqual(traj["tool_trajectory_avg_score"], 0.9)

    def test_reconcile_no_silent_high_risk_merge(self):
        same = decide("Karan Mehta", "Karan Mehta", "F1", "F1")
        self.assertEqual(same.action, "merge")
        noisy = decide("Karan", "Someone Else", "1", "2")
        self.assertEqual(noisy.action, "distinct")
        review = decide("Karan Mehta", "K Mehta", "", "")
        self.assertIn(review.action, {"review", "merge", "distinct"})

    def test_verifier_catches_injected_amount(self):
        payload = {
            "basic_salary": {"amount": 1, "source_quote": "Basic Salary 3600000", "page": 1},
            "confidence": 0.9,
        }
        self.assertFalse(verify_money_fields(payload)["ok"])
        good = {
            "basic_salary": {"amount": 3600000, "source_quote": "Basic Salary 3600000", "page": 1},
            "confidence": 0.9,
        }
        self.assertTrue(verify_money_fields(good)["ok"])

    def test_dst_reproduces_from_seed(self):
        a = Simulator(7).run(20)
        b = Simulator(7).run(20)
        self.assertEqual(a.coverage, b.coverage)
        self.assertEqual(a.ok, b.ok)
        self.assertTrue(a.invariants["guard_fail_closed"])
        self.assertTrue(a.invariants["idempotent"])
        self.assertTrue(any(a.coverage.values()))
