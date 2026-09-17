"""Deterministic exception engine. No LLM. Every rupee comes from calculators."""

from app.exceptions.engine import compute_exceptions, diff_exceptions, merge_hits
from app.exceptions.hits import ExceptionHit, PolicyTable
from app.exceptions.snapshot import BookLot, BookSnapshot, TaxFacts

__all__ = [
    "BookLot",
    "BookSnapshot",
    "ExceptionHit",
    "PolicyTable",
    "TaxFacts",
    "compute_exceptions",
    "diff_exceptions",
    "merge_hits",
]
