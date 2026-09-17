# Vendor risk (processors)

This is a working list for a bank DPIA, not a completed assessment.

| Vendor / library | Role | Data | Notes |
|---|---|---|---|
| PostgreSQL 16 + pgvector | Book of record | Holdings, chunks, events | Self-hosted or Cloud SQL / RDS. RLS on chunks. |
| Redis | Cache, streams | Non-authoritative | Factory publisher today. |
| Anthropic / Gemini / Vertex / Bedrock | LLM | Masked prompts | PAN and account numbers stripped before complete(). |
| Voyage | Embeddings | Chunk text | Optional. Hashing embeddings in CI. |
| Sarvam | STT/TTS | Audio, transcripts | Key-gated. Mock in CI. Numbers still parsed by extractors. |
| Google Cloud (`asia-south1`) | Target host | Same as above | Terraform not applied. Workload Identity, no key files. |
| AWS (`ap-south-1`) | Portable factory | Same contract | Bedrock, S3, SQS adapters retained. |
| Sentry | Errors | Stack traces, request ids | Optional DSN. |

Do not send raw PAN, full account numbers, or unredacted books to a model host.
See [dpdp.md](dpdp.md) and [adr/007-residency.md](../adr/007-residency.md).
