from __future__ import annotations

import io

from src.core.config import load_config


def _is_pg(conn) -> bool:
    return isinstance(conn, _PGConnectionWrapper)


class _CursorWrapper:
    """Wraps a psycopg2 cursor to provide DuckDB-compatible .fetchdf()."""

    def __init__(self, cur):
        self._cur = cur

    def fetchall(self):
        return self._cur.fetchall()

    def fetchone(self):
        return self._cur.fetchone()

    def fetchdf(self):
        import pandas as pd
        cols = [desc[0] for desc in self._cur.description] if self._cur.description else []
        return pd.DataFrame(self._cur.fetchall(), columns=cols)

    def __iter__(self):
        return iter(self._cur)

    def __getattr__(self, name):
        return getattr(self._cur, name)


class _PGConnectionWrapper:
    """Wraps a psycopg2 connection to provide a .execute() interface
    compatible with DuckDB/sqlite3 connections."""

    def __init__(self, pg_conn):
        self._conn = pg_conn
        self._conn.autocommit = True

    def execute(self, sql, params=None):
        cur = self._conn.cursor()
        if params is not None:
            cur.execute(sql.replace("?", "%s"), params)
        else:
            cur.execute(sql)
        return _CursorWrapper(cur)

    def copy_quote_rows(self, rows):
        if not rows:
            return
        buf = io.StringIO()
        for r in rows:
            buf.write('\t'.join(str(v) for v in r) + '\n')
        buf.seek(0)
        cur = self._conn.cursor()
        cur.copy_from(
            buf, 'option_quotes',
            columns=('snapshot_id', 'expiry', 'strike', 'option_right',
                     'bid', 'ask', 'last', 'bid_size', 'ask_size',
                     'oi', 'volume', 'flags'),
        )

    def execute_values(self, sql, argslist, template=None, page_size=1000):
        if not argslist:
            return
        from psycopg2.extras import execute_values as _ev
        cur = self._conn.cursor()
        _ev(cur, sql.replace("?", "%s"), argslist, template=template, page_size=page_size)

    def cursor(self):
        return self._conn.cursor()

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()


def connect():
    config = load_config()
    engine = config["storage"].get("engine", "duckdb")
    if engine == "postgres":
        import psycopg2
        return _PGConnectionWrapper(psycopg2.connect(config["storage"]["dsn"]))
    import duckdb
    return duckdb.connect(config["storage"]["path"])
