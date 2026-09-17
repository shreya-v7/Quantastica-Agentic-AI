# Quantastica

**What this is.** A live Indian household finance exception control plane.
The book changes. Calculators re-run. A queue of exceptions appears, each with a
rupee and a trace. The language model classifies and writes. It does not invent
a number.

**What this is not.** Not a SEBI-registered investment adviser. Not a robo that picks
stocks. Not a consumer app that will get paid by the median SIP investor. The
disclaimer on the site is there because the law requires it. If a bank deploys this,
the bank is the regulated party. Quantastica is decision support sitting under their
licence, not a replacement for it.

Read this file first. Target system design is [system-design.md](system-design.md).
Code layout today is [architecture.md](architecture.md). The agent pipeline is in
[agentic-design.md](agentic-design.md).

## The business, without glaze

Two buyers. One stack.

| Motion | Who | What they buy | Who is liable |
|---|---|---|---|
| **B2B (primary)** | Private banks, wealth RMs, NBFCs, family-office platforms | A deployable module in their VPC. RM copilot. Pre-meeting brief. Tax / concentration / SIP math with an audit trace | The bank, under its existing wealth / advisory licence |
| **B2C (secondary)** | HNIs and family offices | A second-opinion desk on *their* book. Optimize tax regime, SIP top-up, concentration, statement questions | We stay informational unless we become an RIA. Most HNIs will not pay a serious fee for a disclaimed chatbot |

Middle-income households are a **segment we can serve in the UI**, not a **buyer of
this cost structure**. Tax regime comparison and SIP math are free on Groww, ET Money,
ClearTax, and bank apps. An LLM pipeline with Postgres, traces, and a cloud bill cannot
be recovered at Rs 99/month. If we keep a middle-income surface, it is a funnel into
the bank's own app, paid for by the bank, not by the user.

HNIs already have relationship managers. They do not open a new website to "ask their
money a question." They take a call from HDFC Private, Kotak Private, IIFL, or a
family office. The honest HNI product is: make **that RM faster and less wrong**, then
optionally give the client a white-labelled view of the same numbers.

That is the B2B package. Not a foundation model. A **grounded intelligence module**
the bank connects to its core, Account Aggregator, and CAS. Locally we mock the bank
so a demo does not wait on a CBS integration.

## Will this work

**Mass B2C: no.** Unit economics do not close. Acquisition is owned by brokers and
banks. The feature set (tax, SIP, concentration) is already free. This repo is too
expensive to be a consumer app.

**Direct HNI B2C: weak.** Possible as a high-touch second opinion sold through CAs,
family offices, or multi-family offices, not through `/signin`. Trust and data access
are the product. HNIs will not paste a CAS into a startup they found on the internet
and then pay 1% of AUM. A Rs 2–10 lakh/year family-office seat is imaginable if the
desk is boringly correct and private. That is a services-shaped business with software
under it. It does not fund a dual-cloud lab by itself.

**B2B into banks and wealth platforms: the only motion that can pay for this.**
Procurement is slow (12–18 months), security review is real, and they already have
Temenos / Finacle / in-house RM tools / Excel. You do not win by saying "AI." You win
if you can show, in a room with compliance:

1. Numbers come from code. Changing the book changes the answer.
2. Every run has a trace. A bad answer is reconstructible.
3. India tax and concentration are unit-tested, not prompt-wished.
4. Data never leaves the bank VPC.
5. The RM's prep time for a review meeting drops (concentration, old vs new regime,
   SIP to target, CAS exceptions).

Even then, many banks will build a thin wrapper on an LLM vendor and call it a day.
Grounding plus evals is the only differentiator that is not a slide. It is not a
guarantee they will buy.

**Realistic next 12 months:** one mock-bank demo that an RM can run in five minutes
(exception queue on Mehta, not a chat), one design partner, **one cloud (AWS
Mumbai)**, no WhatsApp, no paper trading. If that meeting does not produce a
pilot, the rest of the repo does not matter.

## Is it over-engineered

**Yes, relative to a student demo or a mass consumer app.**

**Partially justified, relative to a bank pitch.**

Keep:

- Deterministic tax / SIP / HHI / FOIR calculators
- Intent classification, then code, then prose
- Persisted step trace
- Golden evals that must match calculator output
- Postgres as the book of record
- A mock bank API that looks like the adapter a real CBS would implement
- MCP so an RM copilot (Cursor, Claude, an internal chat) calls the **same** tools

Cut or freeze until a pilot exists:

- GCP as a production target (factory may still start Vertex in local/dev)
- Redis Streams that nothing consumes
- WhatsApp, live Kite, Account Aggregator client that is not onboarded
- Loan and insurance match as a public nav item
- Paper trading and automation as if we were a broker
- PuppyGraph, SingleStore, Airflow, MLflow, W&B

LangGraph stays. The linear six-step graph is the **explain** subgraph. Branching
is for ingest/parse only (see [system-design.md](system-design.md)).

LangGraph, hybrid RAG, and MCP are not impressive to a CIO by themselves. They are
impressive only when the demo says: "this rupee came from your mock core, this finding
cites a metric id, this tool is the same one Claude just called."

## What the customer actually needs

An HNI or an RM asks things like:

- Is this book too concentrated in one promoter or one sector?
- Old vs new regime on *this* salary and *these* deductions, not a blog example
- What SIP gets this corpus to a named target
- What did this CAS say, in a sentence, with a citation
- What changed since the last review

They do not need a marketplace of personal loans, a kill switch for paper trades, or
a landing page that lists LangGraph.

Data has to come from the institution, not from the user typing holdings:

```
Bank core / wealth API     (production)
Account Aggregator         (India, consent-based, Sahamati)
CAS / CAMS / KFin          (mutual fund statements)
Broker (Kite etc.)         (optional, trading book)
Mock Northstar Private     (this repo, always on, for demos)
```

Yahoo quotes are for market context. They are not the book. The book is the bank.

## Mock bank (what ships in this repo)

A fictional private bank, **Northstar Private**, stands in for a core system. It is
labelled mock in every payload. It is not HDFC, not ICICI, not a scrape.

Two demo customers:

| Id | Segment | Point of the fixture |
|---|---|---|
| `cust_hni_mehta` | HNI / private-bank book | Concentration and tax questions on a real-sized book |
| `cust_affluent_rao` | Mass affluent | The middle-income surface. Cheap to serve in a bank app. Not a B2C buyer of this stack |

HTTP (same envelope as the rest of the API):

- `GET /api/bank/status`
- `GET /api/bank/customers`
- `GET /api/bank/customers/{id}`
- `GET /api/bank/customers/{id}/accounts`
- `GET /api/bank/customers/{id}/holdings`
- `GET /api/bank/customers/{id}/transactions`
- `GET /api/bank/customers/{id}/snapshot`

MCP (`python -m app.mcp`) exposes the same fetchers plus the calculators, so a bank's
internal assistant and the website cannot drift:

- `bank_list_customers`
- `bank_customer_snapshot`
- `bank_holdings`
- `compare_tax_regimes`
- `required_sip`
- `affordability_check`

In a real bank deal, `MockNorthstar` is replaced by one adapter class against their
wealth API. The rest of the desk should not change.

## Packaging for a bank

What we would actually sell:

1. Container in their VPC (or their cloud account). Postgres + the API + the worker.
2. One adapter: `BankCore` with the same methods as the mock.
3. RM UI: exception queue + trace + portfolio, white-labelled. Ask is follow-up.
4. Optional MCP endpoint for their internal copilot.
5. Eval suite they can run in CI against *their* golden cases.
6. A contract: we do not give advice. Their RM / RIA does. We compute and draft.

Price that can exist: per RM seat, or a platform fee, or a thin bps on AUM **only if
they already charge advisory**. Do not invent a 1% AUM consumer fee. We did not earn
that.

## Competitive reality

Helsinki Quantastica is quantum software. Ignore the name collision.

In India: Dezerv, Wealthy, Scripbox, INDmoney, Groww, Zerodha, bank private-banking
apps, Excel. None of them are "wrong." Most of them already own distribution. Our
only non-slide advantage is **refusing to guess a rupee**, with tests. That is a
narrow wedge. Treat it that way.

## What to build next, in order

Phases 1-6 of the Master Build Prompt are in the repo (exception queue, ingest graph,
voice overlay, flagged paper trading, DPDP/RBAC, metrics/demo). Remaining for a bank
pilot: EventBridge/SQS in Mumbai, live Sarvam, Textract, RLS on, legal review of
docs/compliance/trading.md, and a real core adapter only after someone will send traffic.
