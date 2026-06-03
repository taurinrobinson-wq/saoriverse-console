"""Elections mode: periodic leadership selection built on existing village state."""

from __future__ import annotations

from typing import Iterable

from TheVillage.core.models import InternalState
from TheVillage.governance import choose_leader, get_leader, set_leader


class ElectionsMode:
    def _is_triggered(self, state: InternalState) -> bool:
        contradictions = max(
            int(state.health_metrics.contradiction_count),
            len(state.unresolved_tensions),
        )
        cadence = state.turn_index > 0 and state.turn_index % 6 == 0
        pressure = contradictions >= 2 or float(state.bodily_state.get("tension", 0.0)) > 0.5
        return cadence or pressure

    def _score_candidates(self, state: InternalState, villager_names: Iterable[str]) -> dict[str, float]:
        scores: dict[str, float] = {}
        for name in villager_names:
            villager_state = state.villager_states.get(name)
            reward_trend = float(villager_state.reward_trend) if villager_state is not None else 0.0
            role = (villager_state.role if villager_state is not None else "").lower()

            score = 0.5 + reward_trend * 0.25
            if "stability" in role and state.health_metrics.contradiction_count > 0:
                score += 0.12
            if "planner" in role and state.health_metrics.stalled_goals > 0:
                score += 0.1
            if "caretaker" in role and float(state.bodily_state.get("tension", 0.0)) > 0.45:
                score += 0.1
            if "curiosity" in role and state.health_metrics.vocabulary_growth_rate < 0.2:
                score += 0.06
            scores[name] = round(score, 4)
        return scores

    def apply(self, state: InternalState, villager_names: Iterable[str]) -> dict[str, str | int]:
        if not self._is_triggered(state):
            return {
                "mode": "elections",
                "triggered": 0,
                "leader": get_leader(state),
            }

        scores = self._score_candidates(state, villager_names)
        winner = choose_leader(scores)
        previous = get_leader(state)
        reason = f"Election trigger fired with candidate scores: {scores}"
        set_leader(state, winner, reason=reason)

        return {
            "mode": "elections",
            "triggered": 1,
            "leader": get_leader(state),
            "changed": int(previous != winner),
        }
