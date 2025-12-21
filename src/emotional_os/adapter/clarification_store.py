import sqlite3
from pathlib import Path
from typing import Optional, Any, Dict


class ClarificationStore:
	def __init__(self, db_path: Optional[Path] = None):
		self.db_path = Path(db_path or "emotional_os/data/clarifications.db")
		self.db_path.parent.mkdir(parents=True, exist_ok=True)
		self._ensure_table()

	def _ensure_table(self):
		conn = sqlite3.connect(str(self.db_path), timeout=1)
		cur = conn.cursor()
		cur.execute(
			"""
			CREATE TABLE IF NOT EXISTS clarifications (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				trigger TEXT,
				original_input TEXT,
				corrected_intent TEXT,
				context_json TEXT,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
			)
			"""
		)
		conn.commit()
		conn.close()

	def insert(self, trigger: str, original: str, corrected_intent: Optional[str], context: Optional[Dict[str, Any]] = None, timeout: float = 0.5) -> bool:
		import json
		try:
			conn = sqlite3.connect(str(self.db_path), timeout=timeout)
			cur = conn.cursor()
			cur.execute(
				"INSERT INTO clarifications (trigger, original_input, corrected_intent, context_json) VALUES (?, ?, ?, ?)",
				(trigger, original, corrected_intent or "", json.dumps(context or {})),
			)
			conn.commit()
			conn.close()
			return True
		except Exception:
			return False


_DEFAULT_STORE: Optional[ClarificationStore] = None


def get_default_store() -> ClarificationStore:
	global _DEFAULT_STORE
	if _DEFAULT_STORE is None:
		_DEFAULT_STORE = ClarificationStore()
	return _DEFAULT_STORE
