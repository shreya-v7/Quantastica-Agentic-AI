# Quantastica UI

## Overview

Vite + React client for **Quantastica**: financial dashboard (metrics + charts), insight highlights, and agent chat. Uses **TanStack Query** for data, **Zustand** for theme, **Tailwind** + **Framer Motion** + **Recharts**. Consumes the FastAPI backend (ADK `/prompt/ask`, financial intelligence routes, optional features).

---

## Setup

```bash
cd QuantasticaUI
npm install    # builds @quantastica/types via postinstall
npm run dev
```

`@quantastica/types` lives in `../packages/types`. If `dist/` is missing, run `npm run build:types`.

---

## Access

| Environment | URL |
|-------------|-----|
| Dev (Vite default) | [http://localhost:5173](http://localhost:5173) |
| API (typical) | `http://localhost:8000` |

Dev proxy: requests to `/api/*` forward to `http://localhost:8000` (see `vite.config.ts`). Prefer `/api/...` from the browser in development.

---

## Design system

| Topic | Details |
|-------|---------|
| **Theme** | Light / dark via `class="dark"` on `<html>`; persisted with Zustand + `localStorage` (`quantastica-ui-theme`). |
| **Palette** | Blue (primary / trust), near-black surfaces in dark mode, white / slate text — see `src/index.css` CSS variables. |
| **Gradients** | Cards and hero accents — subtle; no loud fills. |
| **Typography** | Large tabular numbers for money; muted labels. |

Token reference (TS): `src/lib/theme.ts`.

---

## Structure

```
src/
├── app/
│   ├── router.tsx       # Lazy routes + layout shell
│   └── layout.tsx       # Sidebar, header, theme toggle
├── components/
│   ├── Card.tsx
│   ├── Chart.tsx        # Recharts area + gradient
│   ├── Metric.tsx
│   ├── ToggleTheme.tsx
│   └── …                # Legacy feature components
├── features/
│   ├── dashboard/       # Net worth, chart, debt, AI teaser
│   ├── insights/        # Highlight cards
│   └── chat/            # Lazy-loaded ChatInterface
├── hooks/
├── store/               # Zustand (e.g. uiStore)
├── lib/                 # api helpers, theme tokens, utils
└── styles/              # fi-globals.css (shimmer, surfaces)
```

---

## Env config

Create `.env` / `.env.local` as needed (Vite exposes only `VITE_*`).

```env
# Production / non-proxy: full API origin (paths like /config, not prefixed with /api)
VITE_API_URL=http://localhost:8000
```

**Feature flags** come from `GET /config` at bootstrap (`SystemConfigProvider`, Zod-validated). Do not hardcode `CLOUD_PROVIDER` or feature toggles in the UI.

In **development**, with `VITE_API_URL` unset, the Vite proxy serves `/api/*` → backend (see `vite.config.ts`).

---

## Features

| Area | Route | Notes |
|------|-------|--------|
| **Dashboard** | `/dashboard` | Metrics, Recharts portfolio trend, debt CTA, link to insights |
| **Charts** | (within dashboard) | `Chart.tsx` — area chart, gradient fill, minimal grid |
| **Insights** | `/insights` | Progressive “what matters” cards (demo data via React Query) |
| **Chat** | `/chat` | Agent UI (`ChatInterface`), lazy-loaded |

Legacy routes (news, investments, etc.) remain lazy-loaded in `app/router.tsx`.

---

## Performance

- **Vite** — ESM, fast HMR, production tree-shaking  
- **Lazy routes** — `React.lazy` + `Suspense` per feature  
- **Charts** — `manualChunks.recharts` in `vite.config.ts` to split Recharts  

---

## Scripts

| Command | Purpose |
|---------|---------|
| `npm run dev` | Start dev server |
| `npm run build` | `tsc -b && vite build` |
| `npm run preview` | Serve `dist/` |
| `npm run lint` | ESLint |

---

## TODO

- Skeleton loaders and consistent error boundaries  
- ARIA / keyboard pass on shell + chat  
- Mobile polish (sidebar + header)  
- Chart drill-downs  
- Wire dashboard / insights to live `GET /insights`, `POST /summary` (JWT) when backend auth is integrated  

---

## Monorepo

Backend and intelligence core: repo root [`README.md`](../README.md).
