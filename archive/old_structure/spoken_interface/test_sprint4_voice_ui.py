"""Tests for Sprint 4: Streamlit Voice UI Integration

Test voice UI components and session management.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from spoken_interface.voice_ui import (
    VoiceUIState,
    VoiceUIComponents,
    VoiceChatSession,
    integrate_voice_ui_into_chat,
)


class TestVoiceUIState:
    """Test voice UI state management."""

    def test_initial_state(self):
        """Should initialize with correct defaults."""
        state = VoiceUIState()

        assert state.is_recording is False
        assert state.audio_buffer is None
        assert state.transcription is None
        assert state.playback_audio is None
        assert state.voice_enabled is True

    def test_reset_recording(self):
        """Should reset recording state."""
        state = VoiceUIState()
        state.is_recording = True
        state.audio_buffer = b"test"

        state.reset_recording()

        assert state.is_recording is False
        assert state.audio_buffer is None

    def test_reset_playback(self):
        """Should reset playback state."""
        state = VoiceUIState()
        state.playback_audio = b"audio"

        state.reset_playback()

        assert state.playback_audio is None


class TestVoiceChatSession:
    """Test voice chat session management."""

    def test_session_initialization(self):
        """Should initialize empty session."""
        session = VoiceChatSession()

        assert session.get_voice_message_count() == 0
        assert isinstance(session.start_time, datetime)

    def test_add_user_message(self):
        """Should add user voice message."""
        session = VoiceChatSession()

        session.add_voice_message("Hello", is_user=True)

        assert session.get_voice_message_count() == 1
        assert session.voice_messages[0]["text"] == "Hello"
        assert session.voice_messages[0]["is_user"] is True

    def test_add_assistant_message(self):
        """Should add assistant voice message."""
        session = VoiceChatSession()

        session.add_voice_message("Hi there!", is_user=False)

        assert session.get_voice_message_count() == 1
        assert session.voice_messages[0]["text"] == "Hi there!"
        assert session.voice_messages[0]["is_user"] is False

    def test_add_message_with_audio(self):
        """Should store audio with message."""
        session = VoiceChatSession()
        audio_bytes = b"audio_data"

        session.add_voice_message("Test", audio_bytes=audio_bytes)

        assert session.voice_messages[0]["audio"] == audio_bytes

    def test_session_duration(self):
        """Should calculate session duration."""
        session = VoiceChatSession()

        # Set start time to 1 second ago
        session.start_time = datetime.now() - timedelta(seconds=1)

        duration = session.get_session_duration()

        # Should be approximately 1 second (allow 0.5 second tolerance)
        assert 0.5 < duration < 1.5

    def test_multiple_messages(self):
        """Should handle multiple messages."""
        session = VoiceChatSession()

        session.add_voice_message("Message 1", is_user=True)
        session.add_voice_message("Response 1", is_user=False)
        session.add_voice_message("Message 2", is_user=True)

        assert session.get_voice_message_count() == 3
        assert session.voice_messages[0]["text"] == "Message 1"
        assert session.voice_messages[1]["text"] == "Response 1"
        assert session.voice_messages[2]["text"] == "Message 2"


class TestVoiceUIComponents:
    """Test voice UI components initialization."""

    def test_components_initialization_with_voice_deps(self):
        """Should initialize components when dependencies available."""
        with patch('spoken_interface.voice_ui.HAS_VOICE_DEPS', True):
            with patch('spoken_interface.voice_ui.AudioPipeline'):
                with patch('spoken_interface.voice_ui.ProsodyPlanner'):
                    with patch('spoken_interface.voice_ui.StreamingTTSPipeline'):
                        components = VoiceUIComponents()

                        assert components.audio_pipeline is not None
                        assert components.prosody_planner is not None
                        assert components.tts_pipeline is not None

    def test_components_initialization_without_deps(self):
        """Should handle missing dependencies gracefully."""
        with patch('spoken_interface.voice_ui.HAS_VOICE_DEPS', False):
            components = VoiceUIComponents()

            assert components.audio_pipeline is None
            assert components.prosody_planner is None
            assert components.tts_pipeline is None


class TestVoiceUIIntegration:
    """Test voice UI integration functions."""

    @patch('spoken_interface.voice_ui.st')
    def test_integrate_voice_ui_into_chat(self, mock_st):
        """Should return integration configuration."""
        # Mock session state as an object with attributes
        session_state_mock = MagicMock()
        session_state_mock.__contains__ = lambda self, key: False
        mock_st.session_state = session_state_mock

        with patch('spoken_interface.voice_ui.HAS_VOICE_DEPS', True):
            with patch('spoken_interface.voice_ui.AudioPipeline'):
                with patch('spoken_interface.voice_ui.ProsodyPlanner'):
                    with patch('spoken_interface.voice_ui.StreamingTTSPipeline'):
                        config = integrate_voice_ui_into_chat()

                        # Should return configuration dict
                        assert "components" in config
                        assert "session" in config
                        assert "render_input" in config
                        assert "render_output" in config
                        assert "render_settings" in config


class TestVoiceUIRenderMethods:
    """Test voice UI render methods."""

    @patch('spoken_interface.voice_ui.st')
    def test_render_voice_settings(self, mock_st):
        """Should render voice settings."""
        with patch('spoken_interface.voice_ui.HAS_VOICE_DEPS', True):
            with patch('spoken_interface.voice_ui.AudioPipeline'):
                with patch('spoken_interface.voice_ui.ProsodyPlanner'):
                    with patch('spoken_interface.voice_ui.StreamingTTSPipeline'):
                        # Mock Streamlit methods
                        mock_st.sidebar.expander.return_value.__enter__ = Mock()
                        mock_st.sidebar.expander.return_value.__exit__ = Mock()
                        mock_st.selectbox.return_value = "base"
                        mock_st.slider.side_effect = [1.0, 1.0]

                        components = VoiceUIComponents()
                        settings = components.render_voice_settings()

                        # Should return settings dict
                        assert isinstance(settings, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
