import unittest

from TheVillage.core.mind import TheVillageEngine, get_or_create_engine, reset_engine
from TheVillage.core.models import EnvironmentState, Goal, InternalState, Task
from TheVillage.core.scheduler import process_hour
from TheVillage.core.scheduler import daily_tick
from TheVillage.core.villagers import Aura, CuriosityVillager, StabilityVillager, default_villagers
from TheVillage.interface.api import app, get_color_scheme
from TheVillage.interface.dialogue import village_summary_to_dialogue, villager_to_dialogue
from TheVillage.memory.store import save_state


class TestTheVillage(unittest.TestCase):
    def setUp(self):
        reset_engine("thevillage-test")

    def tearDown(self):
        reset_engine("thevillage-test")

    def test_persistent_state_across_turns(self):
        engine = get_or_create_engine("thevillage-test")
        first = engine.interact("I was rejected and want to understand what happened.", action="observe")
        second = engine.interact("Please define limerence for me.", action="ask")

        self.assertEqual(first.turn_index, 1)
        self.assertEqual(second.turn_index, 2)
        self.assertGreaterEqual(len(second.state.working_memory), 2)
        self.assertGreaterEqual(second.state.self_model["continuity"], first.state.self_model["continuity"])
        self.assertTrue(second.state.narrative)

    def test_unknown_terms_create_questions(self):
        engine = TheVillageEngine("thevillage-test")
        result = engine.interact("I feel quoralen and vesperline moving through this scene.", action="ask")

        self.assertGreaterEqual(len(result.state.vocabulary_questions), 1)
        self.assertIn("reason", result.state.vocabulary_questions[0])

    def test_teaching_a_term_updates_dictionary(self):
        engine = get_or_create_engine("thevillage-test")
        engine.vocabulary.learn_definition("sonder", "The realization that others have lives as vivid as your own.", source="user")
        result = engine.interact("sonder matters to how I understand others", action="define")

        self.assertIn("sonder", result.state.known_terms)
        self.assertGreater(result.state.reward_signal, -1.0)

    def test_leadership_crisis_changes_state_beyond_log(self):
        engine = get_or_create_engine("thevillage-test")
        result = engine.interact(
            "Tomas has fallen ill and needs someone to take over leadership.",
            action="observe",
        )

        goal_names = {goal.name for goal in result.state.active_goals}
        self.assertIn("stabilize_leadership_transition", goal_names)
        self.assertEqual(result.state.evolution_mode, "elections")
        self.assertTrue(any("Crisis protocol activated" in line for line in result.state.recent_events))
        self.assertIn(result.state.executive_function, {villager.name for villager in engine.villagers})

        tomas_brief = result.state.villager_states["Tomas"].house_brief
        self.assertIn("Recover capacity", tomas_brief.house_goal)
        self.assertTrue(
            "handoff" in tomas_brief.guidance_request.lower()
            or "authority" in tomas_brief.guidance_request.lower()
        )
        self.assertTrue(any("delegate mission-critical" in choice.lower() for choice in tomas_brief.choices))

        interim = result.state.executive_function
        interim_brief = result.state.villager_states[interim].house_brief
        self.assertTrue("interim" in interim_brief.house_goal.lower() or "lead" in interim_brief.house_goal.lower())

    def test_leadership_dispute_phrase_escalates_active_crisis(self):
        engine = get_or_create_engine("thevillage-test")
        engine.interact("Tomas has fallen ill and leadership must be transferred.", action="observe")
        result = engine.interact(
            "Tomas is recovering but does not want to give up leadership.",
            action="observe",
        )

        self.assertTrue(bool(result.state.evolution_meta.get("leadership_dispute")))
        self.assertIn("negotiate_leadership_settlement", {goal.name for goal in result.state.active_goals})
        self.assertTrue(any("dispute" in line.lower() for line in result.state.recent_events))

    def test_edda_refusal_and_election_doubt_trigger_revalidation(self):
        engine = get_or_create_engine("thevillage-test")
        engine.interact("Tomas has fallen ill and needs someone to take over leadership.", action="observe")
        result = engine.interact(
            (
                "Tomas is now recovering, but Edda does not want to give up leadership. "
                "The election results raised doubts that a more dynamic leader like Sable, Lio, Jun, or Mira might "
                "better help the village realize its goal."
            ),
            action="observe",
        )

        self.assertTrue(bool(result.state.evolution_meta.get("leadership_dispute")))
        self.assertEqual(result.state.evolution_meta.get("disputing_actor"), "Edda")
        self.assertTrue(bool(result.state.evolution_meta.get("leadership_revalidation")))
        self.assertIn("revalidate_leadership_mandate", {goal.name for goal in result.state.active_goals})
        self.assertIn("compare_leadership_candidates", {goal.name for goal in result.state.active_goals})
        review_data = result.state.evolution_meta.get("candidate_review_list")
        review_list = review_data if isinstance(review_data, list) else []
        self.assertTrue(all(name in review_list for name in ["Edda", "Sable", "Lio", "Jun", "Mira"]))
        self.assertTrue(any("legitimacy review" in line.lower() for line in result.state.recent_events))

    def test_daily_tick_executes_ranked_tasks(self):
        state = InternalState(session_id="thevillage-test")
        state.vocabulary_questions = [{"term": "quoralen", "question": "What does quoralen mean?", "reason": "unknown_term"}]
        state.unresolved_tensions = ["A contradiction is still open."]
        state.health_metrics.contradiction_count = 2
        villagers = default_villagers()

        executed = daily_tick(state, state.environment, villagers)

        self.assertGreaterEqual(len(executed), 1)
        self.assertTrue(state.narrative)
        self.assertGreaterEqual(state.health_metrics.global_health, 0.0)

    def test_villagers_propose_expected_tasks(self):
        state = InternalState(session_id="thevillage-test")
        state.vocabulary_questions = [{"term": "vesperline", "question": "What does vesperline mean?", "reason": "unknown_term"}]
        state.unresolved_tensions = ["Subsystems disagree"]
        state.health_metrics.contradiction_count = 2

        curiosity_tasks = CuriosityVillager().propose_tasks(state, state.environment)
        stability_tasks = StabilityVillager().propose_tasks(state, state.environment)

        self.assertTrue(any("definition" in task.description.lower() for task in curiosity_tasks))
        self.assertTrue(any("contradiction" in task.description.lower() for task in stability_tasks))

    def test_health_metrics_update_during_daily_tick(self):
        state = InternalState(session_id="thevillage-test")
        state.health_metrics.goal_progress_rate = 0.1
        state.health_metrics.global_health = 0.3
        state.unresolved_tensions = ["One tension", "Another tension"]

        daily_tick(state, EnvironmentState(), default_villagers())

        self.assertGreaterEqual(state.health_metrics.goal_progress_rate, 0.1)
        self.assertGreaterEqual(state.health_metrics.contradiction_count, 0)

    def test_dialogue_generation_handles_sparse_state(self):
        state = InternalState(session_id="thevillage-test")
        summary = village_summary_to_dialogue(state.to_dict(), state.narrative)
        villager_line = villager_to_dialogue({"name": "Tomas", "role": "planner", "mood": "steady"}, [])

        self.assertTrue(summary)
        self.assertTrue(villager_line)

    def test_daily_cycle_runs_once_per_day(self):
        engine = get_or_create_engine("thevillage-test")
        engine.state.last_run = "2000-01-01T00:00:00+00:00"
        save_state(engine.state)
        first = engine.run_daily_cycle()
        second = engine.run_daily_cycle()

        self.assertGreaterEqual(len(first), 1)
        self.assertGreaterEqual(len(second), 1)

    def test_clock_rollover(self):
        engine = get_or_create_engine("thevillage-test")
        engine.state.current_hour = 23
        engine.state.narrative_log = ["already ran one day"]

        executed = engine.tick_hour()

        self.assertEqual(engine.state.current_hour, 0)
        self.assertEqual(engine.state.current_day, 2)
        self.assertGreaterEqual(len(executed), 1)

    def test_dream_generation_once_per_night(self):
        engine = get_or_create_engine("thevillage-test")
        engine.state.current_hour = 0
        for villager in engine.villagers:
            villager.ensure_state(engine.state)

        process_hour(engine.state, engine.state.environment, engine.villagers)
        first_lengths = {
            name: len(v_state.dream_log)
            for name, v_state in engine.state.villager_states.items()
        }

        engine.state.current_hour = 1
        process_hour(engine.state, engine.state.environment, engine.villagers)
        second_lengths = {
            name: len(v_state.dream_log)
            for name, v_state in engine.state.villager_states.items()
        }

        for name in first_lengths:
            self.assertEqual(first_lengths[name], 1)
            self.assertEqual(second_lengths[name], 1)

    def test_color_scheme_ranges(self):
        dawn = get_color_scheme(6)
        day = get_color_scheme(12)
        sunset = get_color_scheme(18)
        night = get_color_scheme(22)

        self.assertNotEqual(dawn["sky_top"], day["sky_top"])
        self.assertNotEqual(day["sky_top"], sunset["sky_top"])
        self.assertNotEqual(sunset["sky_top"], night["sky_top"])

    def test_waking_vs_dream_hours(self):
        engine = get_or_create_engine("thevillage-test")
        engine.state.current_hour = 3
        self.assertTrue(engine.is_dream_time())

        engine.state.current_hour = 10
        self.assertFalse(engine.is_dream_time())

    def test_house_brief_refreshes_with_daily_cycle(self):
        state = InternalState(session_id="thevillage-test")
        state.turn_index = 7
        villagers = default_villagers()

        daily_tick(state, state.environment, villagers)

        self.assertEqual(len(state.villager_states), 6)
        for villager_state in state.villager_states.values():
            brief = villager_state.house_brief
            self.assertTrue(brief.house_goal)
            self.assertTrue(brief.problem_statement)
            self.assertTrue(brief.guidance_request)
            self.assertEqual(len(brief.choices), 4)
            self.assertEqual(brief.last_updated_turn, 7)

    def test_role_specific_dream_interpretation_and_shift_shape(self):
        state = InternalState(session_id="thevillage-test")
        for villager in default_villagers():
            dream = villager.generate_dream(state, state.environment)
            insight = villager.interpret_dream(dream)
            shift = villager.dream_to_goal_shift(dream)

            self.assertIsInstance(insight, str)
            self.assertTrue(insight)
            self.assertIsInstance(shift, dict)
            self.assertIn("priority_delta", shift)
            self.assertIn("new_goal_suggestions", shift)
            self.assertIn("long_horizon_bias", shift)

    def test_dream_night_populates_brief_insight_and_aspiration(self):
        state = InternalState(session_id="thevillage-test")
        villagers = default_villagers()
        state.current_hour = 1

        process_hour(state, state.environment, villagers)
        state.current_hour = 8
        daily_tick(state, state.environment, villagers)

        for villager_state in state.villager_states.values():
            self.assertTrue(villager_state.house_brief.dream_insight)
            self.assertTrue(villager_state.house_brief.aspiration)

    def test_dream_shift_changes_state_subtly(self):
        state = InternalState(session_id="thevillage-test")
        villagers = default_villagers()
        state.current_hour = 2
        baseline_tension = state.bodily_state["tension"]
        baseline_curiosity = state.emotional_state["curiosity"]
        baseline_stability = state.self_model["stability"]

        process_hour(state, state.environment, villagers)

        self.assertNotEqual(state.bodily_state["tension"], baseline_tension)
        self.assertNotEqual(state.emotional_state["curiosity"], baseline_curiosity)
        self.assertNotEqual(state.self_model["stability"], baseline_stability)

    def test_villager_choice_persists_to_brief_selected_choice(self):
        client = app.test_client()
        session_id = "thevillage-test"
        state_response = client.get(f"/api/state/{session_id}")
        self.assertEqual(state_response.status_code, 200)
        payload = state_response.get_json()
        villager_name = payload["villagers"][0]["name"]

        response = client.post(
            "/api/villager-choice",
            json={"session_id": session_id, "villager_name": villager_name, "choice_index": 2},
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        selected = next(item for item in data["villagers"] if item["name"] == villager_name)
        self.assertEqual(selected["house_brief"]["selected_choice"], 2)

    def test_dreams_do_not_include_task_names(self):
        state = InternalState(session_id="thevillage-test")
        state.task_backlog = [
            Task(description="SENSITIVE_TASK_TOKEN_ALPHA", proposed_by="Tomas", priority=1.0, expected_reward=0.2)
        ]
        state.active_goals = [
            Goal(name="SENSITIVE_GOAL_TOKEN_BETA", drive="mission", priority=0.8)
        ]
        state.unresolved_tensions = ["SENSITIVE_TENSION_TOKEN_GAMMA"]

        for villager in default_villagers():
            dream_line = villager.generate_dream(state, state.environment)
            lowered = dream_line.lower()
            self.assertNotIn("sensitive_task_token_alpha".lower(), lowered)
            self.assertNotIn("sensitive_goal_token_beta".lower(), lowered)
            self.assertNotIn("sensitive_tension_token_gamma".lower(), lowered)

    def test_symbolic_dream_generation_per_role(self):
        villagers = default_villagers()
        for villager in villagers:
            line = villager.generate_symbolic_dream()
            self.assertTrue(line.startswith("In "))
            self.assertIn("began to", line)

    def test_dream_arc_advances_and_rolls_theme(self):
        villager = default_villagers()[0]
        start_theme = villager.dream_arc_theme
        villager.dream_arc_stage = 6
        villager.advance_dream_arc()

        self.assertEqual(villager.dream_arc_stage, 0)
        self.assertTrue(villager.dream_arc_theme)
        self.assertIn(villager.dream_arc_theme, ["growth", "fracture", "search", "alignment", "warning"])
        self.assertTrue(start_theme in ["growth", "fracture", "search", "alignment", "warning"])

    def test_subconscious_tension_engine_updates(self):
        villager = default_villagers()[0]
        state = InternalState(session_id="thevillage-test")
        villager.unresolved_tension = 0.0
        state.bodily_state["tension"] = 0.8
        state.health_metrics.contradiction_count = 2
        state.unresolved_tensions = ["conflict"]
        state.subsystem_scores = {"a": 0.9, "b": 0.1}

        villager.update_subconscious_tension(state)

        self.assertGreater(villager.unresolved_tension, 0.0)
        self.assertLessEqual(villager.unresolved_tension, 1.0)

    def test_aura_synthesizes_from_all_dreams(self):
        state = InternalState(session_id="thevillage-test")
        aura = Aura(state)
        dreams = {
            "planner": "In a shifting grid, a map began to loop.",
            "curiosity keeper": "In a library, glyphs began to glow.",
            "stability steward": "In a workshop, mirrors began to fracture.",
            "narrator": "In a corridor, voices began to echo.",
            "architect": "In a blueprint field, pillars began to grow.",
            "caretaker": "In a grove, roots began to wilt.",
        }

        synthesis = aura.synthesize_dreams(dreams)

        self.assertTrue(synthesis)
        self.assertIn("traces of", synthesis)
        self.assertGreaterEqual(len(aura.dream_history), 1)

    def test_aura_tension_increases_with_stress_and_contradictions(self):
        state = InternalState(session_id="thevillage-test")
        state.bodily_state["tension"] = 0.9
        state.health_metrics.contradiction_count = 2
        state.unresolved_tensions = ["rift"]
        state.health_metrics.global_health = 0.4
        aura = Aura(state)
        before = aura.tension_level

        aura.update_arc_and_tension()

        self.assertGreater(aura.tension_level, before)
        self.assertLessEqual(aura.tension_level, 1.0)

    def test_aura_generates_forecast(self):
        state = InternalState(session_id="thevillage-test")
        aura = Aura(state)
        aura.arc_theme = "warning"
        aura.tension_level = 0.9
        aura.last_synthesis = "In a still well, lanterns begin to darken."

        forecast = aura.generate_forecast()

        self.assertIn("Aura glimpses", forecast)
        self.assertTrue(aura.last_forecast)

    def test_aura_state_exposed_in_api(self):
        client = app.test_client()
        session_id = "thevillage-test"

        state_response = client.get(f"/api/state/{session_id}")
        self.assertEqual(state_response.status_code, 200)
        state_payload = state_response.get_json()
        self.assertIn("aura", state_payload)

        aura_response = client.get(f"/aura/{session_id}")
        self.assertEqual(aura_response.status_code, 200)
        aura_payload = aura_response.get_json()
        self.assertEqual(aura_payload.get("name"), "Aura")
        self.assertEqual(aura_payload.get("role"), "oracle")

    def test_interpretation_uses_symbolic_keywords(self):
        villagers = {villager.name: villager for villager in default_villagers()}

        self.assertIn("simplify", villagers["Tomas"].interpret_dream("In a shifting grid, the maps began to loop." ).lower())
        self.assertIn("explore", villagers["Mira"].interpret_dream("In a river of questions, the glyphs began to reveal." ).lower())
        self.assertIn("repair", villagers["Edda"].interpret_dream("In a silent workshop, the mirrors began to fracture." ).lower())
        self.assertIn("narrative", villagers["Lio"].interpret_dream("In an endless stage, the shadows began to fade." ).lower())
        self.assertIn("structural", villagers["Sable"].interpret_dream("In a shifting blueprint, the pillars began to collapse." ).lower())
        self.assertIn("resilience", villagers["Jun"].interpret_dream("In a quiet grove, the gardens began to wilt." ).lower())


if __name__ == "__main__":
    unittest.main()