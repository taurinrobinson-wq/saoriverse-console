"""Sprint 4: Streamlit Voice UI Integration

Voice input/output components for Streamlit chat interface.
Integrates audio pipeline, STT, prosody planning, and TTS.
"""

import streamlit as st
import numpy as np
from typing import Optional, Dict, Any, Callable
from datetime import datetime
from io import BytesIO

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    from spoken_interface import AudioPipeline, SpeechToText
    from spoken_interface.prosody_planner import ProsodyPlanner, GlyphSignals
    from spoken_interface.streaming_tts import StreamingTTSPipeline, TTSConfig
    HAS_VOICE_DEPS = True
except ImportError:
    HAS_VOICE_DEPS = False


class VoiceUIState:
    """Manages voice UI state across Streamlit reruns."""

    def __init__(self):
        """Initialize voice state."""
        self.is_recording = False
        self.audio_buffer = None
        self.transcription = None
        self.playback_audio = None
        self.last_tts_request = None
        self.voice_enabled = True

    def reset_recording(self):
        """Reset recording state."""
        self.is_recording = False
        self.audio_buffer = None

    def reset_playback(self):
        """Reset playback state."""
        self.playback_audio = None


class VoiceUIComponents:
    """Streamlit voice UI components."""

    def __init__(self):
        """Initialize components."""
        self.audio_pipeline = None
        self.prosody_planner = None
        self.tts_pipeline = None
        self._initialize_pipelines()

    def _initialize_pipelines(self):
        """Initialize audio processing pipelines."""
        if not HAS_VOICE_DEPS:
            return

        try:
            self.audio_pipeline = AudioPipeline()
            self.prosody_planner = ProsodyPlanner()
            self.tts_pipeline = StreamingTTSPipeline(
                config=TTSConfig(chunk_size_ms=500)
            )
        except Exception as e:
            st.warning(f"Voice features unavailable: {e}")

    def render_voice_input_section(self) -> Optional[str]:
        """Render voice input controls and return transcription if ready.

        Returns:
            Transcribed text if audio was processed, None otherwise
        """
        if not HAS_VOICE_DEPS:
            st.info("🔇 Voice interface requires: faster-whisper, librosa, TTS")
            return None

        st.sidebar.markdown("---")
        st.sidebar.subheader("🎤 Voice Input")

        # Voice enabled toggle
        voice_enabled = st.sidebar.checkbox(
            "Enable voice chat",
            value=True,
            help="Enable microphone input and voice responses"
        )

        if not voice_enabled:
            st.sidebar.info("Voice chat disabled")
            return None

        # Microphone input
        audio_data = st.sidebar.audio_input(
            "Record message",
            label_visibility="collapsed",
        )

        if audio_data is not None:
            # Process audio
            st.sidebar.info("🔄 Processing audio...")

            try:
                # Read audio bytes
                audio_bytes = audio_data.read()

                # Transcribe
                result = self.audio_pipeline.process_user_audio(audio_bytes)
                transcription = result.get("transcribed_text", "")
                confidence = result.get("confidence", 0.0)

                # Display result
                st.sidebar.success(f"✓ Heard: \"{transcription}\"")
                st.sidebar.caption(f"Confidence: {confidence:.1%}")

                return transcription

            except Exception as e:
                st.sidebar.error(f"Error processing audio: {e}")
                return None

        return None

    def render_voice_output_section(
        self,
        response_text: str,
        glyph_signals: Optional[GlyphSignals] = None,
    ) -> Optional[bytes]:
        """Render voice output synthesis and playback.

        Args:
            response_text: Text to synthesize
            glyph_signals: Optional glyph signals for prosody

        Returns:
            Audio bytes if synthesized, None otherwise
        """
        if not HAS_VOICE_DEPS:
            return None

        if not response_text:
            return None

        st.sidebar.markdown("---")
        st.sidebar.subheader("🔊 Voice Output")

        # Create default glyph signals if not provided
        if glyph_signals is None:
            glyph_signals = GlyphSignals(
                text=response_text,
                voltage=0.5,
                tone="professional",
                emotional_attunement=0.5,
                certainty=0.7,
                valence=0.5
            )

        # Show synthesis options
        col1, col2 = st.sidebar.columns(2)

        with col1:
            if st.button("🎵 Generate Voice"):
                st.sidebar.info("⏳ Synthesizing audio...")

                try:
                    # Plan prosody
                    prosody_plan = self.prosody_planner.plan_from_glyph(
                        glyph_signals
                    )

                    # Synthesize
                    audio = self.tts_pipeline.engine.synthesize_with_prosody(
                        response_text,
                        prosody_plan
                    )

                    # Display success
                    st.sidebar.success("✓ Voice synthesized")

                    # Playback control
                    st.sidebar.audio(
                        data=audio,
                        format="audio/wav",
                        sample_rate=self.tts_pipeline.engine.sample_rate,
                    )

                    return audio

                except Exception as e:
                    st.sidebar.error(f"Synthesis error: {e}")
                    return None

        with col2:
            if st.button("📊 Show Prosody"):
                try:
                    prosody_plan = self.prosody_planner.plan_from_glyph(
                        glyph_signals
                    )

                    # Display prosody plan
                    st.sidebar.caption("Prosody Plan:")
                    st.sidebar.write({
                        "Rate": f"{prosody_plan.speaking_rate:.2f}x",
                        "Pitch": f"{prosody_plan.pitch_shift_semitones:+.1f}st",
                        "Energy": f"{prosody_plan.energy_level:.2f}x",
                        "Style": prosody_plan.voice_style,
                        "Contour": prosody_plan.terminal_contour,
                    })

                except Exception as e:
                    st.sidebar.error(f"Error: {e}")

    def render_voice_settings(self) -> Dict[str, Any]:
        """Render voice settings panel.

        Returns:
            Dictionary of voice settings
        """
        if not HAS_VOICE_DEPS:
            return {}

        with st.sidebar.expander("⚙️ Voice Settings"):
            # STT settings
            st.markdown("**Speech Recognition**")
            stt_model = st.selectbox(
                "Whisper model",
                ["tiny", "small", "base"],
                help="Larger = more accurate but slower"
            )

            # TTS settings
            st.markdown("**Voice Synthesis**")
            speaking_rate = st.slider(
                "Speaking rate",
                0.5, 1.5, 1.0,
                step=0.1,
                help="1.0 = normal speed"
            )

            voice_energy = st.slider(
                "Voice energy",
                0.3, 1.5, 1.0,
                step=0.1,
                help="How loud or quiet"
            )

            return {
                "stt_model": stt_model,
                "speaking_rate": speaking_rate,
                "voice_energy": voice_energy,
            }

        return {}

    def render_voice_debug_info(self) -> None:
        """Render debug information for voice pipeline."""
        if not HAS_VOICE_DEPS:
            return

        with st.sidebar.expander("🔍 Debug Info"):
            if self.audio_pipeline:
                st.write("✓ Audio pipeline loaded")
            else:
                st.write("✗ Audio pipeline not loaded")

            if self.prosody_planner:
                st.write("✓ Prosody planner loaded")
            else:
                st.write("✗ Prosody planner not loaded")

            if self.tts_pipeline:
                info = self.tts_pipeline.get_info()
                st.write("✓ TTS pipeline loaded")
                st.write(info)
            else:
                st.write("✗ TTS pipeline not loaded")


def create_voice_ui_footer() -> None:
    """Create voice UI info footer."""
    if not HAS_VOICE_DEPS:
        return

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "🎤🔊 **Voice Chat Pipeline**\n"
        "- Microphone → Speech-to-Text (Whisper)\n"
        "- Glyph signals → Prosody planning\n"
        "- Text + Prosody → Voice synthesis (Coqui)\n"
        "- Zero API costs · Local processing"
    )


class VoiceChatSession:
    """Manages voice chat session state."""

    def __init__(self):
        """Initialize session."""
        self.voice_messages = []
        self.prosody_history = []
        self.start_time = datetime.now()

    def add_voice_message(
        self,
        message: str,
        audio_bytes: Optional[bytes] = None,
        is_user: bool = True,
    ) -> None:
        """Add message to voice history.

        Args:
            message: Message text
            audio_bytes: Associated audio (optional)
            is_user: True if user message, False if assistant
        """
        self.voice_messages.append({
            "timestamp": datetime.now(),
            "text": message,
            "audio": audio_bytes,
            "is_user": is_user,
        })

    def get_session_duration(self) -> float:
        """Get session duration in seconds."""
        return (datetime.now() - self.start_time).total_seconds()

    def get_voice_message_count(self) -> int:
        """Get number of voice messages."""
        return len(self.voice_messages)


# Streamlit page configuration
def configure_voice_page() -> None:
    """Configure Streamlit page for voice chat."""
    st.set_page_config(
        page_title="FirstPerson - Voice Chat",
        page_icon="🎤",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Custom CSS for voice UI
    st.markdown("""
    <style>
    .voice-input { border: 2px solid #00D9FF; border-radius: 10px; padding: 10px; }
    .voice-output { border: 2px solid #00FF99; border-radius: 10px; padding: 10px; }
    .voice-status { font-size: 12px; color: #999; }
    </style>
    """, unsafe_allow_html=True)


# Integration example for main_v2.py
def integrate_voice_ui_into_chat(
    response_generator: Optional[Callable] = None,
) -> Dict[str, Any]:
    """Return configuration to integrate voice UI into existing chat.

    This function provides the necessary components and integration
    points to add voice I/O to the existing Streamlit chat interface.

    Args:
        response_generator: Optional callback for custom response generation

    Returns:
        Dictionary with voice UI components and callbacks
    """

    # Initialize voice components
    voice_ui = VoiceUIComponents()

    # Get or create voice session
    if "voice_session" not in st.session_state:
        st.session_state.voice_session = VoiceChatSession()

    session = st.session_state.voice_session

    return {
        "components": voice_ui,
        "session": session,
        "render_input": voice_ui.render_voice_input_section,
        "render_output": voice_ui.render_voice_output_section,
        "render_settings": voice_ui.render_voice_settings,
        "render_debug": voice_ui.render_voice_debug_info,
        "create_footer": create_voice_ui_footer,
    }


if __name__ == "__main__":
    # Demo mode
    configure_voice_page()

    st.title("🎤 Voice Chat Interface Demo")

    if HAS_VOICE_DEPS:
        st.info("✓ Voice interface available")

        # Initialize components
        components = VoiceUIComponents()

        # Show voice settings
        settings = components.render_voice_settings()

        # Demo: Render input section
        st.sidebar.markdown("---")
        transcription = components.render_voice_input_section()

        if transcription:
            st.write(f"**You said:** {transcription}")

        # Demo: Render output section
        if st.sidebar.checkbox("Show voice output demo"):
            components.render_voice_output_section(
                "Hello! I'm excited to help you today."
            )

        # Debug info
        components.render_voice_debug_info()
        create_voice_ui_footer()

    else:
        st.warning(
            "Voice interface requires: faster-whisper, librosa, TTS, scipy")
        st.code(
            "pip install -r requirements-voice.txt",
            language="bash"
        )
