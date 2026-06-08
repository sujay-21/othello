"""
Database layer using Python built-in sqlite3 (no external ORM required).
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'othello.db')


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                mode         TEXT    NOT NULL,
                winner       TEXT,
                black_score  INTEGER DEFAULT 0,
                white_score  INTEGER DEFAULT 0,
                moves_played INTEGER DEFAULT 0,
                started_at   TEXT,
                ended_at     TEXT
            )
        """)
        conn.commit()
