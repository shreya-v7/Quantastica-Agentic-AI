See [product.md](product.md) for GTM. See [system-design.md](system-design.md) for the
target exception control plane. See the [root README](../README.md) for the
system, agent, and money-path diagrams. This file is the code layout as it
runs today.

# Architecture

Quantastica is a monorepo with a FastAPI backend, a React frontend, a pip-installable
kernel, and a shared types package.

```
apps/server            FastAPI: routes, services, agents, team, ingest, infra
apps/server/quantastica_kernel  Isolated calculators, exceptions, temporal, guard
apps/web               React 19, Vite, Tailwind, TanStack Query
packages/types         contracts.json version and Zod schemas
infra/gcp              Plan-only Terraform (asia-south1). Not applied.
```

## Layers

Dependencies point downward only. No layer skipping.

1. **routes** parse HTTP input, call a service, and wrap the result in the response
   envelope. They contain no business logic.
2. **services** hold business logic and are the orchestration entry point. They depend on
   the repository and on the agent orchestrator.
3. **agents** are Planner, Researcher, Retrieve, Risk, Insight, Summarizer, and the
   LangGraph orchestrator that runs them in order and records the trace. A second
   ingest graph routes Form 16 / AIS / CAS / text events and pauses on low confidence.
   `QuantasticaTeam` wraps that ingest graph as Sequential / Parallel / Loop (depth 2).
4. **infra** is small interfaces with real implementations:
   - `repo`: PostgreSQL 16 + pgvector on every platform
   - `llm`: Anthropic or Gemini (local), Vertex AI (gcp, asia-south1 target), Bedrock (aws, portable)
   - `events`: Redis Streams in the factory; `LocalBus` / `PubSubShim` for ordered household recompute
   - `storage`: local disk, GCS, or S3
   - `rag`: LlamaIndex chunking, hybrid dense + BM25, RRF fusion, RLS on chunks

## The factory

`app/infra/factory.py` reads `PLATFORM` and builds the matching set. A component is built
only when its required env vars are present. In dev the app starts degraded and reports
honest readiness on `GET /api/platform`. In prod the settings validator aborts startup,
naming each missing variable.

## Configuration

`app/core/config.py` is a single `Settings` class (pydantic-settings). All configuration
comes from environment variables and is validated at startup (twelve-factor).

## Errors and envelope

Typed errors in `app/core/errors.py` carry a stable code. The central exception handler in
`app/main.py` maps them to the response envelope and never leaks stack traces or secrets.
