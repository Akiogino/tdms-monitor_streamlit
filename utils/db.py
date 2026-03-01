from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Mapping

import pandas as pd

DB_PATH = Path("data/mood_app.db")
ALLOWED_USER_TYPES = {"self", "friend"}

RESPONSE_COLUMNS = [
    "id",
    "created_at",
    "user_type",
    "context_text",
    "calm",
    "irritated",
    "lethargic",
    "lively",
    "relaxed",
    "edgy",
    "lazy",
    "energetic",
    "free_text",
    "score_v",
    "score_s",
    "score_p",
    "score_a",
]

CSV_EXPORT_COLUMNS = [
    "created_at",
    "user_type",
    "context_text",
    "calm",
    "irritated",
    "lethargic",
    "lively",
    "relaxed",
    "edgy",
    "lazy",
    "energetic",
    "score_v",
    "score_s",
    "score_p",
    "score_a",
    "free_text",
]


def _connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path = DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with _connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                user_type TEXT NOT NULL CHECK(user_type IN ('self', 'friend')),
                context_text TEXT,
                calm INTEGER NOT NULL,
                irritated INTEGER NOT NULL,
                lethargic INTEGER NOT NULL,
                lively INTEGER NOT NULL,
                relaxed INTEGER NOT NULL,
                edgy INTEGER NOT NULL,
                lazy INTEGER NOT NULL,
                energetic INTEGER NOT NULL,
                free_text TEXT,
                score_v INTEGER NOT NULL,
                score_s INTEGER NOT NULL,
                score_p INTEGER NOT NULL,
                score_a INTEGER NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_responses_user_created_at
            ON responses(user_type, created_at DESC, id DESC)
            """
        )
        conn.commit()


def insert_response(
    user_type: str,
    context_text: str,
    answers: Mapping[str, int],
    free_text: str,
    scores: Mapping[str, int],
    db_path: Path = DB_PATH,
) -> int:
    if user_type not in ALLOWED_USER_TYPES:
        raise ValueError("user_type must be 'self' or 'friend'.")

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with _connect(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO responses (
                created_at, user_type, context_text,
                calm, irritated, lethargic, lively,
                relaxed, edgy, lazy, energetic,
                free_text, score_v, score_s, score_p, score_a
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                created_at,
                user_type,
                context_text,
                answers["calm"],
                answers["irritated"],
                answers["lethargic"],
                answers["lively"],
                answers["relaxed"],
                answers["edgy"],
                answers["lazy"],
                answers["energetic"],
                free_text,
                scores["score_v"],
                scores["score_s"],
                scores["score_p"],
                scores["score_a"],
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)


def fetch_responses(
    user_type: str,
    limit: int = 20,
    db_path: Path = DB_PATH,
) -> pd.DataFrame:
    if user_type not in ALLOWED_USER_TYPES:
        raise ValueError("user_type must be 'self' or 'friend'.")

    safe_limit = max(int(limit), 1)
    query = f"""
        SELECT {', '.join(RESPONSE_COLUMNS)}
        FROM responses
        WHERE user_type = ?
        ORDER BY created_at DESC, id DESC
        LIMIT ?
    """

    with _connect(db_path) as conn:
        return pd.read_sql_query(query, conn, params=(user_type, safe_limit))


def fetch_recent_vs_points(
    user_type: str,
    limit: int = 6,
    db_path: Path = DB_PATH,
) -> list[tuple[int, int]]:
    if user_type not in ALLOWED_USER_TYPES:
        raise ValueError("user_type must be 'self' or 'friend'.")

    safe_limit = max(int(limit), 1)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT score_v, score_s
            FROM responses
            WHERE user_type = ?
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (user_type, safe_limit),
        ).fetchall()

    return [(int(row["score_v"]), int(row["score_s"])) for row in rows]
