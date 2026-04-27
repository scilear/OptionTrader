# OptionTrader Decision Paths (Path-Based Reconstruction)

## 1. System Overview

This system is an options-volatility signal pipeline for SPX-like underlyings that turns raw option quotes into:

- a normalized volatility surface view (`ATM`, `RR25`, `RR10`, `FLY25`, `FLY10`, `term slope`)
- statistically filtered anomaly alerts (`RR_EXTREME`, `FLY_EXTREME`, `TERM_KINK`)
- regime-aware triage labels and draft trade templates
- reviewer-facing dashboards and export artifacts

At a high level, the reasoning path is:

`Market quotes -> quote QC -> IV solve per contract -> delta-bucket surface points -> cross-time z-score tests -> persistence + worst-case gate + regime filter -> alert + trade-idea records -> UI decision worksheet`

Core persistence is DuckDB tables in `src/db/schema.sql`:

- `snapshots`, `option_quotes`, `iv_points`, `surface_metrics`, `regime_state`, `alerts`, `trade_ideas`

## 2. Entry Points / Use Cases

### Use Case: End-to-end pipeline run (daily/cron)

Entry points: `scripts/run_pipeline.py`, `scripts/run_pipeline_and_notify.sh`

**Goal**

- Produce a fresh snapshot analysis and alert set from latest option-chain data.

**Inputs**

- Config (`OPTIONTRADER_CONFIG`, default `config/config-v1.yaml`)
- Source availability (IB hosts and/or yfinance)
- Underlying setup (`data.underlying`, DTE band, quality gates, alert thresholds)

**Execution Flow (Step-by-Step)**

Step 1 - Data ingestion  
-> `run_ingest` tries IB first, then yfinance fallback  
-> IB path: only expiries in configured DTE window, strikes around spot, per-quote QC  
-> yfinance path: pulls chains by expiry, inserts only QC-valid quotes  
-> Assumption: bid/ask are usable for IV inference after QC

Step 2 - Preprocessing  
-> Snapshot loaded (`ts`, `spot`)  
-> Existing outputs for that snapshot are purged (idempotent recompute)  
-> Quotes are DTE-filtered again before metrics (`dte_min..dte_max`)  
-> Tradability score is computed from median relative spread

Step 3 - Core computations  
-> Per quote: solve mid/bid/ask IV (Black-Scholes inversion)  
-> Per expiry: choose ATM by nearest forward strike; choose +/-25d and +/-10d by nearest delta  
-> Build metrics per expiry bucket:

- `rr25_mid = iv(+25C)-iv(-25P)`
- `fly25_mid = (iv(+25C)+iv(-25P))/2 - iv(ATM)`
- analogous 10d measures + "worst" variants using ask/bid pessimistic legs
- `term_slope = ATM(bucket) - ATM(next bucket)`

Step 4 - Decision logic  
-> Alert candidate if absolute z-score exceeds threshold (default 2.0)  
-> Must persist for required consecutive snapshots (default 2)  
-> Must also pass worst-case z-score threshold (`*_worst`)  
-> Must have confidence tier for that bucket (`Core`/`Full`)  
-> Additional policy: reject `RR_EXTREME` when regime is `Stress`

Step 5 - Output generation  
-> Persist `iv_points`, `surface_metrics`, `alerts`  
-> Generate template trade ideas per alert and persist pricing/greeks/risk-flags  
-> Cron wrapper optionally sends Telegram summary of latest alerts

### Use Case: Interactive alert review and decisioning

Entry points: `scripts/run_streamlit.sh`, `src/app/streamlit_app.py`

**Goal**

- Let a reviewer inspect alerts, validate gate evidence, and produce a final decision/export.

**Inputs**

- Existing DB state (pipeline outputs)
- User filters (alert type, tier, regime, severity, tradability)
- Manual worksheet inputs (thesis, rationale, invalidation, risk sizing)

**Execution Flow (Step-by-Step)**

Step 1 - Data ingestion  
-> UI reads from DB tables only; no market fetch in this path

Step 2 - Preprocessing  
-> Alerts are filtered by user criteria  
-> Metrics page constructs continuous/segmented time series for selected metric + bucket

Step 3 - Core computations  
-> For alert detail, UI recomputes a decision summary using five gates:

- Signal, Data, Regime, Execution, Risk

-> Event-study page computes reversion stats from metric time series

Step 4 - Decision logic  
-> Proposed label logic:

- `Reject` if Signal fails or Risk fails or Regime fails
- `Research only` if Data fails or Execution fails
- `Watch for confirmation` if Regime/Risk neutral
- else `Trade now`

-> Final label is blocked unless worksheet gate passes (required rationale/invalidation/thesis and, for actionable labels, positive max loss + size)

Step 5 - Output generation  
-> CSV downloads for alert/metric tables  
-> JSON trade export only when worksheet gate = PASS

### Use Case: Recompute past snapshots with current logic

Entry points: `scripts/replay_last.py`, `src/core/replay.py`

**Goal**

- Re-evaluate recent snapshots after logic/config changes.

**Inputs**

- Last N snapshots (default 20) from DB

**Execution Flow**

1. Load recent snapshot IDs in chronological order
2. For each snapshot, rerun full compute path with purge
3. Replace alerts/ideas for each replayed snapshot
4. Output count of replayed snapshots

### Use Case: Single-chain diagnostics (ad hoc)

Entry points: `tools/option_chain.py`, `tools/parse_chain.py`

**Goal**

- Inspect one chain's IV/Greeks/liquidity flags and implied move quickly.

**Inputs**

- Ticker, target DTE/expiry, optional delta band, output format

**Execution Flow**

1. Fetch via IB if possible, else yfinance
2. Compute per-contract IV + Greeks + stale/wide-spread flags
3. Derive ATM IV and IV-rank proxy vs RV history
4. Optional delta filter
5. Output table/json/csv; `parse_chain` summarizes ATM straddle and implied move

### Use Case: IV rank and term-structure scan

Entry point: `tools/iv_rank.py`

**Goal**

- Classify current vol as elevated/depressed/neutral and show ATM term structure.

**Inputs**

- Ticker, lookback window, cache/IB flags

**Execution Flow**

1. Spot from IB if available else yfinance
2. Historical closes -> rolling RV series
3. yfinance option expiries -> ATM IV near target DTE buckets
4. Compute IV rank / percentile against RV proxy distribution
5. Emit signal (`elevated`, `depressed`, `neutral`, `n/a`)

### Use Case: Multi-ticker earnings vol screen

Entry point: `tools/earnings_screener.py`

**Goal**

- Batch compare tickers on pre-event vol richness and implied move.

**Inputs**

- Ticker list, target DTE, output mode

**Execution Flow**

1. Parallel call into `iv_rank.py` + `option_chain.py` per ticker
2. Derive front IV, RV, IV/RV, ATM straddle implied move
3. Sort and print ranked table
4. Optional "full" mode includes straddle pricing detail

## 3. Decision Trees

### A) Data-source routing

- If any configured IB host reachable and IB ingest succeeds -> use IB
- Else -> fallback to yfinance
- If both fail -> pipeline errors out

### B) Quote acceptance (ingestion QC)

- If bid/ask missing -> reject
- Else if bid > ask (crossed) -> reject
- Else if bid <= 0 and zero-bid not allowed -> reject
- Else -> accept (even if wide spread; wide spread is flagged, not rejected)

### C) Surface confidence tier

- If ATM, +25C, -25P all quality=1 -> `Core`
- If `Core` and +10C and -10P also quality=1 -> `Full`
- Else -> no tier (alerts from that bucket later skipped)

### D) Alert generation per metric/bucket

- If |z_mid| < threshold -> no alert
- Else if persistence streak < required snapshots -> no alert
- Else if worst-case series exists and |z_worst| < threshold -> no alert
- Else -> alert candidate

### E) Regime policy override

- If alert type is `RR_EXTREME` and regime=`Stress` -> drop alert
- Else -> keep alert

### F) Streamlit review label

- If Signal fail or Risk fail or Regime fail -> `Reject`
- Else if Data fail or Execution fail -> `Research only`
- Else if Regime neutral or Risk neutral -> `Watch for confirmation`
- Else -> `Trade now`

### G) Export gate

- If worksheet incomplete -> block export (`Blocked - complete worksheet`)
- Else -> allow JSON trade export

## 4. Algorithms (Only Meaningful)

### Algorithm: Implied vol solver (bisection on Black-Scholes)

**Purpose**  
Recover IV from observed option price.

**Formulation**  
Find `sigma` such that `BSPrice(sigma)=market_price` with bounds `[1e-4, 5.0]`.

**Logic**

1. Reject invalid price/time/spot/strike
2. Reject below intrinsic or outside price bounds at min/max vol
3. Bisection until tolerance or max iterations

**Why this method**  
Robust monotonic root-finding without Newton instability.

**Limitations**

- Uses European BS assumptions
- Fixed rate/dividend in core pipeline (`0.0`, `0.0`)
- No discrete dividends, no microstructure model

### Algorithm: Delta-bucket surface extraction

**Purpose**  
Convert noisy chain into comparable smile points.

**Logic**

1. ATM = strike closest to forward
2. For each target delta (`+0.25C`, `-0.25P`, `+0.10C`, `-0.10P`), pick nearest available contract by absolute delta distance
3. Compute RR/FLY/term metrics from these anchors

**Limitations**

- Nearest-neighbor selection, no interpolation/smoothing
- Bucket can map to a single expiry nearest target DTE (not blended)

### Algorithm: Alert detection with pessimistic gate

**Purpose**  
Detect statistically extreme shape changes while penalizing execution slippage.

**Formulation**

- `z = (latest - mean(window))/std(window)`
- Trigger if `|z_mid|>=threshold` AND persistence streak satisfied
- Also require `|z_worst|>=threshold` when worst series available

**Why this method**  
Simple anomaly detector, adds persistence and execution realism.

**Limitations**

- Gaussian-style z-score assumptions
- Sensitive to small sample variance and regime shifts
- No robust estimators/winsorization

### Algorithm: Regime scoring

**Purpose**  
Classify market context to suppress fragile signals.

**Logic**

- Compute daily RV20 and drawdown from snapshot spot history
- Convert to percentiles
- Score each component 0/1/2 by calm/stress cutoffs
- Sum -> `Calm` / `Transition` / `Stress`

**Limitations**

- In current code, VIX percentile field is populated from RV percentile (proxy), not true VIX feed
- Thresholds in config are not wired into runtime parameters

## 5. Financial Interpretation

- `RR_EXTREME`: skew dislocation signal (put-vs-call wing vol imbalance); template is put-spread skew fade.
- `FLY_EXTREME`: convexity/curvature dislocation around ATM; template is 1x2x1 fly structure.
- `TERM_KINK`: abnormal near/far ATM vol slope; template is ATM calendar.

A "valid" opportunity in system terms is not just extreme z-score. It is:

`statistical extremeness + persistence + worst-case consistency + acceptable regime + tradability + presentable structure template`

So the system is targeting reversion/normalization opportunities under liquidity and regime constraints, not directional forecasting.

## 6. Assumptions (Critical)

### Explicit

- `z_threshold`, persistence snapshots, DTE range, spread gate from config (`config/config-v1.yaml`)
- IB-first ingestion with yfinance fallback
- Black-Scholes pricing framework
- Tradability proxied by median relative spread

### Implicit (inferred from code)

- European-style option model is "good enough" for listed chain screening
- Mid/bid/ask IVs are stable enough for cross-time z-scores
- Nearest-delta contract approximates intended delta bucket
- One nearest expiry per bucket is representative of that tenor
- Worst-case gate approximates executable pessimism
- Regime suppression mainly matters for skew signals (RR in Stress)

## 7. Failure Modes & Blind Spots

- **Config drift risk**: `alerts.pessimistic_gate`, `quality.min_valid_points_*`, `regime.*`, and `structures.*` are defined but not effectively driving core logic in current paths.
- **Regime proxy issue**: regime uses RV percentile for both VIX and RV fields (can mislabel context).
- **No arbitrage checks**: no static smile or term no-arbitrage constraints enforced.
- **Sparse-liquidity distortion**: wide spreads are flagged but quotes still accepted; quality filtering is partial.
- **Nearest-point bias**: no interpolation can produce jumpy bucket metrics.
- **Rate/dividend simplification**: hardcoded to zero in pipeline computations.
- **IV rank proxy mismatch**: tools compare IV to realized vol history, not historical IV distribution.
- **Data-source inconsistency**: IB ingestion pre-filters by DTE; yfinance may ingest all expiries then filter later.
- **Execution realism gap**: trade ideas are templates with theoretical prices/greeks; no slippage/fees/assignment modeling.

## 8. Gaps / Unknowns

- `Unknown`: Intended production snapshot cadence and required minimum history for stable z-scores.
- `Unknown`: Whether alerts are expected to be acted automatically or only manually via Streamlit.
- `Unknown`: Whether `TERM_KINK` and `FLY_EXTREME` should also have regime-specific suppression rules.
- `Unknown`: Target performance benchmarks (precision/recall of alerts, PnL attribution).
- `Unknown`: Whether downstream OMS/execution integration exists outside this repo.

## 9. Reviewer Checklist (Logical Audit)

- [ ] Are quote rejection rules strict enough for illiquid tails, or should wide-spread quotes be excluded (not just flagged)?
- [ ] Is IV solved consistently (mid/bid/ask) and are invalid statuses tracked through to final metrics?
- [ ] Are delta buckets selected robustly when chains are sparse?
- [ ] Is bucket mapping (nearest expiry only) acceptable, or should interpolation across tenors be required?
- [ ] Are no-arbitrage checks (smile monotonicity/convexity, calendar consistency) enforced anywhere?
- [ ] Is the worst-case gate always intended, or should it be controlled by `pessimistic_gate` config?
- [ ] Do regime labels rely on intended signals (true VIX vs RV proxy)?
- [ ] Are configured regime thresholds actually applied at runtime?
- [ ] Are alert thresholds/persistence calibrated per metric and regime, or globally hardcoded?
- [ ] Are deep ITM/OTM and near-expiry edge cases handled safely in IV solving?
- [ ] Is tradability scoring sufficient for real execution constraints (depth, size, slippage)?
- [ ] Are trade-idea templates aligned with alert economics and risk limits (not just generated)?
- [ ] Does replay preserve reproducibility across logic/config changes?
- [ ] Are Telegram/ops notifications complete enough for incident response when pipeline fails?
