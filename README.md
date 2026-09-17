# Quantastica

A grounded intelligence layer for Indian HNI books and bank RM desks.
The model classifies and writes. Calculators and the (mock) bank book supply every
rupee. It does not invent figures.

**Read [docs/product.md](docs/product.md) first.** Target design:
[docs/system-design.md](docs/system-design.md). Demo script: [docs/demo.md](docs/demo.md).
This README is how to run the repo.

B2B is the motion that can pay for this stack: package it for a bank, they remain
the regulated adviser, we compute. B2C HNIs are a second-opinion desk, not a mass
app. Middle-income users can sit on a bank's white-label. They will not fund the
cloud bill.

This is not investment advice, not a SEBI-registered advisory, and not a solicitation
to buy or sell any security.

## The idea

Most "AI finance" products let a language model guess. Quantastica inverts that.

1. The book comes from a bank adapter. Locally that is mock Northstar Private.
2. You ask in plain language: tax, SIP, concentration, a quote, or a statement.
3. Intent is classified. Numbers come from code.
4. If a calculator cannot run, the desk asks for the missing input instead of filling it in.
5. For portfolio questions, a traced pipeline computes weights and risk, then writes from those metrics.

Ask lives at `/ask`. Desk home is the exception queue. Ingest and voice sit on the
desk. The public site is `/`. The operator console is `/operators`. Metrics are
`/metrics`. The mock bank is `/api/bank`. MCP is `python -m app.mcp`.

## What is real today

| Loop | What happens |
|---|---|
| **Exception queue** | Desk home. Regime, lot clock, concentration, deduction headroom. Calculators only. |
| Tax / SIP / affordability | Deterministic calculators. LLM only narrates the output. |
| Portfolio concentration | Planner, researcher, risk, insight, summarizer. Researcher and risk are pure code. |
| Documents | Chunk, embed, hybrid retrieve (dense + BM25 + RRF), cite. Needs embeddings configured. |
| Ingest | Form 16 / AIS / CAS / text events. Mock VLM in CI. Low confidence pauses. |
| Voice | Mock STT/TTS. Spoken questions read the queue. Sarvam when keyed. |
| Northstar books | Mehta and Rao lots, seeded into households. `make seed-small`. |

Match, paper trades, automation, WhatsApp stay in code, off the primary nav (Phase 4).
Conversational trading is off until `TRADING_CHAT_ENABLED=true`. Compliance notes:
[docs/compliance/trading.md](docs/compliance/trading.md).

## Offline proof demo (Phase 0)

After setup, run `make demo`, then open http://127.0.0.1:8010. It needs no
Postgres, Redis, model key, or network services. If macOS blocks make pending
its Xcode license, run `cd apps/server && .venv/bin/python -m app.offline_demo`.
Use `make demo DEMO_ARGS="--tier medium --seed 42"` for generated households.
This is a small, separate proof desk; the full React application still uses
its existing infrastructure. Mock speech returns a labelled placeholder, not audio.

The extracted kernel is independently installable with
`pip install ./apps/server/quantastica_kernel`. Existing calculator imports
remain compatible. `make kernel-check` checks golden amounts and receipt replay.
See [the phase gate and limitations](docs/phase-0-kernel.md).

## Local run

You need Postgres 16 with pgvector, Redis, one LLM key, then:

```
make setup
# add ANTHROPIC_API_KEY or GEMINI_API_KEY to apps/server/.env. Do not commit it.
docker compose up postgres redis   # or your own local instances
# from apps/server: alembic upgrade head
make seed
make dev
```

Open `http://localhost:5173/desk`, select Mehta, confirm at least two exceptions.
Change a lot quantity. The queue updates. That is the product. Smoke:

```
curl localhost:8000/api/health
curl localhost:8000/api/desk/households
curl localhost:8000/api/desk/households/hh_mehta/queue
```

`docker compose up --build` starts API, worker, web, Postgres, and Redis together.
Seed with `curl -X POST localhost:8000/api/seed/load` (needs `ALLOW_SEED=true`).

## Architecture

Dependencies point downward only.

```
routes      HTTP: parse, call service, envelope
  services  business logic
  agents    linear pipeline with a persisted trace
  infra     Postgres + pgvector, Redis, LLM, object storage
```

`PLATFORM=local | gcp | aws` selects LLM and object storage. Postgres and Redis are
used on every platform. Local LLM is Anthropic or Gemini. The new master roadmap targets GCP `asia-south1`, retaining AWS Mumbai portability.
Cloud deployment changes remain gated on the earlier phases; the existing
provider implementations have not been replaced.

See [docs/system-design.md](docs/system-design.md),
[docs/architecture.md](docs/architecture.md), and
[docs/agentic-design.md](docs/agentic-design.md).

## Where this can go next

Keep the spine small. Follow [docs/system-design.md](docs/system-design.md) in order.

1. **Exception engine on a unified book.** Desk home is the Mehta queue. Fixture tests
   must match calculator rupees.
2. **Outbox recompute.** Local relay first; EventBridge/SQS when on AWS.
3. **Parse graph + one VLM fixture.** casparser for CAS. PostgresSaver, interrupt on
   low confidence.
4. **Cloud deployment.** The master roadmap now targets GCP asia-south1.
   The database remains Postgres everywhere.
5. **Hide the rest.** Match, trades, automation, WhatsApp, AA stay in code, off the
   household nav.
6. **Audio last.** Sarvam STT/TTS as a text event. Never let speech invent a rupee.

Later, if the spine holds: Account Aggregator for real holdings, paper trading against
live quotes, a WhatsApp channel that calls the same calculators.

## API

Every `/api/*` response uses one envelope:

```json
{ "ok": true, "data": {}, "error": null, "meta": { "requestId": "...", "version": "2.0.0" } }
```

Typed errors map to stable codes: `NOT_FOUND`, `VALIDATION_ERROR`, `LLM_ERROR`,
`PLATFORM_NOT_CONFIGURED`, `AUTH_REQUIRED`, `INTERNAL_ERROR`. Stack traces and secrets
are never leaked.

## Dev vs prod

`APP_ENV` is `dev` or `prod`. Prod startup aborts if required vars are missing.

| Concern | dev | prod |
|---|---|---|
| PLATFORM | `local` default | GCP asia-south1 planned; existing AWS adapter retained |
| Auth | `REQUIRE_AUTH=false` allowed | forced on, JWT secret 32+ bytes |
| CORS | localhost origins | explicit `CORS_ORIGINS`, refuses `*` |
| Seed | `make seed` / `ALLOW_SEED` | off unless `ALLOW_SEED=true` |
| Logging | console | JSON with request ids |
| OpenAPI /docs | on | off |

## Testing

```
make check        # lint, typecheck, tests, contract check, em dash check
make test         # backend pytest plus frontend vitest
make eval         # India golden calculators plus retrieval sample
```

Integration tests expect Docker (testcontainers for Postgres and Redis). Unit tests for
calculators and graph control flow run offline with a fake LLM.
