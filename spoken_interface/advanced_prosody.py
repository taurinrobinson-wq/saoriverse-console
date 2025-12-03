"""Advanced Prosody Features for Emotional Fidelity

Enhanced prosody with breathiness, micro-pauses, emphasis placement,
and emotional continuity tracking.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import re


class BreathStyle(Enum):
    """Breathing characteristics."""
    NORMAL = "normal"        # Standard breathing
    SHALLOW = "shallow"      # Anxious, tense (less breath)
    DEEP = "deep"            # Confident, thoughtful (more breath)
    GASPING = "gasping"      # Excited, surprised (quick breath)


class EmphasisType(Enum):
    """Types of emphasis to apply."""
    STRESS = "stress"              # Primary stress
    SECONDARY = "secondary"        # Secondary stress
    EMOTIONAL = "emotional"        # Emotional emphasis
    CONTRASTIVE = "contrastive"    # Contrast with alternatives


@dataclass
class EmphasisPoint:
    """Location and type of emphasis."""

    word_index: int
    """Index of word to emphasize."""

    type: EmphasisType
    """Type of emphasis."""

    intensity: float
    """0-1 intensity of emphasis."""


@dataclass
class MicroPause:
    """Strategic pause for emotional effect."""

    position: int
    """Character index for pause."""

    duration_ms: int
    """Pause duration in milliseconds."""

    purpose: str
    """Why: 'reflection', 'emphasis', 'breath', 'emotion'."""


@dataclass
class AdvancedProsodyPlan:
    """Extended prosody with emotional nuance."""

    base_rate: float
    """Base speaking rate."""

    pitch_contour: List[Tuple[float, float]]
    """(time_ratio, pitch_shift_semitones) pairs for dynamic pitch."""

    energy_contour: List[Tuple[float, float]]
    """(time_ratio, energy_level) pairs for dynamic energy."""

    emphasis_points: List[EmphasisPoint]
    """Where and how to emphasize."""

    micro_pauses: List[MicroPause]
    """Strategic pauses for effect."""

    breath_style: BreathStyle
    """Overall breathing style."""

    breathiness: float
    """0-1 amount of breathiness/air sounds."""

    emotion_continuity: float
    """0-1 how consistent to maintain emotional tone."""

    metadata: Dict = field(default_factory=dict)
    """Additional context."""


class AdvancedProsodyPlanner:
    """Plans prosody with emotional nuance and sophistication."""

    def __init__(self):
        """Initialize advanced planner."""
        self.tone_emphasis_map = {
            "excited": ["words", "with", "high", "energy"],
            "calm": ["reflective", "measured", "thoughtful"],
            "sad": ["closing", "final", "quiet"],
            "curious": ["new", "interesting", "unexpected"],
            "confident": ["certainly", "clearly", "obviously"],
            "uncertain": ["perhaps", "maybe", "might"],
        }

    def plan_advanced_prosody(
        self,
        text: str,
        voltage: float,
        tone: str,
        attunement: float,
        certainty: float,
    ) -> AdvancedProsodyPlan:
        """Create advanced prosody plan with emotional nuance.

        Args:
            text: Response text
            voltage: 0-1 arousal
            tone: Emotional tone
            attunement: 0-1 empathy level
            certainty: 0-1 confidence

        Returns:
            Advanced prosody plan with nuanced features
        """
        words = text.split()

        # Build pitch contour (dynamic changes over time)
        pitch_contour = self._build_pitch_contour(
            words, voltage, tone, certainty
        )

        # Build energy contour (volume dynamics)
        energy_contour = self._build_energy_contour(
            words, voltage, tone
        )

        # Identify emphasis points
        emphasis_points = self._identify_emphasis_points(
            words, tone, attunement
        )

        # Place micro-pauses for effect
        micro_pauses = self._place_micro_pauses(
            text, tone, attunement
        )

        # Determine breathing style
        breath_style = self._get_breath_style(voltage, tone)

        return AdvancedProsodyPlan(
            base_rate=1.0 + (voltage * 0.3 - 0.15),  # -15% to +30%
            pitch_contour=pitch_contour,
            energy_contour=energy_contour,
            emphasis_points=emphasis_points,
            micro_pauses=micro_pauses,
            breath_style=breath_style,
            breathiness=self._get_breathiness(voltage, tone),
            emotion_continuity=attunement,
            metadata={
                "voltage": voltage,
                "tone": tone,
                "word_count": len(words),
                "text": text,
            }
        )

    def _build_pitch_contour(
        self,
        words: List[str],
        voltage: float,
        tone: str,
        certainty: float,
    ) -> List[Tuple[float, float]]:
        """Build dynamic pitch contour across text.

        Args:
            words: List of words
            voltage: Arousal level
            tone: Emotional tone
            certainty: Confidence level

        Returns:
            List of (time_ratio, pitch_shift) tuples
        """
        n_words = len(words)
        contour = [(0.0, 0.0)]  # Start at baseline

        # Mid-point pitch shift based on tone
        mid_pitch = self._get_tone_pitch(tone)
        contour.append((0.5, mid_pitch))

        # Terminal pitch based on certainty
        if certainty < 0.3:
            terminal_pitch = mid_pitch + 3  # Rising (questioning)
        elif certainty > 0.7:
            terminal_pitch = mid_pitch - 2  # Falling (assertive)
        else:
            terminal_pitch = mid_pitch  # Mid (neutral)

        contour.append((1.0, terminal_pitch))

        return contour

    def _build_energy_contour(
        self,
        words: List[str],
        voltage: float,
        tone: str,
    ) -> List[Tuple[float, float]]:
        """Build dynamic energy (loudness) contour.

        Args:
            words: List of words
            voltage: Arousal level
            tone: Emotional tone

        Returns:
            List of (time_ratio, energy_level) tuples
        """
        base_energy = 0.7 + (voltage * 0.3)  # 0.7 to 1.0

        # Exclamatory tones should start high and fade
        if tone in ["excited", "surprised"]:
            return [
                (0.0, base_energy + 0.3),
                (0.3, base_energy + 0.2),
                (1.0, base_energy),
            ]

        # Sad tones should fade over time
        elif tone in ["sad", "disappointed"]:
            return [
                (0.0, base_energy),
                (0.7, base_energy - 0.1),
                (1.0, base_energy - 0.2),
            ]

        # Most tones: smooth variation
        else:
            return [
                (0.0, base_energy - 0.1),
                (0.5, base_energy),
                (1.0, base_energy - 0.05),
            ]

    def _identify_emphasis_points(
        self,
        words: List[str],
        tone: str,
        attunement: float,
    ) -> List[EmphasisPoint]:
        """Identify words to emphasize.

        Args:
            words: List of words
            tone: Emotional tone
            attunement: Empathy level (higher = more emphasis on emotional words)

        Returns:
            List of emphasis points
        """
        emphasis_points = []

        # High attunement: emphasize emotional impact words
        if attunement > 0.7:
            emotional_words = {
                "excited": ["really", "so", "very", "absolutely"],
                "sad": ["really", "terribly", "quite", "rather"],
                "curious": ["fascinating", "interesting", "remarkable"],
            }

            target_words = emotional_words.get(tone, [])
            for i, word in enumerate(words):
                if word.lower() in target_words:
                    emphasis_points.append(EmphasisPoint(
                        word_index=i,
                        type=EmphasisType.EMOTIONAL,
                        intensity=attunement
                    ))

        # Always emphasize first content word
        if words:
            for i, word in enumerate(words):
                if len(word) > 2:  # Skip articles/prepositions
                    emphasis_points.append(EmphasisPoint(
                        word_index=i,
                        type=EmphasisType.STRESS,
                        intensity=0.7
                    ))
                    break

        return emphasis_points

    def _place_micro_pauses(
        self,
        text: str,
        tone: str,
        attunement: float,
    ) -> List[MicroPause]:
        """Place strategic micro-pauses for effect.

        Args:
            text: Response text
            tone: Emotional tone
            attunement: Empathy level

        Returns:
            List of micro-pauses
        """
        pauses = []

        # Pauses after sentences
        sentence_endings = [".", "!", "?"]
        for i, char in enumerate(text):
            if char in sentence_endings:
                duration = 200 if char == "?" else 150
                pauses.append(MicroPause(
                    position=i,
                    duration_ms=duration,
                    purpose="sentence_end"
                ))

        # Reflective pauses for thoughtful tones
        if tone in ["calm", "thoughtful", "concerned"]:
            # Add pause before important clauses
            clause_markers = [",", ";"]
            for i, char in enumerate(text):
                if char in clause_markers and attunement > 0.5:
                    pauses.append(MicroPause(
                        position=i,
                        duration_ms=100,
                        purpose="reflection"
                    ))

        # Emotional emphasis pauses
        if attunement > 0.7:
            # Before emotional keywords
            keywords = ["however", "but", "importantly", "remember"]
            for keyword in keywords:
                idx = text.lower().find(keyword)
                if idx != -1:
                    pauses.append(MicroPause(
                        position=idx,
                        duration_ms=150,
                        purpose="emotion"
                    ))

        return pauses

    def _get_breath_style(self, voltage: float, tone: str) -> BreathStyle:
        """Determine breathing style from emotional state.

        Args:
            voltage: Arousal level
            tone: Emotional tone

        Returns:
            Breathing style
        """
        if tone == "excited" or (tone == "surprised" and voltage > 0.7):
            return BreathStyle.GASPING
        elif voltage < 0.3 or tone in ["sad", "calm"]:
            return BreathStyle.SHALLOW
        elif voltage > 0.8:
            return BreathStyle.DEEP
        else:
            return BreathStyle.NORMAL

    def _get_breathiness(self, voltage: float, tone: str) -> float:
        """Calculate breathiness level.

        Args:
            voltage: Arousal level
            tone: Emotional tone

        Returns:
            Breathiness 0-1
        """
        base = 0.3

        if tone == "excited":
            return min(1.0, base + voltage * 0.5)
        elif tone in ["sad", "exhausted"]:
            return min(1.0, base + 0.3)
        else:
            return base

    def _get_tone_pitch(self, tone: str) -> float:
        """Get pitch shift for emotional tone.

        Args:
            tone: Emotional tone

        Returns:
            Pitch shift in semitones (-12 to +12)
        """
        tone_map = {
            "excited": 3,
            "happy": 2,
            "curious": 1,
            "neutral": 0,
            "concerned": -1,
            "sad": -2,
            "angry": 2,  # Higher pitch but with aggression
            "calm": -1,
            "thoughtful": -1,
        }
        return float(tone_map.get(tone, 0))


class EmotionalContinuityTracker:
    """Tracks emotional state across multiple responses."""

    def __init__(self):
        """Initialize tracker."""
        self.response_history: List[Dict] = []

    def add_response(
        self,
        text: str,
        voltage: float,
        tone: str,
        attunement: float,
    ) -> None:
        """Add response to history.

        Args:
            text: Response text
            voltage: Arousal level
            tone: Emotional tone
            attunement: Empathy level
        """
        self.response_history.append({
            "text": text,
            "voltage": voltage,
            "tone": tone,
            "attunement": attunement,
        })

    def get_emotional_continuity_score(self) -> float:
        """Calculate how consistent emotional tone has been.

        Returns:
            Score 0-1 (0=variable, 1=very consistent)
        """
        if len(self.response_history) < 2:
            return 0.5

        voltages = [r["voltage"] for r in self.response_history]
        tones = [r["tone"] for r in self.response_history]
        attunements = [r["attunement"] for r in self.response_history]

        voltage_variance = np.std(voltages) if len(voltages) > 1 else 0
        attunement_variance = np.std(
            attunements) if len(attunements) > 1 else 0

        # Tone consistency (number of tone changes)
        tone_changes = sum(1 for i in range(1, len(tones))
                           if tones[i] != tones[i-1])
        tone_consistency = 1.0 - (tone_changes / len(tones))

        # Combine metrics
        consistency = (
            (1.0 - voltage_variance / 0.5) * 0.3 +
            (1.0 - attunement_variance / 0.5) * 0.3 +
            tone_consistency * 0.4
        )

        return max(0.0, min(1.0, consistency))


# Import numpy for std calculation
try:
    import numpy as np
except ImportError:
    np = None


if __name__ == "__main__":
    planner = AdvancedProsodyPlanner()

    # Example: Excited but empathetic response
    plan = planner.plan_advanced_prosody(
        text="That's wonderful news! I'm really excited for you!",
        voltage=0.8,
        tone="excited",
        attunement=0.9,
        certainty=0.9,
    )

    print("Advanced Prosody Plan:")
    print(f"  Base rate: {plan.base_rate:.2f}x")
    print(f"  Breathiness: {plan.breathiness:.2f}")
    print(f"  Breath style: {plan.breath_style.value}")
    print(f"  Emphasis points: {len(plan.emphasis_points)}")
    print(f"  Micro-pauses: {len(plan.micro_pauses)}")
    print(f"  Emotion continuity: {plan.emotion_continuity:.2f}")
