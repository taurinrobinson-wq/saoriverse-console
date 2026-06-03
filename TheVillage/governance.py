"""Governance helpers for executive leadership transitions."""

from __future__ import annotations

from collections.abc import Mapping

from TheVillage.core.models import InternalState


def get_leader(state: InternalState) -> str:
    return (state.executive_function or "Tomas").strip() or "Tomas"


def set_leader(state: InternalState, leader: str, reason: str | None = None) -> None:
    selected = (leader or "Tomas").strip() or "Tomas"
    previous = get_leader(state)
    state.executive_function = selected
    if previous != selected:
        note = f"Leadership shifted from {previous} to {selected}."
        if reason:
            note = f"{note} Reason: {reason}"
        state.recent_events.append(note)
        state.recent_events = state.recent_events[-20:]


def choose_leader(candidate_scores: Mapping[str, float]) -> str:
    if not candidate_scores:
        return "Tomas"
    return max(candidate_scores.items(), key=lambda item: item[1])[0]
