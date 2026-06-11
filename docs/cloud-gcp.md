# Running on GCP

Set `PLATFORM=gcp`. The factory wires Firestore, Vertex AI, Pub/Sub, and GCS.

## Required env

| Variable | Purpose |
|---|---|
| `GCP_PROJECT` | Firestore, Pub/Sub, and Vertex project |
| `GCP_REGION` | Vertex AI region |
| `VERTEX_MODEL` | Claude model id on Vertex (for example `claude-3-5-haiku@20241022`) |
| `PUBSUB_TOPIC` | Pub/Sub topic for run events |
| `GCS_BUCKET` | Bucket for exported run reports |

## Least privilege roles

Grant the service account only:

- `roles/datastore.user`
- `roles/pubsub.publisher`
- `roles/storage.objectAdmin` (scoped to the single export bucket)
- `roles/aiplatform.user`

## Enable APIs

```
gcloud services enable \
  firestore.googleapis.com \
  pubsub.googleapis.com \
  storage.googleapis.com \
  aiplatform.googleapis.com
```

## Credentials

Use Application Default Credentials or Workload Identity. Never commit a key file. On
Cloud Run, attach the service account and load secrets from Secret Manager.

## Deploy

1. Backend to Cloud Run using `apps/server/Dockerfile`.
2. Frontend: `VITE_API_URL=<cloud run url> npm run build:web`, then deploy
   `apps/web/dist` to Firebase Hosting.
3. Verify `GET /api/platform` shows all four components ready, then run the smoke test
   against the Cloud Run URL.

## CI emulator

The Firestore implementation is tested in CI against the firestore emulator, selected by
the `FIRESTORE_EMULATOR_HOST` environment variable that the Google client library honors.
