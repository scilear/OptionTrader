# OptionTrader Sprint 4 Ablation Artifact

Generated at: 2026-05-04T07:12:41.527910Z
Source script: `scripts/generate_regime_ablation_artifact.py`

## Locked Gate Evaluation

- Minimum sample gate (`>=50` total and `>=10` per active bucket): FAIL
- Precision lift gate (`>= +0.03`): FAIL
- Volume guardrail (`[-15%, +15%]`): FAIL
- Transition FP density worsening (`<= +0.02`): FAIL
- Overall retention gate: FAIL

## Baseline vs Candidate Lineages

- Baseline lineage: `3b024c9`
- Candidate lineage: `5128e8e`

## Summary Payload

```json
{
  "baseline_track": "3b024c9",
  "candidate_track": "5128e8e",
  "feature_decisions": [
    {
      "evidence": "insufficient or blocked gate evidence",
      "feature": "event",
      "reason": "s4_03_gate_failed",
      "status": "disabled"
    },
    {
      "evidence": "insufficient or blocked gate evidence",
      "feature": "stress_proxy",
      "reason": "s4_03_gate_failed",
      "status": "disabled"
    }
  ],
  "gates": {
    "min_sample_pass": false,
    "overall_pass": false,
    "precision_blocked_reason": "missing_outcome_labels",
    "precision_delta": null,
    "precision_gate_pass": false,
    "transition_false_positive_density_worsening": null,
    "transition_fp_gate_pass": false,
    "volume_delta_pct": null,
    "volume_gate_pass": false
  },
  "sample": {
    "baseline_alerts_by_regime": {},
    "baseline_alerts_total": 0,
    "baseline_snapshot_count": 0,
    "candidate_alerts_by_regime": {},
    "candidate_alerts_total": 0,
    "candidate_snapshot_count": 0
  },
  "status": "blocked_pending_precision_labels",
  "window": {
    "end_ts": "2026-04-15T23:59:59Z",
    "start_ts": "2026-04-01T00:00:00Z",
    "underlying": "SPX"
  }
}
```

## Feature Decisions

- `event`: disabled in runtime defaults (`regime.weights.event=0.00`).
- `stress_proxy`: disabled in runtime defaults (`regime.weights.stress_proxy=0.00`).

## Notes

- This run uses the locked S3.2 window by default.
- Baseline/candidate counts are computed from real snapshot lineages (no hardcoded baseline).
- Precision and transition false-positive density require persisted realized outcomes;
  S4-03 remains blocked until outcome labels are available.
