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
    from faster_whisper import WhisperModel
    HAS_SPEECH_RECOGNITION = True
except ImportError:
    HAS_SPEECH_RECOGNITION = False

try:
    import soundfile as sf
    HAS_SOUNDFILE = True
except ImportError:
    HAS_SOUNDFILE = False

try:
    import sounddevice as sd
    HAS_SOUNDDEVICE = True
except (ImportError, OSError) as e:
    # OSError raised when PortAudio library not found
    logger.warning(f"sounddevice unavailable: {e}. Audio recording disabled.")
    HAS_SOUNDDEVICE = False


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
    """Get or create speech recognizer (Faster Whisper model)."""
    global _recognizer
    if _recognizer is None and HAS_SPEECH_RECOGNITION:
        try:
            # Use the base model (lighter weight, ~140MB)
            _recognizer = WhisperModel("base", device="cpu", compute_type="int8")
        except Exception as e:
            logger.warning(f"Failed to load Whisper model: {e}")
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
    # Debug logging
    logger.info(f"Voice dependencies: whisper={HAS_SPEECH_RECOGNITION}, soundfile={HAS_SOUNDFILE}, sounddevice={HAS_SOUNDDEVICE}")
    
    # Check all required dependencies
    missing_deps = []
    if not HAS_SPEECH_RECOGNITION:
        missing_deps.append("faster-whisper")
    if not HAS_SOUNDFILE:
        missing_deps.append("soundfile")
    if not HAS_SOUNDDEVICE:
        missing_deps.append("sounddevice")
    
    if missing_deps:
        st.error(f"Voice recording unavailable - missing: {', '.join(missing_deps)}")
        st.info(f"Install with: `pip install {' '.join(missing_deps)}`")
        return None
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🎤 Record Message", use_container_width=True):
            try:
                recognizer = get_speech_recognizer()
                if recognizer is None:
                    st.error("Speech recognizer not initialized")
                    return None
                
                # Record 10 seconds of audio
                sample_rate = 16000
                duration = 10
                
                with st.spinner(f"🎤 Listening... ({duration} seconds)"):
                    try:
                        audio_data = sd.rec(int(sample_rate * duration), samplerate=sample_rate, channels=1, dtype='float32')
                        sd.wait()
                    except Exception as e:
                        st.error(f"Microphone error: {e}")
                        return None
                
                # Save audio temporarily for transcription
                with st.spinner("📝 Transcribing..."):
                    try:
                        import tempfile
                        import os
                        
                        # Create a temporary audio file
                        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                            sf.write(tmp.name, audio_data, sample_rate)
                            tmp_path = tmp.name
                        
                        try:
                            # Transcribe using Whisper
                            segments, info = recognizer.transcribe(tmp_path)
                            text = " ".join([segment.text for segment in segments]).strip()
                            
                            if text:
                                st.session_state["voice_input_text"] = text
                                st.success(f"✓ Got it: {text}")
                                return text
                            else:
                                st.warning("Could not understand audio. Please try again.")
                                return None
                        finally:
                            # Clean up temp file
                            try:
                                os.unlink(tmp_path)
                            except:
                                pass
                                
                    except Exception as e:
                        st.error(f"Transcription error: {e}")
                        logger.debug(f"Transcription error: {e}")
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
