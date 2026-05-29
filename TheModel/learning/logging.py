"""JSONL logging adapted from tools/feedback_store.py."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
LEARNING_DIR = BASE_DIR / "runtime" / "learning"
LEARNING_DIR.mkdir(parents=True, exist_ok=True)

CONVERSATION_LOG = LEARNING_DIR / "conversation_log.jsonl"
FEEDBACK_LOG = LEARNING_DIR / "feedback_log.jsonl"
VOCABULARY_LOG = LEARNING_DIR / "vocabulary_log.jsonl"


def _append_jsonl(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def append_conversation(entry: dict) -> None:
    _append_jsonl(CONVERSATION_LOG, {"ts": datetime.now(timezone.utc).isoformat(), **entry})


def append_feedback(entry: dict) -> None:
    _append_jsonl(FEEDBACK_LOG, {"ts": datetime.now(timezone.utc).isoformat(), **entry})


def append_vocabulary(entry: dict) -> None:
    _append_jsonl(VOCABULARY_LOG, {"ts": datetime.now(timezone.utc).isoformat(), **entry})