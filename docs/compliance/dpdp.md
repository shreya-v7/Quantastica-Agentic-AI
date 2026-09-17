# DPDP notes

Quantastica processes household financial records. The bank or firm that deploys it is
the data fiduciary for a B2B install. This repo is the processor shape.

## What ships now

- PAN and long account numbers are masked before LLM prompts (`app/privacy.py`) and
  in logs (`app/core/redaction.py`).
- Consent rows (`consents` table) record purpose and grant/withdraw.
- `GET /api/privacy/households/{id}/export` returns the book, lots, exceptions, and
  consents for a household.
- Firm roles: admin, adviser, reviewer, read_only. Dev `user` maps to adviser.

## Still required before a bank pilot

- Household deletion (right to erasure) with retention holds for audit.
- Purpose limitation per ingest artifact.
- Row-level security on `firm_id` (SQL is drafted in runbooks; not enabled in local
  so tests can seed without `SET app.firm_id`).
- Data residency: prod target is AWS Mumbai (`ap-south-1`). Do not dual-cloud.
- DPIA with the deploying bank's DPO.
