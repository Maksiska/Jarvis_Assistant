# core/db.py
import os
import sqlite3
from threading import RLock
from datetime import datetime

DB_PATH = os.getenv("JARVIS_DB_PATH", "jarvis.sqlite3")

_lock = RLock()

def _connect():
    # autocommit через isolation_level=None, чтобы не ловить забытые commit'ы
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

def init_db():
    with _lock, _connect() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL UNIQUE,
            action_type TEXT NOT NULL,
            action_target TEXT,
            console_command TEXT,
            created_at TEXT NOT NULL
        );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_actions_query ON actions(query);")

def get_action_by_query(query: str) -> dict | None:
    if not query:
        return None
    with _lock, _connect() as conn:
        row = conn.execute(
            "SELECT query, action_type, action_target, console_command FROM actions WHERE query = ? LIMIT 1;",
            (query,)
        ).fetchone()
        if not row:
            return None
        return {
            "query": row[0],
            "action_type": row[1],
            "action_target": row[2] or "",
            "console_command": row[3] or ""
        }

def save_action(query: str, action_type: str, action_target: str, console_command: str) -> None:
    if not query or not action_type:
        return
    with _lock, _connect() as conn:
        conn.execute(
            """
            INSERT INTO actions (query, action_type, action_target, console_command, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(query) DO UPDATE SET
                action_type=excluded.action_type,
                action_target=excluded.action_target,
                console_command=excluded.console_command,
                created_at=excluded.created_at;
            """,
            (query, action_type, action_target or "", console_command or "", datetime.utcnow().isoformat())
        )
