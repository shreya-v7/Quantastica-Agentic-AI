# Quantastica

Monorepo: **one FastAPI service**, **one Vite SPA**, **shared TypeScript packages**. No microservices.

## Layout

```
.
├── apps/
│   ├── server/          # Python FastAPI + agents + financial_intelligence
│   └── web/               # React + Vite UI
├── packages/
│   ├── config/          # Shared TS: CloudProvider + CONFIG
│   ├── types/           # API contracts + Zod (SSOT: contracts.json)
│   └── cloud/           # CloudServices interface (types-only; impl in server)
├── scripts/                 # Repo scripts (see scripts/README.md)
│   ├── README.md
│   └── check-contract-sync.mjs
├── package.json         # npm workspaces
├── tsconfig.base.json
└── README.md
```

| Area | Path |
|------|------|
| Insight engine, events, FI API | `apps/server/app/financial_intelligence/` |
| ADK agents | `apps/server/app/agents/` |
| HTTP routes | `apps/server/app/routes/` + `main.py` |
| UI | `apps/web/` |
| Contract version | `packages/types/contracts.json` (read by Python `apps/server/app/contracts/version.py`) |

## Prerequisites

- Node **20+**
- Python **3.11+**
- **npm** (workspaces)

## Setup

```bash
git clone <repo-url> Quantastica-Agentic-AI
cd Quantastica-Agentic-AI

# Install JS workspaces (builds packages via postinstall)
npm install

# Backend
cd apps/server
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## Run locally

**Terminal 1 — API**

```bash
cd apps/server
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — UI**

```bash
npm run dev:web
```

- API: `http://localhost:8000`
- UI: `http://localhost:5173` (Vite default)
- Dev: UI proxies `/api/*` → API (`apps/web/vite.config.ts`)

## npm scripts (root)

| Script | Purpose |
|--------|---------|
| `npm run dev:web` | Vite dev server |
| `npm run build:web` | Production UI build |
| `npm run build:packages` | Build config, types, cloud packages |
| `npm run check:contract` | Verify `contracts.json` ↔ `package.json` version (`scripts/check-contract-sync.mjs`) |

## Environment

**Server:** `apps/server/.env` — see `apps/server/.env.example` (`CLOUD_PROVIDER`, GCP, `FI_*`, etc.).

**UI:** optional `VITE_API_URL` for production API origin (no `/api` prefix). Runtime flags come from `GET /config`.

## Contracts

- **Version:** `packages/types/contracts.json` — must match `packages/types/package.json` version; run `npm run check:contract` (see [`scripts/README.md`](scripts/README.md))
- **Types:** `@quantastica/types` (Zod on client, Pydantic mirrors on server)
- **Config:** `@quantastica/config` (`CloudProvider`, `CONFIG`)
- **Cloud (TS):** `@quantastica/cloud` — interface only; Python adapters live under `apps/server/app/financial_intelligence/cloud/`

## Docs

- UI details: [`apps/web/README.md`](apps/web/README.md)
- Types package: [`packages/types/README.md`](packages/types/README.md)
