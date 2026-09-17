# ADR 001: Single cloud AWS Mumbai

Status: accepted (16 Sep 2026)

Production inference and data stay in AWS `ap-south-1`. Claude on Bedrock in Mumbai is
the residency argument for BFSI buyers. GCP remains a local/dev factory option only.
Postgres 16 + pgvector is the book of record on every platform, including AWS. DynamoDB
is not used.
