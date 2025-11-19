"""Clarification Trace

Detects user clarifications/corrections, stores them in a local
disambiguation memory (JSONL), and provides a lookup to bias future
interpretation toward corrected intents.

Storage: `data/disambiguation_memory.jsonl` (created if missing).
"""
from typing import Optional, Dict, Any
import os
import json
import re
import fcntl
import stat
from pathlib import Path

DEFAULT_STORE = Path(__file__).resolve(
).parents[2] / "data" / "disambiguation_memory.jsonl"

# Limits to keep stored records bounded (avoid huge user text in logs)
MAX_ORIGINAL = 500
MAX_SYSTEM_RESP = 2000
MAX_USER_CLAR = 1000


class ClarificationTrace:
    TRIGGER_PATTERNS = [
        r"^\s*(no\s*,?\s*i\s+meant)\b",
        r"^\s*(actually\b)",
        r"^\s*(not that[\-—]?what)\b",
        r"^\s*(not that)\b",
        r"^\s*(i mean)\b",
        r"^\s*(sorry,?\s*i)\b",
    ]

    def __init__(self, store_path: Optional[Path] = None):
        # allow overriding the store path via env var
        env_path = os.environ.get("CLARIFICATION_TRACE_STORE")
        if store_path:
            self.store_path = Path(store_path)
        elif env_path:
            self.store_path = Path(env_path)
        else:
            self.store_path = Path(DEFAULT_STORE)

        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        # ensure file exists with secure permissions
        if not self.store_path.exists():
            # create file and set owner-only perms where possible
            open(self.store_path, "a", encoding="utf8").close()
            try:
                os.chmod(self.store_path, 0o600)
            except Exception:
                # ignore if chmod unsupported
                pass

    def _is_correction(self, user_input: str) -> bool:
        if not user_input:
            return False
        ui = user_input.lower()
        # allow override via env var of comma-separated regex patterns
        patterns = os.environ.get("CLARIFICATION_TRIGGER_PATTERNS")
        if patterns:
            pats = [p.strip() for p in patterns.split(",") if p.strip()]
        else:
            pats = self.TRIGGER_PATTERNS

        for p in pats:
            try:
                if re.search(p, ui):
                    return True
            except re.error:
                continue
        return False

    def detect_and_store(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Detect a clarification and store a disambiguation record.

        `context` may include:
          - last_user_input
          - last_system_response
          - inferred_intent (optional)

        Returns True if a clarification was detected and stored.
        """
        context = context or {}
        if not self._is_correction(user_input):
            return False

        original = context.get(
            "last_user_input") or context.get("original_input")
        system_resp = context.get(
            "last_system_response") or context.get("system_response")
        if not original:
            # Nothing to anchor to — still store the raw clarification for future signals
            original = ""

        # truncate fields to safe lengths
        original = (original or "")[:MAX_ORIGINAL]
        system_resp = (system_resp or "")[:MAX_SYSTEM_RESP]
        user_input_trunc = (user_input or "")[:MAX_USER_CLAR]

        record = {
            "original_input": original,
            "system_response": system_resp,
            "user_clarification": user_input_trunc,
            "corrected_intent": context.get("inferred_intent") or None,
            "trigger": _normalize_trigger(original or user_input_trunc),
        }

        # append as JSONL with advisory file lock for safety
        try:
            # Prefer the SQLite-backed store when available
            store = get_default_store()
            # attempt to infer intent automatically
            inferred = None
            needs_confirmation = False
            try:
                diag = tag_input_with_diagnostics(user_input)
                tags = diag.get("tags", [])
                matches = diag.get("matches", [])
                # Map symbolic tags to a simple intent
                if "initiatory_signal" in tags:
                    inferred = "emotional_checkin"
                elif "containment_request" in tags:
                    inferred = "containment_support"
                elif "voltage_surge" in tags:
                    inferred = "voltage_help"

                # Evaluate confidence: any regex match gives high confidence
                confidence = 0.0
                for m in matches:
                    if m.get("match_type") == "regex":
                        confidence = max(confidence, 1.0)
                    else:
                        try:
                            score = float(m.get("score", 0.0))
                        except Exception:
                            score = 0.0
                        confidence = max(confidence, score)

                if inferred and confidence < 0.85:
                    # Low-confidence candidate — ask for confirmation instead
                    needs_confirmation = True
                else:
                    # commit corrected_intent when confident
                    record["corrected_intent"] = inferred

            except Exception:
                inferred = None
                needs_confirmation = False

            # attach optional conversation/user identifiers if provided
            if context.get("conversation_id"):
                record["conversation_id"] = context.get("conversation_id")
            if context.get("user_id"):
                record["user_id"] = context.get("user_id")

            rowid = store.insert(record)
            result = {"stored": True, "rowid": rowid, "inferred_intent": inferred,
                      "needs_confirmation": needs_confirmation}
            # keep backward compatibility: store last result and return boolean
            try:
                self._last_result = result
            except Exception:
                pass
            return True
        except Exception:
            # fallback to file append as legacy behaviour
            try:
                with open(self.store_path, "a", encoding="utf8") as fh:
                    try:
                        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
                    except Exception:
                        pass
                    fh.write(json.dumps(record, ensure_ascii=False) + "\n")
                    fh.flush()
                    try:
                        fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
                    except Exception:
                        pass
            except Exception:
                pass
            result = {"stored": True, "rowid": None,
                      "inferred_intent": None, "needs_confirmation": False}
            try:
                self._last_result = result
            except Exception:
                pass
            return True

    def lookup(self, phrase: str) -> Optional[Dict[str, Any]]:
        """Look for a recent clarification matching `phrase` (normalized).

        Returns the most recent matching record or None.
        """
        key = _normalize_trigger(phrase)
        if not key:
            return None

        try:
            with open(self.store_path, "r", encoding="utf8") as fh:
                try:
                    fcntl.flock(fh.fileno(), fcntl.LOCK_SH)
                except Exception:
                    pass
                lines = fh.read().strip().splitlines()
                try:
                    fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
                except Exception:
                    pass
        except Exception:
            return None

        # iterate in reverse to prefer recent
        for ln in reversed(lines):
            try:
                rec = json.loads(ln)
            except Exception:
                continue
            if rec.get("trigger") == key:
                return rec
        return None


def _normalize_trigger(s: str) -> str:
    if not s:
        return ""
    s = s.strip().lower()
    # strip punctuation and extra whitespace
    s = re.sub(r"[^a-z0-9\s]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s


__all__ = ["ClarificationTrace"]
