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

## Addendum - 2026-05-15 (S4-03 V3 Post-Warm-Up Rerun)

- Warm-up exclusion policy applied for S4-03 evidence window: `start_ts=2010-04-05T00:00:00Z`.
- This removes regime warm-up contamination from evidence evaluation while preserving
  fail-closed gate policy.
- Outcome remains `not_promotable`, but blocker scope is now narrowed.

Post-warm-up outputs:

- `docs/roadmap/OptionTrader_S4_03_Release_Validation_Report_full_span_post_warmup.md`
- `docs/roadmap/OptionTrader_S4_03_Release_Validation_Payload_full_span_post_warmup.json`
- `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact_full_span_post_warmup.md`
- `docs/roadmap/OptionTrader_S4_03_Gate_Attrition_Report_full_span_post_warmup.md`
- `docs/roadmap/OptionTrader_S4_03_Baseline_Capture_full_span_post_warmup.json`

Key findings from post-warm-up payload:

- `unknown_regime_count=0` and `unknown_regime_pass=true` (previous unknown-label blocker closed).
- `precision_non_regression=true` (candidate precision is higher than baseline).
- `transition_fp_density_non_worsening=false` remains the active blocker.
- Taxonomy verdict remains `invalid_evidence`, recommendation remains `not_promotable`.
