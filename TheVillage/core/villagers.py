"""Village-style subsystem abstractions for TheVillage."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List

from TheVillage.core.models import EnvironmentState, Goal, HouseBrief, InternalState, Task, VillagerState, clamp_01


ROLE_SYMBOLS = {
    "tomas": {
        "objects": ["maps", "clocks", "corridors", "bridges", "compasses", "lanterns", "unfinished blueprints", "forking paths"],
        "actions": ["split", "loop", "rearrange", "collapse", "stretch", "flicker", "echo", "tilt"],
        "settings": ["a branching hallway", "a shifting grid", "a foggy crossroads", "a half-built tower", "a room full of ticking clocks"],
    },
    "mira": {
        "objects": ["keys", "doors", "glyphs", "books", "rivers", "whispering symbols", "shifting alphabets", "glowing insects"],
        "actions": ["unfold", "glow", "scatter", "whisper", "reveal", "multiply", "drift"],
        "settings": ["a library of shifting symbols", "a river of questions", "a room where words rearrange themselves"],
    },
    "edda": {
        "objects": ["mirrors", "knots", "cracked pottery", "woven threads", "fractured tiles", "frozen storms"],
        "actions": ["fracture", "merge", "tighten", "freeze", "repair", "vibrate"],
        "settings": ["a silent workshop", "a room of suspended shards", "a hall of mirrored contradictions"],
    },
    "lio": {
        "objects": ["ink", "scrolls", "shadows", "echoes", "unfinished chapters", "looping voices"],
        "actions": ["narrate", "loop", "fade", "rewrite", "echo", "unravel"],
        "settings": ["an endless stage", "a corridor of voices", "a theater with no actors"],
    },
    "sable": {
        "objects": ["towers", "foundations", "fractals", "pillars", "ruins", "blueprints"],
        "actions": ["grow", "tilt", "collapse", "rebuild", "spiral"],
        "settings": ["a shifting blueprint", "a half-built structure", "a field of rising pillars"],
    },
    "jun": {
        "objects": ["gardens", "breath", "warm light", "water", "roots", "flickering embers"],
        "actions": ["bloom", "wilt", "pulse", "flow", "brighten", "dim"],
        "settings": ["a quiet grove", "a room filled with warm air", "a garden that grows and dies in seconds"],
    },
}

ARC_THEMES = ["growth", "fracture", "search", "alignment", "warning"]

ROLE_SUBCONSCIOUS = {
    "tomas": {
        "fears": ["losing the map", "timelines collapsing", "directionless loops"],
        "desires": ["clean structure", "clear sequence", "durable coordination"],
    },
    "mira": {
        "fears": ["sealed knowledge", "silent symbols", "curiosity collapse"],
        "desires": ["discovery", "living language", "unexpected insight"],
    },
    "edda": {
        "fears": ["hidden fractures", "unseen contradictions", "repair paralysis"],
        "desires": ["coherence", "stable joins", "calm integrity"],
    },
    "lio": {
        "fears": ["story rupture", "forgotten chapters", "meaning drift"],
        "desires": ["continuity", "shared narrative", "voice alignment"],
    },
    "sable": {
        "fears": ["foundation failure", "structural drift", "premature scaling"],
        "desires": ["sound architecture", "long-horizon growth", "resilient design"],
    },
    "jun": {
        "fears": ["resource depletion", "care exhaustion", "quiet burnout"],
        "desires": ["resilience", "restorative rhythm", "steady warmth"],
    },
}

AURA_SYMBOLS = {
    "objects": [
        "veils", "lanterns", "spirals", "wells",
        "constellations", "threads of light", "mirrored water", "drifting embers",
    ],
    "actions": [
        "shimmer", "converge", "dissolve", "echo",
        "braid", "pulse", "darken", "reveal",
    ],
    "settings": [
        "a quiet pool beneath a starless sky",
        "a circle of stones humming softly",
        "a lantern-lit observatory",
        "a wind-carved shrine at the village edge",
        "a field of drifting embers",
        "a still well reflecting no sky",
    ],
}


class Aura:
    def __init__(self, village_state: InternalState):
        self.role = "aura"
        self.village_state = village_state
        self.dream_history: List[str] = list(village_state.aura_dream_history)
        self.arc_stage = int(village_state.aura_arc_stage)
        self.arc_theme = village_state.aura_arc_theme or "neutral"
        self.tension_level = float(village_state.aura_tension or 0.0)
        self.last_forecast = village_state.aura_forecast
        self.last_synthesis = village_state.aura_last_synthesis

    def _summarize_motifs(self, text: str) -> str:
        motifs = []
        for word in ["loop", "split", "glow", "fracture", "repair", "grow", "wilt", "shadow", "voice"]:
            if word in text:
                motifs.append(word)
        if not motifs:
            return "quiet, unspoken themes"
        return ", ".join(sorted(set(motifs)))

    def _sync_to_state(self) -> None:
        self.village_state.aura_forecast = self.last_forecast
        self.village_state.aura_arc_theme = self.arc_theme
        self.village_state.aura_tension = round(self.tension_level, 3)
        self.village_state.aura_last_synthesis = self.last_synthesis
        self.village_state.aura_arc_stage = self.arc_stage
        self.village_state.aura_dream_history = self.dream_history[-30:]

    def synthesize_dreams(self, villager_dreams: dict) -> str:
        all_text = " ".join(villager_dreams.values()).lower()
        obj = random.choice(AURA_SYMBOLS["objects"])
        act = random.choice(AURA_SYMBOLS["actions"])
        setting = random.choice(AURA_SYMBOLS["settings"])

        stress = self.village_state.bodily_state.get("tension", 0.0)
        cohesion = self.village_state.environment.coherence
        health = self.village_state.health_metrics.global_health
        tone = "steady"
        if stress > 0.4:
            tone = "strained"
        if cohesion < 0.5:
            tone = "fragmented"
        if health < 0.5:
            tone = "faint"

        synthesis = (
            f"In {setting}, {obj} begin to {act} around the village's reflection. "
            f"The psyche feels {tone}, carrying traces of {self._summarize_motifs(all_text)}."
        )

        self.last_synthesis = synthesis
        self.dream_history.append(synthesis)
        self.dream_history = self.dream_history[-30:]
        self._sync_to_state()
        return synthesis

    def update_arc_and_tension(self) -> None:
        stress = self.village_state.bodily_state.get("tension", 0.0)
        contradictions = max(
            self.village_state.health_metrics.contradiction_count,
            len(self.village_state.unresolved_tensions),
        )
        health = self.village_state.health_metrics.global_health

        delta = 0.0
        delta += stress * 0.2
        delta += contradictions * 0.3
        if health < 0.6:
            delta += 0.1
        delta -= 0.05
        self.tension_level = max(0.0, min(1.0, self.tension_level + delta))

        if self.arc_theme == "neutral":
            if self.tension_level > 0.7:
                self.arc_theme = "warning"
            elif self.tension_level > 0.4:
                self.arc_theme = "search"
            else:
                self.arc_theme = "integration"

        self.arc_stage += 1
        if self.arc_stage > 6:
            self.arc_stage = 0
            if self.tension_level > 0.7:
                self.arc_theme = "warning"
            elif self.tension_level > 0.4:
                self.arc_theme = "search"
            else:
                self.arc_theme = "integration"
        self._sync_to_state()

    def generate_forecast(self) -> str:
        t = self.tension_level
        theme = self.arc_theme

        if theme == "warning":
            if t > 0.8:
                msg = "The psyche stands at a fragile edge; today calls for protection and consolidation."
            else:
                msg = "Subtle fractures are forming beneath the surface; gentle stabilization will matter."
        elif theme == "search":
            msg = "Curiosity stirs beneath the surface; exploration will be fruitful if anchored in coherence."
        elif theme == "integration":
            msg = "The inner voices are converging; today is well-suited for weaving threads into a clearer whole."
        else:
            msg = "The subconscious is quiet but watchful; small shifts may reveal new directions."

        if self.last_synthesis:
            msg += f" Aura glimpses: {self.last_synthesis}"

        self.last_forecast = msg
        self._sync_to_state()
        return msg


def _default_house_brief(name: str, role: str) -> HouseBrief:
    role_key = role.lower()
    house_goal = "Maintain steady contribution to village cohesion."
    problem = "No active blocker is currently flagged."
    guidance = "Select a guidance style for today's work."

    if "planner" in role_key:
        house_goal = "Convert mission pressure into concrete next-step plans."
        problem = "The day has multiple competing priorities and limited task slots."
        guidance = "How should planning trade off certainty versus exploration today?"
    elif "curiosity" in role_key:
        house_goal = "Expand the shared lexicon and reduce conceptual blind spots."
        problem = "Unknown terms are appearing faster than they can be integrated."
        guidance = "What learning posture should guide term discovery today?"
    elif "stability" in role_key:
        house_goal = "Reduce contradictions and preserve structural coherence."
        problem = "Small inconsistencies are accumulating across subsystem signals."
        guidance = "Which repair stance should stability apply first?"
    elif "narrator" in role_key:
        house_goal = "Preserve continuity and make internal events legible."
        problem = "Recent events are fragmented and missing connective tissue."
        guidance = "What story strategy should organize today's events?"
    elif "architect" in role_key:
        house_goal = "Tune system design so long-term cohesion improves over time."
        problem = "Current structures may overfit to short-term reward."
        guidance = "Which design bias should architecture favor today?"
    elif "caretaker" in role_key:
        house_goal = "Protect village resilience and keep recovery pathways available."
        problem = "Stress pockets can build before they become visible globally."
        guidance = "What care strategy should shape today's interventions?"

    return HouseBrief(
        house_goal=house_goal,
        problem_statement=problem,
        guidance_request=guidance,
        choices=[
            "Prioritize low-risk stabilization.",
            "Run a bounded experiment to gather new signal.",
            "Coordinate with one neighboring house before acting.",
            "Favor long-term coherence over immediate reward.",
        ],
        selected_choice=None,
        influence_strength=0.2,
        downstream_impacts=[],
        last_updated_turn=0,
    )


def _ensure_villager_state(state: InternalState, name: str, role: str, skills: List[str]) -> VillagerState:
    villager = state.villager_states.get(name)
    if villager is None:
        villager = VillagerState(name=name, role=role, skills=list(skills), house_brief=_default_house_brief(name, role))
        state.villager_states[name] = villager
    else:
        villager.role = role
        villager.skills = list(skills)
        if not villager.house_brief.house_goal:
            villager.house_brief = _default_house_brief(name, role)
    return villager


@dataclass
class Villager:
    name: str
    role: str
    skills: List[str] = field(default_factory=list)
    mood: str = "steady"
    memory_refs: List[str] = field(default_factory=list)
    dream_arc_stage: int = 0
    dream_arc_theme: str = "growth"
    hidden_fear: str = "uncertainty"
    hidden_desire: str = "coherence"
    unresolved_tension: float = 0.0

    def __post_init__(self) -> None:
        self.dream_arc_theme = random.choice(ARC_THEMES)
        subconscious = ROLE_SUBCONSCIOUS.get(self._symbol_key(), ROLE_SUBCONSCIOUS["tomas"])
        self.hidden_fear = random.choice(subconscious["fears"])
        self.hidden_desire = random.choice(subconscious["desires"])

    def ensure_state(self, state: InternalState) -> VillagerState:
        villager_state = _ensure_villager_state(state, self.name, self.role, self.skills)
        villager_state.mood = self.mood
        villager_state.memory_refs = list(self.memory_refs)
        self._sync_subconscious_from_state(villager_state)
        self._sync_subconscious_to_state(villager_state)
        return villager_state

    def _house_choices(self) -> List[str]:
        return [
            "Prioritize low-risk stabilization.",
            "Run a bounded experiment to gather new signal.",
            "Coordinate with one neighboring house before acting.",
            "Favor long-term coherence over immediate reward.",
        ]

    def _symbol_key(self) -> str:
        return self.name.lower()

    def _sync_subconscious_from_state(self, villager_state: VillagerState) -> None:
        arc_stage = villager_state.dream_state.get("dream_arc_stage")
        if isinstance(arc_stage, int):
            self.dream_arc_stage = max(0, arc_stage)

        arc_theme = villager_state.dream_state.get("dream_arc_theme")
        if isinstance(arc_theme, str) and arc_theme:
            self.dream_arc_theme = arc_theme

        hidden_fear = villager_state.dream_state.get("hidden_fear")
        if isinstance(hidden_fear, str) and hidden_fear:
            self.hidden_fear = hidden_fear

        hidden_desire = villager_state.dream_state.get("hidden_desire")
        if isinstance(hidden_desire, str) and hidden_desire:
            self.hidden_desire = hidden_desire

        unresolved_tension = villager_state.dream_state.get("unresolved_tension")
        if isinstance(unresolved_tension, (int, float)):
            self.unresolved_tension = clamp_01(float(unresolved_tension))

    def _sync_subconscious_to_state(self, villager_state: VillagerState) -> None:
        villager_state.dream_state["dream_arc_stage"] = int(self.dream_arc_stage)
        villager_state.dream_state["dream_arc_theme"] = self.dream_arc_theme
        villager_state.dream_state["hidden_fear"] = self.hidden_fear
        villager_state.dream_state["hidden_desire"] = self.hidden_desire
        villager_state.dream_state["unresolved_tension"] = round(self.unresolved_tension, 3)

    def advance_dream_arc(self) -> None:
        self.dream_arc_stage += 1
        if self.dream_arc_stage > 6:
            self.dream_arc_stage = 0
            self.dream_arc_theme = random.choice(ARC_THEMES)

    def update_subconscious_tension(self, global_state: InternalState) -> None:
        stress = clamp_01(global_state.bodily_state.get("tension", 0.2))
        contradictions = max(global_state.health_metrics.contradiction_count, len(global_state.unresolved_tensions))
        unmet_goals = sum(1 for goal in global_state.active_goals if goal.priority < 0.45)
        if global_state.subsystem_scores:
            score_values = list(global_state.subsystem_scores.values())
            cross_role_conflict = max(score_values) - min(score_values)
        else:
            cross_role_conflict = 0.0

        delta = stress * 0.1 + contradictions * 0.06 + unmet_goals * 0.03 + cross_role_conflict * 0.08
        if stress < 0.25 and contradictions == 0:
            delta -= 0.04

        self.unresolved_tension = clamp_01(self.unresolved_tension + delta)

    def _arc_stage_intensity(self) -> str:
        if self.dream_arc_stage < 2:
            return "softly"
        if self.dream_arc_stage < 4:
            return "restlessly"
        return "violently"

    def _theme_clause(self) -> str:
        if self.dream_arc_theme == "growth":
            return "toward something unfinished but promising"
        if self.dream_arc_theme == "fracture":
            return "as hidden seams threatened to break"
        if self.dream_arc_theme == "search":
            return "while an unseen answer stayed just out of reach"
        if self.dream_arc_theme == "alignment":
            return "until scattered pieces briefly matched"
        return "as a warning bell lingered behind every movement"

    def _tension_clause(self) -> str:
        if self.unresolved_tension > 0.7:
            return "The air felt urgent and unstable."
        if self.unresolved_tension < 0.3:
            return "The scene felt calm and nearly harmonious."
        return "The scene felt uneasy but navigable."

    def generate_symbolic_dream(self) -> str:
        vocab = ROLE_SYMBOLS.get(self._symbol_key(), ROLE_SYMBOLS["tomas"])
        obj = random.choice(vocab["objects"])
        act = random.choice(vocab["actions"])
        setting = random.choice(vocab["settings"])
        intensity = self._arc_stage_intensity()
        theme_clause = self._theme_clause()
        tension_clause = self._tension_clause()
        return f"In {setting}, a {obj} began to {act} {intensity} {theme_clause}. {tension_clause}"

    def interpret_dream(self, dream_text: str) -> str:
        return (
            f"{self.name} reads the dream as a signal to balance caution and momentum. "
            f"{self._subconscious_context_clause()}"
        )

    def _subconscious_context_clause(self) -> str:
        if self.unresolved_tension > 0.7:
            level = "high"
        elif self.unresolved_tension < 0.3:
            level = "low"
        else:
            level = "medium"
        return (
            f"Arc theme '{self.dream_arc_theme}', fear '{self.hidden_fear}', desire '{self.hidden_desire}', "
            f"tension {self.unresolved_tension:.2f} ({level})."
        )

    def dream_to_goal_shift(self, dream_text: str) -> dict:
        suggestions: List[str] = []
        priority_delta = 0.02
        tension_delta = -0.01
        curiosity_delta = 0.01
        structure_delta = 0.01
        stability_delta = 0.01
        cohesion_delta = 0.01
        long_horizon_bias = 0.01

        if self.dream_arc_theme == "fracture":
            suggestions.append("repair_coherence_seam")
            stability_delta += 0.04
            cohesion_delta += 0.04
            curiosity_delta -= 0.01
        elif self.dream_arc_theme == "growth":
            suggestions.append("expand_learning_frontier")
            curiosity_delta += 0.04
            long_horizon_bias += 0.03
        elif self.dream_arc_theme == "warning":
            suggestions.append("stabilize_critical_path")
            stability_delta += 0.05
            tension_delta -= 0.03
        elif self.dream_arc_theme == "search":
            suggestions.append("map_unknown_corridor")
            curiosity_delta += 0.03
            cohesion_delta += 0.02
        else:
            suggestions.append("align_cross_house_plans")
            structure_delta += 0.03
            cohesion_delta += 0.03

        if self.unresolved_tension > 0.7:
            suggestions.append(f"protect_{self._symbol_key()}_core")
            priority_delta += 0.03
            stability_delta += 0.04
            tension_delta -= 0.03
        elif self.unresolved_tension < 0.3:
            suggestions.append(f"pursue_long_horizon_{self._symbol_key()}")
            long_horizon_bias += 0.03
            curiosity_delta += 0.02

        return {
            "priority_delta": priority_delta,
            "new_goal_suggestions": suggestions,
            "tension_delta": tension_delta,
            "curiosity_delta": curiosity_delta,
            "structure_delta": structure_delta,
            "stability_delta": stability_delta,
            "cohesion_delta": cohesion_delta,
            "long_horizon_bias": long_horizon_bias,
        }

    def generate_aspiration(self, dream_text: str) -> str | None:
        return None

    def _apply_dream_brief_bias(self, villager_state: VillagerState, brief: HouseBrief) -> None:
        latest_dream = villager_state.dream_log[-1] if villager_state.dream_log else ""
        shift = self.dream_to_goal_shift(latest_dream) if latest_dream else {}
        dream_insight_value = villager_state.dream_state.get("dream_insight")
        stored_insight = dream_insight_value if isinstance(dream_insight_value, str) else None
        brief.dream_insight = stored_insight or (self.interpret_dream(latest_dream) if latest_dream else None)
        brief.aspiration = self.generate_aspiration(latest_dream) if latest_dream else None
        if shift and shift.get("new_goal_suggestions") and brief.choices:
            aspirational = f"Pilot aspiration: {shift['new_goal_suggestions'][0].replace('_', ' ')}."
            brief.choices[-1] = aspirational
        if brief.dream_insight and "Dream signal:" not in brief.problem_statement:
            brief.problem_statement = f"{brief.problem_statement} Dream signal: {brief.dream_insight}"
        if brief.dream_insight:
            brief.guidance_request = "Which option best honors the dream signal while preserving cohesion?"

    def refresh_house_brief(self, state: InternalState, environment: EnvironmentState) -> None:
        villager_state = self.ensure_state(state)
        brief = villager_state.house_brief
        brief.house_goal = "Maintain steady contribution to village cohesion."
        brief.problem_statement = "No active blocker is currently flagged."
        brief.guidance_request = "Select a guidance style for today's work."
        brief.choices = self._house_choices()
        brief.downstream_impacts = [
            "Slightly shifts local house priorities.",
            "Feeds into next cycle cohesion updates.",
        ]
        self._apply_dream_brief_bias(villager_state, brief)
        brief.last_updated_turn = state.turn_index

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

    def generate_dream(self, state: InternalState, environment: EnvironmentState) -> str:
        villager_state = self.ensure_state(state)
        self.update_subconscious_tension(state)
        arc_stage_used = self.dream_arc_stage
        dream_line = f"{self.name} dreamed: {self.generate_symbolic_dream()}"

        villager_state.dream_log.append(dream_line)
        villager_state.dream_log = villager_state.dream_log[-20:]
        villager_state.dream_state["last_dream_day"] = state.current_day
        villager_state.dream_state["last_dream_hour"] = state.current_hour
        villager_state.dream_state["dream_intensity"] = round(random.uniform(0.08, 0.22), 3)
        villager_state.dream_state["dream_arc_stage_used"] = arc_stage_used
        villager_state.dream_state["dream_arc_theme_used"] = self.dream_arc_theme

        state.emotional_state["curiosity"] = clamp_01(state.emotional_state.get("curiosity", 0.3) + 0.02)
        state.emotional_state["arousal"] = clamp_01(state.emotional_state.get("arousal", 0.2) - 0.01)
        state.self_model["coherence"] = clamp_01(state.self_model.get("coherence", 0.5) + 0.01)

        villager_state.reward_trend = max(-1.0, min(1.0, villager_state.reward_trend + random.uniform(-0.03, 0.04)))
        villager_state.mood = derive_mood(villager_state.reward_trend, state.health_metrics.global_health)
        self.advance_dream_arc()
        self._sync_subconscious_to_state(villager_state)
        return dream_line

    def apply_hourly_behavior(self, state: InternalState, environment: EnvironmentState) -> str:
        villager_state = self.ensure_state(state)
        drift = random.uniform(-0.02, 0.03)
        villager_state.reward_trend = max(-1.0, min(1.0, villager_state.reward_trend + drift))
        villager_state.mood = derive_mood(villager_state.reward_trend, state.health_metrics.global_health)
        return f"{self.name} adjusted pace for hour {state.current_hour} and now feels {villager_state.mood}."


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

    def refresh_house_brief(self, state: InternalState, environment: EnvironmentState) -> None:
        super().refresh_house_brief(state, environment)
        villager_state = state.villager_states[self.name]
        brief = villager_state.house_brief
        top_goal = state.active_goals[0].name.replace("_", " ") if state.active_goals else "main mission scaffolding"
        brief.house_goal = "Convert mission pressure into concrete next-step plans."
        brief.problem_statement = f"Planning load is split across '{top_goal}' and day-{state.current_day} execution limits."
        brief.guidance_request = "Which planning posture should shape today's queue?"
        brief.downstream_impacts = [
            "Backlog ordering changes for all houses.",
            "Affects coherence and goal progress rates.",
        ]
        self._apply_dream_brief_bias(villager_state, brief)

    def interpret_dream(self, dream_text: str) -> str:
        lowered = dream_text.lower()
        if "loop" in lowered or "split" in lowered:
            core = "Tomas saw planning confusion in repeating routes; simplify plan branches before scaling."
            return f"{core} {self._subconscious_context_clause()}"
        if "collapse" in lowered:
            core = "Tomas sensed brittle sequencing; reinforce one planning bridge before adding new work."
            return f"{core} {self._subconscious_context_clause()}"
        core = "Tomas found directional clarity in the symbols; keep one coherent plan corridor for the next cycle."
        return f"{core} {self._subconscious_context_clause()}"

    def dream_to_goal_shift(self, dream_text: str) -> dict:
        shift = super().dream_to_goal_shift(dream_text)
        shift["priority_delta"] = float(shift["priority_delta"]) + 0.02
        shift["structure_delta"] = float(shift["structure_delta"]) + 0.03
        shift["long_horizon_bias"] = float(shift["long_horizon_bias"]) + 0.02
        suggestions = list(shift.get("new_goal_suggestions", []))
        if "simplify_plan_path" not in suggestions:
            suggestions.append("simplify_plan_path")
        shift["new_goal_suggestions"] = suggestions
        return shift

    def generate_aspiration(self, dream_text: str) -> str | None:
        return "I want to simplify our long-term plan."


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

    def refresh_house_brief(self, state: InternalState, environment: EnvironmentState) -> None:
        super().refresh_house_brief(state, environment)
        villager_state = state.villager_states[self.name]
        brief = villager_state.house_brief
        term_count = len(state.vocabulary_questions)
        brief.house_goal = "Expand the lexicon and reduce conceptual blind spots."
        brief.problem_statement = f"There are {term_count} unresolved language gap(s) influencing interpretation quality."
        brief.guidance_request = "What learning posture should guide today's term work?"
        brief.downstream_impacts = [
            "Influences interpreter confidence and explorer subsystem strength.",
            "Can lower contradiction pressure in later cycles.",
        ]
        self._apply_dream_brief_bias(villager_state, brief)

    def interpret_dream(self, dream_text: str) -> str:
        lowered = dream_text.lower()
        if "glow" in lowered or "reveal" in lowered:
            core = "Mira read discovery signals in the dream; explore one unknown concept with focused curiosity."
            return f"{core} {self._subconscious_context_clause()}"
        if "scatter" in lowered:
            core = "Mira sensed attention drift; gather questions into one thread before broad exploration."
            return f"{core} {self._subconscious_context_clause()}"
        core = "Mira perceived quiet curiosity pressure; pursue a gentle conceptual discovery pass."
        return f"{core} {self._subconscious_context_clause()}"

    def dream_to_goal_shift(self, dream_text: str) -> dict:
        shift = super().dream_to_goal_shift(dream_text)
        shift["curiosity_delta"] = float(shift["curiosity_delta"]) + 0.03
        shift["structure_delta"] = float(shift["structure_delta"]) - 0.01
        suggestions = list(shift.get("new_goal_suggestions", []))
        if "probe_unresolved_concept" not in suggestions:
            suggestions.append("probe_unresolved_concept")
        shift["new_goal_suggestions"] = suggestions
        return shift

    def generate_aspiration(self, dream_text: str) -> str | None:
        return "I feel drawn to explore a new unknown concept."


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

    def refresh_house_brief(self, state: InternalState, environment: EnvironmentState) -> None:
        super().refresh_house_brief(state, environment)
        villager_state = state.villager_states[self.name]
        brief = villager_state.house_brief
        contradiction_count = state.health_metrics.contradiction_count
        brief.house_goal = "Reduce contradictions and preserve structural coherence."
        brief.problem_statement = (
            f"Stability sees {contradiction_count} contradiction marker(s) with coherence at {environment.coherence:.2f}."
        )
        brief.guidance_request = "Which repair stance should stability apply first?"
        brief.downstream_impacts = [
            "Directly affects global health and stalled-goal pressure.",
            "Changes perceived safety for caretaker behaviors.",
        ]
        self._apply_dream_brief_bias(villager_state, brief)

    def interpret_dream(self, dream_text: str) -> str:
        lowered = dream_text.lower()
        if "fracture" in lowered or "cracked" in lowered:
            core = "Edda saw coherence fracture signals; repair the primary contradiction before new expansion."
            return f"{core} {self._subconscious_context_clause()}"
        if "merge" in lowered or "repair" in lowered:
            core = "Edda read integration momentum; merge nearby tensions into one coherent thread."
            return f"{core} {self._subconscious_context_clause()}"
        core = "Edda sensed subtle instability; tighten coherence checks across the village core."
        return f"{core} {self._subconscious_context_clause()}"

    def dream_to_goal_shift(self, dream_text: str) -> dict:
        shift = super().dream_to_goal_shift(dream_text)
        shift["priority_delta"] = float(shift["priority_delta"]) + 0.03
        shift["stability_delta"] = float(shift["stability_delta"]) + 0.03
        shift["cohesion_delta"] = float(shift["cohesion_delta"]) + 0.02
        suggestions = list(shift.get("new_goal_suggestions", []))
        if "resolve_primary_contradiction" not in suggestions:
            suggestions.append("resolve_primary_contradiction")
        shift["new_goal_suggestions"] = suggestions
        return shift

    def generate_aspiration(self, dream_text: str) -> str | None:
        return "I want to unify two conflicting goals."


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

    def refresh_house_brief(self, state: InternalState, environment: EnvironmentState) -> None:
        super().refresh_house_brief(state, environment)
        villager_state = state.villager_states[self.name]
        brief = villager_state.house_brief
        brief.house_goal = "Preserve continuity and make village dynamics legible."
        brief.problem_statement = f"Narrative buffer has {len(state.narrative_log)} recent entries to weave into one coherent account."
        brief.guidance_request = "What storytelling lens should narrator use today?"
        brief.downstream_impacts = [
            "Improves explainability when users check each house.",
            "Stabilizes mission continuity across day/night transitions.",
        ]
        self._apply_dream_brief_bias(villager_state, brief)

    def interpret_dream(self, dream_text: str) -> str:
        lowered = dream_text.lower()
        if "fade" in lowered:
            core = "Lio detected narrative gaps where meaning is fading; restitch missing links in the story arc."
            return f"{core} {self._subconscious_context_clause()}"
        if "rewrite" in lowered or "loop" in lowered:
            core = "Lio noticed repetitive framing; rewrite one recurring chapter to improve alignment."
            return f"{core} {self._subconscious_context_clause()}"
        core = "Lio felt the story can align further; narrate one clear throughline across the houses."
        return f"{core} {self._subconscious_context_clause()}"

    def dream_to_goal_shift(self, dream_text: str) -> dict:
        shift = super().dream_to_goal_shift(dream_text)
        shift["cohesion_delta"] = float(shift["cohesion_delta"]) + 0.03
        shift["structure_delta"] = float(shift["structure_delta"]) + 0.02
        suggestions = list(shift.get("new_goal_suggestions", []))
        if "clarify_missing_story_link" not in suggestions:
            suggestions.append("clarify_missing_story_link")
        shift["new_goal_suggestions"] = suggestions
        return shift

    def generate_aspiration(self, dream_text: str) -> str | None:
        return "I want to clarify a missing part of our story."


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

    def refresh_house_brief(self, state: InternalState, environment: EnvironmentState) -> None:
        super().refresh_house_brief(state, environment)
        villager_state = state.villager_states[self.name]
        brief = villager_state.house_brief
        brief.house_goal = "Tune system structures for long-horizon cohesion."
        brief.problem_statement = (
            f"Architecture sees progress {state.health_metrics.goal_progress_rate:.2f} and health {state.health_metrics.global_health:.2f}; balance may be off."
        )
        brief.guidance_request = "Which design bias should architecture favor this cycle?"
        brief.downstream_impacts = [
            "Adjusts medium-term reward and planning tendencies.",
            "Can amplify or dampen subsystem disagreement.",
        ]
        self._apply_dream_brief_bias(villager_state, brief)

    def interpret_dream(self, dream_text: str) -> str:
        lowered = dream_text.lower()
        if "collapse" in lowered or "tilt" in lowered:
            core = "Sable saw structural weakness signals; reinforce a failing support before extending complexity."
            return f"{core} {self._subconscious_context_clause()}"
        if "rebuild" in lowered or "grow" in lowered:
            core = "Sable sensed latent potential; rebuild one foundation to support long-horizon growth."
            return f"{core} {self._subconscious_context_clause()}"
        core = "Sable read mixed architecture pressure; inspect core supports before new design moves."
        return f"{core} {self._subconscious_context_clause()}"

    def dream_to_goal_shift(self, dream_text: str) -> dict:
        shift = super().dream_to_goal_shift(dream_text)
        shift["priority_delta"] = float(shift["priority_delta"]) + 0.02
        shift["structure_delta"] = float(shift["structure_delta"]) + 0.03
        shift["long_horizon_bias"] = float(shift["long_horizon_bias"]) + 0.03
        suggestions = list(shift.get("new_goal_suggestions", []))
        if "reinforce_structural_support" not in suggestions:
            suggestions.append("reinforce_structural_support")
        shift["new_goal_suggestions"] = suggestions
        return shift

    def generate_aspiration(self, dream_text: str) -> str | None:
        return "I want to reinforce a structural weakness."


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

    def refresh_house_brief(self, state: InternalState, environment: EnvironmentState) -> None:
        super().refresh_house_brief(state, environment)
        villager_state = state.villager_states[self.name]
        brief = villager_state.house_brief
        brief.house_goal = "Protect resilience and maintain recovery capacity."
        brief.problem_statement = (
            f"Caretaker tracks tension {state.bodily_state.get('tension', 0.0):.2f} and safety {environment.safety:.2f}; stress pockets may form."
        )
        brief.guidance_request = "What care strategy should shape interventions today?"
        brief.downstream_impacts = [
            "Shifts mood drift and hourly stability.",
            "Constrains how aggressively other houses can explore.",
        ]
        self._apply_dream_brief_bias(villager_state, brief)

    def interpret_dream(self, dream_text: str) -> str:
        lowered = dream_text.lower()
        if "wilt" in lowered or "freeze" in lowered:
            core = "Jun sensed depletion in the dream; restore resilience reserves before stress rises."
            return f"{core} {self._subconscious_context_clause()}"
        if "bloom" in lowered or "flow" in lowered:
            core = "Jun read recovery momentum; protect restorative rhythms while energy is available."
            return f"{core} {self._subconscious_context_clause()}"
        core = "Jun noticed subtle strain markers; prioritize care routines that stabilize recovery capacity."
        return f"{core} {self._subconscious_context_clause()}"

    def dream_to_goal_shift(self, dream_text: str) -> dict:
        shift = super().dream_to_goal_shift(dream_text)
        shift["tension_delta"] = float(shift["tension_delta"]) - 0.03
        shift["stability_delta"] = float(shift["stability_delta"]) + 0.03
        suggestions = list(shift.get("new_goal_suggestions", []))
        if "restore_resilience_reserve" not in suggestions:
            suggestions.append("restore_resilience_reserve")
        shift["new_goal_suggestions"] = suggestions
        return shift

    def generate_aspiration(self, dream_text: str) -> str | None:
        return "I want to restore our resilience."


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