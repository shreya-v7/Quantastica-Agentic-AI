"""Incremental dirty-set planning. Cost is independent of household count."""
from datetime import date
from unittest import TestCase

from quantastica_kernel.exceptions.engine import compute_exceptions, merge_hits
from quantastica_kernel.exceptions.snapshot import BookLot, BookSnapshot, TaxFacts
from quantastica_kernel.recompute import (
    ALL_RULES,
    fields_from_event,
    plan_recompute,
)


def _book(**updates):
    book = BookSnapshot(
        household_id="hh", household_name="Test", as_of=date(2026, 9, 16),
        lots=[BookLot(
            id="l1", symbol="X", name="X", asset_class="equity", sector="IT",
            quantity=100, cost=10, price=20, acquired_on=date(2025, 10, 1),
        )],
        tax=TaxFacts(basic_salary=1_500_000, deduction_80c=50_000),
    )
    return book.model_copy(update=updates)


class RecomputeTests(TestCase):
    def test_quantity_does_not_dirty_tax_rules(self):
        plan = plan_recompute(fields_from_event(
            "book.patch", {"lot_quantities": [{"id": "l1", "quantity": 2}]}))
        self.assertEqual(plan.rules, frozenset({"lot_clock", "concentration_tripwire"}))
        self.assertNotIn("regime_watch", plan.rules)
        self.assertNotIn("deduction_headroom", plan.rules)
        self.assertIn("weights", plan.calculators)
        self.assertNotIn("compare_regimes", plan.calculators)

    def test_tax_does_not_dirty_lot_rules(self):
        plan = plan_recompute(fields_from_event("book.patch", {"tax": {"basic_salary": 1}}))
        self.assertEqual(plan.rules, frozenset({"regime_watch", "deduction_headroom"}))
        self.assertEqual(plan.calculators, frozenset({"compare_regimes"}))
        self.assertNotIn("lot_clock", plan.rules)

    def test_name_only_is_free(self):
        plan = plan_recompute(fields_from_event("book.patch", {"household_name": "N"}))
        self.assertEqual(plan.cost, 0)
        self.assertFalse(plan.rules)

    def test_snapshot_and_unknown_fail_closed(self):
        snap = plan_recompute(fields_from_event("book.snapshot", {}))
        unknown = plan_recompute(fields_from_event("book.mystery", {}))
        self.assertEqual(snap.rules, ALL_RULES)
        self.assertEqual(unknown.rules, ALL_RULES)

    def test_cost_independent_of_household_count(self):
        changed = fields_from_event(
            "book.patch", {"lot_quantities": [{"id": "l1", "quantity": 8}]})
        one = plan_recompute(changed).cost
        self.assertEqual(one, 2)
        self.assertLess(one, 5)
        # 1,000 households would cost 5,000 under full recompute; incremental stays 2.
        self.assertLess(one, 1_000 * len(ALL_RULES))
        self.assertEqual(one, plan_recompute(changed).cost)

    def test_incremental_merge_matches_full(self):
        before = _book()
        prior = compute_exceptions(before)
        lots = [before.lots[0].model_copy(update={"quantity": 400})]
        after = before.model_copy(update={"lots": lots})
        dirty = plan_recompute(fields_from_event(
            "book.patch", {"lot_quantities": [{"id": "l1", "quantity": 400}]})).rules
        merged = merge_hits(prior, compute_exceptions(after, rule_ids=dirty), dirty)
        self.assertEqual(merged, compute_exceptions(after))
        tax = after.tax.model_copy(update={"basic_salary": 4_000_000})
        taxed = after.model_copy(update={"tax": tax})
        tax_dirty = plan_recompute(fields_from_event(
            "book.patch", {"tax": tax.model_dump(mode="json")})).rules
        tax_merged = merge_hits(
            merged, compute_exceptions(taxed, rule_ids=tax_dirty), tax_dirty)
        self.assertEqual(tax_merged, compute_exceptions(taxed))
