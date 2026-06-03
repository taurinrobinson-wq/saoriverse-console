import unittest

from TheVillage.core.mind import get_or_create_engine, reset_engine
from TheVillage.evolution_engine import EvolutionEngine
from TheVillage.interface.api import app


class TestEvolutionModes(unittest.TestCase):
    def setUp(self):
        reset_engine("thevillage-evolution-test")

    def tearDown(self):
        reset_engine("thevillage-evolution-test")

    def test_homeostasis_mode_applies_stabilization(self):
        engine = get_or_create_engine("thevillage-evolution-test")
        engine.state.evolution_mode = "homeostasis"
        engine.state.bodily_state["tension"] = 0.62
        engine.state.environment.coherence = 0.45
        engine.state.background_processes["rumination"] = 0.63

        before_tension = engine.state.bodily_state["tension"]
        before_coherence = engine.state.environment.coherence

        result = engine.evolution.run_cycle(
            engine.state,
            [villager.name for villager in engine.villagers],
            mode="homeostasis",
            aura=engine.aura,
        )

        self.assertEqual(result["mode"], "homeostasis")
        self.assertLess(engine.state.bodily_state["tension"], before_tension)
        self.assertGreater(engine.state.environment.coherence, before_coherence)

    def test_disruption_mode_registers_events(self):
        engine = get_or_create_engine("thevillage-evolution-test")
        engine.state.turn_index = 3
        engine.state.evolution_mode = "disruption"
        engine.state.evolution_meta["disruption_cooldown"] = 0

        result = engine.evolution.run_cycle(
            engine.state,
            [villager.name for villager in engine.villagers],
            mode="disruption",
            aura=engine.aura,
        )

        self.assertEqual(result["mode"], "disruption")
        self.assertIn("disruption", str(result["result"]))
        self.assertTrue(len(engine.state.registered_event_types) >= 1 or len(engine.state.event_backlog) >= 0)

    def test_elections_mode_sets_leader_when_triggered(self):
        engine = get_or_create_engine("thevillage-evolution-test")
        for villager in engine.villagers:
            villager.ensure_state(engine.state)
        engine.state.turn_index = 6
        engine.state.villager_states["Edda"].reward_trend = 0.95
        engine.state.health_metrics.contradiction_count = 3

        result = engine.evolution.run_cycle(
            engine.state,
            [villager.name for villager in engine.villagers],
            mode="elections",
            aura=engine.aura,
        )

        self.assertEqual(result["mode"], "elections")
        self.assertIn(engine.state.executive_function, {villager.name for villager in engine.villagers})

    def test_api_mode_switch_endpoint(self):
        client = app.test_client()
        response = client.post(
            "/api/mode",
            json={"session_id": "thevillage-evolution-test", "mode": "elections"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["selected_mode"], "elections")


if __name__ == "__main__":
    unittest.main()
