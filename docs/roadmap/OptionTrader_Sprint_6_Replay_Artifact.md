# OptionTrader Sprint 6 Replay Artifact

Generated at: 2026-05-06T10:26:54.269245Z
Source script: `scripts/generate_s6_replay_artifact.py`

## Contract

- Contract ID: `S6-CONTRACT-v1`
- Underlying: `SPX`
- Start: `2010-01-01T00:00:00Z`
- End: `2023-12-31T23:59:59Z`
- Baseline lineage: `3b024c9`
- Candidate lineage: `5128e8e`
- Config path: `config/config-eod-truth.yaml`

## Gate Evaluation

- Decomposition coverage gate: PASS
- ExecutionReady non-positive edge gate: PASS
- Monotonic size impact gate: PASS
- Ranking stability gate: PASS
- Overall gate: PASS

## Recommendation

- Final recommendation: `promotable`

## Summary Payload

```json
{
  "baseline": {
    "alerts_by_state": {
      "Candidate": 231,
      "ExecutionReady": 5
    },
    "alerts_total": 236,
    "blocked_reason_counts": {},
    "execution_ready_with_non_positive_edge": 0,
    "ideas_total": 5,
    "ideas_with_cost_decomposition": 5,
    "mean_edge_after_cost": 17013.489688957932,
    "median_edge_after_cost": 19815.91661472227,
    "monotonic_size_violations": 0,
    "non_positive_edge_count": 0,
    "promote_eligible_count": 5,
    "stable_rank_fraction": 1.0
  },
  "candidate": {
    "alerts_by_state": {
      "Candidate": 231,
      "ExecutionReady": 5
    },
    "alerts_total": 236,
    "blocked_reason_counts": {},
    "execution_ready_with_non_positive_edge": 0,
    "ideas_total": 5,
    "ideas_with_cost_decomposition": 5,
    "mean_edge_after_cost": 17013.489688957932,
    "median_edge_after_cost": 19815.91661472227,
    "monotonic_size_violations": 0,
    "non_positive_edge_count": 0,
    "promote_eligible_count": 5,
    "stable_rank_fraction": 1.0
  },
  "contract": {
    "baseline_lineage": "3b024c9",
    "candidate_lineage": "5128e8e",
    "config_path": "config/config-eod-truth.yaml",
    "id": "S6-CONTRACT-v1"
  },
  "gates": {
    "decomposition_coverage_pass": true,
    "executionready_non_positive_edge_pass": true,
    "monotonic_size_impact_pass": true,
    "overall_pass": true,
    "ranking_stability_pass": true
  },
  "generated_at": "2026-05-06T10:26:54.269245Z",
  "lineage_metadata": {
    "baseline": {
      "code_version": "3b024c98c829a6406bbfcc08ea5c18a0c5bab41f+profile:baseline_rv_only",
      "config_hash": "ba56410eb197f5895a80d324d76769291595e0f645b97f52ba2e5ad60907de68",
      "profile_id": "baseline_rv_only",
      "run_id": 23
    },
    "candidate": {
      "code_version": "5128e8e6f314f117e8f8eb29735d24f2bd4dd3d6+profile:candidate_multi_signal",
      "config_hash": "b0a92b8978a2afae3b4d0a7aaaded8d5a2c95d2da19d946fe6fc456c0bea5b36",
      "profile_id": "candidate_multi_signal",
      "run_id": 24
    }
  },
  "recommendation": "promotable",
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
python scripts/generate_s6_replay_artifact.py --config-path config/config-eod-truth.yaml --start-ts 2010-01-01T00:00:00Z --end-ts 2023-12-31T23:59:59Z --underlying SPX --baseline-lineage 3b024c9 --candidate-lineage 5128e8e
```

