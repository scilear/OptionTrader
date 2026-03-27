from __future__ import annotations

import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

import pandas as pd
import streamlit as st
import altair as alt

import json

from src.db.connection import connect
from src.core.config import load_config


def query_df(sql: str, params: tuple | None = None) -> pd.DataFrame:
    conn = connect()
    try:
        if params:
            return conn.execute(sql, params).fetchdf()
        return conn.execute(sql).fetchdf()
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()


def _to_float(value) -> float | None:
    try:
        if value is None or pd.isna(value):
            return None
        return float(value)
    except Exception:
        return None


def _gate_badge(status: str) -> str:
    if status == "pass":
        return "PASS"
    if status == "neutral":
        return "NEUTRAL"
    return "FAIL"


def _decision_summary(alert_row: dict) -> tuple[str, list[dict]]:
    config = load_config()
    z_threshold = float(config["alerts"]["z_threshold"])
    persistence_required = int(config["alerts"]["persistence_snapshots"])
    buckets = config["metrics"]["expiry_buckets_days"]
    expected_bucket_count = len(buckets)

    alert_id = int(alert_row["alert_id"])
    snapshot_id = int(alert_row["snapshot_id"])
    alert_type = alert_row["alert_type"]
    bucket = alert_row["expiry_bucket"]

    z_mid = _to_float(alert_row.get("zscore_mid"))
    z_worst = _to_float(alert_row.get("zscore_worst"))
    persistence = int(alert_row.get("persistence_count") or 0)
    tradability = _to_float(alert_row.get("tradability_score"))
    regime_label = str(alert_row.get("regime_label") or "Unknown")

    signal_pass = (
        z_mid is not None
        and z_worst is not None
        and abs(z_mid) >= z_threshold
        and abs(z_worst) >= z_threshold
        and persistence >= persistence_required
    )
    signal_reason = (
        f"|z_mid|={abs(z_mid):.2f} |z_worst|={abs(z_worst):.2f} "
        f"threshold={z_threshold:.2f} persistence={persistence}/{persistence_required}"
        if z_mid is not None and z_worst is not None
        else "missing z-score values"
    )

    metrics_count_df = query_df(
        "SELECT COUNT(*) AS n FROM surface_metrics WHERE snapshot_id = ?",
        (snapshot_id,),
    )
    bucket_present_df = query_df(
        "SELECT COUNT(*) AS n FROM surface_metrics WHERE snapshot_id = ? AND expiry_bucket = ?",
        (snapshot_id, bucket),
    )
    iv_points_df = query_df(
        "SELECT COUNT(*) AS n FROM iv_points WHERE snapshot_id = ?",
        (snapshot_id,),
    )
    metrics_count = (
        int(metrics_count_df.iloc[0]["n"]) if not metrics_count_df.empty else 0
    )
    bucket_present = (
        int(bucket_present_df.iloc[0]["n"]) if not bucket_present_df.empty else 0
    )
    iv_points = int(iv_points_df.iloc[0]["n"]) if not iv_points_df.empty else 0

    metric_field_map = {
        "RR_EXTREME": "rr25_mid",
        "FLY_EXTREME": "fly25_mid",
        "TERM_KINK": "term_slope_mid",
    }
    metric_field = metric_field_map.get(alert_type, "rr25_mid")
    recent_df = query_df(
        f"""
        SELECT s.ts, m.{metric_field} AS metric_value
        FROM surface_metrics m
        JOIN snapshots s ON s.snapshot_id = m.snapshot_id
        WHERE m.expiry_bucket = ?
        ORDER BY s.ts DESC
        LIMIT 12
        """,
        (bucket,),
    )
    cadence_note = ""
    cadence_ok = True
    if recent_df.empty or len(recent_df) < 3:
        cadence_ok = False
        cadence_note = "insufficient recent points"
    else:
        recent_df["ts"] = pd.to_datetime(recent_df["ts"], errors="coerce")
        recent_df = recent_df.dropna(subset=["ts"]).sort_values("ts")
        if len(recent_df) < 3:
            cadence_ok = False
            cadence_note = "insufficient timestamp points"
        else:
            gaps = recent_df["ts"].diff().dt.total_seconds().div(3600).dropna()
            max_gap = float(gaps.max()) if not gaps.empty else 0.0
            cadence_note = f"recent_points={len(recent_df)} max_gap_h={max_gap:.1f}"
            cadence_ok = max_gap <= 72.0

    data_pass = (
        metrics_count >= expected_bucket_count
        and bucket_present > 0
        and iv_points > 0
        and cadence_ok
    )
    data_reason = (
        f"metrics_rows={metrics_count}/{expected_bucket_count} bucket_present={bucket_present} "
        f"iv_points={iv_points} {cadence_note}"
    )

    if alert_type == "RR_EXTREME" and regime_label == "Stress":
        regime_status = "fail"
        regime_reason = "RR_EXTREME conflicts with Stress regime policy"
    elif regime_label == "Transition":
        regime_status = "neutral"
        regime_reason = "Transition regime: thesis needs stronger confirmation"
    else:
        regime_status = "pass"
        regime_reason = f"regime_label={regime_label}"

    execution_pass = tradability is not None and tradability > 0.0
    execution_reason = (
        f"tradability_score={tradability:.2f} (pass if > 0.00)"
        if tradability is not None
        else "missing tradability score"
    )

    ideas_df = query_df(
        "SELECT COUNT(*) AS n, MAX(price_worst) AS max_price_worst FROM trade_ideas WHERE alert_id = ?",
        (alert_id,),
    )
    idea_count = int(ideas_df.iloc[0]["n"]) if not ideas_df.empty else 0
    max_price_worst = (
        _to_float(ideas_df.iloc[0]["max_price_worst"]) if not ideas_df.empty else None
    )
    if idea_count <= 0:
        risk_status = "fail"
        risk_reason = "no trade idea generated"
    elif max_price_worst is None:
        risk_status = "neutral"
        risk_reason = "idea exists but worst-case pricing unavailable"
    else:
        risk_status = "pass"
        risk_reason = f"idea_count={idea_count} price_worst_available"

    gates = [
        {
            "Gate": "Signal",
            "Status": "pass" if signal_pass else "fail",
            "Evidence": signal_reason,
        },
        {
            "Gate": "Data",
            "Status": "pass" if data_pass else "fail",
            "Evidence": data_reason,
        },
        {"Gate": "Regime", "Status": regime_status, "Evidence": regime_reason},
        {
            "Gate": "Execution",
            "Status": "pass" if execution_pass else "fail",
            "Evidence": execution_reason,
        },
        {"Gate": "Risk", "Status": risk_status, "Evidence": risk_reason},
    ]

    statuses = {g["Gate"]: g["Status"] for g in gates}
    if statuses["Risk"] == "fail" or statuses["Signal"] == "fail":
        decision = "Reject"
    elif statuses["Data"] == "fail" or statuses["Execution"] == "fail":
        decision = "Research only"
    elif statuses["Regime"] == "fail":
        decision = "Reject"
    elif statuses["Risk"] == "neutral" or statuses["Regime"] == "neutral":
        decision = "Watch for confirmation"
    else:
        decision = "Trade now"

    return decision, gates


def alerts_page():
    st.header("Alerts Dashboard")
    alerts = query_df(
        """
        SELECT alert_id, alert_type, expiry_bucket, severity, tradability_score,
               regime_label, confidence_tier, zscore_mid, zscore_worst,
               persistence_count
        FROM alerts
        ORDER BY severity DESC
        """
    )
    if alerts.empty:
        st.info("No alerts available yet.")
        return
    st.sidebar.subheader("Alert Filters")
    types = ["All"] + sorted(alerts["alert_type"].unique().tolist())
    tiers = ["All"] + sorted(alerts["confidence_tier"].unique().tolist())
    regimes = ["All"] + sorted(alerts["regime_label"].unique().tolist())

    sel_type = st.sidebar.selectbox("Type", types)
    sel_tier = st.sidebar.selectbox("Tier", tiers)
    sel_regime = st.sidebar.selectbox("Regime", regimes)
    min_severity = st.sidebar.slider("Min severity", 0.0, 5.0, 2.0, 0.1)
    min_tradability = st.sidebar.slider("Min tradability", 0.0, 1.0, 0.0, 0.05)

    filtered = alerts
    if sel_type != "All":
        filtered = filtered[filtered["alert_type"] == sel_type]
    if sel_tier != "All":
        filtered = filtered[filtered["confidence_tier"] == sel_tier]
    if sel_regime != "All":
        filtered = filtered[filtered["regime_label"] == sel_regime]
    filtered = filtered[
        (filtered["severity"] >= min_severity)
        & (filtered["tradability_score"] >= min_tradability)
    ]

    st.dataframe(filtered, use_container_width=True)
    from src.core.export import export_df_to_csv

    st.download_button(
        "Download alerts CSV",
        data=export_df_to_csv(filtered),
        file_name="alerts.csv",
        mime="text/csv",
    )


def metrics_page():
    st.header("Metric Explorer")
    metric = st.selectbox(
        "Metric", ["rr25_mid", "fly25_mid", "term_slope_mid", "event_premium"]
    )
    bucket = st.selectbox("Expiry bucket", ["21D", "30D", "45D"])
    if metric == "event_premium":
        data = query_df(
            """
            SELECT s.ts, m.atm_iv_mid
            FROM surface_metrics m
            JOIN snapshots s ON s.snapshot_id = m.snapshot_id
            WHERE m.expiry_bucket = ?
            ORDER BY s.ts
            """,
            (bucket,),
        )
        if data.empty:
            st.info("No metric data available yet.")
            return
        from src.core.metrics import event_premium_series

        data["event_premium"] = event_premium_series(data)
        st.line_chart(data.set_index("ts")[["event_premium"]])
        from src.core.export import export_df_to_csv

        st.download_button(
            "Download metric CSV",
            data=export_df_to_csv(data[["ts", "event_premium"]]),
            file_name=f"metric_event_premium_{bucket}.csv",
            mime="text/csv",
        )
        return

    data = query_df(
        """
        SELECT s.snapshot_id, s.ts, s.source, m.{metric}
        FROM surface_metrics m
        JOIN snapshots s ON s.snapshot_id = m.snapshot_id
        WHERE m.expiry_bucket = ?
        ORDER BY s.ts
        """.format(metric=metric),
        (bucket,),
    )
    if data.empty:
        st.info("No metric data available yet.")
        return

    data["ts"] = pd.to_datetime(data["ts"], errors="coerce")
    data = data.dropna(subset=["ts", metric]).sort_values("ts").reset_index(drop=True)
    if data.empty:
        st.info("No metric data available yet.")
        return

    data["gap_hours"] = data["ts"].diff().dt.total_seconds().div(3600).fillna(0.0)
    gap_break_hours = st.slider(
        "Break line if time gap exceeds (hours)",
        min_value=1,
        max_value=168,
        value=12,
        step=1,
    )
    data["segment"] = (data["gap_hours"] > gap_break_hours).cumsum().astype(str)
    data["snapshot_seq"] = range(1, len(data) + 1)

    median_gap = float(data["gap_hours"].iloc[1:].median()) if len(data) > 1 else 0.0
    max_gap = float(data["gap_hours"].max()) if len(data) > 0 else 0.0
    st.caption(
        f"Points={len(data)} | median gap={median_gap:.2f}h | max gap={max_gap:.2f}h"
    )

    x_mode = st.radio(
        "X-axis",
        ["Timeline", "Snapshot sequence"],
        horizontal=True,
    )

    if x_mode == "Timeline":
        x_encoding = alt.X("ts:T", title="Timestamp")
    else:
        x_encoding = alt.X("snapshot_seq:Q", title="Snapshot sequence")

    chart = (
        alt.Chart(data)
        .mark_line(point=True)
        .encode(
            x=x_encoding,
            y=alt.Y(f"{metric}:Q", title=metric),
            color=alt.Color("source:N", title="Source"),
            detail="segment:N",
            tooltip=[
                alt.Tooltip("snapshot_id:Q", title="snapshot_id"),
                alt.Tooltip("ts:T", title="ts"),
                alt.Tooltip("source:N", title="source"),
                alt.Tooltip(f"{metric}:Q", title=metric, format=".6f"),
                alt.Tooltip("gap_hours:Q", title="gap_hours", format=".2f"),
            ],
        )
        .properties(height=360)
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)
    from src.core.export import export_df_to_csv

    st.download_button(
        "Download metric CSV",
        data=export_df_to_csv(data),
        file_name=f"metric_{metric}_{bucket}.csv",
        mime="text/csv",
    )


def alert_detail_page():
    st.header("Alert Detail")
    alerts = query_df("SELECT alert_id, alert_type, expiry_bucket FROM alerts")
    if alerts.empty:
        st.info("No alerts available yet.")
        return
    alert_id = st.selectbox("Alert", alerts["alert_id"].tolist())
    detail = query_df(
        """
        SELECT alert_id, snapshot_id, alert_type, expiry_bucket, severity, zscore_mid, zscore_worst,
               tradability_score, confidence_tier, persistence_count, regime_label, explain
        FROM alerts
        WHERE alert_id = ?
        """,
        (alert_id,),
    )
    st.dataframe(detail, use_container_width=True)

    decision = "Watch for confirmation"
    if not detail.empty:
        decision, gates = _decision_summary(detail.iloc[0].to_dict())
        st.subheader("Decision Summary")
        st.metric("Proposed label", decision)
        gates_df = pd.DataFrame(gates)
        gates_df["Status"] = gates_df["Status"].apply(_gate_badge)
        st.dataframe(gates_df, use_container_width=True)

        explain_raw = detail.iloc[0]["explain"]
        try:
            explain = json.loads(explain_raw) if explain_raw else {}
        except Exception:
            explain = {}
        st.subheader("Explainability")
        st.json(explain)

    ideas = query_df(
        """
        SELECT template, price_mid, price_worst, greeks, risk_flags, legs
        FROM trade_ideas
        WHERE alert_id = ?
        """,
        (alert_id,),
    )
    if ideas.empty:
        st.info("No trade ideas available yet.")
        return

    def parse_json(value):
        try:
            return json.loads(value) if value else None
        except Exception:
            return None

    ideas = ideas.copy()
    ideas["risk_flags"] = ideas["risk_flags"].apply(parse_json)
    ideas["legs"] = ideas["legs"].apply(parse_json)

    display = ideas.drop(columns=["legs", "risk_flags"]).copy()
    display["risk_flags"] = ideas["risk_flags"].apply(
        lambda v: ", ".join(v) if isinstance(v, list) else (v or "")
    )
    st.dataframe(display, use_container_width=True)

    for i, row in ideas.iterrows():
        st.subheader(f"Legs — {row['template']}")
        legs = row["legs"]
        if isinstance(legs, list):
            right_map = {"P": "Put", "C": "Call"}
            rows = [
                {
                    "Action": leg.get("action", ""),
                    "Type": right_map.get(leg.get("right", ""), leg.get("right", "")),
                    "Strike": int(leg["strike"])
                    if leg.get("strike") is not None
                    else "—",
                    "Expiry": leg.get("expiry") or leg.get("tenor") or "—",
                    "Delta": leg.get("delta", ""),
                }
                for leg in legs
            ]
            st.dataframe(rows, use_container_width=True)

    from src.core.export import build_trade_export, export_to_json

    st.subheader("Decision Worksheet")
    thesis_options = ["Reversion", "Continuation", "No-trade"]
    thesis = st.selectbox("Thesis", thesis_options, key=f"thesis_{alert_id}")
    intended_options = [
        "Trade now",
        "Watch for confirmation",
        "Research only",
        "Reject",
    ]
    default_idx = (
        intended_options.index(decision) if decision in intended_options else 1
    )
    intended_label = st.selectbox(
        "Intended decision label",
        intended_options,
        index=default_idx,
        key=f"intended_label_{alert_id}",
    )
    rationale = st.text_area(
        "Rationale",
        placeholder="Explain why this decision label is justified by signal/data/regime/execution evidence.",
        key=f"rationale_{alert_id}",
    )
    invalidation = st.text_area(
        "Invalidation trigger",
        placeholder="State the specific condition that invalidates this thesis.",
        key=f"invalidation_{alert_id}",
    )
    max_loss = st.number_input(
        "Max loss (currency units)",
        min_value=0.0,
        value=0.0,
        step=1.0,
        key=f"max_loss_{alert_id}",
    )
    position_size = st.number_input(
        "Position size (contracts or normalized units)",
        min_value=0.0,
        value=0.0,
        step=1.0,
        key=f"position_size_{alert_id}",
    )

    base_fields_ok = (
        bool(rationale.strip()) and bool(invalidation.strip()) and bool(thesis)
    )
    risk_fields_required = intended_label in {"Trade now", "Watch for confirmation"}
    risk_fields_ok = max_loss > 0 and position_size > 0
    worksheet_gate_pass = base_fields_ok and (
        risk_fields_ok if risk_fields_required else True
    )

    st.metric("Worksheet gate", "PASS" if worksheet_gate_pass else "FAIL")
    if not worksheet_gate_pass:
        if risk_fields_required:
            st.warning(
                "Decision is blocked: complete rationale, invalidation, thesis, max loss, and position size."
            )
        else:
            st.warning(
                "Decision is blocked: complete thesis, rationale, and invalidation."
            )

    final_label = (
        intended_label if worksheet_gate_pass else "Blocked - complete worksheet"
    )
    st.metric("Final label", final_label)

    idea_idx = st.number_input(
        "Idea index", min_value=0, max_value=max(len(ideas) - 1, 0), value=0
    )
    if not detail.empty and not ideas.empty:
        alert_row = detail.iloc[0].to_dict()
        idea_row = ideas.iloc[int(idea_idx)].to_dict()
        decision_context = {
            "proposed_label": decision,
            "intended_label": intended_label,
            "final_label": final_label,
            "thesis": thesis,
            "rationale": rationale.strip(),
            "invalidation_trigger": invalidation.strip(),
            "max_loss": max_loss,
            "position_size": position_size,
            "worksheet_gate": "PASS" if worksheet_gate_pass else "FAIL",
        }
        if worksheet_gate_pass:
            payload = build_trade_export(alert_row, idea_row, decision_context)
            st.download_button(
                "Download trade idea",
                data=export_to_json(payload),
                file_name=f"trade_idea_{alert_id}.json",
                mime="application/json",
            )
        else:
            st.info("Complete the worksheet to enable trade idea download.")


def main():
    st.set_page_config(page_title="OptionTrader", layout="wide")
    page = st.sidebar.radio(
        "Navigation",
        ["Alerts", "Metrics", "Alert Detail", "Replay", "Event Study", "Health"],
    )
    if page == "Alerts":
        alerts_page()
    elif page == "Metrics":
        metrics_page()
    elif page == "Alert Detail":
        alert_detail_page()
    elif page == "Replay":
        st.header("Replay")
        data = query_df(
            """
            SELECT s.ts, s.snapshot_id, COUNT(a.alert_id) AS alert_count
            FROM snapshots s
            LEFT JOIN alerts a ON a.snapshot_id = s.snapshot_id
            GROUP BY s.ts, s.snapshot_id
            ORDER BY s.ts DESC
            LIMIT 50
            """
        )
        if data.empty:
            st.info("No replay data available yet.")
            return
        st.dataframe(data, use_container_width=True)
    elif page == "Event Study":
        st.header("Event Study")
        metric = st.selectbox("Metric", ["rr25_mid", "fly25_mid", "term_slope_mid"])
        threshold = st.slider(
            "Z threshold", min_value=1.5, max_value=3.0, value=2.0, step=0.1
        )
        series = query_df(
            """
            SELECT s.ts, m.{metric}
            FROM surface_metrics m
            JOIN snapshots s ON s.snapshot_id = m.snapshot_id
            ORDER BY s.ts
            """.format(metric=metric)
        )
        if series.empty:
            st.info("No data available for event study.")
            return
        from src.core.event_study import (
            compute_event_study,
            compute_event_study_by_regime,
        )

        stats = compute_event_study(series, metric, threshold)
        st.metric("Events", stats.events)
        st.metric("Hit rate", f"{stats.hit_rate:.2f}")
        st.metric(
            "Median reversion days",
            "N/A"
            if stats.median_reversion_days is None
            else f"{stats.median_reversion_days:.1f}",
        )

        regime = query_df("SELECT regime_date, regime_label FROM regime_state")
        by_regime = compute_event_study_by_regime(series, metric, threshold, regime)
        if not by_regime.empty:
            st.subheader("By Regime")
            st.dataframe(by_regime, use_container_width=True)
    else:
        st.header("Health")
        from src.core.health import compute_health_summary, latest_snapshot_summary

        summary = compute_health_summary()
        st.metric("Snapshots", summary.snapshots)
        st.metric("Quotes", summary.quotes)
        st.metric("IV points", summary.iv_points)
        st.metric("Metrics", summary.metrics)
        st.metric("Alerts", summary.alerts)

        latest = latest_snapshot_summary()
        st.subheader("Latest Snapshot")
        st.text(f"snapshot_id: {latest.snapshot_id}")
        st.text(f"ts: {latest.ts}")
        st.text(f"alert_count: {latest.alert_count}")


if __name__ == "__main__":
    main()
