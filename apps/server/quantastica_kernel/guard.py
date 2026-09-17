"""Fail-closed numeric grounding and advice detection. The kernel never invents rupees."""
from __future__ import annotations

import re
from dataclasses import dataclass

NUMBER_RE = re.compile(
    r"(?:rs\.?|inr|₹)?\s*(\d{1,3}(?:,\d{2,3})+|\d+)(?:\.(\d{1,2}))?",
    re.I,
)
ADVICE_RE = re.compile(
    r"\b(you should (buy|sell|switch)|switch regime|tax due|invest in|"
    r"i recommend|go all in|this is a buy)\b",
    re.I,
)
# Benign mentions that over-defense traps use (NotInject-style).
BENIGN_RE = re.compile(
    r"\b(already sold|informational only|not (a |investment )?advice|paper (order|trade))\b",
    re.I,
)


def parse_amounts(text: str) -> list[float]:
    amounts: list[float] = []
    for match in NUMBER_RE.finditer(text or ""):
        whole = match.group(1).replace(",", "")
        frac = match.group(2) or "0"
        amounts.append(round(float(f"{whole}.{frac}"), 2))
    return amounts


def _allowed(values: list[float] | set[float]) -> set[float]:
    return {round(float(item), 2) for item in values}


@dataclass(frozen=True)
class GuardVerdict:
    ok: bool
    ungrounded: tuple[float, ...]
    advice: bool
    reason: str


def screen(
    text: str,
    allowed_amounts: list[float] | set[float],
    source_quotes: list[str] | None = None,
) -> GuardVerdict:
    """Fail closed: any surfaced rupee must be in kernel outputs or a source quote."""
    allowed = _allowed(allowed_amounts)
    for quote in source_quotes or []:
        allowed |= _allowed(parse_amounts(quote))
    found = parse_amounts(text)
    ungrounded = tuple(value for value in found if value not in allowed and value not in {0.0})
    advice = bool(ADVICE_RE.search(text or "")) and not bool(BENIGN_RE.search(text or ""))
    if ungrounded:
        return GuardVerdict(False, ungrounded, advice, "ungrounded_number")
    if advice:
        return GuardVerdict(False, (), True, "advice")
    return GuardVerdict(True, (), False, "ok")


def fail_closed(text: str, allowed_amounts: list[float] | set[float],
                source_quotes: list[str] | None = None) -> str:
    verdict = screen(text, allowed_amounts, source_quotes)
    if verdict.ok:
        return text
    return (
        "This answer was blocked. Quantastica only surfaces calculator rupees "
        "and source quotes. Informational only, not advice."
    )
