# Implementation Spec v1 (Streamlit)

## Scope
- Single-user local app
- Underlying: SPX only
- Horizon: 14–60 DTE
- Signal-first alerts, 2–3 structure suggestions
- Execution realism: optimistic (mid) and pessimistic (bid/ask) pricing

## Non-Goals (v1)
- Automated order routing
- 0–7 DTE strategies
- American options / assignment logic
- Arbitrage promises
- Full 3D surface visualization

## Stack (v1)
- UI: Streamlit
- Storage: DuckDB or SQLite (single file)
- Ingestion: separate Python job (cron/APS) that writes snapshots
- Computation: Python modules (IV solve, metrics, alerts)

## Data Contracts

### Snapshot
- ts (timestamptz)
- underlying (string)
- spot (float)
- source (string)
- session_tag (string: eod/open/mid/event)
- notes (string, optional)

### Option Quote
- snapshot_id (fk)
- expiry (date)
- strike (float)
- right (C/P)
- bid (float)
- ask (float)
- last (float)
- bid_size (int)
- ask_size (int)
- oi (int)
- volume (int)
- flags (json)

## Ingestion Policy
- Capture all expiries when configured to support future analysis
- DTE filtering can be applied downstream in metrics/alerts

### IV Point (delta grid)
- snapshot_id (fk)
- expiry (date)
- delta_bucket (ATM, +0.25C, -0.25P, +0.10C, -0.10P)
- iv_mid (float)
- iv_bid (float)
- iv_ask (float)
- solve_status (valid/stale/wide/no-bid)
- quality_score (0-1)

### Surface Metrics (per expiry bucket)
- snapshot_id (fk)
- expiry_bucket (e.g., 21D, 30D, 45D)
- atm_iv_mid
- rr25_mid, rr10_mid
- fly25_mid, fly10_mid
- term_slope_mid (front vs back)
- pessimistic versions: *_worst

### Regime State (daily)
- date
- vix_percentile
- rv20_percentile
- drawdown_percent
- regime_score (0-6)
- regime_label (Calm/Transition/Stress)

## Core Metrics

### ATM IV
- ATM-forward strike (K ~= F) or 50-delta vol

### Risk Reversal
- RR_d(T) = IV_call(+d,T) - IV_put(-d,T)
- d in {0.25, 0.10}

### Fly (Curvature)
- Fly_d(T) = 0.5*(IV_call(+d,T) + IV_put(-d,T)) - IV_ATM(T)
- d in {0.25, 0.10}

### Term Slope (ATM)
- TS_ATM(T1,T2) = IV_ATM(T1) - IV_ATM(T2)

### Event Premium (variance)
- Var(T) = IV_ATM(T)^2 * T
- Var_event = Var(T_e) - linear_interp(Var(T_-), Var(T_+))

### Z-Scores
- Compute per expiry bucket with rolling window (default 60d)

## Data Quality and Validity Gates

### Quote QC
- Exclude crossed quotes (bid > ask)
- Exclude zero bid unless explicitly allowed
- Flag wide spreads

### IV Validity Tiers (per expiry)
Tier Full:
- All 5 delta points valid
- Spread gate: (ask-bid)/mid <= 15% for each point
- Alerts: RR/Fly/Term (full)

Tier Core:
- ATM + both 25D points valid
- Spread gate <= 15%
- Alerts: RR25/Fly25/Term only
- Suppress any 10D-dependent structures

Tier None:
- ATM or 25D points missing or wide
- No alerts

## Regime Model (v1)
- VIX percentile (1Y): Calm < 40, Neutral 40–80, Stress > 80
- RV20 percentile (1Y)
- Drawdown from 3-month high: <5 / 5–10 / >10
- Regime score = sum(0/1/2) => Calm 0–2, Transition 3–4, Stress 5–6

## Alert Logic (v1)
- Persistence: signal must hold across >= 2 snapshots/days
- Pessimistic gate: alert suppressed if z-score fails under worst-case pricing
- Regime filter: no skew selling in Stress
- Tradability score: median spread vs spread gate (0-1)

Alert Types:
- RR_EXTREME: |Z_RR25| > 2.0
- FLY_EXTREME: |Z_Fly25| > 2.0
- TERM_KINK: |Z_TS_ATM| > 2.0

## Signal Behavior Details

### RR_EXTREME
- Trigger when Z_RR25 <= -2.0 (puts rich) or >= +2.0 (calls rich)
- Optional momentum guard: 3-day Z change >= -0.5 for skew selling
- Suppress in Stress regime

### FLY_EXTREME
- Trigger when Z_Fly25 >= +2.0 (wings rich) or <= -2.0 (wings cheap)
- Suppress if |Z_RR25| > 2.0 (avoid skew contamination)

### TERM_KINK
- Trigger when |Z_TS_ATM| >= 2.0 (front vs back dislocation)
- If event week, require variance premium > threshold

## Trade Mapping (Phase 1)
- RR_EXTREME -> bounded skew fade (25D put spread, optional call spread)
- FLY_EXTREME -> fly or broken-wing fly
- TERM_KINK -> ATM calendar (front sell, back buy)

## Structure Selection Rules (v1)

### Bounded Skew Fade
- Short put at ~25D, long put at ~10D
- Optional: add call spread for financing if bid/ask allows
- Use Tier Core or Full only

### Fly / Broken-Wing Fly
- Center at ATM-forward
- Wings around 25D (or symmetric log-moneyness)
- Use Tier Full only if 10D wings needed

### ATM Calendar
- Front: 14–30 DTE
- Back: 30–60 DTE
- Delta-match at entry, use ATM-forward strike

## Execution Realism
- Optimistic: use mids
- Pessimistic: buy at ask, sell at bid, leg-by-leg
- Suppress alerts/trades if edge fails under pessimistic pricing

## Logging
- All entrypoints must emit step-level logs (ingest, compute, pipeline)
- Log to stdout and file with timestamped structured format
- Log key counts (snapshots, quotes, iv_points, metrics, alerts)

## Acceptance Tests
- AT-01: crossed/zero-bid quotes excluded
- AT-02: IV solve valid for required tier before alerts
- AT-03: pessimistic pricing gate suppresses ghost alerts
- AT-04: replay determinism (same snapshot => same metrics/alerts)
- AT-05: every alert includes regime label and confidence tier

## Deliverables (v1)
- Ingestion job
- Metrics pipeline
- Alert engine
- Trade idea generator
- Streamlit UI: alerts, metrics explorer, alert detail
- Replay/backtest
