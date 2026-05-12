# OptionTrader Sprint 4 Ablation Artifact

Generated at: 2026-05-12T20:16:46.329534Z
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
- Baseline run/profile/hash: `run_id=27` `profile=baseline_rv_only` `config_hash=ba56410eb197f5895a80d324d76769291595e0f645b97f52ba2e5ad60907de68`
- Candidate run/profile/hash: `run_id=28` `profile=candidate_multi_signal` `config_hash=b0a92b8978a2afae3b4d0a7aaaded8d5a2c95d2da19d946fe6fc456c0bea5b36`

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
  "lineage_metadata": {
    "baseline": {
      "code_version": "3b024c98c829a6406bbfcc08ea5c18a0c5bab41f+profile:baseline_rv_only",
      "config_hash": "ba56410eb197f5895a80d324d76769291595e0f645b97f52ba2e5ad60907de68",
      "profile_id": "baseline_rv_only",
      "run_id": 27
    },
    "candidate": {
      "code_version": "5128e8e6f314f117e8f8eb29735d24f2bd4dd3d6+profile:candidate_multi_signal",
      "config_hash": "b0a92b8978a2afae3b4d0a7aaaded8d5a2c95d2da19d946fe6fc456c0bea5b36",
      "profile_id": "candidate_multi_signal",
      "run_id": 28
    }
  },
  "sample": {
    "baseline_alerts_by_regime": {},
    "baseline_alerts_total": 0,
    "baseline_outcomes": {
      "fp": 0,
      "outcomes_observed": 0,
      "precision": null,
      "tp": 0,
      "transition_alerts": 0,
      "transition_fp": 0,
      "transition_fp_density": null
    },
    "baseline_outcomes_by_regime": {},
    "baseline_snapshot_count": 249,
    "candidate_alerts_by_regime": {},
    "candidate_alerts_total": 0,
    "candidate_outcomes": {
      "fp": 0,
      "outcomes_observed": 0,
      "precision": null,
      "tp": 0,
      "transition_alerts": 0,
      "transition_fp": 0,
      "transition_fp_density": null
    },
    "candidate_outcomes_by_regime": {},
    "candidate_snapshot_count": 249
  },
  "status": "blocked_pending_precision_labels",
  "window": {
    "end_ts": "2023-12-31T23:59:59Z",
    "start_ts": "2023-01-01T00:00:00Z",
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
