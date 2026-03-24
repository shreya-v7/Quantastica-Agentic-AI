# `@quantastica/types`

**Single source of truth** for API JSON shapes, feature-flag schema, contract `version`, and shared TS config/cloud types.

| Artifact | Role |
|----------|------|
| `contracts.json` | Canonical semver — Python reads this via `app/contracts/version.py` |
| `src/*.ts` | TypeScript types + Zod parsers, `CloudProvider` / `CONFIG`, `CloudServices` interface |
| `dist/` | Build output consumed by `apps/web` (`@quantastica/web`) |

Bump **`contracts.json`** and **`package.json` version** together; update FastAPI `read_contract_version()` consumers and redeploy UI + API together on mismatch.

```bash
npm install
npm run build
```

Drift check from repo root: `npm run check:contract`.
