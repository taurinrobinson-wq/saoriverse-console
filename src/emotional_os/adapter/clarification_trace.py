import json
import os
import uuid
from pathlib import Path
from typing import Optional, Dict, Any

from emotional_os.adapter.clarification_store import get_default_store, ClarificationStore


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

		# Try DB insert first
		try:
			ok = self._store.insert(trigger, original or "", corrected_intent, ctx, timeout=float(os.environ.get("CLARIFICATION_DB_INSERT_TIMEOUT", 0.5)))
			if ok:
				return True
		except Exception:
			ok = False

		# Fallback to JSONL
		if self.store_path:
			rec = {
				"trigger": trigger,
				"original_input": (original or "")[:500],
				"user_clarification": clarification[:1000],
				"corrected_intent": corrected_intent,
				"context": ctx,
			}
			self.store_path.parent.mkdir(parents=True, exist_ok=True)
			with open(self.store_path, "a", encoding="utf8") as f:
				f.write(json.dumps(rec, ensure_ascii=False) + "\n")
			try:
				os.chmod(self.store_path, 0o600)
			except Exception:
				pass
			return True

		return False

	def lookup(self, original_input: str) -> Optional[Dict[str, Any]]:
		# Check DB first
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

		# Check JSONL
		if self.store_path and self.store_path.exists():
			for ln in reversed(self.store_path.read_text(encoding="utf8").splitlines()):
				if not ln.strip():
					continue
				try:
					rec = json.loads(ln)
				except Exception:
					continue
				if rec.get("original_input") and rec.get("original_input").lower().strip() == original_input.lower().strip():
					return rec

		return None
