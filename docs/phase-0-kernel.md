# Phase 0: kernel boundary and offline proof desk

Status: implemented. Isolated golden-vector and replay checks live in
`kernel_tests/` and the `kernel-phase-0` GitHub Actions job. That job installs
only `quantastica_kernel` and must not import `app`. Application-boundary checks
(demo tiers, re-export identity) live in `tests/test_kernel_compat.py`.

Phase 1 (bitemporal book) and Phase 2 (incremental recompute) follow this gate.
See [phase-1-bitemporal.md](phase-1-bitemporal.md) and
[phase-2-recompute.md](phase-2-recompute.md).

## Boundary

`apps/server/quantastica_kernel` is an independently packaged Python library whose
only runtime dependency is Pydantic. It owns the existing tax, capital gains, SIP,
step-up SIP, EMI, affordability, Monte Carlo, snapshot models, and exception rules.
Application modules re-export those implementations to preserve existing callers.
The LangGraph graphs, MCP server and golden_india suite remain in place.

`quantastica_kernel.api.calculate(calculator_id, inputs, version)` returns JSON
containing calculator identity, version, normalized inputs including defaults,
outputs and a SHA-256 content hash. `replay(receipt)` recomputes and compares the
entire receipt, rejecting unknown versions, changed inputs, outputs or hashes.
No wall clock, network, database or external RNG state participates in computation.
Monte Carlo defaults to seed 0 and rejects an explicit null seed. Existing callers
therefore become repeatable without requiring an API contract change.

Receipts are returned to the caller for storage. Phase 0 does not add persistent
receipt storage to existing application routes. The offline demo exposes full
receipts for inspection. Durable storage and temporal state belong to Phase 1.
A content hash establishes consistency, not a signature or proof of source truth.

The version identifies the preserved AY 2025-26 implementation. This extraction
is not a tax-law update or an audit of its legal completeness. Float formulas
remain unchanged; scalar monetary outputs at the receipt interface round to paisa.
Cross-platform byte determinism of floating-point Monte Carlo is not claimed.
Historical replay after changing an implementation will require retaining that
version's implementation; unknown versions fail closed today.

## Offline demo

After dependencies are installed, `make demo` serves a local proof desk at
http://127.0.0.1:8010. It uses the existing Mehta/Rao fixtures, mock VLM and mock
STT/TTS. No database, Redis, model credentials, external fonts or network calls
are needed at runtime. The full React application remains the existing product UI;
this small desk demonstrates the isolated kernel without its infrastructure.
Mock TTS returns a labelled placeholder, not playable speech.

`make demo DEMO_ARGS="--tier medium --seed 42"` selects a generated tier.
Small, medium and large expose 10, 1,000 and 100,000 households respectively,
generated on demand by index with a private RNG. The first two are fixed fixtures;
remaining household quantities depend on the seed. All are synthetic.
The frozen book date is 2026-09-16. This is not the full messiness/ground-truth
synthetic generator planned for Phase 12.

On this machine `/usr/bin/make` is blocked by an unaccepted Xcode license. The
same demo runs directly with:

```sh
cd apps/server
.venv/bin/python -m app.offline_demo
```

## Verification and remaining gates

`make kernel-check` runs exact golden vectors, tamper rejection, fresh-process
replay, boundary checks, seed/tier checks and mock-provider smoke checks. The
standalone CI job installs only the kernel and verifies import outside the app.
The existing backend integration job remains responsible for database regressions.

The fifth rule, `ais_mismatch`, was already a stub and remains a stub. Golden
coverage includes its empty behavior, not a functioning AIS reconciler. The
remaining four rules and the calculators are preserved and regression tested.
A green suite proves the tested vectors; it does not establish universal financial
correctness or the later-phase evaluation targets.

The new roadmap targets GCP asia-south1 with local and AWS portability. Older
cloud design documents describe the previous AWS-first implementation and are not
changed into claims of completed GCP provisioning. Cloud, compliance and market
claims in the supplied dossier have not been independently verified in Phase 0.
