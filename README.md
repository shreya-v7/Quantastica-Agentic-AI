# Quantastica

Monorepo: **one FastAPI service** (`apps/server`), **one Vite SPA** (`apps/web`), **one shared TS package** (`packages/types`). No microservices.

## Layout

```
.
├── apps/
│   ├── server/              # Python FastAPI + agents + financial_intelligence
│   └── web/                 # React + Vite UI (@quantastica/web)
├── packages/
│   └── types/               # contracts.json + Zod + CloudProvider/CONFIG + CloudServices type
├── check-contract-sync.mjs  # CI: contract version drift check
├── package.json             # npm workspaces
├── tsconfig.base.json
└── README.md
```

| Area | Path |
|------|------|
| Insight engine, events, FI API | `apps/server/app/financial_intelligence/` |
| ADK agents | `apps/server/app/agents/` |
| HTTP routes | `apps/server/app/routes/` + `main.py` |
| UI | `apps/web/` |
| Contract version | `packages/types/contracts.json` (read by `apps/server/app/contracts/version.py`) |

## Prerequisites

- Node **20+**
- Python **3.11+**
- **npm** (workspaces)

---

## Run the app (local)

**1. Install the UI workspace and build shared types**

```bash
cd /path/to/Quantastica-Agentic-AI
npm install
```

(`postinstall` runs `npm run build:types` so `@quantastica/types` is ready for the web app.)

**2. Backend — venv, deps, env**

```bash
cd apps/server
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # edit .env as needed
```

**3. Start API (terminal 1)**

```bash
cd apps/server
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**4. Start UI (terminal 2, from repo root)**

```bash
npm run dev:web
```

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| UI | http://localhost:5173 |

Dev: the UI proxies `/api/*` to the API (`apps/web/vite.config.ts`).

---

## npm scripts (repo root)

| Script | Purpose |
|--------|---------|
| `npm run dev:web` | Vite dev server |
| `npm run build:web` | Production UI build |
| `npm run build:types` | Build `@quantastica/types` |
| `npm run check:contract` | `contracts.json` ↔ `package.json` version (`check-contract-sync.mjs`) |

## Environment

**Server:** `apps/server/.env` — see `apps/server/.env.example` (`CLOUD_PROVIDER`, GCP, `FI_*`, etc.).

**UI:** optional `VITE_API_URL` for production API origin (no `/api` prefix). Runtime flags come from `GET /config`.

## Contracts

- **Version:** `packages/types/contracts.json` must match `packages/types/package.json` version; run `npm run check:contract` in CI before deploy.
- **Types:** `@quantastica/types` — Zod on client, Pydantic mirrors on server; also exports `CloudProvider`, `CONFIG`, and the `CloudServices` interface (Python adapters live under `apps/server/app/financial_intelligence/cloud/`).

## Docs

- UI: [`apps/web/README.md`](apps/web/README.md)
- Types: [`packages/types/README.md`](packages/types/README.md)
