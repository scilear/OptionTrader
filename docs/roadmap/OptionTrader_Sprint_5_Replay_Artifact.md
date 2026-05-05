# OptionTrader Sprint 5 Replay Artifact

Generated at: 2026-05-05T21:11:32.436009Z
Source script: `scripts/generate_s5_replay_artifact.py`

## Evaluation Contract

- Underlying: `SPX`
- Start: `2010-01-01T00:00:00Z`
- End: `2023-12-31T23:59:59Z`
- Baseline lineage: `3b024c9`
- Candidate lineage: `5128e8e`
- Outcome horizon: `5` days
- Volume inflation guardrail: `<= +15.0%`
- Transition FP density rule: `candidate < baseline`

## Baseline vs Candidate Metadata

- Baseline run/profile/hash: `run_id=19` `profile=baseline_rv_only` `config_hash=e6a5ea43d46b2b414cd2ae0cc7d31da804253bfb4e7917f46031f42e1a273af1`
- Candidate run/profile/hash: `run_id=20` `profile=candidate_multi_signal` `config_hash=1a7ffc0cf8fc05901c7747ea770dfcc08968dad8635232b95f208c13e314468b`

## Signal Counts by State

| State | Baseline | Candidate |
| --- | ---: | ---: |
| Candidate | 683 | 683 |
| ExecutionReady | 12 | 12 |

## Gate Evaluation

- Min sample gate (`>=50` alerts/track): PASS
- Volume guardrail (`candidate-baseline`): PASS (delta=+0.00%)
- Transition FP density improvement: FAIL (baseline=N/A, candidate=N/A, blocked_reason=missing_transition_alerts)
- State distribution sanity: PASS
- Precision non-regression: PASS
- Overall release gate: FAIL

## Recommendation

- Final recommendation: `not_promotable`

## Summary Payload

```json
{
  "baseline": {
    "alerts_by_state": {
      "Candidate": 683,
      "ExecutionReady": 12
    },
    "alerts_total": 695,
    "invalid_signal_states": [],
    "outcomes": {
      "fp": 630,
      "horizon_days": 5,
      "outcomes_observed": 683,
      "precision": 0.07759882869692533,
      "tp": 53,
      "transition_alerts": 0,
      "transition_fp": 0,
      "transition_fp_density": null
    },
    "snapshot_count": 1063
  },
  "candidate": {
    "alerts_by_state": {
      "Candidate": 683,
      "ExecutionReady": 12
    },
    "alerts_total": 695,
    "invalid_signal_states": [],
    "outcomes": {
      "fp": 630,
      "horizon_days": 5,
      "outcomes_observed": 683,
      "precision": 0.07759882869692533,
      "tp": 53,
      "transition_alerts": 0,
      "transition_fp": 0,
      "transition_fp_density": null
    },
    "snapshot_count": 1063
  },
  "contract": {
    "baseline_lineage": "3b024c9",
    "candidate_lineage": "5128e8e",
    "config_path": "config/config-eod-truth.yaml",
    "horizon_days": 5,
    "max_volume_inflation_pct": 15.0,
    "state_sanity_required_states": [
      "Candidate",
      "ExecutionReady",
      "Validated"
    ],
    "transition_fp_density_rule": "candidate < baseline"
  },
  "gates": {
    "min_sample_gate_pass": true,
    "overall_pass": false,
    "precision_non_regression_pass": true,
    "state_distribution_sanity_pass": true,
    "transition_fp_density_baseline": null,
    "transition_fp_density_blocked_reason": "missing_transition_alerts",
    "transition_fp_density_candidate": null,
    "transition_fp_density_improved_pass": false,
    "volume_delta_pct": 0.0,
    "volume_guardrail_pass": true
  },
  "generated_at": "2026-05-05T21:11:32.436009Z",
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
  "recommendation": "not_promotable",
  "window": {
    "end_ts": "2023-12-31T23:59:59Z",
    "start_ts": "2010-01-01T00:00:00Z",
    "underlying": "SPX"
  }
}
```

## Reproducibility

```bash
source .venv/bin/activate
python scripts/generate_s5_replay_artifact.py --config-path config/config-eod-truth.yaml --start-ts 2010-01-01T00:00:00Z --end-ts 2023-12-31T23:59:59Z --underlying SPX --baseline-lineage 3b024c9 --candidate-lineage 5128e8e
```

