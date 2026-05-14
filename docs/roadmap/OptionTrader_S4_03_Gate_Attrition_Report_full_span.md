# OptionTrader S4-03 Gate Attrition Report

Generated at: 2026-05-14T19:03:11.912778Z

## Window

- Underlying: `SPX`
- Start: `2010-01-01T00:00:00Z`
- End: `2023-12-31T23:59:59Z`

## Baseline

- Lineage: `3b024c9`
- Run/Profile/Hash: `run_id=33` `profile=baseline_rv_only` `config_hash=ba56410eb197f5895a80d324d76769291595e0f645b97f52ba2e5ad60907de68`
- Snapshots: `3499`
- Surface rows: `2684`
- QC pass: `2667`
- Z-score pass: `443`
- Persistence pass: `443`
- Regime pass: `286`
- Tradability pass: `435`
- ExecutionReady: `121`

## Candidate

- Lineage: `5128e8e`
- Run/Profile/Hash: `run_id=34` `profile=candidate_multi_signal` `config_hash=b0a92b8978a2afae3b4d0a7aaaded8d5a2c95d2da19d946fe6fc456c0bea5b36`
- Snapshots: `3499`
- Surface rows: `5005`
- QC pass: `4953`
- Z-score pass: `1031`
- Persistence pass: `1031`
- Regime pass: `839`
- Tradability pass: `741`
- ExecutionReady: `343`

## Raw Payload

```json
{
  "baseline": {
    "attrition": {
      "alerts_total": 443,
      "execution_ready": 121,
      "persistence_pass": 443,
      "qc_pass": 2667,
      "regime_pass": 286,
      "snapshots": 3499,
      "surface_rows": 2684,
      "tradability_pass": 435,
      "zscore_pass": 443
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
      "alerts_total": 1031,
      "execution_ready": 343,
      "persistence_pass": 1031,
      "qc_pass": 4953,
      "regime_pass": 839,
      "snapshots": 3499,
      "surface_rows": 5005,
      "tradability_pass": 741,
      "zscore_pass": 1031
    },
    "lineage": "5128e8e",
    "meta": {
      "code_version": "5128e8e6f314f117e8f8eb29735d24f2bd4dd3d6+profile:candidate_multi_signal",
      "config_hash": "b0a92b8978a2afae3b4d0a7aaaded8d5a2c95d2da19d946fe6fc456c0bea5b36",
      "profile_id": "candidate_multi_signal",
      "run_id": 34
    }
  },
  "generated_at": "2026-05-14T19:03:11.912778Z",
  "window": {
    "end_ts": "2023-12-31T23:59:59Z",
    "start_ts": "2010-01-01T00:00:00Z",
    "underlying": "SPX"
  }
}
```
