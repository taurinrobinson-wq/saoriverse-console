"""Homeostasis mode: stabilize stress, drift, and coherence via light-touch corrections."""

from __future__ import annotations

from dataclasses import dataclass

from TheVillage.aura import interpret_global_state
from TheVillage.core.models import InternalState
from TheVillage.village_state import update_emotional_field


@dataclass
class HomeostasisThresholds:
    stress_high: float = 0.45
    drift_high: float = 0.5
    coherence_low: float = 0.55


class HomeostasisMode:
    def __init__(self, thresholds: HomeostasisThresholds | None = None):
        self.thresholds = thresholds or HomeostasisThresholds()

    def apply(self, state: InternalState, aura=None) -> dict[str, float | str]:
        stress = float(state.bodily_state.get("tension", 0.0))
        drift = max(
            float(state.background_processes.get("rumination", 0.0)),
            float(state.background_processes.get("monitoring", 0.0)),
        )
        coherence = min(float(state.environment.coherence), float(state.self_model.get("coherence", 0.0)))

        stress_relief = 0.0
        coherence_boost = 0.0
        drift_relief = 0.0

        if stress >= self.thresholds.stress_high:
            stress_relief += 0.03
        if drift >= self.thresholds.drift_high:
            drift_relief += 0.03
        if coherence <= self.thresholds.coherence_low:
            coherence_boost += 0.035

        if stress_relief > 0.0 or drift_relief > 0.0 or coherence_boost > 0.0:
            update_emotional_field(
                state,
                stress_relief=stress_relief,
                coherence_boost=coherence_boost,
                drift_relief=drift_relief,
            )
            state.recent_events.append(
                "Homeostasis mode damped stress/drift and reinforced coherence after threshold pressure."
            )
            state.recent_events = state.recent_events[-20:]

        forecast = interpret_global_state(state, aura)
        return {
            "mode": "homeostasis",
            "stress_relief": round(stress_relief, 3),
            "coherence_boost": round(coherence_boost, 3),
            "drift_relief": round(drift_relief, 3),
            "forecast": forecast,
        }
