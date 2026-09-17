# Running on GCP

**Target, not live.** Production intent is GCP `asia-south1`. See
[adr/007-residency.md](adr/007-residency.md). Terraform in `infra/gcp` has not
been applied. CMEK is false. Postgres 16 remains the book of record; Firestore
is not used.

Local and CI use the same contracts: LocalBus for Pub/Sub, JSONL for OLAP,
Mock VLM, Mock speech.

## Required env when PLATFORM=gcp

| Variable | Purpose |
|---|---|
| `GCP_PROJECT` | Vertex, GCS, and (later) Pub/Sub project |
| `GCP_REGION` | Vertex region. Use `asia-south1`. |
| `VERTEX_MODEL` | Claude or Gemini model id on Vertex |
| `GCS_BUCKET` | Bucket for exports and (later) Parquet |
| `PUBSUB_TOPIC` | Optional. LocalBus stands in until credentials exist. |

## Least privilege roles (when applied)

Grant the service account only:

- `roles/cloudsql.client`
- `roles/pubsub.publisher`
- `roles/storage.objectAdmin` (scoped to the single export bucket)
- `roles/aiplatform.user`
- `roles/secretmanager.secretAccessor`

## Enable APIs (when applied)

```
gcloud services enable \
  sqladmin.googleapis.com \
  pubsub.googleapis.com \
  storage.googleapis.com \
  aiplatform.googleapis.com \
  secretmanager.googleapis.com \
  run.googleapis.com
```

## Credentials

Workload Identity Federation. Never commit a key file. On Cloud Run, attach the
service account and load secrets from Secret Manager.
