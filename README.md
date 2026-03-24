# Quantastica

## What this is

**Quantastica** is a cloud-agnostic financial intelligence platform: ingest and normalize user financial data, compute insights, expose lean APIs, drive optional AI answers from structured context (not RAG-first), and emit lightweight events. A **Vite + React** UI consumes summaries and conversational flows.

---

## Architecture overview

| Module | Role | Location in repo |
|--------|------|------------------|
| **core** | Unified financial snapshot model + insight engine (`generateInsights`-style metrics). | `QuantasticaAPI/app/financial_intelligence/core/` |
| **cloud** | Thin adapters (queue, store, fetch, run, ai) behind one provider switch. | `QuantasticaAPI/app/financial_intelligence/cloud/` |
| **api** | HTTP surface for summaries, insights, and orchestration. | `QuantasticaAPI/app/` (FastAPI) + `financial_intelligence/api/` |
| **ai** | Context-injected prompts (no document RAG in v1). | `QuantasticaAPI/app/financial_intelligence/ai/` + ADK agents under `app/agents/` |
| **events** | Single abstraction: enqueue topic + payload (e.g. `INSIGHT_READY`). | `QuantasticaAPI/app/financial_intelligence/events/` |
| **ui** | Dashboard, charts, insights, chat; proxies API calls. | `QuantasticaUI/` — see [`QuantasticaUI/README.md`](QuantasticaUI/README.md) |

---

## Cloud-agnostic design

- **Flag:** `CLOUD_PROVIDER` — `aws` | `azure` | `gcp` (default `gcp`).
- **Swap:** `financial_intelligence/cloud/index.py` selects the matching module; each implements the same surface (`queue`, `store`, `fetch`, `run`, `ai`). Swap env only — no code forks in business logic.

---

## Project structure

```
Quantastica-Agentic-AI/
├── README.md                 # This file
├── ui/README.md              # Pointer to frontend docs
├── QuantasticaAPI/           # FastAPI backend + intelligence core + ADK agents
│   ├── app/
│   │   ├── main.py
│   │   ├── financial_intelligence/
│   │   │   ├── core/
│   │   │   ├── cloud/
│   │   │   ├── api/
│   │   │   ├── ai/
│   │   │   ├── events/
│   │   │   └── ingestion/
│   │   ├── agents/
│   │   └── routes/
│   ├── requirements.txt
│   └── .env.example
├── packages/types/           # SSOT: contract version + TS types + Zod (see packages/types/README.md)
├── scripts/
│   └── check-contract-sync.mjs
├── QuantasticaUI/            # Vite + React SPA
│   ├── src/
│   ├── package.json
│   └── README.md
└── ...
```

---

## Cross-layer contracts (SSOT)

| Piece | Source |
|-------|--------|
| **Contract version** | `packages/types/contracts.json` — Python reads via `app/contracts/version.py` |
| **JSON shapes** | `@quantastica/types` (Zod parse on UI; Pydantic `CamelModel` on API) |
| **Feature flags** | `GET /config` — UI bootstraps via `SystemConfigProvider` (no hardcoded flags) |
| **Financial metrics** | Insight engine on API only; UI displays server fields (`summary`, `showRefinanceCta`, etc.) |

**Drift check:** `node scripts/check-contract-sync.mjs` (version alignment).

---

## Prerequisites

| Requirement | Notes |
|-------------|--------|
| **Node.js** | 20+ (matches Vite 7 / current toolchain) |
| **npm** | Used for `QuantasticaUI` |
| **Python** | 3.11+ recommended for `QuantasticaAPI` |
| **pip** | Install backend deps from `requirements.txt` |

---

## Setup (full system)

```bash
git clone <repository-url> Quantastica-Agentic-AI
cd Quantastica-Agentic-AI

# Backend
cd QuantasticaAPI
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # fill GCP / optional keys

# Frontend
cd ../QuantasticaUI
npm install
```

---

## Running services

Run **two terminals** (API first if the UI calls the backend).

**Backend (FastAPI)**

```bash
cd QuantasticaAPI
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (Vite)**

```bash
cd QuantasticaUI
npm run dev
```

- API default: `http://localhost:8000`
- UI dev server: `http://localhost:5173` (Vite default)
- The UI proxies `/api/*` → `http://localhost:8000` (see `QuantasticaUI/vite.config.ts`). Prefer `fetch('/api/...')` in dev to avoid CORS.

There is **no** root `npm run dev:api` / `dev:ui` script today; use the commands above or add your own orchestration.

---

## Environment variables

**Backend (`QuantasticaAPI/.env`) — examples**

```env
# Intelligence layer
CLOUD_PROVIDER=gcp

# Financial intelligence API (JWT + optional encryption)
FI_JWT_SECRET=change-me-in-production
FI_JWT_ALGORITHM=HS256
FI_ENCRYPTION_KEY=          # optional Fernet key for snapshot at rest

# GCP / ADK (agents)
GCP_PROJECT=
GCP_REGION=us-central1
# ... see .env.example for full list
```

**Frontend — optional**

```env
VITE_API_URL=http://localhost:8000
```

If unset, use relative `/api` in dev (proxy) or set explicitly for production builds.

---

## AI layer

- **No RAG in v1** for core Q&A: pass **structured snapshots** and questions into `cloud.ai(...)` / ADK agents.
- **Add RAG** when you introduce documents (PDFs, statements, research corpora) or long conversational memory — not required for basic dashboard + insights.

---

## Event flow (simple)

1. **Ingest** → normalize to a snapshot  
2. **Store** → `user:{id}:snapshot`  
3. **Insights** → computed metrics  
4. **Event** → e.g. `INSIGHT_READY` via `cloud.queue(...)`  
5. **API / UI** → read summaries and chat with context  

---

## Deployment (high level)

| Piece | Approach |
|-------|----------|
| **UI** | Static hosting (S3, GCS + CDN, Firebase Hosting, Netlify, etc.) — `npm run build` in `QuantasticaUI` |
| **API** | Container (Cloud Run, ECS, AKS) or PaaS; set `CLOUD_PROVIDER` and secrets per environment |
| **Cloud adapters** | Same code path; only env and IAM differ per provider |

---

## Scripts

### QuantasticaAPI

| Command | Purpose |
|---------|---------|
| `uvicorn app.main:app --reload --port 8000` | Dev server |
| *(add your own)* `pytest` | Tests if/when added |

### QuantasticaUI

| Script | Purpose |
|--------|---------|
| `npm run dev` | Vite dev server |
| `npm run build` | Production build |
| `npm run preview` | Preview production build |
| `npm run lint` | ESLint |

---

## Roadmap / TODO

- Streaming ingestion  
- RAG for documents and long-term memory  
- Threshold-based real-time alerts  
- Richer risk / portfolio optimization models  
- Skeleton loaders, error states, and a11y hardening on UI  

---

## License / support

See repository defaults. For UI-only docs: **[`QuantasticaUI/README.md`](QuantasticaUI/README.md)**.
