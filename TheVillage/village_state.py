"""State helpers that extend existing village dynamics without replacing core loops."""

from __future__ import annotations

from TheVillage.core.models import InternalState, clamp_01


def update_emotional_field(
    state: InternalState,
    *,
    stress_relief: float = 0.0,
    coherence_boost: float = 0.0,
    drift_relief: float = 0.0,
) -> None:
    """Apply a light-touch homeostatic correction onto the current state."""
    state.bodily_state["tension"] = clamp_01(state.bodily_state.get("tension", 0.2) - stress_relief)
    state.environment.coherence = clamp_01(state.environment.coherence + coherence_boost)
    state.self_model["coherence"] = clamp_01(state.self_model.get("coherence", 0.5) + coherence_boost * 0.7)
    state.background_processes["rumination"] = clamp_01(
        state.background_processes.get("rumination", 0.0) - drift_relief
    )
    state.background_processes["monitoring"] = clamp_01(
        state.background_processes.get("monitoring", 0.0) - drift_relief * 0.6
    )
