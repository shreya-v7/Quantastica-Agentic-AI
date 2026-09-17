"""Deterministic identity and holdings matching. The scorer, not the model, decides."""
from __future__ import annotations

import re
from dataclasses import dataclass

_HONOR = re.compile(r"\b(mr|mrs|ms|shri|smt|dr)\b\.?", re.I)
_SPACE = re.compile(r"\s+")
_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def normalize_name(value: str) -> str:
    text = _HONOR.sub(" ", (value or "").lower())
    text = text.replace("kumar", "k")
    return _SPACE.sub(" ", text).strip()


def normalize_folio(value: str) -> str:
    return _NON_ALNUM.sub("", (value or "").lower())


def _tokens(value: str) -> set[str]:
    return {token for token in normalize_name(value).split() if token}


def name_score(left: str, right: str) -> float:
    a, b = _tokens(left), _tokens(right)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    overlap = len(a & b)
    return overlap / max(len(a), len(b))


def folio_score(left: str, right: str) -> float:
    a, b = normalize_folio(left), normalize_folio(right)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    # Prefix/suffix folio noise (old vs new AMC codes).
    if a in b or b in a:
        return 0.9
    return 0.0


@dataclass(frozen=True)
class MatchDecision:
    score: float
    action: str
    risk: float


def decide(
    name_a: str,
    name_b: str,
    folio_a: str = "",
    folio_b: str = "",
    merge_floor: float = 0.93,
    review_floor: float = 0.75,
    max_auto_risk: float = 0.20,
) -> MatchDecision:
    """No silent auto-merge when estimated error risk exceeds max_auto_risk."""
    score = max(name_score(name_a, name_b), folio_score(folio_a, folio_b))
    if folio_a and folio_b:
        score = 0.6 * folio_score(folio_a, folio_b) + 0.4 * name_score(name_a, name_b)
    risk = round(1.0 - score, 4)
    if score >= merge_floor and risk <= max_auto_risk:
        action = "merge"
    elif score >= review_floor:
        action = "review"
    else:
        action = "distinct"
    return MatchDecision(score=round(score, 4), action=action, risk=risk)


def pairwise_clusters(pairs: list[tuple[int, int, str]], n: int) -> list[str]:
    """Union-find from merge decisions. Returns cluster id per record."""
    parent = list(range(n))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for left, right, action in pairs:
        if action != "merge":
            continue
        a, b = find(left), find(right)
        if a != b:
            parent[b] = a
    return [str(find(i)) for i in range(n)]
