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
from pathlib import Path

DEFAULT_STORE = Path(__file__).resolve(
).parents[2] / "data" / "disambiguation_memory.jsonl"


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
        self.store_path = Path(store_path or DEFAULT_STORE)
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        # ensure file exists
        if not self.store_path.exists():
            self.store_path.write_text("")

    def _is_correction(self, user_input: str) -> bool:
        if not user_input:
            return False
        ui = user_input.lower()
        for p in self.TRIGGER_PATTERNS:
            if re.search(p, ui):
                return True
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

        record = {
            "original_input": original,
            "system_response": system_resp or "",
            "user_clarification": user_input,
            "corrected_intent": context.get("inferred_intent") or None,
            "trigger": _normalize_trigger(original or user_input),
        }

        # append as JSONL
        with open(self.store_path, "a", encoding="utf8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

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
                lines = fh.read().strip().splitlines()
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
