"""Relational memory capsule storage and retrieval.

This is a lightweight in-memory store suitable for prototyping. It is
privacy-conscious: stored capsules do not contain backend identifiers and
are intended to be recalled in emotional language only.
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class RelationalMemoryCapsule:
    symbolic_tags: List[str]
    relational_phase: str
    voltage_marking: str
    user_input: str
    response_summary: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "symbolic_tags": self.symbolic_tags,
            "relational_phase": self.relational_phase,
            "voltage_marking": self.voltage_marking,
            "user_input": self.user_input,
            "response_summary": self.response_summary,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "RelationalMemoryCapsule":
        ts = d.get("timestamp")
        dt = datetime.fromisoformat(ts) if ts else datetime.now(timezone.utc)
        return cls(
            symbolic_tags=d.get("symbolic_tags", []),
            relational_phase=d.get("relational_phase", ""),
            voltage_marking=d.get("voltage_marking", ""),
            user_input=d.get("user_input", ""),
            response_summary=d.get("response_summary", ""),
            timestamp=dt,
        )


# Simple in-memory store; consider swapping for a lightweight DB later.
_CAPSULE_STORE: List[RelationalMemoryCapsule] = []


def store_capsule(capsule: RelationalMemoryCapsule) -> None:
    """Store a capsule in the in-memory list."""
    _CAPSULE_STORE.append(capsule)


def retrieve_capsule_by_tag(tag: str) -> List[RelationalMemoryCapsule]:
    """Return capsules that include `tag` in `symbolic_tags`."""
    return [c for c in _CAPSULE_STORE if tag in c.symbolic_tags]


def list_recent(limit: int = 10) -> List[RelationalMemoryCapsule]:
    """Return the most recent `limit` capsules (most recent first)."""
    return sorted(_CAPSULE_STORE, key=lambda c: c.timestamp, reverse=True)[:limit]


def save_store(path: str) -> None:
    """Persist the in-memory capsule store to `path` as JSON.

    This writes an array of capsule dicts. Existing files will be overwritten.
    """
    data = [c.to_dict() for c in _CAPSULE_STORE]
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def load_store(path: str) -> None:
    """Load capsule entries from `path` (JSON array) into the in-memory store.

    Existing in-memory items are preserved; loaded items are appended.
    """
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        return

    for item in data:
        try:
            capsule = RelationalMemoryCapsule.from_dict(item)
            _CAPSULE_STORE.append(capsule)
        except Exception:
            # Skip malformed entries but continue loading remaining
            continue
