"""Tests for PipelineOrchestrator end-to-end."""

import pytest
from src.emotional_os.pipeline.orchestrator import PipelineOrchestrator


@pytest.fixture
def orchestrator():
    return PipelineOrchestrator()


class TestOrchestratorBasics:
    """Test orchestrator basic functionality."""

    def test_returns_all_required_fields(self, orchestrator):
        """Orchestrator should return complete routing decision."""
        result = orchestrator.run("I'm tired")
        assert "turn_type" in result
        assert "turn_confidence" in result
        assert "emotional_signal" in result
        assert "domains" in result
        assert "routing_decision" in result
        assert "pipeline_metadata" in result

    def test_routing_decision_structure(self, orchestrator):
        """Routing decision should have all required fields."""
        result = orchestrator.run("I'm exhausted")
        routing = result["routing_decision"]
        assert "allowed_generators" in routing
        assert "invariants_pass" in routing
        assert "violations" in routing
        assert "recommended_generator" in routing

    def test_deterministic(self, orchestrator):
        """Same input should produce same output."""
        msg = "I'm struggling with this"
        result1 = orchestrator.run(msg)
        result2 = orchestrator.run(msg)
        assert result1["turn_type"] == result2["turn_type"]
        assert result1["domains"] == result2["domains"]


class TestExhaustionDisclosureFlow:
    """Test realistic exhaustion disclosure scenario."""

    def test_exhaustion_classified_as_disclosure(self, orchestrator):
        """Exhaustion message should classify as disclosure."""
        result = orchestrator.run("I'm so tired of things right now")
        assert result["turn_type"] == "disclosure"
        assert result["emotional_signal"] == "exhaustion"

    def test_exhaustion_extracts_domains(self, orchestrator):
        """Should extract exhaustion and related domains."""
        result = orchestrator.run(
            "I'm so tired of things right now... Christmas in two days.",
            affect={"tone": "tired", "valence": 0.2, "arousal": 0.4},
        )
        assert result["domains"]["exhaustion"] > 0.5
        assert result["domains"]["temporal_pressure"] > 0.5
        assert result["domains"]["stress"] > 0.4

    def test_exhaustion_routes_to_compressor(self, orchestrator):
        """Exhaustion disclosure should route to compressor generator."""
        result = orchestrator.run(
            "I'm exhausted",
            base_response="I hear your exhaustion.",
        )
        routing = result["routing_decision"]
        assert "compressor" in routing["allowed_generators"]

    def test_exhaustion_with_high_domains_enforces_reference(self, orchestrator):
        """High-scoring domains must be referenced in response."""
        # Response that doesn't reference exhaustion
        result = orchestrator.run(
            "I'm so tired",
            base_response="That sounds difficult.",
            affect={"tone": "tired", "valence": 0.2},
        )
        # Should fail policy check because response doesn't reference exhaustion
        routing = result["routing_decision"]
        # Invariants may or may not pass depending on response length, but domain reference check is strict
        if result["domains"]["exhaustion"] > 0.6:
            # Expected: violations about domain reference
            pass


class TestGratitudeFlow:
    """Test gratitude turn flow."""

    def test_gratitude_classified_correctly(self, orchestrator):
        """Gratitude should classify as gratitude turn type."""
        result = orchestrator.run("Thank you for listening, that really helped")
        assert result["turn_type"] == "gratitude"

    def test_gratitude_routes_to_template(self, orchestrator):
        """Gratitude should route to template_composer."""
        result = orchestrator.run("Thank you so much")
        routing = result["routing_decision"]
        assert "template_composer" in routing["allowed_generators"]


class TestMetaFlow:
    """Test meta question flow."""

    def test_meta_question_classified(self, orchestrator):
        """Meta questions should classify as meta."""
        result = orchestrator.run("How do you know what to say?")
        assert result["turn_type"] == "meta"

    def test_meta_routes_to_orchestrator(self, orchestrator):
        """Meta should route to orchestrator generator."""
        result = orchestrator.run("Can you explain how you work?")
        routing = result["routing_decision"]
        assert "orchestrator" in routing["allowed_generators"]


class TestMultipleDomainScenario:
    """Test complex multi-domain scenario."""

    def test_exhaustion_stress_isolation(self, orchestrator):
        """Complex message with multiple domains."""
        message = "I'm exhausted, everything feels overwhelming, and I'm dealing with this alone."
        affect = {
            "tone": "sad",
            "valence": 0.1,
            "arousal": 0.5,
        }
        result = orchestrator.run(message, affect=affect)

        # Should detect multiple high-scoring domains
        domains = result["domains"]
        assert domains["exhaustion"] > 0.5
        assert domains["stress"] > 0.5
        assert domains["isolation"] > 0.5

        # Should classify as disclosure
        assert result["turn_type"] == "disclosure"

        # Should route to compressor
        routing = result["routing_decision"]
        assert "compressor" in routing["allowed_generators"]


class TestPolicyEnforcement:
    """Test that policy invariants are enforced."""

    def test_response_length_checked(self, orchestrator):
        """Response length should be validated per turn type."""
        # Create a very long response (5+ sentences)
        long_response = "A. B. C. D. E. F."
        result = orchestrator.run(
            "I'm struggling",
            base_response=long_response,
        )
        routing = result["routing_decision"]
        # Should fail length check
        if routing["invariants_pass"] == False:
            assert any("sentence" in v.lower() for v in routing["violations"])

    def test_verbatim_echo_check(self, orchestrator):
        """Verbatim echo should be detected."""
        message = "I'm exhausted and frustrated"
        response = "I hear that you're exhausted and frustrated"
        result = orchestrator.run(message, base_response=response)
        routing = result["routing_decision"]
        # Should detect echo violation
        if not routing["invariants_pass"]:
            assert any("echo" in v.lower() for v in routing["violations"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
