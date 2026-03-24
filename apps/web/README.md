# Quantastica Web (`apps/web`)

Vite + React client. Workspace: **`@quantastica/web`**.

## Setup

From **repository root**:

```bash
npm install
npm run dev:web
```

Or from this folder (after root `npm install`):

```bash
npm run dev
```

## URLs

| Env | URL |
|-----|-----|
| Dev | http://localhost:5173 |
| API (typical) | http://localhost:8000 |

### Dev-only: dummy session (no Firebase)

In **`npm run dev`** only, open:

**http://localhost:5173/dev/session**

That sets `localStorage.userId` to a stable dummy id and redirects to `/dashboard`. It does **not** work in production builds: `import.meta.env.PROD` routes `/dev/session` to `/` and never sets the dummy user.

In **production**, signed-in routes require Firebase login via `/auth` (`RequireAuth` checks `userId` in `localStorage`).

For **dev vs prod commands** and **which credentials to use in dev** (Firebase vs dummy session vs `apps/server/.env`), see the root **[README.md](../README.md#development-vs-production)**.

## Source layout

| Path | Role |
|------|------|
| `src/app/` | Router + shell layout |
| `src/features/` | Dashboard, insights, chat |
| `src/components/` | Shared UI + legacy feature screens |
| `src/lib/` | API helpers (`api.ts`, `apiUrl.ts`) |
| `src/providers/` | `SystemConfigProvider` (bootstraps `/config`) |
| `src/store/` | Client state (e.g. theme) |
| `src/styles/` | Extra CSS (`fi-globals.css`) |

## Static demo data

`public/test_data_dir/3333333333/`  - minimal JSON bundle used by **Trade execution** for local charts. Full multi-user fixtures live under `apps/server/test_data_dir/` for the API.

## Env

Optional `VITE_API_URL` for production. Feature flags and cloud provider come from **`GET /config`** (`src/providers/SystemConfigProvider.tsx`), not hardcoded env in the UI.

## Build

```bash
npm run build
```

Output: `dist/` (static hosting).
