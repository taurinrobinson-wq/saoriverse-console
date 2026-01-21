"""Tests for PolicyRouter."""

import pytest
from src.emotional_os.pipeline.policy_router import PolicyRouter


@pytest.fixture
def router():
    return PolicyRouter()


class TestTurnTypeRouting:
    """Test turn-type to generator routing."""

    def test_closure_routes_to_template(self, router):
        """Closure should route to template_composer."""
        result = router.route(
            turn_type="closure",
            base_response="Goodbye, thanks for talking",
        )
        assert "template_composer" in result["allowed_generators"]

    def test_gratitude_routes_to_template(self, router):
        """Gratitude should route to template_composer."""
        result = router.route(
            turn_type="gratitude",
            base_response="I appreciate that",
        )
        assert "template_composer" in result["allowed_generators"]

    def test_disclosure_routes_to_compressor(self, router):
        """Disclosure should route to compressor."""
        result = router.route(
            turn_type="disclosure",
            base_response="I hear your struggle",
        )
        assert "compressor" in result["allowed_generators"]

    def test_meta_routes_to_orchestrator(self, router):
        """Meta questions should route to orchestrator."""
        result = router.route(
            turn_type="meta",
            base_response="I work by listening",
        )
        assert "orchestrator" in result["allowed_generators"]


class TestSentenceLimitEnforcement:
    """Test response length constraints."""

    def test_closure_max_2_sentences(self, router):
        """Closure responses max 2 sentences."""
        # 3 sentences should violate
        long_response = "Goodbye. Thanks for talking. See you soon."
        result = router.route(turn_type="closure", base_response=long_response)
        assert not result["invariants_pass"]
        assert any("sentence" in v.lower() for v in result["violations"])

    def test_disclosure_max_4_sentences(self, router):
        """Disclosure responses max 4 sentences."""
        # 5 sentences should violate
        long_response = (
            "I hear you. This is hard. You're not alone. "
            "That takes courage. I'm here with you. That matters."
        )
        result = router.route(turn_type="disclosure", base_response=long_response)
        assert not result["invariants_pass"]

    def test_short_response_passes(self, router):
        """Short responses should pass length check."""
        result = router.route(
            turn_type="disclosure",
            base_response="I hear you. That's real.",
        )
        assert result["invariants_pass"]


class TestVerbatimEchoPrevention:
    """Test verbatim echo detection."""

    def test_detects_verbatim_echo(self, router):
        """Should detect >3 consecutive user words in response."""
        user_message = "I'm exhausted and overwhelmed by work"
        response = "I hear that you're exhausted and overwhelmed by work stress"
        result = router.route(
            turn_type="disclosure",
            base_response=response,
            user_message=user_message,
        )
        assert not result["invariants_pass"]
        assert any("echo" in v.lower() for v in result["violations"])

    def test_paraphrasing_passes(self, router):
        """Paraphrased responses should pass."""
        user_message = "I'm exhausted and overwhelmed by work"
        response = "The weight of your job is draining you right now."
        result = router.route(
            turn_type="disclosure",
            base_response=response,
            user_message=user_message,
        )
        assert result["invariants_pass"]

    def test_no_user_message_passes(self, router):
        """Empty user message should not fail echo check."""
        result = router.route(
            turn_type="disclosure",
            base_response="Some response",
            user_message="",
        )
        # Should pass (no echo possible)
        assert "echo" not in " ".join(result["violations"]).lower()


class TestDomainReferenceRequirement:
    """Test domain reference enforcement."""

    def test_high_domain_requires_reference(self, router):
        """High-scoring domains (>0.6) must be referenced."""
        domains = {
            "exhaustion": 0.9,
            "stress": 0.7,
            "blocked_joy": 0.3,
        }
        response = "You seem overwhelmed right now"  # Doesn't reference exhaustion
        result = router.route(
            turn_type="disclosure",
            base_response=response,
            domains=domains,
        )
        assert not result["invariants_pass"]
        assert any("domain" in v.lower() for v in result["violations"])

    def test_referenced_domain_passes(self, router):
        """Referenced domains should pass."""
        domains = {"exhaustion": 0.9, "stress": 0.5}
        response = "The exhaustion you're describing is real and deep."
        result = router.route(
            turn_type="disclosure",
            base_response=response,
            domains=domains,
        )
        assert result["invariants_pass"]

    def test_no_high_domains_passes(self, router):
        """No high-scoring domains means no requirement."""
        domains = {
            "exhaustion": 0.3,
            "stress": 0.2,
            "blocked_joy": 0.1,
        }
        response = "I'm here to listen."
        result = router.route(
            turn_type="disclosure",
            base_response=response,
            domains=domains,
        )
        assert result["invariants_pass"]


class TestAffectConsistency:
    """Test affect consistency checking."""

    def test_negative_valence_no_celebrate(self, router):
        """Negative valence + celebratory tone = violation."""
        affect = {"valence": 0.2, "tone": "frustrated"}
        response = "This is amazing and wonderful!"
        result = router.route(
            turn_type="disclosure",
            base_response=response,
            affect=affect,
        )
        assert not result["invariants_pass"]

    def test_positive_affect_can_celebrate(self, router):
        """Positive affect + celebration = OK."""
        affect = {"valence": 0.8, "tone": "excited"}
        response = "This is wonderful and amazing!"
        result = router.route(
            turn_type="disclosure",
            base_response=response,
            affect=affect,
        )
        assert result["invariants_pass"]

    def test_neutral_tone_matches_negative_valence(self, router):
        """Neutral tone OK with negative valence."""
        affect = {"valence": 0.3, "tone": "neutral"}
        response = "I hear your concern about this situation."
        result = router.route(
            turn_type="disclosure",
            base_response=response,
            affect=affect,
        )
        assert result["invariants_pass"]


class TestRecommendedGenerator:
    """Test generator recommendations."""

    def test_closure_recommends_template(self, router):
        """Closure turn recommends template_composer."""
        result = router.route(
            turn_type="closure",
            base_response="Goodbye",
        )
        assert result["recommended_generator"] == "template_composer"

    def test_disclosure_recommends_compressor(self, router):
        """Disclosure turn recommends compressor."""
        result = router.route(
            turn_type="disclosure",
            base_response="I hear you",
        )
        assert result["recommended_generator"] == "compressor"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
