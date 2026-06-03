"""Unified evolution engine for routing village cycles through active pressure modes."""

from __future__ import annotations

from typing import Iterable

from TheVillage.aura import interpret_global_state
from TheVillage.core.models import InternalState
from TheVillage.modes.disruption import DisruptionMode
from TheVillage.modes.elections import ElectionsMode
from TheVillage.modes.homeostasis import HomeostasisMode

VALID_MODES = {"homeostasis", "disruption", "elections"}


class EvolutionEngine:
    def __init__(self):
        self.homeostasis = HomeostasisMode()
        self.disruption = DisruptionMode()
        self.elections = ElectionsMode()

    @staticmethod
    def normalize_mode(mode: str | None, fallback: str = "homeostasis") -> str:
        proposed = (mode or fallback or "homeostasis").strip().lower()
        return proposed if proposed in VALID_MODES else "homeostasis"

    def run_cycle(
        self,
        state: InternalState,
        villager_names: Iterable[str],
        *,
        mode: str | None = None,
        aura=None,
    ) -> dict:
        active_mode = self.normalize_mode(mode, state.evolution_mode)
        state.evolution_mode = active_mode

        if active_mode == "homeostasis":
            mode_result = self.homeostasis.apply(state, aura=aura)
        elif active_mode == "disruption":
            mode_result = self.disruption.apply(state)
        elif active_mode == "elections":
            mode_result = self.elections.apply(state, villager_names)
        else:
            mode_result = {"mode": "homeostasis"}

        # Aura is always the final interpretive layer for the resulting global state.
        forecast = interpret_global_state(state, aura)
        state.evolution_meta["last_mode_result"] = dict(mode_result)
        state.mode_history.append(active_mode)
        state.mode_history = state.mode_history[-40:]
        state.recent_events.append(f"Evolution mode {active_mode} completed. Aura final reading updated.")
        state.recent_events = state.recent_events[-20:]

        return {
            "mode": active_mode,
            "forecast": forecast,
            "result": mode_result,
        }
