"""Disruption mode: inject bounded disturbances into the existing village event flow."""

from __future__ import annotations

import random

from TheVillage.core.models import Goal, InternalState, clamp_01
from TheVillage.event_loop import dispatch_next_event, register_event


class DisruptionMode:
    def __init__(self):
        self.library = [
            {
                "type": "signal_noise",
                "headline": "A burst of signal noise blurred several house cues.",
                "stress": 0.03,
                "coherence": -0.02,
                "novelty": 0.04,
            },
            {
                "type": "resource_dip",
                "headline": "A temporary resource dip tightened the village schedule.",
                "stress": 0.04,
                "coherence": -0.015,
                "novelty": 0.01,
            },
            {
                "type": "surprise_opportunity",
                "headline": "A surprise opportunity arrived and challenged current priorities.",
                "stress": 0.015,
                "coherence": -0.01,
                "novelty": 0.05,
            },
        ]

    def _maybe_register_disruption(self, state: InternalState) -> dict | None:
        cooldown_raw = state.evolution_meta.get("disruption_cooldown", 0)
        if isinstance(cooldown_raw, (int, float)):
            cooldown = max(0, int(cooldown_raw))
        elif isinstance(cooldown_raw, str) and cooldown_raw.isdigit():
            cooldown = int(cooldown_raw)
        else:
            cooldown = 0
        if cooldown > 0:
            state.evolution_meta["disruption_cooldown"] = cooldown - 1
            return None

        should_fire = (state.turn_index % 3 == 0) or (random.random() < 0.25)
        if not should_fire:
            return None

        disruption = random.choice(self.library)
        register_event(state, disruption["type"], disruption)
        state.evolution_meta["disruption_cooldown"] = 2
        return disruption

    def _apply_disruption_effect(self, state: InternalState, event: dict) -> None:
        payload = event.get("payload", {})
        stress_delta = float(payload.get("stress", 0.0))
        coherence_delta = float(payload.get("coherence", 0.0))
        novelty_delta = float(payload.get("novelty", 0.0))

        state.bodily_state["tension"] = clamp_01(state.bodily_state.get("tension", 0.2) + stress_delta)
        state.environment.coherence = clamp_01(state.environment.coherence + coherence_delta)
        state.environment.novelty = clamp_01(state.environment.novelty + novelty_delta)

        # Houses adapt through mission-focused repair goals rather than a parallel behavior system.
        if not any(goal.name == "absorb_disruption" for goal in state.active_goals):
            state.active_goals.append(
                Goal(
                    name="absorb_disruption",
                    drive="integration",
                    priority=0.74,
                    created_turn=state.turn_index,
                    last_updated_turn=state.turn_index,
                )
            )

    def apply(self, state: InternalState) -> dict[str, str | int]:
        registered = self._maybe_register_disruption(state)
        fired_event = dispatch_next_event(state)
        if fired_event is not None:
            self._apply_disruption_effect(state, fired_event)

        return {
            "mode": "disruption",
            "registered": int(registered is not None),
            "dispatched": int(fired_event is not None),
        }
