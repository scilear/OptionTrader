# OptionTrader Sprint 3.2 Replay Artifact

Generated at: 2026-05-02T15:56:40.855823Z
Source script: `scripts/generate_replay_artifact.py`

## Locked Comparison Contract

- `underlying`: `SPX`
- `start_ts`: `2026-04-01T00:00:00Z`
- `end_ts`: `2026-04-15T23:59:59Z`
- `baseline_commit`: `3b024c9`
- `candidate_commit`: `5128e8e`

## Required Summary Fields

```json
{
  "alert_count_baseline": 0,
  "alert_count_candidate": 0,
  "alert_delta_pct": "N/A",
  "baseline_commit": "3b024c9",
  "baseline_lineage": "3b024c9",
  "baseline_snapshot_count": 0,
  "candidate_commit": "5128e8e",
  "candidate_lineage": "5128e8e",
  "candidate_snapshot_count": 0,
  "end_ts": "2026-04-15T23:59:59Z",
  "precision_status": "not_available_in_v1_schema",
  "regime_split_counts": {
    "Unknown": 32
  },
  "start_ts": "2026-04-01T00:00:00Z",
  "total_snapshots": 32,
  "underlying": "SPX"
}
```

## Regime Split Counts (window total)

| regime_label | snapshot_count |
| --- | --- |
| Unknown | 32 |

## Per-Family Precision/Volume Summary

| alert_family | baseline_volume | candidate_volume | volume_delta_pct | baseline_precision | candidate_precision | precision_delta | note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| (none) | 0 | 0 | N/A | N/A | N/A | N/A | No alerts in window |

## Reproducibility

```bash
source .venv/bin/activate
python scripts/generate_replay_artifact.py --start-ts 2026-04-01T00:00:00Z --end-ts 2026-04-15T23:59:59Z
```

## Notes

- Precision columns are `N/A` because the current alert schema does not persist realized
  outcome labels required for true precision estimation.
- Volume and regime split are computed directly from persisted snapshots + alerts.
