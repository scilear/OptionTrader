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
               regime_label, confidence_tier, zscore_mid, zscore_worst
        FROM alerts
        ORDER BY severity DESC
        """
    )
    if alerts.empty:
        st.info("No alerts available yet.")
        return
    st.dataframe(alerts, use_container_width=True)


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

    ideas = query_df(
        """
        SELECT template, price_mid, price_worst, greeks, risk_flags
        FROM trade_ideas
        WHERE alert_id = ?
        """,
        (alert_id,),
    )
    if ideas.empty:
        st.info("No trade ideas available yet.")
        return
    st.dataframe(ideas, use_container_width=True)


def main():
    st.set_page_config(page_title="OptionTrader", layout="wide")
    page = st.sidebar.radio("Navigation", ["Alerts", "Metrics", "Alert Detail"])
    if page == "Alerts":
        alerts_page()
    elif page == "Metrics":
        metrics_page()
    else:
        alert_detail_page()


if __name__ == "__main__":
    main()
