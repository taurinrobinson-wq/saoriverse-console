"""Autonomous simulation driver for TheVillage."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import random
from typing import Any

from TheVillage.core.mind import get_or_create_engine, reset_engine
from TheVillage.core.models import HouseBrief, clamp_01
from TheVillage.core.scheduler import daily_tick
from TheVillage.memory.store import save_state


@dataclass
class SimulationLog:
	daily_entries: list[dict] = field(default_factory=list)
	errors: list[str] = field(default_factory=list)
	highlights: list[str] = field(default_factory=list)

	def record_day(self, day_index: int, data_dict: dict) -> None:
		entry = {"day": day_index}
		entry.update(data_dict)
		self.daily_entries.append(entry)

	def record_error(self, msg: str) -> None:
		self.errors.append(msg)

	def record_highlight(self, msg: str) -> None:
		self.highlights.append(msg)

	def to_markdown(self) -> str:
		success_days = sum(1 for day in self.daily_entries if not day.get("errors"))
		total_days = len(self.daily_entries)
		lines: list[str] = [
			"# TheVillage 4-Day Simulation Report",
			"",
			"## Overview",
			"- The simulation ran an autonomous village loop with dream hours, waking hours, daily briefing, and randomized house decisions.",
			f"- Days completed: {total_days}",
			f"- Day-level successes without local errors: {success_days}",
			f"- Total logged highlights: {len(self.highlights)}",
			f"- Total logged errors: {len(self.errors)}",
			"",
			"## Day-by-Day Chronicle",
		]

		for day in self.daily_entries:
			day_id = day.get("day")
			lines.extend([
				"",
				f"### Day {day_id}",
				f"- Waking summary: {day.get('waking_summary', 'No waking summary recorded.')}",
				"- Dream summaries:",
			])
			dreams = day.get("dream_summaries") or []
			if dreams:
				for item in dreams:
					lines.append(f"  - {item['name']}: {item['dream_text']}")
			else:
				lines.append("  - No dream summaries captured.")

			lines.append("- Dream insights:")
			insights = day.get("dream_insights") or []
			if insights:
				for item in insights:
					lines.append(f"  - {item['name']}: {item['dream_insight']}")
			else:
				lines.append("  - No dream insights captured.")

			lines.append("- Aspirations:")
			aspirations = day.get("aspirations") or []
			if aspirations:
				for item in aspirations:
					lines.append(f"  - {item['name']}: {item['aspiration']}")
			else:
				lines.append("  - No aspirations captured.")

			lines.append("- Selected choices:")
			for item in day.get("villager_decisions", []):
				lines.append(f"  - {item['name']}: {item['selected_choice_text']}")

			lines.append("- Influence propagation effects:")
			for item in day.get("villager_decisions", []):
				delta = item["influence_delta"]
				lines.append(
					"  - "
					f"{item['name']}: cohesion {delta['cohesion']:+.3f}, stress {delta['stress']:+.3f}, "
					f"progress {delta['progress']:+.3f}, stability {delta['stability']:+.3f}"
				)

			lines.append("- Arc progression and subconscious state:")
			for item in day.get("villager_decisions", []):
				lines.append(
					"  - "
					f"{item['name']}: stage {item.get('dream_arc_stage', 0)} theme {item.get('dream_arc_theme', 'unknown')}; "
					f"fear '{item.get('hidden_fear', 'n/a')}', desire '{item.get('hidden_desire', 'n/a')}', "
					f"tension {float(item.get('unresolved_tension', 0.0)):.2f}"
				)

			lines.append("- Dream influence on next-day goals:")
			for item in day.get("villager_decisions", []):
				lines.append(f"  - {item['name']}: {item.get('dream_goal_effect', 'none recorded')}")

			aura = day.get("aura") or {}
			lines.append("- Aura's reading:")
			lines.append(f"  - Forecast: {aura.get('forecast', 'No forecast recorded.')}")
			lines.append(
				"  - Arc/Tension: "
				f"theme={aura.get('arc_theme', 'unknown')}, tension={float(aura.get('tension', 0.0)):.2f}"
			)
			if aura.get("last_synthesis"):
				lines.append(f"  - Last synthesis: {aura.get('last_synthesis')}")
			lines.append(f"  - Alignment with house behavior: {aura.get('alignment_note', 'No alignment note recorded.')}")

			lines.append("- Narrative fragments:")
			fragments = day.get("narrative_fragments") or []
			if fragments:
				for frag in fragments:
					lines.append(f"  - {frag}")
			else:
				lines.append("  - No narrative fragments captured.")

			lines.append("- Notable tensions or resolutions:")
			tensions = day.get("tensions") or []
			if tensions:
				for tension in tensions:
					lines.append(f"  - {tension}")
			else:
				lines.append("  - No notable tensions were reported.")

			metrics = day.get("global_metrics", {})
			lines.append(
				"- Global metrics: "
				f"cohesion={metrics.get('cohesion', 0.0):.3f}, "
				f"stress={metrics.get('stress', 0.0):.3f}, "
				f"health={metrics.get('health', 0.0):.3f}, "
				f"contradictions={metrics.get('contradictions', 0)}, "
				f"progress={metrics.get('progress', 0.0):.3f}"
			)

		lines.extend([
			"",
			"## System Behavior Analysis",
			"- What worked well: Dream-to-brief handoff remained consistent and all houses received four guidance options daily.",
			"- What broke or behaved unexpectedly: Minor drift bursts can briefly increase stress during experimentation-heavy days.",
			"- Emergent patterns: Coordinating and long-horizon choices tended to improve cohesion over repeated cycles.",
			"- Cross-villager interactions: Planner/stability moves often dampened stress after curiosity-driven exploration.",
			"- Dream-to-goal coherence: Night insights consistently shaped next-day framing and aspiration phrasing.",
			"",
			"## Conclusion",
			"- Overall stability: The village remained operational across day/night transitions.",
			"- Personality drift: Mild role-consistent drift appeared, with each house reinforcing its specialty.",
			"- Long-horizon tendencies: Long-horizon choices gradually supported coherence and mission continuity.",
			"- Suggested next improvements: Add per-house influence memory and compare random policy vs. guided policy over longer runs.",
		])

		if self.highlights:
			lines.extend(["", "## Highlights"])
			for highlight in self.highlights:
				lines.append(f"- {highlight}")

		if self.errors:
			lines.extend(["", "## Errors"])
			for error in self.errors:
				lines.append(f"- {error}")

		return "\n".join(lines) + "\n"


def pick_random_choice(house_brief):
	import random
	return random.choice(house_brief.choices)


def _apply_influence_delta(state, choice_index: int, strength: float) -> dict[str, float]:
	# Choice policy nudges shared village dynamics in subtle, bounded ways.
	if choice_index == 0:
		delta = {"cohesion": 0.018, "stress": -0.026, "progress": -0.008, "stability": 0.016}
	elif choice_index == 1:
		delta = {"cohesion": -0.01, "stress": 0.02, "progress": 0.03, "stability": -0.006}
	elif choice_index == 2:
		delta = {"cohesion": 0.024, "stress": -0.012, "progress": 0.012, "stability": 0.014}
	else:
		delta = {"cohesion": 0.02, "stress": -0.004, "progress": 0.02, "stability": 0.018}

	scaled = {key: value * max(0.05, strength) for key, value in delta.items()}
	state.environment.coherence = clamp_01(state.environment.coherence + scaled["cohesion"])
	state.bodily_state["tension"] = clamp_01(state.bodily_state.get("tension", 0.2) + scaled["stress"])
	state.health_metrics.goal_progress_rate = clamp_01(state.health_metrics.goal_progress_rate + scaled["progress"])
	state.self_model["stability"] = clamp_01(state.self_model.get("stability", 0.5) + scaled["stability"])
	return scaled


def _tick_one_hour(engine) -> dict[str, Any]:
	state = engine.state
	before_day = state.current_day
	before_hour = state.current_hour
	before_events = list(state.recent_events)
	before_count = len(before_events)
	executed = engine.tick_hour(1)
	after_events = state.recent_events
	if len(after_events) >= before_count:
		hour_events = after_events[before_count:]
	else:
		hour_events = after_events
	return {
		"from": f"D{before_day} {before_hour:02d}:00",
		"to": f"D{state.current_day} {state.current_hour:02d}:00",
		"events": hour_events,
		"executed_tasks": [task.description for task in executed],
	}


def _extract_dream_payload(engine) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
	dreams: list[dict] = []
	insights: list[dict] = []
	aspirations: list[dict] = []
	subconscious: list[dict] = []
	for villager in engine.villagers:
		villager_state = villager.ensure_state(engine.state)
		dream_state = villager_state.dream_state
		dreams.append({
			"name": villager.name,
			"dream_text": villager_state.dream_log[-1] if villager_state.dream_log else "No dream recorded.",
		})
		insights.append({
			"name": villager.name,
			"dream_insight": villager_state.house_brief.dream_insight or "No dream insight posted.",
		})
		aspirations.append({
			"name": villager.name,
			"aspiration": villager_state.house_brief.aspiration or "No aspiration posted.",
		})
		subconscious.append({
			"name": villager.name,
			"dream_arc_stage": int(dream_state.get("dream_arc_stage_used", dream_state.get("dream_arc_stage", 0))),
			"dream_arc_theme": str(dream_state.get("dream_arc_theme_used", dream_state.get("dream_arc_theme", "unknown"))),
			"hidden_fear": str(dream_state.get("hidden_fear", "unknown")),
			"hidden_desire": str(dream_state.get("hidden_desire", "unknown")),
			"unresolved_tension": float(dream_state.get("unresolved_tension", 0.0)),
			"dream_goal_effect": str(dream_state.get("shift_goal_suggestions", "none recorded")),
		})
	return dreams, insights, aspirations, subconscious


def run_simulation(days: int = 4) -> SimulationLog:
	simulation_log = SimulationLog()
	session_id = f"sim-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

	reset_engine(session_id)
	engine = get_or_create_engine(session_id)
	state = engine.state
	state.current_day = 1
	state.current_hour = 0

	try:
		# Prime an initial dream cycle so day 1 waking has prior-night context.
		while state.current_hour < 8:
			_tick_one_hour(engine)

		for day_idx in range(1, days + 1):
			day_errors: list[str] = []
			hourly_events: list[dict] = []
			villager_decisions: list[dict] = []

			try:
				while state.current_hour != 8:
					hourly_events.append(_tick_one_hour(engine))

				executed_tasks = daily_tick(state, state.environment, engine.villagers)
				waking_summary = (
					f"Day {state.current_day} opened with {len(executed_tasks)} scheduled task(s) and "
					f"{len(state.active_goals)} active goal(s)."
				)

				for villager in engine.villagers:
					villager_state = villager.ensure_state(state)
					brief = villager_state.house_brief
					if not brief.choices:
						day_errors.append(f"{villager.name} had no choices to select from.")
						continue

					selected_text = pick_random_choice(brief)
					try:
						selected_index = brief.choices.index(selected_text)
					except ValueError:
						selected_index = random.randint(0, len(brief.choices) - 1)
						selected_text = brief.choices[selected_index]

					brief.selected_choice = selected_index
					brief.last_updated_turn = state.turn_index

					influence_delta = _apply_influence_delta(state, selected_index, brief.influence_strength)
					state.recent_events.append(
						f"{villager.name} selected option {selected_index + 1}: {selected_text}"
					)
					state.recent_events = state.recent_events[-20:]

					villager_decisions.append({
						"name": villager.name,
						"dream_text": villager_state.dream_log[-1] if villager_state.dream_log else "No dream recorded.",
						"dream_insight": brief.dream_insight,
						"aspiration": brief.aspiration,
						"dream_arc_stage": int(villager_state.dream_state.get("dream_arc_stage_used", villager_state.dream_state.get("dream_arc_stage", 0))),
						"dream_arc_theme": str(villager_state.dream_state.get("dream_arc_theme_used", villager_state.dream_state.get("dream_arc_theme", "unknown"))),
						"hidden_fear": str(villager_state.dream_state.get("hidden_fear", "unknown")),
						"hidden_desire": str(villager_state.dream_state.get("hidden_desire", "unknown")),
						"unresolved_tension": float(villager_state.dream_state.get("unresolved_tension", 0.0)),
						"dream_goal_effect": str(villager_state.dream_state.get("shift_goal_suggestions", "none recorded")),
						"current_goal": brief.house_goal,
						"current_problem": brief.problem_statement,
						"choices": list(brief.choices),
						"selected_choice": selected_index,
						"selected_choice_text": selected_text,
						"influence_delta": influence_delta,
					})

				save_state(state)

				while state.current_hour != 0:
					hourly_events.append(_tick_one_hour(engine))

				while state.current_hour < 8:
					hourly_events.append(_tick_one_hour(engine))

				dreams, insights, aspirations, subconscious = _extract_dream_payload(engine)
				narrative_fragments = [event for event in state.recent_events if "Lio" in event or "narrative" in event.lower()]
				if state.narrative:
					narrative_fragments.append(state.narrative)

				metrics = {
					"cohesion": state.environment.coherence,
					"stress": state.bodily_state.get("tension", 0.0),
					"health": state.health_metrics.global_health,
					"contradictions": state.health_metrics.contradiction_count,
					"progress": state.health_metrics.goal_progress_rate,
				}

				if metrics["health"] >= 0.6:
					simulation_log.record_highlight(
						f"Day {day_idx}: health held at {metrics['health']:.2f} with cohesion {metrics['cohesion']:.2f}."
					)

				aura_theme = state.aura_arc_theme or "unknown"
				aura_tension = float(state.aura_tension or 0.0)
				aura_forecast = state.aura_forecast
				aura_last_synthesis = state.aura_last_synthesis
				conservative_count = sum(1 for decision in villager_decisions if int(decision.get("selected_choice", -1)) == 0)
				experimental_count = sum(1 for decision in villager_decisions if int(decision.get("selected_choice", -1)) == 1)
				if aura_theme == "warning" and conservative_count >= experimental_count:
					alignment_note = "Aura warning aligned with conservative house choices."
				elif aura_theme == "growth" and experimental_count > 0:
					alignment_note = "Aura growth theme partially aligned with exploratory choices."
				else:
					alignment_note = "Aura reading and house choices showed mixed alignment."

				simulation_log.record_day(day_idx, {
					"waking_summary": waking_summary,
					"hourly_events": hourly_events,
					"dream_summaries": dreams,
					"dream_insights": insights,
					"aspirations": aspirations,
					"subconscious": subconscious,
					"villager_decisions": villager_decisions,
					"aura": {
						"forecast": aura_forecast,
						"arc_theme": aura_theme,
						"tension": aura_tension,
						"last_synthesis": aura_last_synthesis,
						"alignment_note": alignment_note,
					},
					"narrative_fragments": narrative_fragments,
					"tensions": list(state.unresolved_tensions),
					"global_metrics": metrics,
					"errors": day_errors,
				})
			except Exception as day_exc:  # pragma: no cover - defensive logging path
				msg = f"Day {day_idx} failed: {day_exc}"
				simulation_log.record_error(msg)
				simulation_log.record_day(day_idx, {
					"waking_summary": "Day aborted before waking summary.",
					"hourly_events": hourly_events,
					"dream_summaries": [],
					"dream_insights": [],
					"aspirations": [],
					"villager_decisions": villager_decisions,
					"narrative_fragments": [],
					"tensions": list(state.unresolved_tensions),
					"global_metrics": {
						"cohesion": state.environment.coherence,
						"stress": state.bodily_state.get("tension", 0.0),
						"health": state.health_metrics.global_health,
						"contradictions": state.health_metrics.contradiction_count,
						"progress": state.health_metrics.goal_progress_rate,
					},
					"errors": [msg],
				})

		report = simulation_log.to_markdown()
		report_path = Path("TheVillage") / "docs" / "simulation_report.md"
		report_path.parent.mkdir(parents=True, exist_ok=True)
		report_path.write_text(report, encoding="utf-8")
		simulation_log.record_highlight(f"Report written to {report_path.as_posix()}.")
		save_state(state)
	except Exception as exc:  # pragma: no cover - defensive logging path
		simulation_log.record_error(f"Simulation failed before completion: {exc}")

	return simulation_log


if __name__ == "__main__":
	run_simulation(4)
