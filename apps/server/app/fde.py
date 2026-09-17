"""Forward-deployed engineer onboarding: tenant config plus Form 16 layout pack."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TenantSpec:
    tenant_id: str
    name: str
    segment: str
    employers: tuple[str, ...]
    layout_pack: str


def load_spec(path: str | Path) -> TenantSpec:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return TenantSpec(
        tenant_id=raw["tenant_id"],
        name=raw["name"],
        segment=raw.get("segment") or "ca",
        employers=tuple(raw.get("employers") or ()),
        layout_pack=raw.get("layout_pack") or "default",
    )


NORTHSTAR_LAYOUT = {
    "employer": "Northstar Labs Pvt Ltd",
    "fields": {"basic_salary": {"page": 1, "label": "Basic Salary"}},
}


def layout_for(employer: str) -> dict:
    if "northstar" in employer.lower():
        return NORTHSTAR_LAYOUT
    return {"employer": employer, "fields": {"basic_salary": {"page": 1, "label": "Salary"}}}


def health(adoption: float, exceptions_cleared: int, rupees: float, freshness_s: float,
           ingest_error_rate: float, layout_coverage: float) -> dict:
    score = (
        0.25 * min(adoption, 1.0)
        + 0.2 * min(exceptions_cleared / 10, 1.0)
        + 0.2 * (1.0 if rupees > 0 else 0.0)
        + 0.15 * (1.0 if freshness_s < 60 else 0.4)
        + 0.1 * (1.0 - min(ingest_error_rate, 1.0))
        + 0.1 * min(layout_coverage, 1.0)
    )
    return {
        "score": round(score, 3),
        "adoption": adoption,
        "exceptionsCleared": exceptions_cleared,
        "rupeesSurfaced": rupees,
        "freshnessSeconds": freshness_s,
        "ingestErrorRate": ingest_error_rate,
        "layoutCoverage": layout_coverage,
    }
