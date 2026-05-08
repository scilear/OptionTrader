# PM Handoff - Sprint 7 Validation Findings

Date: 2026-05-08
Owner handoff: Dev -> PM
Sprint: 7 (release-control)

## Executive Outcome

- Sprint 7 validation command completed successfully.
- Final recommendation is `not_promotable`.
- Three gates pass (`walk_forward`, `adversarial`, `ablation_ledger`), and one gate fails
  (`regime_falsification`), which blocks promotion under `S7-CONTRACT-v1` fail-closed policy.

## Canonical Validation Run

Command executed:

```bash
source .venv/bin/activate
python scripts/validate_release.py --config-path config/config-eod-truth.yaml
```

Contract and lineage metadata from payload:

- Contract: `S7-CONTRACT-v1`
- Window: `2010-01-01T00:00:00Z` -> `2023-12-31T23:59:59Z`
- Underlying: `SPX`
- Baseline lineage/run: `3b024c9`, `run_id=23`, `profile=baseline_rv_only`
- Candidate lineage/run: `5128e8e`, `run_id=24`, `profile=candidate_multi_signal`

## Gate Results

- `walk_forward_pass`: `PASS`
  - Deterministic schedule confirmed
  - `split_count=28`
  - `train_size=252`, `test_size=63`, `step_size=63`
- `adversarial_resilience_pass`: `PASS`
  - All scenario selectors passed (`sparse_wings`, `stale_books`, `missing_tenors`,
    `discontinuous_chain_snapshots`)
- `ablation_ledger_pass`: `PASS`
  - `ideas_with_ranking=5`
  - `mean_edge_after_cost=17013.489688957932`
  - `mean_total_friction_cost=17.21802978316799`
  - Component ledger captured (`event` and `stress_proxy` currently ablated in config)
- `regime_falsification_pass`: `FAIL`
  - Precision non-regression is true, but gate still fails on regime/falsification requirements
  - Blocking reasons encoded in payload:
    - `missing_regimes` (required `Calm`, `Transition`, `Stress` not all observed)
    - `transition_fp_density_blocked_reason=missing_transition_alerts`

## What Was Produced

- Release report: `docs/roadmap/OptionTrader_Sprint_7_Release_Validation_Report.md`
- Machine payload: `docs/roadmap/OptionTrader_Sprint_7_Release_Validation_Payload.json`
- Baseline capture: `docs/roadmap/OptionTrader_Sprint_7_Baseline_Capture_v1.json`
- Sprint docs updated:
  - `docs/roadmap/OptionTrader_Sprint_7_Execution_Plan.md`
  - `docs/roadmap/OptionTrader_Sprint_7_Dev_Ticket_Sheet.md`

## Implementation Status (for PM awareness)

- `S7-01`: Done (deterministic walk-forward in `src/core/replay.py`)
- `S7-02`: Done (`scripts/validate_release.py`, payload/report generation, strict exit codes)
- `S7-03`: Done (adversarial scenario tests wired into validator)
- `S7-04`: Partially complete in tooling, blocked in evidence (insufficient observed regime spread)
- `S7-05`: Done (final report + recommendation artifact generated)
- `S7-06`: In progress (process wrapper present: `scripts/run_release_gate.sh`)

## Test Evidence

Executed focused suite:

```bash
pytest tests/test_surface_adversarial.py tests/test_s7_walk_forward.py tests/test_validate_release.py tests/test_config_contract.py -q
```

Result: `19 passed`.

## PM Decision Frame

- Current evidence supports a release block (`not_promotable`) under locked Sprint 7 policy.
- To revisit promotion status, PM can schedule a follow-up validation cycle specifically aimed at:
  1. obtaining required regime coverage evidence (`Calm`, `Transition`, `Stress`) in the
     evaluation population, and
  2. producing non-null transition false-positive density comparisons.

No gate thresholds were relaxed in this cycle.
