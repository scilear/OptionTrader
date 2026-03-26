# Decision Log

## 2026-03-26
- Added standalone tools layer (`tools/`) — DB-free, run independently of pipeline
- IB Gateway integration added as primary data source for option chain and spot price; yfinance retained as fallback
- IV rank uses RV-proxy (rolling 21D realized vol) rather than stored historical IV — avoids needing a separate IV history store; labeled clearly as "RV proxy" in all output
- Theta implemented directly in `option_chain.py` rather than in `iv_solve.py` to keep tool self-contained
- Tool client_id convention: pipeline uses `client_id` from config (default 10); tools use `client_id + 5` to avoid TWS conflicts
- 1-day file cache for historical closes in `data/cache/` to keep iv_rank fast on repeated calls

## 2026-02-13
- Use Streamlit for v1 UI
- Use DuckDB for v1 storage
- Data source: yfinance (upgrade path to IBKR later)
- Universe: SPX only
- Horizon: 14–60 DTE
- Signal-first workflow (alerts before structures)
- Pessimistic pricing gate required
- Tiered IV validity rule with spread gate (15%)
