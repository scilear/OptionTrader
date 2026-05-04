# OptionTrader S4-03 Synthetic Methodology Protocol

Date: 2026-05-04
Scope: Validate S4-03 gate mechanics with deterministic synthetic data (non-production evidence).
Related issues: `#2`, `#3`, `#4`

## Purpose

This protocol validates that S4-03 tooling and gates are implemented correctly, even when production
window data is sparse. It does not replace real-data validation for final Sprint 4 sign-off.

## Evidence Separation Rule

Maintain two separate evidence streams:

1. Methodology evidence (this protocol):
   - synthetic dataset,
   - deterministic outcomes,
   - expected gate behavior.
2. Production evidence (final sign-off):
   - real replay window,
   - observed market/QC behavior,
   - final retain/disable decision.

Do not use synthetic results alone to claim production incremental value.

## Test Database and Isolation

- Use a dedicated DB path, never `data/optiontrader.duckdb`.
- Recommended path: `data/s4_03_synthetic.duckdb`.
- Run with an isolated config (copy `config/config-test.yaml` and set storage path).

## Synthetic Contract (Deterministic)

### Window and lineage

- Underlying: `SPX`
- Start: `2026-04-01T00:00:00Z`
- End: `2026-04-15T23:59:59Z`
- Baseline lineage: `3b024c9`
- Candidate lineage: `5128e8e`

### Minimum sample targets

For each lineage:

- `>= 60` alerts total.
- At least `10` alerts labeled `Transition`.
- At least `10` alerts each in two other regime labels (`Calm`, `Stress`) where applicable.

### Outcome label design

Use deterministic, explicit outcome mapping for synthetic alerts:

- `tp` if configured reversion ratio threshold is met.
- `fp` otherwise.

Populate enough rows so precision and transition FP density are both computable for baseline and
candidate tracks.

## Scenario Matrix

Generate at least 3 deterministic scenarios in synthetic DB:

1. Gate-pass scenario:
   - candidate precision >= baseline precision + 0.03,
   - transition FP density worsening <= +0.02,
   - volume delta in [-15%, +15%].
2. Gate-fail scenario (precision):
   - candidate precision delta < +0.03.
3. Gate-fail scenario (transition FP):
   - transition FP worsening > +0.02.

Optional 4th scenario:

4. Gate-block scenario:
   - insufficient outcomes for one lineage to verify blocked path handling.

## Required Artifacts

For each scenario, produce:

- JSON summary payload from ablation script.
- Markdown artifact with gate status.
- SQL row-count snapshot (lineage counts, alerts, outcomes, transition alerts/fp).

Store under:

- `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact_Synthetic.md`

## Commands (Reference)

```bash
source .venv/bin/activate

# 1) Prepare isolated config pointing to synthetic DB
# (dev script or one-off helper should create/populate synthetic tracks)

# 2) Evaluate outcomes
python scripts/evaluate_alert_outcomes.py --horizon-days 5 --overwrite

# 3) Generate artifact on locked contract
python scripts/generate_regime_ablation_artifact.py \
  --start-ts 2026-04-01T00:00:00Z \
  --end-ts 2026-04-15T23:59:59Z \
  --baseline-lineage 3b024c9 \
  --candidate-lineage 5128e8e \
  --output docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact_Synthetic.md
```

## Test Requirements

Add/extend tests to cover:

- lineage filtering correctness,
- outcome evaluation determinism,
- precision/transition gate calculations,
- blocked-path behavior when outcomes are missing,
- status resolution (`passed`, `failed_gate`, `blocked_pending_precision_labels`).

Recommended file:

- `tests/test_s4_ablation.py`

## Acceptance Criteria (Methodology Complete)

Methodology protocol is complete when all are true:

1. Synthetic scenarios reproduce expected gate outcomes deterministically.
2. Artifact status and numeric fields match scenario definitions.
3. Tests cover gate math and status transitions.
4. Synthetic artifact is clearly labeled non-production evidence.

## Exit to Production Validation

After methodology completion, run production evidence track (issue `#4`) with real data and maintain
separate artifact naming.

S4-03 can be signed off only after production evidence gates are satisfied or a formally approved
alternate real-data contract is met.
