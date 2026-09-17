# Quantastica: live Indian household exception control plane

This is the **target** system design (16 Sep 2026), updated the same day for
GCP `asia-south1` as the residency *target* ([ADR 007](adr/007-residency.md)).
The running repo implements phases 0 to 18 as tested local contracts. Terraform
is not applied. CMEK is false. OLAP is JSONL. Google ADK is not a dependency.

Read [product.md](product.md) for GTM. Read [architecture.md](architecture.md) for
the code layout as it exists today. Phase gates: [phases-3-18.md](phases-3-18.md).

**Specialty.** The desk is not a question box. The book changes. Calculators
re-run. A queue of exceptions appears, each with a rupee and a trace. LLM and VLM
classify and narrate. They never emit a tax figure or advice.

## TL;DR

- One cloud: **AWS Mumbai (`ap-south-1`)**. In-country Claude on Bedrock (announced
  3 Aug 2026), RDS Postgres + pgvector, EventBridge, SQS, ECS Fargate. That is the
  cleanest RBI / SEBI / DPDP story for BFSI buyers. Freeze GCP as a production
  target. Keep the LLM factory so local Gemini/Anthropic still works for dev.
- Become distributed without a zoo: replace the in-process Redis-leader worker
  with `book_events`, a transactional outbox, EventBridge/SQS fan-out, and
  idempotent recompute consumers.
- LangGraph parse graph with a **Postgres checkpointer** and `interrupt()` for
  low-confidence human review. The existing six-step portfolio graph stays as the
  **explain** subgraph.
- Build order: (1) exception engine + desk home on a unified book, (2) branching
  parse graph plus one VLM fixture, (3) audio STT/TTS. Rupee math stays
  deterministic.

Out of scope: Account Aggregator, live Kite, WhatsApp-as-product, paper trades,
loan marketplace, dual-cloud, fine-tuning, PuppyGraph, SingleStore, Airflow,
MLflow, W&B.

## ADR-1: Cloud platform

**Context.** One vertical slice, B2B BFSI buyers in India, need Claude plus
multimodal, Hinglish STT/TTS, durable events, and India data residency.

**Options.** (A) AWS Mumbai. (B) GCP Mumbai / `asia-south1`. (C) Azure India.

**Decision.** AWS, `ap-south-1`.

Claude inference in India via Bedrock is the deciding fact. GCP has in-country
Gemini, not Claude. Azure Foundry Claude Data Zone is US-only, and Microsoft
startup credits will not pay for Claude. Indian bank references around the
Bedrock launch (Axis, NPCI, IndusInd, Kotak) match the buyer.

**Consequences.** Vendor concentration on AWS. Mitigate by keeping
`LLMClient` behind the factory. Sarvam is off-AWS for speech and is
India-resident. If a bank mandates GCP, re-evaluate; do not dual-run.

Confirm in-console that in-country Claude is GA for the account before production
traffic. The 3 Aug 2026 announcement said "coming weeks."

Local `PLATFORM=local` is unchanged (Anthropic or Gemini keys).

## ADR-2: Agent runtime

**Context.** Branching ingest with a human pause. Existing linear portfolio graph
to reuse.

**Decision.** LangGraph with `PostgresSaver` for the agent graph, on ECS Fargate
at first. AgentCore Gateway fronts MCP tools later. Step Functions and
EventBridge own fan-out recompute, not LLM reasoning. No LangChain rewrite of
`chat_service`. LangChain may appear later only as multimodal message types in
the ingest node.

**Consequences.** `interrupt()` plus a Postgres checkpointer is the low-confidence
parse pattern. Never `MemorySaver` in anything that can restart. AgentCore
Evaluations/Policy in Mumbai is ambiguous; do not depend on them until the
console agrees. Core AgentCore (Runtime, Gateway, Identity, Memory) is the later
host, not Phase 1.

## ADR-3: Document extraction

**Context.** Mixed Indian docs: fixed (Form 16, contract notes) and novel (AIS
photos).

**Decision.** Route by kind.

1. CAS PDF: `casparser` first (typed `CASData` / `NSDLCASData`, Decimal, 112A
   grandfathering). No VLM unless parse fails.
2. Form 16 / AIS screenshot / contract note: Textract or Bedrock Data Automation
   for OCR, Claude VLM for schema mapping.
3. Novel layouts: Claude VLM direct.

All outputs are Pydantic. VLM is forbidden from emitting tax due or advice.
Unreadable fields are `missing`, not guessed. Store source image, JSON, exception
diffs. Every extracted amount carries a source quote and offset; reject
unsupported scalars.

## Speech

Sarvam (Saaras STT, Bulbul TTS) is the India path: Hinglish at the model, data
processed in India. Amazon Transcribe/Polly (`en-IN`, `hi-IN`) is the in-cloud
fallback. Transcribe has no unified Hinglish model; do not pretend it does.

Speech never creates a number. STT is a text event through the same parse.

## Target components

```
typed / PDF / image / audio
        │
        ▼
 FastAPI  /api/ingest
        │
        ▼
 LangGraph parse   ingest → parse → apply_to_book → recompute → exceptions → explain?
        │                 interrupt() on low confidence → desk review → Command(resume)
        ▼
 Postgres          book_events + outbox  (one transaction)
        │
        ▼
 EventBridge / SQS household.recompute
        │
        ▼
 Recompute consumer   risk + four exceptions, diff vs prior set
        │
        ▼
 Desk home queue      row → trace; mic and file drop → /api/ingest
```

- **API:** existing chat/agents plus exception queue, ingest, resume-interrupt.
- **Book:** one household state. Northstar mock holdings merge into the same
  tables calculators and risk read.
- **Ingest workers (Fargate):** text, CAS, image, audio. Write `ingest_artifacts`,
  append `book_events`.
- **Exception engine:** regime watch, lot clock, concentration tripwire, deduction
  headroom. Code only.
- **LLM:** Bedrock Claude in Mumbai in prod. Factory unchanged for local.
- **Embeddings:** Voyage when keyed; retrieve still skips if missing.

Redis stays for cache and the price-alert poller until that poller is retired.
Redis Streams that nothing consumes stay frozen.

## Data model

- `book_events(event_id, household_id, event_type, payload jsonb, source_artifact_id, created_at, seq)` append-only.
- `ingest_artifacts(artifact_id, household_id, kind, source_uri, extracted_json jsonb, confidence, status, created_at)`.
- `outbox(id, aggregate_type, aggregate_id, event_type, payload jsonb, status, created_at)`.
- `processed_events(consumer, event_id, processed_at)` PK `(consumer, event_id)`.
- `exceptions(exception_id, household_id, type, title, rupee_delta, metric_ids jsonb, trace_id, status, computed_at)`.
- `traces(trace_id, household_id, graph, steps jsonb, metric_snapshot jsonb, created_at)`.
- LangGraph checkpoints via `PostgresSaver` tables.

Relay: `FOR UPDATE SKIP LOCKED` on outbox so multiple relays can run. Consumers
are idempotent. At-least-once delivery, exactly-once observable effects.

## Exception definitions (deterministic)

- **Regime watch.** Old vs new on this income and these deductions. Fire when the
  cheaper regime or the saving flips. Rupee delta from `compare_regimes`.
- **Lot clock.** Days to the 12-month LTCG boundary. Cost of selling now (STCG
  20% under 111A) vs after (LTCG 12.5% under 112A above Rs 1.25 lakh),
  grandfathering lot by lot via `capital_gains.py`.
- **Concentration tripwire.** HHI, top-5, single name over 15%, sector over 40%
  against a small policy table.
- **Deduction headroom.** Remaining 80C (Rs 1.5 lakh) and 80CCD(1B) (Rs 50,000)
  under old regime. Suppress when new regime is the live choice.

Carry both 1961 Act and Income-tax Act 2025 section labels (80C/123, 80CCD/124,
80D/126, 87A/156). FY 2025-26 math stays on 1961-Act rules until filing year
changes. Confirm rates against CBDT before shipping calculator edits. This file
is not tax advice.

## Feasibility vs the repo today

| Capability | Status |
|---|---|
| Calculators, MCP, Postgres + pgvector, hybrid RAG | Exists |
| Linear LangGraph explain pipeline | Exists; reuse as subgraph |
| Unify Northstar into household state | Small |
| Four exceptions + desk-home queue | Phase 1 core |
| Outbox + EventBridge + idempotent consumer | Phase 1 (local: outbox + in-process relay) |
| Parse graph + PostgresSaver + interrupt | Phase 2 |
| casparser CAS | Phase 2 small |
| One VLM fixture, Pydantic, grounding | Phase 2 |
| Sarvam STT/TTS | Phase 3 |
| AA, Kite, WhatsApp product, paper, match, dual-cloud | Out of scope |

Local Phase 1 does **not** require AWS. Outbox table plus a local relay that
calls the recompute function is the same pattern. EventBridge is the prod bus.

## Phased rollout

**Phase 1.** Unify the book. Four exceptions with fixture-book exact-set tests.
Desk home is the queue; row opens the existing `AgentTrace`. Outbox + one
recompute consumer. Hide Match, Trades, Automation from primary nav. No LLM
changes. No VLM. No audio.

**Phase 2.** Branching parse graph, `PostgresSaver`, `interrupt()`. casparser for
CAS. One Form 16 VLM fixture. Mock the VLM in CI.

**Phase 3.** Sarvam STT/TTS. Speech is a text event. Mock STT/TTS in CI.

**Phase 4.** Feature-flagged paper trading + WhatsApp on the same intent pipeline.
Compliance write-up in docs/compliance/trading.md.

**Phase 5.** Firm RBAC, DPDP masking and consents, runbooks for outbox/DLQ.

**Phase 6.** Metrics page and `/demo` scripted run.


## Guardrails

- Pydantic with `ge`/`le` and enums. Validate-and-retry. Structured fallback, not
  a raw model dump.
- Numeric grounding on every extracted amount.
- Prompts and schemas forbid tax-due and advice fields.
- `golden_india.json` still must match calculator output. Add fixture-book
  exception-set cases. FinanceBench sample stays in pytest.

## Failure modes

| Failure | Response |
|---|---|
| Duplicate events | `processed_events` |
| Lost events | Outbox in the same transaction |
| Low parse confidence | `interrupt()`, no silent guess |
| VLM invented a rupee | Schema reject + grounding |
| Deploy mid-pause | Version graph state; retain paused runs |
| Consumer crash | SQS redelivery, idempotent recompute |

## Cost and credits (indicative)

AWS Activate 2026: Founders ~1k USD, Portfolio up to 100k via a provider Org ID,
a gen-AI tier up to 300k. Claude on Bedrock is payable with AWS credits. Confirm
on official pages; credit programs change.

## Caveats

- Bedrock AgentCore Evaluations/Policy in Mumbai: docs disagree. Verify in
  console. Do not block Phase 1 on AgentCore.
- App Runner is Mumbai-only; ECS Fargate is in Mumbai and Hyderabad. Prefer
  Fargate.
- Tax figures are FY 2025-26 / AY 2026-27 as reported by tax portals and the
  CBDT budget FAQ. Confirm before calculator changes.
- Sarvam accuracy on this desk's Hinglish is unproven until we record fixtures.
- Account Aggregator is a regulated-entity program (FIU, Sahamati, months and
  lakhs), not a feature.
