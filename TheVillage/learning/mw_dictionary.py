"""Merriam-Webster dictionary lookup adapted from src/emotional_os/shared/mw_dictionary.py."""

from __future__ import annotations

import json
import os
import re
import threading
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from functools import lru_cache
from typing import Any


_MW_DICTIONARY_API_KEY_ALIASES = (
    "MW_DICTIONARY_API_KEY",
    "MERRIAM_WEBSTER_DICTIONARY_API_KEY",
    "MERIAM_WEBSTER_DICTIONARY_API_KEY",
)
_MW_DICTIONARY_BASE_URL = "https://www.dictionaryapi.com/api/v3/references/collegiate/json"
_SESSION_LOOKUP_EVENTS: dict[str, list[float]] = defaultdict(list)
_SESSION_LOOKUP_LOCK = threading.Lock()


def _normalize_lookup_word(word: str) -> str:
    normalized = word.strip().lower()
    normalized = re.sub(r"[^a-z\-\s']", "", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _resolve_dictionary_api_key() -> str:
    for env_name in _MW_DICTIONARY_API_KEY_ALIASES:
        value = os.getenv(env_name, "").strip()
        if value:
            return value
    return ""


def _check_rate_limit(session_key: str, *, max_per_hour: int = 40, max_per_minute: int = 12) -> tuple[bool, str | None]:
    now = time.time()
    hour_ago = now - 3600
    minute_ago = now - 60
    with _SESSION_LOOKUP_LOCK:
        events = _SESSION_LOOKUP_EVENTS[session_key]
        events[:] = [timestamp for timestamp in events if timestamp >= hour_ago]
        minute_count = sum(1 for timestamp in events if timestamp >= minute_ago)
        if minute_count >= max_per_minute:
            return False, f"Rate limit reached for this session ({max_per_minute} lookups/minute)."
        if len(events) >= max_per_hour:
            return False, f"Rate limit reached for this session ({max_per_hour} lookups/hour)."
        events.append(now)
    return True, None


@lru_cache(maxsize=512)
def _query_dictionary(word: str) -> Any:
    api_key = _resolve_dictionary_api_key()
    if not api_key:
        return {"_error": f"Missing dictionary API key env var. Checked: {', '.join(_MW_DICTIONARY_API_KEY_ALIASES)}"}
    url = f"{_MW_DICTIONARY_BASE_URL}/{urllib.parse.quote(word)}?key={urllib.parse.quote(api_key)}"
    try:
        with urllib.request.urlopen(url, timeout=4) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        return {"_error": f"Dictionary lookup failed: {exc}"}


def lookup_word(word: str, *, session_key: str | None = None, max_defs: int = 3) -> dict[str, Any]:
    normalized = _normalize_lookup_word(word)
    if not normalized:
        return {"ok": False, "error": "Please provide a valid word to define."}
    if session_key:
        allowed, reason = _check_rate_limit(session_key)
        if not allowed:
            return {"ok": False, "word": normalized, "error": reason}
    payload = _query_dictionary(normalized)
    if isinstance(payload, dict) and payload.get("_error"):
        return {"ok": False, "word": normalized, "error": payload["_error"]}
    if not isinstance(payload, list) or not payload:
        return {"ok": False, "word": normalized, "error": "No dictionary entry found."}
    if isinstance(payload[0], str):
        return {"ok": False, "word": normalized, "error": "No exact entry found.", "suggestions": payload[:8]}
    entry = payload[0]
    shortdefs = entry.get("shortdef") if isinstance(entry, dict) else []
    if not isinstance(shortdefs, list):
        shortdefs = []
    stems = entry.get("meta", {}).get("stems", []) if isinstance(entry, dict) else []
    return {
        "ok": True,
        "word": normalized,
        "headword": entry.get("hwi", {}).get("hw", normalized).replace("*", ""),
        "part_of_speech": entry.get("fl"),
        "definitions": [definition for definition in shortdefs if isinstance(definition, str)][:max_defs],
        "stems": [stem for stem in stems if isinstance(stem, str)][:10],
        "source": "merriam_webster_collegiate",
    }