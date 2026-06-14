import sqlite3
from datetime import datetime
from typing import List, Dict, Any

DB_PATH = "mood_journal.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT    NOT NULL,
            vent      TEXT    NOT NULL,
            emotion   TEXT    NOT NULL,
            response  TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def log_entry(vent: str, emotion: str, response: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO entries (timestamp, vent, emotion, response) VALUES (?, ?, ?, ?)",
        (datetime.now().isoformat(), vent, emotion, response),
    )
    conn.commit()
    conn.close()


def get_history(limit: int = 10) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT timestamp, vent, emotion, response FROM entries ORDER BY timestamp DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [
        {"timestamp": r[0], "vent": r[1], "emotion": r[2], "response": r[3]}
        for r in rows
    ]
