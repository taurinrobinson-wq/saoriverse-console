"""Village-metaphor dialogue helpers."""

from __future__ import annotations

from typing import List


def villager_to_dialogue(villager_state: dict, recent_events: List[str]) -> str:
    name = villager_state.get("name", "A villager")
    role = villager_state.get("role", "worker")
    mood = villager_state.get("mood", "steady")
    tasks = villager_state.get("recent_tasks", [])
    outcomes = villager_state.get("recent_outcomes", [])
    last_task = tasks[-1] if tasks else "keeping an eye on the square"
    last_outcome = outcomes[-1] if outcomes else (recent_events[-1] if recent_events else "Nothing urgent has happened yet.")
    next_step = tasks[-2] if len(tasks) > 1 else "returning to the mission at sunrise"
    return (
        f"{name} the {role} seems {mood}. They spent their latest stretch {last_task}. "
        f"Afterward, they said: '{last_outcome}' Next they expect to be {next_step}."
    )


def village_summary_to_dialogue(global_state: dict, narrative: str) -> str:
    mission = global_state.get("main_mission", {}).get("statement", "keep the village moving")
    metrics = global_state.get("health_metrics", {})
    day = global_state.get("current_day", 1)
    health = metrics.get("global_health", 0.0)
    contradictions = metrics.get("contradiction_count", 0)
    stalled = metrics.get("stalled_goals", 0)
    mood = "calm" if health > 0.7 else "tense" if health < 0.45 else "busy"
    return (
        f"On day {day}, the village gathers around one shared purpose: {mission} The town feels {mood}. "
        f"There are {contradictions} open contradiction(s) and {stalled} stalled goal(s) drawing attention. "
        f"The latest word from the square is: {narrative or 'The villagers are preparing their next move.'}"
    )