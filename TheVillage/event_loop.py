"""Event registration and dispatch helpers for evolutionary modes."""

from __future__ import annotations

from typing import Any

from TheVillage.core.models import InternalState


def register_event(state: InternalState, event_type: str, payload: dict[str, Any]) -> None:
    event_name = (event_type or "generic").strip() or "generic"
    if event_name not in state.registered_event_types:
        state.registered_event_types.append(event_name)
    state.event_backlog.append({"type": event_name, "payload": payload})
    state.event_backlog = state.event_backlog[-30:]


def dispatch_next_event(state: InternalState) -> dict[str, Any] | None:
    if not state.event_backlog:
        return None
    event = state.event_backlog.pop(0)
    headline = event.get("payload", {}).get("headline") or f"Event fired: {event.get('type', 'generic')}"
    state.recent_events.append(str(headline))
    state.recent_events = state.recent_events[-20:]
    return event
