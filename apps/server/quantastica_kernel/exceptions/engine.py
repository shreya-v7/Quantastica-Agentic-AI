from __future__ import annotations

from quantastica_kernel.exceptions.hits import ExceptionHit, PolicyTable
from quantastica_kernel.exceptions.rules import RULES
from quantastica_kernel.exceptions.snapshot import BookSnapshot


def _sort_hits(hits: list[ExceptionHit]) -> list[ExceptionHit]:
    hits.sort(key=lambda h: (-h.rupee_delta, h.due_date.isoformat() if h.due_date else "9999"))
    return hits


def compute_exceptions(
    book: BookSnapshot,
    policy: PolicyTable | None = None,
    *,
    rule_ids: frozenset[str] | None = None,
) -> list[ExceptionHit]:
    table = policy or PolicyTable()
    known = {rule.__name__ for rule in RULES}
    if rule_ids is not None:
        unknown = set(rule_ids) - known
        if unknown:
            raise ValueError(f"Unknown rules: {sorted(unknown)}")
        selected = tuple(rule for rule in RULES if rule.__name__ in rule_ids)
    else:
        selected = RULES
    hits: list[ExceptionHit] = []
    for rule in selected:
        hits.extend(rule(book, table))
    return _sort_hits(hits)


def merge_hits(
    prior: list[ExceptionHit],
    current: list[ExceptionHit],
    dirty: frozenset[str],
) -> list[ExceptionHit]:
    kept = [hit for hit in prior if hit.rule_id not in dirty]
    return _sort_hits(kept + list(current))


def diff_exceptions(
    prior: list[ExceptionHit], current: list[ExceptionHit]
) -> dict[str, list[str]]:
    before = {hit.fingerprint: hit for hit in prior}
    after = {hit.fingerprint: hit for hit in current}
    added = [fp for fp in after if fp not in before]
    removed = [fp for fp in before if fp not in after]
    changed = [
        fp
        for fp in after
        if fp in before and before[fp].rupee_delta != after[fp].rupee_delta
    ]
    return {"added": added, "removed": removed, "changed": changed}
