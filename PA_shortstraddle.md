# PA Short Straddle and Put Credit Spread - Backtest and Screening Plan

## 1) Strategy rules from the two PDFs (encode both with equal depth)

Source files:
- `ressources/Strategy Profitability & Options.pdf`
- `ressources/Structuring and Managing Your Trades.pdf`

### 1.1 Strategy A: Short ATM straddle (30 DTE) with daily delta hedge

Entry and structure:
- Sell ATM call and ATM put at the same strike and expiration.
- Target nearest 30 DTE contract (tolerance band 25-35 DTE for implementation).
- Use VIX gate at 40 for risk control.

Management and lifecycle:
- Hedge once per day near market close to bring net position delta toward neutral.
- Flatten hedge shares before opening the next cycle.
- Close manually before expiration (no assignment).
- Immediately roll into next 30 DTE cycle if gate conditions pass.

Risk and sizing:
- Treat as undefined-risk structure with strict margin controls.
- Target 20-40% margin utilization for this strategy sleeve, hard cap at 50%.
- Include 20% underlying shock stress test before order approval.

### 1.2 Strategy B: Put credit spread (30/10 delta, 30 DTE)

Entry and structure:
- Sell ~30 delta put and buy ~10 delta put in same expiration.
- Target nearest 30 DTE contract (use closest liquid monthly if exact 30 DTE is unavailable).
- Use closest available deltas if exact values are missing.

Management and lifecycle:
- No daily delta hedge in baseline process.
- If near max profit (~70-80% of credit), close early and re-enter new 30 DTE spread.
- If 1-2 days to expiration and short put is ITM, close and roll to avoid assignment.
- If worthless at expiration, allow expiration and re-enter the next cycle.

Risk and sizing:
- Treat as defined-risk strategy; risk per trade is spread width minus net credit.
- Position sizing is based on max portfolio drawdown tolerance (example in PDF: 20% max drawdown window).
- Track portfolio-level concurrent max-loss sum and cap at configured budget.

### 1.3 Shared thesis and shared constraints

- Both structures seek to monetize the variance risk premium (IV tends to exceed realized vol).
- Both must use documented assumptions for slippage, commissions, and contract selection.
- Both must be simulated with full time-series outputs (daily PnL and trade/event logs in CSV).


## 2) Data inventory from `/mnt/Data/dolt_data/options`

Tables found:
- `option_chain`
- `volatility_history`

Schema highlights:
- `option_chain`: `date`, `act_symbol`, `expiration`, `strike`, `call_put`, `bid`, `ask`, `vol`, `delta`, `gamma`, `theta`, `vega`, `rho`.
- `volatility_history`: `date`, `act_symbol`, `hv_current`, `hv_week_ago`, `hv_month_ago`, `hv_year_high/low`, `iv_current`, `iv_week_ago`, `iv_month_ago`, `iv_year_high/low`.

Observed coverage (from Dolt SQL checks):
- `option_chain` date range: `2019-02-09` to `2026-05-21`.
- `option_chain` on `2026-05-21`: `109,450` rows, `0` missing bid/ask, `0` missing delta.
- `volatility_history` total rows: `1,808,151`, range `2019-02-09` to `2026-05-21`.
- `volatility_history` on `2026-05-21`: `1,528` symbols; `99` rows missing `iv_current`, none missing `hv_current`.
- ETF basket overlap on `2026-05-21` confirmed for `SPY` and `DIA`; full historical overlap audit still required for `IWM`, `QQQ`, `GLD`.
- No VIX symbol found in `volatility_history`.

Implications:
- Core option and IV/HV simulation is feasible directly from this DB.
- PDF-faithful VIX(>40) gate requires external VIX daily close series added to local data.


## 3) Backtest design (equal detail for both strategies)

### 3.1 Shared engine foundation

- Simulation frequency: daily EOD snapshots.
- Contract selection: deterministic rules only (no manual overrides).
- Transaction costs: baseline run with 50% spread cross on entry, then sensitivity runs adding exit and hedge slippage plus commissions.
- Accounting mode: event-driven trade ledger + daily mark-to-market.

### 3.2 Strategy A simulation spec (hedged short straddle)

Per symbol cycle:
1. Select target expiration nearest 30 DTE.
2. Select ATM strike (min distance to spot; tie-breaker abs(call_delta-0.50)).
3. Apply entry gates (VIX, liquidity, data quality).
4. Open short call + short put.
5. Daily rebalance hedge shares once near close.
6. Mark option and hedge PnL daily.
7. Close before expiration and flatten shares.
8. Re-enter next valid cycle.

Required metrics:
- Option PnL, hedge PnL, total PnL.
- Daily net delta before/after hedge.
- Hedge turnover and realized hedge slippage.
- Margin proxy and stress losses under +/-20% move.

### 3.3 Strategy B simulation spec (put credit spread)

Per symbol cycle:
1. Select target expiration nearest 30 DTE.
2. Select short put near delta 0.30 and long put near delta 0.10.
3. Apply entry gates (liquidity, data quality, optional VIX gate for factor test).
4. Open spread for net credit.
5. Monitor daily for early-profit exit or ITM-expiry-risk roll condition.
6. Close or expire per rule, then re-enter next valid cycle.

Required metrics:
- Net credit, max risk, realized PnL.
- Early-close frequency and roll frequency.
- Max-risk utilization over time and drawdown path.
- Return-on-risk and loss distribution at trade level.

### 3.4 Factor matrix (run for both strategies)

- Gate variants: with/without VIX gate; threshold sensitivity (`35`, `40`, `45`).
- Universe variants: single ticker vs ETF basket.
- DTE variants: nearest 21/30/45.
- Execution variants: mid vs spread-cross + commissions.
- Management variants:
  - Straddle: daily hedge vs less frequent hedge.
  - Put spread: hold-to-expiry vs early-profit close.


## 4) CSV time-series outputs (mandatory for no-rerun filtering)

All simulations must persist run outputs under:
- `artifacts/simulations/<run_id>/`

### 4.1 Core CSV files

- `daily_pnl_timeseries.csv`
  - One row per `date x strategy x symbol x trade_id`.
  - Columns: `run_id,date,strategy,symbol,trade_id,option_pnl,hedge_pnl,total_pnl,cum_pnl,margin_used,max_risk,vix_close,iv_current,hv_current`.

- `trades_timeseries.csv`
  - One row per completed trade lifecycle.
  - Columns: `run_id,trade_id,strategy,symbol,entry_date,exit_date,entry_dte,entry_expiration,entry_credit,max_risk,exit_reason,realized_pnl,return_on_risk,days_held`.

- `trade_events_timeseries.csv`
  - Event log for reproducibility.
  - Columns: `run_id,trade_id,date,event_type,event_price,event_qty,fees,slippage,notes`.
  - `event_type` includes `ENTRY`, `HEDGE`, `REBALANCE`, `ROLL`, `EXIT`.

- `eligibility_timeseries.csv`
  - One row per `date x strategy x symbol x candidate` with gate decisions.
  - Columns: `run_id,date,strategy,symbol,expiration,strike_short,strike_long,gate_vix_pass,gate_liquidity_pass,gate_data_pass,gate_margin_pass,fail_reason`.

### 4.2 Why this solves filter/gate experiments

- You can test new filters by subsetting `eligibility_timeseries.csv` and mapping to `trade_id`.
- You can recompute filtered performance by aggregating existing `daily_pnl_timeseries.csv` rows for kept `trade_id` values.
- You can ignore rejected trades without rerunning pricing or hedge simulation.

### 4.3 Additional recommended CSV files

- `positions_eod_timeseries.csv` (position state and Greeks by day).
- `features_timeseries.csv` (all ranking features and raw inputs).
- `run_manifest.json` (parameter hash, data snapshot date range, code version).


## 5) Screening information process (two-strategy production flow)

### 5.1 Daily feature build (shared)

Per symbol-date-expiry candidate:
- Liquidity: spread width, spread as % of mid, strike density around target deltas.
- Volatility context: `iv_current`, `hv_current`, `iv_current - hv_current`, IV percentile proxy.
- Structural features: ATM premium, expected move proxy, skew around ATM/put wing.
- Risk features: gamma/theta/vega concentration and jump-risk proxies.

### 5.2 Strategy-specific candidate builder

- Straddle candidates:
  - ATM strike map, hedge burden estimate, margin/stress eligibility.

- Put spread candidates:
  - 30/10 delta pair quality, width/credit efficiency, max-risk efficiency.

### 5.3 Hard filters and ranking

- Hard filters: data completeness, quote quality, DTE availability, margin/risk caps, VIX gate (configurable by strategy).
- Ranking:
  - Straddle score: VRP strength + liquidity - hedge burden - tail risk.
  - Put spread score: credit/max-risk efficiency + VRP strength + liquidity - downside stress risk.

### 5.4 Daily outputs

- `screen_candidates` table for each strategy.
- `trade_plan` table with selected strikes/expiry and projected risk.
- `risk_report` table with strategy and portfolio limits.


## 6) Data gaps and required additions

Must-have before final PDF-faithful comparisons:
- Add VIX daily close series into Dolt and join by `date`.
- Complete symbol/date overlap audit for `SPY`, `IWM`, `QQQ`, `DIA`, `GLD` across both tables.
- Add or confirm underlying close series for accurate hedge/share PnL and assignment-risk logic.

Quality controls to implement:
- Coverage heatmap by symbol and month.
- Missing quote/Greek diagnostics.
- Expiration availability diagnostics near 30 DTE.


## 7) Detailed implementation sprints (tasks + acceptance criteria)

Engineering best practices applied to all phases:
- Single source of truth in config files (no hidden constants in code).
- Typed Python interfaces, docstrings on public functions, and deterministic logic.
- Unit tests + integration tests + regression snapshots.
- Idempotent data pipelines with explicit data quality checks and fail-fast behavior.
- Artifact versioning via `run_id` + `run_manifest.json` + immutable output folders.
- Clear separation of concerns: data access, strategy logic, simulation engine, reporting.

### Phase 1 - Data contracts and ingestion hardening

Goal:
- Make all required datasets available and contract-stable before simulation work.

Tasks:
- P1-T1: Add a VIX daily table in Dolt (`vix_daily`) with fields for `date`, `close`, and source metadata.
- P1-T2: Add or validate underlying daily close table (`underlying_prices_daily`) for hedge PnL and ITM checks.
- P1-T3: Build idempotent ingestion scripts for VIX and underlying prices (upsert behavior, no duplicates).
- P1-T4: Implement schema contract checks (required columns, types, non-null constraints where needed).
- P1-T5: Build completeness audit job for basket symbols (`SPY`, `IWM`, `QQQ`, `DIA`, `GLD`) across required date ranges.
- P1-T6: Build data quality report CSVs (null rates, stale values, date gaps, expiry availability near target DTE).

Acceptance criteria:
- AC1.1: All required tables exist and are queryable from Dolt.
- AC1.2: For every simulation date, one VIX close exists and can be joined by `date`.
- AC1.3: Underlying close data is present for all simulated symbols/dates used in hedge and assignment logic.
- AC1.4: Contract checks fail the pipeline when required fields are missing or invalid.
- AC1.5: A reproducible audit artifact set is produced (`coverage.csv`, `null_diagnostics.csv`, `dte_availability.csv`).

### Phase 2 - Shared simulation framework

Goal:
- Build a strategy-agnostic simulation core that writes stable, reusable time-series artifacts.

Tasks:
- P2-T1: Create simulation config model (YAML/JSON) with schema validation.
- P2-T2: Implement run orchestration (`run_id`, timestamp, parameter hash, code version capture).
- P2-T3: Build event ledger engine supporting `ENTRY`, `HEDGE`, `REBALANCE`, `ROLL`, `EXIT`.
- P2-T4: Build daily mark-to-market engine for option legs and hedge legs.
- P2-T5: Build CSV artifact writer with strict column schema and ordering.
- P2-T6: Implement portfolio accounting layer (cum PnL, margin proxy, max-risk usage).
- P2-T7: Add guardrail checks (duplicate trade IDs, negative DTE, missing required marks).

Acceptance criteria:
- AC2.1: A single run creates all mandatory artifacts in `artifacts/simulations/<run_id>/`.
- AC2.2: Two runs with identical config and data produce identical outputs (deterministic reproducibility).
- AC2.3: CSV schema checks pass for `daily_pnl_timeseries.csv`, `trades_timeseries.csv`, `trade_events_timeseries.csv`, `eligibility_timeseries.csv`.
- AC2.4: Engine rejects invalid state transitions (for example, `EXIT` before `ENTRY`).
- AC2.5: Integration tests validate event-to-PnL reconciliation on fixed fixtures.

### Phase 3 - Strategy modules (parity depth for both strategies)

Goal:
- Implement both strategies with equivalent rigor in lifecycle logic, risk controls, and metrics.

Tasks:
- P3-T1: Implement Short Straddle module:
  - 30 DTE selection, ATM strike selection, VIX gate.
  - Daily close delta hedge and hedge flattening on exit.
  - Pre-expiry close and immediate re-entry logic.
- P3-T2: Implement Put Credit Spread module:
  - 30/10 delta leg selection with nearest available fallback.
  - Early close at configurable profit threshold.
  - ITM near-expiry close-and-roll logic.
- P3-T3: Implement shared risk manager:
  - Margin/risk caps by strategy sleeve.
  - Stress checks and trade approval/rejection reasons.
- P3-T4: Implement strategy metrics calculators:
  - Trade-level and daily-level diagnostics for each strategy.
- P3-T5: Build unit tests for each decision rule and integration tests for full trade lifecycle.

Acceptance criteria:
- AC3.1: Both strategies generate valid trade lifecycles from the same simulation framework.
- AC3.2: Rule-specific tests pass for entry, management, exit, and roll conditions.
- AC3.3: Strategy parity is met: both output full PnL/trade/event/eligibility time-series with equivalent depth.
- AC3.4: Risk manager blocks trades that violate configured caps and logs precise `fail_reason`.
- AC3.5: No assignment paths are present in straddle baseline; spread assignment is proactively avoided by rule.

### Phase 4 - Screening and gating pipeline

Goal:
- Produce daily actionable candidate lists and decision traces for both strategies.

Tasks:
- P4-T1: Build shared feature generation layer (liquidity, VRP proxy, risk, structure features).
- P4-T2: Build strategy-specific candidate constructors (ATM map for straddle; 30/10 pairing for spread).
- P4-T3: Implement hard gates (data quality, liquidity, DTE availability, VIX, risk budget).
- P4-T4: Implement ranking models per strategy with explainable component scores.
- P4-T5: Write daily screening outputs (`screen_candidates`, `trade_plan`, `risk_report`).
- P4-T6: Add decision trace export so every included/excluded candidate has a reason code.

Acceptance criteria:
- AC4.1: Daily run generates screening outputs for both strategies without manual intervention.
- AC4.2: Every excluded candidate has explicit machine-readable gate failure reasons.
- AC4.3: Ranked candidates are reproducible under fixed config and data snapshot.
- AC4.4: Screening output can be joined to simulation artifacts by symbol/date/contract identifiers.
- AC4.5: Feature and ranking tests verify no leakage of future information.

### Phase 5 - Experimentation, post-hoc filtering, and reporting

Goal:
- Enable rapid what-if analysis from saved time series without recomputing core simulations.

Tasks:
- P5-T1: Build experiment runner for factor matrix (gate thresholds, DTE variants, execution models).
- P5-T2: Build post-hoc filter tool that reads `eligibility_timeseries.csv` and remaps kept `trade_id` values.
- P5-T3: Build re-aggregation utility for filtered performance from `daily_pnl_timeseries.csv` only.
- P5-T4: Build reporting pack generator (performance, stability, drawdown, turnover, replication gap).
- P5-T5: Add regression benchmark suite (baseline run hashes, key metric drift thresholds).
- P5-T6: Publish runbook for reproducible reruns and interpretation of outputs.

Acceptance criteria:
- AC5.1: At least one filter/gate what-if experiment runs end-to-end without rerunning pricing/hedge simulation.
- AC5.2: Reports include assumptions, date range, cost model, strategy config, and data snapshot metadata.
- AC5.3: Baseline metrics are reproducible and tracked for drift.
- AC5.4: Output bundle is sufficient for external review (CSV artifacts + manifest + report).
- AC5.5: CLI entrypoints and runbook allow a new operator to reproduce results from scratch.


## 8) Definition of done per phase gate

Gate 1 (after Phase 1):
- Required data exists, passes quality checks, and is contract-validated.

Gate 2 (after Phase 2):
- Shared engine produces deterministic, schema-valid artifacts with reconciled accounting.

Gate 3 (after Phase 3):
- Both strategies are live in simulation with parity depth and tested lifecycle behavior.

Gate 4 (after Phase 4):
- Screening outputs are reliable, explainable, and fully joinable to simulation artifacts.

Gate 5 (after Phase 5):
- Post-hoc filtering works from saved CSV time series; reporting is reproducible and decision-ready.
