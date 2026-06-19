# Runbook

On-call reference for the Quantastica platform. Every alert below maps to a Terraform
alert policy in `infra/terraform/alerts.tf`.

## Health and readiness

- `GET /api/health` - process is up.
- `GET /api/ready` - dependencies (Postgres, Redis, providers) are reachable. A 503 here
  is what trips the readiness alert.

## Alerts and first responses

### 5xx error spike
1. Check the latest deploy; if it correlates, roll back traffic to the previous revision.
2. Inspect logs filtered by `level=ERROR`; secrets are redacted, request ids correlate.
3. If a provider is the cause, the circuit breaker should already be returning typed
   `PROVIDER_UNAVAILABLE`; confirm the upstream and let the breaker recover.

### Readiness failing
1. Identify the failing dependency in the `/api/ready` payload.
2. Postgres down: check Cloud SQL status and connections; the pool may be exhausted.
3. Redis down: caching and rate limiting degrade open (fail-open); not user-facing fatal.

### DB CPU saturation
1. Look for slow queries or a missing index; check connection count vs pool size.
2. Scale the Cloud SQL tier or add a read replica if sustained.

### Worker lag / automation volume anomaly
1. Only one worker is leader at a time (Redis lock `quantastica:worker:leader`).
2. If automation firing volume spikes, use the kill switch: `POST /api/trades/kill-switch`
   to disable trading, and the automation master toggle to stop rule execution.
3. Per-user hard caps (notional and executions/day) are enforced server-side and cannot be
   raised from the client.

### LLM spend anomaly
1. `llm.usage` log lines carry model, tokens, and `cost_usd`. Aggregate by day/user.
2. The deterministic response cache (24h) absorbs repeated temperature-0 calls; confirm it
   is healthy (Redis up). A cache outage roughly multiplies spend by the repeat rate.

## Money-path safety

- Live trading and enabling automation require 2FA (TOTP) on the account.
- Manual approval of an order requires fresh auth.
- WhatsApp trade commands are rejected unless the number is OTP-verified.
- Nothing on the money path or auth path is cached.

## Common operations

- Reseed demo data (dev only): `POST /api/seed/reset`.
- Rotate JWT secret: update Secret Manager, then roll the server revision. Existing refresh
  tokens are invalidated; users re-authenticate.
- Disable a user's automation: admin sets `automation_enabled=false` (audit logged).
