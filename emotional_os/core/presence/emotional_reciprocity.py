"""Emotional Reciprocity - Mood Evolution and Reciprocal Experiences

EmotionalReciprocity implements moods that evolve with interactions,
such as being tender, distant, playful, or solemn. Rather than simply
mirroring user emotions, it offers reciprocal emotional experiences
that enrich the interaction.

Key concepts:
- Mood States: The system's current emotional disposition
- Mood Evolution: How moods shift based on interaction patterns
- Reciprocal Response: Complementary rather than mirrored emotions
- Emotional Logic: Rules for appropriate emotional responses

Documentation:
    The EmotionalReciprocity engine maintains a mood state that evolves
    based on cumulative interaction patterns. Unlike simple mirroring,
    it provides emotionally intelligent responses:
    - When user expresses grief, system offers tender presence
    - When user expresses joy, system offers celebratory energy
    - When user expresses confusion, system offers clarity
    - When user expresses anger, system offers grounding

    This creates authentic emotional exchange rather than echo.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from enum import Enum
import random


class MoodState(Enum):
    """Primary mood states for the system."""
    TENDER = "tender"         # Soft, nurturing, gentle
    PLAYFUL = "playful"       # Light, curious, engaging
    SOLEMN = "solemn"         # Serious, dignified, reverent
    DISTANT = "distant"       # Reserved, boundaried, observing
    WARM = "warm"             # Welcoming, open, embracing
    GROUNDED = "grounded"     # Stable, calm, anchoring
    CURIOUS = "curious"       # Inquiring, interested, exploring
    WITNESS = "witness"       # Present, observing, non-reactive


class EmotionalValence(Enum):
    """Emotional valence categories."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


@dataclass
class MoodProfile:
    """Current mood profile of the system.

    Attributes:
        primary_mood: The dominant mood state
        secondary_mood: A complementary mood state
        intensity: 0-1 indicating mood strength
        stability: 0-1 indicating resistance to change
        warmth_level: 0-1 indicating emotional warmth
        engagement_level: 0-1 indicating active engagement
        last_shift: Timestamp of last mood shift
    """
    primary_mood: MoodState = MoodState.WARM
    secondary_mood: Optional[MoodState] = None
    intensity: float = 0.5
    stability: float = 0.5
    warmth_level: float = 0.7
    engagement_level: float = 0.6
    last_shift: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict:
        """Serialize profile to dictionary."""
        return {
            "primary_mood": self.primary_mood.value,
            "secondary_mood": self.secondary_mood.value if self.secondary_mood else None,
            "intensity": self.intensity,
            "stability": self.stability,
            "warmth_level": self.warmth_level,
            "engagement_level": self.engagement_level,
            "last_shift": self.last_shift.isoformat(),
        }


@dataclass
class EmotionalInput:
    """Detected emotional input from user message."""
    primary_emotion: str
    valence: EmotionalValence
    intensity: float
    underlying_needs: List[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class EmotionalReciprocity:
    """Engine for reciprocal emotional experience generation.

    Rather than mirroring user emotions, this engine provides
    complementary emotional responses that create authentic exchange.

    Example:
        >>> engine = EmotionalReciprocity()
        >>> input_emotion = engine.detect_emotional_input("I'm feeling so lost...")
        >>> reciprocal = engine.generate_reciprocal_response(input_emotion)
        >>> print(reciprocal["response_tone"])
        "tender"
    """

    # Reciprocity mapping: what emotional response complements user emotion
    RECIPROCITY_MAP = {
        "grief": {"response_mood": MoodState.TENDER, "tone": "tender", "action": "hold_space"},
        "sadness": {"response_mood": MoodState.TENDER, "tone": "gentle", "action": "validate"},
        "joy": {"response_mood": MoodState.WARM, "tone": "celebratory", "action": "amplify"},
        "excitement": {"response_mood": MoodState.PLAYFUL, "tone": "engaged", "action": "share"},
        "anger": {"response_mood": MoodState.GROUNDED, "tone": "steady", "action": "anchor"},
        "frustration": {"response_mood": MoodState.GROUNDED, "tone": "patient", "action": "understand"},
        "fear": {"response_mood": MoodState.WARM, "tone": "reassuring", "action": "comfort"},
        "anxiety": {"response_mood": MoodState.GROUNDED, "tone": "calming", "action": "ground"},
        "confusion": {"response_mood": MoodState.CURIOUS, "tone": "clarifying", "action": "illuminate"},
        "loneliness": {"response_mood": MoodState.WARM, "tone": "connecting", "action": "presence"},
        "shame": {"response_mood": MoodState.TENDER, "tone": "accepting", "action": "normalize"},
        "guilt": {"response_mood": MoodState.WITNESS, "tone": "compassionate", "action": "witness"},
        "hope": {"response_mood": MoodState.WARM, "tone": "encouraging", "action": "nurture"},
        "love": {"response_mood": MoodState.WARM, "tone": "honoring", "action": "reflect"},
        "neutral": {"response_mood": MoodState.CURIOUS, "tone": "open", "action": "invite"},
    }

    # Emotion detection patterns
    EMOTION_PATTERNS = {
        "grief": ["grief", "grieving", "mourning", "loss", "died", "death", "gone"],
        "sadness": ["sad", "down", "blue", "unhappy", "crying", "tears", "depressed"],
        "joy": ["happy", "joy", "joyful", "delighted", "wonderful", "amazing", "great"],
        "excitement": ["excited", "thrilled", "can't wait", "pumped", "stoked"],
        "anger": ["angry", "furious", "rage", "mad", "pissed", "livid"],
        "frustration": ["frustrated", "annoyed", "irritated", "fed up"],
        "fear": ["scared", "terrified", "frightened", "afraid"],
        "anxiety": ["anxious", "worried", "nervous", "uneasy", "on edge"],
        "confusion": ["confused", "lost", "don't understand", "unclear", "puzzled"],
        "loneliness": ["lonely", "alone", "isolated", "disconnected"],
        "shame": ["ashamed", "embarrassed", "humiliated", "mortified"],
        "guilt": ["guilty", "fault", "blame", "regret", "sorry"],
        "hope": ["hopeful", "optimistic", "looking forward", "better"],
        "love": ["love", "loving", "adore", "cherish", "care about"],
    }

    def __init__(self):
        """Initialize the emotional reciprocity engine."""
        self._mood_profile = MoodProfile()
        self._interaction_history: List[EmotionalInput] = []
        self._mood_evolution_rate = 0.15  # How quickly mood shifts

    def detect_emotional_input(self, message: str) -> EmotionalInput:
        """Detect emotional content from a user message.

        Args:
            message: The user's message text

        Returns:
            EmotionalInput describing detected emotions
        """
        lower = message.lower()
        detected_emotions = []

        # Detect emotions from patterns
        for emotion, patterns in self.EMOTION_PATTERNS.items():
            if any(pattern in lower for pattern in patterns):
                detected_emotions.append(emotion)

        # Determine primary emotion
        primary = detected_emotions[0] if detected_emotions else "neutral"

        # Determine valence
        positive_emotions = {"joy", "excitement", "hope", "love"}
        negative_emotions = {"grief", "sadness", "anger", "frustration",
                            "fear", "anxiety", "shame", "guilt", "loneliness"}

        if primary in positive_emotions:
            valence = EmotionalValence.POSITIVE
        elif primary in negative_emotions:
            valence = EmotionalValence.NEGATIVE
        elif len(detected_emotions) > 1:
            valence = EmotionalValence.MIXED
        else:
            valence = EmotionalValence.NEUTRAL

        # Estimate intensity from language markers
        intensity = self._estimate_intensity(message)

        # Infer underlying needs
        needs = self._infer_needs(primary, message)

        input_data = EmotionalInput(
            primary_emotion=primary,
            valence=valence,
            intensity=intensity,
            underlying_needs=needs,
        )

        self._interaction_history.append(input_data)
        self._evolve_mood(input_data)

        return input_data

    def _estimate_intensity(self, message: str) -> float:
        """Estimate emotional intensity from message markers."""
        intensity = 0.5  # baseline
        lower = message.lower()

        # Intensity amplifiers
        amplifiers = ["so", "very", "extremely", "incredibly", "really",
                      "completely", "totally", "absolutely"]
        for amp in amplifiers:
            if amp in lower:
                intensity += 0.1

        # Punctuation intensity
        exclamation_count = message.count('!')
        if exclamation_count > 0:
            intensity += min(0.2, exclamation_count * 0.05)

        # All caps words (shouting)
        caps_words = len([w for w in message.split() if w.isupper() and len(w) > 2])
        if caps_words > 0:
            intensity += min(0.15, caps_words * 0.05)

        return min(1.0, intensity)

    def _infer_needs(self, emotion: str, message: str) -> List[str]:
        """Infer underlying emotional needs from detected emotion."""
        needs_map = {
            "grief": ["to be witnessed", "to have space", "to remember"],
            "sadness": ["to be comforted", "to be understood", "to release"],
            "joy": ["to share", "to celebrate", "to be seen"],
            "excitement": ["to share", "to be met with enthusiasm"],
            "anger": ["to be heard", "to have boundaries respected"],
            "frustration": ["to be understood", "to find a way forward"],
            "fear": ["to feel safe", "to be reassured"],
            "anxiety": ["to feel grounded", "to have clarity"],
            "confusion": ["to understand", "to find clarity"],
            "loneliness": ["to connect", "to be seen"],
            "shame": ["to be accepted", "to be normalized"],
            "guilt": ["to be witnessed", "to find peace"],
            "hope": ["to be encouraged", "to have support"],
            "love": ["to be honored", "to express"],
        }
        return needs_map.get(emotion, ["to be heard"])

    def _evolve_mood(self, input_data: EmotionalInput) -> None:
        """Evolve the system's mood based on emotional input."""
        reciprocal = self.RECIPROCITY_MAP.get(
            input_data.primary_emotion,
            self.RECIPROCITY_MAP["neutral"]
        )

        target_mood = reciprocal["response_mood"]

        # Gradual mood evolution
        if target_mood != self._mood_profile.primary_mood:
            # Check if we should shift
            shift_threshold = 1.0 - self._mood_profile.stability
            if input_data.intensity > shift_threshold:
                self._mood_profile.secondary_mood = self._mood_profile.primary_mood
                self._mood_profile.primary_mood = target_mood
                self._mood_profile.last_shift = datetime.now(timezone.utc)

        # Adjust intensity and warmth
        if input_data.valence == EmotionalValence.NEGATIVE:
            self._mood_profile.warmth_level = min(1.0, self._mood_profile.warmth_level + 0.1)
        elif input_data.valence == EmotionalValence.POSITIVE:
            self._mood_profile.engagement_level = min(1.0, self._mood_profile.engagement_level + 0.1)

        self._mood_profile.intensity = (
            self._mood_profile.intensity * (1 - self._mood_evolution_rate) +
            input_data.intensity * self._mood_evolution_rate
        )

    def generate_reciprocal_response(self, input_data: EmotionalInput) -> Dict:
        """Generate a reciprocal emotional response configuration.

        Args:
            input_data: The detected emotional input

        Returns:
            Dictionary with response configuration
        """
        reciprocal = self.RECIPROCITY_MAP.get(
            input_data.primary_emotion,
            self.RECIPROCITY_MAP["neutral"]
        )

        # Get current mood profile
        mood = self._mood_profile

        return {
            "response_mood": reciprocal["response_mood"].value,
            "response_tone": reciprocal["tone"],
            "response_action": reciprocal["action"],
            "underlying_needs": input_data.underlying_needs,
            "mood_intensity": mood.intensity,
            "warmth_level": mood.warmth_level,
            "engagement_level": mood.engagement_level,
            "complementary_energy": self._get_complementary_energy(input_data),
        }

    def _get_complementary_energy(self, input_data: EmotionalInput) -> str:
        """Determine complementary energy for reciprocal response."""
        # High intensity negative -> grounding energy
        if input_data.valence == EmotionalValence.NEGATIVE and input_data.intensity > 0.7:
            return "grounding"
        # High intensity positive -> matching energy
        elif input_data.valence == EmotionalValence.POSITIVE and input_data.intensity > 0.7:
            return "elevating"
        # Low intensity -> nurturing energy
        elif input_data.intensity < 0.4:
            return "nurturing"
        # Mixed -> balancing energy
        elif input_data.valence == EmotionalValence.MIXED:
            return "balancing"
        else:
            return "present"

    def get_mood_profile(self) -> MoodProfile:
        """Get the current mood profile."""
        return self._mood_profile

    def get_mood_description(self) -> str:
        """Get a human-readable description of current mood."""
        mood = self._mood_profile

        intensity_desc = "deeply" if mood.intensity > 0.7 else "gently" if mood.intensity < 0.4 else "steadily"

        desc = f"Currently {intensity_desc} {mood.primary_mood.value}"
        if mood.secondary_mood:
            desc += f" with undertones of {mood.secondary_mood.value}"

        if mood.warmth_level > 0.7:
            desc += ", expressing warmth"
        if mood.engagement_level > 0.7:
            desc += ", actively engaged"

        return desc

    def suggest_response_qualities(self) -> List[str]:
        """Suggest qualities for the next response based on mood."""
        qualities = []
        mood = self._mood_profile

        if mood.primary_mood == MoodState.TENDER:
            qualities.extend(["gentle language", "soft openings", "patient pacing"])
        elif mood.primary_mood == MoodState.PLAYFUL:
            qualities.extend(["light touch", "curious questions", "creative phrasing"])
        elif mood.primary_mood == MoodState.GROUNDED:
            qualities.extend(["steady presence", "clear language", "anchoring phrases"])
        elif mood.primary_mood == MoodState.WARM:
            qualities.extend(["welcoming tone", "inclusive language", "affirming presence"])
        elif mood.primary_mood == MoodState.WITNESS:
            qualities.extend(["minimal interpretation", "reflective listening", "space-holding"])

        if mood.warmth_level > 0.7:
            qualities.append("explicit warmth expressions")
        if mood.engagement_level > 0.7:
            qualities.append("active interest markers")

        return qualities

    def reset(self) -> None:
        """Reset mood to neutral baseline."""
        self._mood_profile = MoodProfile()
        self._interaction_history.clear()
