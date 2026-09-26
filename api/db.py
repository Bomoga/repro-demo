"""SQLite storage for notes.

Handlers share one connection per process, as a Lambda container would. Tests swap in an
in-memory database with use().
"""
import os
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
CREATE TABLE IF NOT EXISTS shares (
    token TEXT PRIMARY KEY,
    note_id INTEGER NOT NULL REFERENCES notes(id),
    password_hash TEXT NOT NULL
);
"""

_connection = None


def connect(path):
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def get_db():
    global _connection
    if _connection is None:
        _connection = connect(os.environ.get("NOTEWISE_DB_PATH", "/tmp/notewise.db"))
    return _connection


def use(conn):
    """Point every handler at this connection (tests, the dev server)."""
    global _connection
    _connection = conn
