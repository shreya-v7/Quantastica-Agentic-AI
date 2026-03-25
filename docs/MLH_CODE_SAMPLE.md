# Code sample: Quantastica

**Repo link:** paste your public GitHub URL here when you publish. You can link the repo root or this file directly.

---

## What it does

I built Quantastica for Google Agentic AI Day. It is a full stack financial intelligence app. The backend is FastAPI. It takes user prompts, keeps sessions, and sends traffic to Google ADK agents through one runner. Responses can come back normally or as an SSE stream if streaming is on. The frontend is React and Vite. It has dashboards, a few analysis flows, and an assistant UI with a dock so chat stays on the same screen. The code is spread across real files: API wiring in `main.py` and `routes/prompt.py`, the runner and agent registry under `apps/server/app`, and the client under `apps/web`. I am not submitting a single function or a notebook. It is meant to be something you can run locally from the README and talk about like a small product.

## What I learned

I had to think about sessions end to end: how `app_name`, user id, and session id line up when someone sends a message. The runner can run agents in process for local work or proxy out to separate services, and I had to understand why that split exists. On the UI side I got more comfortable with a monorepo, shared TypeScript types, lazy loading heavy pieces, and keeping layout and auth sane while the backend changed. Nothing fancy on paper, but wiring agents, HTTP, and a usable frontend together taught me more than reading docs alone. Env vars, CORS, and actually documenting how to start the API and the web app mattered if I wanted anyone else to run it.

---

## Where to look first

If you only have a few minutes, I would read in this order: `apps/server/app/main.py`, then `apps/server/app/routes/prompt.py`, then `apps/server/app/runner.py`, then `apps/server/app/agents/__init__.py`. For the client, `apps/web/src/app/layout.tsx`, `ChatDock.tsx`, and `ChatInterface.tsx` show how the shell and assistant work. Root `README.md` explains install and run commands. Optional: `apps/server/app/financial_intelligence/` and `packages/types/` if you want more depth.

---

## Notes for me in an interview

I can walk through how sessions attach to prompts, why streaming uses SSE, and what I would add next (tests, stricter API auth, rate limits). If other people contributed to the repo, I will say clearly what I wrote versus what I did not.
