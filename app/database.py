"""SQLite persistence layer for the calculation history.

SQLite is used so that the project can run anywhere without a database
server.  The table schema is deliberately simple:

    calculation_history
    -------------------
    id          INTEGER PRIMARY KEY AUTOINCREMENT
    expression  TEXT NOT NULL
    result      TEXT NOT NULL
    created_at  TEXT NOT NULL
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# The database file lives next to this package by default; it can be
# overridden through the CALCULATOR_DB environment variable.
_DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "calculator.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS calculation_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    expression  TEXT    NOT NULL,
    result      TEXT    NOT NULL,
    created_at  TEXT    NOT NULL
);
"""


def _get_db_path() -> Path:
    """Resolve the database file path from the environment or default."""
    import os

    override = os.environ.get("CALCULATOR_DB")
    if override:
        return Path(override)
    return _DEFAULT_DB_PATH


class HistoryRepository:
    """Thin wrapper around the sqlite3 connection."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = db_path or _get_db_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(_SCHEMA)
            connection.commit()

    def insert(self, expression: str, result: str) -> int:
        """Persist one calculation record and return its id."""
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO calculation_history (expression, result, created_at) "
                "VALUES (?, ?, ?)",
                (expression, result, created_at),
            )
            connection.commit()
            return int(cursor.lastrowid)

    def get_latest(self, limit: int = 100) -> List[Dict[str, object]]:
        """Return the most recent records, newest first."""
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, expression, result, created_at "
                "FROM calculation_history ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def delete(self, record_id: int) -> bool:
        """Delete one record.  Returns True when a row was removed."""
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM calculation_history WHERE id = ?", (record_id,)
            )
            connection.commit()
            return cursor.rowcount > 0

    def clear(self) -> int:
        """Delete every record.  Returns the number of removed rows."""
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM calculation_history")
            connection.commit()
            return cursor.rowcount


# A module-level default repository shared by the FastAPI app.
repository = HistoryRepository()
