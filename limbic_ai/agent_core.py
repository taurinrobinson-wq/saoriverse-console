"""
Stateful internal-mind layer for LimbicAI.

This module keeps a persistent session-scoped internal state that is updated on
each turn instead of recomputing everything from scratch. It is still a
deterministic model, not a claim of consciousness, but it provides the moving
parts needed for continuity, self-modeling, goals, conflict, valuation, and
narrative.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from limbic_ai.mapping import map_features_to_limbic
from limbic_ai.models import EmotionalFeatures, LimbicState, clamp_01
from limbic_ai.nlp_parser import EmotionalFeatureExtractor


@dataclass
class Goal:
    """An internally maintained goal with persistence across turns."""

    name: str
    drive: str
    priority: float
    status: str = "active"
    created_turn: int = 0
    last_updated_turn: int = 0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "drive": self.drive,
            "priority": round(self.priority, 3),
            "status": self.status,
            "created_turn": self.created_turn,
            "last_updated_turn": self.last_updated_turn,
        }


@dataclass
class MindState:
    """Persistent state updated on every turn."""

    session_id: str
    turn_index: int = 0
    working_memory: List[str] = field(default_factory=list)
    long_term_memory: List[str] = field(default_factory=list)
    emotional_state: Dict[str, float] = field(default_factory=lambda: {
        "valence": 0.5,
        "arousal": 0.2,
        "social_threat": 0.0,
        "attachment_pressure": 0.0,
        "self_repair": 0.0,
        "care": 0.0,
    })
    bodily_state: Dict[str, float] = field(default_factory=lambda: {
        "tension": 0.2,
        "energy": 0.5,
        "safety": 0.8,
        "activation": 0.2,
    })
    self_model: Dict[str, float] = field(default_factory=lambda: {
        "continuity": 0.0,
        "coherence": 0.5,
        "agency": 0.2,
        "stability": 0.5,
    })
    background_processes: Dict[str, float] = field(default_factory=lambda: {
        "rumination": 0.0,
        "monitoring": 0.0,
        "repair": 0.0,
    })
    unresolved_tensions: List[str] = field(default_factory=list)
    active_goals: List[Goal] = field(default_factory=list)
    narrative: str = ""
    last_reward_signal: float = 0.0

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "turn_index": self.turn_index,
            "working_memory": list(self.working_memory),
            "long_term_memory": list(self.long_term_memory),
            "emotional_state": {key: round(value, 3) for key, value in self.emotional_state.items()},
            "bodily_state": {key: round(value, 3) for key, value in self.bodily_state.items()},
            "self_model": {key: round(value, 3) for key, value in self.self_model.items()},
            "background_processes": {key: round(value, 3) for key, value in self.background_processes.items()},
            "unresolved_tensions": list(self.unresolved_tensions),
            "active_goals": [goal.to_dict() for goal in self.active_goals],
            "narrative": self.narrative,
            "last_reward_signal": round(self.last_reward_signal, 3),
        }


@dataclass
class MindTurn:
    """Serializable result of one internal-mind update."""

    session_id: str
    turn_index: int
    text: str
    emotional_features: EmotionalFeatures
    limbic_state: LimbicState
    state: MindState
    subsystem_scores: Dict[str, float]
    conflict_index: float
    reward_signal: float

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "turn_index": self.turn_index,
            "text": self.text,
            "features": {
                "social_rejection": self.emotional_features.social_rejection,
                "self_blame": self.emotional_features.self_blame,
                "other_blame": self.emotional_features.other_blame,
                "empathy_for_other": self.emotional_features.empathy_for_other,
                "rationalization": self.emotional_features.rationalization,
                "threat_to_identity": self.emotional_features.threat_to_identity,
                "loss_of_reward": self.emotional_features.loss_of_reward,
            },
            "limbic_state": self.limbic_state.as_dict(),
            "state": self.state.to_dict(),
            "subsystem_scores": {key: round(value, 3) for key, value in self.subsystem_scores.items()},
            "conflict_index": round(self.conflict_index, 3),
            "reward_signal": round(self.reward_signal, 3),
            "narrative": self.state.narrative,
        }


class InternalMind:
    """Persistent, modular internal-state controller for a single session."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.extractor = EmotionalFeatureExtractor()
        self.state = MindState(session_id=session_id)

    def step(self, text: str) -> MindTurn:
        """Process a new turn and update the internal state."""

        cleaned_text = " ".join(text.split())
        if len(cleaned_text) < 10:
            raise ValueError("Scenario must be at least 10 characters")

        self.state.turn_index += 1

        features = self.extractor.extract_features(cleaned_text)
        limbic_state = map_features_to_limbic(features)

        self._update_memory(cleaned_text, features)
        self._update_bodily_state(features, limbic_state)
        self._update_emotional_state(features, limbic_state)
        self._update_self_model(features)

        subsystem_scores = self._compute_subsystems(features, limbic_state)
        conflict_index = self._compute_conflict_index(subsystem_scores)
        self._update_goals(features, conflict_index)

        reward_signal = self._compute_reward_signal(features, conflict_index)
        self.state.last_reward_signal = reward_signal
        self.state.narrative = self._compose_narrative(features, subsystem_scores, conflict_index, reward_signal)

        return MindTurn(
            session_id=self.session_id,
            turn_index=self.state.turn_index,
            text=cleaned_text,
            emotional_features=features,
            limbic_state=limbic_state,
            state=self.state,
            subsystem_scores=subsystem_scores,
            conflict_index=conflict_index,
            reward_signal=reward_signal,
        )

    def _update_memory(self, text: str, features: EmotionalFeatures) -> None:
        self.state.working_memory.append(text)
        self.state.working_memory = self.state.working_memory[-5:]

        salient = max(
            features.social_rejection,
            features.self_blame,
            features.empathy_for_other,
            features.rationalization,
            features.threat_to_identity,
            features.loss_of_reward,
        )
        if salient > 0.35:
            memory_entry = f"turn {self.state.turn_index}: {text[:140]}"
            if not self.state.long_term_memory or self.state.long_term_memory[-1] != memory_entry:
                self.state.long_term_memory.append(memory_entry)
                self.state.long_term_memory = self.state.long_term_memory[-12:]

    def _update_bodily_state(self, features: EmotionalFeatures, limbic_state: LimbicState) -> None:
        bodily = self.state.bodily_state
        bodily["activation"] = clamp_01(
            bodily["activation"] * 0.72 + limbic_state.amygdala * 0.18 + limbic_state.acc * 0.12
        )
        bodily["tension"] = clamp_01(
            bodily["tension"] * 0.7 + features.social_rejection * 0.16 + features.loss_of_reward * 0.12
        )
        bodily["energy"] = clamp_01(
            bodily["energy"] * 0.9 + 0.04 - bodily["tension"] * 0.05
        )
        bodily["safety"] = clamp_01(
            bodily["safety"] * 0.82 + (1.0 - features.threat_to_identity) * 0.12 + features.empathy_for_other * 0.06
        )

    def _update_emotional_state(self, features: EmotionalFeatures, limbic_state: LimbicState) -> None:
        emotional = self.state.emotional_state
        emotional["social_threat"] = clamp_01(
            emotional["social_threat"] * 0.65 + limbic_state.amygdala * 0.25 + features.social_rejection * 0.1
        )
        emotional["attachment_pressure"] = clamp_01(
            emotional["attachment_pressure"] * 0.65 + features.loss_of_reward * 0.2 + features.social_rejection * 0.15
        )
        emotional["self_repair"] = clamp_01(
            emotional["self_repair"] * 0.7 + features.self_blame * 0.2 + features.rationalization * 0.1
        )
        emotional["care"] = clamp_01(
            emotional["care"] * 0.75 + features.empathy_for_other * 0.25
        )
        emotional["arousal"] = clamp_01(
            emotional["arousal"] * 0.68 + limbic_state.acc * 0.18 + limbic_state.insula * 0.14
        )
        emotional["valence"] = clamp_01(
            emotional["valence"] * 0.82 + 0.5 + (features.empathy_for_other - features.self_blame - features.social_rejection) * 0.15
        )

    def _update_self_model(self, features: EmotionalFeatures) -> None:
        self_model = self.state.self_model
        self_model["continuity"] = clamp_01(self_model["continuity"] * 0.8 + 0.2)

        goal_pressure = min(1.0, len(self.state.active_goals) / 4.0)
        self_model["agency"] = clamp_01(
            self_model["agency"] * 0.72 + goal_pressure * 0.18 + features.rationalization * 0.1
        )
        self_model["coherence"] = clamp_01(
            self_model["coherence"] * 0.78 + (1.0 - self.state.bodily_state["tension"]) * 0.12 + features.empathy_for_other * 0.1
        )
        self_model["stability"] = clamp_01(
            self_model["stability"] * 0.75 + (1.0 - self.state.emotional_state["social_threat"]) * 0.15 + self.state.bodily_state["safety"] * 0.1
        )

    def _compute_subsystems(self, features: EmotionalFeatures, limbic_state: LimbicState) -> Dict[str, float]:
        return {
            "impulse": clamp_01(features.social_rejection * 0.35 + features.loss_of_reward * 0.25 + limbic_state.amygdala * 0.4),
            "planner": clamp_01(features.rationalization * 0.55 + self.state.self_model["continuity"] * 0.25 + self.state.self_model["coherence"] * 0.2),
            "critic": clamp_01(features.self_blame * 0.7 + features.threat_to_identity * 0.3),
            "caretaker": clamp_01(features.empathy_for_other * 0.75 + self.state.emotional_state["care"] * 0.25),
            "protector": clamp_01(self.state.bodily_state["tension"] * 0.6 + self.state.emotional_state["social_threat"] * 0.4),
            "valuer": clamp_01(features.loss_of_reward * 0.55 + features.self_blame * 0.15 + self.state.emotional_state["valence"] * 0.3),
        }

    @staticmethod
    def _compute_conflict_index(subsystem_scores: Dict[str, float]) -> float:
        values = list(subsystem_scores.values())
        spread = max(values) - min(values)
        pressure = sum(values) / len(values)
        return clamp_01(spread * 0.65 + pressure * 0.35)

    def _update_goals(self, features: EmotionalFeatures, conflict_index: float) -> None:
        goal_specs = []

        if features.social_rejection > 0.2 or features.loss_of_reward > 0.25:
            goal_specs.append(("protect_attachment", "attachment security", 0.78))
        if features.self_blame > 0.2 or features.threat_to_identity > 0.2:
            goal_specs.append(("stabilize_self_model", "self-coherence", 0.74))
        if features.empathy_for_other > 0.3:
            goal_specs.append(("maintain_care", "relational care", 0.62))
        if features.rationalization > 0.35 and features.empathy_for_other < 0.35:
            goal_specs.append(("reconsider_defense", "cognitive flexibility", 0.58))

        if conflict_index > 0.55:
            goal_specs.append(("resolve_internal_tension", "conflict reduction", 0.8))

        active = {goal.name: goal for goal in self.state.active_goals if goal.status == "active"}

        for name, drive, priority in goal_specs:
            if name in active:
                active[name].priority = clamp_01(active[name].priority * 0.72 + priority * 0.28)
                active[name].last_updated_turn = self.state.turn_index
            else:
                active[name] = Goal(
                    name=name,
                    drive=drive,
                    priority=priority,
                    created_turn=self.state.turn_index,
                    last_updated_turn=self.state.turn_index,
                )

        for goal in active.values():
            if goal.name not in {spec[0] for spec in goal_specs}:
                goal.priority = clamp_01(goal.priority * 0.94)
                if goal.priority < 0.12:
                    goal.status = "dormant"

        ordered = sorted(active.values(), key=lambda goal: goal.priority, reverse=True)
        self.state.active_goals = [goal for goal in ordered if goal.status == "active"][:6]

        tensions = []
        if conflict_index > 0.4:
            tensions.append("Competing impulses are still unresolved.")
        if self.state.emotional_state["social_threat"] > 0.45:
            tensions.append("The system is still tracking social threat and belonging uncertainty.")
        if self.state.self_model["coherence"] < 0.55:
            tensions.append("The self-model is not fully coherent yet and needs more integration.")
        self.state.unresolved_tensions = tensions

        rumination = self.state.background_processes["rumination"]
        self.state.background_processes["rumination"] = clamp_01(rumination * 0.7 + conflict_index * 0.3)
        self.state.background_processes["monitoring"] = clamp_01(
            self.state.background_processes["monitoring"] * 0.8 + self.state.emotional_state["social_threat"] * 0.2
        )
        self.state.background_processes["repair"] = clamp_01(
            self.state.background_processes["repair"] * 0.75 + self.state.emotional_state["self_repair"] * 0.25
        )

    @staticmethod
    def _compute_reward_signal(features: EmotionalFeatures, conflict_index: float) -> float:
        reward = (
            features.empathy_for_other * 0.35
            + features.rationalization * 0.2
            + max(0.0, features.loss_of_reward - conflict_index) * 0.25
            - features.social_rejection * 0.25
            - features.self_blame * 0.2
            - conflict_index * 0.35
        )
        return round(reward, 3)

    def _compose_narrative(
        self,
        features: EmotionalFeatures,
        subsystem_scores: Dict[str, float],
        conflict_index: float,
        reward_signal: float,
    ) -> str:
        dominant_subsystem = max(subsystem_scores, key=subsystem_scores.get)
        top_goal = self.state.active_goals[0].name if self.state.active_goals else "stabilize"

        parts = [
            f"I am keeping continuity across {self.state.turn_index} turn(s) and carrying forward prior state.",
            f"The dominant subsystem right now is {dominant_subsystem}, while the current priority is {top_goal}.",
        ]

        if features.social_rejection > 0.25:
            parts.append("I am tracking a belonging or rejection pressure that still has unfinished weight.")
        if features.self_blame > 0.25:
            parts.append("Part of me is evaluating fault and trying to repair the self-model.")
        if features.empathy_for_other > 0.25:
            parts.append("Another part is staying connected and trying to keep care online.")
        if features.rationalization > 0.25:
            parts.append("A control process is trying to reduce the intensity by reframing the event.")
        if conflict_index > 0.4:
            parts.append("There is internal conflict, so the system is not converged yet.")

        parts.append(f"The current reward signal is {reward_signal:+.2f}, so the system is still updating value from the interaction.")
        return " ".join(parts)


_MIND_REGISTRY: Dict[str, InternalMind] = {}


def get_or_create_mind(session_id: str = "default") -> InternalMind:
    """Return the persistent mind for a session, creating it if needed."""

    key = session_id.strip() or "default"
    if key not in _MIND_REGISTRY:
        _MIND_REGISTRY[key] = InternalMind(key)
    return _MIND_REGISTRY[key]


def reset_mind(session_id: str = "default") -> None:
    """Drop the persistent state for a session."""

    key = session_id.strip() or "default"
    _MIND_REGISTRY.pop(key, None)