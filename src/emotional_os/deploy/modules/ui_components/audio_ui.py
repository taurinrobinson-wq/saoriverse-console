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

logger = logging.getLogger(__name__)

# Lazy imports to avoid loading heavy audio libraries unnecessarily
_audio_pipeline = None
_tts_pipeline = None


def get_audio_pipeline():
    """Get or create the audio pipeline (lazy initialization)."""
    global _audio_pipeline
    if _audio_pipeline is None:
        try:
            from .audio_pipeline import AudioPipeline
            _audio_pipeline = AudioPipeline()
        except Exception as e:
            logger.warning(f"Failed to initialize AudioPipeline: {e}")
    return _audio_pipeline


def get_tts_pipeline():
    """Get or create the TTS pipeline (lazy initialization)."""
    global _tts_pipeline
    if _tts_pipeline is None:
        try:
            from .streaming_tts import StreamingTTSPipeline, TTSConfig
            config = TTSConfig(gpu=False)
            _tts_pipeline = StreamingTTSPipeline(config)
        except Exception as e:
            logger.warning(f"Failed to initialize StreamingTTSPipeline: {e}")
    return _tts_pipeline


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
    """Render audio recording widget using custom HTML/JS component.
    
    Returns:
        Dict with recorded audio data or None if not recorded
    """
    # Custom HTML/JS for microphone recording without external dependencies
    recorder_component = components.html(
        """
        <div id="recorder-container" style="padding: 20px; text-align: center;">
            <button id="recordBtn" style="
                padding: 12px 24px;
                font-size: 16px;
                background-color: #ff4b4b;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                margin: 10px;
            ">🎙️ Start Recording</button>
            
            <button id="stopBtn" style="
                padding: 12px 24px;
                font-size: 16px;
                background-color: #4b7bff;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                margin: 10px;
                display: none;
            ">⏹️ Stop Recording</button>
            
            <div id="status" style="margin-top: 20px; font-size: 14px; color: #666;"></div>
            <audio id="audioPlayback" style="display: none; margin-top: 20px;"></audio>
        </div>

        <script>
            let mediaRecorder;
            let audioChunks = [];
            let recordingStartTime = null;

            document.getElementById('recordBtn').onclick = async () => {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    recordingStartTime = Date.now();

                    mediaRecorder.ondataavailable = (event) => {
                        audioChunks.push(event.data);
                    };

                    mediaRecorder.onstop = () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        const reader = new FileReader();
                        reader.onloadend = () => {
                            const base64Audio = reader.result.split(',')[1];
                            window.parent.postMessage({
                                type: 'AUDIO_RECORDED',
                                audioData: base64Audio,
                                duration: (Date.now() - recordingStartTime) / 1000
                            }, '*');
                        };
                        reader.readAsDataURL(audioBlob);
                    };

                    mediaRecorder.start();
                    document.getElementById('recordBtn').style.display = 'none';
                    document.getElementById('stopBtn').style.display = 'inline-block';
                    document.getElementById('status').innerText = '🔴 Recording...';
                } catch (error) {
                    document.getElementById('status').innerText = '❌ Microphone access denied';
                    console.error('Error accessing microphone:', error);
                }
            };

            document.getElementById('stopBtn').onclick = () => {
                mediaRecorder.stop();
                mediaRecorder.stream.getTracks().forEach(track => track.stop());
                document.getElementById('recordBtn').style.display = 'inline-block';
                document.getElementById('stopBtn').style.display = 'none';
                document.getElementById('status').innerText = '✓ Recording saved';
            };
        </script>
        """,
        height=200
    )
    
    return None  # Streamlit component returns None for custom components


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
    """Synthesize response text to audio with emotional prosody.
    
    Args:
        response_text: Text to synthesize
        glyph_name: Name of glyph for prosody guidance
        voice: Voice option (Default, Warm, Professional, Gentle)
        speed: Speech rate multiplier
        
    Returns:
        Audio bytes or None if synthesis failed
    """
    try:
        pipeline = get_tts_pipeline()
        if pipeline is None:
            st.warning("TTS not available. Displaying text response only.")
            return None
        
        with st.spinner("🔄 Synthesizing response audio..."):
            # Map glyph names to prosody parameters
            prosody_map = {
                "I_HEAR_YOU": {"energy": 0.8, "rate": 0.95},
                "EXACTLY": {"energy": 1.0, "rate": 0.9},
                "THAT_LANDS": {"energy": 0.9, "rate": 1.0},
                "RECURSIVE_ACHE": {"energy": 0.7, "rate": 0.85},
            }
            
            prosody = prosody_map.get(glyph_name, {"energy": 0.9, "rate": 1.0})
            prosody["rate"] *= speed
            
            # Generate audio
            audio_buffer = pipeline.synthesize_with_prosody(
                response_text,
                prosody=prosody
            )
            
            if audio_buffer:
                st.success("✓ Audio synthesized")
                return audio_buffer
            else:
                st.warning("Could not synthesize audio")
                return None
                
    except Exception as e:
        logger.warning(f"TTS synthesis error: {e}")
        logger.debug(f"Error details: {str(e)}")
        return None


def initialize_voice_session():
    """Initialize voice mode state in session."""
    st.session_state.setdefault("voice_mode_enabled", False)
    st.session_state.setdefault("last_audio_input", None)
    st.session_state.setdefault("last_audio_output", None)
