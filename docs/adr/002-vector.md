# ADR 002: pgvector, not a separate vector DB

Status: accepted

Hybrid retrieval is dense + BM25 + RRF over Postgres. One operational store. Voyage or
Bedrock embeddings sit behind the existing provider slot.
