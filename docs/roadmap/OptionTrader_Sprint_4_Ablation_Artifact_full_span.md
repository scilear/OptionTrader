# OptionTrader Sprint 4 Ablation Artifact

Generated at: 2026-05-05T17:50:11.247758Z
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
- Baseline run/profile/hash: `run_id=19` `profile=baseline_rv_only` `config_hash=e6a5ea43d46b2b414cd2ae0cc7d31da804253bfb4e7917f46031f42e1a273af1`
- Candidate run/profile/hash: `run_id=20` `profile=candidate_multi_signal` `config_hash=1a7ffc0cf8fc05901c7747ea770dfcc08968dad8635232b95f208c13e314468b`

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
    "transition_false_positive_density_worsening": null,
    "transition_fp_gate_pass": false,
    "volume_delta_pct": 0.0,
    "volume_gate_pass": true
  },
  "lineage_metadata": {
    "baseline": {
      "code_version": "3b024c98c829a6406bbfcc08ea5c18a0c5bab41f+profile:baseline_rv_only",
      "config_hash": "e6a5ea43d46b2b414cd2ae0cc7d31da804253bfb4e7917f46031f42e1a273af1",
      "profile_id": "baseline_rv_only",
      "run_id": 19
    },
    "candidate": {
      "code_version": "5128e8e6f314f117e8f8eb29735d24f2bd4dd3d6+profile:candidate_multi_signal",
      "config_hash": "1a7ffc0cf8fc05901c7747ea770dfcc08968dad8635232b95f208c13e314468b",
      "profile_id": "candidate_multi_signal",
      "run_id": 20
    }
  },
  "sample": {
    "baseline_alerts_by_regime": {
      "Neutral": 695
    },
    "baseline_alerts_total": 695,
    "baseline_outcomes": {
      "fp": 630,
      "outcomes_observed": 683,
      "precision": 0.07759882869692533,
      "tp": 53,
      "transition_alerts": 0,
      "transition_fp": 0,
      "transition_fp_density": null
    },
    "baseline_snapshot_count": 1063,
    "candidate_alerts_by_regime": {
      "Neutral": 695
    },
    "candidate_alerts_total": 695,
    "candidate_outcomes": {
      "fp": 630,
      "outcomes_observed": 683,
      "precision": 0.07759882869692533,
      "tp": 53,
      "transition_alerts": 0,
      "transition_fp": 0,
      "transition_fp_density": null
    },
    "candidate_snapshot_count": 1063
  },
  "status": "failed_gate",
  "window": {
    "end_ts": "2023-12-31T23:59:59Z",
    "start_ts": "2010-01-01T00:00:00Z",
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
