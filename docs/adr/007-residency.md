# ADR 007: Residency target GCP asia-south1, AWS portable

Status: accepted (16 Sep 2026)
Supersedes: [ADR 001](001-cloud.md) for the production *target*. ADR 001 still
describes the AWS factory adapters that remain in the repo.

## Decision

Ship toward GCP `asia-south1` (Mumbai) for the B2B bank VPC story: Cloud SQL
Postgres 16, Pub/Sub ordering keys, Cloud Run, Secret Manager, Vertex. Keep
`PLATFORM=local|gcp|aws` and the AWS Mumbai adapters so a later port is a
factory swap, not a rewrite.

## Why not apply Terraform today

`infra/gcp/main.tf` is plan-only. No project is bound. CMEK is false. DuckDB
and PyArrow are not required dependencies. LocalBus and JSONL stand in for
Pub/Sub and Parquet with the same envelopes.

## Consequences

- Docs and `/api/control/trust` must say "planned", not "live in asia-south1".
- Google ADK is not a runtime. `QuantasticaTeam` is the portable graph.
- Isolated kernel CI still installs `quantastica_kernel` with pydantic only.
