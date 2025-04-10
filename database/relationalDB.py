# relational_db.py
import sqlite3
import asyncio
from contextlib import contextmanager
from typing import Any, Dict, Iterable, List, Sequence, Tuple

Row = Dict[str, Any]


class RelationalDB:
    """
    Minimal relational‑DB helper that an agent (or any Python code) can call.
    Uses SQLite by default but accepts any PEP‑249 connection.
    """

    def __init__(self, path: str = "data.db") -> None:
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # rows behave like dicts

    def create_table(self, name: str, schema_sql: str) -> None:
        """
        Example:  db.create_table("tasks",
                                  "id INTEGER PRIMARY KEY, "
                                  "description TEXT, status TEXT")
        """
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.execute(f"CREATE TABLE IF NOT EXISTS {name} ({schema_sql});")
        self.conn.commit()

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        keys = ", ".join(data)
        qs   = ", ".join("?" for _ in data)
        cur  = self.conn.execute(
            f"INSERT INTO {table} ({keys}) VALUES ({qs});",
            tuple(data.values()),
        )
        self.conn.commit()
        return cur.lastrowid            # handy for autoincrement PKs

    def fetch(self, sql: str, params: Sequence[Any] | None = None) -> List[Dict]:
        cur = self.conn.execute(sql, params or ())
        return [dict(row) for row in cur.fetchall()]

    def close(self) -> None:
        self.conn.close()
