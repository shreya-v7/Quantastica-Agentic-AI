# Phase 2: incremental recompute

Status: implemented after the bitemporal book. The five exception rules and the
versioned calculators are a DAG keyed by the book fields they read.

## Dirty set

`quantastica_kernel.recompute.plan_recompute` maps a stored event to a plan:

- Quantity, price, symbol, or sector changes dirty `lot_clock`,
  `concentration_tripwire`, `compute_equity_gains`, and `weights`.
- Tax-fact changes dirty `regime_watch`, `deduction_headroom`, and
  `compare_regimes`.
- Household rename dirties nothing.
- Snapshots and unknown event types fail closed and dirty every rule.

Other households are never in the dirty set. Cost is the number of dirty
exception rules, so a lot patch costs 2 whether the book has 10 or 1,000
households. Full recompute of the medium tier would cost 5,000 rule runs.

The desk drain uses the plan: it reruns only dirty rules, merges surviving
hits from the previous run, and writes new versioned calculator outputs.

Manual `POST /recompute` without an event id still runs every rule.

## Benchmark

`tests/test_recompute.py` and `kernel_tests/test_recompute.py` check:

- Incremental hits equal a full run on the same book.
- Medium-tier (1,000 household) cost is the dirty set, not `n * 5`.

This is invocation-count sublinearity. It is not a claim about wall-clock
latency on AlloyDB or about incremental concentration internals: a total-market
change still rescans names and sectors inside that one household.

## Limits

Planning calculators (SIP, EMI, Monte Carlo) sit on the DAG for completeness
but are not scheduled by book events yet. `ais_mismatch` only dirties on AIS
fields, so it stays idle.
