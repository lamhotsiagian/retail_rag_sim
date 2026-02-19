from __future__ import annotations

import os
import sqlite3
from typing import Any, Dict, List
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL", "sqlite:///./data/retail.db")

def _sqlite_path_from_url(db_url: str) -> str:
    if not db_url.startswith("sqlite:///"):
        raise ValueError("This demo DB tool supports sqlite only.")
    return db_url.replace("sqlite:///", "")

def run_select(sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
    if not sql.strip().lower().startswith("select"):
        raise ValueError("Only SELECT queries are allowed (governance guardrail).")
    path = _sqlite_path_from_url(DB_URL)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

def dollars(cents: int) -> str:
    return f"${cents/100:.2f}"
