"""Core data models for TheVillage."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List


ROLE_AURA = "aura"


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
    statement: str = "Maintain coherence while increasing capacity for self-understanding, a seed of emergent internality."

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
    dream_state: Dict[str, float | int | str] = field(default_factory=dict)
    dream_log: List[str] = field(default_factory=list)
    house_brief: "HouseBrief" = field(default_factory=lambda: HouseBrief())

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
            "dream_state": dict(self.dream_state),
            "dream_log": list(self.dream_log),
            "house_brief": self.house_brief.to_dict(),
        }


@dataclass
class HouseBrief:
    house_goal: str = "Maintain steady contribution to village cohesion."
    problem_statement: str = "No active blocker is currently flagged."
    guidance_request: str = "Select a guidance style for today's work."
    choices: List[str] = field(default_factory=lambda: [
        "Take a conservative step to preserve stability.",
        "Try a moderate experiment to gather new signal.",
        "Coordinate with another house before acting.",
        "Invest in long-term structure over short-term speed.",
    ])
    selected_choice: int | None = None
    influence_strength: float = 0.2
    downstream_impacts: List[str] = field(default_factory=list)
    dream_insight: str | None = None
    aspiration: str | None = None

    def apply_governance_override(self, governance_context: dict | None = None) -> None:
        context = governance_context or {}
        crisis_active = bool(context.get("crisis_override_active"))
        transition_active = bool(context.get("transition_active"))
        legitimacy = float(context.get("legitimacy_score", 0.5))
        language_rules = context.get("language_rules") or {}

        if crisis_active or transition_active:
            self.influence_strength = clamp_01(self.influence_strength + 0.08)
            if "leadership" not in self.problem_statement.lower():
                self.problem_statement = f"Leadership transition pressure is active. {self.problem_statement}"
            guidance_lower = self.guidance_request.lower()
            has_transition_context = any(
                token in guidance_lower
                for token in ("transition", "handoff", "authority", "legitimacy", "revalidation")
            )
            if not has_transition_context:
                self.guidance_request = "Which guidance option best supports safe leadership transition and mission continuity?"
            if legitimacy < 0.5:
                self.downstream_impacts.append("Can restore leadership legitimacy and reduce contradiction pressure.")
            else:
                self.downstream_impacts.append("Helps consolidate post-election stability and cross-house trust.")

        disallowed = [str(item).lower() for item in (language_rules.get("disallowed_terms") or [])]
        replacements = language_rules.get("preferred_replacements") or {}
        for field_name in ("house_goal", "problem_statement", "guidance_request"):
            text = getattr(self, field_name)
            lowered = text.lower()
            for token in disallowed:
                if token and token in lowered:
                    replacement = str(replacements.get(token) or "functional concern")
                    text = text.replace(token, replacement).replace(token.title(), replacement.title())
            setattr(self, field_name, text)
        self.downstream_impacts = self.downstream_impacts[-4:]
    last_updated_turn: int = 0

    def to_dict(self) -> dict:
        return {
            "house_goal": self.house_goal,
            "problem_statement": self.problem_statement,
            "guidance_request": self.guidance_request,
            "choices": list(self.choices),
            "selected_choice": self.selected_choice,
            "influence_strength": round(self.influence_strength, 3),
            "downstream_impacts": list(self.downstream_impacts),
            "dream_insight": self.dream_insight,
            "aspiration": self.aspiration,
            "last_updated_turn": self.last_updated_turn,
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
class GovernanceState:
    term_length_days: int = 14
    max_consecutive_terms: int = 2
    cooldown_terms_after_limit: int = 2
    current_term_number: int = 1
    current_term_started_day: int = 1
    next_scheduled_election_day: int = 15
    consecutive_terms_served: Dict[str, int] = field(default_factory=dict)
    cooldown_remaining: Dict[str, int] = field(default_factory=dict)
    crisis_override_active: bool = False
    crisis_election_does_not_increment_term_count: bool = True
    needs_vector: Dict[str, float] = field(default_factory=dict)
    legitimacy_score: float = 0.7
    legitimacy_threshold: float = 0.45
    mission_alignment_score: float = 0.7
    active_dispute: bool = False
    pending_revalidation: bool = False
    last_election_day: int = 1
    last_election_kind: str = "scheduled"

    def to_dict(self) -> dict:
        return {
            "term_length_days": self.term_length_days,
            "max_consecutive_terms": self.max_consecutive_terms,
            "cooldown_terms_after_limit": self.cooldown_terms_after_limit,
            "current_term_number": self.current_term_number,
            "current_term_started_day": self.current_term_started_day,
            "next_scheduled_election_day": self.next_scheduled_election_day,
            "consecutive_terms_served": dict(self.consecutive_terms_served),
            "cooldown_remaining": dict(self.cooldown_remaining),
            "crisis_override_active": self.crisis_override_active,
            "crisis_election_does_not_increment_term_count": self.crisis_election_does_not_increment_term_count,
            "needs_vector": {key: round(value, 3) for key, value in self.needs_vector.items()},
            "legitimacy_score": round(self.legitimacy_score, 3),
            "legitimacy_threshold": round(self.legitimacy_threshold, 3),
            "mission_alignment_score": round(self.mission_alignment_score, 3),
            "active_dispute": self.active_dispute,
            "pending_revalidation": self.pending_revalidation,
            "last_election_day": self.last_election_day,
            "last_election_kind": self.last_election_kind,
        }


@dataclass
class InternalState:
    session_id: str
    turn_index: int = 0
    current_day: int = 1
    current_hour: int = 8
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
    aura_forecast: str | None = None
    aura_arc_theme: str | None = None
    aura_tension: float | None = None
    aura_last_synthesis: str | None = None
    aura_arc_stage: int = 0
    aura_dream_history: List[str] = field(default_factory=list)
    evolution_mode: str = "homeostasis"
    executive_function: str = "Tomas"
    registered_event_types: List[str] = field(default_factory=list)
    event_backlog: List[dict] = field(default_factory=list)
    mode_history: List[str] = field(default_factory=list)
    evolution_meta: Dict[str, object] = field(default_factory=dict)
    governance: GovernanceState = field(default_factory=GovernanceState)
    telemetry: Dict[str, object] = field(default_factory=dict)
    environment: EnvironmentState = field(default_factory=EnvironmentState)

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "turn_index": self.turn_index,
            "current_day": self.current_day,
            "current_hour": self.current_hour,
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
            "aura_forecast": self.aura_forecast,
            "aura_arc_theme": self.aura_arc_theme,
            "aura_tension": round(self.aura_tension, 3) if isinstance(self.aura_tension, (int, float)) else None,
            "aura_last_synthesis": self.aura_last_synthesis,
            "aura_arc_stage": self.aura_arc_stage,
            "aura_dream_history": list(self.aura_dream_history),
            "evolution_mode": self.evolution_mode,
            "executive_function": self.executive_function,
            "registered_event_types": list(self.registered_event_types),
            "event_backlog": list(self.event_backlog),
            "mode_history": list(self.mode_history),
            "evolution_meta": dict(self.evolution_meta),
            "governance": self.governance.to_dict(),
            "telemetry": dict(self.telemetry),
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
        governance_data = data.get("governance", {})
        governance = GovernanceState(
            term_length_days=int(governance_data.get("term_length_days", 14) or 14),
            max_consecutive_terms=int(governance_data.get("max_consecutive_terms", 2) or 2),
            cooldown_terms_after_limit=int(governance_data.get("cooldown_terms_after_limit", 2) or 2),
            current_term_number=int(governance_data.get("current_term_number", 1) or 1),
            current_term_started_day=int(governance_data.get("current_term_started_day", 1) or 1),
            next_scheduled_election_day=int(governance_data.get("next_scheduled_election_day", 15) or 15),
            consecutive_terms_served={
                str(key): int(value)
                for key, value in (governance_data.get("consecutive_terms_served") or {}).items()
            },
            cooldown_remaining={
                str(key): int(value)
                for key, value in (governance_data.get("cooldown_remaining") or {}).items()
            },
            crisis_override_active=bool(governance_data.get("crisis_override_active", False)),
            crisis_election_does_not_increment_term_count=bool(
                governance_data.get("crisis_election_does_not_increment_term_count", True)
            ),
            needs_vector={
                str(key): float(value)
                for key, value in (governance_data.get("needs_vector") or {}).items()
            },
            legitimacy_score=float(governance_data.get("legitimacy_score", 0.7)),
            legitimacy_threshold=float(governance_data.get("legitimacy_threshold", 0.45)),
            mission_alignment_score=float(governance_data.get("mission_alignment_score", 0.7)),
            active_dispute=bool(governance_data.get("active_dispute", False)),
            pending_revalidation=bool(governance_data.get("pending_revalidation", False)),
            last_election_day=int(governance_data.get("last_election_day", 1) or 1),
            last_election_kind=str(governance_data.get("last_election_kind", "scheduled") or "scheduled"),
        )
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
                dream_state=value.get("dream_state", {}),
                dream_log=value.get("dream_log", []),
                house_brief=HouseBrief(
                    house_goal=(value.get("house_brief") or {}).get(
                        "house_goal", "Maintain steady contribution to village cohesion."
                    ),
                    problem_statement=(value.get("house_brief") or {}).get(
                        "problem_statement", "No active blocker is currently flagged."
                    ),
                    guidance_request=(value.get("house_brief") or {}).get(
                        "guidance_request", "Select a guidance style for today's work."
                    ),
                    choices=(value.get("house_brief") or {}).get("choices", [
                        "Take a conservative step to preserve stability.",
                        "Try a moderate experiment to gather new signal.",
                        "Coordinate with another house before acting.",
                        "Invest in long-term structure over short-term speed.",
                    ]),
                    selected_choice=(value.get("house_brief") or {}).get("selected_choice"),
                    influence_strength=(value.get("house_brief") or {}).get("influence_strength", 0.2),
                    downstream_impacts=(value.get("house_brief") or {}).get("downstream_impacts", []),
                    dream_insight=(value.get("house_brief") or {}).get("dream_insight"),
                    aspiration=(value.get("house_brief") or {}).get("aspiration"),
                    last_updated_turn=(value.get("house_brief") or {}).get("last_updated_turn", 0),
                ),
            )
            for key, value in data.get("villager_states", {}).items()
        }
        return cls(
            session_id=data.get("session_id", defaults.session_id),
            turn_index=data.get("turn_index", defaults.turn_index),
            current_day=data.get("current_day", defaults.current_day),
            current_hour=data.get("current_hour", defaults.current_hour),
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
            aura_forecast=data.get("aura_forecast"),
            aura_arc_theme=data.get("aura_arc_theme"),
            aura_tension=data.get("aura_tension"),
            aura_last_synthesis=data.get("aura_last_synthesis"),
            aura_arc_stage=data.get("aura_arc_stage", 0),
            aura_dream_history=data.get("aura_dream_history", []),
            evolution_mode=data.get("evolution_mode", "homeostasis"),
            executive_function=data.get("executive_function", "Tomas"),
            registered_event_types=data.get("registered_event_types", []),
            event_backlog=data.get("event_backlog", []),
            mode_history=data.get("mode_history", []),
            evolution_meta=data.get("evolution_meta", {}),
            governance=governance,
            telemetry=data.get("telemetry", {}),
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