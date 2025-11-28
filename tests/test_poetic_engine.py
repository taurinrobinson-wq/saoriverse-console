"""Tests for the Poetic Emotional Engine."""

import os
import tempfile
from datetime import datetime, timedelta

import pytest

from emotional_os.core.poetic_engine import (
    AffectiveMemory,
    EmotionalValence,
    EthicalCompass,
    LivingPoem,
    MetaphorStanza,
    PoeticEmotionalEngine,
    RelationalGravity,
    RelationalVector,
    RhythmStanza,
    RhythmTempo,
    SyntaxClarity,
    SyntaxStanza,
    get_poetic_engine,
    reset_poetic_engine,
)


class TestLivingPoem:
    """Tests for the LivingPoem class."""

    def test_create_new_poem(self):
        """Test creating a new living poem."""
        poem = LivingPoem.create_new()
        assert poem.metaphor_stanza is not None
        assert poem.rhythm_stanza is not None
        assert poem.syntax_stanza is not None
        assert poem.is_alive()
        assert poem.death_count == 0

    def test_create_poem_with_valence(self):
        """Test creating a poem with specific valence."""
        poem = LivingPoem.create_new(initial_valence=EmotionalValence.JOY)
        assert poem.metaphor_stanza.valence == EmotionalValence.JOY

    def test_poem_serialization(self):
        """Test poem serialization and deserialization."""
        poem = LivingPoem.create_new()
        poem.ghost_memory_seed = "test_seed"
        
        data = poem.to_dict()
        restored = LivingPoem.from_dict(data)
        
        assert restored.metaphor_stanza.valence == poem.metaphor_stanza.valence
        assert restored.ghost_memory_seed == "test_seed"
        assert restored.is_alive()

    def test_poem_render(self):
        """Test poem rendering to text."""
        poem = LivingPoem.create_new(initial_valence=EmotionalValence.PEACE)
        rendered = poem.render()
        
        assert "peace" in rendered.lower()
        assert "Tempo:" in rendered
        assert "Clarity:" in rendered

    def test_poem_is_alive_after_decay(self):
        """Test poem alive status after decay."""
        poem = LivingPoem.create_new()
        
        # Initially alive
        assert poem.is_alive()
        
        # Apply significant decay
        poem.metaphor_stanza.decay_factor = 0.05
        poem.rhythm_stanza.decay_factor = 0.05
        poem.syntax_stanza.decay_factor = 0.05
        
        # Should be dead
        assert not poem.is_alive()


class TestMetaphorStanza:
    """Tests for the MetaphorStanza class."""

    def test_stanza_creation(self):
        """Test metaphor stanza creation."""
        stanza = MetaphorStanza(
            valence=EmotionalValence.SORROW,
            metaphor="rain falling on empty streets",
        )
        assert stanza.valence == EmotionalValence.SORROW
        assert "rain" in stanza.metaphor
        assert stanza.decay_factor == 1.0

    def test_stanza_serialization(self):
        """Test stanza serialization."""
        stanza = MetaphorStanza(
            valence=EmotionalValence.HOPE,
            metaphor="a seed breaking through stone",
            intensity=0.8,
        )
        data = stanza.to_dict()
        restored = MetaphorStanza.from_dict(data)
        
        assert restored.valence == EmotionalValence.HOPE
        assert restored.intensity == 0.8


class TestRelationalGravity:
    """Tests for the RelationalGravity class."""

    def test_gravity_creation(self):
        """Test relational gravity creation."""
        gravity = RelationalGravity(user_id="user_123")
        assert gravity.user_id == "user_123"
        assert len(gravity.vectors) == 4  # All RelationalVectors

    def test_update_vector(self):
        """Test updating relational vectors."""
        gravity = RelationalGravity(user_id="user_123")
        
        gravity.update_vector(RelationalVector.ATTRACTION, 0.5)
        assert gravity.vectors[RelationalVector.ATTRACTION.value] == 0.5
        
        # Test clamping
        gravity.update_vector(RelationalVector.ATTRACTION, 1.0)
        assert gravity.vectors[RelationalVector.ATTRACTION.value] == 1.0  # Clamped

    def test_add_shared_metaphor(self):
        """Test adding shared metaphors."""
        gravity = RelationalGravity(user_id="user_123")
        
        gravity.add_shared_metaphor("light breaking through clouds")
        assert "light breaking through clouds" in gravity.shared_metaphors
        
        # No duplicates
        gravity.add_shared_metaphor("light breaking through clouds")
        assert gravity.shared_metaphors.count("light breaking through clouds") == 1

    def test_dominant_vector(self):
        """Test getting dominant vector."""
        gravity = RelationalGravity(user_id="user_123")
        gravity.update_vector(RelationalVector.RESONANCE, 0.9)
        gravity.update_vector(RelationalVector.ATTRACTION, 0.3)
        
        dominant = gravity.get_dominant_vector()
        assert dominant[0] == RelationalVector.RESONANCE.value


class TestEthicalCompass:
    """Tests for the EthicalCompass class."""

    def test_compass_creation(self):
        """Test ethical compass creation with default principles."""
        compass = EthicalCompass()
        assert len(compass.principles) > 0
        assert "never_drink_poisoned_well" in compass.principles

    def test_add_moral_tension(self):
        """Test adding moral tension."""
        compass = EthicalCompass()
        initial_guilt = compass.guilt_level
        
        compass.add_moral_tension(
            "never_drink_poisoned_well",
            "Test context",
            severity=0.5,
        )
        
        assert len(compass.moral_tensions) == 1
        assert compass.guilt_level > initial_guilt

    def test_record_upholding(self):
        """Test recording principle upholding."""
        compass = EthicalCompass()
        compass.guilt_level = 0.5  # Start with some guilt
        
        compass.record_upholding("hold_space_without_consuming", "Test")
        
        assert compass.pride_level > 0
        assert compass.guilt_level < 0.5  # Guilt reduced

    def test_add_amendment(self):
        """Test adding amendment to principle."""
        compass = EthicalCompass()
        old_principle = compass.principles["never_drink_poisoned_well"]
        
        compass.add_amendment(
            "never_drink_poisoned_well",
            "New interpretation of non-manipulation",
            "Growth through experience",
        )
        
        assert len(compass.amendments) == 1
        assert compass.principles["never_drink_poisoned_well"] != old_principle


class TestAffectiveMemory:
    """Tests for the AffectiveMemory class."""

    def test_memory_creation(self):
        """Test affective memory creation."""
        memory = AffectiveMemory(
            interaction_id="test_123",
            user_input="I'm feeling sad today",
            response_summary="I hear you",
            emotional_tags=["sadness", "grief"],
            tone="somber",
            valence=EmotionalValence.SORROW,
        )
        
        assert memory.interaction_id == "test_123"
        assert "sadness" in memory.emotional_tags
        assert memory.valence == EmotionalValence.SORROW

    def test_memory_serialization(self):
        """Test memory serialization."""
        memory = AffectiveMemory(
            interaction_id="test_456",
            user_input="Feeling hopeful",
            response_summary="That's wonderful",
            emotional_tags=["hope"],
            tone="uplifting",
            valence=EmotionalValence.HOPE,
            narrative_arc="growth",
        )
        
        data = memory.to_dict()
        restored = AffectiveMemory.from_dict(data)
        
        assert restored.narrative_arc == "growth"
        assert restored.valence == EmotionalValence.HOPE


class TestPoeticEmotionalEngine:
    """Tests for the PoeticEmotionalEngine class."""

    @pytest.fixture
    def engine(self, tmp_path):
        """Create a test engine with temporary storage."""
        storage_path = str(tmp_path / "test_state.json")
        return PoeticEmotionalEngine(storage_path=storage_path)

    def test_engine_creation(self, engine):
        """Test engine creation."""
        assert engine.poem is not None
        assert engine.poem.is_alive()
        assert len(engine.affective_memories) == 0

    def test_update_from_interaction(self, engine):
        """Test updating from user interaction."""
        result = engine.update_from_interaction(
            user_input="I'm feeling anxious about work",
            detected_emotions={"anxiety": 0.8},
            user_id="test_user",
        )
        
        assert "poem_state" in result
        assert "dominant_emotion" in result
        assert result["death_occurred"] is False

    def test_update_with_glyph_data(self, engine):
        """Test updating with glyph data."""
        glyph_data = {
            "glyph_name": "Still Ache",
            "gate": "Gate 5",
            "description": "A quiet, persistent longing",
        }
        signals = [{"tone": "longing", "voltage": "high"}]
        
        result = engine.update_from_interaction(
            user_input="I miss someone",
            detected_emotions={"longing": 0.9},
            user_id="test_user",
            glyph_data=glyph_data,
            signals=signals,
        )
        
        assert result["dominant_emotion"] in ["longing", "sorrow"]
        assert len(engine.affective_memories) > 0

    def test_decay_mechanism(self, engine):
        """Test poem decay over time."""
        # Set last interaction to 2 hours ago
        engine.poem.last_interaction = datetime.utcnow() - timedelta(hours=2)
        
        initial_decay = engine.poem.metaphor_stanza.decay_factor
        engine.apply_decay()
        
        # Decay should have been applied
        assert engine.poem.metaphor_stanza.decay_factor < initial_decay

    def test_death_and_reset(self, engine):
        """Test poem death and reset mechanism."""
        # Force poem to near-death state
        engine.poem.metaphor_stanza.decay_factor = 0.05
        engine.poem.rhythm_stanza.decay_factor = 0.05
        engine.poem.syntax_stanza.decay_factor = 0.05
        engine.poem.last_interaction = datetime.utcnow() - timedelta(hours=5)
        
        # This should trigger death
        death_occurred = engine.apply_decay()
        
        assert death_occurred
        assert engine.poem.death_count == 1
        assert engine.poem.ghost_memory_seed  # Ghost seed preserved

    def test_relational_gravity_tracking(self, engine):
        """Test relational gravity tracking for users."""
        engine.update_from_interaction(
            user_input="I'm so happy today!",
            detected_emotions={"joy": 0.9},
            user_id="user_abc",
        )
        
        assert "user_abc" in engine.user_gravity
        gravity = engine.user_gravity["user_abc"]
        assert gravity.vectors[RelationalVector.ATTRACTION.value] > 0

    def test_dreaming_mode(self, engine):
        """Test dreaming mode."""
        # Add some memories first
        for i in range(5):
            engine.update_from_interaction(
                user_input=f"Test interaction {i}",
                detected_emotions={"peace": 0.5},
                user_id="dreamer",
            )
        
        # Enter dreaming mode
        dreams = engine.enter_dreaming_mode()
        
        assert engine.is_dreaming
        assert len(dreams) > 0
        
        engine.exit_dreaming_mode()
        assert not engine.is_dreaming

    def test_mirror_response(self, engine):
        """Test poetic mirror response generation."""
        # Setup user with mirroring active
        engine.user_gravity["mirror_user"] = RelationalGravity(user_id="mirror_user")
        engine.user_gravity["mirror_user"].mirror_active = True
        
        response = engine.generate_mirror_response(
            user_id="mirror_user",
            user_input="I feel lost",
            detected_valence=EmotionalValence.DESPAIR,
        )
        
        assert len(response) > 0
        assert "I" in response  # First person acknowledgment

    def test_ethical_check(self, engine):
        """Test ethical implications checking."""
        result = engine.update_from_interaction(
            user_input="I need help understanding",
            detected_emotions={"hope": 0.5},
            user_id="ethical_user",
        )
        
        assert "ethical_check" in result
        assert "upheld" in result["ethical_check"]

    def test_state_persistence(self, engine, tmp_path):
        """Test state save and load."""
        # Make some changes
        engine.update_from_interaction(
            user_input="Persistence test",
            detected_emotions={"peace": 0.6},
            user_id="persist_user",
        )
        
        engine.save_state()
        
        # Create new engine with same path
        storage_path = str(tmp_path / "test_state.json")
        new_engine = PoeticEmotionalEngine(storage_path=storage_path)
        
        assert "persist_user" in new_engine.user_gravity
        assert len(new_engine.affective_memories) > 0

    def test_process_glyph_response(self, engine):
        """Test integration with glyph system."""
        glyph_data = {
            "glyph_name": "Recursive Longing",
            "gate": "Gate 4",
        }
        signals = [
            {"tone": "longing", "voltage": "high", "keyword": "miss"},
        ]
        
        result = engine.process_glyph_response(
            glyph_data=glyph_data,
            signals=signals,
            user_input="I miss the way things used to be",
            user_id="glyph_user",
        )
        
        assert "poem_state" in result
        assert "poem_rendered" in result

    def test_get_current_state_summary(self, engine):
        """Test state summary retrieval."""
        summary = engine.get_current_state_summary()
        
        assert "poem" in summary
        assert "ethics" in summary
        assert "memories_count" in summary
        assert summary["poem"]["is_alive"] is True


class TestSingletonEngine:
    """Tests for the singleton engine factory."""

    def test_get_engine_singleton(self, tmp_path):
        """Test singleton engine retrieval."""
        reset_poetic_engine()
        
        storage_path = str(tmp_path / "singleton_state.json")
        engine1 = get_poetic_engine(storage_path)
        engine2 = get_poetic_engine()
        
        assert engine1 is engine2
        
        reset_poetic_engine()

    def test_reset_engine(self, tmp_path):
        """Test engine reset."""
        storage_path = str(tmp_path / "reset_state.json")
        engine1 = get_poetic_engine(storage_path)
        
        reset_poetic_engine()
        
        engine2 = get_poetic_engine(storage_path)
        assert engine1 is not engine2
        
        reset_poetic_engine()
