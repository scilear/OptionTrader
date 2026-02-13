from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd

from src.db.connection import connect


@dataclass
class RegimeParams:
    rv_window: int = 20
    dd_window: int = 63
    calm_pct: float = 40.0
    stress_pct: float = 80.0
    dd_calm: float = 5.0
    dd_stress: float = 10.0


def compute_regime_state(params: RegimeParams | None = None) -> int:
    logger = logging.getLogger("regime")
    params = params or RegimeParams()

    conn = connect()
    try:
        snapshots = conn.execute(
            """
            SELECT ts, spot
            FROM snapshots
            ORDER BY ts
            """
        ).fetchdf()
        if snapshots.empty:
            logger.info("no snapshots for regime")
            return 0

        snapshots["date"] = pd.to_datetime(snapshots["ts"]).dt.date
        daily = snapshots.sort_values("ts").groupby("date").tail(1)
        daily = daily.set_index(pd.to_datetime(daily["date"]))
        daily["ret"] = daily["spot"].pct_change()
        daily["rv20"] = daily["ret"].rolling(params.rv_window).std() * (252 ** 0.5)
        rolling_high = daily["spot"].rolling(params.dd_window).max()
        daily["drawdown"] = (daily["spot"] / rolling_high - 1.0) * -100.0

        rv_pct = daily["rv20"].rank(pct=True) * 100.0
        dd_pct = daily["drawdown"].rank(pct=True) * 100.0

        daily["rv_pct"] = rv_pct
        daily["dd_pct"] = dd_pct

        inserts = 0
        for idx, row in daily.iterrows():
            if pd.isna(row["rv20"]) or pd.isna(row["drawdown"]):
                continue

            vix_pct = float(row["rv_pct"])
            rv20_pct = float(row["rv_pct"])
            drawdown = float(row["drawdown"])

            score = 0
            score += 0 if vix_pct < params.calm_pct else (1 if vix_pct < params.stress_pct else 2)
            score += 0 if rv20_pct < params.calm_pct else (1 if rv20_pct < params.stress_pct else 2)
            score += 0 if drawdown < params.dd_calm else (1 if drawdown < params.dd_stress else 2)

            regime_label = "Calm" if score <= 2 else ("Transition" if score <= 4 else "Stress")

            conn.execute(
                """
                INSERT INTO regime_state (
                    regime_date, vix_percentile, rv20_percentile, drawdown_percent,
                    regime_score, regime_label
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(regime_date) DO UPDATE SET
                    vix_percentile=excluded.vix_percentile,
                    rv20_percentile=excluded.rv20_percentile,
                    drawdown_percent=excluded.drawdown_percent,
                    regime_score=excluded.regime_score,
                    regime_label=excluded.regime_label
                """,
                (
                    idx.date(),
                    vix_pct,
                    rv20_pct,
                    drawdown,
                    score,
                    regime_label,
                ),
            )
            inserts += 1

        logger.info("regime rows updated=%s", inserts)
        return inserts
    finally:
        conn.close()
