"""Versioned, JSON-in/JSON-out calculation receipts and fail-closed replay."""
from __future__ import annotations

import inspect
import json
from hashlib import sha256
from typing import Any

from pydantic import BaseModel

from .calculators.capital_gains import SellLot, compute_equity_gains
from .calculators.planning import (
    AffordabilityInput,
    affordability,
    emi,
    monte_carlo_sip,
    required_monthly_sip,
    step_up_sip_first_month,
)
from .calculators.tax import TaxInput, compare_regimes
from .exceptions.engine import compute_exceptions
from .exceptions.hits import PolicyTable
from .exceptions.snapshot import BookSnapshot

VERSION = "1.0.0-ay2025_26"
SCALARS = {
    "sip": required_monthly_sip,
    "step_up_sip": step_up_sip_first_month,
    "emi": emi,
    "monte_carlo": monte_carlo_sip,
}
CALCULATORS = (*SCALARS, "tax", "capital_gains", "affordability", "exceptions")


def canonical(value: Any) -> str:
    """Stable encoding; non-finite numbers cannot become evidence."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _json(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return _json(value.model_dump(mode="python"))
    if isinstance(value, list):
        return [_json(item) for item in value]
    if isinstance(value, dict):
        return {key: _json(item) for key, item in value.items()}
    from datetime import date
    if isinstance(value, date):
        return value.isoformat()
    return value


def calculate(calculator_id: str, inputs: dict, version: str = VERSION) -> dict:
    """Inputs and outputs are detached JSON values. Persist the returned receipt at the edge.

    A hash proves content integrity, not source authenticity or legal correctness.
    Scalar monetary results are rounded to paisa at this interface.
    """
    if version != VERSION:
        raise ValueError(f"Unsupported calculator version: {version}")
    data = json.loads(canonical(inputs))
    if calculator_id in SCALARS:
        fn = SCALARS[calculator_id]
        args = inspect.signature(fn).bind(**data)
        args.apply_defaults()
        data = dict(args.arguments)
        result = fn(**data)
        if isinstance(result, float):
            result = round(result, 2)
    elif calculator_id in {"tax", "affordability"}:
        model, fn = (TaxInput, compare_regimes) if calculator_id == "tax" else (
            AffordabilityInput, affordability
        )
        validated = model.model_validate(data)
        data = _json(validated)
        result = fn(validated)
    elif calculator_id == "capital_gains":
        if set(data) != {"lots"}:
            raise ValueError("capital_gains requires only lots")
        lots = [SellLot.model_validate(lot) for lot in data["lots"]]
        data = {"lots": _json(lots)}
        result = compute_equity_gains(lots)
    elif calculator_id == "exceptions":
        if set(data) - {"book", "policy"}:
            raise ValueError("Unexpected exception inputs")
        book = BookSnapshot.model_validate(data["book"])
        policy = PolicyTable.model_validate(data.get("policy", {}))
        data = {"book": _json(book), "policy": _json(policy)}
        result = compute_exceptions(book, policy)
    else:
        raise ValueError(f"Unknown calculator: {calculator_id}")
    payload = {
        "calculator_id": calculator_id, "version": version,
        "inputs": data, "outputs": _json(result),
    }
    encoded = canonical(payload)
    return {**json.loads(encoded), "content_hash": sha256(encoded.encode()).hexdigest()}


def replay(receipt: dict) -> dict:
    if set(receipt) != {"calculator_id", "version", "inputs", "outputs", "content_hash"}:
        raise ValueError("Invalid receipt fields")
    actual = calculate(receipt["calculator_id"], receipt["inputs"], receipt["version"])
    if canonical(actual) != canonical(receipt):
        raise ValueError("Receipt failed replay verification")
    return actual
