# OptionTrader S4-03 Gate Attrition Report

Generated at: 2026-05-13T14:39:46.032846Z

## Window

- Underlying: `SPX`
- Start: `2010-01-01T00:00:00Z`
- End: `2023-12-31T23:59:59Z`

## Baseline

- Lineage: `3b024c9`
- Run/Profile/Hash: `run_id=31` `profile=baseline_rv_only` `config_hash=ba56410eb197f5895a80d324d76769291595e0f645b97f52ba2e5ad60907de68`
- Snapshots: `3499`
- Surface rows: `1188`
- QC pass: `1169`
- Z-score pass: `290`
- Persistence pass: `290`
- Regime pass: `145`
- Tradability pass: `282`
- ExecutionReady: `6`

## Candidate

- Lineage: `5128e8e`
- Run/Profile/Hash: `run_id=32` `profile=candidate_multi_signal` `config_hash=b0a92b8978a2afae3b4d0a7aaaded8d5a2c95d2da19d946fe6fc456c0bea5b36`
- Snapshots: `3499`
- Surface rows: `582`
- QC pass: `577`
- Z-score pass: `120`
- Persistence pass: `120`
- Regime pass: `62`
- Tradability pass: `112`
- ExecutionReady: `0`

## Raw Payload

```json
{
  "baseline": {
    "attrition": {
      "alerts_total": 290,
      "execution_ready": 6,
      "persistence_pass": 290,
      "qc_pass": 1169,
      "regime_pass": 145,
      "snapshots": 3499,
      "surface_rows": 1188,
      "tradability_pass": 282,
      "zscore_pass": 290
    },
    "lineage": "3b024c9",
    "meta": {
      "code_version": "3b024c98c829a6406bbfcc08ea5c18a0c5bab41f+profile:baseline_rv_only",
      "config_hash": "ba56410eb197f5895a80d324d76769291595e0f645b97f52ba2e5ad60907de68",
      "profile_id": "baseline_rv_only",
      "run_id": 31
    }
  },
  "candidate": {
    "attrition": {
      "alerts_total": 120,
      "execution_ready": 0,
      "persistence_pass": 120,
      "qc_pass": 577,
      "regime_pass": 62,
      "snapshots": 3499,
      "surface_rows": 582,
      "tradability_pass": 112,
      "zscore_pass": 120
    },
    "lineage": "5128e8e",
    "meta": {
      "code_version": "5128e8e6f314f117e8f8eb29735d24f2bd4dd3d6+profile:candidate_multi_signal",
      "config_hash": "b0a92b8978a2afae3b4d0a7aaaded8d5a2c95d2da19d946fe6fc456c0bea5b36",
      "profile_id": "candidate_multi_signal",
      "run_id": 32
    }
  },
  "generated_at": "2026-05-13T14:39:46.032846Z",
  "window": {
    "end_ts": "2023-12-31T23:59:59Z",
    "start_ts": "2010-01-01T00:00:00Z",
    "underlying": "SPX"
  }
}
```
