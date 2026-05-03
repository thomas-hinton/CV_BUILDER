from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "SQL" / "create_db.sql"
DB_PATH = PROJECT_ROOT / "data" / "db.db"


def init_database(reset: bool = False) -> Path:
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    if reset and DB_PATH.exists():
        DB_PATH.unlink()

    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")
        connection.executescript(schema)
        connection.commit()

    return DB_PATH


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create the local SQLite database from SQL/create_db.sql."
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete the existing database before recreating it.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db_path = init_database(reset=args.reset)
    print(f"Database ready: {db_path}")


if __name__ == "__main__":
    main()
