"""Tests for Frequency Reflection Module."""

import pytest
from emotional_os.core.firstperson.frequency_reflector import (
    FrequencyReflector,
    detect_theme,
    analyze_frequency,
    get_frequency_reflection,
)


class TestFrequencyReflector:
    """Test suite for frequency reflection."""

    @pytest.fixture
    def reflector(self):
        """Create a reflector instance for testing."""
        return FrequencyReflector()

    def test_detect_theme_family_conflict(self, reflector):
        """Test detection of family conflict theme."""
        text = "I'm angry with the kids again."
        theme = reflector.detect_theme(text)

        assert theme == "family_conflict"

    def test_detect_theme_work_stress(self, reflector):
        """Test detection of work stress theme."""
        text = "My boss was unreasonable in the meeting today."
        theme = reflector.detect_theme(text)

        assert theme == "work_stress"

    def test_detect_theme_relationship_tension(self, reflector):
        """Test detection of relationship tension theme."""
        text = "They keep belittling me and I feel so ignored."
        theme = reflector.detect_theme(text)

        assert theme == "relationship_tension"

    def test_detect_theme_no_match(self, reflector):
        """Test that no theme is detected for neutral input."""
        text = "I had coffee this morning."
        theme = reflector.detect_theme(text)

        assert theme is None

    def test_record_theme(self, reflector):
        """Test recording a theme."""
        text = "I'm angry with the kids."
        theme = reflector.record_theme(text)

        assert theme == "family_conflict"
        assert reflector.theme_counts["family_conflict"] == 1

    def test_theme_frequency_counting(self, reflector):
        """Test frequency counting across multiple inputs."""
        inputs = [
            "I'm angry with the kids.",
            "The kids are driving me crazy again.",
            "Family conflict is getting worse.",
        ]

        for text in inputs:
            reflector.record_theme(text)

        frequency = reflector.get_theme_frequency("family_conflict")
        assert frequency == 3

    def test_analyze_frequency_below_threshold(self, reflector):
        """Test that reflection doesn't trigger below threshold."""
        text = "I'm angry with the kids."
        analysis = reflector.analyze_frequency(text)

        assert analysis["detected_theme"] == "family_conflict"
        assert analysis["frequency"] == 1
        assert analysis["should_reflect"] is False  # threshold is 2

    def test_analyze_frequency_at_threshold(self, reflector):
        """Test that reflection triggers at threshold."""
        reflector.record_theme("I'm angry with the kids.")
        text = "Family conflict is back."
        analysis = reflector.analyze_frequency(text)

        assert analysis["frequency"] == 2
        assert analysis["should_reflect"] is True
        assert analysis["reflection"] is not None

    def test_generate_reflection_low_frequency(self, reflector):
        """Test reflection generation at frequency 2."""
        reflection = reflector.generate_frequency_reflection(
            "family_conflict", 2)

        assert reflection is not None
        assert "family conflict" in reflection.lower()
        assert "?" in reflection

    def test_generate_reflection_medium_frequency(self, reflector):
        """Test reflection generation at frequency 4."""
        reflection = reflector.generate_frequency_reflection(
            "family_conflict", 4)

        assert reflection is not None
        assert "family conflict" in reflection.lower()

    def test_generate_reflection_high_frequency(self, reflector):
        """Test reflection generation at frequency 5+."""
        reflection = reflector.generate_frequency_reflection(
            "family_conflict", 6)

        assert reflection is not None
        assert "family conflict" in reflection.lower()
        assert "recurring" in reflection.lower()

    def test_get_top_themes(self, reflector):
        """Test retrieval of top themes."""
        reflector.record_theme("I'm angry with the kids.")
        reflector.record_theme("Family conflict is back.")
        reflector.record_theme("Work stress is mounting.")
        reflector.record_theme("I'm tired from work.")

        top_themes = reflector.get_top_themes(limit=2)

        assert len(top_themes) <= 2
        # Should have at least one theme recorded
        assert len(top_themes) > 0

    def test_confidence_calculation(self, reflector):
        """Test confidence score calculation."""
        text = "I'm angry with the kids and my husband is frustrated too."
        analysis = reflector.analyze_frequency(text)

        confidence = analysis.get("confidence", 0)
        assert 0 <= confidence <= 1
        # Confidence is matching keywords / total keywords in pattern (11-12)
        # Text has 'kids' and 'husband' = 2/11 ≈ 0.18
        assert confidence > 0.1

    def test_module_level_detect_theme(self):
        """Test module-level detect_theme function."""
        text = "I'm angry with the kids."
        theme = detect_theme(text)

        assert theme == "family_conflict"

    def test_module_level_analyze_frequency(self):
        """Test module-level analyze_frequency function."""
        text = "I'm angry with the kids."
        analysis = analyze_frequency(text)

        assert analysis["detected_theme"] == "family_conflict"
        assert isinstance(analysis, dict)

    def test_module_level_get_frequency_reflection(self):
        """Test module-level get_frequency_reflection function."""
        # NOTE: Module-level functions use a global singleton reflector
        # that persists state across calls. First call with any theme
        # will record it (frequency=1), second call will reach threshold.

        # First occurrence - threshold is 2, so no reflection yet
        text1 = "I'm angry with the kids."
        reflection1 = get_frequency_reflection(text1)
        # After first call, frequency = 1, so no reflection
        assert reflection1 is None or isinstance(reflection1, str)

        # Second occurrence - should reflect (frequency=2)
        text2 = "Family conflict again."
        reflection2 = get_frequency_reflection(text2)
        # After second call, frequency >= 2, should have reflection
        assert reflection2 is not None
        assert isinstance(reflection2, str)


class TestFrequencyReflectionContexts:
    """Test real-world frequency contexts."""

    def test_repeated_family_conflict(self):
        """Test repeated family conflict pattern."""
        reflector = FrequencyReflector()

        inputs = [
            "I'm angry with the kids.",
            "They're fighting again.",
            "Family stress is mounting.",
        ]

        for text in inputs:
            reflector.record_theme(text)

        reflection = reflector.generate_frequency_reflection(
            "family_conflict", 3)
        assert "family conflict" in reflection.lower()

    def test_mixed_themes(self):
        """Test handling multiple different themes."""
        reflector = FrequencyReflector()

        reflector.record_theme("Work is stressing me out.")
        reflector.record_theme("My boss was unfair today.")
        reflector.record_theme("I'm angry with the kids.")

        top_themes = reflector.get_top_themes()
        assert len(top_themes) >= 2

    def test_theme_window_analysis(self):
        """Test recent theme analysis with window."""
        reflector = FrequencyReflector()

        # Add many entries
        for i in range(5):
            reflector.record_theme("I'm angry with the kids.")

        reflector.record_theme("Work is stressful.")
        reflector.record_theme("Family conflict strikes again.")

        # Check recent window
        recent_family = reflector.get_theme_frequency(
            "family_conflict", window=2)
        assert recent_family == 1  # Only last family_conflict in last 2

    def test_case_insensitivity(self):
        """Test that theme detection is case-insensitive."""
        reflector = FrequencyReflector()

        text1 = "I'm ANGRY with the KIDS."
        text2 = "I'm angry with the kids."
        text3 = "I'm Angry With The Kids."

        theme1 = reflector.detect_theme(text1)
        theme2 = reflector.detect_theme(text2)
        theme3 = reflector.detect_theme(text3)

        assert theme1 == theme2 == theme3 == "family_conflict"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
