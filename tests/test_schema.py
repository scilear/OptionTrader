import duckdb
from pathlib import Path


def test_schema_executes():
    conn = duckdb.connect(":memory:")
    try:
        sql = Path("src/db/schema.sql").read_text()
        conn.execute(sql)
        tables = conn.execute("SHOW TABLES").fetchall()
        assert ("option_quotes",) in tables
        cols = conn.execute("DESCRIBE option_quotes").fetchall()
        col_names = {c[0] for c in cols}
        assert "option_right" in col_names
        assert "right" not in col_names
    finally:
        conn.close()
