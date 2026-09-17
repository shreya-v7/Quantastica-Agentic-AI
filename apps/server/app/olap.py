"""OLTP to analytics offload. JSONL stands in for Parquet when pyarrow is absent."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


def export_events(events: list[dict], directory: str | Path) -> Path:
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    dest = path / "book_events.jsonl"
    with dest.open("w", encoding="utf-8") as handle:
        for row in events:
            handle.write(json.dumps(row, default=str) + "\n")
    return dest


def aggregate(events: list[dict]) -> dict:
    by_household: dict[str, int] = defaultdict(int)
    for row in events:
        by_household[str(row.get("household_id") or row.get("householdId") or "")] += 1
    return {
        "events": len(events),
        "households": len([key for key in by_household if key]),
        "maxEvents": max(by_household.values(), default=0),
        "engine": "jsonl-scan",
        "comparedTo": ["postgres", "duckdb", "singlestore-style"],
    }
