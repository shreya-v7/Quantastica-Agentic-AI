# Phase 1: bitemporal event-sourced book

Status: implemented behind the Phase 0 kernel gate. Reconstruction is a pure
function in `quantastica_kernel.temporal`. Postgres stores the append-only log.

## Model

`book_events` is the system of record. Each row has:

- `valid_time`: when the fact holds in the world. Backdated AIS/CAS corrections
  use this axis.
- `recorded_time`: immutable transaction time. It is monotonic per household and
  is never rewritten. A trigger rejects updates, deletes, and clock regression.

Household and lot rows carry the same two timestamps as a cache of the latest
reconstructed state. They are not a second history. As-of queries always fold
the event log.

Allowed event types are `book.snapshot` (initial known state) and `book.patch`
(named field changes, including `lot_quantities`). Unknown types fail closed.

The outbox row is written in the same transaction as the event.

## Queries

`GET /api/desk/households/{id}/as-of?valid_time=&recorded_time=` reconstructs
that pair. Naive datetimes are rejected. A query before the first known
`valid_time` returns no book rather than a guess.

`GET /api/desk/households/{id}/history` returns the immutable log.

## Determinism seam

`BookRepository` takes a clock callable. Tests inject
`quantastica_kernel.sim.SimulatedClock`. Wall clocks stay out of the kernel.
Network and disk are still at the application edge; a full simulator is Phase 13.

## Limits

History before the bitemporal migration is unknown. The migration writes one
baseline snapshot of whatever current rows exist. That is not a reconstructed
pre-migration past.

`ais_mismatch` remains an empty rule. Entity time axes are stored; AIS facts are
not yet a first-class event type.

Cross-platform clock resolution depends on Postgres timestamptz. The application
also bumps `recorded_time` by one microsecond when a frozen clock repeats.
