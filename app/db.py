from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Any

from .config import settings


DB_PATH = settings.data_dir / "logs.db"


def init_db() -> None:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS dialog_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                question TEXT,
                answer TEXT,
                top_question TEXT,
                top_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def log_dialog(
    user_id: int | None,
    username: str | None,
    question: str,
    answer: str,
    top_question: str | None,
    top_url: str | None,
) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO dialog_logs (
                user_id, username, question, answer, top_question, top_url
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, username, question, answer, top_question, top_url),
        )
        conn.commit()
