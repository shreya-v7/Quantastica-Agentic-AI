# Quantastica

Quantastica is an agentic financial intelligence platform. You ask a natural language
question about a portfolio ("How concentrated is my AI portfolio?") and an agent
pipeline analyzes the actual portfolio data, then returns a structured, explainable
answer with a full execution trace.

The same codebase runs locally with no cloud account, on GCP, or on AWS, selected by one
environment variable (`PLATFORM`).

## Architecture

Clean layered partition. Dependencies point downward only.

```
routes      HTTP only: parse, call service, wrap envelope
  services  business logic, orchestration entry
  agents    Planner, Researcher, Risk, Insight, Summarizer, Orchestrator
  infra
    repo    data access (SQLite local, Firestore gcp, DynamoDB aws)
    llm     LLM client (Anthropic local, Vertex AI gcp, Bedrock aws)
    events  event publisher (in-process local, Pub/Sub gcp, SQS aws)
    storage blob storage for exports (local disk, GCS gcp, S3 aws)
```

Each infrastructure concern is one small interface with three real implementations. A
factory reads `PLATFORM` (`local | gcp | aws`) and wires the matching set. Local is a
real implementation: SQLite is a real database, local disk is real storage, the Anthropic
API is a real LLM.

See [docs/architecture.md](docs/architecture.md) and
[docs/agentic-design.md](docs/agentic-design.md) for detail.

## Local setup (no cloud account needed)

```
git clone <repo> && cd quantastica
make setup        # npm install (builds types), python venv, pip install, copies .env.example to .env
# add ANTHROPIC_API_KEY=sk-... to apps/server/.env (the only required secret locally)
make seed         # loads flagged seed data into SQLite
make dev          # starts API :8000 and web :5173 together
```

Smoke test:

```
curl localhost:8000/api/health
curl localhost:8000/api/platform
curl -X POST localhost:8000/api/agents/run -H 'content-type: application/json' \
  -d '{"query":"How concentrated is my AI portfolio?","portfolioId":"pf_tech_heavy"}'
```

Then open localhost:5173, run the same query on the Agents page, and watch the trace.

Alternative: `docker compose up` (set `ANTHROPIC_API_KEY` in your shell first) runs the
full stack with one command, then load seed data with
`curl -X POST localhost:8000/api/seed/load`.

## GCP

1. Service account with least privilege roles: `roles/datastore.user`,
   `roles/pubsub.publisher`, `roles/storage.objectAdmin` (scoped to one bucket),
   `roles/aiplatform.user`.
2. Enable APIs:
   `gcloud services enable firestore.googleapis.com pubsub.googleapis.com storage.googleapis.com aiplatform.googleapis.com`
3. Env: `PLATFORM=gcp`, `GCP_PROJECT`, `GCP_REGION`, `GCS_BUCKET`, `PUBSUB_TOPIC`,
   `VERTEX_MODEL` (default a Claude model on Vertex). Credentials via Application Default
   Credentials or Workload Identity, never a key file in the repo.
4. Deploy: backend to Cloud Run (secrets from Secret Manager), frontend
   `npm run build:web` with `VITE_API_URL=<cloud run url>` to Firebase Hosting.
5. Verify with `GET /api/platform` showing all four components ready, then run the smoke
   test against the Cloud Run URL.

See [docs/cloud-gcp.md](docs/cloud-gcp.md).

## AWS

1. IAM role with least privilege inline policies scoped to one DynamoDB table prefix, one
   SQS queue, one S3 bucket, and `bedrock:InvokeModel` on the chosen model. The exact
   policy is in [docs/cloud-aws.md](docs/cloud-aws.md). No FullAccess policies.
2. Env: `PLATFORM=aws`, `AWS_REGION`, `DDB_TABLE_PREFIX`, `SQS_QUEUE_URL`, `S3_BUCKET`,
   `BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0`. Credentials via the role
   (ECS task role or Lambda execution role), never static keys in prod.
3. Deploy: backend container to ECS Fargate (or Lambda plus API Gateway via Mangum),
   frontend `aws s3 sync apps/web/dist s3://<bucket>` behind CloudFront with `VITE_API_URL`
   set at build time.
4. Verify with `GET /api/platform`, then the smoke test against the public URL.

## API

Every `/api/*` response uses one envelope:

```json
{ "ok": true, "data": {}, "error": null, "meta": { "requestId": "...", "version": "2.0.0" } }
```

Typed errors map to stable codes: `NOT_FOUND`, `VALIDATION_ERROR`, `LLM_ERROR`,
`PLATFORM_NOT_CONFIGURED`, `AUTH_REQUIRED`, `INTERNAL_ERROR`. Stack traces and secret
values are never leaked. Every request carries `X-Request-ID`, propagated to logs.

Endpoints: `GET /api/health`, `GET /api/platform`, `GET /api/portfolios`,
`GET /api/portfolios/{id}`, `GET /api/insights?portfolioId=&severity=`,
`POST /api/agents/run`, `GET /api/agents/runs`, `GET /api/agents/runs/{id}`,
`POST /api/agents/runs/{id}/export`, `POST /api/seed/load`, `POST /api/seed/reset`.

## Dev vs prod

`APP_ENV` is `dev` or `prod`. Startup validates and fails fast, naming the exact missing
variable.

| Concern | dev | prod |
|---|---|---|
| PLATFORM | `local` default | `gcp` or `aws`, all required vars present or startup aborts |
| Auth | `REQUIRE_AUTH=false` allowed, `/dev/session` active | forced on, JWT secret 32+ bytes, `/dev/session` excluded |
| CORS | localhost origins | explicit `CORS_ORIGINS`, refuses `*` |
| Seed endpoints | enabled | disabled unless `ALLOW_SEED=true` |
| Logging | readable console | structured JSON with request ids |
| OpenAPI /docs | on | off |

## Seed data

Seed data lives in exactly one place: `apps/server/app/seed/`. Every record is flagged
`"seed": true`. Loading is always an explicit action (`make seed`, `python -m app.seed`,
or `POST /api/seed/load`), never automatic in prod. Nothing else in the codebase
fabricates data. The only other permitted fake is the deterministic LLM test double under
`apps/server/tests/`, which never ships in `app/`.

## Testing

```
make check        # lint, typecheck, tests, contract check, and the em dash check
make test         # backend pytest plus frontend vitest
```

All tests pass offline with `PLATFORM=local` and a fake LLM injected in tests only. The
Firestore and DynamoDB implementations are tested against their official local emulators
in CI (firestore emulator and dynamodb-local), not mocked out.
