"""Sprint 5c: Enhanced Voice UI with Glyph Visualization & Edge Cases

Extended Streamlit UI with emotional signal visualization,
graceful error handling, and edge case management.
"""

import streamlit as st
import numpy as np
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


@dataclass
class EdgeCaseHandler:
    """Handles edge cases in voice processing."""

    min_audio_duration_ms: float = 500
    """Minimum audio to process."""

    max_audio_duration_ms: float = 120000
    """Maximum audio to process (2 minutes)."""

    min_confidence_threshold: float = 0.3
    """Minimum STT confidence to accept."""

    max_silence_ratio: float = 0.7
    """Maximum silence allowed in audio."""


class EdgeCaseManager:
    """Manages edge cases in voice interaction."""

    def __init__(self, handler: EdgeCaseHandler = None):
        """Initialize edge case manager.

        Args:
            handler: Configuration for edge case handling
        """
        self.handler = handler or EdgeCaseHandler()

    def validate_audio(
        self,
        audio_bytes: bytes,
        sample_rate: int = 22050,
    ) -> Tuple[bool, Optional[str]]:
        """Validate audio input.

        Args:
            audio_bytes: Audio data
            sample_rate: Sample rate in Hz

        Returns:
            (is_valid, error_message)
        """
        if not audio_bytes:
            return False, "No audio data received"

        # Check size constraints
        audio_duration_ms = (len(audio_bytes) /
                             sample_rate / 2) * 1000  # Rough estimate

        if audio_duration_ms < self.handler.min_audio_duration_ms:
            return False, f"Audio too short ({audio_duration_ms:.0f}ms, min {self.handler.min_audio_duration_ms:.0f}ms)"

        if audio_duration_ms > self.handler.max_audio_duration_ms:
            return False, f"Audio too long ({audio_duration_ms:.0f}ms, max {self.handler.max_audio_duration_ms:.0f}ms)"

        # Check for clipping
        try:
            import numpy as np
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
            if np.max(np.abs(audio_array)) >= 32767 * 0.95:
                return False, "Audio appears clipped (distorted)"
        except Exception:
            pass  # Can't validate without numpy

        return True, None

    def validate_transcription(
        self,
        text: str,
        confidence: float,
    ) -> Tuple[bool, Optional[str]]:
        """Validate transcription result.

        Args:
            text: Transcribed text
            confidence: STT confidence (0-1)

        Returns:
            (is_valid, error_message)
        """
        if not text or not text.strip():
            return False, "No speech detected - please speak clearly"

        if confidence < self.handler.min_confidence_threshold:
            return False, (
                f"Transcription confidence too low ({confidence:.1%}) - "
                "please speak more clearly"
            )

        return True, None

    def handle_silence_in_audio(self, audio_bytes: bytes) -> Tuple[bool, Optional[str]]:
        """Detect and handle excessive silence.

        Args:
            audio_bytes: Audio data

        Returns:
            (has_acceptable_speech, message)
        """
        try:
            import numpy as np
            audio_array = np.frombuffer(
                audio_bytes, dtype=np.int16).astype(float)

            # Simple energy-based silence detection
            rms = np.sqrt(np.mean(audio_array ** 2))
            threshold = 2000  # Adjust based on your mic sensitivity

            silent_frames = np.sum(np.abs(audio_array) < threshold)
            silence_ratio = silent_frames / len(audio_array)

            if silence_ratio > self.handler.max_silence_ratio:
                return False, (
                    f"Mostly silence detected ({silence_ratio:.1%}) - "
                    "please speak into the microphone"
                )

            return True, None
        except Exception:
            return True, None  # Can't validate, assume ok


class GlyphSignalVisualizer:
    """Visualizes glyph signals as emotional gauge."""

    @staticmethod
    def render_glyph_gauge(
        signals: Dict[str, float],
        columns: int = 2,
    ) -> None:
        """Render glyph signals as visual gauges.

        Args:
            signals: Dict with voltage, tone, attunement, certainty, valence
            columns: Number of columns for layout
        """
        if not HAS_MATPLOTLIB:
            st.info("📊 Visualization requires matplotlib")
            return

        signal_items = [
            ("Arousal", signals.get("voltage", 0.5), "🔋"),
            ("Attunement", signals.get("emotional_attunement", 0.5), "💝"),
            ("Certainty", signals.get("certainty", 0.5), "💪"),
            ("Valence", signals.get("valence", 0.5), "😊"),
        ]

        cols = st.columns(columns)

        for idx, (label, value, emoji) in enumerate(signal_items):
            with cols[idx % columns]:
                # Create gauge visualization
                fig, ax = plt.subplots(figsize=(4, 2))

                # Draw gauge arc
                theta = np.linspace(np.pi, 2*np.pi, 100)
                r = 1
                x = r * np.cos(theta)
                y = r * np.sin(theta)

                ax.plot(x, y, 'k-', linewidth=2)

                # Color zones: red (low), yellow (medium), green (high)
                low_end = np.pi
                mid_point = low_end + (np.pi * value)

                # Draw indicator
                indicator_x = np.cos(mid_point)
                indicator_y = np.sin(mid_point)
                ax.arrow(0, 0, indicator_x * 0.8, indicator_y * 0.8,
                         head_width=0.1, head_length=0.1,
                         fc='darkblue', ec='darkblue', linewidth=2)

                ax.set_xlim(-1.5, 1.5)
                ax.set_ylim(-0.5, 1.5)
                ax.set_aspect('equal')
                ax.axis('off')

                plt.title(f"{emoji} {label}: {value:.2f}", fontsize=12, pad=10)
                st.pyplot(fig, use_container_width=True)
                plt.close()

    @staticmethod
    def render_emotional_timeline(
        emotional_history: list,
        max_points: int = 20,
    ) -> None:
        """Render emotional state timeline.

        Args:
            emotional_history: List of emotional_attunement values over time
            max_points: Maximum number of points to display
        """
        if not HAS_MATPLOTLIB or not emotional_history:
            return

        if len(emotional_history) > max_points:
            emotional_history = emotional_history[-max_points:]

        fig, ax = plt.subplots(figsize=(10, 3))

        x = np.arange(len(emotional_history))
        colors = ['red' if v < 0.33 else 'yellow' if v < 0.67 else 'green'
                  for v in emotional_history]

        ax.bar(x, emotional_history, color=colors,
               alpha=0.7, edgecolor='black')
        ax.axhline(y=0.5, color='gray', linestyle='--',
                   alpha=0.5, label='Neutral')
        ax.set_ylim(0, 1)
        ax.set_ylabel("Emotional Attunement")
        ax.set_xlabel("Message Number")
        ax.legend()

        plt.title("Emotional Attunement Over Time")
        st.pyplot(fig, use_container_width=True)
        plt.close()


class VoiceUIEnhancements:
    """Enhanced voice UI features for Sprint 5c."""

    def __init__(self):
        """Initialize enhancements."""
        self.edge_case_manager = EdgeCaseManager()
        self.visualizer = GlyphSignalVisualizer()
        self.emotional_history = []

    def render_glyph_visualization(
        self,
        response_text: str,
        glyph_signals: Optional[Dict[str, float]] = None,
    ) -> None:
        """Render glyph signal visualization in Streamlit.

        Args:
            response_text: Response being analyzed
            glyph_signals: Emotional signals to visualize
        """
        if not glyph_signals:
            return

        with st.expander("📊 Emotional Signal Analysis"):
            st.write(f"**Response:** {response_text[:100]}...")

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Arousal", f"{glyph_signals.get('voltage', 0):.2f}",
                          help="Energy/intensity level")
                st.metric("Attunement", f"{glyph_signals.get('emotional_attunement', 0):.2f}",
                          help="Empathy/connection level")

            with col2:
                st.metric("Certainty", f"{glyph_signals.get('certainty', 0):.2f}",
                          help="Confidence level")
                st.metric("Valence", f"{glyph_signals.get('valence', 0):.2f}",
                          help="Positive/negative sentiment")

            # Track emotional history
            self.emotional_history.append(
                glyph_signals.get("emotional_attunement", 0.5))

            if len(self.emotional_history) > 1:
                self.visualizer.render_emotional_timeline(
                    self.emotional_history)

    def handle_audio_edge_cases(
        self,
        audio_bytes: bytes,
    ) -> Tuple[bool, Optional[str]]:
        """Validate audio and handle edge cases.

        Args:
            audio_bytes: Audio data

        Returns:
            (is_valid, error_message)
        """
        # Check audio validity
        is_valid, error_msg = self.edge_case_manager.validate_audio(
            audio_bytes)
        if not is_valid:
            return is_valid, error_msg

        # Check for silence
        has_speech, silence_msg = self.edge_case_manager.handle_silence_in_audio(
            audio_bytes)
        if not has_speech:
            return False, silence_msg

        return True, None

    def handle_transcription_edge_cases(
        self,
        text: str,
        confidence: float,
    ) -> Tuple[bool, Optional[str]]:
        """Validate and handle transcription edge cases.

        Args:
            text: Transcribed text
            confidence: STT confidence

        Returns:
            (is_valid, error_message)
        """
        # Fallback for very low confidence
        if confidence < 0.3:
            return False, (
                f"⚠️ Very low confidence ({confidence:.1%})\n"
                "**Suggestions:**\n"
                "- Speak more clearly\n"
                "- Reduce background noise\n"
                "- Try again"
            )

        # Check for empty transcription
        if not text.strip():
            return False, "🤔 No speech detected"

        # Check for repeated noise (often error pattern)
        words = text.lower().split()
        if len(words) > 1:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.3:  # Too much repetition
                return False, "🔁 Repetitive noise detected - please try again"

        return True, None

    def render_fallback_ui(
        self,
        error_message: str,
    ) -> None:
        """Render graceful fallback UI for errors.

        Args:
            error_message: Error to display
        """
        with st.info():
            st.markdown(f"### ⚠️ Voice Processing Issue\n\n{error_message}")

            st.markdown("**Try these steps:**")
            suggestions = [
                "📍 Move closer to the microphone",
                "🔇 Reduce background noise",
                "🎤 Check microphone is working",
                "📝 Or use text input instead",
            ]
            for suggestion in suggestions:
                st.write(suggestion)

    def render_performance_metrics(
        self,
        latency_ms: Optional[float] = None,
        confidence: Optional[float] = None,
    ) -> None:
        """Display performance metrics.

        Args:
            latency_ms: Processing latency
            confidence: STT/TTS confidence
        """
        with st.expander("⏱️ Performance Metrics"):
            cols = st.columns(2)

            with cols[0]:
                if latency_ms:
                    latency_color = "🟢" if latency_ms < 300 else "🟡" if latency_ms < 500 else "🔴"
                    st.metric(f"{latency_color} Latency",
                              f"{latency_ms:.0f}ms")

            with cols[1]:
                if confidence:
                    conf_color = "🟢" if confidence > 0.8 else "🟡" if confidence > 0.6 else "🔴"
                    st.metric(f"{conf_color} Confidence", f"{confidence:.1%}")

            # Performance guidelines
            st.caption(
                "🟢 < 300ms (excellent) | 🟡 300-500ms (good) | 🔴 > 500ms (slow)"
            )


if __name__ == "__main__":
    # Demo
    st.set_page_config(page_title="Voice UI Enhancements Demo", page_icon="🎤")
    st.title("🎤 Voice UI Enhancements Demo")

    enhancements = VoiceUIEnhancements()

    # Demo glyph visualization
    demo_signals = {
        "voltage": 0.75,
        "emotional_attunement": 0.85,
        "certainty": 0.8,
        "valence": 0.7,
    }

    enhancements.render_glyph_visualization(
        "That's wonderful news! I'm really happy for you!",
        demo_signals
    )

    # Demo performance metrics
    enhancements.render_performance_metrics(latency_ms=245, confidence=0.92)

    # Demo error handling
    if st.checkbox("Show error handling example"):
        enhancements.render_fallback_ui(
            "No speech detected - please speak into the microphone"
        )
