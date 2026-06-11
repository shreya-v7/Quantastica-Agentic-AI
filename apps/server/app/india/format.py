"""Indian numbering system formatters. The single INR renderer used by the API,
the LLM prompts, and exports. The frontend mirrors this in src/lib/format.ts."""

from __future__ import annotations

LAKH = 100_000
CRORE = 10_000_000


def format_inr_grouping(value: float, decimals: int = 0) -> str:
    """Render with Indian digit grouping: 1,50,000 / 12,34,56,789.50."""
    negative = value < 0
    quantized = round(abs(value), decimals)
    integer = int(quantized)
    fraction = quantized - integer

    digits = str(integer)
    if len(digits) <= 3:
        grouped = digits
    else:
        head, tail = digits[:-3], digits[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        grouped = ",".join([*parts, tail])

    if decimals > 0:
        grouped += f"{fraction:.{decimals}f}"[1:]
    return f"-{grouped}" if negative else grouped


def format_inr(value: float, decimals: int = 0) -> str:
    """Rs 1,50,000 style absolute rendering."""
    return f"Rs {format_inr_grouping(value, decimals)}"


def format_inr_compact(value: float) -> str:
    """Lakh/crore rendering: 12.5 lakh, 1.2 crore, 75,000."""
    sign = "-" if value < 0 else ""
    magnitude = abs(value)
    if magnitude >= CRORE:
        return f"{sign}{_trim(magnitude / CRORE)} crore"
    if magnitude >= LAKH:
        return f"{sign}{_trim(magnitude / LAKH)} lakh"
    return f"{sign}{format_inr_grouping(magnitude)}"


def _trim(scaled: float) -> str:
    text = f"{scaled:.2f}".rstrip("0").rstrip(".")
    return text if text else "0"
