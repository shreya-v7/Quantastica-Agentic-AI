# MLH Fellowship — code sample (Quantastica)

Use this document when you submit your application and share a link with reviewers. Replace the placeholder **repository URL** below once the repo is public.

---

## Public repository link

**Doc / repo URL (paste in MLH form):**  
`https://github.com/<your-username>/<your-repo>`  

*(Update this line after you publish. If you prefer, link directly to this file on GitHub:  
`https://github.com/<your-username>/<your-repo>/blob/main/docs/MLH_CODE_SAMPLE.md`)*

---

## Application blurbs (copy-paste)

### What the code sample does (one paragraph)

**Quantastica** is a full-stack financial intelligence app I worked on around **Google Agentic AI Day**: a **FastAPI** backend exposes session-aware HTTP APIs that route user prompts to **Google ADK** agents via a unified runner (sync or SSE streaming), while a **React + Vite** SPA provides dashboards, analysis views, and an in-app assistant experience. The sample spans multiple files—API wiring (`main.py`, `routes/prompt.py`), agent orchestration (`runner.py`, agent registry), and client UI—so it represents a **real, deployable product surface**, not a single algorithm or notebook.

### What I learned (one paragraph)

Building this taught me how to **integrate LLM agents into a production-shaped stack**: designing request/session flows, mapping many agent “apps” to one runner and registry, and choosing between **in-process** versus **proxied** agent execution for local dev versus scale-out. On the frontend, I learned to structure a **monorepo** with shared TypeScript contracts, lazy-loaded UI, and UX that stays usable (layout, chat dock, auth-aware routes) while the backend evolves—plus practical lessons in **env/config**, CORS, and shipping something reviewers can run from the README.

---

## What reviewers should look at (file map)

Read in this order for a coherent story (~15 minutes):

| Area | Path |
|------|------|
| API entry, routers | `apps/server/app/main.py` |
| Prompt + session + streaming | `apps/server/app/routes/prompt.py` |
| ADK runner, sessions, modes | `apps/server/app/runner.py` |
| Agent registry | `apps/server/app/agents/__init__.py` |
| Web app shell + chat dock | `apps/web/src/app/layout.tsx`, `apps/web/src/components/ChatDock.tsx`, `apps/web/src/components/ChatInterface.tsx` |
| Repo layout & how to run | `README.md` |

Optional deeper dive: `apps/server/app/financial_intelligence/`, `packages/types/`.

---

## Interview talking points (short)

- **Sessions:** how `app_name`, `user_id`, and `session_id` tie prompts to a conversation.
- **Runner:** `in_process` vs microservice-style proxy—tradeoffs for dev vs deployment.
- **Streaming:** why SSE for `streaming=True` on `/prompt/ask`-style routes.
- **Frontend:** lazy loading, docked chat vs full-page routes, auth bypass only in dev (`/dev/session`).
- **Next steps:** tests, API auth, rate limits, observability—shows maturity.

---

## Honesty

If teammates contributed large parts of the repo, say what **you** owned in your MLH application (e.g. backend runner + API, or UI + dock). Accurate attribution matters.

---

## Requirements checklist (MLH)

| Requirement | How this repo meets it |
|-------------|-------------------------|
| Representative / real problem | Financial AI assistant + dashboards—not a toy BST or course boilerplate. |
| Existing sample | Built for the hackathon / product, not only for MLH. |
| Public on GitHub | *You* make the repo public and paste the URL above. |
| Multiple files | Backend + frontend + shared types—substantive. |
| Not a huge mono-repo of unrelated services | Single API app + single SPA + shared `packages/types` (documented in root `README.md`). |
| Deployable / end-user | README: install, run API + web; production notes for build/deploy. |
| No Jupyter | Application code only. |
| Languages | **TypeScript** (web), **Python** (server)—aligned with MLH tracks. |

---

*Last updated: fill in your GitHub URL when you publish.*
