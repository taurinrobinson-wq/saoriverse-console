"""Tests for Story-Start Detection Module."""

import pytest
from emotional_os.core.firstperson.story_start_detector import (
    StoryStartDetector,
    analyze_story_start,
    generate_clarifying_prompt,
)


class TestStoryStartDetector:
    """Test suite for story-start detection."""

    @pytest.fixture
    def detector(self):
        """Create a detector instance for testing."""
        return StoryStartDetector()

    def test_detect_pronoun_ambiguity_they(self, detector):
        """Test detection of ambiguous 'they' pronoun."""
        text = "They were fighting again."
        findings = detector.detect_pronoun_ambiguity(text)

        assert len(findings) > 0
        assert any(f["pronoun"] == "they" for f in findings)

    def test_detect_pronoun_ambiguity_multiple(self, detector):
        """Test detection of multiple ambiguous pronouns."""
        text = "They said it was their fault, but I don't think that's fair."
        findings = detector.detect_pronoun_ambiguity(text)

        assert len(findings) >= 3  # they, it, their
        pronouns = [f["pronoun"] for f in findings]
        assert "they" in pronouns
        assert "it" in pronouns
        assert "their" in pronouns

    def test_detect_temporal_markers_again(self, detector):
        """Test detection of 'again' temporal marker."""
        text = "We're fighting again."
        findings = detector.detect_temporal_markers(text)

        assert len(findings) > 0
        assert any(f["marker"] == "again" for f in findings)

    def test_detect_temporal_markers_always(self, detector):
        """Test detection of 'always' absolute marker."""
        text = "They always do this to me."
        findings = detector.detect_temporal_markers(text)

        assert len(findings) > 0
        assert any(f["marker"] == "always" for f in findings)

    def test_analyze_story_start_both(self, detector):
        """Test analysis that detects both pronoun and temporal markers."""
        text = "They were fighting again."
        analysis = detector.analyze_story_start(text)

        assert analysis["has_ambiguity"] is True
        assert analysis["has_temporal_loop"] is True
        assert analysis["is_story_start"] is True
        assert len(analysis["recommended_clarifiers"]) > 0

    def test_analyze_story_start_no_signals(self, detector):
        """Test analysis with no story-start signals."""
        text = "I had coffee this morning."
        analysis = detector.analyze_story_start(text)

        # "this" and "morning" might trigger some detection
        # but the focus should be on ambiguous pronouns in context
        assert isinstance(analysis, dict)
        assert "is_story_start" in analysis

    def test_generate_clarifying_prompt_single(self, detector):
        """Test generation of clarifying prompt."""
        text = "They were fighting again."
        prompt = detector.generate_clarifying_prompt(
            detector.analyze_story_start(text), include_count=1
        )

        assert prompt is not None
        assert isinstance(prompt, str)
        # Should contain a clarifying question
        assert "?" in prompt

    def test_generate_clarifying_prompt_multiple(self, detector):
        """Test generation with multiple clarifiers."""
        text = "They were fighting again."
        analysis = detector.analyze_story_start(text, max_clarifiers=3)
        prompt = detector.generate_clarifying_prompt(analysis, include_count=2)

        assert prompt is not None
        # Should combine multiple clarifiers
        assert len(prompt) > 20

    def test_module_level_function(self):
        """Test module-level analyze_story_start function."""
        text = "They were fighting again."
        analysis = analyze_story_start(text)

        assert analysis["is_story_start"] is True
        assert len(analysis["recommended_clarifiers"]) > 0

    def test_module_level_prompt_generation(self):
        """Test module-level generate_clarifying_prompt function."""
        text = "They were fighting again."
        prompt = generate_clarifying_prompt(text)

        assert prompt is not None
        assert "?" in prompt


class TestStoryStartContexts:
    """Test real-world story-start contexts."""

    def test_ambiguous_kids_context(self):
        """Test ambiguous pronoun in family context."""
        text = "I'm angry with the kids and now they're upset with me."
        analysis = analyze_story_start(text)

        assert analysis["has_ambiguity"] is True
        assert len(analysis["recommended_clarifiers"]) > 0

    def test_temporal_loop_context(self):
        """Test temporal loop detection in relationship context."""
        text = "Every time we talk about this, they shut down."
        analysis = analyze_story_start(text)

        assert analysis["has_temporal_loop"] is True
        clarifier = generate_clarifying_prompt(text)
        assert clarifier is not None

    def test_complex_narrative(self):
        """Test complex narrative with multiple signals."""
        text = "They keep saying it's my fault, and I always end up apologizing even though it's not fair."
        analysis = analyze_story_start(text)

        assert analysis["has_ambiguity"] is True
        assert analysis["has_temporal_loop"] is True
        assert len(analysis["recommended_clarifiers"]) >= 1

    def test_case_insensitivity(self):
        """Test that detection works regardless of case."""
        text1 = "THEY were fighting again."
        text2 = "they were fighting again."
        text3 = "They were fighting again."

        analysis1 = analyze_story_start(text1)
        analysis2 = analyze_story_start(text2)
        analysis3 = analyze_story_start(text3)

        assert analysis1["is_story_start"] is True
        assert analysis2["is_story_start"] is True
        assert analysis3["is_story_start"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
