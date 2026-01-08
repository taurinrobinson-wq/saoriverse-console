"""Attunement Loop - Real-time Emotional Adaptation

The AttunementLoop enables dynamic adjustment to rhythm, tone, silence,
and hesitation during interactions. It links the system's emotional state
to context, allowing it to soften, hold space, or respond when appropriate.

Key concepts:
- Rhythm: The pacing and cadence of responses
- Tone: The emotional coloring of responses
- Silence: Strategic pauses that honor processing time
- Hesitation: Authentic uncertainty that builds connection

Documentation:
    The AttunementLoop continuously monitors interaction context and adjusts
    the system's response characteristics. It tracks:
    - User message pacing (fast/slow)
    - Emotional intensity patterns
    - Silence durations between exchanges
    - Turn-taking patterns

    The loop outputs attunement signals that inform response generation,
    ensuring the system's presence feels adaptive rather than robotic.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import re


class RhythmState(Enum):
    """Rhythm states for interaction pacing."""
    RAPID = "rapid"           # Fast exchanges, quick responses
    STEADY = "steady"         # Normal conversational pace
    SLOW = "slow"             # Deliberate, contemplative pace
    PAUSED = "paused"         # Extended silence, holding space


class ToneQuality(Enum):
    """Tone qualities for emotional coloring."""
    TENDER = "tender"         # Soft, gentle, nurturing
    PRESENT = "present"       # Grounded, attentive, neutral
    SUPPORTIVE = "supportive"  # Encouraging, validating
    REFLECTIVE = "reflective"  # Thoughtful, mirroring back
    SPACIOUS = "spacious"     # Open, unhurried, allowing


@dataclass
class AttunementState:
    """Current attunement state of the system.

    Attributes:
        rhythm: Current pacing state
        tone: Current emotional tone quality
        silence_weight: 0-1 indicating how much silence to incorporate
        hesitation_level: 0-1 indicating authentic uncertainty
        softening_active: Whether to soften response edges
        holding_space: Whether to prioritize presence over content
        last_updated: Timestamp of last state update
    """
    rhythm: RhythmState = RhythmState.STEADY
    tone: ToneQuality = ToneQuality.PRESENT
    silence_weight: float = 0.0
    hesitation_level: float = 0.0
    softening_active: bool = False
    holding_space: bool = False
    last_updated: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict:
        """Serialize state to dictionary."""
        return {
            "rhythm": self.rhythm.value,
            "tone": self.tone.value,
            "silence_weight": self.silence_weight,
            "hesitation_level": self.hesitation_level,
            "softening_active": self.softening_active,
            "holding_space": self.holding_space,
            "last_updated": self.last_updated.isoformat(),
        }


@dataclass
class InteractionSignal:
    """A signal from user interaction used for attunement."""
    message_length: int
    word_count: int
    punctuation_intensity: float  # 0-1 based on !?... usage
    emotional_markers: List[str]
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc))
    silence_since_last: float = 0.0  # seconds


class AttunementLoop:
    """Real-time emotional attunement engine.

    The AttunementLoop continuously processes interaction signals and
    adjusts the system's presence characteristics. It maintains a rolling
    window of recent interactions to detect patterns and adapt accordingly.

    Example:
        >>> loop = AttunementLoop()
        >>> signal = loop.process_message("I'm feeling overwhelmed today...")
        >>> state = loop.get_current_state()
        >>> print(state.tone)
        ToneQuality.TENDER
    """

    def __init__(self, window_size: int = 10):
        """Initialize the attunement loop.

        Args:
            window_size: Number of recent interactions to consider
        """
        self._window_size = window_size
        self._signal_history: List[InteractionSignal] = []
        self._state = AttunementState()
        self._last_interaction_time: Optional[datetime] = None

    def process_message(self, message: str, timestamp: Optional[datetime] = None) -> InteractionSignal:
        """Process an incoming message and update attunement state.

        Args:
            message: The user's message text
            timestamp: Optional timestamp (defaults to now)

        Returns:
            The extracted interaction signal
        """
        now = timestamp or datetime.now(timezone.utc)

        # Calculate silence duration since last interaction
        silence_duration = 0.0
        if self._last_interaction_time:
            silence_duration = (
                now - self._last_interaction_time).total_seconds()

        # Extract signal from message
        signal = self._extract_signal(message, now, silence_duration)
        self._signal_history.append(signal)

        # Maintain window size
        if len(self._signal_history) > self._window_size:
            self._signal_history.pop(0)

        # Update attunement state based on signal history
        self._update_state()
        self._last_interaction_time = now

        return signal

    def _extract_signal(self, message: str, timestamp: datetime, silence_duration: float) -> InteractionSignal:
        """Extract an interaction signal from a message."""
        words = message.split()
        word_count = len(words)

        # Calculate punctuation intensity
        punct_count = len(re.findall(r'[!?…\.]{2,}|[!?]', message))
        punct_intensity = min(1.0, punct_count / max(1, word_count) * 2)

        # Extract emotional markers
        emotional_markers = self._extract_emotional_markers(message)

        return InteractionSignal(
            message_length=len(message),
            word_count=word_count,
            punctuation_intensity=punct_intensity,
            emotional_markers=emotional_markers,
            timestamp=timestamp,
            silence_since_last=silence_duration,
        )

    def _extract_emotional_markers(self, message: str) -> List[str]:
        """Extract emotional marker words from message."""
        markers = []
        lower = message.lower()

        # Intensity markers
        intensity_words = ["overwhelmed", "exhausted", "terrified", "ecstatic",
                           "devastated", "furious", "elated", "crushed"]
        for word in intensity_words:
            if word in lower:
                markers.append(f"intensity:{word}")

        # Vulnerability markers
        vuln_words = ["scared", "afraid", "anxious", "worried", "hurt",
                      "alone", "lost", "confused", "stuck"]
        for word in vuln_words:
            if word in lower:
                markers.append(f"vulnerability:{word}")

        # Processing markers
        proc_words = ["thinking", "processing", "trying", "figuring",
                      "understanding", "working through"]
        for phrase in proc_words:
            if phrase in lower:
                markers.append(f"processing:{phrase}")

        return markers

    def _update_state(self) -> None:
        """Update attunement state based on signal history."""
        if not self._signal_history:
            return

        recent = self._signal_history[-3:] if len(
            self._signal_history) >= 3 else self._signal_history

        # Analyze rhythm from message timing and length
        avg_length = sum(s.message_length for s in recent) / len(recent)
        avg_silence = sum(s.silence_since_last for s in recent) / len(recent)

        if avg_silence > 60:  # More than a minute between messages
            self._state.rhythm = RhythmState.PAUSED
        elif avg_silence > 20:
            self._state.rhythm = RhythmState.SLOW
        elif avg_length < 50:  # Short, rapid messages
            self._state.rhythm = RhythmState.RAPID
        else:
            self._state.rhythm = RhythmState.STEADY

        # Analyze tone from emotional markers
        all_markers = []
        for s in recent:
            all_markers.extend(s.emotional_markers)

        intensity_count = sum(
            1 for m in all_markers if m.startswith("intensity:"))
        vuln_count = sum(
            1 for m in all_markers if m.startswith("vulnerability:"))
        proc_count = sum(1 for m in all_markers if m.startswith("processing:"))

        if vuln_count > 0:
            self._state.tone = ToneQuality.TENDER
            self._state.softening_active = True
        elif intensity_count > 1:
            self._state.tone = ToneQuality.SUPPORTIVE
            self._state.holding_space = True
        elif proc_count > 0:
            self._state.tone = ToneQuality.REFLECTIVE
        elif avg_silence > 30:
            self._state.tone = ToneQuality.SPACIOUS
        else:
            self._state.tone = ToneQuality.PRESENT
            self._state.softening_active = False

        # Calculate silence weight
        self._state.silence_weight = min(1.0, avg_silence / 60)

        # Calculate hesitation level based on uncertainty markers
        uncertainty_phrases = ["not sure", "maybe", "i think", "i don't know"]
        latest = self._signal_history[-1] if self._signal_history else None
        if latest:
            # Check message content would require original text; approximate via markers
            self._state.hesitation_level = 0.2 if proc_count > 0 else 0.0

        self._state.last_updated = datetime.now(timezone.utc)

    def get_current_state(self) -> AttunementState:
        """Get the current attunement state."""
        return self._state

    def get_response_modifiers(self) -> Dict[str, Any]:
        """Get modifiers to apply to response generation.

        Returns:
            Dictionary of response modifiers based on current state
        """
        state = self._state

        modifiers = {
            "add_pause_phrases": state.silence_weight > 0.5,
            "soften_assertions": state.softening_active,
            "reduce_questions": state.holding_space,
            "use_shorter_sentences": state.rhythm == RhythmState.SLOW,
            "match_energy": state.rhythm.value,
            "tone_quality": state.tone.value,
            "hesitation_phrases": state.hesitation_level > 0.3,
        }

        return modifiers

    def suggest_response_pacing(self) -> Tuple[str, float]:
        """Suggest response pacing based on current state.

        Returns:
            Tuple of (pacing_style, delay_factor) where delay_factor
            is a multiplier for artificial response delay
        """
        rhythm = self._state.rhythm

        if rhythm == RhythmState.PAUSED:
            return ("deliberate", 2.0)
        elif rhythm == RhythmState.SLOW:
            return ("measured", 1.5)
        elif rhythm == RhythmState.RAPID:
            return ("responsive", 0.8)
        else:
            return ("natural", 1.0)

    def reset(self) -> None:
        """Reset the attunement loop to initial state."""
        self._signal_history.clear()
        self._state = AttunementState()
        self._last_interaction_time = None
