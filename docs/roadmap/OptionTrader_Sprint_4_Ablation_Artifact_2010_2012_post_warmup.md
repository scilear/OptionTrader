# OptionTrader Sprint 4 Ablation Artifact

Generated at: 2026-05-18T06:36:55.641658Z
Source script: `scripts/generate_regime_ablation_artifact.py`

## Locked Gate Evaluation

- Minimum sample gate (`>=50` total and `>=10` per active bucket): PASS
- Precision lift gate (`>= +0.03`): FAIL
- Volume guardrail (`[-15%, +15%]`): PASS
- Transition FP density worsening (`<= +0.02`): FAIL
- Overall retention gate: FAIL

## Baseline vs Candidate Lineages

- Baseline lineage: `3b024c9`
- Candidate lineage: `5128e8e`
- Requested start: `2010-01-01T00:00:00Z`
- Effective start (post warm-up): `2010-04-05T00:00:00Z`
- Baseline run/profile/hash: `run_id=33` `profile=baseline_rv_only` `config_hash=ba56410eb197f5895a80d324d76769291595e0f645b97f52ba2e5ad60907de68`
- Candidate run/profile/hash: `run_id=34` `profile=candidate_multi_signal` `config_hash=b0a92b8978a2afae3b4d0a7aaaded8d5a2c95d2da19d946fe6fc456c0bea5b36`

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
    "min_sample_pass": true,
    "overall_pass": false,
    "precision_blocked_reason": null,
    "precision_delta": 0.0,
    "precision_gate_pass": false,
    "transition_false_positive_density_worsening": 0.06736842105263158,
    "transition_fp_gate_pass": false,
    "volume_delta_pct": 0.0,
    "volume_gate_pass": true
  },
  "lineage_metadata": {
    "baseline": {
      "code_version": "3b024c98c829a6406bbfcc08ea5c18a0c5bab41f+profile:baseline_rv_only",
      "config_hash": "ba56410eb197f5895a80d324d76769291595e0f645b97f52ba2e5ad60907de68",
      "profile_id": "baseline_rv_only",
      "run_id": 33
    },
    "candidate": {
      "code_version": "5128e8e6f314f117e8f8eb29735d24f2bd4dd3d6+profile:candidate_multi_signal",
      "config_hash": "b0a92b8978a2afae3b4d0a7aaaded8d5a2c95d2da19d946fe6fc456c0bea5b36",
      "profile_id": "candidate_multi_signal",
      "run_id": 34
    }
  },
  "sample": {
    "baseline_alerts_by_regime": {
      "Calm": 40,
      "Stress": 176,
      "Transition": 57
    },
    "baseline_alerts_total": 273,
    "baseline_outcomes": {
      "fp": 141,
      "outcomes_observed": 165,
      "precision": 0.14545454545454545,
      "tp": 24,
      "transition_alerts": 57,
      "transition_fp": 22,
      "transition_fp_density": 0.38596491228070173
    },
    "baseline_outcomes_by_regime": {
      "Calm": 13,
      "Stress": 121,
      "Transition": 31
    },
    "baseline_snapshot_count": 683,
    "candidate_alerts_by_regime": {
      "Calm": 39,
      "Stress": 159,
      "Transition": 75
    },
    "candidate_alerts_total": 273,
    "candidate_outcomes": {
      "fp": 141,
      "outcomes_observed": 165,
      "precision": 0.14545454545454545,
      "tp": 24,
      "transition_alerts": 75,
      "transition_fp": 34,
      "transition_fp_density": 0.4533333333333333
    },
    "candidate_outcomes_by_regime": {
      "Calm": 12,
      "Stress": 107,
      "Transition": 46
    },
    "candidate_snapshot_count": 683
  },
  "status": "failed_gate",
  "window": {
    "effective_start_ts": "2010-04-05T00:00:00Z",
    "end_ts": "2012-12-31T23:59:59Z",
    "regime_ready_dates": {
      "baseline": "2010-04-05",
      "candidate": "2010-04-05"
    },
    "requested_start_ts": "2010-01-01T00:00:00Z",
    "underlying": "SPX",
    "warmup_excluded_days": 94,
    "warmup_exclusion_applied": true
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
