# Functional Test Plan (Manual)

## Setup

### Test DB (seeded)
```bash
source .venv/bin/activate
python scripts/seed_test_db.py --reset
```

Run Streamlit with test DB by setting config path:
```bash
export OPTIONTRADER_CONFIG=config/config-v1.yaml
streamlit run src/app/streamlit_app.py
```

### Main DB (live ingest)
```bash
source .venv/bin/activate
python scripts/run_pipeline.py
streamlit run src/app/streamlit_app.py
```

---

## Alerts Dashboard
**Goal:** Validate alerts display + filtering + CSV export.

### Test DB Expected
- At least 2 alerts present (RR_EXTREME, FLY_EXTREME)
- Filters update table correctly
- Min severity + tradability sliders reduce results
- Download alerts CSV produces file with columns

### Main DB Expected
- Alerts may be empty (acceptable)
- Filters still work (no errors)
- CSV download works even if empty

---

## Metric Explorer
**Goal:** Validate time series charts and CSV export.

### Test DB Expected
- rr25_mid / fly25_mid / term_slope_mid chart renders
- Event premium chart renders
- CSV download works for each metric

### Main DB Expected
- Charts render if data exists, else “No metric data” message

---

## Alert Detail
**Goal:** Validate explainability + trade ideas + export.

### Test DB Expected
- Explainability JSON visible
- Trade ideas table shows legs + risk flags
- Download trade idea JSON works

### Main DB Expected
- If alerts exist, same behavior
- If no alerts, no errors

---

## Replay
**Goal:** Validate snapshot coverage and alert counts.

### Test DB Expected
- 3 snapshots shown
- Alert count > 0 for last snapshot

### Main DB Expected
- Snapshot list shows most recent data

---

## Event Study
**Goal:** Validate reversion stats and regime breakdown.

### Test DB Expected
- Events, hit rate, median reversion days shown
- By regime table appears if regime_state exists

### Main DB Expected
- If data exists, stats render
- If data not enough, show “No data” message

---

## Health
**Goal:** Validate pipeline counts.

### Test DB Expected
- Counts show snapshots/quotes/metrics/alerts
- Latest snapshot info visible

### Main DB Expected
- Counts match latest run
- Latest snapshot info visible

---

## Pass/Fail Criteria
- No uncaught exceptions during navigation
- UI renders consistently for empty + non-empty data
- Exports produce valid files
- All expected seeded alerts appear in test DB
