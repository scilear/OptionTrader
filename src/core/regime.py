from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass

import pandas as pd

from src.core.config import load_config
from src.db.connection import connect


@dataclass
class RegimeParams:
    rv_window: int = 20
    dd_window: int = 63
    vix_pct_calm: float = 40.0
    vix_pct_stress: float = 80.0
    rv20_pct_calm: float = 40.0
    rv20_pct_stress: float = 80.0
    drawdown_calm: float = 5.0
    drawdown_stress: float = 10.0


def regime_params_from_config(config: dict | None = None) -> RegimeParams:
    cfg = config or load_config()
    regime_cfg = cfg.get("regime", {})
    return RegimeParams(
        vix_pct_calm=float(regime_cfg.get("vix_pct_calm", 40.0)),
        vix_pct_stress=float(regime_cfg.get("vix_pct_stress", 80.0)),
        rv20_pct_calm=float(regime_cfg.get("rv20_pct_calm", 40.0)),
        rv20_pct_stress=float(regime_cfg.get("rv20_pct_stress", 80.0)),
        drawdown_calm=float(regime_cfg.get("drawdown_calm", 5.0)),
        drawdown_stress=float(regime_cfg.get("drawdown_stress", 10.0)),
    )


def regime_threshold_hash(params: RegimeParams) -> str:
    payload = {
        "vix_pct_calm": params.vix_pct_calm,
        "vix_pct_stress": params.vix_pct_stress,
        "rv20_pct_calm": params.rv20_pct_calm,
        "rv20_pct_stress": params.rv20_pct_stress,
        "drawdown_calm": params.drawdown_calm,
        "drawdown_stress": params.drawdown_stress,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def compute_regime_state(params: RegimeParams | None = None) -> int:
    logger = logging.getLogger("regime")
    params = params or regime_params_from_config()
    thresholds_hash = regime_threshold_hash(params)

    conn = connect()
    try:
        existing_hash_row = conn.execute(
            """
            SELECT regime_config_hash
            FROM regime_state
            WHERE regime_config_hash IS NOT NULL
            ORDER BY regime_date DESC
            LIMIT 1
            """
        ).fetchone()
        if existing_hash_row and existing_hash_row[0] and existing_hash_row[0] != thresholds_hash:
            logger.warning(
                "Regime thresholds changed (config hash mismatch). Recompute regime_state history "
                "before relying on historical comparisons."
            )

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
            score += 0 if vix_pct < params.vix_pct_calm else (1 if vix_pct < params.vix_pct_stress else 2)
            score += 0 if rv20_pct < params.rv20_pct_calm else (1 if rv20_pct < params.rv20_pct_stress else 2)
            score += 0 if drawdown < params.drawdown_calm else (1 if drawdown < params.drawdown_stress else 2)

            regime_label = "Calm" if score <= 2 else ("Transition" if score <= 4 else "Stress")

            conn.execute(
                """
                INSERT INTO regime_state (
                    regime_date, vix_percentile, rv20_percentile, drawdown_percent,
                    regime_score, regime_label, regime_config_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(regime_date) DO UPDATE SET
                    vix_percentile=excluded.vix_percentile,
                    rv20_percentile=excluded.rv20_percentile,
                    drawdown_percent=excluded.drawdown_percent,
                    regime_score=excluded.regime_score,
                    regime_label=excluded.regime_label,
                    regime_config_hash=excluded.regime_config_hash
                """,
                (
                    idx.date(),
                    vix_pct,
                    rv20_pct,
                    drawdown,
                    score,
                    regime_label,
                    thresholds_hash,
                ),
            )
            inserts += 1

        logger.info("regime rows updated=%s", inserts)
        return inserts
    finally:
        conn.close()
