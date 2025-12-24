"""Tests for TurnClassifier."""

import pytest
from src.emotional_os.pipeline.turn_classifier import TurnClassifier


@pytest.fixture
def classifier():
    return TurnClassifier()


class TestTurnClassifierBasics:
    """Test basic classification functionality."""

    def test_always_returns_one_turn_type(self, classifier):
        """Verify classifier always returns exactly one turn_type."""
        messages = [
            "I'm so tired",
            "Thank you for listening",
            "How do you work?",
            "Goodbye",
            "Actually, I meant something else",
        ]

        for msg in messages:
            result = classifier.classify(msg)
            assert "turn_type" in result
            assert result["turn_type"] in [
                "disclosure",
                "gratitude",
                "meta",
                "closure",
                "correction",
            ]

    def test_deterministic_classification(self, classifier):
        """Verify same input always produces same output."""
        message = "I'm struggling with this"
        result1 = classifier.classify(message)
        result2 = classifier.classify(message)
        assert result1["turn_type"] == result2["turn_type"]
        assert result1["confidence"] == result2["confidence"]

    def test_returns_required_fields(self, classifier):
        """Verify all required output fields are present."""
        result = classifier.classify("I feel sad")
        assert "turn_type" in result
        assert "confidence" in result
        assert "emotional_signal" in result
        assert "reasoning" in result
        assert isinstance(result["confidence"], float)
        assert 0.0 <= result["confidence"] <= 1.0


class TestDisclosureDetection:
    """Test disclosure classification."""

    def test_explicit_feeling_statement(self, classifier):
        """Detect 'I feel' statement."""
        result = classifier.classify("I feel overwhelmed")
        assert result["turn_type"] == "disclosure"
        assert result["confidence"] > 0.5

    def test_exhaustion_disclosure(self, classifier):
        """Detect exhaustion markers."""
        result = classifier.classify("I'm so tired of things right now")
        assert result["turn_type"] == "disclosure"
        assert result["emotional_signal"] == "exhaustion"

    def test_grief_disclosure(self, classifier):
        """Detect grief markers."""
        result = classifier.classify("I lost my father last year")
        assert result["turn_type"] == "disclosure"
        assert result["emotional_signal"] == "grief"

    def test_stress_disclosure(self, classifier):
        """Detect stress markers."""
        result = classifier.classify("I'm overwhelmed with work pressure")
        assert result["turn_type"] == "disclosure"
        assert result["emotional_signal"] == "stress"


class TestGratitudeDetection:
    """Test gratitude classification."""

    def test_explicit_thanks(self, classifier):
        """Detect explicit thanks."""
        result = classifier.classify("Thank you for listening")
        assert result["turn_type"] == "gratitude"
        assert result["confidence"] > 0.7

    def test_appreciation(self, classifier):
        """Detect appreciation language."""
        result = classifier.classify("I appreciate your help")
        assert result["turn_type"] == "gratitude"

    def test_that_helped(self, classifier):
        """Detect 'that helped' pattern."""
        result = classifier.classify("That really helped me think about this")
        assert result["turn_type"] == "gratitude"


class TestMetaDetection:
    """Test meta-question classification."""

    def test_how_question(self, classifier):
        """Detect 'How do you' questions."""
        result = classifier.classify("How do you know what to say?")
        assert result["turn_type"] == "meta"

    def test_can_you_question(self, classifier):
        """Detect 'Can you' questions."""
        result = classifier.classify("Can you help me understand?")
        assert result["turn_type"] == "meta"

    def test_are_you_question(self, classifier):
        """Detect 'Are you' questions."""
        result = classifier.classify("Are you always this insightful?")
        assert result["turn_type"] == "meta"


class TestClosureDetection:
    """Test closure classification."""

    def test_goodbye(self, classifier):
        """Detect goodbye."""
        result = classifier.classify("Goodbye, thanks for talking")
        assert result["turn_type"] == "closure"

    def test_talk_soon(self, classifier):
        """Detect 'talk soon' pattern."""
        result = classifier.classify("I gotta go, but thanks")
        assert result["turn_type"] == "closure"


class TestCorrectionDetection:
    """Test correction classification."""

    def test_actually(self, classifier):
        """Detect 'actually' correction."""
        result = classifier.classify("Actually, I think I misspoke")
        assert result["turn_type"] == "correction"

    def test_wait(self, classifier):
        """Detect 'wait' correction."""
        result = classifier.classify("Wait, let me rephrase that")
        assert result["turn_type"] == "correction"


class TestEmotionalSignalDetection:
    """Test emotional signal extraction."""

    def test_exhaustion_signal(self, classifier):
        """Detect exhaustion signal."""
        result = classifier.classify("I'm exhausted")
        assert result["emotional_signal"] == "exhaustion"

    def test_grief_signal(self, classifier):
        """Detect grief signal."""
        result = classifier.classify("I'm mourning the loss")
        assert result["emotional_signal"] == "grief"

    def test_joy_signal(self, classifier):
        """Detect joy signal."""
        result = classifier.classify("I'm so happy about this!")
        assert result["emotional_signal"] == "joy"

    def test_isolation_signal(self, classifier):
        """Detect isolation signal."""
        result = classifier.classify("I feel so alone in this")
        assert result["emotional_signal"] == "isolation"

    def test_no_signal_for_neutral(self, classifier):
        """No emotional signal for neutral statements."""
        result = classifier.classify("How do you work?")
        assert result["emotional_signal"] is None


class TestConfidenceScoring:
    """Test confidence scoring."""

    def test_high_confidence_for_clear_markers(self, classifier):
        """Clear markers should have high confidence."""
        result = classifier.classify("Thank you so much for your help")
        assert result["confidence"] > 0.7

    def test_lower_confidence_for_ambiguous(self, classifier):
        """Ambiguous messages should have lower confidence."""
        result = classifier.classify("So")
        assert result["confidence"] < 0.7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
