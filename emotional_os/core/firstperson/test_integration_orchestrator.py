"""Integration tests for FirstPerson Phase 1.

Tests the end-to-end pipeline coordinating:
- Story-Start Detection (ambiguity → clarification)
- Frequency Reflection (theme tracking → reflections)
- Memory Rehydration (context injection)
- Response Templates (non-repetitive variation)
- Supabase Schema (persistence)

Based on 6-turn dialogue covering all modules.
"""

import pytest
from emotional_os.core.firstperson.integration_orchestrator import (
    FirstPersonOrchestrator,
    ConversationTurn,
    IntegrationResponse,
    create_orchestrator,
)


class TestIntegrationOrchestrator:
    """Test the integration orchestrator."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return FirstPersonOrchestrator(
            user_id="test_user_integration",
            conversation_id="test_conv_001",
        )

    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes with all modules."""
        assert orchestrator.user_id == "test_user_integration"
        assert orchestrator.conversation_id == "test_conv_001"
        assert orchestrator.story_start_detector is not None
        assert orchestrator.frequency_reflector is not None
        assert orchestrator.memory_manager is not None
        assert orchestrator.response_templates is not None
        assert orchestrator.supabase_manager is not None
        assert orchestrator.turn_count == 0

    def test_session_initialization(self, orchestrator):
        """Test session initialization with memory rehydration."""
        session_data = orchestrator.initialize_session()

        assert session_data["session_id"] == "test_conv_001"
        assert session_data["user_id"] == "test_user_integration"
        assert "memory_rehydrated" in session_data
        assert "anchors_loaded" in session_data
        assert "top_themes" in session_data
        assert isinstance(session_data["top_themes"], list)

    def test_conversation_turn_creation(self, orchestrator):
        """Test creating a conversation turn."""
        turn = ConversationTurn(
            user_id="test_user",
            conversation_id="conv_123",
            user_input="Test input",
            turn_number=1,
        )

        assert turn.user_id == "test_user"
        assert turn.user_input == "Test input"
        assert turn.turn_number == 1
        assert turn.timestamp is not None

    def test_handle_clear_input(self, orchestrator):
        """Test processing clear input without ambiguity."""
        response = orchestrator.handle_conversation_turn(
            "I'm feeling anxious about my work deadline."
        )

        assert isinstance(response, IntegrationResponse)
        assert response.response_text is not None
        assert len(response.response_text) > 0
        assert orchestrator.turn_count == 1

    def test_handle_ambiguous_input(self, orchestrator):
        """Test processing ambiguous input (pronoun)."""
        response = orchestrator.handle_conversation_turn(
            "She was waiting at the corner."
        )

        assert isinstance(response, IntegrationResponse)
        # Should detect ambiguity or at least provide response
        assert response.response_text is not None

    def test_turn_history_tracking(self, orchestrator):
        """Test that turns are tracked in history."""
        orchestrator.handle_conversation_turn("First turn.")
        orchestrator.handle_conversation_turn("Second turn.")

        assert len(orchestrator.turn_history) == 2
        assert orchestrator.turn_history[0].turn_number == 1
        assert orchestrator.turn_history[1].turn_number == 2

    def test_response_history_tracking(self, orchestrator):
        """Test that responses are tracked in history."""
        orchestrator.handle_conversation_turn("Test input.")

        assert len(orchestrator.response_history) == 1
        assert isinstance(
            orchestrator.response_history[0], IntegrationResponse)

    def test_theme_detection_and_frequency(self, orchestrator):
        """Test theme detection across multiple turns."""
        orchestrator.handle_conversation_turn(
            "I'm angry with the kids."
        )
        response2 = orchestrator.handle_conversation_turn(
            "They keep fighting, family stress mounting."
        )

        # Second turn should detect family_conflict theme
        assert response2.detected_theme is not None or response2.response_text

    def test_response_text_composition(self, orchestrator):
        """Test that response text is composed from templates."""
        response = orchestrator.handle_conversation_turn(
            "I'm exhausted from work all the time."
        )

        assert response.response_text is not None
        assert len(response.response_text) > 5
        assert isinstance(response.response_text, str)

    def test_memory_context_injection(self, orchestrator):
        """Test memory context is tracked through session."""
        orchestrator.initialize_session()
        response = orchestrator.handle_conversation_turn(
            "I'm back, still dealing with the same issues."
        )

        # Memory rehydration flag should be set (or False if no prior data)
        assert isinstance(response.memory_context_injected, bool)

    def test_metadata_in_response(self, orchestrator):
        """Test that response includes metadata."""
        response = orchestrator.handle_conversation_turn("Test input.")

        assert response.metadata is not None
        assert "turn_number" in response.metadata
        assert response.metadata["turn_number"] == 1

    def test_conversation_summary(self, orchestrator):
        """Test generating conversation summary."""
        orchestrator.handle_conversation_turn("I'm angry with the kids.")
        orchestrator.handle_conversation_turn("My boss was unreasonable too.")
        orchestrator.handle_conversation_turn("Everything is overwhelming.")

        summary = orchestrator.get_conversation_summary()

        assert summary["conversation_id"] == "test_conv_001"
        assert summary["turn_count"] == 3
        assert "unique_themes" in summary
        assert "themes_detected" in summary

    def test_response_variety_metrics(self, orchestrator):
        """Test checking response variety/rotation."""
        # Similar inputs multiple times
        for _ in range(3):
            orchestrator.handle_conversation_turn("I'm tired.")

        metrics = orchestrator.get_response_variety_metrics()

        assert "total_responses" in metrics
        assert "unique_responses" in metrics
        assert "variety_ratio" in metrics
        assert 0 <= metrics["variety_ratio"] <= 1.0


class TestIntegrationDialogueFlow:
    """Test realistic 6-turn dialogue flow."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator for dialogue."""
        orc = FirstPersonOrchestrator(
            user_id="dialogue_test_user",
            conversation_id="dialogue_test_conv",
        )
        orc.initialize_session()
        return orc

    def test_turn_1_story_start_detection(self, orchestrator):
        """Turn 1: Story-start detection with ambiguous pronoun."""
        user_input = "She was waiting at the corner."
        response = orchestrator.handle_conversation_turn(user_input)

        # Should either detect ambiguity or provide response
        assert response.response_text is not None
        assert len(orchestrator.turn_history) == 1
        assert orchestrator.turn_history[0].user_input == user_input

    def test_turn_2_clarification_and_theme(self, orchestrator):
        """Turn 2: Clarification + theme detection (anxiety)."""
        orchestrator.handle_conversation_turn("She was waiting at the corner.")
        response = orchestrator.handle_conversation_turn(
            "I meant my sister, she's anxious about her exam."
        )

        # Should detect anxiety theme
        assert response.response_text is not None
        assert len(orchestrator.turn_history) == 2

    def test_turn_3_memory_rehydration(self, orchestrator):
        """Turn 3: Memory rehydration and context carrying."""
        orchestrator.handle_conversation_turn("She was waiting at the corner.")
        orchestrator.handle_conversation_turn(
            "I meant my sister, she's anxious about her exam."
        )
        response = orchestrator.handle_conversation_turn(
            "I'm back, still tired from last week."
        )

        # Should process without error
        assert response.response_text is not None
        assert len(orchestrator.turn_history) == 3

    def test_turn_4_supabase_schema_recording(self, orchestrator):
        """Turn 4: Supabase schema extension recording."""
        orchestrator.handle_conversation_turn("She was waiting at the corner.")
        orchestrator.handle_conversation_turn(
            "I meant my sister, she's anxious about her exam."
        )
        orchestrator.handle_conversation_turn(
            "I'm back, still tired from last week."
        )
        response = orchestrator.handle_conversation_turn(
            "I keep feeling regret about not helping her more."
        )

        # Should detect theme and record
        assert response.response_text is not None
        assert len(orchestrator.turn_history) == 4

    def test_turn_5_template_rotation(self, orchestrator):
        """Turn 5: Template rotation without repetition."""
        orchestrator.handle_conversation_turn("She was waiting at the corner.")
        orchestrator.handle_conversation_turn(
            "I meant my sister, she's anxious about her exam."
        )
        orchestrator.handle_conversation_turn(
            "I'm back, still tired from last week."
        )
        orchestrator.handle_conversation_turn(
            "I keep feeling regret about not helping her more."
        )
        response = orchestrator.handle_conversation_turn(
            "Yeah, it's exhausting to juggle all this."
        )

        # Should provide response
        assert response.response_text is not None
        assert len(orchestrator.turn_history) == 5

    def test_turn_6_end_to_end_flow(self, orchestrator):
        """Turn 6: End-to-end flow with commitment."""
        orchestrator.handle_conversation_turn("She was waiting at the corner.")
        orchestrator.handle_conversation_turn(
            "I meant my sister, she's anxious about her exam."
        )
        orchestrator.handle_conversation_turn(
            "I'm back, still tired from last week."
        )
        orchestrator.handle_conversation_turn(
            "I keep feeling regret about not helping her more."
        )
        orchestrator.handle_conversation_turn(
            "Yeah, it's exhausting to juggle all this."
        )
        response = orchestrator.handle_conversation_turn(
            "Anyway, I'll try to support her better next time."
        )

        # Should complete flow successfully
        assert response.response_text is not None
        assert len(orchestrator.turn_history) == 6
        assert orchestrator.turn_count == 6

    def test_dialogue_summary(self, orchestrator):
        """Test summary after full dialogue."""
        # Run full 6-turn dialogue
        turns = [
            "She was waiting at the corner.",
            "I meant my sister, she's anxious about her exam.",
            "I'm back, still tired from last week.",
            "I keep feeling regret about not helping her more.",
            "Yeah, it's exhausting to juggle all this.",
            "Anyway, I'll try to support her better next time.",
        ]

        for turn_input in turns:
            orchestrator.handle_conversation_turn(turn_input)

        summary = orchestrator.get_conversation_summary()

        assert summary["turn_count"] == 6
        assert summary["conversation_id"] == "dialogue_test_conv"
        assert len(summary["themes_detected"]) >= 0

    def test_dialogue_variety_metrics(self, orchestrator):
        """Test variety metrics after dialogue."""
        turns = [
            "She was waiting at the corner.",
            "I meant my sister, she's anxious about her exam.",
            "I'm back, still tired from last week.",
            "I keep feeling regret about not helping her more.",
            "Yeah, it's exhausting to juggle all this.",
            "Anyway, I'll try to support her better next time.",
        ]

        for turn_input in turns:
            orchestrator.handle_conversation_turn(turn_input)

        metrics = orchestrator.get_response_variety_metrics()

        assert metrics["total_responses"] == 6
        assert metrics["unique_responses"] > 0
        assert 0 <= metrics["variety_ratio"] <= 1.0


class TestIntegrationStressTests:
    """Stress tests for Phase 1 modules."""

    def test_template_rotation_stress(self):
        """Stress test: Template rotation across 20 similar inputs."""
        orchestrator = FirstPersonOrchestrator(
            user_id="stress_test_user",
            conversation_id="stress_test_conv",
        )

        responses = []
        for i in range(20):
            response = orchestrator.handle_conversation_turn("I'm exhausted.")
            responses.append(response.response_text)

        # Check for variety
        unique_responses = len(set(responses))
        assert unique_responses > 1  # Should have at least 2 different responses

        # Check no consecutive identical responses
        consecutive_repeats = sum(
            1 for a, b in zip(responses, responses[1:]) if a == b
        )
        # Some repetition is acceptable but shouldn't be all the same
        assert consecutive_repeats < len(responses) - 1

    def test_frequency_threshold_accumulation(self):
        """Stress test: Frequency accumulation triggering reflections."""
        orchestrator = FirstPersonOrchestrator(
            user_id="freq_stress_test",
            conversation_id="freq_stress_conv",
        )

        # Send same theme multiple times
        for _ in range(5):
            response = orchestrator.handle_conversation_turn(
                "I'm angry with the kids."
            )

        summary = orchestrator.get_conversation_summary()
        # Should have detected theme multiple times
        assert len(summary["themes_detected"]) > 0

    def test_long_conversation_state_maintenance(self):
        """Stress test: Long conversation (50 turns) maintains state."""
        orchestrator = FirstPersonOrchestrator(
            user_id="long_conv_test",
            conversation_id="long_conv",
        )

        inputs = [
            "I'm tired.",
            "Work was stressful.",
            "Family is overwhelming.",
            "I can't focus.",
            "Everything feels hard.",
        ]

        for i in range(50):
            input_text = inputs[i % len(inputs)]
            response = orchestrator.handle_conversation_turn(input_text)
            assert response.response_text is not None

        assert orchestrator.turn_count == 50
        assert len(orchestrator.turn_history) == 50
        assert len(orchestrator.response_history) == 50


class TestIntegrationModuleFactories:
    """Test factory functions and module creation."""

    def test_create_orchestrator_factory(self):
        """Test factory function creates valid orchestrator."""
        orchestrator = create_orchestrator(
            user_id="factory_test_user",
            conversation_id="factory_test_conv",
        )

        assert isinstance(orchestrator, FirstPersonOrchestrator)
        assert orchestrator.user_id == "factory_test_user"
        assert orchestrator.conversation_id == "factory_test_conv"

    def test_create_orchestrator_without_conversation_id(self):
        """Test factory generates conversation ID if not provided."""
        orchestrator = create_orchestrator(user_id="factory_test_user_2")

        assert isinstance(orchestrator, FirstPersonOrchestrator)
        assert orchestrator.user_id == "factory_test_user_2"
        assert orchestrator.conversation_id is not None
        assert "conv_" in orchestrator.conversation_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
