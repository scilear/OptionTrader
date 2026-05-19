# OptionTrader S4-03 Gate Attrition Report

Generated at: 2026-05-19T15:21:43.249316Z

## Window

- Underlying: `SPX`
- Requested start: `2023-01-01T00:00:00Z`
- Effective start (post warm-up): `2023-01-01T00:00:00Z`
- End: `2023-12-31T23:59:59Z`
- Warm-up exclusion applied: `False`
- Warm-up excluded days: `0`

## Baseline

- Lineage: `3b024c9`
- Run/Profile/Hash: `run_id=33` `profile=baseline_rv_only` `config_hash=ba56410eb197f5895a80d324d76769291595e0f645b97f52ba2e5ad60907de68`
- Snapshots: `249`
- Surface rows: `0`
- QC pass: `0`
- Z-score pass: `0`
- Persistence pass: `0`
- Regime pass: `0`
- Tradability pass: `0`
- ExecutionReady: `0`

## Candidate

- Lineage: `5128e8e`
- Run/Profile/Hash: `run_id=34` `profile=candidate_multi_signal` `config_hash=b0a92b8978a2afae3b4d0a7aaaded8d5a2c95d2da19d946fe6fc456c0bea5b36`
- Snapshots: `249`
- Surface rows: `0`
- QC pass: `0`
- Z-score pass: `0`
- Persistence pass: `0`
- Regime pass: `0`
- Tradability pass: `0`
- ExecutionReady: `0`

## Raw Payload

```json
{
  "baseline": {
    "attrition": {
      "alerts_total": 0,
      "execution_ready": 0,
      "persistence_pass": 0,
      "qc_pass": 0,
      "regime_pass": 0,
      "snapshots": 249,
      "surface_rows": 0,
      "tradability_pass": 0,
      "zscore_pass": 0
    },
    "lineage": "3b024c9",
    "meta": {
      "code_version": "3b024c98c829a6406bbfcc08ea5c18a0c5bab41f+profile:baseline_rv_only",
      "config_hash": "ba56410eb197f5895a80d324d76769291595e0f645b97f52ba2e5ad60907de68",
      "profile_id": "baseline_rv_only",
      "run_id": 33
    }
  },
  "candidate": {
    "attrition": {
      "alerts_total": 0,
      "execution_ready": 0,
      "persistence_pass": 0,
      "qc_pass": 0,
      "regime_pass": 0,
      "snapshots": 249,
      "surface_rows": 0,
      "tradability_pass": 0,
      "zscore_pass": 0
    },
    "lineage": "5128e8e",
    "meta": {
      "code_version": "5128e8e6f314f117e8f8eb29735d24f2bd4dd3d6+profile:candidate_multi_signal",
      "config_hash": "b0a92b8978a2afae3b4d0a7aaaded8d5a2c95d2da19d946fe6fc456c0bea5b36",
      "profile_id": "candidate_multi_signal",
      "run_id": 34
    }
  },
  "generated_at": "2026-05-19T15:21:43.249316Z",
  "window": {
    "effective_start_ts": "2023-01-01T00:00:00Z",
    "end_ts": "2023-12-31T23:59:59Z",
    "regime_ready_dates": {
      "baseline": "2010-04-05",
      "candidate": "2010-04-05"
    },
    "requested_start_ts": "2023-01-01T00:00:00Z",
    "underlying": "SPX",
    "warmup_excluded_days": 0,
    "warmup_exclusion_applied": false
  }
}
```
