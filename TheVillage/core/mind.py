"""TheVillage orchestration engine."""

from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Dict

from TheVillage.core.interpreter import interpret_text
from TheVillage.core.models import Goal, InteractionResult, InternalState, clamp_01
from TheVillage.core.scheduler import daily_tick, process_hour
from TheVillage.core.villagers import Aura, default_villagers
from TheVillage.evolution_engine import EvolutionEngine
from TheVillage.embodiment.environment import SimpleWorldEnvironment
from TheVillage.learning.logging import append_conversation
from TheVillage.learning.vocabulary import VocabularyLearner
from TheVillage.memory.capsule import MemoryCapsule
from TheVillage.memory.store import append_capsule, load_state, reset_session, save_state


class TheVillageEngine:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.vocabulary = VocabularyLearner()
        self.environment = SimpleWorldEnvironment()
        self.state = load_state(session_id)
        self.villagers = default_villagers()
        self.aura = Aura(self.state)
        self.evolution = EvolutionEngine()

    def refresh_state(self) -> InternalState:
        self.state = load_state(self.session_id)
        self.aura = Aura(self.state)
        self.evolution = EvolutionEngine()
        return self.state

    def set_evolution_mode(self, mode: str) -> str:
        normalized = self.evolution.normalize_mode(mode, self.state.evolution_mode)
        self.state.evolution_mode = normalized
        save_state(self.state)
        return normalized

    def is_dream_time(self) -> bool:
        return self.state.current_hour < 8

    def tick_hour(self, hours: int = 1) -> list:
        executed_tasks = []
        tick_count = max(1, int(hours))
        for _ in range(tick_count):
            previous_hour = self.state.current_hour
            self.state.current_hour = (self.state.current_hour + 1) % 24
            process_hour(self.state, self.state.environment, self.villagers, aura=self.aura)
            self._advance_crisis_arc()
            self.evolution.run_cycle(
                self.state,
                [villager.name for villager in self.villagers],
                mode=self.state.evolution_mode,
                aura=self.aura,
            )
            if previous_hour == 23 and self.state.current_hour == 0:
                if self.state.narrative_log:
                    self.state.current_day += 1
                executed = daily_tick(self.state, self.state.environment, self.villagers, aura=self.aura)
                executed_tasks.extend(executed)
        self._refresh_house_briefs()
        self.state.last_run = datetime.now(timezone.utc).isoformat()
        return executed_tasks

    def run_daily_cycle(self) -> list:
        self.refresh_state()
        hours_to_rollover = (24 - self.state.current_hour) % 24
        if hours_to_rollover == 0:
            hours_to_rollover = 24
        executed = self.tick_hour(hours_to_rollover)
        save_state(self.state)
        return executed

    @staticmethod
    def _extract_advance_hours(text: str, action: str | None) -> int:
        combined = f"{action or ''} {text}".lower()
        if "advance" not in combined or "hour" not in combined:
            return 0
        match = re.search(r"(\d+)\s*hour", combined)
        if match:
            return max(1, int(match.group(1)))
        return 1

    def _apply_crisis_signal(self, cleaned_text: str) -> bool:
        lowered = cleaned_text.lower()
        crisis_terms = ("crisis", "emergency", "ill", "sick", "collapsed", "unable")
        leadership_terms = ("leader", "leadership", "take over", "replace", "succession")
        is_crisis = any(term in lowered for term in crisis_terms)
        leadership_crisis = is_crisis and any(term in lowered for term in leadership_terms)
        if not leadership_crisis:
            return False

        # Ensure villager state is available for scoring and immediate role impact.
        for villager in self.villagers:
            villager.ensure_state(self.state)

        affected = None
        for villager in self.villagers:
            if villager.name.lower() in lowered:
                affected = villager.name
                break

        self.state.bodily_state["tension"] = clamp_01(self.state.bodily_state.get("tension", 0.2) + 0.34)
        self.state.environment.coherence = clamp_01(self.state.environment.coherence - 0.08)
        self.state.health_metrics.contradiction_count = max(2, self.state.health_metrics.contradiction_count)
        self.state.unresolved_tensions.append("Leadership continuity is threatened by a crisis signal.")
        self.state.unresolved_tensions = self.state.unresolved_tensions[-8:]

        active = {goal.name: goal for goal in self.state.active_goals if goal.status == "active"}
        active["stabilize_leadership_transition"] = Goal(
            name="stabilize_leadership_transition",
            drive="stability",
            priority=0.92,
            created_turn=self.state.turn_index,
            last_updated_turn=self.state.turn_index,
        )
        active["maintain_service_continuity"] = Goal(
            name="maintain_service_continuity",
            drive="mission",
            priority=0.86,
            created_turn=self.state.turn_index,
            last_updated_turn=self.state.turn_index,
        )
        self.state.active_goals = sorted(active.values(), key=lambda goal: goal.priority, reverse=True)[:8]

        if affected and affected in self.state.villager_states:
            self.state.villager_states[affected].reward_trend = max(-1.0, self.state.villager_states[affected].reward_trend - 0.45)
            self.state.villager_states[affected].mood = "worried"
        if "Edda" in self.state.villager_states:
            self.state.villager_states["Edda"].reward_trend = min(1.0, self.state.villager_states["Edda"].reward_trend + 0.25)

        self.state.evolution_mode = "elections"
        mode_result = self.evolution.run_cycle(
            self.state,
            [villager.name for villager in self.villagers],
            mode="elections",
            aura=self.aura,
        )

        elected = (mode_result.get("result") or {}).get("leader") or self.state.executive_function
        self.state.recent_events.append(
            f"Crisis protocol activated: governance shifted to elections mode and selected leader {elected}."
        )
        self.state.evolution_meta["active_crisis"] = "leadership"
        self.state.evolution_meta["crisis_turn_started"] = self.state.turn_index
        self.state.evolution_meta["affected_villager"] = affected or "Tomas"
        self.state.evolution_meta["interim_leader"] = elected
        self.state.evolution_meta["recovery_status"] = "acute"
        self.state.evolution_meta["leadership_dispute"] = False
        self.state.evolution_meta["dispute_resolved"] = False
        self.state.recent_events = self.state.recent_events[-20:]
        return True

    def _advance_crisis_arc(self) -> None:
        if str(self.state.evolution_meta.get("active_crisis") or "") != "leadership":
            return

        started_at = self.state.evolution_meta.get("crisis_turn_started", self.state.turn_index)
        if not isinstance(started_at, int):
            started_at = self.state.turn_index
        elapsed_turns = max(0, self.state.turn_index - started_at)

        affected = str(self.state.evolution_meta.get("affected_villager") or "Tomas")
        interim = str(self.state.evolution_meta.get("interim_leader") or self.state.executive_function or "Tomas")
        recovery = str(self.state.evolution_meta.get("recovery_status") or "acute")
        dispute = bool(self.state.evolution_meta.get("leadership_dispute"))
        resolved = bool(self.state.evolution_meta.get("dispute_resolved"))

        if elapsed_turns >= 1 and recovery == "acute":
            self.state.evolution_meta["recovery_status"] = "improving"
            self.state.recent_events.append(
                f"{affected} is stabilizing physically, but leadership confidence is still unsettled."
            )

        if elapsed_turns >= 2 and not dispute and interim == "Edda" and affected != interim:
            self.state.evolution_meta["leadership_dispute"] = True
            self.state.health_metrics.contradiction_count = max(2, self.state.health_metrics.contradiction_count)
            self.state.unresolved_tensions.append(
                f"Interpersonal strain rose as {affected} began recovering while {interim} resisted immediate handover."
            )
            active = {goal.name: goal for goal in self.state.active_goals if goal.status == "active"}
            active["negotiate_leadership_settlement"] = Goal(
                name="negotiate_leadership_settlement",
                drive="integration",
                priority=0.9,
                created_turn=self.state.turn_index,
                last_updated_turn=self.state.turn_index,
            )
            self.state.active_goals = sorted(active.values(), key=lambda goal: goal.priority, reverse=True)[:8]
            self.state.recent_events.append(
                "Leadership dispute surfaced: village initiated mediation planning between recovery and legitimacy needs."
            )

        if elapsed_turns >= 4 and dispute and not resolved:
            self.state.evolution_meta["dispute_resolved"] = True
            self.state.evolution_meta["active_crisis"] = ""
            self.state.evolution_meta["leadership_dispute"] = False
            self.state.recent_events.append(
                "Leadership settlement reached: interim mandate converted into a reviewed transition plan."
            )

        self.state.unresolved_tensions = self.state.unresolved_tensions[-8:]
        self.state.recent_events = self.state.recent_events[-20:]

    def _apply_leadership_dispute_signal(self, cleaned_text: str) -> bool:
        if str(self.state.evolution_meta.get("active_crisis") or "") != "leadership":
            return False

        lowered = cleaned_text.lower()
        dispute_markers = (
            "does not want to give up leadership",
            "doesn't want to give up leadership",
            "does not want to give up",
            "doesn't want to give up",
            "refuses to step back",
            "refuses to give up leadership",
            "refuses to hand over leadership",
            "does not want to relinquish leadership",
            "doesn't want to relinquish leadership",
            "wont step down",
            "won't step down",
            "power struggle",
            "leadership dispute",
        )
        election_doubt_markers = (
            "election raised doubts",
            "election results raised doubts",
            "results of the election",
            "raised doubts",
            "new leader",
            "more dynamic",
            "revalidate",
            "legitimacy",
        )
        candidate_pool = ("Tomas", "Edda", "Sable", "Lio", "Jun", "Mira")
        recovery_markers = ("recovering", "feels better", "getting better", "stabilizing")

        touched = False
        if any(marker in lowered for marker in recovery_markers):
            self.state.evolution_meta["recovery_status"] = "improving"
            touched = True

        if any(marker in lowered for marker in dispute_markers):
            if not bool(self.state.evolution_meta.get("leadership_dispute")):
                self.state.evolution_meta["leadership_dispute"] = True
                self.state.health_metrics.contradiction_count = max(2, self.state.health_metrics.contradiction_count)
                affected = str(self.state.evolution_meta.get("affected_villager") or "Tomas")
                interim = str(self.state.evolution_meta.get("interim_leader") or self.state.executive_function or "Tomas")
                disputing_actor = affected
                marker_index = -1
                for marker in dispute_markers:
                    idx = lowered.find(marker)
                    if idx != -1:
                        marker_index = idx
                        break
                if marker_index >= 0:
                    best_pos = -1
                    for candidate in candidate_pool:
                        pos = lowered.rfind(candidate.lower(), 0, marker_index)
                        if pos > best_pos:
                            best_pos = pos
                            disputing_actor = candidate
                else:
                    for candidate in candidate_pool:
                        if candidate.lower() in lowered:
                            disputing_actor = candidate
                            break
                self.state.evolution_meta["disputing_actor"] = disputing_actor
                self.state.unresolved_tensions.append(
                    f"Interpersonal strain rose as {disputing_actor} challenged {interim}'s interim authority."
                )
                active = {goal.name: goal for goal in self.state.active_goals if goal.status == "active"}
                active["negotiate_leadership_settlement"] = Goal(
                    name="negotiate_leadership_settlement",
                    drive="integration",
                    priority=0.9,
                    created_turn=self.state.turn_index,
                    last_updated_turn=self.state.turn_index,
                )
                self.state.active_goals = sorted(active.values(), key=lambda goal: goal.priority, reverse=True)[:8]
                self.state.recent_events.append(
                    "Leadership dispute escalated from live report: mediation track and legitimacy review were activated."
                )
            touched = True

        if any(marker in lowered for marker in election_doubt_markers):
            reviewed_candidates = [name for name in candidate_pool if name.lower() in lowered]
            if not reviewed_candidates:
                reviewed_candidates = ["Edda", "Sable", "Lio", "Jun", "Mira"]
            self.state.evolution_meta["leadership_revalidation"] = True
            self.state.evolution_meta["candidate_review_list"] = reviewed_candidates
            self.state.bodily_state["tension"] = clamp_01(self.state.bodily_state.get("tension", 0.2) + 0.08)
            self.state.health_metrics.contradiction_count = max(2, self.state.health_metrics.contradiction_count)
            active = {goal.name: goal for goal in self.state.active_goals if goal.status == "active"}
            active["revalidate_leadership_mandate"] = Goal(
                name="revalidate_leadership_mandate",
                drive="integration",
                priority=0.91,
                created_turn=self.state.turn_index,
                last_updated_turn=self.state.turn_index,
            )
            active["compare_leadership_candidates"] = Goal(
                name="compare_leadership_candidates",
                drive="meaning",
                priority=0.84,
                created_turn=self.state.turn_index,
                last_updated_turn=self.state.turn_index,
            )
            self.state.active_goals = sorted(active.values(), key=lambda goal: goal.priority, reverse=True)[:8]
            self.state.recent_events.append(
                "Election legitimacy review opened: the village will compare leadership fitness against coherence and self-understanding goals."
            )
            touched = True

        if touched:
            self.state.unresolved_tensions = self.state.unresolved_tensions[-8:]
            self.state.recent_events = self.state.recent_events[-20:]
        return touched

    def _refresh_house_briefs(self) -> None:
        for villager in self.villagers:
            villager.refresh_house_brief(self.state, self.state.environment)

    def interact(self, text: str, action: str | None = None) -> InteractionResult:
        cleaned_text = " ".join(text.split())
        if len(cleaned_text) < 2:
            raise ValueError("Interaction text is required.")

        advanced_hours = self._extract_advance_hours(cleaned_text, action)
        if advanced_hours > 0:
            executed = self.tick_hour(advanced_hours)
            if executed:
                self.state.recent_events.append(
                    f"Hourly rollover triggered {len(executed)} scheduled task(s) for day {self.state.current_day}."
                )
                self.state.recent_events = self.state.recent_events[-20:]

        self.state.turn_index += 1
        interpretation = interpret_text(cleaned_text, self.vocabulary.known_terms())
        vocab_result = self.vocabulary.inspect_unknown_terms(self.session_id, interpretation.unknown_terms)
        env_feedback = self.environment.apply_action(self.state.environment, action or cleaned_text, cleaned_text)

        self._update_memory(cleaned_text, interpretation.features)
        self._apply_crisis_signal(cleaned_text)
        self._apply_leadership_dispute_signal(cleaned_text)
        self._advance_crisis_arc()
        self._update_emotions(interpretation.features, env_feedback)
        self._update_self_model(interpretation.features, vocab_result)
        self._update_subsystems(interpretation.features)
        self._update_goals(interpretation.features, env_feedback)
        self._update_reward(interpretation.features, env_feedback, vocab_result)
        self._update_narrative(interpretation.features, env_feedback, vocab_result)
        self._refresh_house_briefs()

        self.state.vocabulary_questions = vocab_result["questions"]
        self.state.known_terms = vocab_result["known_terms"]
        self.state.last_run = datetime.now(timezone.utc).isoformat()

        capsule = MemoryCapsule(
            symbolic_tags=self._memory_tags(interpretation.features),
            relational_phase=self.state.environment.scene,
            voltage_marking=f"reward:{self.state.reward_signal:+.2f}",
            user_input=cleaned_text,
            response_summary=self.state.narrative,
        )
        append_capsule(self.session_id, capsule)
        save_state(self.state)
        append_conversation({
            "session_id": self.session_id,
            "turn_index": self.state.turn_index,
            "text": cleaned_text,
            "action": action or "",
            "reward_signal": self.state.reward_signal,
            "unknown_terms": interpretation.unknown_terms,
        })

        return InteractionResult(
            session_id=self.session_id,
            turn_index=self.state.turn_index,
            text=cleaned_text,
            action=action or "",
            interpretation=interpretation,
            state=self.state,
            environment_feedback=env_feedback,
        )

    def _update_memory(self, text: str, features: Dict[str, float]) -> None:
        self.state.working_memory.append(text)
        self.state.working_memory = self.state.working_memory[-6:]
        salience = max(features.values()) if features else 0.0
        if salience > 0.2:
            self.state.long_term_memory.append(f"turn {self.state.turn_index}: {text[:160]}")
            self.state.long_term_memory = self.state.long_term_memory[-20:]
        self.state.recent_events.append(f"The village heard: {text[:120]}")
        self.state.recent_events = self.state.recent_events[-20:]

    def _update_emotions(self, features: Dict[str, float], env_feedback: dict) -> None:
        emotional = self.state.emotional_state
        bodily = self.state.bodily_state
        emotional["social_threat"] = clamp_01(emotional["social_threat"] * 0.7 + features.get("social_threat", 0.0) * 0.3)
        emotional["attachment_pressure"] = clamp_01(emotional["attachment_pressure"] * 0.72 + features.get("loss", 0.0) * 0.18 + features.get("self_blame", 0.0) * 0.1)
        emotional["curiosity"] = clamp_01(emotional["curiosity"] * 0.7 + features.get("curiosity", 0.0) * 0.2 + len(self.state.vocabulary_questions) * 0.05)
        emotional["care"] = clamp_01(emotional["care"] * 0.74 + features.get("care", 0.0) * 0.26)
        emotional["arousal"] = clamp_01(emotional["arousal"] * 0.7 + emotional["social_threat"] * 0.15 + env_feedback.get("novelty", 0.0) * 0.15)
        emotional["valence"] = clamp_01(emotional["valence"] * 0.8 + 0.5 + self.state.environment.safety * 0.08 - emotional["social_threat"] * 0.12)

        bodily["tension"] = clamp_01(bodily["tension"] * 0.74 + emotional["social_threat"] * 0.12 + features.get("identity_pressure", 0.0) * 0.14)
        bodily["energy"] = clamp_01(bodily["energy"] * 0.88 + 0.05 - bodily["tension"] * 0.04)
        bodily["safety"] = clamp_01(bodily["safety"] * 0.7 + env_feedback.get("safety", 0.0) * 0.3)
        bodily["activation"] = clamp_01(bodily["activation"] * 0.72 + emotional["arousal"] * 0.28)

    def _update_self_model(self, features: Dict[str, float], vocab_result: dict) -> None:
        self_model = self.state.self_model
        self_model["continuity"] = clamp_01(self_model["continuity"] * 0.82 + 0.18)
        self_model["agency"] = clamp_01(self_model["agency"] * 0.75 + len(self.state.active_goals) * 0.06 + self.state.environment.coherence * 0.08)
        self_model["coherence"] = clamp_01(self_model["coherence"] * 0.78 + self.state.environment.coherence * 0.12 + (1.0 - self.state.bodily_state["tension"]) * 0.1)
        self_model["stability"] = clamp_01(self_model["stability"] * 0.8 + self.state.environment.safety * 0.12 + self.state.bodily_state["safety"] * 0.08)
        self_model["curiosity"] = clamp_01(self_model["curiosity"] * 0.7 + features.get("curiosity", 0.0) * 0.15 + len(vocab_result.get("questions", [])) * 0.08)
        self.state.background_processes["lexicon_growth"] = clamp_01(
            self.state.background_processes["lexicon_growth"] * 0.8 + len(vocab_result.get("auto_definitions", {})) * 0.1
        )

    def _update_subsystems(self, features: Dict[str, float]) -> None:
        scores = {
            "impulse": clamp_01(features.get("social_threat", 0.0) * 0.5 + features.get("loss", 0.0) * 0.3),
            "planner": clamp_01(features.get("rational_control", 0.0) * 0.55 + self.state.self_model["coherence"] * 0.25),
            "critic": clamp_01(features.get("self_blame", 0.0) * 0.7 + features.get("identity_pressure", 0.0) * 0.3),
            "caretaker": clamp_01(features.get("care", 0.0) * 0.7 + self.state.emotional_state["care"] * 0.3),
            "explorer": clamp_01(features.get("curiosity", 0.0) * 0.45 + self.state.environment.novelty * 0.35 + self.state.self_model["curiosity"] * 0.2),
            "protector": clamp_01(self.state.bodily_state["tension"] * 0.5 + self.state.environment.safety * 0.15 + self.state.emotional_state["social_threat"] * 0.35),
        }
        self.state.subsystem_scores = scores
        spread = max(scores.values()) - min(scores.values())
        tension = sum(scores.values()) / len(scores)
        self.state.background_processes["rumination"] = clamp_01(self.state.background_processes["rumination"] * 0.7 + spread * 0.3)
        self.state.background_processes["monitoring"] = clamp_01(self.state.background_processes["monitoring"] * 0.8 + tension * 0.2)
        unresolved = []
        if spread > 0.25:
            unresolved.append("Subsystems disagree about the next best action.")
        if self.state.emotional_state["social_threat"] > 0.35:
            unresolved.append("The system is still tracking interpersonal threat.")
        if self.state.vocabulary_questions:
            unresolved.append("The system is missing definitions it wants to resolve.")
        self.state.unresolved_tensions = unresolved

    def _update_goals(self, features: Dict[str, float], env_feedback: dict) -> None:
        candidates = []
        if features.get("social_threat", 0.0) > 0.2:
            candidates.append(("restore_safety", "stability", 0.78))
        if features.get("care", 0.0) > 0.15:
            candidates.append(("maintain_connection", "care", 0.68))
        if features.get("curiosity", 0.0) > 0.1 or self.state.vocabulary_questions:
            candidates.append(("resolve_unknown_terms", "meaning", 0.72))
        if env_feedback.get("coherence", 0.0) < 0.7:
            candidates.append(("improve_world_model", "grounding", 0.64))
        if self.state.background_processes["rumination"] > 0.35:
            candidates.append(("reduce_internal_conflict", "integration", 0.7))

        active = {goal.name: goal for goal in self.state.active_goals if goal.status == "active"}
        for name, drive, priority in candidates:
            if name in active:
                active[name].priority = clamp_01(active[name].priority * 0.75 + priority * 0.25)
                active[name].last_updated_turn = self.state.turn_index
            else:
                active[name] = Goal(name=name, drive=drive, priority=priority, created_turn=self.state.turn_index, last_updated_turn=self.state.turn_index)
        for goal in active.values():
            if goal.name not in {candidate[0] for candidate in candidates}:
                goal.priority = clamp_01(goal.priority * 0.95)
        self.state.active_goals = sorted(active.values(), key=lambda goal: goal.priority, reverse=True)[:6]
        self.state.health_metrics.stalled_goals = sum(1 for goal in self.state.active_goals if goal.priority < 0.45)

    def _update_reward(self, features: Dict[str, float], env_feedback: dict, vocab_result: dict) -> None:
        reward = (
            env_feedback.get("reward_delta", 0.0)
            + self.state.environment.coherence * 0.12
            + len(vocab_result.get("auto_definitions", {})) * 0.08
            + features.get("care", 0.0) * 0.05
            - self.state.background_processes["rumination"] * 0.1
            - features.get("social_threat", 0.0) * 0.08
        )
        self.state.reward_signal = round(reward, 3)
        self.state.health_metrics.vocabulary_growth_rate = round(
            self.state.health_metrics.vocabulary_growth_rate * 0.85 + len(vocab_result.get("auto_definitions", {})) * 0.15,
            3,
        )
        self.state.health_metrics.goal_progress_rate = round(
            min(1.0, self.state.health_metrics.goal_progress_rate * 0.9 + len(self.state.active_goals) * 0.03),
            3,
        )
        self.state.health_metrics.contradiction_count = len(self.state.unresolved_tensions)
        health = 0.58 + self.state.health_metrics.goal_progress_rate * 0.18 + self.state.health_metrics.vocabulary_growth_rate * 0.12
        health -= self.state.health_metrics.contradiction_count * 0.06
        health -= self.state.health_metrics.stalled_goals * 0.04
        health -= self.state.health_metrics.error_events * 0.08
        self.state.health_metrics.global_health = round(clamp_01(health), 3)

    def _update_narrative(self, features: Dict[str, float], env_feedback: dict, vocab_result: dict) -> None:
        dominant_subsystem = max(self.state.subsystem_scores.items(), key=lambda item: item[1])[0]
        top_goal = self.state.active_goals[0].name if self.state.active_goals else "stabilize"
        parts = [
            f"The village is carrying continuity through turn {self.state.turn_index} at hour {self.state.current_hour:02d}.",
            f"The loudest voice in the square is {dominant_subsystem}, and the village is leaning toward {top_goal}.",
            f"Current executive function is led by {self.state.executive_function}.",
            f"The environment reports: {env_feedback.get('last_event', 'No event available.')}",
        ]
        if features.get("social_threat", 0.0) > 0.2:
            parts.append("The watch posts are still alert for threat or rejection.")
        if features.get("care", 0.0) > 0.15:
            parts.append("The caretaking houses are trying to preserve connection and care.")
        if vocab_result.get("questions"):
            asked_terms = ", ".join(question["term"] for question in vocab_result["questions"])
            parts.append(f"The village found terms it does not yet understand: {asked_terms}.")
        if vocab_result.get("auto_definitions"):
            learned_terms = ", ".join(sorted(vocab_result["auto_definitions"].keys()))
            parts.append(f"The library expanded with definitions for: {learned_terms}.")
        parts.append(f"The village's reward signal is {self.state.reward_signal:+.2f}.")
        self.state.narrative = " ".join(parts)
        self.state.narrative_log.append(self.state.narrative)
        self.state.narrative_log = self.state.narrative_log[-30:]

    @staticmethod
    def _memory_tags(features: Dict[str, float]) -> list[str]:
        return [name for name, value in features.items() if value > 0.15] or ["low_signal"]


_ENGINE_REGISTRY: Dict[str, TheVillageEngine] = {}


def get_or_create_engine(session_id: str = "default") -> TheVillageEngine:
    key = session_id.strip() or "default"
    if key not in _ENGINE_REGISTRY:
        _ENGINE_REGISTRY[key] = TheVillageEngine(key)
    return _ENGINE_REGISTRY[key]


def reset_engine(session_id: str = "default") -> None:
    key = session_id.strip() or "default"
    _ENGINE_REGISTRY.pop(key, None)
    reset_session(key)


def main() -> None:
    engine = get_or_create_engine("default")
    executed = engine.run_daily_cycle()
    print(f"day={engine.state.current_day} executed_tasks={len(executed)}")


if __name__ == "__main__":
    main()