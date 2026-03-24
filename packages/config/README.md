# `@quantastica/config`

Shared TypeScript: **`CloudProvider`** and **`CONFIG`** (reads `process.env.CLOUD_PROVIDER` when present).

Runtime UI flags still come from **`GET /config`** on the API. Python uses env vars directly in `apps/server`.
