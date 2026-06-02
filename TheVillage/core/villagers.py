"""Village-style subsystem abstractions for TheVillage."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from TheVillage.core.models import EnvironmentState, Goal, InternalState, Task, VillagerState, clamp_01


def _ensure_villager_state(state: InternalState, name: str, role: str, skills: List[str]) -> VillagerState:
    villager = state.villager_states.get(name)
    if villager is None:
        villager = VillagerState(name=name, role=role, skills=list(skills))
        state.villager_states[name] = villager
    else:
        villager.role = role
        villager.skills = list(skills)
    return villager


@dataclass
class Villager:
    name: str
    role: str
    skills: List[str] = field(default_factory=list)
    mood: str = "steady"
    memory_refs: List[str] = field(default_factory=list)

    def ensure_state(self, state: InternalState) -> VillagerState:
        villager_state = _ensure_villager_state(state, self.name, self.role, self.skills)
        villager_state.mood = self.mood
        villager_state.memory_refs = list(self.memory_refs)
        return villager_state

    def propose_tasks(self, state: InternalState, environment: EnvironmentState) -> List[Task]:
        return []

    def evaluate_outcomes(self, state: InternalState, environment: EnvironmentState) -> str:
        health = state.health_metrics.global_health
        if health > 0.72:
            return f"{self.name} thinks the village is moving in the right direction."
        if health < 0.45:
            return f"{self.name} is worried about the strain showing across the village."
        return f"{self.name} sees mixed signals and wants another day of careful work."

    def to_dialogue_view(self, state: InternalState, recent_events: List[str]) -> str:
        villager_state = self.ensure_state(state)
        task_text = villager_state.recent_tasks[-1] if villager_state.recent_tasks else "keeping watch over the work"
        event_text = recent_events[-1] if recent_events else "The square is quiet for the moment."
        return (
            f"{self.name}, the {self.role}, feels {villager_state.mood}. "
            f"Today they focused on {task_text}. {event_text}"
        )


class PlannerVillager(Villager):
    def __init__(self):
        super().__init__(
            name="Tomas",
            role="planner",
            skills=["goal decomposition", "prioritization", "maintenance"],
        )

    def propose_tasks(self, state: InternalState, environment: EnvironmentState) -> List[Task]:
        self.ensure_state(state)
        tasks = [
            Task(
                description=f"Break the mission into the next concrete step for day {state.current_day}",
                proposed_by=self.name,
                priority=0.82,
                expected_reward=0.2,
            )
        ]
        if not state.active_goals:
            tasks.append(
                Task(
                    description="Refresh active goals so the village keeps a clear direction",
                    proposed_by=self.name,
                    priority=0.78,
                    expected_reward=0.16,
                )
            )
        if environment.coherence < 0.72:
            tasks.append(
                Task(
                    description="Schedule a coherence walk through the environment",
                    proposed_by=self.name,
                    priority=0.7,
                    expected_reward=0.14,
                )
            )
        return tasks


class CuriosityVillager(Villager):
    def __init__(self):
        super().__init__(
            name="Mira",
            role="curiosity keeper",
            skills=["vocabulary growth", "question asking", "definition finding"],
        )

    def propose_tasks(self, state: InternalState, environment: EnvironmentState) -> List[Task]:
        self.ensure_state(state)
        tasks: List[Task] = []
        for question in state.vocabulary_questions[:2]:
            tasks.append(
                Task(
                    description=f"Seek a definition for '{question['term']}' and add it to the village lexicon",
                    proposed_by=self.name,
                    priority=0.8,
                    expected_reward=0.22,
                )
            )
        if state.self_model.get("curiosity", 0.0) > 0.45 and not tasks:
            tasks.append(
                Task(
                    description="Survey recent language for weakly understood concepts",
                    proposed_by=self.name,
                    priority=0.62,
                    expected_reward=0.12,
                )
            )
        return tasks


class StabilityVillager(Villager):
    def __init__(self):
        super().__init__(
            name="Edda",
            role="stability steward",
            skills=["contradiction tracking", "repair", "coherence monitoring"],
        )

    def propose_tasks(self, state: InternalState, environment: EnvironmentState) -> List[Task]:
        self.ensure_state(state)
        metrics = state.health_metrics
        tasks: List[Task] = []
        if metrics.contradiction_count > 1 or state.unresolved_tensions:
            tasks.append(
                Task(
                    description="Resolve contradictions and reduce internal tension",
                    proposed_by=self.name,
                    priority=0.88,
                    expected_reward=0.2,
                )
            )
        if metrics.stalled_goals > 0:
            tasks.append(
                Task(
                    description="Unstick stalled goals and restore motion",
                    proposed_by=self.name,
                    priority=0.76,
                    expected_reward=0.16,
                )
            )
        if environment.coherence < 0.65:
            tasks.append(
                Task(
                    description="Patch weak coherence in the environment model",
                    proposed_by=self.name,
                    priority=0.7,
                    expected_reward=0.13,
                )
            )
        return tasks


class NarratorVillager(Villager):
    def __init__(self):
        super().__init__(
            name="Lio",
            role="narrator",
            skills=["memory weaving", "summary", "story continuity"],
        )

    def propose_tasks(self, state: InternalState, environment: EnvironmentState) -> List[Task]:
        self.ensure_state(state)
        return [
            Task(
                description="Record the village's important events into a coherent daybook entry",
                proposed_by=self.name,
                priority=0.66,
                expected_reward=0.1,
            )
        ]


class ArchitectVillager(Villager):
    def __init__(self):
        super().__init__(
            name="Sable",
            role="architect",
            skills=["system design", "reward tuning", "structure revision"],
        )

    def propose_tasks(self, state: InternalState, environment: EnvironmentState) -> List[Task]:
        self.ensure_state(state)
        tasks: List[Task] = []
        if state.health_metrics.goal_progress_rate < 0.35:
            tasks.append(
                Task(
                    description="Adjust internal reward weights to favor progress and coherence",
                    proposed_by=self.name,
                    priority=0.72,
                    expected_reward=0.14,
                )
            )
        tasks.append(
            Task(
                description="Review the goal structure for redundant or conflicting work",
                proposed_by=self.name,
                priority=0.58,
                expected_reward=0.09,
            )
        )
        return tasks


class CaretakerVillager(Villager):
    def __init__(self):
        super().__init__(
            name="Jun",
            role="caretaker",
            skills=["health monitoring", "self-repair", "recovery"],
        )

    def propose_tasks(self, state: InternalState, environment: EnvironmentState) -> List[Task]:
        self.ensure_state(state)
        metrics = state.health_metrics
        tasks: List[Task] = []
        if metrics.global_health < 0.55 or metrics.error_events > 0:
            tasks.append(
                Task(
                    description="Run a self-diagnosis and repair cycle for the village",
                    proposed_by=self.name,
                    priority=0.9,
                    expected_reward=0.22,
                )
            )
        if state.bodily_state.get("tension", 0.0) > 0.45:
            tasks.append(
                Task(
                    description="Guide the village into a recovery pause to reduce tension",
                    proposed_by=self.name,
                    priority=0.74,
                    expected_reward=0.15,
                )
            )
        return tasks


def default_villagers() -> List[Villager]:
    return [
        PlannerVillager(),
        CuriosityVillager(),
        StabilityVillager(),
        NarratorVillager(),
        ArchitectVillager(),
        CaretakerVillager(),
    ]


def derive_mood(reward_trend: float, global_health: float) -> str:
    score = reward_trend * 0.55 + (global_health - 0.5) * 0.45
    if score > 0.18:
        return "hopeful"
    if score < -0.18:
        return "worried"
    return "steady"


def record_villager_outcome(state: InternalState, villager: Villager, task: str, outcome: str, reward_delta: float) -> None:
    villager_state = villager.ensure_state(state)
    villager_state.recent_tasks.append(task)
    villager_state.recent_tasks = villager_state.recent_tasks[-8:]
    villager_state.recent_outcomes.append(outcome)
    villager_state.recent_outcomes = villager_state.recent_outcomes[-8:]
    villager_state.reward_trend = clamp_01((villager_state.reward_trend + reward_delta + 1.0) / 2.0) * 2.0 - 1.0
    villager_state.mood = derive_mood(villager_state.reward_trend, state.health_metrics.global_health)