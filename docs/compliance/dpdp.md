# DPDP notes

Quantastica processes household financial records. The bank or firm that deploys it is
the data fiduciary for a B2B install. This repo is the processor shape.

## What ships now

- PAN and long account numbers are masked before LLM prompts (`app/privacy.py`) and
  in logs (`app/core/redaction.py`).
- Consent rows (`consents` table) record purpose and grant/withdraw.
- `GET /api/privacy/households/{id}/export` and `POST /api/control/dsr/access`
  return the book, lots, exceptions, and consents for a household.
- `POST /api/control/dsr/erasure` (admin only) clears lots, exceptions, artifacts,
  and consents, and marks the household erased. DSR audit rows are retained.
- Firm roles: admin, adviser, reviewer, read_only. Dev `user` maps to adviser, so
  erasure stays admin-only even in default dev.
- Row-level security on `document_chunks` via `SET LOCAL app.current_user_id`
  and FORCE RLS in the control-plane migration.

## Still required before a bank pilot

- Purpose limitation per ingest artifact.
- Data residency: prod *target* is GCP `asia-south1`. AWS adapters remain.
  Terraform has not been applied. CMEK is false.
- DPIA with the deploying bank's DPO.
- 72-hour breach process with the fiduciary, not only a JSON field.
