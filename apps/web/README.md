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

`public/test_data_dir/3333333333/` — minimal JSON bundle used by **Trade execution** for local charts. Full multi-user fixtures live under `apps/server/test_data_dir/` for the API.

## Env

Optional `VITE_API_URL` for production. Feature flags and cloud provider come from **`GET /config`** (`src/providers/SystemConfigProvider.tsx`), not hardcoded env in the UI.

## Build

```bash
npm run build
```

Output: `dist/` (static hosting).
