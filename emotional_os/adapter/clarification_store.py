"""SQLite-backed store for clarification traces.

Provides simple insert and lookup by trigger and optional conversation scope.
"""
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any, List
import os
import time

DEFAULT_DB = Path(os.environ.get("CLARIFICATION_TRACE_DB") or Path(
    __file__).resolve().parents[2] / "data" / "disambiguation_memory.db")


class ClarificationStore:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path or DEFAULT_DB)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self):
        # Reduce client-side timeout to avoid long blocking when DB is locked.
        return sqlite3.connect(str(self.db_path), timeout=0.5, check_same_thread=False)

    def _init_db(self):
        sql = """
        CREATE TABLE IF NOT EXISTS clarifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT,
            user_id TEXT,
            trigger TEXT NOT NULL,
            original_input TEXT,
            system_response TEXT,
            user_clarification TEXT,
            corrected_intent TEXT,
            created_at INTEGER
        );
        CREATE INDEX IF NOT EXISTS ix_trigger ON clarifications(trigger);
        CREATE INDEX IF NOT EXISTS ix_convo_trigger ON clarifications(conversation_id, trigger);
        -- Ensure uniqueness per conversation+trigger to avoid duplicate clarifications
        CREATE UNIQUE INDEX IF NOT EXISTS ux_convo_trigger ON clarifications(conversation_id, trigger);
        """
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.executescript(sql)
            conn.commit()
        finally:
            conn.close()

    def insert(self, record: Dict[str, Any]) -> int:
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            # Use INSERT OR IGNORE to avoid violating unique constraint under contention.
            cur.execute(
                "INSERT OR IGNORE INTO clarifications (conversation_id, user_id, trigger, original_input, system_response, user_clarification, corrected_intent, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    record.get("conversation_id"),
                    record.get("user_id"),
                    record.get("trigger"),
                    record.get("original_input"),
                    record.get("system_response"),
                    record.get("user_clarification"),
                    record.get("corrected_intent"),
                    int(time.time()),
                ),
            )
            conn.commit()
            # If insert was ignored due to uniqueness, fetch existing id
            if cur.lastrowid:
                return cur.lastrowid
            # fallback: select existing row id
            cur.execute("SELECT id FROM clarifications WHERE conversation_id=? AND trigger=? LIMIT 1",
                        (record.get("conversation_id"), record.get("trigger")))
            row = cur.fetchone()
            return row[0] if row else None
        finally:
            conn.close()

    def lookup(self, trigger: str, conversation_id: Optional[str] = None, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            if conversation_id:
                cur.execute("SELECT conversation_id, user_id, trigger, original_input, system_response, user_clarification, corrected_intent, created_at FROM clarifications WHERE conversation_id=? AND trigger=? ORDER BY created_at DESC LIMIT 1", (conversation_id, trigger))
            elif user_id:
                cur.execute("SELECT conversation_id, user_id, trigger, original_input, system_response, user_clarification, corrected_intent, created_at FROM clarifications WHERE user_id=? AND trigger=? ORDER BY created_at DESC LIMIT 1", (user_id, trigger))
            else:
                cur.execute("SELECT conversation_id, user_id, trigger, original_input, system_response, user_clarification, corrected_intent, created_at FROM clarifications WHERE trigger=? ORDER BY created_at DESC LIMIT 1", (trigger,))
            row = cur.fetchone()
            if not row:
                return None
            keys = ["conversation_id", "user_id", "trigger", "original_input",
                    "system_response", "user_clarification", "corrected_intent", "created_at"]
            return dict(zip(keys, row))
        finally:
            conn.close()

    def update_corrected_intent(self, rowid: int, corrected_intent: Optional[str]) -> bool:
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE clarifications SET corrected_intent=? WHERE id=?", (corrected_intent, rowid))
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()


_default_store = None


def get_default_store() -> ClarificationStore:
    global _default_store
    if _default_store is None:
        _default_store = ClarificationStore()
    return _default_store


__all__ = ["ClarificationStore", "get_default_store"]
