"""Aura integration helpers for global interpretation hooks."""

from __future__ import annotations

from TheVillage.core.models import InternalState
from TheVillage.core.villagers import Aura


def interpret_global_state(state: InternalState, aura: Aura | None = None) -> str:
    """Run Aura as the final interpretive layer for the latest global state."""
    active_aura = aura or Aura(state)
    active_aura.update_arc_and_tension()
    return active_aura.generate_forecast()
