# db.py
# Simple SQLite helper for logging conversations
from os import path
import sqlite3
from datetime import datetime
from typing import Optional, List, Tuple


DB_PATH = "chat_logs.db"


def init_db(path: str = DB_PATH):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute(
    """
    CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    role TEXT,
    message TEXT,
    created_at TEXT
    )
    """
    )
    conn.commit()
    conn.close()


def log_message(session_id: str, role: str, message: str, path: str = DB_PATH):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute(
    "INSERT INTO messages (session_id, role, message, created_at) VALUES (?,?,?,?)",
    (session_id, role, message, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def get_session_history(session_id: str, path: str = DB_PATH) -> List[Tuple]:
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute(
    "SELECT role, message FROM messages WHERE session_id=? ORDER BY id ASC",
    (session_id,)
    )
    rows = c.fetchall()
    conn.close()
    return rows