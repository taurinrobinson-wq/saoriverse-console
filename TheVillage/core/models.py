"""Core data models for TheVillage."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List


def clamp_01(value: float) -> float:
    return max(0.0, min(1.0, value))


@dataclass
class Goal:
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
class Task:
    description: str
    proposed_by: str
    priority: float
    expected_reward: float
    dependencies: List[str] = field(default_factory=list)
    status: str = "proposed"

    def to_dict(self) -> dict:
        return {
            "description": self.description,
            "proposed_by": self.proposed_by,
            "priority": round(self.priority, 3),
            "expected_reward": round(self.expected_reward, 3),
            "dependencies": list(self.dependencies),
            "status": self.status,
        }


@dataclass
class MainMission:
    statement: str = "Increase internal coherence and conceptual richness over time."

    def to_dict(self) -> dict:
        return {"statement": self.statement}


@dataclass
class HealthMetrics:
    goal_progress_rate: float = 0.0
    contradiction_count: int = 0
    vocabulary_growth_rate: float = 0.0
    error_events: int = 0
    stalled_goals: int = 0
    global_health: float = 0.6

    def to_dict(self) -> dict:
        return {
            "goal_progress_rate": round(self.goal_progress_rate, 3),
            "contradiction_count": self.contradiction_count,
            "vocabulary_growth_rate": round(self.vocabulary_growth_rate, 3),
            "error_events": self.error_events,
            "stalled_goals": self.stalled_goals,
            "global_health": round(self.global_health, 3),
        }


@dataclass
class VillagerState:
    name: str
    role: str
    mood: str = "steady"
    skills: List[str] = field(default_factory=list)
    memory_refs: List[str] = field(default_factory=list)
    recent_tasks: List[str] = field(default_factory=list)
    recent_outcomes: List[str] = field(default_factory=list)
    reward_trend: float = 0.0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "role": self.role,
            "mood": self.mood,
            "skills": list(self.skills),
            "memory_refs": list(self.memory_refs),
            "recent_tasks": list(self.recent_tasks),
            "recent_outcomes": list(self.recent_outcomes),
            "reward_trend": round(self.reward_trend, 3),
        }


@dataclass
class EnvironmentState:
    scene: str = "intake"
    safety: float = 0.7
    novelty: float = 0.2
    coherence: float = 0.6
    last_event: str = "The environment is waiting for input."
    affordances: List[str] = field(default_factory=lambda: ["observe", "ask", "rest", "approach"])

    def to_dict(self) -> dict:
        return {
            "scene": self.scene,
            "safety": round(self.safety, 3),
            "novelty": round(self.novelty, 3),
            "coherence": round(self.coherence, 3),
            "last_event": self.last_event,
            "affordances": list(self.affordances),
        }


@dataclass
class InternalState:
    session_id: str
    turn_index: int = 0
    current_day: int = 1
    last_run: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    working_memory: List[str] = field(default_factory=list)
    long_term_memory: List[str] = field(default_factory=list)
    emotional_state: Dict[str, float] = field(default_factory=lambda: {
        "valence": 0.5,
        "arousal": 0.2,
        "social_threat": 0.0,
        "attachment_pressure": 0.0,
        "curiosity": 0.3,
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
        "curiosity": 0.3,
    })
    background_processes: Dict[str, float] = field(default_factory=lambda: {
        "rumination": 0.0,
        "monitoring": 0.0,
        "repair": 0.0,
        "lexicon_growth": 0.0,
    })
    active_goals: List[Goal] = field(default_factory=list)
    main_mission: MainMission = field(default_factory=MainMission)
    health_metrics: HealthMetrics = field(default_factory=HealthMetrics)
    villager_states: Dict[str, VillagerState] = field(default_factory=dict)
    task_backlog: List[Task] = field(default_factory=list)
    recent_events: List[str] = field(default_factory=list)
    narrative_log: List[str] = field(default_factory=list)
    subsystem_scores: Dict[str, float] = field(default_factory=dict)
    unresolved_tensions: List[str] = field(default_factory=list)
    narrative: str = ""
    reward_signal: float = 0.0
    vocabulary_questions: List[dict] = field(default_factory=list)
    known_terms: List[str] = field(default_factory=list)
    environment: EnvironmentState = field(default_factory=EnvironmentState)

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "turn_index": self.turn_index,
            "current_day": self.current_day,
            "last_run": self.last_run,
            "working_memory": list(self.working_memory),
            "long_term_memory": list(self.long_term_memory),
            "emotional_state": {key: round(value, 3) for key, value in self.emotional_state.items()},
            "bodily_state": {key: round(value, 3) for key, value in self.bodily_state.items()},
            "self_model": {key: round(value, 3) for key, value in self.self_model.items()},
            "background_processes": {key: round(value, 3) for key, value in self.background_processes.items()},
            "active_goals": [goal.to_dict() for goal in self.active_goals],
            "main_mission": self.main_mission.to_dict(),
            "health_metrics": self.health_metrics.to_dict(),
            "villager_states": {key: value.to_dict() for key, value in self.villager_states.items()},
            "task_backlog": [task.to_dict() for task in self.task_backlog],
            "recent_events": list(self.recent_events),
            "narrative_log": list(self.narrative_log),
            "subsystem_scores": {key: round(value, 3) for key, value in self.subsystem_scores.items()},
            "unresolved_tensions": list(self.unresolved_tensions),
            "narrative": self.narrative,
            "reward_signal": round(self.reward_signal, 3),
            "vocabulary_questions": list(self.vocabulary_questions),
            "known_terms": list(self.known_terms),
            "environment": self.environment.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "InternalState":
        defaults = cls(session_id=data.get("session_id", "default"))
        goals = [Goal(**goal) for goal in data.get("active_goals", [])]
        tasks = [Task(**task) for task in data.get("task_backlog", [])]
        env_data = data.get("environment", {})
        environment = EnvironmentState(
            scene=env_data.get("scene", defaults.environment.scene),
            safety=env_data.get("safety", defaults.environment.safety),
            novelty=env_data.get("novelty", defaults.environment.novelty),
            coherence=env_data.get("coherence", defaults.environment.coherence),
            last_event=env_data.get("last_event", defaults.environment.last_event),
            affordances=env_data.get("affordances", defaults.environment.affordances),
        )
        health_data = data.get("health_metrics", {})
        health_metrics = HealthMetrics(
            goal_progress_rate=health_data.get("goal_progress_rate", 0.0),
            contradiction_count=health_data.get("contradiction_count", 0),
            vocabulary_growth_rate=health_data.get("vocabulary_growth_rate", 0.0),
            error_events=health_data.get("error_events", 0),
            stalled_goals=health_data.get("stalled_goals", 0),
            global_health=health_data.get("global_health", 0.6),
        )
        mission_data = data.get("main_mission", {})
        mission = MainMission(statement=mission_data.get("statement", defaults.main_mission.statement))
        villager_states = {
            key: VillagerState(
                name=value.get("name", key),
                role=value.get("role", "villager"),
                mood=value.get("mood", "steady"),
                skills=value.get("skills", []),
                memory_refs=value.get("memory_refs", []),
                recent_tasks=value.get("recent_tasks", []),
                recent_outcomes=value.get("recent_outcomes", []),
                reward_trend=value.get("reward_trend", 0.0),
            )
            for key, value in data.get("villager_states", {}).items()
        }
        return cls(
            session_id=data.get("session_id", defaults.session_id),
            turn_index=data.get("turn_index", defaults.turn_index),
            current_day=data.get("current_day", defaults.current_day),
            last_run=data.get("last_run", defaults.last_run),
            working_memory=data.get("working_memory", []),
            long_term_memory=data.get("long_term_memory", []),
            emotional_state=data.get("emotional_state") or defaults.emotional_state,
            bodily_state=data.get("bodily_state") or defaults.bodily_state,
            self_model=data.get("self_model") or defaults.self_model,
            background_processes=data.get("background_processes") or defaults.background_processes,
            active_goals=goals,
            main_mission=mission,
            health_metrics=health_metrics,
            villager_states=villager_states,
            task_backlog=tasks,
            recent_events=data.get("recent_events", []),
            narrative_log=data.get("narrative_log", []),
            subsystem_scores=data.get("subsystem_scores", {}),
            unresolved_tensions=data.get("unresolved_tensions", []),
            narrative=data.get("narrative", ""),
            reward_signal=data.get("reward_signal", 0.0),
            vocabulary_questions=data.get("vocabulary_questions", []),
            known_terms=data.get("known_terms", []),
            environment=environment,
        )


@dataclass
class Interpretation:
    features: Dict[str, float]
    tokens: List[str]
    unknown_terms: List[str]


@dataclass
class InteractionResult:
    session_id: str
    turn_index: int
    text: str
    action: str
    interpretation: Interpretation
    state: InternalState
    environment_feedback: Dict[str, object]

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "turn_index": self.turn_index,
            "text": self.text,
            "action": self.action,
            "interpretation": {
                "features": {key: round(value, 3) for key, value in self.interpretation.features.items()},
                "tokens": list(self.interpretation.tokens),
                "unknown_terms": list(self.interpretation.unknown_terms),
            },
            "state": self.state.to_dict(),
            "environment_feedback": self.environment_feedback,
        }