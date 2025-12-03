"""Streamlit Audio Input Component for Voice Interface

Handles microphone input and audio streaming in Streamlit.
"""

import streamlit as st
from io import BytesIO
import numpy as np
from pathlib import Path


def render_audio_input_widget():
    """
    Render audio input widget in Streamlit sidebar.
    
    Uses st.audio_input() for browser microphone access.
    Streamlit handles all browser permissions and audio encoding.
    
    Returns:
        audio_bytes or None if no audio captured
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎙️ Voice Input (Optional)")
    
    # Audio input widget - browser handles permissions
    audio_data = st.sidebar.audio_input(
        "Record a voice message (3-10 seconds)",
        label_visibility="collapsed",
        key="voice_input_widget"
    )
    
    if audio_data:
        # Show audio player for confirmation
        st.sidebar.audio(audio_data, format="audio/wav")
        
        return audio_data
    
    return None


def render_audio_visualization(audio_bytes: bytes):
    """
    Visualize audio waveform in Streamlit.
    
    Args:
        audio_bytes: Audio data in bytes
    """
    try:
        import librosa
        import matplotlib.pyplot as plt
        
        # Load audio
        audio_buffer = BytesIO(audio_bytes)
        y, sr = librosa.load(audio_buffer, sr=16000, mono=True)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 3))
        
        # Plot waveform
        time = np.linspace(0, len(y) / sr, len(y))
        ax.plot(time, y, linewidth=0.5, color='#1f77b4')
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.set_title("Audio Waveform")
        ax.grid(True, alpha=0.3)
        
        st.pyplot(fig, use_container_width=True)
        
    except Exception as e:
        st.warning(f"Could not visualize audio: {e}")


def render_transcription_status(is_loading: bool = False, 
                                confidence: float = 0.0):
    """
    Show transcription status indicator.
    
    Args:
        is_loading: Whether currently transcribing
        confidence: Confidence score (0-1)
    """
    if is_loading:
        st.spinner("🎙️ Transcribing audio...")
    elif confidence > 0:
        # Show confidence level
        col1, col2 = st.columns([3, 1])
        with col1:
            st.metric("Transcription Confidence", f"{confidence:.1%}")
        
        if confidence < 0.6:
            st.warning("⚠️ Low confidence - audio quality may be poor")
        elif confidence < 0.8:
            st.info("ℹ️ Moderate confidence - result may have errors")
        else:
            st.success("✅ High confidence - transcription is reliable")


def render_audio_settings():
    """
    Render advanced audio settings in sidebar.
    
    Returns:
        dict with audio settings
    """
    with st.sidebar.expander("⚙️ Audio Settings"):
        input_device = st.selectbox(
            "Microphone",
            ["Default", "USB Headset", "Built-in Microphone"],
            key="audio_device"
        )
        
        sample_rate = st.selectbox(
            "Sample Rate",
            [16000, 22050, 44100],
            value=16000,
            help="16kHz optimal for speech recognition"
        )
        
        noise_suppression = st.checkbox(
            "Enable Noise Suppression",
            value=True,
            help="Filter background noise"
        )
        
        auto_gain = st.checkbox(
            "Auto Gain Control",
            value=True,
            help="Automatically normalize volume"
        )
        
        return {
            "device": input_device,
            "sample_rate": sample_rate,
            "noise_suppression": noise_suppression,
            "auto_gain": auto_gain,
        }


def render_voice_message_preview(transcribed_text: str, 
                                 duration: float,
                                 voice_analysis: dict = None):
    """
    Display voice message with metadata.
    
    Args:
        transcribed_text: What user said
        duration: Audio duration in seconds
        voice_analysis: Optional voice emotion analysis
    """
    with st.expander("📝 Voice Message Details", expanded=True):
        col1, col2, col3 = st.columns(3)
        col1.metric("Duration", f"{duration:.1f}s")
        col2.metric("Text Length", f"{len(transcribed_text)} chars")
        col3.metric("Clarity", "Good" if duration > 1 else "Short")
        
        st.write("**You said:**")
        st.info(transcribed_text)
        
        if voice_analysis:
            st.write("**Voice Analysis:**")
            col1, col2, col3 = st.columns(3)
            if "estimated_arousal" in voice_analysis:
                col1.metric("Arousal", f"{voice_analysis['estimated_arousal']:.0%}")
            if "speech_rate_wpm" in voice_analysis:
                col2.metric("Speech Rate", f"{voice_analysis['speech_rate_wpm']} WPM")
            if "energy_level" in voice_analysis:
                col3.metric("Energy", f"{voice_analysis['energy_level']:.0%}")


def render_audio_errors(error_message: str):
    """
    Display audio processing errors with recovery suggestions.
    
    Args:
        error_message: Error description
    """
    st.error(f"🎤 Audio Error: {error_message}")
    
    with st.expander("Troubleshooting"):
        st.write("""
        **Try these steps:**
        1. Check microphone is working (test in another app)
        2. Allow browser permission for microphone
        3. Check for background noise
        4. Try recording again with clearer audio
        5. Use a wired microphone for better quality
        """)


class AudioStreamHandler:
    """Handle streaming audio input and processing."""
    
    def __init__(self):
        """Initialize audio stream handler."""
        self.is_recording = False
        self.audio_buffer = []
    
    def start_recording(self):
        """Start recording audio stream."""
        self.is_recording = True
        self.audio_buffer = []
    
    def add_audio_chunk(self, chunk: bytes):
        """Add chunk to buffer."""
        if self.is_recording:
            self.audio_buffer.append(chunk)
    
    def stop_recording(self) -> bytes:
        """Stop recording and return full audio."""
        self.is_recording = False
        return b''.join(self.audio_buffer)
    
    def get_buffer_status(self) -> dict:
        """Get current buffer status."""
        total_size = sum(len(chunk) for chunk in self.audio_buffer)
        return {
            "chunks": len(self.audio_buffer),
            "total_bytes": total_size,
            "estimated_duration_sec": total_size / (16000 * 2),  # Assuming 16kHz, 16-bit
        }
