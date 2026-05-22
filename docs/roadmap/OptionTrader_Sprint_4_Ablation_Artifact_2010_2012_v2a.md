# OptionTrader Sprint 4 Ablation Artifact

Generated at: 2026-05-22T02:46:23.007348Z
Source script: `scripts/generate_regime_ablation_artifact.py`

## Locked Gate Evaluation

- Minimum sample gate (`>=50` total and `>=10` per active bucket): FAIL
- Precision lift gate (`>= +0.03`): FAIL
- Volume guardrail (`[-15%, +15%]`): FAIL
- Transition FP density worsening (`<= +0.02`): FAIL
- Overall retention gate: FAIL

## Baseline vs Candidate Lineages

- Baseline lineage: `3b024c9`
- Candidate lineage: `5128e8e-v2a`
- Requested start: `2010-01-01T00:00:00Z`
- Effective start (post warm-up): `2010-04-05T00:00:00Z`
- Baseline run/profile/hash: `run_id=51` `profile=baseline_rv_only` `config_hash=a6440afa83ff9f447c210ff9943e54243434132725f466e6bff0f9b1890c8c07`
- Candidate run/profile/hash: `run_id=50` `profile=candidate_multi_signal_v2a` `config_hash=20776af3d4924050091369612d07a73770d51f41965c43a6de8b8dd71e9d70ec`

## Summary Payload

```json
{
  "baseline_track": "3b024c9",
  "candidate_track": "5128e8e-v2a",
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
    "volume_delta_pct": -100.0,
    "volume_gate_pass": false
  },
  "lineage_metadata": {
    "baseline": {
      "code_version": "3b024c98c829a6406bbfcc08ea5c18a0c5bab41f+profile:baseline_rv_only",
      "config_hash": "a6440afa83ff9f447c210ff9943e54243434132725f466e6bff0f9b1890c8c07",
      "profile_id": "baseline_rv_only",
      "run_id": 51
    },
    "candidate": {
      "code_version": "5128e8e-v2a+profile:candidate_multi_signal_v2a",
      "config_hash": "20776af3d4924050091369612d07a73770d51f41965c43a6de8b8dd71e9d70ec",
      "profile_id": "candidate_multi_signal_v2a",
      "run_id": 50
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
    "candidate_snapshot_count": 683
  },
  "status": "blocked_pending_precision_labels",
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
