"""Elections mode: periodic leadership selection built on existing village state."""

from __future__ import annotations

from typing import Iterable

from TheVillage.core.models import InternalState
from TheVillage.governance import (
    get_leader,
    maybe_run_crisis_election,
    maybe_run_revalidation_election,
    maybe_run_scheduled_election,
    run_election,
)


class ElectionsMode:
    @staticmethod
    def _as_int(value: object, fallback: int = 0) -> int:
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str) and value.strip().lstrip("-").isdigit():
            return int(value)
        return fallback

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
        names = list(villager_names)

        scheduled = maybe_run_scheduled_election(state, names)
        if isinstance(scheduled, dict):
            return {
                "mode": "elections",
                "triggered": 1,
                "leader": str(scheduled.get("leader", get_leader(state))),
                "changed": self._as_int(scheduled.get("changed", 0), 0),
            }

        crisis = maybe_run_crisis_election(state, names)
        if isinstance(crisis, dict):
            return {
                "mode": "elections",
                "triggered": 1,
                "leader": str(crisis.get("leader", get_leader(state))),
                "changed": self._as_int(crisis.get("changed", 0), 0),
            }

        revalidation = maybe_run_revalidation_election(state, names)
        if isinstance(revalidation, dict):
            return {
                "mode": "elections",
                "triggered": 1,
                "leader": str(revalidation.get("leader", get_leader(state))),
                "changed": self._as_int(revalidation.get("changed", 0), 0),
            }

        if not self._is_triggered(state):
            return {
                "mode": "elections",
                "triggered": 0,
                "leader": get_leader(state),
            }

        result = run_election(
            state,
            names,
            election_type="pressure",
            reason="Election trigger fired from contradiction/tension pressure.",
        )
        return {
            "mode": "elections",
            "triggered": 1,
            "leader": str(result.get("leader", get_leader(state))),
            "changed": self._as_int(result.get("changed", 0), 0),
        }
