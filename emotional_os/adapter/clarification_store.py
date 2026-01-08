import json
import sqlite3
import threading
from pathlib import Path
from typing import Optional


class ClarificationStore:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else Path("clarifications.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._ensure_table()

    def _ensure_table(self):
        conn = sqlite3.connect(str(self.db_path), timeout=1, check_same_thread=False)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS clarifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trigger TEXT,
                original_input TEXT,
                corrected_intent TEXT,
                context_json TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
        conn.close()

    def insert(self, trigger: str, original: str, corrected_intent: Optional[str], context: dict, timeout: float = 0.5) -> bool:
        """Insert a clarification row. Returns True on success, False on timeout/failure."""
        try:
            with self._lock:
                conn = sqlite3.connect(str(self.db_path), timeout=timeout, check_same_thread=False)
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO clarifications (trigger, original_input, corrected_intent, context_json) VALUES (?, ?, ?, ?)",
                    (trigger, original, corrected_intent, json.dumps(context, ensure_ascii=False)),
                )
                conn.commit()
                conn.close()
            return True
        except Exception:
            return False


_default_store: Optional[ClarificationStore] = None


def get_default_store() -> ClarificationStore:
    global _default_store
    if _default_store is None:
        _default_store = ClarificationStore()
    return _default_store
