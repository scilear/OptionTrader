# OptionTrader S4-03 Gate Attrition Report

Generated at: 2026-05-18T06:37:18.981183Z

## Window

- Underlying: `SPX`
- Requested start: `2010-01-01T00:00:00Z`
- Effective start (post warm-up): `2010-04-05T00:00:00Z`
- End: `2012-12-31T23:59:59Z`
- Warm-up exclusion applied: `True`
- Warm-up excluded days: `94`

## Baseline

- Lineage: `3b024c9`
- Run/Profile/Hash: `run_id=33` `profile=baseline_rv_only` `config_hash=ba56410eb197f5895a80d324d76769291595e0f645b97f52ba2e5ad60907de68`
- Snapshots: `683`
- Surface rows: `1080`
- QC pass: `1063`
- Z-score pass: `273`
- Persistence pass: `273`
- Regime pass: `145`
- Tradability pass: `273`
- ExecutionReady: `6`

## Candidate

- Lineage: `5128e8e`
- Run/Profile/Hash: `run_id=34` `profile=candidate_multi_signal` `config_hash=b0a92b8978a2afae3b4d0a7aaaded8d5a2c95d2da19d946fe6fc456c0bea5b36`
- Snapshots: `683`
- Surface rows: `1080`
- QC pass: `1063`
- Z-score pass: `273`
- Persistence pass: `273`
- Regime pass: `159`
- Tradability pass: `273`
- ExecutionReady: `6`

## Raw Payload

```json
{
  "baseline": {
    "attrition": {
      "alerts_total": 273,
      "execution_ready": 6,
      "persistence_pass": 273,
      "qc_pass": 1063,
      "regime_pass": 145,
      "snapshots": 683,
      "surface_rows": 1080,
      "tradability_pass": 273,
      "zscore_pass": 273
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
      "alerts_total": 273,
      "execution_ready": 6,
      "persistence_pass": 273,
      "qc_pass": 1063,
      "regime_pass": 159,
      "snapshots": 683,
      "surface_rows": 1080,
      "tradability_pass": 273,
      "zscore_pass": 273
    },
    "lineage": "5128e8e",
    "meta": {
      "code_version": "5128e8e6f314f117e8f8eb29735d24f2bd4dd3d6+profile:candidate_multi_signal",
      "config_hash": "b0a92b8978a2afae3b4d0a7aaaded8d5a2c95d2da19d946fe6fc456c0bea5b36",
      "profile_id": "candidate_multi_signal",
      "run_id": 34
    }
  },
  "generated_at": "2026-05-18T06:37:18.981183Z",
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
