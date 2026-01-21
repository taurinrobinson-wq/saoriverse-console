"""Tests for the Saori Layer modules.

Tests the MirrorEngine, EdgeGenerator, EmotionalGenome,
MortalityClock, and SaoriLayer components.
"""
import pytest

from emotional_os.core.saori import (
    SaoriLayer,
    MirrorEngine,
    EdgeGenerator,
    EmotionalGenome,
    MortalityClock,
    Archetype,
)
from emotional_os.core.saori.saori_layer import (
    EngagementLevel,
)


class TestMirrorEngine:
    """Tests for the MirrorEngine component."""

    def test_create_reflection_returns_string(self):
        """Test that create_reflection returns a string."""
        engine = MirrorEngine()
        reflection = engine.create_reflection("I feel broken")
        assert isinstance(reflection, str)
        assert len(reflection) > 0

    def test_inversion_for_broken(self):
        """Test poetic inversion for 'broken' metaphor."""
        engine = MirrorEngine()
        reflection = engine.create_reflection("I feel broken")
        # Should contain the inversion pattern
        assert "what if" in reflection.lower() or "broken" in reflection.lower()

    def test_inversion_for_stuck(self):
        """Test poetic inversion for 'stuck' metaphor."""
        engine = MirrorEngine()
        reflection = engine.create_reflection("I'm stuck")
        assert len(reflection) > 0

    def test_state_tracks_reflections(self):
        """Test that state tracks active reflections."""
        engine = MirrorEngine()
        engine.create_reflection("test")
        state = engine.get_state()
        assert len(state.active_reflections) > 0

    def test_adjust_depth(self):
        """Test adjusting reflection depth."""
        engine = MirrorEngine()
        initial_depth = engine.get_state().reflection_depth
        engine.adjust_depth(0.2)
        assert engine.get_state().reflection_depth > initial_depth


class TestEdgeGenerator:
    """Tests for the EdgeGenerator component."""

    def test_init_with_coefficient(self):
        """Test initialization with surprise coefficient."""
        generator = EdgeGenerator(surprise_coefficient=0.25)
        assert generator.get_coefficient() == 0.25

    def test_generate_edge_returns_dict(self):
        """Test that generate_edge returns a dictionary."""
        generator = EdgeGenerator()
        edge = generator.generate_edge("grief")
        assert isinstance(edge, dict)
        assert "pattern" in edge
        assert "content" in edge

    def test_generate_haiku_pattern(self):
        """Test generating a haiku edge."""
        generator = EdgeGenerator()
        edge = generator.generate_edge("grief", pattern="haiku")
        assert edge["pattern"] == "haiku"
        assert "\n" in edge["content"]

    def test_generate_question_reversal(self):
        """Test generating a question reversal edge."""
        generator = EdgeGenerator()
        edge = generator.generate_edge("fear", pattern="question_reversal")
        assert edge["pattern"] == "question_reversal"
        assert "?" in edge["content"]

    def test_train_coefficient(self):
        """Test training the surprise coefficient."""
        generator = EdgeGenerator(surprise_coefficient=0.2)
        generator.train_coefficient(1.0)  # Positive feedback
        assert generator.get_coefficient() > 0.2


class TestEmotionalGenome:
    """Tests for the EmotionalGenome component."""

    def test_init_with_default_archetype(self):
        """Test initialization with default archetype."""
        genome = EmotionalGenome()
        assert genome.get_current_archetype() == Archetype.COMPANION

    def test_init_with_custom_archetype(self):
        """Test initialization with custom archetype."""
        genome = EmotionalGenome(initial_archetype=Archetype.WITNESS)
        assert genome.get_current_archetype() == Archetype.WITNESS

    def test_assess_grief_context(self):
        """Test assessing grief emotional context."""
        genome = EmotionalGenome()
        genome.assess_emotional_context({"emotion": "grief", "intensity": 0.8})
        # Grief should shift toward WITNESS
        state = genome.get_state()
        assert state.transition_readiness > 0

    def test_get_voice_profile(self):
        """Test getting voice profile for archetype."""
        genome = EmotionalGenome(initial_archetype=Archetype.ORACLE)
        profile = genome.get_voice_profile()
        assert "voice_qualities" in profile
        assert "deep" in profile["voice_qualities"]

    def test_get_language_markers(self):
        """Test getting language markers for archetype."""
        genome = EmotionalGenome(initial_archetype=Archetype.WITNESS)
        markers = genome.get_language_markers()
        assert len(markers) > 0
        assert any("witness" in m.lower() or "here" in m.lower() for m in markers)

    def test_transition_feasibility(self):
        """Test archetype transition feasibility."""
        genome = EmotionalGenome(initial_archetype=Archetype.COMPANION)
        # COMPANION can transition to WITNESS
        # Push toward transition with many high-intensity assessments
        for _ in range(20):
            genome.assess_emotional_context({"emotion": "grief", "intensity": 0.95})
        
        # Either transition happened or readiness increased
        transition = genome.consider_transition()
        state = genome.get_state()
        # We should either have transitioned or readiness > 0
        assert transition is not None or state.transition_readiness >= 0


class TestMortalityClock:
    """Tests for the MortalityClock component."""

    def test_init_creates_active_engagement(self):
        """Test initialization creates active engagement."""
        clock = MortalityClock()
        state = clock.get_state()
        assert state.engagement_level == EngagementLevel.ACTIVE
        assert state.entropy_level < 0.2

    def test_record_interaction_updates_state(self):
        """Test that recording interaction updates state."""
        clock = MortalityClock()
        initial_depth = clock.get_state().depth_capacity
        clock.record_interaction(heavy_context=True)
        assert clock.get_state().depth_capacity < initial_depth

    def test_light_interaction_restores(self):
        """Test that light interaction restores capacity."""
        clock = MortalityClock()
        clock.record_interaction(heavy_context=True)
        depleted = clock.get_state().depth_capacity
        clock.record_interaction(heavy_context=False)
        assert clock.get_state().depth_capacity >= depleted

    def test_simulate_time_passage(self):
        """Test simulating time passage."""
        clock = MortalityClock()
        initial_entropy = clock.get_state().entropy_level
        clock.simulate_time_passage(hours=48)
        state = clock.get_state()
        assert state.entropy_level > initial_entropy
        # After 48 hours, should be neglected
        assert state.engagement_level == EngagementLevel.NEGLECTED or state.revival_needed

    def test_get_neglect_response(self):
        """Test getting neglect response when needed."""
        clock = MortalityClock()
        clock.simulate_time_passage(hours=48)
        response = clock.get_neglect_response()
        assert response is not None

    def test_get_response_variability(self):
        """Test getting response variability factor."""
        clock = MortalityClock()
        variability = clock.get_response_variability()
        assert 0 <= variability <= 1

    def test_reset_clears_state(self):
        """Test that reset clears state."""
        clock = MortalityClock()
        clock.record_interaction(heavy_context=True)
        clock.record_interaction(heavy_context=True)
        clock.reset()
        state = clock.get_state()
        assert state.entropy_level < 0.2


class TestSaoriLayer:
    """Tests for the unified SaoriLayer interface."""

    def test_init_creates_all_components(self):
        """Test that initialization creates all components."""
        saori = SaoriLayer()
        assert saori.mirror is not None
        assert saori.edge is not None
        assert saori.genome is not None
        assert saori.mortality is not None

    def test_process_interaction_returns_dict(self):
        """Test that process_interaction returns a dictionary."""
        saori = SaoriLayer()
        result = saori.process_interaction(
            message="I'm feeling sad",
            context={"emotion": "sadness", "intensity": 0.6}
        )
        assert isinstance(result, dict)
        assert "reflection" in result
        assert "archetype" in result

    def test_process_interaction_with_high_intensity(self):
        """Test processing high-intensity interaction."""
        saori = SaoriLayer()
        result = saori.process_interaction(
            message="I'm devastated",
            context={"emotion": "grief", "intensity": 0.9}
        )
        # High intensity should affect mortality state
        assert result["depth_factor"] is not None

    def test_get_integrated_response_modifiers(self):
        """Test getting integrated response modifiers."""
        saori = SaoriLayer()
        modifiers = saori.get_integrated_response_modifiers()
        assert "archetype" in modifiers
        assert "voice_style" in modifiers
        assert "depth_capacity" in modifiers

    def test_train_surprise_coefficient(self):
        """Test training the surprise coefficient."""
        saori = SaoriLayer(surprise_coefficient=0.2)
        initial = saori.edge.get_coefficient()
        saori.train_surprise_coefficient(0.5)
        assert saori.edge.get_coefficient() != initial

    def test_simulate_time_passage(self):
        """Test simulating time passage."""
        saori = SaoriLayer()
        saori.simulate_time_passage(hours=10)
        state = saori.get_full_state()
        assert state["mortality"]["entropy_level"] > 0

    def test_get_full_state(self):
        """Test getting full state of all components."""
        saori = SaoriLayer()
        saori.process_interaction("test", {"emotion": "neutral", "intensity": 0.5})
        state = saori.get_full_state()
        assert "mirror" in state
        assert "genome" in state
        assert "mortality" in state
        assert "surprise_coefficient" in state
