from __future__ import annotations

import pandas as pd


def compute_tradability_score(quotes: pd.DataFrame, spread_gate_pct: float) -> float:
    if quotes.empty:
        return 0.0

    bids = quotes["bid"].astype(float)
    asks = quotes["ask"].astype(float)
    mids = (bids + asks) / 2
    valid = (bids > 0) & (asks > 0) & (mids > 0)
    if not valid.any():
        return 0.0

    spreads = (asks[valid] - bids[valid]) / mids[valid]
    median_spread = float(spreads.median()) if not spreads.empty else 1.0
    score = 1.0 - min(1.0, median_spread / spread_gate_pct) if spread_gate_pct > 0 else 0.0
    return max(0.0, score)
