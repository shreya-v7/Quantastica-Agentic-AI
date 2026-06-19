# Deployment

The platform runs as two containers built from `apps/server`: the API server and the
background worker. Infrastructure lives in `infra/terraform` (GCP: Cloud Run, Cloud SQL
Postgres 16, Memorystore Redis 7, a GCS bucket, and Secret Manager).

## Build images

```bash
# API server (also runs Alembic migrations on boot via its CMD)
docker build -t REGION-docker.pkg.dev/PROJECT/quantastica/server:$(git rev-parse --short HEAD) apps/server

# Worker uses the same image with a different command (see docker-compose.yml / Terraform)
```

## Provision infrastructure

```bash
cd infra/terraform
terraform init
terraform apply \
  -var project_id=PROJECT \
  -var server_image=REGION-docker.pkg.dev/PROJECT/quantastica/server:TAG \
  -var worker_image=REGION-docker.pkg.dev/PROJECT/quantastica/server:TAG
```

Populate secrets (`*-jwt-secret`, `*-database-url`, `*-anthropic-api-key`,
`*-whatsapp-app-secret`) in Secret Manager and mount them into the Run services.

## Database migrations

Migrations run automatically when the server container starts
(`alembic upgrade head && uvicorn ...`). To run them out of band:

```bash
DATABASE_URL=postgresql+asyncpg://... alembic upgrade head
```

The pgvector extension is created by the first migration; the Cloud SQL flag
`cloudsql.enable_pgvector` (or `CREATE EXTENSION vector`) must be permitted.

## Releases (blue/green)

1. Deploy the new revision with `--no-traffic`.
2. Smoke test against the revision URL (`/api/ready`, a read, a chat call).
3. Shift 10% -> 50% -> 100% traffic, watching the error-rate and latency alerts.
4. Roll back instantly by shifting traffic to the previous healthy revision.

## Configuration

All config is environment driven (twelve-factor). See `apps/server/.env.example` for the
full list. `PLATFORM=gcp` selects the GCP provider implementations; `APP_ENV=prod`
enables auth, disables the dev cache bypass, and switches logs to redacted JSON.
