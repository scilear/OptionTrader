# OptionTrader S4-03 Gate Attrition Report

Generated at: 2026-05-22T02:44:49.557081Z

## Window

- Underlying: `SPX`
- Requested start: `2010-01-01T00:00:00Z`
- Effective start (post warm-up): `2010-04-05T00:00:00Z`
- End: `2023-12-31T23:59:59Z`
- Warm-up exclusion applied: `True`
- Warm-up excluded days: `94`

## Baseline

- Lineage: `3b024c9`
- Run/Profile/Hash: `run_id=51` `profile=baseline_rv_only` `config_hash=a6440afa83ff9f447c210ff9943e54243434132725f466e6bff0f9b1890c8c07`
- Snapshots: `3437`
- Surface rows: `3169`
- QC pass: `3152`
- Z-score pass: `223`
- Persistence pass: `517`
- Regime pass: `329`
- Tradability pass: `517`
- ExecutionReady: `56`

## Candidate

- Lineage: `5128e8e-v2b`
- Run/Profile/Hash: `run_id=52` `profile=candidate_multi_signal_v2b` `config_hash=2521728f713d993f8f7688b18f3cdb1229dd5681a415e7b3ce02446f8b9db7f4`
- Snapshots: `3437`
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
      "alerts_total": 517,
      "execution_ready": 56,
      "persistence_pass": 517,
      "qc_pass": 3152,
      "regime_pass": 329,
      "snapshots": 3437,
      "surface_rows": 3169,
      "tradability_pass": 517,
      "zscore_pass": 223
    },
    "lineage": "3b024c9",
    "meta": {
      "code_version": "3b024c98c829a6406bbfcc08ea5c18a0c5bab41f+profile:baseline_rv_only",
      "config_hash": "a6440afa83ff9f447c210ff9943e54243434132725f466e6bff0f9b1890c8c07",
      "profile_id": "baseline_rv_only",
      "run_id": 51
    }
  },
  "candidate": {
    "attrition": {
      "alerts_total": 0,
      "execution_ready": 0,
      "persistence_pass": 0,
      "qc_pass": 0,
      "regime_pass": 0,
      "snapshots": 3437,
      "surface_rows": 0,
      "tradability_pass": 0,
      "zscore_pass": 0
    },
    "lineage": "5128e8e-v2b",
    "meta": {
      "code_version": "5128e8e-v2b+profile:candidate_multi_signal_v2b",
      "config_hash": "2521728f713d993f8f7688b18f3cdb1229dd5681a415e7b3ce02446f8b9db7f4",
      "profile_id": "candidate_multi_signal_v2b",
      "run_id": 52
    }
  },
  "generated_at": "2026-05-22T02:44:49.557081Z",
  "window": {
    "effective_start_ts": "2010-04-05T00:00:00Z",
    "end_ts": "2023-12-31T23:59:59Z",
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
