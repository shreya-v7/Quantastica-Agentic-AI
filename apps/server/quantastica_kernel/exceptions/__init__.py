"""Deterministic exception engine. No LLM. Every rupee comes from calculators."""

from quantastica_kernel.exceptions.engine import compute_exceptions, diff_exceptions
from quantastica_kernel.exceptions.hits import ExceptionHit, PolicyTable
from quantastica_kernel.exceptions.snapshot import BookLot, BookSnapshot, TaxFacts

__all__ = [
    "BookLot",
    "BookSnapshot",
    "ExceptionHit",
    "PolicyTable",
    "TaxFacts",
    "compute_exceptions",
    "diff_exceptions",
]
