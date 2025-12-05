"""Audio UI Components - Voice Input/Output Widgets for Streamlit.

Provides high-level UI components for:
- Recording audio from microphone (via custom HTML/JS)
- Displaying transcription
- Playing synthesized speech
- Voice mode toggle
"""

import streamlit as st
import streamlit.components.v1 as components
import logging
from typing import Optional, Tuple
import json
import io

logger = logging.getLogger(__name__)

# Lazy imports for audio libraries
_tts_engine = None
_recognizer = None

try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False

try:
    import speech_recognition as sr
    HAS_SPEECH_RECOGNITION = True
except ImportError:
    HAS_SPEECH_RECOGNITION = False


def get_tts_engine():
    """Get or create TTS engine."""
    global _tts_engine
    if _tts_engine is None and HAS_PYTTSX3:
        try:
            _tts_engine = pyttsx3.init()
            _tts_engine.setProperty('rate', 150)
            _tts_engine.setProperty('volume', 0.9)
        except Exception as e:
            logger.warning(f"Failed to initialize TTS: {e}")
    return _tts_engine


def get_speech_recognizer():
    """Get or create speech recognizer."""
    global _recognizer
    if _recognizer is None and HAS_SPEECH_RECOGNITION:
        _recognizer = sr.Recognizer()
    return _recognizer


def render_voice_mode_toggle():
    """Render voice mode toggle in sidebar."""
    with st.sidebar:
        st.markdown("---")
        st.subheader("🎙️ Voice Mode")
        
        voice_enabled = st.checkbox(
            "Enable Voice Input/Output",
            value=st.session_state.get("voice_mode_enabled", False),
            help="Enable microphone input and audio playback (experimental)"
        )
        
        st.session_state["voice_mode_enabled"] = voice_enabled
        
        if voice_enabled:
            st.info(
                "✓ Voice mode enabled\n\n"
                "Click the mic button to record your message. "
                "Responses will be synthesized to speech."
            )


def render_audio_recorder():
    """Record audio from microphone and return transcribed text.
    
    Returns:
        Transcribed text or None if recording failed
    """
    if not HAS_SPEECH_RECOGNITION:
        st.error("Speech recognition not available")
        return None
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🎤 Record Message", use_container_width=True):
            try:
                recognizer = get_speech_recognizer()
                if recognizer is None:
                    st.error("Speech recognizer not initialized")
                    return None
                
                with st.spinner("🎤 Listening... (10 seconds)"):
                    try:
                        with sr.Microphone() as source:
                            # Adjust for ambient noise
                            recognizer.adjust_for_ambient_noise(source, duration=0.5)
                            # Record audio with 10 second timeout
                            audio_data = recognizer.listen(source, timeout=10, phrase_time_limit=10)
                    except sr.RequestError as e:
                        st.error(f"Microphone error: {e}")
                        return None
                
                with st.spinner("📝 Transcribing..."):
                    # Use Google Speech Recognition (free, requires internet)
                    try:
                        text = recognizer.recognize_google(audio_data)
                        st.session_state["voice_input_text"] = text
                        st.success(f"✓ Got it: {text}")
                        return text
                    except sr.UnknownValueError:
                        st.warning("Could not understand audio. Please try again.")
                        return None
                    except sr.RequestError as e:
                        st.error(f"Transcription service error: {e}")
                        return None
                    
            except Exception as e:
                st.error(f"Recording error: {e}")
                logger.debug(f"Voice recording error: {e}")
                return None
    
    with col2:
        # Fallback text input option
        voice_text = st.text_input("Or type:", key="voice_text_input", label_visibility="collapsed")
        if voice_text:
            st.session_state["voice_input_text"] = voice_text
            return voice_text
    
    # Check if we have stored voice input from session
    if st.session_state.get("voice_input_text"):
        result = st.session_state["voice_input_text"]
        st.session_state["voice_input_text"] = None  # Clear after use
        return result
    
    return None


def render_audio_playback(audio_bytes: bytes, label: str = "🔊 Response Audio"):
    """Render audio playback widget.
    
    Args:
        audio_bytes: Audio data in bytes
        label: Label for the audio player
    """
    st.audio(audio_bytes, format="audio/wav", label=label)


def render_voice_chat_interface():
    """Render complete voice chat interface.
    
    Integrates audio recording, transcription, and response synthesis.
    """
    if not st.session_state.get("voice_mode_enabled"):
        return None
    
    st.subheader("🎙️ Voice Chat")
    
    # Create columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**Speak your message**")
        render_audio_recorder()
    
    with col2:
        st.markdown("**Options**")
        synthesis_voice = st.selectbox(
            "Voice",
            options=["Default", "Warm", "Professional", "Gentle"],
            key="voice_synthesis_voice"
        )
        speech_rate = st.slider(
            "Speed",
            min_value=0.8,
            max_value=1.5,
            value=1.0,
            step=0.1,
            key="voice_speech_rate"
        )


def process_audio_input(audio_bytes: bytes) -> Optional[str]:
    """Process user's audio input to text.
    
    Args:
        audio_bytes: Raw audio bytes from recording
        
    Returns:
        Transcribed text or None if processing failed
    """
    try:
        pipeline = get_audio_pipeline()
        if pipeline is None:
            st.error("Audio pipeline not available. Check dependencies.")
            return None
        
        with st.spinner("🔄 Transcribing..."):
            result = pipeline.process_user_audio(audio_bytes)
            
            if result.get("error"):
                st.error(f"Transcription failed: {result['error']}")
                return None
            
            transcribed_text = result.get("text", "").strip()
            confidence = result.get("confidence", 0)
            
            if transcribed_text:
                st.success(f"✓ Transcribed (confidence: {confidence:.0%})")
                st.info(f'"{transcribed_text}"')
                return transcribed_text
            else:
                st.warning("No speech detected. Please try again.")
                return None
                
    except Exception as e:
        logger.error(f"Audio processing error: {e}")
        st.error(f"Error processing audio: {str(e)}")
        return None


def synthesize_response_audio(
    response_text: str,
    glyph_name: str = "",
    voice: str = "Default",
    speed: float = 1.0
) -> Optional[bytes]:
    """Synthesize response text to audio.
    
    Args:
        response_text: Text to synthesize
        glyph_name: Name of glyph for prosody guidance (optional)
        voice: Voice option (Default, Warm, Professional, Gentle)
        speed: Speech rate multiplier
        
    Returns:
        Audio bytes (WAV format) or None if synthesis failed
    """
    if not HAS_PYTTSX3:
        return None
    
    try:
        engine = get_tts_engine()
        if engine is None:
            return None
        
        # Adjust speech rate
        engine.setProperty('rate', int(150 * speed))
        
        # Save to bytes buffer
        audio_buffer = io.BytesIO()
        engine.save_to_file(response_text, '__temp_audio.wav')
        engine.runAndWait()
        
        # Read the generated file into bytes
        try:
            with open('__temp_audio.wav', 'rb') as f:
                audio_bytes = f.read()
            return audio_bytes
        except Exception as e:
            logger.debug(f"Error reading audio file: {e}")
            return None
                
    except Exception as e:
        logger.debug(f"TTS synthesis error: {e}")
        return None


def initialize_voice_session():
    """Initialize voice mode state in session."""
    st.session_state.setdefault("voice_mode_enabled", False)
    st.session_state.setdefault("last_audio_input", None)
    st.session_state.setdefault("last_audio_output", None)
