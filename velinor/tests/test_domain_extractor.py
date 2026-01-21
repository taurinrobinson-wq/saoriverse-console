"""Tests for DomainExtractor."""

import pytest
from src.emotional_os.pipeline.domain_extractor import DomainExtractor


@pytest.fixture
def extractor():
    return DomainExtractor()


class TestDomainExtractionBasics:
    """Test basic domain extraction."""

    def test_always_returns_all_domains(self, extractor):
        """Should always return all 7 domains with values in [0.0, 1.0]."""
        result = extractor.extract("Hello")
        assert len(result) == 7
        assert set(result.keys()) == {
            "exhaustion",
            "stress",
            "blocked_joy",
            "contrast",
            "temporal_pressure",
            "disappointment",
            "isolation",
        }
        for domain, score in result.items():
            assert isinstance(score, float)
            assert 0.0 <= score <= 1.0

    def test_deterministic(self, extractor):
        """Same input should produce same output."""
        msg = "I'm exhausted and stressed"
        result1 = extractor.extract(msg)
        result2 = extractor.extract(msg)
        assert result1 == result2


class TestExhaustionDetection:
    """Test exhaustion domain."""

    def test_detects_exhaustion_markers(self, extractor):
        """Should detect exhaustion keywords."""
        result = extractor.extract("I'm exhausted")
        assert result["exhaustion"] > 0.5

    def test_multiple_exhaustion_markers_increase_score(self, extractor):
        """Multiple markers should increase exhaustion score."""
        result1 = extractor.extract("I'm tired")
        result2 = extractor.extract("I'm tired and weary and drained")
        assert result2["exhaustion"] > result1["exhaustion"]

    def test_exhaustion_tone_boost(self, extractor):
        """Exhaustion tone in affect should boost exhaustion domain."""
        result = extractor.extract("I'm struggling", affect={"tone": "exhausted"})
        assert result["exhaustion"] > 0.7


class TestStressDetection:
    """Test stress domain."""

    def test_detects_stress_markers(self, extractor):
        """Should detect stress keywords."""
        result = extractor.extract("I'm stressed and overwhelmed")
        assert result["stress"] > 0.5

    def test_stress_tone_boost(self, extractor):
        """Stress tone should boost stress domain."""
        result = extractor.extract("Pressure building", affect={"tone": "overwhelmed"})
        assert result["stress"] > 0.5


class TestBlockedJoyDetection:
    """Test blocked_joy domain."""

    def test_detects_blocked_joy_markers(self, extractor):
        """Should detect blocked joy keywords."""
        result = extractor.extract("I can't feel joy anymore")
        assert result["blocked_joy"] > 0.5

    def test_negative_valence_increases_blocked_joy(self, extractor):
        """Negative valence should increase blocked_joy risk."""
        result_neutral = extractor.extract("Something happened", affect={"valence": 0.5})
        result_negative = extractor.extract(
            "Something happened", affect={"valence": 0.2}
        )
        assert result_negative["blocked_joy"] > result_neutral["blocked_joy"]

    def test_positive_valence_decreases_blocked_joy(self, extractor):
        """Positive valence should decrease blocked_joy."""
        result_positive = extractor.extract(
            "I can't feel joy", affect={"valence": 0.8}
        )
        assert result_positive["blocked_joy"] < 0.5


class TestContrastDetection:
    """Test contrast domain (out-of-sync with surroundings)."""

    def test_detects_contrast_markers(self, extractor):
        """Should detect contrast keywords."""
        result = extractor.extract("Everyone else is rushing by while I'm stuck")
        assert result["contrast"] > 0.5


class TestTemporalPressureDetection:
    """Test temporal_pressure domain."""

    def test_detects_deadline_language(self, extractor):
        """Should detect time-pressure keywords."""
        result = extractor.extract("Christmas in two days")
        assert result["temporal_pressure"] > 0.5

    def test_detects_soon_language(self, extractor):
        """Should detect 'soon' language."""
        result = extractor.extract("The deadline is soon")
        assert result["temporal_pressure"] > 0.4


class TestDisappointmentDetection:
    """Test disappointment domain."""

    def test_detects_disappointment_markers(self, extractor):
        """Should detect disappointment keywords."""
        result = extractor.extract("I'm disappointed and let down")
        assert result["disappointment"] > 0.5

    def test_sardonic_tone_boosts_disappointment(self, extractor):
        """Sardonic tone should boost disappointment."""
        result = extractor.extract(
            "So happy about this", affect={"tone": "sardonic"}
        )
        assert result["disappointment"] > 0.5


class TestIsolationDetection:
    """Test isolation domain."""

    def test_detects_isolation_markers(self, extractor):
        """Should detect isolation keywords."""
        result = extractor.extract("I feel so alone")
        assert result["isolation"] > 0.5

    def test_sad_tone_boosts_isolation(self, extractor):
        """Sad tone should boost isolation."""
        result = extractor.extract("Nobody understands", affect={"tone": "sad"})
        assert result["isolation"] > 0.5


class TestMultipleDomains:
    """Test multiple domains in one message."""

    def test_exhaustion_plus_stress(self, extractor):
        """Message with both exhaustion and stress should score both."""
        result = extractor.extract("I'm exhausted and stressed out")
        assert result["exhaustion"] > 0.5
        assert result["stress"] > 0.5

    def test_exhaustion_temporal_pressure(self, extractor):
        """Realistic message: exhaustion + temporal pressure."""
        result = extractor.extract("I'm so tired of things right now... Christmas in two days.")
        assert result["exhaustion"] > 0.5
        assert result["temporal_pressure"] > 0.5


class TestAffectInfluence:
    """Test that affect metadata properly influences domains."""

    def test_valence_influences_blocked_joy(self, extractor):
        """Valence should shift blocked_joy score."""
        result_neg = extractor.extract("I'm here", affect={"valence": 0.1})
        result_pos = extractor.extract("I'm here", affect={"valence": 0.9})
        assert result_neg["blocked_joy"] > result_pos["blocked_joy"]

    def test_tone_provides_primary_signal(self, extractor):
        """Tone should provide strong primary domain signal."""
        result = extractor.extract("Things are hard", affect={"tone": "exhausted"})
        assert result["exhaustion"] > 0.6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
