"""Tests for the Generative Tension modules.

Tests the SurpriseEngine, ChallengeEngine, SubversionEngine,
CreationEngine, and GenerativeTension components.
"""
import pytest

from emotional_os.core.tension import (
    GenerativeTension,
    SurpriseEngine,
    ChallengeEngine,
    SubversionEngine,
    CreationEngine,
)
from emotional_os.core.tension.generative_tension import (
    TensionType,
    DivergenceStyle,
    ChallengeLevel,
)


class TestSurpriseEngine:
    """Tests for the SurpriseEngine component."""

    def test_init_with_coefficient(self):
        """Test initialization with surprise coefficient."""
        engine = SurpriseEngine(surprise_coefficient=0.3)
        assert engine.get_surprise_coefficient() == 0.3

    def test_generate_divergence_returns_output(self):
        """Test that generate_divergence returns a TensionOutput."""
        engine = SurpriseEngine()
        output = engine.generate_divergence("I'm feeling stuck")
        assert output.tension_type == TensionType.SURPRISE
        assert len(output.content) > 0

    def test_divergence_with_emotion(self):
        """Test divergence generation with specified emotion."""
        engine = SurpriseEngine()
        output = engine.generate_divergence("I'm feeling sad", emotion="sadness")
        assert output.content is not None

    def test_divergence_with_style(self):
        """Test divergence generation with specified style."""
        engine = SurpriseEngine()
        output = engine.generate_divergence(
            "test message",
            style=DivergenceStyle.TEMPORAL
        )
        assert output.content is not None

    def test_set_surprise_coefficient(self):
        """Test setting surprise coefficient."""
        engine = SurpriseEngine()
        engine.set_surprise_coefficient(0.5)
        assert engine.get_surprise_coefficient() == 0.5

    def test_coefficient_capped_at_bounds(self):
        """Test that coefficient is capped at bounds."""
        engine = SurpriseEngine()
        engine.set_surprise_coefficient(1.5)
        assert engine.get_surprise_coefficient() == 1.0
        engine.set_surprise_coefficient(-0.5)
        assert engine.get_surprise_coefficient() == 0.0


class TestChallengeEngine:
    """Tests for the ChallengeEngine component."""

    def test_detect_absolutism_pattern(self):
        """Test detection of absolutism pattern."""
        engine = ChallengeEngine()
        pattern = engine.detect_challenge_opportunity("I always fail at everything")
        assert pattern is not None
        assert pattern[0] == "absolutism"

    def test_detect_avoidance_pattern(self):
        """Test detection of avoidance pattern."""
        engine = ChallengeEngine()
        pattern = engine.detect_challenge_opportunity("It's just fine, whatever")
        assert pattern is not None

    def test_generate_gentle_challenge(self):
        """Test generating a gentle challenge."""
        engine = ChallengeEngine()
        output = engine.generate_challenge(
            "I never do anything right",
            level=ChallengeLevel.GENTLE,
            pattern_info=("absolutism", "never")
        )
        assert output.tension_type == TensionType.CHALLENGE
        assert output.intensity < 0.5

    def test_generate_moderate_challenge(self):
        """Test generating a moderate challenge."""
        engine = ChallengeEngine()
        output = engine.generate_challenge(
            "I can't do this",
            level=ChallengeLevel.MODERATE,
            pattern_info=("absolutism", "can't")
        )
        assert output.intensity >= 0.5

    def test_generate_deep_challenge(self):
        """Test generating a deep challenge."""
        engine = ChallengeEngine()
        output = engine.generate_challenge(
            "This always happens",
            level=ChallengeLevel.DEEP,
            pattern_info=("absolutism", "always")
        )
        assert output.intensity >= 0.7


class TestSubversionEngine:
    """Tests for the SubversionEngine component."""

    def test_reframe_falling_metaphor(self):
        """Test reframing the 'falling' metaphor."""
        engine = SubversionEngine()
        output = engine.reframe_metaphor("I feel like I'm falling apart")
        assert output is not None
        assert "falling" in output.content.lower()

    def test_reframe_broken_metaphor(self):
        """Test reframing the 'broken' metaphor."""
        engine = SubversionEngine()
        output = engine.reframe_metaphor("I feel broken")
        assert output is not None
        assert output.tension_type == TensionType.SUBVERSION

    def test_surface_avoided_metaphor(self):
        """Test surfacing avoided metaphors."""
        engine = SubversionEngine()
        output = engine.surface_avoided_metaphor()
        assert output is not None
        assert "?" in output.content  # Should be a question

    def test_surface_nuance_for_anger(self):
        """Test surfacing nuance underneath anger."""
        engine = SubversionEngine()
        output = engine.surface_nuance("anger")
        assert output is not None
        # Should mention underlying emotions

    def test_poetic_inversion(self):
        """Test poetic inversion of statement."""
        engine = SubversionEngine()
        result = engine.poetic_inversion("I can't do this")
        assert "can't" not in result.lower() or "learning" in result.lower()


class TestCreationEngine:
    """Tests for the CreationEngine component."""

    def test_generate_question_for_grief(self):
        """Test generating a question for grief context."""
        engine = CreationEngine()
        output = engine.generate_initiative(
            emotion="grief",
            form=CreationEngine.CreativeForm.QUESTION
        )
        assert output.tension_type == TensionType.CREATION
        assert "?" in output.content

    def test_generate_haiku(self):
        """Test generating a haiku."""
        engine = CreationEngine()
        output = engine.generate_initiative(
            emotion="grief",
            form=CreationEngine.CreativeForm.HAIKU
        )
        assert output is not None
        # Haiku has line breaks
        assert "\n" in output.content

    def test_generate_invitation(self):
        """Test generating an invitation."""
        engine = CreationEngine()
        output = engine.generate_initiative(
            emotion="fear",
            form=CreationEngine.CreativeForm.INVITATION
        )
        assert output is not None

    def test_generate_metaphor_for_joy(self):
        """Test generating a metaphor for joy."""
        engine = CreationEngine()
        output = engine.generate_initiative(
            emotion="joy",
            form=CreationEngine.CreativeForm.METAPHOR
        )
        assert output is not None

    def test_generate_haiku_for_context(self):
        """Test generating haiku for specific context."""
        engine = CreationEngine()
        haiku = engine.generate_haiku_for_context({"primary_emotion": "peace"})
        assert haiku is not None


class TestGenerativeTension:
    """Tests for the unified GenerativeTension interface."""

    def test_init_creates_all_engines(self):
        """Test that initialization creates all engines."""
        tension = GenerativeTension()
        assert tension.surprise is not None
        assert tension.challenge is not None
        assert tension.subversion is not None
        assert tension.creation is not None

    def test_generate_tensions_with_challenge_pattern(self):
        """Test generating tensions when challenge pattern exists."""
        tension = GenerativeTension()
        outputs = tension.generate_tensions(
            message="I always fail",
            emotion="sadness"
        )
        # Should detect the "always" pattern
        has_challenge = any(o.tension_type == TensionType.CHALLENGE for o in outputs)
        assert has_challenge

    def test_generate_tensions_with_metaphor(self):
        """Test generating tensions when metaphor exists."""
        tension = GenerativeTension()
        outputs = tension.generate_tensions(
            message="I'm falling apart",
            emotion="grief"
        )
        # Should detect the "falling" metaphor
        has_subversion = any(o.tension_type == TensionType.SUBVERSION for o in outputs)
        assert has_subversion

    def test_get_single_tension(self):
        """Test getting a single specific tension type."""
        tension = GenerativeTension()
        output = tension.get_single_tension(
            message="I'm stuck",
            tension_type=TensionType.SURPRISE,
            emotion="frustration"
        )
        assert output is not None
        assert output.tension_type == TensionType.SURPRISE

    def test_integrate_tensions(self):
        """Test integrating tensions into base response."""
        tension = GenerativeTension()
        
        base = "I hear you."
        outputs = [
            tension.surprise.generate_divergence("test", "sadness"),
            tension.challenge.generate_challenge("I can't", pattern_info=("absolutism", "can't")),
        ]
        
        result = tension.integrate_tensions(base, outputs)
        assert "I hear you" in result
        assert len(result) > len(base)
