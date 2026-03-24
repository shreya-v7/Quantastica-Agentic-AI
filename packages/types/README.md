# `@quantastica/types`

**Single source of truth** for API JSON shapes, feature-flag schema, and contract `version`.

| Artifact | Role |
|----------|------|
| `contracts.json` | Canonical semver — Python reads this via `app/contracts/version.py` |
| `src/*.ts` | TypeScript types + Zod parsers for the UI |
| `dist/` | Build output consumed by `QuantasticaUI` |

Bump **`contracts.json`** and **`package.json` version** together; update FastAPI `read_contract_version()` consumers and redeploy UI + API together on mismatch.

```bash
npm install
npm run build
```
