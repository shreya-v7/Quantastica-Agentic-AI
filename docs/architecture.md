# Architecture

Quantastica is a monorepo with a FastAPI backend, a React frontend, and a shared types
package.

```
apps/server   FastAPI service (routes, services, agents, infra, seed, schemas)
apps/web      React 19 + Vite + Tailwind + TanStack Query
packages/types  contracts.json version and Zod schemas shared with the frontend
```

## Layers

Dependencies point downward only. No layer skipping.

1. **routes** parse HTTP input, call a service, and wrap the result in the response
   envelope. They contain no business logic.
2. **services** hold business logic and are the orchestration entry point. They depend on
   the repository and on the agent orchestrator.
3. **agents** are the Planner, Researcher, Risk, Insight, Summarizer, and the
   Orchestrator that runs them in order and records the trace.
4. **infra** is four small interfaces, each with three real implementations:
   - `repo`: SQLite (local), Firestore (gcp), DynamoDB (aws)
   - `llm`: Anthropic API (local), Vertex AI (gcp), Bedrock (aws)
   - `events`: in-process (local), Pub/Sub (gcp), SQS (aws)
   - `storage`: local disk (local), GCS (gcp), S3 (aws)

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
