# Phases 3 to 18

Status: implemented as local contracts with tests. Cloud services are not live.
Terraform in `infra/gcp` is plan-only. CMEK is false. OLAP is JSONL, not Parquet.

Kernel isolation, the bitemporal book, and incremental recompute are in
[phase-0-kernel.md](phase-0-kernel.md), [phase-1-bitemporal.md](phase-1-bitemporal.md),
and [phase-2-recompute.md](phase-2-recompute.md).

## Phase 3: ordered bus

`app/bus/LocalBus` is FIFO per household, idempotent on
`(consumer, event_id, calculator_version)`, and dead-letters after redeliveries.
A failed handler is pushed back to the front of that household queue so order
is preserved. `PubSubShim` is the same class under the GCP name. Redis Streams
remains the existing factory publisher until credentials exist.

## Phase 4: ADK-shaped team

`app/team/QuantasticaTeam` is Sequential / Parallel / Loop with depth at most 2.
The ingest coordinator is classifier, then parallel extractors, then a verify
loop (max two retries). Google ADK is not a runtime dependency. The kernel is
not an agent.

## Phase 5: ingest and VLM

LangGraph ingest already routes Form 16 / AIS / CAS / text. Mock VLM returns the
Northstar fixture. Overrides apply only when `kind` matches, so a Form 16 poison
payload cannot leak into AIS parse. Hinglish `barah lakh` maps to Rs 12,00,000.

## Phase 6: reconciler

`quantastica_kernel.reconcile.decide` scores names and folios. High-risk pairs
never silent-merge. Pairwise union-find and BCubed live in the eval catalog.

## Phase 7: fail-closed guard

`quantastica_kernel.guard.screen` requires every surfaced rupee to be in kernel
outputs or a source quote. Advice phrases fail closed. Chat `_ground` walks
computed dicts so FakeLLM tax tests still pass.

## Phase 8: RLS retrieval

`document_repo.search` and `search_hybrid` run
`SET LOCAL app.current_user_id`. Alembic enables FORCE RLS plus policy
`user_id = current_setting('app.current_user_id', true)`. Tests create the
policy, assert no cross-tenant rows, then disable RLS so later tests are not
poisoned.

## Phase 9: model gateway

`FailoverLLM` plus `TokenMeter` emit `gen_ai.*` span attributes and a redacted
content event. Per-tenant hit limits raise `RateLimitedError`.

## Phase 10: OLAP stand-in

`app/olap.export_events` writes JSONL. `aggregate` is a scan. DuckDB and
PyArrow are not required. `engine` reports `jsonl-scan`.

## Phase 11: voice budgets

`timed_speak` records TTFA and end-to-end milliseconds against a 1500 ms budget.
Mock speech is instantaneous. Sarvam remains key-gated.

## Phase 12: synthgen

`python -m tools.synthgen --tier small|medium|large --seed 42` writes a sample
plus a count. Large does not materialize 100k rows. Defects (name variant,
duplicate folio, missing field) are seeded.

## Phase 13: DST

`quantastica_kernel.dst.Simulator(seed)` applies reorder, duplicate, delay, and
drop. Reconstruction is recorded-time ordered, so delivery reorder does not
break the book. The same seed reproduces coverage and `ok`.

## Phase 14: Terraform

`infra/gcp/main.tf` sketches Pub/Sub, Cloud SQL, GCS, and Secret Manager in
`asia-south1`. It has not been applied. No long-lived keys. AWS Mumbai adapters
stay in the factory. See [adr/007-residency.md](adr/007-residency.md).

## Phase 15: DSR

`POST /api/control/dsr/access` (admin, adviser) and `POST /api/control/dsr/erasure`
(admin only). Dev `user` maps to adviser, so erasure stays forbidden in default
dev. Audit rows are retained. Trust JSON lists the 72-hour breach window.

## Phase 16: FDE

`tenants/northstar.json` plus `python -m tools.fde onboard`. Layout packs map
employer labels to Form 16 fields. Health score is a weighted blend of adoption,
exceptions cleared, rupees surfaced, freshness, ingest error rate, and coverage.

## Phase 17: dashboards, evals, SLOs

`GET /api/control/dashboards` and `/evals` feed Metrics. `app/slo.alert` pages on
14.4x burn over 1h confirmed by 5m (Google SRE multiwindow).
`GET /api/control/slo/synthetic-incident` fires a page. Catalog PILOT gates are
in `evals/catalog.py`.

## Phase 18: docs and GTM

Trust center, vendor risk, ADRs, and the pitch metrics page. Informational copy
only. No em dashes.
