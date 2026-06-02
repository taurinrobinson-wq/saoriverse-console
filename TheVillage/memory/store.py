"""Persistent storage helpers for TheVillage state and capsules."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from TheVillage.core.models import InternalState
from TheVillage.memory.capsule import MemoryCapsule


BASE_DIR = Path(__file__).resolve().parents[1]
RUNTIME_DIR = BASE_DIR / "runtime"
SESSIONS_DIR = RUNTIME_DIR / "sessions"
CAPSULE_DIR = RUNTIME_DIR / "capsules"

SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
CAPSULE_DIR.mkdir(parents=True, exist_ok=True)


def _session_path(session_id: str) -> Path:
    return SESSIONS_DIR / f"{session_id}.json"


def _capsule_path(session_id: str) -> Path:
    return CAPSULE_DIR / f"{session_id}.json"


def load_state(session_id: str) -> InternalState:
    path = _session_path(session_id)
    if not path.exists():
        return InternalState(session_id=session_id)
    payload = json.loads(path.read_text(encoding="utf-8"))
    return InternalState.from_dict(payload)


def save_state(state: InternalState) -> None:
    path = _session_path(state.session_id)
    path.write_text(json.dumps(state.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


def load_capsules(session_id: str) -> List[MemoryCapsule]:
    path = _capsule_path(session_id)
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [MemoryCapsule.from_dict(item) for item in payload]


def append_capsule(session_id: str, capsule: MemoryCapsule) -> None:
    capsules = load_capsules(session_id)
    capsules.append(capsule)
    path = _capsule_path(session_id)
    path.write_text(
        json.dumps([item.to_dict() for item in capsules[-50:]], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def reset_session(session_id: str) -> None:
    for path in (_session_path(session_id), _capsule_path(session_id)):
        if path.exists():
            path.unlink()