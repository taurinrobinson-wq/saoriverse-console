import json
import os
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
import threading

from emotional_os.adapter.clarification_store import get_default_store, ClarificationStore

# Simple process-global lock to serialize JSONL writes when multiple threads
# append to the same JSONL file. This prevents lost lines on platforms where
# concurrent appends from multiple threads can interleave or be dropped.
_jsonl_write_lock = threading.Lock()


class ClarificationTrace:
	def __init__(self, store_path: Optional[Path] = None, store: Optional[ClarificationStore] = None):
		self.store_path = Path(store_path) if store_path else None
		self._store = store or get_default_store()

	def _is_correction(self, text: str) -> bool:
		t = text.lower()
		return "meant" in t or t.startswith("no,") or "i meant" in t

	def detect_and_store(self, clarification: str, context: Optional[Dict[str, Any]] = None) -> bool:
		ctx = dict(context or {})
		if not self._is_correction(clarification):
			return False

		original = ctx.get("last_user_input") or ctx.get("original_input") or ctx.get("user_input")
		trigger = str(uuid.uuid4())
		corrected_intent = ctx.get("inferred_intent")

		# If a JSONL store_path was provided, prefer writing to it directly
		# (tests construct ClarificationTrace with a JSONL path when they
		# expect JSONL-based storage).
		if self.store_path:
			rec = {
				"trigger": trigger,
				"original_input": (original or "")[:500],
				"user_clarification": clarification[:1000],
				"corrected_intent": corrected_intent,
				"context": ctx,
				"conversation_id": ctx.get("conversation_id"),
				"user_id": ctx.get("user_id"),
			}
			self.store_path.parent.mkdir(parents=True, exist_ok=True)
			# Serialize writes to avoid races in concurrent test scenarios
			with _jsonl_write_lock:
				with open(self.store_path, "a", encoding="utf8") as f:
					f.write(json.dumps(rec, ensure_ascii=False) + "\n")
					try:
						f.flush()
						os.fsync(f.fileno())
					except Exception:
						# best-effort; ignore if fsync isn't available
						pass
			try:
				os.chmod(self.store_path, 0o600)
			except Exception:
				pass
			return True

		# Try DB insert first if no JSONL path provided
		try:
			ok = self._store.insert(trigger, original or "", corrected_intent, ctx, timeout=float(os.environ.get("CLARIFICATION_DB_INSERT_TIMEOUT", 0.5)))
			if ok:
				return True
		except Exception:
			ok = False

		return False

	def lookup(self, original_input: str) -> Optional[Dict[str, Any]]:
		# If a JSONL path was provided, prefer reading that (tests create
		# ClarificationTrace with a JSONL path and expect JSONL-only behavior).
		if self.store_path:
			if self.store_path.exists():
				for ln in reversed(self.store_path.read_text(encoding="utf8").splitlines()):
					if not ln.strip():
						continue
					try:
						rec = json.loads(ln)
					except Exception:
						continue
					if rec.get("original_input") and rec.get("original_input").lower().strip() == original_input.lower().strip():
						return rec
			# If JSONL was provided but no match, do not fall back to DB
			return None

		# Otherwise, check DB first (legacy/default behavior)
		try:
			conn = self._store
			# direct DB access
			import sqlite3
			db = sqlite3.connect(str(self._store.db_path), timeout=1, check_same_thread=False)
			cur = db.cursor()
			cur.execute("SELECT trigger, original_input, corrected_intent, context_json FROM clarifications ORDER BY id DESC LIMIT 100")
			rows = cur.fetchall()
			db.close()
			for tr, orig, corr, ctx_json in rows:
				if orig and original_input and orig.lower().strip() == original_input.lower().strip():
					try:
						ctx = json.loads(ctx_json) if ctx_json else {}
					except Exception:
						ctx = {}
					return {"trigger": tr, "original_input": orig, "corrected_intent": corr, "context": ctx}
		except Exception:
			pass

		return None
