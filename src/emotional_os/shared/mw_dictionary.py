"""Merriam-Webster dictionary lookup helpers for FirstPerson surfaces.

Uses server-side env var MW_DICTIONARY_API_KEY and in-process caching to reduce
request volume.
"""

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

_MW_DICTIONARY_API_KEY_ENV = "MW_DICTIONARY_API_KEY"
_MW_DICTIONARY_API_KEY_ALIASES = (
    _MW_DICTIONARY_API_KEY_ENV,
    "MERRIAM_WEBSTER_DICTIONARY_API_KEY",
    "MERIAM_WEBSTER_DICTIONARY_API_KEY",
)
_MW_DICTIONARY_BASE_URL = "https://www.dictionaryapi.com/api/v3/references/collegiate/json"
_SESSION_LOOKUP_EVENTS: dict[str, list[float]] = defaultdict(list)
_SESSION_LOOKUP_LOCK = threading.Lock()


def _check_and_record_rate_limit(
    session_key: str,
    *,
    max_per_hour: int = 40,
    max_per_minute: int = 12,
) -> tuple[bool, str | None]:
    now = time.time()
    hour_ago = now - 3600
    minute_ago = now - 60

    with _SESSION_LOOKUP_LOCK:
        events = _SESSION_LOOKUP_EVENTS[session_key]
        events[:] = [ts for ts in events if ts >= hour_ago]

        minute_count = sum(1 for ts in events if ts >= minute_ago)
        hour_count = len(events)

        if minute_count >= max_per_minute:
            return (
                False,
                f"Rate limit reached for this session ({max_per_minute} lookups/minute).",
            )
        if hour_count >= max_per_hour:
            return (
                False,
                f"Rate limit reached for this session ({max_per_hour} lookups/hour).",
            )

        events.append(now)
    return True, None


def _normalize_lookup_word(word: str) -> str:
    normalized = word.strip().lower()
    normalized = re.sub(r"[^a-z\-\s']", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


@lru_cache(maxsize=512)
def _query_dictionary_cached(word: str) -> Any:
    return _query_dictionary_uncached(word)


def _resolve_dictionary_api_key() -> str:
    for env_name in _MW_DICTIONARY_API_KEY_ALIASES:
        value = os.getenv(env_name, "").strip()
        if value:
            return value
    return ""


def _query_dictionary_uncached(word: str) -> Any:
    api_key = _resolve_dictionary_api_key()
    if not api_key:
        return {
            "_error": (
                "Missing dictionary API key env var. "
                f"Checked: {', '.join(_MW_DICTIONARY_API_KEY_ALIASES)}"
            )
        }

    quoted_word = urllib.parse.quote(word)
    quoted_key = urllib.parse.quote(api_key)
    url = f"{_MW_DICTIONARY_BASE_URL}/{quoted_word}?key={quoted_key}"

    try:
        with urllib.request.urlopen(url, timeout=4) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        return {"_error": f"Dictionary lookup failed: {exc}"}


def _query_dictionary(word: str, *, force_refresh: bool = False) -> tuple[Any, bool]:
    if force_refresh:
        return _query_dictionary_uncached(word), False

    before_hits = _query_dictionary_cached.cache_info().hits
    payload = _query_dictionary_cached(word)
    after_hits = _query_dictionary_cached.cache_info().hits
    return payload, after_hits > before_hits


def lookup_word(
    word: str,
    max_defs: int = 3,
    session_key: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    normalized = _normalize_lookup_word(word)
    if not normalized:
        return {"ok": False, "error": "Please provide a valid word to define."}

    if session_key:
        allowed, reason = _check_and_record_rate_limit(session_key)
        if not allowed:
            return {"ok": False, "word": normalized, "error": reason}

    payload, cache_hit = _query_dictionary(normalized, force_refresh=force_refresh)
    if isinstance(payload, dict) and payload.get("_error"):
        return {"ok": False, "word": normalized, "error": payload["_error"]}

    if not isinstance(payload, list):
        return {"ok": False, "word": normalized, "error": "Unexpected dictionary response format."}

    if payload and isinstance(payload[0], str):
        suggestions = [item for item in payload if isinstance(item, str)][:8]
        return {
            "ok": False,
            "word": normalized,
            "error": "No exact entry found.",
            "suggestions": suggestions,
        }

    if not payload:
        return {"ok": False, "word": normalized, "error": "No dictionary entry found."}

    entry = payload[0] if isinstance(payload[0], dict) else {}
    hwi = entry.get("hwi", {}) if isinstance(entry, dict) else {}
    meta = entry.get("meta", {}) if isinstance(entry, dict) else {}

    headword = hwi.get("hw") if isinstance(hwi, dict) else None
    if isinstance(headword, str):
        headword = headword.replace("*", "")
    else:
        headword = normalized

    fl = entry.get("fl") if isinstance(entry, dict) else None
    shortdef_raw = entry.get("shortdef") if isinstance(entry, dict) else []
    shortdef = shortdef_raw if isinstance(shortdef_raw, list) else []
    defs = [d for d in shortdef if isinstance(d, str)][: max(1, max_defs)]

    stems: list[str] = []
    if isinstance(meta, dict):
        raw_stems = meta.get("stems")
        if isinstance(raw_stems, list):
            stems = [s for s in raw_stems if isinstance(s, str)][:10]

    return {
        "ok": True,
        "word": normalized,
        "headword": headword,
        "part_of_speech": fl if isinstance(fl, str) else None,
        "definitions": defs,
        "stems": stems,
        "source": "merriam_webster_collegiate",
        "debug": {
            "cache_hit": cache_hit,
            "force_refresh": force_refresh,
            "api_key_configured": bool(_resolve_dictionary_api_key()),
        },
    }


def format_lookup_response(result: dict[str, Any]) -> str:
    if not result.get("ok"):
        suggestions = result.get("suggestions") or []
        suffix = ""
        if suggestions:
            suffix = f" Suggestions: {', '.join(suggestions)}"
        return f"I couldn't find an exact dictionary entry. {result.get('error', 'Lookup failed.')}{suffix}"

    headword = result.get("headword") or result.get("word") or "(unknown)"
    part = result.get("part_of_speech")
    defs = result.get("definitions") or []

    lines = [f"Definition: {headword}"]
    if part:
        lines.append(f"Part of speech: {part}")
    for index, definition in enumerate(defs, start=1):
        lines.append(f"{index}. {definition}")
    return "\n".join(lines)
