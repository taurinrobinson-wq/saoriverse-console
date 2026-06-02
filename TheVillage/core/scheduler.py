"""Daily scheduler for the village simulator layer."""

from __future__ import annotations

import random
from typing import List

from TheVillage.core.models import EnvironmentState, Goal, InternalState, Task, clamp_01
from TheVillage.core.villagers import Villager, record_villager_outcome
from TheVillage.learning.logging import append_feedback


def _rank_tasks(tasks: List[Task]) -> List[Task]:
    return sorted(tasks, key=lambda task: (task.priority * 0.7 + task.expected_reward * 0.3), reverse=True)


def _execute_task(task: Task, state: InternalState, environment: EnvironmentState) -> tuple[str, float]:
    description = task.description.lower()
    reward_delta = task.expected_reward
    if "definition" in description or "lexicon" in description or "survey recent language" in description:
        state.health_metrics.vocabulary_growth_rate = round(state.health_metrics.vocabulary_growth_rate + 0.1, 3)
        state.background_processes["lexicon_growth"] = clamp_01(state.background_processes.get("lexicon_growth", 0.0) + 0.12)
        outcome = "New language pathways were opened in the village library."
    elif "coherence" in description or "contradiction" in description or "repair" in description:
        state.health_metrics.contradiction_count = max(0, state.health_metrics.contradiction_count - 1)
        environment.coherence = clamp_01(environment.coherence + 0.08)
        state.background_processes["repair"] = clamp_01(state.background_processes.get("repair", 0.0) + 0.1)
        outcome = "The villagers patched a weak seam and steadied the town's shared map."
    elif "recovery" in description or "pause" in description:
        environment.safety = clamp_01(environment.safety + 0.08)
        state.bodily_state["tension"] = clamp_01(state.bodily_state.get("tension", 0.0) - 0.12)
        outcome = "The square quieted and the village recovered its breath."
    elif "goal" in description or "mission" in description:
        state.health_metrics.goal_progress_rate = round(min(1.0, state.health_metrics.goal_progress_rate + 0.12), 3)
        if not state.active_goals:
            state.active_goals.append(
                Goal(name="advance_main_mission", drive="mission", priority=0.8, created_turn=state.turn_index, last_updated_turn=state.turn_index)
            )
        outcome = "The work ahead became clearer and the village chose a firmer direction."
    elif "reward" in description or "structure" in description:
        state.self_model["coherence"] = clamp_01(state.self_model.get("coherence", 0.0) + 0.05)
        state.self_model["agency"] = clamp_01(state.self_model.get("agency", 0.0) + 0.04)
        outcome = "The workshop adjusted its tools and made the internal machinery easier to steer."
    else:
        environment.novelty = clamp_01(environment.novelty + 0.03)
        outcome = "A small piece of useful work was completed around the village."

    state.reward_signal = round(state.reward_signal + reward_delta, 3)
    task.status = "completed"
    return outcome, reward_delta


def _update_health_metrics(state: InternalState, executed_tasks: List[Task]) -> None:
    metrics = state.health_metrics
    metrics.stalled_goals = sum(1 for goal in state.active_goals if goal.priority < 0.4)
    metrics.goal_progress_rate = round(min(1.0, metrics.goal_progress_rate + len(executed_tasks) * 0.04), 3)
    metrics.contradiction_count = max(metrics.contradiction_count, len(state.unresolved_tensions))
    health = 0.55 + metrics.goal_progress_rate * 0.22 + metrics.vocabulary_growth_rate * 0.14
    health -= metrics.contradiction_count * 0.05
    health -= metrics.error_events * 0.06
    health -= metrics.stalled_goals * 0.04
    metrics.global_health = round(clamp_01(health), 3)


def _apply_dream_shift(state: InternalState, villager: Villager, dream_text: str, deltas: dict) -> None:
    villager_state = villager.ensure_state(state)
    priority_delta = float(deltas.get("priority_delta", 0.0))
    tension_delta = float(deltas.get("tension_delta", 0.0))
    curiosity_delta = float(deltas.get("curiosity_delta", 0.0))
    structure_delta = float(deltas.get("structure_delta", 0.0))
    stability_delta = float(deltas.get("stability_delta", 0.0))
    cohesion_delta = float(deltas.get("cohesion_delta", 0.0))
    horizon_delta = float(deltas.get("long_horizon_bias", 0.0))

    drive_bias = {
        "planner": "mission",
        "curiosity keeper": "meaning",
        "stability steward": "integration",
        "narrator": "mission",
        "architect": "grounding",
        "caretaker": "stability",
    }
    target_drive = drive_bias.get(villager.role, "mission")
    for goal in state.active_goals:
        if goal.drive == target_drive:
            goal.priority = clamp_01(goal.priority + priority_delta)
            goal.last_updated_turn = state.turn_index

    suggestions = [str(item) for item in deltas.get("new_goal_suggestions", [])]
    for suggestion in suggestions:
        existing = next((goal for goal in state.active_goals if goal.name == suggestion), None)
        if existing is None:
            state.active_goals.append(
                Goal(
                    name=suggestion,
                    drive=target_drive,
                    priority=clamp_01(0.5 + priority_delta),
                    created_turn=state.turn_index,
                    last_updated_turn=state.turn_index,
                )
            )
        else:
            existing.priority = clamp_01(existing.priority + priority_delta * 0.5)

    state.bodily_state["tension"] = clamp_01(state.bodily_state.get("tension", 0.2) + tension_delta)
    state.emotional_state["curiosity"] = clamp_01(state.emotional_state.get("curiosity", 0.3) + curiosity_delta)
    state.self_model["coherence"] = clamp_01(state.self_model.get("coherence", 0.5) + cohesion_delta + structure_delta * 0.5)
    state.self_model["stability"] = clamp_01(state.self_model.get("stability", 0.5) + stability_delta)
    state.self_model["agency"] = clamp_01(state.self_model.get("agency", 0.2) + horizon_delta * 0.4)

    villager_state.dream_state["shift_priority_delta"] = round(priority_delta, 3)
    villager_state.dream_state["shift_tension_delta"] = round(tension_delta, 3)
    villager_state.dream_state["shift_curiosity_delta"] = round(curiosity_delta, 3)
    villager_state.dream_state["shift_structure_delta"] = round(structure_delta, 3)
    villager_state.dream_state["shift_stability_delta"] = round(stability_delta, 3)
    villager_state.dream_state["shift_cohesion_delta"] = round(cohesion_delta, 3)
    villager_state.dream_state["shift_long_horizon_bias"] = round(horizon_delta, 3)
    villager_state.dream_state["shift_goal_suggestions"] = ",".join(suggestions)
    villager_state.dream_state["shift_arc_theme"] = getattr(villager, "dream_arc_theme", "unknown")
    villager_state.dream_state["shift_tension_level"] = round(float(getattr(villager, "unresolved_tension", 0.0)), 3)
    villager_state.dream_state["last_dream_text"] = dream_text


def daily_tick(state: InternalState, environment: EnvironmentState, villagers: List[Villager], max_tasks: int = 4, aura=None) -> List[Task]:
    proposed_tasks: List[Task] = []
    state.recent_events = state.recent_events[-12:]

    if aura is not None:
        forecast = aura.generate_forecast()
        state.recent_events.append(f"Aura forecast: {forecast}")
        state.recent_events = state.recent_events[-20:]

    for villager in villagers:
        villager.ensure_state(state)
        villager.refresh_house_brief(state, environment)
        proposals = villager.propose_tasks(state, environment)
        proposed_tasks.extend(proposals)

    ranked_tasks = _rank_tasks(proposed_tasks)
    state.task_backlog = ranked_tasks[:12]
    executed: List[Task] = []

    for task in ranked_tasks[:max_tasks]:
        try:
            outcome, reward_delta = _execute_task(task, state, environment)
        except Exception as exc:
            task.status = "failed"
            state.health_metrics.error_events += 1
            outcome = f"The task failed unexpectedly: {exc}"
            reward_delta = -0.08
        state.recent_events.append(outcome)
        executed.append(task)
        villager = next((item for item in villagers if item.name == task.proposed_by), None)
        if villager is not None:
            record_villager_outcome(state, villager, task.description, outcome, reward_delta)

    _update_health_metrics(state, executed)

    narrative_entry = (
        f"Day {state.current_day}: The village pursued {len(executed)} task(s) in service of '{state.main_mission.statement}'. "
        f"Health now rests at {state.health_metrics.global_health:.0%}."
    )
    state.narrative = narrative_entry
    state.narrative_log.append(narrative_entry)
    state.narrative_log = state.narrative_log[-30:]
    append_feedback({
        "session_id": state.session_id,
        "day": state.current_day,
        "executed_tasks": [task.to_dict() for task in executed],
        "health": state.health_metrics.to_dict(),
    })
    return executed


def process_hour(state: InternalState, environment: EnvironmentState, villagers: List[Villager], aura=None) -> List[str]:
    events: List[str] = []
    if state.current_hour < 8:
        villager_dreams = {}
        for villager in villagers:
            villager_state = villager.ensure_state(state)
            last_dream_day = int(villager_state.dream_state.get("last_dream_day", -1))
            if last_dream_day == state.current_day:
                continue
            dream_line = villager.generate_dream(state, environment)
            villager_dreams[villager.role] = dream_line
            insight = villager.interpret_dream(dream_line)
            villager_state.dream_state["dream_insight"] = insight
            shift = villager.dream_to_goal_shift(dream_line)
            _apply_dream_shift(state, villager, dream_line, shift)
            events.append(dream_line)
            events.append(f"{villager.name} interpreted the dream: {insight}")
        if aura is not None and villager_dreams:
            synthesis = aura.synthesize_dreams(villager_dreams)
            aura.update_arc_and_tension()
            events.append(f"Aura synthesized the dreams: {synthesis}")
        state.recent_events.extend(events)
        state.recent_events = state.recent_events[-20:]
        return events

    for villager in villagers:
        events.append(villager.apply_hourly_behavior(state, environment))

    state.bodily_state["energy"] = clamp_01(state.bodily_state.get("energy", 0.5) + random.uniform(-0.04, 0.03))
    state.bodily_state["tension"] = clamp_01(state.bodily_state.get("tension", 0.2) + random.uniform(-0.02, 0.02))

    if len(villagers) >= 2:
        speaker, listener = random.sample(villagers, 2)
        interaction = f"{speaker.name} checked in with {listener.name} to align priorities for hour {state.current_hour}."
        events.append(interaction)

    state.recent_events.extend(events)
    state.recent_events = state.recent_events[-20:]
    return events