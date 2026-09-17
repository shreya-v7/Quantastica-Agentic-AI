from __future__ import annotations

from quantastica_kernel.exceptions.hits import ExceptionHit, PolicyTable
from quantastica_kernel.exceptions.rules import RULES
from quantastica_kernel.exceptions.snapshot import BookSnapshot


def compute_exceptions(
    book: BookSnapshot, policy: PolicyTable | None = None
) -> list[ExceptionHit]:
    table = policy or PolicyTable()
    hits: list[ExceptionHit] = []
    for rule in RULES:
        hits.extend(rule(book, table))
    hits.sort(key=lambda h: (-h.rupee_delta, h.due_date.isoformat() if h.due_date else "9999"))
    return hits


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
