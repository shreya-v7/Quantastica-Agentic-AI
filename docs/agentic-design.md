# Agentic design

The Orchestrator (`app/agents/orchestrator.py`) runs a LangGraph state graph and persists
an `AgentRun` with a per-step trace (name, input summary, output summary, duration, status,
and error if any). A step failure marks the run failed with a clear error. There is no
fake success.

Target design ([system-design.md](system-design.md)): this six-step graph is the
**explain** subgraph. A second graph (ingest) routes Form 16 / AIS / CAS / text,
validates Pydantic extracts, and pauses on low confidence. `QuantasticaTeam`
wraps that ingest graph as Sequential(classifier) / Parallel(extractors) /
Loop(verify, max 2). Google ADK is not imported.

## Pipeline

1. **Planner** (one LLM call). Input: the user query plus a portfolio summary. Output: a
   strict JSON plan validated against a Pydantic schema. On invalid JSON it retries once
   with the validation error in the prompt, then fails.
2. **Researcher** (pure code, no LLM). Pulls holdings and transactions from the repository
   and computes total value, per holding weights, sector and asset class allocation, top
   positions, and cost basis vs current value.
3. **Retrieve** (hybrid RAG, no LLM). LlamaIndex sentence chunks, dense pgvector search plus
   Postgres BM25, fused with reciprocal rank fusion. Missing embeddings skip the step.
   Passages are attached to context so later nodes can cite them.
4. **Risk** (pure code, deterministic, unit tested). Computes the Herfindahl-Hirschman
   index, top 5 weight share, sector concentration, a diversification score, and a simple
   volatility proxy from transaction history. Each metric returns value, threshold, and a
   low/medium/high rating.
5. **Insight** (one LLM call). Input: the researcher and risk outputs as structured JSON,
   plus retrieved passages. Output: a strict JSON list of findings, each with title, body,
   severity, confidence, and the metric ids that support it. Same validate, retry, fail
   rule. Findings are persisted, and metric ids that do not exist are dropped so every
   finding cites real computed metrics.
6. **Summarizer** (one LLM call). Produces the final plain language answer, grounded in
   the findings and retrieved passages. Stored on the run.

LangGraph is control flow only. The money path is not checkpointed through the graph.
MCP (`python -m app.mcp`) exposes the same tax, SIP, and affordability calculators to
Cursor and Claude Desktop.

## Events

The orchestrator publishes `run.started`, `run.step_completed`, and
`run.completed` or `run.failed` through the events interface.

## Storage

A completed run can be exported as a JSON report through the storage interface
(`POST /api/agents/runs/{id}/export`), which returns the location of the report.

## LLM rules

Prompts live in `app/agents/prompts.py`. JSON outputs use temperature 0. Max retries is 1.
Every call is logged with token counts. The interface is
`complete(system, user, json_schema=None) -> str | dict`: it returns prose as a string and
a parsed object when a JSON schema is supplied.

Local `PLATFORM=local` accepts `ANTHROPIC_API_KEY` or `GEMINI_API_KEY`. GCP still uses
Vertex with ADC. Never commit keys.

## Grounding

Because the Researcher and Risk agents are pure code over the repository data, the answer
is grounded: every insight cites real computed metrics, and changing the seed data changes
the answer. Retrieval citations are document ids. CI runs `evals/golden_india.json` against
the calculators and a FinanceBench sample against hybrid retrieval.
