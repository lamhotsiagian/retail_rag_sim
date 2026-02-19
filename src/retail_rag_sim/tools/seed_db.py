from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL", "sqlite:///./data/retail.db")

def _sqlite_path_from_url(db_url: str) -> str:
    if not db_url.startswith("sqlite:///"):
        raise ValueError("Only sqlite is supported in this seed script.")
    return db_url.replace("sqlite:///", "")

def main():
    db_path = _sqlite_path_from_url(DB_URL)
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    sql_text = Path("data/seed.sql").read_text(encoding="utf-8")
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(sql_text)
        conn.commit()
        print(f"Seeded database at {db_path}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
