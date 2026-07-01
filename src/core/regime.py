from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

import pandas as pd
import yaml

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
    weight_vix: float = 0.25
    weight_rv20: float = 0.25
    weight_drawdown: float = 0.25
    weight_event: float = 0.15
    weight_stress_proxy: float = 0.10
    score_calm_max: float = 0.67
    score_stress_min: float = 1.33
    event_path: str = "config/regime_events_v1.yaml"
    stress_proxy_ticker: str = "^VIX"


def regime_params_from_config(config: dict | None = None) -> RegimeParams:
    cfg = config or load_config()
    regime_cfg = cfg.get("regime", {})
    weights = regime_cfg.get("weights", {})
    return RegimeParams(
        vix_pct_calm=float(regime_cfg.get("vix_pct_calm", 40.0)),
        vix_pct_stress=float(regime_cfg.get("vix_pct_stress", 80.0)),
        rv20_pct_calm=float(regime_cfg.get("rv20_pct_calm", 40.0)),
        rv20_pct_stress=float(regime_cfg.get("rv20_pct_stress", 80.0)),
        drawdown_calm=float(regime_cfg.get("drawdown_calm", 5.0)),
        drawdown_stress=float(regime_cfg.get("drawdown_stress", 10.0)),
        weight_vix=float(weights.get("vix", 0.25)),
        weight_rv20=float(weights.get("rv20", 0.25)),
        weight_drawdown=float(weights.get("drawdown", 0.25)),
        weight_event=float(weights.get("event", 0.15)),
        weight_stress_proxy=float(weights.get("stress_proxy", 0.10)),
        score_calm_max=float(regime_cfg.get("score_calm_max", 0.67)),
        score_stress_min=float(regime_cfg.get("score_stress_min", 1.33)),
        event_path=str(regime_cfg.get("event_path", "config/regime_events_v1.yaml")),
        stress_proxy_ticker=str(regime_cfg.get("stress_proxy_ticker", "^VIX")),
    )


def _normalize_event_path(path_value: str) -> str:
    path = Path(path_value).expanduser()
    try:
        resolved = path.resolve(strict=False)
        repo_root = Path(__file__).resolve().parents[2]
        try:
            return str(resolved.relative_to(repo_root))
        except ValueError:
            return str(resolved)
    except Exception:
        return str(path)


def _event_file_digest(path_value: str) -> str | None:
    path = Path(path_value)
    if not path.exists() or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def regime_threshold_hash(params: RegimeParams) -> str:
    normalized_event_path = _normalize_event_path(params.event_path)
    payload = {
        "vix_pct_calm": params.vix_pct_calm,
        "vix_pct_stress": params.vix_pct_stress,
        "rv20_pct_calm": params.rv20_pct_calm,
        "rv20_pct_stress": params.rv20_pct_stress,
        "drawdown_calm": params.drawdown_calm,
        "drawdown_stress": params.drawdown_stress,
        "weight_vix": params.weight_vix,
        "weight_rv20": params.weight_rv20,
        "weight_drawdown": params.weight_drawdown,
        "weight_event": params.weight_event,
        "weight_stress_proxy": params.weight_stress_proxy,
        "score_calm_max": params.score_calm_max,
        "score_stress_min": params.score_stress_min,
        "event_path": normalized_event_path,
        "event_file_digest": _event_file_digest(params.event_path),
        "stress_proxy_ticker": params.stress_proxy_ticker,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _level_from_thresholds(value: float, calm: float, stress: float) -> int:
    if value < calm:
        return 0
    if value < stress:
        return 1
    return 2


def _load_event_scores(event_path: str) -> dict[date, float]:
    path = Path(event_path)
    if not path.exists():
        return {}
    payload = yaml.safe_load(path.read_text()) or {}
    events = payload.get("events", []) if isinstance(payload, dict) else []
    severity_to_score = {"low": 0.5, "medium": 1.0, "high": 2.0}
    scores: dict[date, float] = {}
    for event in events:
        if not isinstance(event, dict):
            continue
        raw_date = event.get("date")
        if not raw_date:
            continue
        try:
            event_date = pd.to_datetime(raw_date).date()
        except Exception:
            continue
        severity = str(event.get("severity", "low")).lower()
        score = severity_to_score.get(severity, 0.5)
        scores[event_date] = max(scores.get(event_date, 0.0), float(score))
    return scores


def _fetch_ticker_close_series(
    ticker: str,
    dates: Iterable[date],
) -> dict[date, float]:
    if not ticker:
        return {}
    date_list = sorted(set(dates))
    if not date_list:
        return {}
    start = pd.Timestamp(date_list[0]) - pd.Timedelta(days=5)
    end = pd.Timestamp(date_list[-1]) + pd.Timedelta(days=5)
    try:
        import yfinance as yf  # local import to keep runtime optional

        data = yf.download(
            ticker,
            start=start.strftime("%Y-%m-%d"),
            end=end.strftime("%Y-%m-%d"),
            progress=False,
            auto_adjust=False,
        )
    except Exception:
        return {}
    if data is None or data.empty or "Close" not in data.columns:
        return {}
    close = data["Close"].dropna()
    if isinstance(close, pd.DataFrame):
        if close.empty:
            return {}
        close = close.iloc[:, 0]
    if close.empty:
        return {}
    return {
        pd.Timestamp(ts).date(): float(value)
        for ts, value in close.items()
    }


def _percentiles_from_daily_values(values: dict[date, float]) -> dict[date, float]:
    if not values:
        return {}
    series = pd.Series(values).sort_index()
    history: list[float] = []
    out: dict[date, float] = {}
    for idx, raw_value in series.items():
        value = float(raw_value)
        history.append(value)
        percentile = 100.0 * (sum(1 for sample in history if sample <= value) / len(history))
        out[idx] = float(percentile)
    return out


def _trailing_percentile_series(series: pd.Series) -> pd.Series:
    if series.empty:
        return pd.Series(dtype=float)
    history: list[float] = []
    out: list[float] = []
    for raw_value in series.tolist():
        if pd.isna(raw_value):
            out.append(float("nan"))
            continue
        value = float(raw_value)
        history.append(value)
        percentile = 100.0 * (sum(1 for sample in history if sample <= value) / len(history))
        out.append(float(percentile))
    return pd.Series(out, index=series.index, dtype=float)


def _stress_proxy_score(stress_proxy_pct: float | None) -> float:
    if stress_proxy_pct is None:
        return 0.0
    if stress_proxy_pct < 40.0:
        return 0.0
    if stress_proxy_pct < 80.0:
        return 1.0
    return 2.0


def _first_ready_date_from_snapshots(snapshots: pd.DataFrame, params: RegimeParams) -> date | None:
    if snapshots.empty:
        return None
    work = snapshots.copy()
    work["date"] = pd.to_datetime(work["ts"]).dt.date
    daily = work.sort_values("ts").groupby("date").tail(1)
    daily = daily.set_index(pd.to_datetime(daily["date"]))
    daily["ret"] = daily["spot"].pct_change()
    daily["rv20"] = daily["ret"].rolling(params.rv_window).std() * (252 ** 0.5)
    rolling_high = daily["spot"].rolling(params.dd_window).max()
    daily["drawdown"] = (daily["spot"] / rolling_high - 1.0) * -100.0
    ready = daily[daily["rv20"].notna() & daily["drawdown"].notna()]
    if ready.empty:
        return None
    return pd.to_datetime(ready.index[0]).date()


def first_regime_ready_date(run_id: int, params: RegimeParams | None = None) -> date | None:
    params = params or regime_params_from_config()
    conn = connect()
    try:
        label_row = conn.execute(
            """
            SELECT MIN(regime_date)
            FROM regime_snapshot_labels
            WHERE run_id = ?
            """,
            (run_id,),
        ).fetchone()
        if label_row and label_row[0] is not None:
            return pd.to_datetime(label_row[0]).date()

        snapshots = conn.execute(
            """
            SELECT snapshot_id, run_id, ts, spot
            FROM snapshots
            WHERE run_id = ?
            ORDER BY ts, snapshot_id
            """,
            (run_id,),
        ).fetchdf()
    finally:
        conn.close()
    return _first_ready_date_from_snapshots(snapshots, params)


def compute_regime_state(params: RegimeParams | None = None, run_id: int | None = None) -> int:
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

        if run_id is None:
            snapshots = conn.execute(
                """
                SELECT snapshot_id, run_id, ts, spot
                FROM snapshots
                ORDER BY ts, snapshot_id
                """
            ).fetchdf()
        else:
            snapshots = conn.execute(
                """
                SELECT snapshot_id, run_id, ts, spot
                FROM snapshots
                WHERE run_id = ?
                ORDER BY ts, snapshot_id
                """,
                (run_id,),
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

        rv_pct = _trailing_percentile_series(daily["rv20"])
        dd_pct = _trailing_percentile_series(daily["drawdown"])

        daily["rv_pct"] = rv_pct
        daily["dd_pct"] = dd_pct
        event_scores_by_date = _load_event_scores(params.event_path)

        date_index = [idx.date() for idx in daily.index]
        vix_values = _fetch_ticker_close_series("^VIX", date_index)
        vix_pct_by_date = _percentiles_from_daily_values(vix_values)
        stress_values = _fetch_ticker_close_series(params.stress_proxy_ticker, date_index)
        stress_pct_by_date = _percentiles_from_daily_values(stress_values)

        if daily["rv20"].isna().all() or daily["drawdown"].isna().all():
            logger.warning(
                "Regime warm-up incomplete: insufficient lookback history for rolling features "
                "(rv_window=%s, dd_window=%s).",
                params.rv_window,
                params.dd_window,
            )

        inserts = 0
        regime_by_date: dict[date, tuple[str, str, str]] = {}
        for idx, row in daily.iterrows():
            if pd.isna(row["rv20"]) or pd.isna(row["drawdown"]):
                continue

            vix_pct = float(vix_pct_by_date.get(idx.date(), float(row["dd_pct"])))
            rv20_pct = float(row["rv_pct"])
            drawdown = float(row["drawdown"])
            vix_spot = vix_values.get(idx.date())

            event_score = float(event_scores_by_date.get(idx.date(), 0.0))
            stress_proxy_pct = stress_pct_by_date.get(idx.date())
            if stress_proxy_pct is None and params.stress_proxy_ticker:
                stress_proxy_pct = float(row["dd_pct"])
            stress_proxy_score = _stress_proxy_score(stress_proxy_pct)

            component_levels = {
                "vix": _level_from_thresholds(vix_pct, params.vix_pct_calm, params.vix_pct_stress),
                "rv20": _level_from_thresholds(rv20_pct, params.rv20_pct_calm, params.rv20_pct_stress),
                "drawdown": _level_from_thresholds(
                    drawdown,
                    params.drawdown_calm,
                    params.drawdown_stress,
                ),
                "event": _level_from_thresholds(event_score, 0.5, 1.0),
                "stress_proxy": _level_from_thresholds(stress_proxy_score, 0.5, 1.0),
            }
            weights = {
                "vix": params.weight_vix,
                "rv20": params.weight_rv20,
                "drawdown": params.weight_drawdown,
                "event": params.weight_event,
                "stress_proxy": params.weight_stress_proxy,
            }
            weight_sum = sum(weights.values()) or 1.0
            contributions = {
                name: component_levels[name] * weights[name]
                for name in component_levels
            }
            normalized_score = sum(contributions.values()) / weight_sum

            if normalized_score <= params.score_calm_max:
                regime_label = "Calm"
            elif normalized_score >= params.score_stress_min:
                regime_label = "Stress"
            else:
                regime_label = "Transition"

            decomposition = {
                "features": {
                    "vix_percentile": vix_pct,
                    "rv20_percentile": rv20_pct,
                    "drawdown_percent": drawdown,
                    "event_score": event_score,
                    "stress_proxy_score": stress_proxy_score,
                    "stress_proxy_percentile": stress_proxy_pct,
                    "vix_spot": vix_spot,
                    "stress_proxy_ticker": params.stress_proxy_ticker,
                },
                "levels": component_levels,
                "weights": weights,
                "contributions": contributions,
                "normalized_score": normalized_score,
                "thresholds": {
                    "score_calm_max": params.score_calm_max,
                    "score_stress_min": params.score_stress_min,
                },
                "label": regime_label,
            }

            conn.execute(
                """
                INSERT INTO regime_state (
                    regime_date, vix_percentile, rv20_percentile, drawdown_percent,
                    regime_score, regime_label, regime_config_hash,
                    vix_spot, rv20_value, drawdown_value,
                    event_score, stress_proxy_score, decomposition
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(regime_date) DO UPDATE SET
                    vix_percentile=excluded.vix_percentile,
                    rv20_percentile=excluded.rv20_percentile,
                    drawdown_percent=excluded.drawdown_percent,
                    regime_score=excluded.regime_score,
                    regime_label=excluded.regime_label,
                    regime_config_hash=excluded.regime_config_hash,
                    vix_spot=excluded.vix_spot,
                    rv20_value=excluded.rv20_value,
                    drawdown_value=excluded.drawdown_value,
                    event_score=excluded.event_score,
                    stress_proxy_score=excluded.stress_proxy_score,
                    decomposition=excluded.decomposition
                """,
                (
                    idx.date(),
                    vix_pct,
                    rv20_pct,
                    drawdown,
                    int(round(normalized_score * 100)),
                    regime_label,
                    thresholds_hash,
                    vix_spot,
                    float(row["rv20"]),
                    drawdown,
                    event_score,
                    stress_proxy_score,
                    json.dumps(decomposition, sort_keys=True, separators=(",", ":")),
                ),
            )
            regime_by_date[idx.date()] = (
                regime_label,
                thresholds_hash,
                json.dumps(decomposition, sort_keys=True, separators=(",", ":")),
            )
            inserts += 1

        snapshot_label_inserts = 0
        for snapshot_row in snapshots.itertuples(index=False):
            snapshot_ts = pd.to_datetime(snapshot_row.ts)
            regime_date = snapshot_ts.date()
            mapping = regime_by_date.get(regime_date)
            if mapping is None:
                continue
            mapped_label, mapped_hash, mapped_decomposition = mapping
            conn.execute(
                """
                INSERT INTO regime_snapshot_labels (
                    snapshot_id,
                    run_id,
                    regime_date,
                    regime_label,
                    regime_config_hash,
                    decomposition
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(snapshot_id) DO UPDATE SET
                    run_id=excluded.run_id,
                    regime_date=excluded.regime_date,
                    regime_label=excluded.regime_label,
                    regime_config_hash=excluded.regime_config_hash,
                    decomposition=excluded.decomposition
                """,
                (
                    int(snapshot_row.snapshot_id),
                    int(snapshot_row.run_id) if pd.notna(snapshot_row.run_id) else None,
                    regime_date,
                    mapped_label,
                    mapped_hash,
                    mapped_decomposition,
                ),
            )
            snapshot_label_inserts += 1

        if inserts == 0:
            logger.warning(
                "Regime warm-up incomplete: no regime rows emitted yet; add more snapshot history "
                "to satisfy rolling lookback windows (rv_window=%s, dd_window=%s).",
                params.rv_window,
                params.dd_window,
            )

        logger.info("regime rows updated=%s snapshot_labels_updated=%s", inserts, snapshot_label_inserts)
        return inserts
    finally:
        conn.close()
