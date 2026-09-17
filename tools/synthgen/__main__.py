"""Deterministic synthetic household generator.

Usage from repo root:
  PYTHONPATH=apps/server python -m tools.synthgen --tier small --seed 42
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.exceptions.engine import compute_exceptions
from app.exceptions.fixtures import demo_books


def small_bundle(seed: int = 42) -> dict:
    households = []
    for book in demo_books():
        hits = compute_exceptions(book)
        households.append(
            {
                "id": book.household_id,
                "name": book.household_name,
                "asOf": book.as_of.isoformat(),
                "tax": book.tax.model_dump(mode="json") if book.tax else None,
                "lots": [lot.model_dump(mode="json") for lot in book.lots],
                "exceptions": [
                    {
                        "ruleId": hit.rule_id,
                        "rupeeDelta": hit.rupee_delta,
                        "fingerprint": hit.fingerprint,
                    }
                    for hit in hits
                ],
                "synthetic": True,
                "seed": seed,
            }
        )
    return {
        "tier": "small",
        "seed": seed,
        "firms": [{"id": "firm_northstar", "name": "Northstar Private", "synthetic": True}],
        "households": households,
        "note": "Fake PANs and books. Not real people. Mehta and Rao are hand-crafted.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tier", choices=["small", "medium", "large"], default="small")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.tier != "small":
        raise SystemExit(f"{args.tier} tier is not implemented yet. Use --tier small.")
    bundle = small_bundle(args.seed)
    out = Path("tools/synthgen/out")
    out.mkdir(parents=True, exist_ok=True)
    path = out / "small.json"
    path.write_text(json.dumps(bundle, indent=2) + "\n")
    print(f"wrote {path} households={len(bundle['households'])}")


if __name__ == "__main__":
    main()
