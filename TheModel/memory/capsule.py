"""Relational memory capsules adapted from src/relational_memory.py."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List


@dataclass
class MemoryCapsule:
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
    def from_dict(cls, payload: dict) -> "MemoryCapsule":
        raw_timestamp = payload.get("timestamp")
        timestamp = datetime.fromisoformat(raw_timestamp) if raw_timestamp else datetime.now(timezone.utc)
        return cls(
            symbolic_tags=payload.get("symbolic_tags", []),
            relational_phase=payload.get("relational_phase", ""),
            voltage_marking=payload.get("voltage_marking", ""),
            user_input=payload.get("user_input", ""),
            response_summary=payload.get("response_summary", ""),
            timestamp=timestamp,
        )