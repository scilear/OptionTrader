# OptionTrader S4-03 Gate Attrition Report

Generated at: 2026-05-05T17:50:16.951851Z

## Window

- Underlying: `SPX`
- Start: `2010-01-01T00:00:00Z`
- End: `2023-12-31T23:59:59Z`

## Baseline

- Lineage: `3b024c9`
- Run/Profile/Hash: `run_id=19` `profile=baseline_rv_only` `config_hash=e6a5ea43d46b2b414cd2ae0cc7d31da804253bfb4e7917f46031f42e1a273af1`
- Snapshots: `1063`
- Surface rows: `794`
- QC pass: `57`
- Z-score pass: `695`
- Persistence pass: `695`
- Regime pass: `695`
- Tradability pass: `695`
- ExecutionReady: `12`

## Candidate

- Lineage: `5128e8e`
- Run/Profile/Hash: `run_id=20` `profile=candidate_multi_signal` `config_hash=1a7ffc0cf8fc05901c7747ea770dfcc08968dad8635232b95f208c13e314468b`
- Snapshots: `1063`
- Surface rows: `794`
- QC pass: `57`
- Z-score pass: `695`
- Persistence pass: `695`
- Regime pass: `695`
- Tradability pass: `695`
- ExecutionReady: `12`

## Raw Payload

```json
{
  "baseline": {
    "attrition": {
      "alerts_total": 695,
      "execution_ready": 12,
      "persistence_pass": 695,
      "qc_pass": 57,
      "regime_pass": 695,
      "snapshots": 1063,
      "surface_rows": 794,
      "tradability_pass": 695,
      "zscore_pass": 695
    },
    "lineage": "3b024c9",
    "meta": {
      "code_version": "3b024c98c829a6406bbfcc08ea5c18a0c5bab41f+profile:baseline_rv_only",
      "config_hash": "e6a5ea43d46b2b414cd2ae0cc7d31da804253bfb4e7917f46031f42e1a273af1",
      "profile_id": "baseline_rv_only",
      "run_id": 19
    }
  },
  "candidate": {
    "attrition": {
      "alerts_total": 695,
      "execution_ready": 12,
      "persistence_pass": 695,
      "qc_pass": 57,
      "regime_pass": 695,
      "snapshots": 1063,
      "surface_rows": 794,
      "tradability_pass": 695,
      "zscore_pass": 695
    },
    "lineage": "5128e8e",
    "meta": {
      "code_version": "5128e8e6f314f117e8f8eb29735d24f2bd4dd3d6+profile:candidate_multi_signal",
      "config_hash": "1a7ffc0cf8fc05901c7747ea770dfcc08968dad8635232b95f208c13e314468b",
      "profile_id": "candidate_multi_signal",
      "run_id": 20
    }
  },
  "generated_at": "2026-05-05T17:50:16.951851Z",
  "window": {
    "end_ts": "2023-12-31T23:59:59Z",
    "start_ts": "2010-01-01T00:00:00Z",
    "underlying": "SPX"
  }
}
```
