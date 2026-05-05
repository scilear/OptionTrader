# OptionTrader S4-03 Gate Attrition Report

Generated at: 2026-05-05T16:05:25.609217Z

## Window

- Underlying: `SPX`
- Start: `2010-01-01T00:00:00Z`
- End: `2012-12-31T23:59:59Z`

## Baseline

- Lineage: `3b024c9`
- Run/Profile/Hash: `run_id=15` `profile=baseline_rv_only` `config_hash=e6a5ea43d46b2b414cd2ae0cc7d31da804253bfb4e7917f46031f42e1a273af1`
- Snapshots: `745`
- Surface rows: `25`
- QC pass: `23`
- Z-score pass: `0`
- Persistence pass: `0`
- Regime pass: `0`
- Tradability pass: `0`
- ExecutionReady: `0`

## Candidate

- Lineage: `5128e8e`
- Run/Profile/Hash: `run_id=16` `profile=candidate_multi_signal` `config_hash=1a7ffc0cf8fc05901c7747ea770dfcc08968dad8635232b95f208c13e314468b`
- Snapshots: `745`
- Surface rows: `25`
- QC pass: `23`
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
      "qc_pass": 23,
      "regime_pass": 0,
      "snapshots": 745,
      "surface_rows": 25,
      "tradability_pass": 0,
      "zscore_pass": 0
    },
    "lineage": "3b024c9",
    "meta": {
      "code_version": "3b024c98c829a6406bbfcc08ea5c18a0c5bab41f+profile:baseline_rv_only",
      "config_hash": "e6a5ea43d46b2b414cd2ae0cc7d31da804253bfb4e7917f46031f42e1a273af1",
      "profile_id": "baseline_rv_only",
      "run_id": 15
    }
  },
  "candidate": {
    "attrition": {
      "alerts_total": 0,
      "execution_ready": 0,
      "persistence_pass": 0,
      "qc_pass": 23,
      "regime_pass": 0,
      "snapshots": 745,
      "surface_rows": 25,
      "tradability_pass": 0,
      "zscore_pass": 0
    },
    "lineage": "5128e8e",
    "meta": {
      "code_version": "5128e8e6f314f117e8f8eb29735d24f2bd4dd3d6+profile:candidate_multi_signal",
      "config_hash": "1a7ffc0cf8fc05901c7747ea770dfcc08968dad8635232b95f208c13e314468b",
      "profile_id": "candidate_multi_signal",
      "run_id": 16
    }
  },
  "generated_at": "2026-05-05T16:05:25.609217Z",
  "window": {
    "end_ts": "2012-12-31T23:59:59Z",
    "start_ts": "2010-01-01T00:00:00Z",
    "underlying": "SPX"
  }
}
```
