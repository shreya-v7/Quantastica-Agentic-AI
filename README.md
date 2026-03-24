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
- **npm 7+** (workspaces; run `npm install` from the repo root)

---

## Run the app (local)

**1. Install the UI workspace and build shared types**

```bash
cd /path/to/Quantastica-Agentic-AI
npm install
```

(`postinstall` runs `npm run build:types` so `@quantastica/types` is ready for the web app.)

**2. Backend  - venv, deps, env**

```bash
cd apps/server
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # edit .env as needed
```

**3. Start API (terminal 1)**

Use the **same Python** you used for `pip` (avoids “no module named fastapi” when a global `uvicorn` is on your PATH):

```bash
cd apps/server
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt   # run again if anything failed earlier
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**4. Start UI (terminal 2, from repo root)**

```bash
cd /path/to/Quantastica-Agentic-AI
npm install          # once per clone; builds shared types via postinstall
npm run dev:web
```

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| UI | http://localhost:5173 |

Dev: the UI proxies `/api/*` to the API (`apps/web/vite.config.ts`).

---

## Development vs production

| Topic | **Development** | **Production** |
|-------|-----------------|----------------|
| **UI** | `npm run dev:web` (Vite, hot reload, `import.meta.env.DEV === true`) | `npm run build:web` → deploy the `apps/web/dist/` folder (Firebase Hosting, S3+CDN, etc.) |
| **API** | `python -m uvicorn app.main:app --reload` from `apps/server` | Same app behind gunicorn/Cloud Run/etc., with real `BASE_URL`, secrets, and HTTPS |
| **API URL in the browser** | Defaults to same origin via Vite proxy (`/api` → `localhost:8000`) | Set **`VITE_API_URL`** at build time to your public API origin (no `/api` suffix; see `apps/web/src/lib/apiUrl.ts`) |
| **Auth bypass** | **`/dev/session`** is available on the dev server only (see below) | Disabled: production bundles never set a dummy session from that route |

Preview a production build locally: `npm run build:web` then `npm run preview -w @quantastica/web` (or `vite preview` inside `apps/web`).

---

## Credentials in development

### Web UI: Firebase sign-in (`/auth`)

The client loads Firebase from `apps/web/src/auth/firebase.ts` (normal for client SDKs: that file holds the **public** web config, not admin secrets).

- **Sign up** or **sign in** at **`http://localhost:5173/auth`** with any email/password allowed by your Firebase project (enable Email/Password in Firebase Console → Authentication → Sign-in method).
- Use **test accounts** you create in the [Firebase Console](https://console.firebase.google.com) or via the on-page sign-up flow.

### Web UI: skip login (dev only)

For layout and dashboard work **without** creating a Firebase user:

1. Run the **dev** server: `npm run dev:web`.
2. Open **`http://localhost:5173/dev/session`**.

That sets a dummy `userId` in `localStorage` and redirects to `/dashboard`. It **does not** authenticate with Firebase; it is ignored in production builds (`/dev/session` redirects home).

### Backend: `apps/server/.env`

1. `cp apps/server/.env.example apps/server/.env`
2. Fill variables your features need. For a minimal local API, many entries can stay empty; **GCP / Alpaca / Twilio** are only required when you exercise those integrations.

**API troubleshooting:** If you see `ModuleNotFoundError: No module named 'fastapi'`, your venv is missing deps or a different Python is running `uvicorn`. After `source .venv/bin/activate`, run `python -m pip show fastapi`  - if empty, run `python -m pip install -r requirements.txt` again. Prefer **`python -m uvicorn`** (not bare `uvicorn`) so the server uses the venv’s packages.

**npm `EUNSUPPORTEDPROTOCOL` / `workspace:`:** Install from the **repo root** with **npm 7+** (`npm -v`). Upgrade if needed: `npm install -g npm@10`. The web app links `@quantastica/types` via `file:../../packages/types` so it resolves without the `workspace:*` protocol.

---

## npm scripts (repo root)

| Script | Purpose |
|--------|---------|
| `npm run dev:web` | Vite dev server |
| `npm run build:web` | Production UI build |
| `npm run build:types` | Build `@quantastica/types` |
| `npm run check:contract` | `contracts.json` ↔ `package.json` version (`check-contract-sync.mjs`) |

## Environment

**Server:** `apps/server/.env`  - see `apps/server/.env.example` (`CLOUD_PROVIDER`, GCP, `FI_*`, etc.).

**UI:** optional `VITE_API_URL` for production API origin (no `/api` prefix). Runtime flags come from `GET /config`.

## Contracts

- **Version:** `packages/types/contracts.json` must match `packages/types/package.json` version; run `npm run check:contract` in CI before deploy.
- **Types:** `@quantastica/types`  - Zod on client, Pydantic mirrors on server; also exports `CloudProvider`, `CONFIG`, and the `CloudServices` interface (Python adapters live under `apps/server/app/financial_intelligence/cloud/`).

## Docs

- UI: [`apps/web/README.md`](apps/web/README.md)
- Types: [`packages/types/README.md`](packages/types/README.md)
