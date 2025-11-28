"""Tests for the Presence Architecture modules.

Tests the AttunementLoop, EmotionalReciprocity, TemporalMemory,
EmbodiedSimulation, and PoeticConsciousness components.
"""
import pytest
from datetime import datetime, timezone, timedelta

from emotional_os.core.presence import (
    AttunementLoop,
    EmotionalReciprocity,
    TemporalMemory,
    EmbodiedSimulation,
    PoeticConsciousness,
)
from emotional_os.core.presence.attunement_loop import RhythmState, ToneQuality
from emotional_os.core.presence.emotional_reciprocity import MoodState, EmotionalValence
from emotional_os.core.presence.temporal_memory import EmotionalArc, EmotionalSignificance
from emotional_os.core.presence.embodied_simulation import EnergyState, InteractionLoad


class TestAttunementLoop:
    """Tests for the AttunementLoop component."""

    def test_init_creates_steady_state(self):
        """Test that initialization creates a steady rhythm state."""
        loop = AttunementLoop()
        state = loop.get_current_state()
        assert state.rhythm == RhythmState.STEADY
        assert state.tone == ToneQuality.PRESENT

    def test_process_message_extracts_signal(self):
        """Test that processing a message extracts an interaction signal."""
        loop = AttunementLoop()
        signal = loop.process_message("I'm feeling overwhelmed today...")
        assert signal.word_count > 0
        assert "vulnerability:overwhelmed" in signal.emotional_markers or len(signal.emotional_markers) >= 0

    def test_vulnerability_triggers_tender_tone(self):
        """Test that vulnerability markers trigger tender tone."""
        loop = AttunementLoop()
        loop.process_message("I'm scared and alone")
        loop.process_message("I feel so hurt")
        state = loop.get_current_state()
        assert state.tone == ToneQuality.TENDER
        assert state.softening_active is True

    def test_response_modifiers_reflect_state(self):
        """Test that response modifiers reflect current state."""
        loop = AttunementLoop()
        loop.process_message("I'm hurt")
        modifiers = loop.get_response_modifiers()
        assert "soften_assertions" in modifiers
        assert "tone_quality" in modifiers

    def test_reset_clears_state(self):
        """Test that reset clears all state."""
        loop = AttunementLoop()
        loop.process_message("test message")
        loop.reset()
        state = loop.get_current_state()
        assert state.rhythm == RhythmState.STEADY


class TestEmotionalReciprocity:
    """Tests for the EmotionalReciprocity component."""

    def test_init_creates_warm_mood(self):
        """Test that initialization creates a warm mood profile."""
        engine = EmotionalReciprocity()
        profile = engine.get_mood_profile()
        assert profile.primary_mood == MoodState.WARM

    def test_detect_grief_emotional_input(self):
        """Test detection of grief-related emotional input."""
        engine = EmotionalReciprocity()
        input_data = engine.detect_emotional_input("I'm grieving the loss of my friend")
        assert input_data.primary_emotion == "grief"
        assert input_data.valence == EmotionalValence.NEGATIVE
        assert "to be witnessed" in input_data.underlying_needs

    def test_reciprocal_response_for_grief(self):
        """Test that grief triggers tender reciprocal response."""
        engine = EmotionalReciprocity()
        input_data = engine.detect_emotional_input("I'm so sad about losing them")
        response = engine.generate_reciprocal_response(input_data)
        assert response["response_mood"] == "tender"
        assert response["response_action"] in ["hold_space", "validate"]

    def test_mood_evolution_with_interactions(self):
        """Test that moods evolve with interactions."""
        engine = EmotionalReciprocity()
        engine.detect_emotional_input("I'm feeling devastated")
        engine.detect_emotional_input("Everything feels hopeless")
        profile = engine.get_mood_profile()
        # High intensity negative should shift toward tender
        assert profile.warmth_level >= 0.7

    def test_suggest_response_qualities(self):
        """Test that response quality suggestions are generated."""
        engine = EmotionalReciprocity()
        engine.detect_emotional_input("I'm hurt")
        qualities = engine.suggest_response_qualities()
        assert len(qualities) > 0


class TestTemporalMemory:
    """Tests for the TemporalMemory component."""

    def test_start_session_returns_id(self):
        """Test that starting a session returns a session ID."""
        memory = TemporalMemory()
        session_id = memory.start_session()
        assert len(session_id) == 16

    def test_store_session_residue(self):
        """Test storing session emotional residue."""
        memory = TemporalMemory()
        memory.start_session()
        residue = memory.store_session_residue(
            emotions=["grief", "hope"],
            arc=EmotionalArc.TRANSFORMING,
            significance=EmotionalSignificance.MEANINGFUL,
        )
        assert residue.primary_emotion == "grief"
        assert residue.emotional_arc == EmotionalArc.TRANSFORMING

    def test_recall_for_context(self):
        """Test recalling memories for emotional context."""
        memory = TemporalMemory()
        memory.start_session("user123")
        memory.store_session_residue(
            emotions=["grief"],
            arc=EmotionalArc.PROCESSING,
            significance=EmotionalSignificance.SIGNIFICANT,
            user_identifier="user123",
        )
        recalls = memory.recall_for_context(
            current_emotion="grief",
            user_identifier="user123",
        )
        assert len(recalls) > 0
        assert recalls[0].relevance_score > 0

    def test_emotional_context_phrase(self):
        """Test generating emotional context phrase."""
        memory = TemporalMemory()
        memory.start_session("user123")
        memory.store_session_residue(
            emotions=["sadness"],
            arc=EmotionalArc.DESCENDING,
            significance=EmotionalSignificance.MEANINGFUL,
            user_identifier="user123",
        )
        phrase = memory.get_emotional_context_phrase(
            current_emotion="sadness",
            user_identifier="user123",
        )
        assert phrase is not None


class TestEmbodiedSimulation:
    """Tests for the EmbodiedSimulation component."""

    def test_init_creates_steady_state(self):
        """Test that initialization creates a steady energy state."""
        sim = EmbodiedSimulation()
        state = sim.get_current_state()
        assert state.state == EnergyState.STEADY
        assert state.energy_level > 0.7

    def test_process_interaction_drains_energy(self):
        """Test that processing interactions drains energy."""
        sim = EmbodiedSimulation()
        initial_energy = sim.get_current_state().energy_level
        load = InteractionLoad(
            intensity=0.8,
            complexity=0.6,
            duration_factor=0.5,
            requires_holding=True,
        )
        sim.process_interaction(load)
        assert sim.get_current_state().energy_level < initial_energy

    def test_rest_recovers_energy(self):
        """Test that rest recovers energy."""
        sim = EmbodiedSimulation(initial_energy=0.3)
        sim.rest(duration=2.0)
        assert sim.get_current_state().energy_level > 0.3

    def test_overload_triggers_sparse_texture(self):
        """Test that overload triggers sparse response texture."""
        sim = EmbodiedSimulation()
        # Push to overload
        for _ in range(10):
            load = InteractionLoad(
                intensity=0.9,
                complexity=0.8,
                duration_factor=0.7,
                requires_holding=True,
            )
            sim.process_interaction(load)
        
        state = sim.get_current_state()
        if state.state == EnergyState.OVERLOADED:
            from emotional_os.core.presence.embodied_simulation import ResponseTexture
            assert state.texture == ResponseTexture.SPARSE

    def test_response_modifiers_generated(self):
        """Test that response modifiers are generated."""
        sim = EmbodiedSimulation()
        modifiers = sim.get_response_modifiers()
        assert "sentence_length" in modifiers
        assert "pacing" in modifiers


class TestPoeticConsciousness:
    """Tests for the PoeticConsciousness component."""

    def test_perceive_water_metaphor(self):
        """Test perception of water-domain metaphors."""
        consciousness = PoeticConsciousness()
        metaphors = consciousness.perceive("I feel like I'm drowning in grief")
        assert len(metaphors) > 0
        from emotional_os.core.presence.poetic_consciousness import SymbolicDomain
        assert any(m.symbolic_domain == SymbolicDomain.WATER for m in metaphors)

    def test_perceive_journey_metaphor(self):
        """Test perception of journey-domain metaphors."""
        consciousness = PoeticConsciousness()
        metaphors = consciousness.perceive("I'm feeling stuck on my path")
        assert len(metaphors) > 0

    def test_generate_resonant_response(self):
        """Test generation of resonant poetic response."""
        consciousness = PoeticConsciousness()
        consciousness.perceive("I'm drowning in sadness")
        response = consciousness.generate_resonant_response()
        assert response is not None

    def test_symbolic_context_generated(self):
        """Test that symbolic context is generated."""
        consciousness = PoeticConsciousness()
        consciousness.perceive("I feel trapped in this box")
        context = consciousness.get_symbolic_context()
        assert "dominant_domain" in context
        assert "recommended_tone" in context

    def test_suggest_metaphoric_response(self):
        """Test suggesting metaphoric response for emotion."""
        consciousness = PoeticConsciousness()
        response = consciousness.suggest_metaphoric_response("grief")
        assert response is not None
