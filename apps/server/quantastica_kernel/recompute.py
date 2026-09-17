"""Rule and calculator dependency graph for incremental recompute.

A book event dirties only the nodes whose declared reads overlap the changed
fields. Other households are never in the dirty set. Cost is the number of
dirty exception rules, independent of book size.
"""
from __future__ import annotations

from dataclasses import dataclass

from .exceptions.rules import RULES

RULE_READS: dict[str, frozenset[str]] = {
    "regime_watch": frozenset({"tax", "policy.regime_saving_threshold"}),
    "lot_clock": frozenset({"lots", "as_of", "policy.lot_clock_days"}),
    "concentration_tripwire": frozenset({"lots", "policy.name_cap", "policy.sector_cap"}),
    "deduction_headroom": frozenset({"tax", "policy.deduction_unused_threshold"}),
    "ais_mismatch": frozenset({"ais"}),
}

CALCULATOR_READS: dict[str, frozenset[str]] = {
    "compare_regimes": frozenset({"tax"}),
    "compute_equity_gains": frozenset({"lots", "as_of"}),
    "weights": frozenset({"lots"}),
    "sip": frozenset({"plan.sip"}),
    "step_up_sip": frozenset({"plan.sip"}),
    "emi": frozenset({"plan.emi"}),
    "affordability": frozenset({"plan.affordability"}),
    "monte_carlo": frozenset({"plan.sip"}),
}

DOWNSTREAM: dict[str, tuple[str, ...]] = {
    "compare_regimes": ("regime_watch", "deduction_headroom"),
    "compute_equity_gains": ("lot_clock",),
    "weights": ("concentration_tripwire",),
}

ALL_BOOK_FIELDS = frozenset({"tax", "as_of", "household_name", "lots", "ais"})
ALL_RULES = frozenset(rule.__name__ for rule in RULES)
NODE_READS = {**RULE_READS, **CALCULATOR_READS}


def _overlaps(changed: frozenset[str], reads: frozenset[str]) -> bool:
    for field in changed:
        for read in reads:
            if field == read or field.startswith(read + ".") or read.startswith(field + "."):
                return True
    return False


def fields_from_event(event_type: str, payload: dict) -> frozenset[str]:
    """Map a stored book event to book field names. Unknown events fail closed."""
    if event_type != "book.patch":
        return ALL_BOOK_FIELDS
    fields: set[str] = set()
    if "tax" in payload:
        fields.add("tax")
    if "as_of" in payload:
        fields.add("as_of")
    if "household_name" in payload:
        fields.add("household_name")
    if payload.get("lot_quantities") or payload.get("lots_upsert") or payload.get("lots_remove"):
        fields.add("lots")
    if payload.get("ais") is not None:
        fields.add("ais")
    return frozenset(fields) if fields else ALL_BOOK_FIELDS


def dirty_nodes(changed: frozenset[str]) -> frozenset[str]:
    nodes = {name for name, reads in NODE_READS.items() if _overlaps(changed, reads)}
    growing = True
    while growing:
        growing = False
        for source, destinations in DOWNSTREAM.items():
            if source not in nodes:
                continue
            for dest in destinations:
                if dest not in nodes:
                    nodes.add(dest)
                    growing = True
    return frozenset(nodes)


def dirty_rules(changed: frozenset[str]) -> frozenset[str]:
    return frozenset(name for name in dirty_nodes(changed) if name in RULE_READS)


@dataclass(frozen=True)
class RecomputePlan:
    changed_fields: frozenset[str]
    rules: frozenset[str]
    calculators: frozenset[str]

    @property
    def cost(self) -> int:
        """Exception-rule invocations. Independent of household count."""
        return len(self.rules)


def plan_recompute(changed: frozenset[str]) -> RecomputePlan:
    nodes = dirty_nodes(changed)
    return RecomputePlan(
        changed_fields=changed,
        rules=frozenset(name for name in nodes if name in RULE_READS),
        calculators=frozenset(name for name in nodes if name in CALCULATOR_READS),
    )
