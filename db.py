"""Camada de banco: SQLite local ou Postgres (Neon) via DATABASE_URL."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("DATA_DIR", BASE_DIR / "data"))
DB_PATH = DATA_DIR / "qrcodes.db"
DATABASE_URL = (os.environ.get("DATABASE_URL") or "").strip()


def using_postgres() -> bool:
    return bool(DATABASE_URL)


def persistent_data() -> bool:
    if using_postgres():
        return True
    return str(DATA_DIR).startswith("/var/data") or os.environ.get("PERSISTENT_DATA") == "1"


def _normalize_pg_url(url: str) -> str:
    # Render/Heroku às vezes usam postgres://
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    return url


class _Row(dict):
    """Permite row['col'] e row[0] como sqlite3.Row."""

    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except (KeyError, IndexError):
            return default


class Database:
    def __init__(self):
        self.pg = using_postgres()
        if self.pg:
            import psycopg
            from psycopg.rows import dict_row

            self._conn = psycopg.connect(
                _normalize_pg_url(DATABASE_URL),
                row_factory=dict_row,
                autocommit=False,
            )
        else:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(DB_PATH)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON")

    def execute(self, sql: str, params=()):
        sql_run = sql
        if self.pg:
            sql_run = sql.replace("?", "%s")
        cur = self._conn.execute(sql_run, params)
        return _Cursor(cur, self.pg)

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()

    def table_columns(self, table: str) -> set[str]:
        if self.pg:
            rows = self.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = ?
                """,
                (table,),
            ).fetchall()
            return {r["column_name"] for r in rows}
        rows = self.execute(f"PRAGMA table_info({table})").fetchall()
        return {r[1] for r in rows}


class _Cursor:
    def __init__(self, cur, pg: bool):
        self._cur = cur
        self._pg = pg

    def fetchone(self):
        row = self._cur.fetchone()
        if row is None:
            return None
        if self._pg:
            return _Row(row)
        return row

    def fetchall(self):
        rows = self._cur.fetchall()
        if self._pg:
            return [_Row(r) for r in rows]
        return rows


def init_schema(db: Database):
    if db.pg:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS qrcodes (
                id SERIAL PRIMARY KEY,
                code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                company TEXT,
                target_url TEXT NOT NULL,
                notes TEXT,
                scans INTEGER NOT NULL DEFAULT 0,
                last_scan TEXT,
                active INTEGER NOT NULL DEFAULT 1,
                sold INTEGER NOT NULL DEFAULT 0,
                sale_price DOUBLE PRECISION,
                sold_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
    else:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS qrcodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                company TEXT,
                target_url TEXT NOT NULL,
                notes TEXT,
                scans INTEGER NOT NULL DEFAULT 0,
                last_scan TEXT,
                active INTEGER NOT NULL DEFAULT 1,
                sold INTEGER NOT NULL DEFAULT 0,
                sale_price REAL,
                sold_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

    cols = db.table_columns("qrcodes")
    migrations = {
        "last_scan": "ALTER TABLE qrcodes ADD COLUMN last_scan TEXT",
        "sold": "ALTER TABLE qrcodes ADD COLUMN sold INTEGER NOT NULL DEFAULT 0",
        "sale_price": (
            "ALTER TABLE qrcodes ADD COLUMN sale_price DOUBLE PRECISION"
            if db.pg
            else "ALTER TABLE qrcodes ADD COLUMN sale_price REAL"
        ),
        "sold_at": "ALTER TABLE qrcodes ADD COLUMN sold_at TEXT",
    }
    for col, sql in migrations.items():
        if col not in cols:
            db.execute(sql)
    db.commit()


def integrity_error_types():
    types = [sqlite3.IntegrityError]
    try:
        import psycopg

        types.append(psycopg.IntegrityError)
    except ImportError:
        pass
    return tuple(types)
