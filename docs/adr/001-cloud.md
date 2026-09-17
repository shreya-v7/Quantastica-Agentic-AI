# ADR 001: Single cloud AWS Mumbai

Status: superseded (16 Sep 2026) by [ADR 007](007-residency.md).

AWS `ap-south-1` adapters remain in the factory. The production *target* is now
GCP `asia-south1`. Postgres 16 + pgvector is still the book of record on every
platform. DynamoDB is not used.

Original decision (kept for history): production inference and data stay in AWS
`ap-south-1`. Claude on Bedrock in Mumbai is the residency argument for BFSI
buyers. GCP remains a local/dev factory option only.

