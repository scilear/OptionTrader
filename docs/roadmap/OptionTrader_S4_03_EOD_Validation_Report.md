# OptionTrader S4-03 EOD Validation Report

DB path: `data/optiontrader_eod_truth.duckdb`
Snapshot count: `8`
Quote count: `111398`

## Hard Checks

- `tables_present`: PASS
- `non_empty_snapshots`: PASS
- `non_empty_quotes`: PASS
- `no_crossed_quotes`: PASS
- `no_missing_bidask`: PASS
- `valid_option_rights`: PASS
- `no_orphan_quotes`: PASS
- `no_duplicate_natural_keys`: PASS
- `no_null_expiry`: PASS

## Issue Counts

- `crossed_quotes`: `0`
- `missing_bidask`: `0`
- `invalid_right`: `0`
- `orphan_quotes`: `0`
- `duplicate_quotes`: `0`
- `null_expiry`: `0`

## Soft Stats

- `min_bid`: `0.05`
- `max_ask`: `6540.2`
- `avg_relative_spread`: `0.051878921274796305`
- `zero_bid_ratio`: `0.0`

## Snapshot Density by Date

| date | snapshot_count |
| --- | ---: |
| 2023-01-04 | 1 |
| 2023-01-05 | 1 |
| 2023-01-06 | 1 |
| 2023-01-09 | 1 |
| 2023-01-10 | 1 |
| 2023-01-11 | 1 |
| 2023-01-12 | 1 |
| 2023-01-13 | 1 |

## Gate

- `hard_pass`: PASS
