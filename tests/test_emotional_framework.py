"""Tests for the EmotionalFramework integration module.

Tests the unified EmotionalFramework which integrates all components.
"""
import pytest

from emotional_os.core.emotional_framework import EmotionalFramework


class TestEmotionalFramework:
    """Tests for the EmotionalFramework integration class."""

    def test_init_creates_all_components(self):
        """Test that initialization creates all components."""
        framework = EmotionalFramework()
        assert framework._attunement is not None
        assert framework._reciprocity is not None
        assert framework._temporal is not None
        assert framework._embodiment is not None
        assert framework._poetic is not None
        assert framework._tension is not None
        assert framework._saori is not None

    def test_start_session_returns_id(self):
        """Test that start_session returns a session ID."""
        framework = EmotionalFramework()
        session_id = framework.start_session()
        assert len(session_id) == 16
        assert framework._state.session_id == session_id

    def test_process_message_returns_dict(self):
        """Test that process_message returns a complete dictionary."""
        framework = EmotionalFramework()
        framework.start_session()
        result = framework.process_message("I'm feeling overwhelmed today")
        
        assert isinstance(result, dict)
        assert "enhanced_response" in result
        assert "presence" in result
        assert "tension" in result
        assert "saori" in result
        assert "archetype" in result

    def test_process_message_with_grief(self):
        """Test processing a grief-related message."""
        framework = EmotionalFramework()
        framework.start_session()
        result = framework.process_message("I'm grieving the loss of my friend")
        
        assert len(result["enhanced_response"]) > 0
        # Should detect negative emotion
        assert result["framework_state"]["last_emotion"] != "neutral"

    def test_process_message_with_metaphor(self):
        """Test processing a message with metaphor."""
        framework = EmotionalFramework()
        framework.start_session()
        result = framework.process_message("I feel like I'm drowning in sadness")
        
        # Should detect water metaphor
        metaphors = result["presence"].get("metaphors", [])
        assert len(metaphors) > 0

    def test_process_message_increments_count(self):
        """Test that processing increments interaction count."""
        framework = EmotionalFramework()
        framework.start_session()
        
        framework.process_message("First message")
        assert framework._state.interaction_count == 1
        
        framework.process_message("Second message")
        assert framework._state.interaction_count == 2

    def test_enable_component(self):
        """Test enabling/disabling components."""
        framework = EmotionalFramework()
        
        framework.enable_component("poetic", False)
        assert framework._state.poetic_active is False
        
        framework.enable_component("poetic", True)
        assert framework._state.poetic_active is True

    def test_get_state(self):
        """Test getting framework state."""
        framework = EmotionalFramework()
        framework.start_session()
        framework.process_message("test")
        
        state = framework.get_state()
        assert state.interaction_count == 1

    def test_get_full_state(self):
        """Test getting complete state from all components."""
        framework = EmotionalFramework()
        framework.start_session()
        framework.process_message("test message")
        
        full_state = framework.get_full_state()
        
        assert "framework" in full_state
        assert "attunement" in full_state
        assert "reciprocity" in full_state
        assert "embodiment" in full_state
        assert "poetic" in full_state
        assert "saori" in full_state

    def test_end_session(self):
        """Test ending a session."""
        framework = EmotionalFramework()
        framework.start_session()
        framework.process_message("I'm feeling better now")
        
        from emotional_os.core.presence.temporal_memory import EmotionalArc, EmotionalSignificance
        summary = framework.end_session(
            arc=EmotionalArc.ASCENDING,
            significance=EmotionalSignificance.MEANINGFUL,
        )
        
        assert "session_id" in summary
        assert "interaction_count" in summary
        assert summary["interaction_count"] == 1

    def test_disabled_components_not_processed(self):
        """Test that disabled components are not processed."""
        framework = EmotionalFramework(enable_all=False)
        framework.start_session()
        
        result = framework.process_message("test")
        
        # Presence should be empty or minimal when disabled
        assert not result["presence"].get("metaphors")
        assert not result["presence"].get("attunement")

    def test_train_surprise_coefficient(self):
        """Test training the surprise coefficient."""
        framework = EmotionalFramework(surprise_coefficient=0.2)
        initial = framework._tension.surprise.get_surprise_coefficient()
        
        framework.train_surprise_coefficient(1.0)  # Positive feedback
        
        # Coefficient should increase
        new = framework._tension.surprise.get_surprise_coefficient()
        assert new >= initial

    def test_simulate_time_passage(self):
        """Test simulating time passage."""
        framework = EmotionalFramework()
        framework.start_session()
        
        initial_entropy = framework._saori.mortality.get_state().entropy_level
        framework.simulate_time_passage(hours=10)
        
        new_entropy = framework._saori.mortality.get_state().entropy_level
        assert new_entropy > initial_entropy

    def test_process_message_with_challenge_pattern(self):
        """Test processing a message with absolutism pattern."""
        framework = EmotionalFramework()
        framework.start_session()
        
        result = framework.process_message("I always fail at everything")
        
        # Should detect challenge opportunity
        tensions = result["tension"].get("tensions", [])
        assert len(tensions) > 0

    def test_multiple_messages_build_context(self):
        """Test that multiple messages build emotional context."""
        framework = EmotionalFramework()
        framework.start_session("user123")
        
        framework.process_message("I'm feeling sad")
        framework.process_message("Everything feels heavy")
        result = framework.process_message("I don't know what to do")
        
        # Should have accumulated context
        assert framework._state.interaction_count == 3
        # Mood should have evolved
        mood = framework._reciprocity.get_mood_profile()
        assert mood.warmth_level >= 0.7  # Should be tender after sad messages
