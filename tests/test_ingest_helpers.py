import duckdb

from src.ingest.ingest_yfinance import _next_id


def test_next_id_increments():
    conn = duckdb.connect(":memory:")
    try:
        conn.execute("CREATE TABLE t (id INTEGER)")
        assert _next_id(conn, "t", "id") == 1
        conn.execute("INSERT INTO t (id) VALUES (1)")
        assert _next_id(conn, "t", "id") == 2
    finally:
        conn.close()
