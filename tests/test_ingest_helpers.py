import duckdb
import pandas as pd

from src.ingest.ingest_yfinance import _next_id, to_int


def test_next_id_increments():
    conn = duckdb.connect(":memory:")
    try:
        conn.execute("CREATE TABLE t (id INTEGER)")
        assert _next_id(conn, "t", "id") == 1
        conn.execute("INSERT INTO t (id) VALUES (1)")
        assert _next_id(conn, "t", "id") == 2
    finally:
        conn.close()


def test_nan_to_int_behavior():
    value = float("nan")
    assert pd.isna(value)
    assert to_int(value) == 0
