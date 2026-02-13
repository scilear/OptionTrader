# Decision Log

## 2026-02-13
- Use Streamlit for v1 UI
- Use DuckDB for v1 storage
- Data source: yfinance (upgrade path to IBKR later)
- Universe: SPX only
- Horizon: 14–60 DTE
- Signal-first workflow (alerts before structures)
- Pessimistic pricing gate required
- Tiered IV validity rule with spread gate (15%)
