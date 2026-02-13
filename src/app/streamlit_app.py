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

import json

from src.db.connection import connect


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
    filtered = filtered[(filtered["severity"] >= min_severity) & (filtered["tradability_score"] >= min_tradability)]

    st.dataframe(filtered, use_container_width=True)


def metrics_page():
    st.header("Metric Explorer")
    metric = st.selectbox("Metric", ["rr25_mid", "fly25_mid", "term_slope_mid"])
    bucket = st.selectbox("Expiry bucket", ["21D", "30D", "45D"])
    data = query_df(
        """
        SELECT s.ts, m.{metric}
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
    st.line_chart(data.set_index("ts"))


def alert_detail_page():
    st.header("Alert Detail")
    alerts = query_df("SELECT alert_id, alert_type, expiry_bucket FROM alerts")
    if alerts.empty:
        st.info("No alerts available yet.")
        return
    alert_id = st.selectbox("Alert", alerts["alert_id"].tolist())
    detail = query_df(
        """
        SELECT alert_id, alert_type, expiry_bucket, severity, zscore_mid, zscore_worst,
               tradability_score, confidence_tier, persistence_count, regime_label, explain
        FROM alerts
        WHERE alert_id = ?
        """,
        (alert_id,),
    )
    st.dataframe(detail, use_container_width=True)

    if not detail.empty:
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
    st.dataframe(ideas, use_container_width=True)

    from src.core.export import build_trade_export, export_to_json

    idea_idx = st.number_input("Idea index", min_value=0, max_value=max(len(ideas) - 1, 0), value=0)
    if not detail.empty and not ideas.empty:
        alert_row = detail.iloc[0].to_dict()
        idea_row = ideas.iloc[int(idea_idx)].to_dict()
        payload = build_trade_export(alert_row, idea_row)
        st.download_button(
            "Download trade idea",
            data=export_to_json(payload),
            file_name=f"trade_idea_{alert_id}.json",
            mime="application/json",
        )


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
        threshold = st.slider("Z threshold", min_value=1.5, max_value=3.0, value=2.0, step=0.1)
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
        from src.core.event_study import compute_event_study

        stats = compute_event_study(series, metric, threshold)
        st.metric("Events", stats.events)
        st.metric("Hit rate", f"{stats.hit_rate:.2f}")
        st.metric(
            "Median reversion days",
            "N/A" if stats.median_reversion_days is None else f"{stats.median_reversion_days:.1f}",
        )
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
