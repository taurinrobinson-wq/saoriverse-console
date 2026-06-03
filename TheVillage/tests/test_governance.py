import unittest

from TheVillage.core.mind import get_or_create_engine, reset_engine
from TheVillage.governance import (
    compute_leadership_score,
    get_governance,
    maybe_run_revalidation_election,
    refresh_needs_vector,
    run_election,
    trigger_revalidation_if_needed,
)


class TestGovernanceRegression(unittest.TestCase):
    def setUp(self):
        reset_engine("thevillage-governance-test")

    def tearDown(self):
        reset_engine("thevillage-governance-test")

    def _engine(self):
        engine = get_or_create_engine("thevillage-governance-test")
        for villager in engine.villagers:
            villager.ensure_state(engine.state)
        return engine

    def test_term_limits_and_cooldowns_enforce(self):
        engine = self._engine()
        state = engine.state
        governance = get_governance(state)
        governance["consecutive_term_limit"] = 2
        governance["cooldown_terms"] = 2

        for name, villager_state in state.villager_states.items():
            villager_state.reward_trend = -0.2
            if name == "Edda":
                villager_state.reward_trend = 0.95

        names = [villager.name for villager in engine.villagers]
        first = run_election(state, names, election_type="scheduled", reason="test election #1")
        second = run_election(state, names, election_type="scheduled", reason="test election #2")
        third = run_election(state, names, election_type="scheduled", reason="test election #3")

        self.assertEqual(first["leader"], "Edda")
        self.assertEqual(second["leader"], "Edda")
        self.assertNotEqual(third["leader"], "Edda")
        self.assertEqual(int(get_governance(state)["cooldown_remaining"].get("Edda", 0)), 2)

    def test_crisis_election_does_not_increment_term_count(self):
        engine = self._engine()
        state = engine.state
        governance = get_governance(state)
        governance["consecutive_terms_served"] = {"Edda": 1}
        governance["term_started_day"] = state.current_day
        governance["crisis_election_does_not_increment_term_count"] = True

        state.evolution_meta["active_crisis"] = "leadership"
        state.evolution_meta["affected_villager"] = "Tomas"
        state.evolution_meta["recovery_status"] = "acute"

        names = [villager.name for villager in engine.villagers]
        result = run_election(state, names, election_type="crisis", reason="test crisis election")

        self.assertFalse(bool(result.get("counted", 1)))
        self.assertEqual(int(get_governance(state)["consecutive_terms_served"].get("Edda", 1)), 1)

    def test_revalidation_trigger_and_outcome(self):
        engine = self._engine()
        state = engine.state
        governance = get_governance(state)
        governance["legitimacy_score"] = 0.2

        should_revalidate = trigger_revalidation_if_needed(state)
        election_result = maybe_run_revalidation_election(state, [villager.name for villager in engine.villagers])

        self.assertTrue(should_revalidate)
        self.assertIsNotNone(election_result)
        self.assertFalse(bool(get_governance(state)["revalidation_pending"]))

    def test_scoring_responds_to_needs_vector(self):
        engine = self._engine()
        state = engine.state

        state.environment.coherence = 0.8
        refresh_needs_vector(state)
        score_stable = compute_leadership_score("Tomas", {"state": state})

        state.environment.coherence = 0.35
        refresh_needs_vector(state)
        score_low_coherence = compute_leadership_score("Tomas", {"state": state})

        self.assertGreater(score_low_coherence, score_stable)

    def test_crisis_language_remains_non_adversarial(self):
        engine = self._engine()
        engine.interact("Tomas has fallen ill and leadership continuity is at risk.", action="observe")
        result = engine.interact(
            "Tomas is recovering but Edda does not want to give up leadership and election legitimacy is in doubt.",
            action="observe",
        )

        blocked = ["sabotage", "manipulate", "attack", "undermine", "hostility", "resentment"]
        for villager_state in result.state.villager_states.values():
            brief = villager_state.house_brief
            corpus = " ".join([brief.house_goal, brief.problem_statement, brief.guidance_request] + brief.choices).lower()
            for token in blocked:
                self.assertNotIn(token, corpus)

    def test_crisis_to_election_to_stabilization_loop(self):
        engine = self._engine()
        result = engine.interact("Tomas has fallen ill and needs interim leadership now.", action="observe")

        self.assertTrue(any("Crisis protocol activated" in event for event in result.state.recent_events))
        self.assertTrue(any("Post-election stabilization" in event for event in result.state.recent_events))
        self.assertIn("governance", result.state.telemetry)


if __name__ == "__main__":
    unittest.main()
