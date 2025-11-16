"""
learning/writer.py
Append-only JSONL writer and reader helpers for local learning events.

Schema (per-line JSON object):
{
  "id": "uuid4 string",
  "timestamp": "ISO8601 UTC string",
  "source": "string (module or system name)",
  "event_type": "string (e.g., 'candidate', 'accept', 'reject')",
  "payload": { ... arbitrary event data ... },
  "confidence": number|null
}

Notes:
- Files are append-only. Writers should append a single JSON object per
  line, flush, and fsync to minimize data loss on crashes.
- Readers should treat the file as newline-delimited JSON and tolerate
  trailing partial lines (they will be ignored).

This module provides small helper functions to write and read events
in a consistent, atomic way.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional


DEFAULT_LEARNING_DIR = os.path.join(
    os.path.dirname(__file__), "..", "learning")


def ensure_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_event(path: str, event: Dict[str, Any]) -> None:
    """Append a single event (dict) as a JSON line to `path`.

    The function will ensure parent directories exist, open the file in
    append-binary mode, write the JSON and newline, flush and fsync.
    """
    ensure_dir(path)
    # Normalize event: ensure id and timestamp exist
    evt = dict(event)
    evt.setdefault("id", str(uuid.uuid4()))
    evt.setdefault("timestamp", _now_iso())

    line = (json.dumps(evt, ensure_ascii=False) + "\n").encode("utf-8")

    # Write atomically by flushing and syncing
    with open(path, "ab") as fh:
        fh.write(line)
        fh.flush()
        try:
            os.fsync(fh.fileno())
        except OSError:
            # On some platforms (e.g., some network filesystems) fsync
            # may not be available or permitted; swallow the error but
            # keep writing semantics best-effort.
            pass


def read_events(path: str) -> Iterable[Dict[str, Any]]:
    """Yield parsed JSON objects from a JSONL file at `path`.

    Ignores partial/truncated final lines and continues on parse errors
    while logging nothing (caller can handle exceptions if desired).
    """
    if not os.path.exists(path):
        return

    with open(path, "rb") as fh:
        for raw in fh:
            try:
                line = raw.decode("utf-8").strip()
            except Exception:
                continue
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                # Skip malformed line
                continue


def read_all(path: str) -> List[Dict[str, Any]]:
    return list(read_events(path))
