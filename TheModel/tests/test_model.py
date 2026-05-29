import unittest

from TheModel.core.mind import TheModelEngine, get_or_create_engine, reset_engine
from TheModel.core.models import EnvironmentState, InternalState
from TheModel.core.scheduler import daily_tick
from TheModel.core.villagers import CuriosityVillager, StabilityVillager, default_villagers
from TheModel.interface.dialogue import village_summary_to_dialogue, villager_to_dialogue
from TheModel.memory.store import save_state


class TestTheModel(unittest.TestCase):
    def setUp(self):
        reset_engine("themodel-test")

    def tearDown(self):
        reset_engine("themodel-test")

    def test_persistent_state_across_turns(self):
        engine = get_or_create_engine("themodel-test")
        first = engine.interact("I was rejected and want to understand what happened.", action="observe")
        second = engine.interact("Please define limerence for me.", action="ask")

        self.assertEqual(first.turn_index, 1)
        self.assertEqual(second.turn_index, 2)
        self.assertGreaterEqual(len(second.state.working_memory), 2)
        self.assertGreaterEqual(second.state.self_model["continuity"], first.state.self_model["continuity"])
        self.assertTrue(second.state.narrative)

    def test_unknown_terms_create_questions(self):
        engine = TheModelEngine("themodel-test")
        result = engine.interact("I feel quoralen and vesperline moving through this scene.", action="ask")

        self.assertGreaterEqual(len(result.state.vocabulary_questions), 1)
        self.assertIn("reason", result.state.vocabulary_questions[0])

    def test_teaching_a_term_updates_dictionary(self):
        engine = get_or_create_engine("themodel-test")
        engine.vocabulary.learn_definition("sonder", "The realization that others have lives as vivid as your own.", source="user")
        result = engine.interact("sonder matters to how I understand others", action="define")

        self.assertIn("sonder", result.state.known_terms)
        self.assertGreater(result.state.reward_signal, -1.0)

    def test_daily_tick_executes_ranked_tasks(self):
        state = InternalState(session_id="themodel-test")
        state.vocabulary_questions = [{"term": "quoralen", "question": "What does quoralen mean?", "reason": "unknown_term"}]
        state.unresolved_tensions = ["A contradiction is still open."]
        state.health_metrics.contradiction_count = 2
        villagers = default_villagers()

        executed = daily_tick(state, state.environment, villagers)

        self.assertGreaterEqual(len(executed), 1)
        self.assertTrue(state.narrative)
        self.assertGreaterEqual(state.health_metrics.global_health, 0.0)

    def test_villagers_propose_expected_tasks(self):
        state = InternalState(session_id="themodel-test")
        state.vocabulary_questions = [{"term": "vesperline", "question": "What does vesperline mean?", "reason": "unknown_term"}]
        state.unresolved_tensions = ["Subsystems disagree"]
        state.health_metrics.contradiction_count = 2

        curiosity_tasks = CuriosityVillager().propose_tasks(state, state.environment)
        stability_tasks = StabilityVillager().propose_tasks(state, state.environment)

        self.assertTrue(any("definition" in task.description.lower() for task in curiosity_tasks))
        self.assertTrue(any("contradiction" in task.description.lower() for task in stability_tasks))

    def test_health_metrics_update_during_daily_tick(self):
        state = InternalState(session_id="themodel-test")
        state.health_metrics.goal_progress_rate = 0.1
        state.health_metrics.global_health = 0.3
        state.unresolved_tensions = ["One tension", "Another tension"]

        daily_tick(state, EnvironmentState(), default_villagers())

        self.assertGreaterEqual(state.health_metrics.goal_progress_rate, 0.1)
        self.assertGreaterEqual(state.health_metrics.contradiction_count, 0)

    def test_dialogue_generation_handles_sparse_state(self):
        state = InternalState(session_id="themodel-test")
        summary = village_summary_to_dialogue(state.to_dict(), state.narrative)
        villager_line = villager_to_dialogue({"name": "Tomas", "role": "planner", "mood": "steady"}, [])

        self.assertTrue(summary)
        self.assertTrue(villager_line)

    def test_daily_cycle_runs_once_per_day(self):
        engine = get_or_create_engine("themodel-test")
        engine.state.last_run = "2000-01-01T00:00:00+00:00"
        save_state(engine.state)
        first = engine.run_daily_cycle()
        second = engine.run_daily_cycle()

        self.assertGreaterEqual(len(first), 1)
        self.assertEqual(second, [])


if __name__ == "__main__":
    unittest.main()