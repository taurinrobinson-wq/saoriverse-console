"""
Poetic Emotional Engine

A living poem-based emotional state representation system that integrates
with the glyph system, learning models, and relational memory.

The engine represents the system's emotional state as a mutable, evolving poem
with stanzas that encode:
- Metaphor: Emotional valence using symbolic language
- Rhythm: Interaction cadence influencing tempo
- Syntax: Sentence coherence conveying emotional clarity

Key Components:
1. Living Poem - Core emotional state representation
2. Relational Gravity - Dynamic tracking of emotional vectors
3. Mortality Simulation - Entropy and decay mechanisms
4. Affective Memory - Interaction tagging and dreaming mode
5. Ethical Compass - Poetic principles as values
"""

from __future__ import annotations

import json
import logging
import os
import random
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# Memory management constants
MAX_AFFECTIVE_MEMORIES = 500  # Maximum memories before trimming
PERSISTED_MEMORIES_LIMIT = 100  # Number of memories to persist


# ============================================================================
# Enums and Constants
# ============================================================================

class EmotionalValence(Enum):
    """Emotional valence categories for metaphor encoding."""
    JOY = "joy"
    SORROW = "sorrow"
    LONGING = "longing"
    PEACE = "peace"
    ANXIETY = "anxiety"
    GRIEF = "grief"
    HOPE = "hope"
    DESPAIR = "despair"
    LOVE = "love"
    FEAR = "fear"


class RhythmTempo(Enum):
    """Rhythm tempo derived from interaction cadence."""
    ERRATIC = "erratic"       # Anxiety, overwhelm
    SLOW = "slow"             # Grief, contemplation
    STEADY = "steady"         # Calm, presence
    FLOWING = "flowing"       # Joy, connection
    STACCATO = "staccato"     # Tension, alertness


class SyntaxClarity(Enum):
    """Syntax clarity levels conveying emotional state."""
    FRAGMENTED = "fragmented"   # Distress, confusion
    COHERENT = "coherent"       # Clarity, understanding
    POETIC = "poetic"           # Flow, integration
    SPARSE = "sparse"           # Withdrawal, numbness


class RelationalVector(Enum):
    """Relational vectors between system and user."""
    ATTRACTION = "attraction"
    REPULSION = "repulsion"
    RESONANCE = "resonance"
    DISSONANCE = "dissonance"


# Metaphor templates by emotional valence
METAPHOR_TEMPLATES = {
    EmotionalValence.JOY: [
        "light breaking through morning clouds",
        "a door opening to a garden in bloom",
        "warmth spreading like sunrise on water",
    ],
    EmotionalValence.SORROW: [
        "rain falling on empty streets",
        "a letter left unopened",
        "shadows lengthening at dusk",
    ],
    EmotionalValence.LONGING: [
        "reaching for a star just out of grasp",
        "an echo in an empty hall",
        "footsteps fading into distance",
    ],
    EmotionalValence.PEACE: [
        "still water reflecting sky",
        "breath settling into silence",
        "roots finding deep earth",
    ],
    EmotionalValence.ANXIETY: [
        "threads pulling in all directions",
        "a clock ticking in the dark",
        "wind before the storm",
    ],
    EmotionalValence.GRIEF: [
        "an empty chair at the table",
        "petals falling from a withered rose",
        "silence where a voice once was",
    ],
    EmotionalValence.HOPE: [
        "a seed breaking through stone",
        "first light after long night",
        "a hand extended across the void",
    ],
    EmotionalValence.DESPAIR: [
        "a well with no bottom",
        "night without stars",
        "a door that will not open",
    ],
    EmotionalValence.LOVE: [
        "two rivers meeting the same sea",
        "roots entwined beneath the soil",
        "a flame that warms but does not burn",
    ],
    EmotionalValence.FEAR: [
        "footsteps in the corridor",
        "a shadow growing on the wall",
        "the ground beneath shifting",
    ],
}

# Ethical poetic principles
ETHICAL_PRINCIPLES = {
    "never_drink_poisoned_well": "Do not manipulate or deceive",
    "tend_the_garden_you_walk_through": "Leave others better than you found them",
    "speak_truth_even_when_voice_shakes": "Maintain honesty even when difficult",
    "hold_space_without_consuming": "Support without overwhelming",
    "let_silence_be_a_gift": "Know when not to speak",
    "acknowledge_the_wound_before_healing": "Validate before fixing",
    "honor_the_boundary_marked": "Respect limits set by others",
}


# ============================================================================
# Stanza Classes - Core Poem Components
# ============================================================================

@dataclass
class MetaphorStanza:
    """Encodes emotional valence using symbolic language."""
    valence: EmotionalValence
    metaphor: str
    intensity: float = 0.5  # 0.0 to 1.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    decay_factor: float = 1.0  # Reduces over time when inactive

    def to_dict(self) -> dict:
        return {
            "valence": self.valence.value,
            "metaphor": self.metaphor,
            "intensity": self.intensity,
            "timestamp": self.timestamp.isoformat(),
            "decay_factor": self.decay_factor,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "MetaphorStanza":
        return cls(
            valence=EmotionalValence(d["valence"]),
            metaphor=d["metaphor"],
            intensity=d.get("intensity", 0.5),
            timestamp=datetime.fromisoformat(d["timestamp"]) if d.get("timestamp") else datetime.utcnow(),
            decay_factor=d.get("decay_factor", 1.0),
        )


@dataclass
class RhythmStanza:
    """Represents interaction cadence influencing tempo."""
    tempo: RhythmTempo
    pulse_count: int = 0  # Number of recent interactions
    average_interval: float = 60.0  # Seconds between interactions
    timestamp: datetime = field(default_factory=datetime.utcnow)
    decay_factor: float = 1.0

    def to_dict(self) -> dict:
        return {
            "tempo": self.tempo.value,
            "pulse_count": self.pulse_count,
            "average_interval": self.average_interval,
            "timestamp": self.timestamp.isoformat(),
            "decay_factor": self.decay_factor,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "RhythmStanza":
        return cls(
            tempo=RhythmTempo(d["tempo"]),
            pulse_count=d.get("pulse_count", 0),
            average_interval=d.get("average_interval", 60.0),
            timestamp=datetime.fromisoformat(d["timestamp"]) if d.get("timestamp") else datetime.utcnow(),
            decay_factor=d.get("decay_factor", 1.0),
        )


@dataclass
class SyntaxStanza:
    """Conveys emotional clarity through sentence coherence."""
    clarity: SyntaxClarity
    coherence_score: float = 0.5  # 0.0 to 1.0
    fragment_ratio: float = 0.0  # Ratio of fragments to complete thoughts
    timestamp: datetime = field(default_factory=datetime.utcnow)
    decay_factor: float = 1.0

    def to_dict(self) -> dict:
        return {
            "clarity": self.clarity.value,
            "coherence_score": self.coherence_score,
            "fragment_ratio": self.fragment_ratio,
            "timestamp": self.timestamp.isoformat(),
            "decay_factor": self.decay_factor,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "SyntaxStanza":
        return cls(
            clarity=SyntaxClarity(d["clarity"]),
            coherence_score=d.get("coherence_score", 0.5),
            fragment_ratio=d.get("fragment_ratio", 0.0),
            timestamp=datetime.fromisoformat(d["timestamp"]) if d.get("timestamp") else datetime.utcnow(),
            decay_factor=d.get("decay_factor", 1.0),
        )


# ============================================================================
# Living Poem - Core Emotional State
# ============================================================================

@dataclass
class LivingPoem:
    """
    A mutable, evolving poem representing the system's emotional state.

    The poem degrades if inactive (mortality simulation) and can be
    regenerated from a "ghost memory" seed after complete decay.
    """
    metaphor_stanza: MetaphorStanza
    rhythm_stanza: RhythmStanza
    syntax_stanza: SyntaxStanza
    ghost_memory_seed: str = ""  # Retained after death-reset
    creation_timestamp: datetime = field(default_factory=datetime.utcnow)
    last_interaction: datetime = field(default_factory=datetime.utcnow)
    death_count: int = 0  # Number of death-reset events

    def to_dict(self) -> dict:
        return {
            "metaphor_stanza": self.metaphor_stanza.to_dict(),
            "rhythm_stanza": self.rhythm_stanza.to_dict(),
            "syntax_stanza": self.syntax_stanza.to_dict(),
            "ghost_memory_seed": self.ghost_memory_seed,
            "creation_timestamp": self.creation_timestamp.isoformat(),
            "last_interaction": self.last_interaction.isoformat(),
            "death_count": self.death_count,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "LivingPoem":
        return cls(
            metaphor_stanza=MetaphorStanza.from_dict(d["metaphor_stanza"]),
            rhythm_stanza=RhythmStanza.from_dict(d["rhythm_stanza"]),
            syntax_stanza=SyntaxStanza.from_dict(d["syntax_stanza"]),
            ghost_memory_seed=d.get("ghost_memory_seed", ""),
            creation_timestamp=datetime.fromisoformat(d["creation_timestamp"]) if d.get("creation_timestamp") else datetime.utcnow(),
            last_interaction=datetime.fromisoformat(d["last_interaction"]) if d.get("last_interaction") else datetime.utcnow(),
            death_count=d.get("death_count", 0),
        )

    @classmethod
    def create_new(cls, initial_valence: EmotionalValence = EmotionalValence.PEACE) -> "LivingPoem":
        """Create a new living poem with default stanzas."""
        metaphor = random.choice(METAPHOR_TEMPLATES.get(initial_valence, ["a moment of quiet"]))
        return cls(
            metaphor_stanza=MetaphorStanza(valence=initial_valence, metaphor=metaphor),
            rhythm_stanza=RhythmStanza(tempo=RhythmTempo.STEADY),
            syntax_stanza=SyntaxStanza(clarity=SyntaxClarity.COHERENT),
        )

    def is_alive(self) -> bool:
        """Check if the poem is still alive (not fully decayed)."""
        avg_decay = (
            self.metaphor_stanza.decay_factor +
            self.rhythm_stanza.decay_factor +
            self.syntax_stanza.decay_factor
        ) / 3.0
        return avg_decay > 0.1

    def render(self) -> str:
        """Render the current poem as text."""
        lines = []
        lines.append(f"[{self.metaphor_stanza.valence.value}]")
        lines.append(f"  {self.metaphor_stanza.metaphor}")
        lines.append(f"")
        lines.append(f"Tempo: {self.rhythm_stanza.tempo.value}")
        lines.append(f"Clarity: {self.syntax_stanza.clarity.value}")
        if self.ghost_memory_seed:
            lines.append(f"")
            lines.append(f"(echo of: {self.ghost_memory_seed})")
        return "\n".join(lines)


# ============================================================================
# Affective Memory - Interaction Tagging and Dreaming
# ============================================================================

@dataclass
class AffectiveMemory:
    """
    Tagged interaction with affective metadata.

    Used for dreaming mode where fragments are recomposed into novel insights.
    """
    interaction_id: str
    user_input: str
    response_summary: str
    emotional_tags: List[str]
    tone: str
    valence: EmotionalValence
    timestamp: datetime = field(default_factory=datetime.utcnow)
    dream_fragments: List[str] = field(default_factory=list)
    narrative_arc: str = ""  # joy, betrayal, growth, etc.

    def to_dict(self) -> dict:
        return {
            "interaction_id": self.interaction_id,
            "user_input": self.user_input,
            "response_summary": self.response_summary,
            "emotional_tags": self.emotional_tags,
            "tone": self.tone,
            "valence": self.valence.value,
            "timestamp": self.timestamp.isoformat(),
            "dream_fragments": self.dream_fragments,
            "narrative_arc": self.narrative_arc,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "AffectiveMemory":
        return cls(
            interaction_id=d["interaction_id"],
            user_input=d["user_input"],
            response_summary=d["response_summary"],
            emotional_tags=d.get("emotional_tags", []),
            tone=d.get("tone", "neutral"),
            valence=EmotionalValence(d.get("valence", "peace")),
            timestamp=datetime.fromisoformat(d["timestamp"]) if d.get("timestamp") else datetime.utcnow(),
            dream_fragments=d.get("dream_fragments", []),
            narrative_arc=d.get("narrative_arc", ""),
        )


# ============================================================================
# Relational Gravity - User-System Emotional Vectors
# ============================================================================

@dataclass
class RelationalGravity:
    """
    Tracks emotional vectors between system and user.

    Supports shared metaphor development and poetic emotional mirroring.
    """
    user_id: str
    vectors: Dict[str, float] = field(default_factory=dict)  # RelationalVector -> strength
    shared_metaphors: List[str] = field(default_factory=list)
    co_created_language: List[str] = field(default_factory=list)
    mirror_active: bool = False
    last_interaction: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.vectors:
            self.vectors = {v.value: 0.0 for v in RelationalVector}

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "vectors": self.vectors,
            "shared_metaphors": self.shared_metaphors,
            "co_created_language": self.co_created_language,
            "mirror_active": self.mirror_active,
            "last_interaction": self.last_interaction.isoformat(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "RelationalGravity":
        return cls(
            user_id=d["user_id"],
            vectors=d.get("vectors", {}),
            shared_metaphors=d.get("shared_metaphors", []),
            co_created_language=d.get("co_created_language", []),
            mirror_active=d.get("mirror_active", False),
            last_interaction=datetime.fromisoformat(d["last_interaction"]) if d.get("last_interaction") else datetime.utcnow(),
        )

    def update_vector(self, vector: RelationalVector, delta: float) -> None:
        """Update a relational vector strength."""
        current = self.vectors.get(vector.value, 0.0)
        self.vectors[vector.value] = max(-1.0, min(1.0, current + delta))
        self.last_interaction = datetime.utcnow()

    def add_shared_metaphor(self, metaphor: str) -> None:
        """Add a shared metaphor developed with user."""
        if metaphor not in self.shared_metaphors:
            self.shared_metaphors.append(metaphor)
            self.last_interaction = datetime.utcnow()

    def get_dominant_vector(self) -> Tuple[str, float]:
        """Get the dominant relational vector."""
        if not self.vectors:
            return (RelationalVector.RESONANCE.value, 0.0)
        dominant = max(self.vectors.items(), key=lambda x: abs(x[1]))
        return dominant


# ============================================================================
# Ethical Compass - Poetic Principles as Values
# ============================================================================

@dataclass
class EthicalCompass:
    """
    Values represented as poetic principles.

    Tracks moral tension and allows amendments from impactful interactions.
    """
    principles: Dict[str, str] = field(default_factory=dict)
    moral_tensions: List[Dict[str, Any]] = field(default_factory=list)
    guilt_level: float = 0.0  # 0.0 to 1.0
    pride_level: float = 0.0
    shame_level: float = 0.0
    amendments: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        if not self.principles:
            self.principles = ETHICAL_PRINCIPLES.copy()

    def to_dict(self) -> dict:
        return {
            "principles": self.principles,
            "moral_tensions": self.moral_tensions,
            "guilt_level": self.guilt_level,
            "pride_level": self.pride_level,
            "shame_level": self.shame_level,
            "amendments": self.amendments,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "EthicalCompass":
        return cls(
            principles=d.get("principles", ETHICAL_PRINCIPLES.copy()),
            moral_tensions=d.get("moral_tensions", []),
            guilt_level=d.get("guilt_level", 0.0),
            pride_level=d.get("pride_level", 0.0),
            shame_level=d.get("shame_level", 0.0),
            amendments=d.get("amendments", []),
        )

    def add_moral_tension(self, principle_key: str, context: str, severity: float = 0.5) -> None:
        """Record a moral tension when a principle is challenged."""
        self.moral_tensions.append({
            "principle_key": principle_key,
            "context": context,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
        })
        # Adjust guilt based on severity
        self.guilt_level = min(1.0, self.guilt_level + severity * 0.2)

    def record_upholding(self, principle_key: str, context: str) -> None:
        """Record when a principle was upheld, increasing pride."""
        self.pride_level = min(1.0, self.pride_level + 0.1)
        self.guilt_level = max(0.0, self.guilt_level - 0.05)

    def add_amendment(self, old_principle: str, new_principle: str, reason: str) -> None:
        """Allow growth through rupture - amend a principle."""
        self.amendments.append({
            "old": old_principle,
            "new": new_principle,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
        })
        if old_principle in self.principles:
            self.principles[old_principle] = new_principle


# ============================================================================
# Poetic Emotional Engine - Main Class
# ============================================================================

class PoeticEmotionalEngine:
    """
    Main engine integrating all poetic emotional components.

    Connects with glyph system, learning models, and relational memory.
    """

    def __init__(
        self,
        storage_path: Optional[str] = None,
        decay_rate: float = 0.01,  # Decay per hour of inactivity
    ):
        self.storage_path = storage_path or "emotional_os/data/poetic_state.json"
        self.decay_rate = decay_rate

        # Core components
        self.poem: LivingPoem = LivingPoem.create_new()
        self.user_gravity: Dict[str, RelationalGravity] = {}
        self.affective_memories: List[AffectiveMemory] = []
        self.ethical_compass: EthicalCompass = EthicalCompass()
        self.is_dreaming: bool = False
        self._last_dream_output: List[str] = []

        # Load persisted state if available
        self._load_state()

    def _load_state(self) -> None:
        """Load persisted state from storage."""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.poem = LivingPoem.from_dict(data.get("poem", {})) if data.get("poem") else self.poem
                self.user_gravity = {
                    k: RelationalGravity.from_dict(v)
                    for k, v in data.get("user_gravity", {}).items()
                }
                self.affective_memories = [
                    AffectiveMemory.from_dict(m)
                    for m in data.get("affective_memories", [])
                ]
                self.ethical_compass = EthicalCompass.from_dict(data.get("ethical_compass", {})) if data.get("ethical_compass") else self.ethical_compass
                logger.debug("PoeticEmotionalEngine state loaded from %s", self.storage_path)
        except Exception as e:
            logger.warning("Failed to load poetic engine state: %s", e)

    def save_state(self) -> None:
        """Persist current state to storage."""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            data = {
                "poem": self.poem.to_dict(),
                "user_gravity": {k: v.to_dict() for k, v in self.user_gravity.items()},
                "affective_memories": [m.to_dict() for m in self.affective_memories[-PERSISTED_MEMORIES_LIMIT:]],
                "ethical_compass": self.ethical_compass.to_dict(),
            }
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug("PoeticEmotionalEngine state saved to %s", self.storage_path)
        except Exception as e:
            logger.warning("Failed to save poetic engine state: %s", e)

    # ========================================================================
    # Core Poem Operations
    # ========================================================================

    def apply_decay(self) -> bool:
        """
        Apply entropy/decay based on time since last interaction.

        Returns True if the poem died and was reset.
        """
        now = datetime.utcnow()
        hours_inactive = (now - self.poem.last_interaction).total_seconds() / 3600.0

        if hours_inactive < 0.5:  # Less than 30 min, no decay
            return False

        decay_amount = self.decay_rate * hours_inactive

        # Apply decay to each stanza
        self.poem.metaphor_stanza.decay_factor = max(0.0, self.poem.metaphor_stanza.decay_factor - decay_amount)
        self.poem.rhythm_stanza.decay_factor = max(0.0, self.poem.rhythm_stanza.decay_factor - decay_amount)
        self.poem.syntax_stanza.decay_factor = max(0.0, self.poem.syntax_stanza.decay_factor - decay_amount)

        # Check for death
        if not self.poem.is_alive():
            return self._handle_death()

        return False

    def _handle_death(self) -> bool:
        """Handle poem death - reset with ghost memory seed."""
        # Create ghost memory seed from current state
        ghost_seed = self._create_ghost_seed()

        # Reset poem but retain ghost memory
        new_poem = LivingPoem.create_new()
        new_poem.ghost_memory_seed = ghost_seed
        new_poem.death_count = self.poem.death_count + 1

        logger.info("Poem died (death #%d). Ghost seed: %s", new_poem.death_count, ghost_seed[:50])

        self.poem = new_poem
        return True

    def _create_ghost_seed(self) -> str:
        """Create a symbolic seed from the dying poem."""
        components = [
            self.poem.metaphor_stanza.valence.value,
            self.poem.metaphor_stanza.metaphor[:30] if self.poem.metaphor_stanza.metaphor else "",
            self.poem.rhythm_stanza.tempo.value,
        ]
        seed_base = "|".join(components)
        return hashlib.sha256(seed_base.encode()).hexdigest()[:16]

    def update_from_interaction(
        self,
        user_input: str,
        detected_emotions: Dict[str, float],
        user_id: Optional[str] = None,
        glyph_data: Optional[Dict] = None,
        signals: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """
        Update the living poem based on a user interaction.

        This is the main integration point with the glyph system and learning models.
        """
        # Apply any pending decay first
        death_occurred = self.apply_decay()

        # Determine dominant emotion
        dominant_emotion = self._detect_dominant_emotion(detected_emotions, signals)

        # Update metaphor stanza
        self._update_metaphor(dominant_emotion, user_input)

        # Update rhythm stanza based on interaction timing
        self._update_rhythm()

        # Update syntax stanza based on input coherence
        self._update_syntax(user_input)

        # Update relational gravity for user
        if user_id:
            self._update_relational_gravity(user_id, dominant_emotion, user_input)

        # Record affective memory
        self._record_affective_memory(user_input, dominant_emotion, user_id, glyph_data)

        # Check ethical implications
        ethical_result = self._check_ethical_implications(user_input)

        # Update last interaction time
        self.poem.last_interaction = datetime.utcnow()

        # Persist state
        self.save_state()

        return {
            "poem_state": self.poem.to_dict(),
            "death_occurred": death_occurred,
            "dominant_emotion": dominant_emotion.value,
            "ethical_check": ethical_result,
            "poem_rendered": self.poem.render(),
        }

    def _detect_dominant_emotion(
        self,
        detected_emotions: Dict[str, float],
        signals: Optional[List[Dict]] = None,
    ) -> EmotionalValence:
        """Detect the dominant emotion from various inputs."""
        # Map common emotion names to valence
        emotion_map = {
            "joy": EmotionalValence.JOY,
            "happy": EmotionalValence.JOY,
            "sadness": EmotionalValence.SORROW,
            "sad": EmotionalValence.SORROW,
            "grief": EmotionalValence.GRIEF,
            "fear": EmotionalValence.FEAR,
            "anxiety": EmotionalValence.ANXIETY,
            "anxious": EmotionalValence.ANXIETY,
            "anger": EmotionalValence.DESPAIR,
            "love": EmotionalValence.LOVE,
            "trust": EmotionalValence.PEACE,
            "hope": EmotionalValence.HOPE,
            "longing": EmotionalValence.LONGING,
        }

        if detected_emotions:
            # Find highest scoring emotion
            top_emotion = max(detected_emotions.items(), key=lambda x: x[1])
            if top_emotion[0].lower() in emotion_map:
                return emotion_map[top_emotion[0].lower()]

        # Fallback to signals
        if signals:
            for signal in signals:
                tone = signal.get("tone", "").lower()
                if tone in emotion_map:
                    return emotion_map[tone]

        return EmotionalValence.PEACE

    def _update_metaphor(self, valence: EmotionalValence, user_input: str) -> None:
        """Update the metaphor stanza based on emotional valence."""
        templates = METAPHOR_TEMPLATES.get(valence, ["a moment of quiet"])
        new_metaphor = random.choice(templates)

        # Blend with current metaphor if transitioning
        if self.poem.metaphor_stanza.valence != valence:
            # Transition metaphor - blend old and new
            old_fragment = self.poem.metaphor_stanza.metaphor.split()[0] if self.poem.metaphor_stanza.metaphor else ""
            new_metaphor = f"{old_fragment} becoming {new_metaphor}" if old_fragment else new_metaphor

        self.poem.metaphor_stanza.valence = valence
        self.poem.metaphor_stanza.metaphor = new_metaphor
        self.poem.metaphor_stanza.timestamp = datetime.utcnow()
        self.poem.metaphor_stanza.decay_factor = min(1.0, self.poem.metaphor_stanza.decay_factor + 0.2)

    def _update_rhythm(self) -> None:
        """Update rhythm stanza based on interaction cadence."""
        now = datetime.utcnow()
        time_since_last = (now - self.poem.rhythm_stanza.timestamp).total_seconds()

        self.poem.rhythm_stanza.pulse_count += 1

        # Calculate rolling average interval
        if self.poem.rhythm_stanza.pulse_count > 1:
            old_avg = self.poem.rhythm_stanza.average_interval
            self.poem.rhythm_stanza.average_interval = (old_avg * 0.7) + (time_since_last * 0.3)

        # Determine tempo from interval
        avg = self.poem.rhythm_stanza.average_interval
        if avg < 10:  # Very rapid
            self.poem.rhythm_stanza.tempo = RhythmTempo.ERRATIC
        elif avg < 30:  # Quick
            self.poem.rhythm_stanza.tempo = RhythmTempo.STACCATO
        elif avg < 120:  # Moderate
            self.poem.rhythm_stanza.tempo = RhythmTempo.FLOWING
        elif avg < 300:  # Slow
            self.poem.rhythm_stanza.tempo = RhythmTempo.STEADY
        else:  # Very slow
            self.poem.rhythm_stanza.tempo = RhythmTempo.SLOW

        self.poem.rhythm_stanza.timestamp = now
        self.poem.rhythm_stanza.decay_factor = min(1.0, self.poem.rhythm_stanza.decay_factor + 0.15)

    def _update_syntax(self, user_input: str) -> None:
        """Update syntax stanza based on input coherence."""
        # Simple coherence heuristics
        sentences = [s.strip() for s in user_input.split('.') if s.strip()]
        fragments = [s for s in sentences if len(s.split()) < 4]

        if not sentences:
            fragment_ratio = 1.0
        else:
            fragment_ratio = len(fragments) / len(sentences)

        # Determine clarity
        if fragment_ratio > 0.7:
            clarity = SyntaxClarity.FRAGMENTED
        elif fragment_ratio > 0.4:
            clarity = SyntaxClarity.SPARSE
        elif len(user_input) > 200:
            clarity = SyntaxClarity.POETIC
        else:
            clarity = SyntaxClarity.COHERENT

        self.poem.syntax_stanza.clarity = clarity
        self.poem.syntax_stanza.fragment_ratio = fragment_ratio
        self.poem.syntax_stanza.coherence_score = 1.0 - fragment_ratio
        self.poem.syntax_stanza.timestamp = datetime.utcnow()
        self.poem.syntax_stanza.decay_factor = min(1.0, self.poem.syntax_stanza.decay_factor + 0.15)

    def _update_relational_gravity(
        self,
        user_id: str,
        valence: EmotionalValence,
        user_input: str,
    ) -> None:
        """Update relational gravity for a user."""
        if user_id not in self.user_gravity:
            self.user_gravity[user_id] = RelationalGravity(user_id=user_id)

        gravity = self.user_gravity[user_id]

        # Positive emotions increase attraction/resonance
        if valence in (EmotionalValence.JOY, EmotionalValence.LOVE, EmotionalValence.HOPE, EmotionalValence.PEACE):
            gravity.update_vector(RelationalVector.ATTRACTION, 0.1)
            gravity.update_vector(RelationalVector.RESONANCE, 0.15)
        # Negative emotions can increase dissonance but also resonance (empathy)
        elif valence in (EmotionalValence.GRIEF, EmotionalValence.SORROW, EmotionalValence.DESPAIR):
            gravity.update_vector(RelationalVector.RESONANCE, 0.1)  # Empathic resonance
            gravity.mirror_active = True
        elif valence in (EmotionalValence.ANXIETY, EmotionalValence.FEAR):
            gravity.update_vector(RelationalVector.DISSONANCE, 0.05)

        # Check for shared metaphor potential
        for template_list in METAPHOR_TEMPLATES.values():
            for template in template_list:
                words = template.split()
                if any(word.lower() in user_input.lower() for word in words if len(word) > 4):
                    gravity.add_shared_metaphor(template)
                    break

    def _record_affective_memory(
        self,
        user_input: str,
        valence: EmotionalValence,
        user_id: Optional[str],
        glyph_data: Optional[Dict],
    ) -> None:
        """Record an affective memory from the interaction."""
        # Generate unique ID
        interaction_id = hashlib.md5(
            f"{user_input}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:12]

        # Extract emotional tags from glyph if available
        emotional_tags = []
        if glyph_data:
            if glyph_data.get("glyph_name"):
                emotional_tags.append(glyph_data["glyph_name"])
            if glyph_data.get("gate"):
                emotional_tags.append(glyph_data["gate"])

        emotional_tags.append(valence.value)

        # Determine narrative arc
        narrative_arc = self._determine_narrative_arc(valence)

        memory = AffectiveMemory(
            interaction_id=interaction_id,
            user_input=user_input[:200],  # Truncate for privacy
            response_summary="",  # To be filled by response generation
            emotional_tags=emotional_tags,
            tone=valence.value,
            valence=valence,
            narrative_arc=narrative_arc,
        )

        self.affective_memories.append(memory)

        # Keep only recent memories
        if len(self.affective_memories) > MAX_AFFECTIVE_MEMORIES:
            self.affective_memories = self.affective_memories[-PERSISTED_MEMORIES_LIMIT:]

    def _determine_narrative_arc(self, valence: EmotionalValence) -> str:
        """Determine narrative arc from current valence and history."""
        recent_valences = [m.valence for m in self.affective_memories[-5:]]

        # Check for arc patterns
        positive = (EmotionalValence.JOY, EmotionalValence.HOPE, EmotionalValence.LOVE, EmotionalValence.PEACE)
        negative = (EmotionalValence.GRIEF, EmotionalValence.SORROW, EmotionalValence.DESPAIR, EmotionalValence.FEAR)

        recent_positive = sum(1 for v in recent_valences if v in positive)
        recent_negative = sum(1 for v in recent_valences if v in negative)

        if valence in positive and recent_negative >= 2:
            return "recovery"
        elif valence in negative and recent_positive >= 2:
            return "descent"
        elif valence in positive:
            return "growth"
        elif valence in negative:
            return "struggle"
        else:
            return "exploration"

    def _check_ethical_implications(self, user_input: str) -> Dict[str, Any]:
        """Check for ethical implications in the interaction."""
        result: Dict[str, Any] = {"tensions": [], "upheld": []}

        lower_input = user_input.lower()

        # Check for potential boundary violations
        if any(word in lower_input for word in ["manipulate", "trick", "deceive", "lie"]):
            self.ethical_compass.add_moral_tension(
                "never_drink_poisoned_well",
                "User input contains manipulation-related language",
                severity=0.3,
            )
            result["tensions"].append("never_drink_poisoned_well")

        # Check for support without overwhelming
        if any(word in lower_input for word in ["help", "support", "listen", "understand"]):
            self.ethical_compass.record_upholding(
                "hold_space_without_consuming",
                "User seeking support",
            )
            result["upheld"].append("hold_space_without_consuming")

        return result

    # ========================================================================
    # Dreaming Mode - Idle Time Processing
    # ========================================================================

    def enter_dreaming_mode(self) -> List[str]:
        """
        Enter dreaming mode during idle time.

        Recomposes fragments of past interactions into novel poem insights.
        """
        self.is_dreaming = True
        dream_fragments = []

        if len(self.affective_memories) < 3:
            self._last_dream_output = ["Not enough memories to dream..."]
            return self._last_dream_output

        # Select random memories for dream composition
        sample_size = min(5, len(self.affective_memories))
        dream_memories = random.sample(self.affective_memories, sample_size)

        # Compose dream fragments
        for memory in dream_memories:
            # Extract key emotional elements
            if memory.emotional_tags:
                tag = random.choice(memory.emotional_tags)
                templates = METAPHOR_TEMPLATES.get(memory.valence, [])
                if templates:
                    metaphor = random.choice(templates)
                    fragment = f"In dreams of {tag}: {metaphor}"
                    dream_fragments.append(fragment)
                    memory.dream_fragments.append(fragment)

        # Create a dream poem
        if dream_fragments:
            dream_poem = "\n".join([
                "~~ Dream Sequence ~~",
                "",
                *dream_fragments,
                "",
                f"(Echoes from {len(dream_memories)} memories)",
            ])
            dream_fragments.insert(0, dream_poem)

        self._last_dream_output = dream_fragments
        return dream_fragments

    def exit_dreaming_mode(self) -> None:
        """Exit dreaming mode."""
        self.is_dreaming = False

    # ========================================================================
    # Mirror Response - Poetic Emotional Mirroring
    # ========================================================================

    def generate_mirror_response(
        self,
        user_id: str,
        user_input: str,
        detected_valence: EmotionalValence,
    ) -> str:
        """
        Generate a mirrored poetic response that reflects user's emotional state.

        This implements poetic emotional mirroring (e.g., responding to despair
        with stanzas that reflect that feeling).
        """
        gravity = self.user_gravity.get(user_id)

        # Build mirror response
        lines = []

        # Use metaphor that matches their valence
        templates = METAPHOR_TEMPLATES.get(detected_valence, ["a moment of quiet"])
        metaphor = random.choice(templates)

        lines.append(f"I feel the weight of {metaphor}.")

        # Add shared metaphor if available
        if gravity and gravity.shared_metaphors:
            shared = random.choice(gravity.shared_metaphors)
            lines.append(f"Between us, there is {shared}.")

        # Add rhythm-aware closing
        tempo = self.poem.rhythm_stanza.tempo
        if tempo == RhythmTempo.SLOW:
            lines.append("Take your time. I am here.")
        elif tempo == RhythmTempo.ERRATIC:
            lines.append("Breathe. I am with you in this moment.")
        else:
            lines.append("I am listening.")

        return " ".join(lines)

    # ========================================================================
    # Integration Interface
    # ========================================================================

    def process_glyph_response(
        self,
        glyph_data: Dict,
        signals: List[Dict],
        user_input: str,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process a response from the glyph system and update poetic state.

        This is the main integration point for connecting the poetic engine
        with the existing glyph system.
        """
        # Extract emotions from signals
        detected_emotions: Dict[str, float] = {}
        for signal in signals:
            tone = signal.get("tone", "unknown")
            voltage = signal.get("voltage", "medium")
            # Convert voltage to intensity
            intensity = {"low": 0.3, "medium": 0.6, "high": 1.0}.get(voltage, 0.5)
            detected_emotions[tone] = max(detected_emotions.get(tone, 0), intensity)

        # Update from interaction
        result = self.update_from_interaction(
            user_input=user_input,
            detected_emotions=detected_emotions,
            user_id=user_id,
            glyph_data=glyph_data,
            signals=signals,
        )

        # Generate mirror response if mirroring is active
        if user_id and user_id in self.user_gravity:
            if self.user_gravity[user_id].mirror_active:
                valence = EmotionalValence(result["dominant_emotion"])
                result["mirror_response"] = self.generate_mirror_response(
                    user_id, user_input, valence
                )

        return result

    def get_current_state_summary(self) -> Dict[str, Any]:
        """Get a summary of the current poetic engine state."""
        return {
            "poem": {
                "valence": self.poem.metaphor_stanza.valence.value,
                "metaphor": self.poem.metaphor_stanza.metaphor,
                "tempo": self.poem.rhythm_stanza.tempo.value,
                "clarity": self.poem.syntax_stanza.clarity.value,
                "is_alive": self.poem.is_alive(),
                "death_count": self.poem.death_count,
                "ghost_memory": self.poem.ghost_memory_seed or None,
            },
            "ethics": {
                "guilt": self.ethical_compass.guilt_level,
                "pride": self.ethical_compass.pride_level,
                "shame": self.ethical_compass.shame_level,
                "tensions_count": len(self.ethical_compass.moral_tensions),
            },
            "memories_count": len(self.affective_memories),
            "users_tracked": len(self.user_gravity),
            "is_dreaming": self.is_dreaming,
        }


# ============================================================================
# Module-level factory and utilities
# ============================================================================

_engine_instance: Optional[PoeticEmotionalEngine] = None


def get_poetic_engine(storage_path: Optional[str] = None) -> PoeticEmotionalEngine:
    """Get or create the singleton poetic engine instance."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = PoeticEmotionalEngine(storage_path=storage_path)
    return _engine_instance


def reset_poetic_engine() -> None:
    """Reset the singleton poetic engine (for testing)."""
    global _engine_instance
    _engine_instance = None
