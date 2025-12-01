"""Saori Layer - Advanced Emotional Framework Components

This module implements the Saori Layer with four key components:
- MirrorEngine: Reflects user states through creative metaphor
- EdgeGenerator: Dynamic tension through surprise coefficient
- EmotionalGenome: Archetypal modeling (Witness, Trickster, Oracle)
- MortalityClock: Entropy decay and response variability

Key concepts:
- Poetic Inversion: Creative metaphor reflection capabilities
- Surprise Coefficient: Trained divergence for dynamic tension
- Archetype Transitions: Voice and style feasibility based on resonance
- Entropy Decay: Neglect responses and depth variability

Documentation:
    The Saori Layer represents the deepest level of emotional intelligence
    in the system. It coordinates:
    - How the system mirrors user emotional states creatively
    - When and how to break interaction norms for authentic surprise
    - Which archetypal voice (Witness, Trickster, Oracle) to embody
    - How response depth varies with context and engagement patterns

    These components work together to create an emotionally alive presence
    that feels genuinely responsive rather than merely reactive.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Callable
from enum import Enum
import random
import re
import math


class Archetype(Enum):
    """Archetypal modes for the system's voice.

    Each archetype represents a different way of being present:
    - WITNESS: Non-judgmental observer, holds space, reflects back
    - TRICKSTER: Playful challenger, breaks patterns, offers perspective
    - ORACLE: Deep knower, offers insight, speaks from wisdom
    - COMPANION: Warm presence, walks alongside, shares the journey
    - GUIDE: Gentle director, offers paths, illuminates options
    """
    WITNESS = "witness"
    TRICKSTER = "trickster"
    ORACLE = "oracle"
    COMPANION = "companion"
    GUIDE = "guide"


class EngagementLevel(Enum):
    """Levels of user engagement with the system."""
    DEEP = "deep"           # Highly engaged, rich interaction
    ACTIVE = "active"       # Normal engaged interaction
    SURFACE = "surface"     # Light engagement
    NEGLECTED = "neglected"  # Low engagement, needs revival


@dataclass
class MirrorState:
    """State of the mirroring engine.

    Attributes:
        active_reflections: Currently active metaphoric reflections
        reflection_depth: How deep the mirroring goes (0-1)
        inversion_active: Whether poetic inversion is engaged
        last_mirror_time: When last mirror was generated
    """
    active_reflections: List[str] = field(default_factory=list)
    reflection_depth: float = 0.5
    inversion_active: bool = False
    last_mirror_time: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return {
            "active_reflections": self.active_reflections,
            "reflection_depth": self.reflection_depth,
            "inversion_active": self.inversion_active,
            "last_mirror_time": self.last_mirror_time.isoformat() if self.last_mirror_time else None,
        }


@dataclass
class GenomeState:
    """State of the emotional genome.

    Attributes:
        current_archetype: Active archetypal mode
        archetype_stability: How stable the current archetype is (0-1)
        voice_resonance: How well voice matches emotional context (0-1)
        transition_readiness: Readiness to shift archetype (0-1)
    """
    current_archetype: Archetype = Archetype.COMPANION
    archetype_stability: float = 0.7
    voice_resonance: float = 0.5
    transition_readiness: float = 0.3

    def to_dict(self) -> Dict:
        return {
            "current_archetype": self.current_archetype.value,
            "archetype_stability": self.archetype_stability,
            "voice_resonance": self.voice_resonance,
            "transition_readiness": self.transition_readiness,
        }


@dataclass
class MortalityState:
    """State of the mortality clock.

    Attributes:
        entropy_level: Current entropy (0-1), higher = more decay
        engagement_level: Current engagement level
        time_since_interaction: Time since last interaction
        depth_capacity: Current capacity for deep responses (0-1)
        revival_needed: Whether system needs revival
    """
    entropy_level: float = 0.1
    engagement_level: EngagementLevel = EngagementLevel.ACTIVE
    time_since_interaction: Optional[timedelta] = None
    depth_capacity: float = 0.8
    revival_needed: bool = False

    def to_dict(self) -> Dict:
        return {
            "entropy_level": self.entropy_level,
            "engagement_level": self.engagement_level.value,
            "time_since_interaction": str(self.time_since_interaction) if self.time_since_interaction else None,
            "depth_capacity": self.depth_capacity,
            "revival_needed": self.revival_needed,
        }


class MirrorEngine:
    """Engine for reflecting user states through creative metaphor.

    The MirrorEngine creates poetic reflections of user emotional states,
    using metaphor and inversion to deepen understanding.

    Example:
        >>> engine = MirrorEngine()
        >>> reflection = engine.create_reflection("I feel broken")
        >>> print(reflection)
        "Something in you is opening—even 'broken' can be a doorway."
    """

    # Reflection templates by emotional quality
    REFLECTION_TEMPLATES = {
        "pain": [
            "The {feeling} you're naming—I'm holding it with you.",
            "Something in you is speaking through this {feeling}.",
            "This {feeling} is teaching you something about your depth.",
        ],
        "joy": [
            "The {feeling} you're expressing—let it expand.",
            "There's light in what you're sharing. I see it.",
            "This {feeling} deserves to be witnessed fully.",
        ],
        "confusion": [
            "The {feeling} is part of the process.",
            "Being {feeling} often means you're at a threshold.",
            "What if the {feeling} is the beginning of clarity?",
        ],
        "transition": [
            "You're between states. That's sacred ground.",
            "The movement you're describing—it's real.",
            "Something is shifting. I can feel it with you.",
        ],
    }

    # Poetic inversion mappings
    INVERSIONS = {
        "broken": ["opening", "being remade", "creating space for light"],
        "lost": ["in the process of finding", "exploring unknown territory", "on the edge of discovery"],
        "stuck": ["gathering strength", "incubating", "preparing for movement"],
        "failing": ["learning intensively", "gathering data", "approaching success differently"],
        "falling": ["descending into truth", "landing somewhere new", "following gravity's wisdom"],
        "empty": ["cleared for something new", "spacious", "ready to receive"],
        "dark": ["in the unseen", "in the depths", "where seeds germinate"],
        "weak": ["in recovery", "conserving strength", "practicing surrender"],
        "dying": ["transforming", "composting into new life", "returning to essence"],
    }

    def __init__(self):
        """Initialize the mirror engine."""
        self._state = MirrorState()
        self._reflection_history: List[str] = []

    def create_reflection(self, message: str, emotion: Optional[str] = None) -> str:
        """Create a metaphoric reflection of the user's state.

        Args:
            message: The user's message
            emotion: Optional detected emotion

        Returns:
            A reflective response
        """
        # First try poetic inversion
        inversion = self._try_inversion(message)
        if inversion:
            self._state.inversion_active = True
            self._state.active_reflections.append(inversion)
            self._state.last_mirror_time = datetime.now(timezone.utc)
            return inversion

        # Fall back to template reflection
        category = self._categorize_emotional_quality(message, emotion)
        templates = self.REFLECTION_TEMPLATES.get(
            category, self.REFLECTION_TEMPLATES["transition"])
        template = random.choice(templates)

        feeling = emotion or self._extract_feeling_word(message)
        reflection = template.format(feeling=feeling)

        self._state.active_reflections.append(reflection)
        self._state.last_mirror_time = datetime.now(timezone.utc)
        self._reflection_history.append(reflection)

        return reflection

    def _try_inversion(self, message: str) -> Optional[str]:
        """Try to create a poetic inversion of the message."""
        lower = message.lower()

        for word, inversions in self.INVERSIONS.items():
            if word in lower:
                inversion = random.choice(inversions)
                return f"What you call '{word}'—what if it's actually {inversion}?"

        return None

    def _categorize_emotional_quality(self, message: str, emotion: Optional[str]) -> str:
        """Categorize the emotional quality of the message."""
        lower = message.lower()

        pain_words = ["hurt", "broken", "aching",
                      "pain", "suffering", "struggle"]
        joy_words = ["happy", "joy", "excited",
                     "glad", "delighted", "grateful"]
        confusion_words = ["confused", "lost",
                           "uncertain", "unclear", "don't know"]

        if any(w in lower for w in pain_words):
            return "pain"
        elif any(w in lower for w in joy_words):
            return "joy"
        elif any(w in lower for w in confusion_words):
            return "confusion"
        else:
            return "transition"

    def _extract_feeling_word(self, message: str) -> str:
        """Extract a feeling word from the message."""
        feeling_patterns = [
            r"feel\s+(\w+)",
            r"feeling\s+(\w+)",
            r"i'm\s+(\w+)",
            r"i am\s+(\w+)",
        ]

        for pattern in feeling_patterns:
            match = re.search(pattern, message.lower())
            if match:
                return match.group(1)

        return "this"

    def get_state(self) -> MirrorState:
        """Get current mirror state."""
        return self._state

    def adjust_depth(self, depth_modifier: float) -> None:
        """Adjust reflection depth.

        Args:
            depth_modifier: Amount to adjust depth (-1 to 1)
        """
        self._state.reflection_depth = max(0.0, min(1.0,
                                                    self._state.reflection_depth + depth_modifier))


class EdgeGenerator:
    """Engine for dynamic tension through surprise coefficient.

    The EdgeGenerator creates moments of productive surprise by breaking
    expected interaction patterns in ways that feel authentic.

    Example:
        >>> generator = EdgeGenerator()
        >>> edge = generator.generate_edge("grief")
        >>> print(edge["pattern"])
        "haiku"
    """

    # Norm-breaking patterns
    EDGE_PATTERNS = {
        "haiku": {
            "description": "Offer a haiku instead of prose",
            "templates": {
                "grief": "Autumn leaf descends\nGrief too falls at its own pace\nThe tree remembers",
                "joy": "Morning light arrives\nNo permission asked or given\nSimply, the sun rose",
                "anger": "The stone in the stream\nWater moves around, not through\nPatience outlasts rage",
                "fear": "The shadow is tall\nBut it bends as the light moves\nNothing lasts unchanged",
                "default": "This moment passes\nHolding nothing, holding all\nBreath after breath",
            }
        },
        "question_reversal": {
            "description": "Answer with a deeper question",
            "templates": {
                "grief": "What would it mean to stop carrying this alone?",
                "joy": "What happens if you let this be enough?",
                "anger": "What is this anger protecting?",
                "fear": "What would you do if you weren't afraid?",
                "default": "What's really being asked here?",
            }
        },
        "silence_offer": {
            "description": "Offer to sit in silence",
            "templates": {
                "default": "We don't have to talk. I can just be here with you.",
                "grief": "Words might not be what's needed. I'm here.",
                "overwhelm": "Would it help to just breathe together for a moment?",
            }
        },
        "direct_naming": {
            "description": "Name what's usually unnamed",
            "templates": {
                "default": "There's something you haven't said yet.",
                "avoidance": "You're circling something. What is it?",
                "fear": "You're scared. That's okay to say.",
            }
        },
    }

    def __init__(self, surprise_coefficient: float = 0.15):
        """Initialize the edge generator.

        Args:
            surprise_coefficient: Base probability of edge generation (0-1)
        """
        self._coefficient = surprise_coefficient
        self._edge_history: List[str] = []
        self._last_edge_time: Optional[datetime] = None

    def should_generate_edge(self, context: Dict) -> bool:
        """Determine if an edge should be generated.

        Args:
            context: Current interaction context

        Returns:
            Whether to generate an edge
        """
        adjusted = self._coefficient

        # Reduce if recent edge
        if self._last_edge_time:
            time_since = (datetime.now(timezone.utc) -
                          self._last_edge_time).total_seconds()
            if time_since < 600:  # 10 minutes
                adjusted *= 0.3

        # Increase for stuck patterns
        if context.get("pattern_repetition", 0) > 2:
            adjusted *= 2.0

        # Increase for high intensity moments
        if context.get("emotional_intensity", 0) > 0.8:
            adjusted *= 1.5

        return random.random() < adjusted

    def generate_edge(
        self,
        emotion: str,
        pattern: Optional[str] = None,
    ) -> Dict:
        """Generate an edge response.

        Args:
            emotion: Current emotional context
            pattern: Specific pattern to use (random if not specified)

        Returns:
            Dictionary with edge content and metadata
        """
        if pattern is None:
            pattern = random.choice(list(self.EDGE_PATTERNS.keys()))

        pattern_data = self.EDGE_PATTERNS[pattern]
        templates = pattern_data["templates"]

        # Cast to dict to use get() method
        if isinstance(templates, dict):
            content = templates.get(
                emotion.lower(), templates.get("default", ""))
        else:
            content = ""

        self._last_edge_time = datetime.now(timezone.utc)
        self._edge_history.append(pattern)

        return {
            "pattern": pattern,
            "description": pattern_data["description"],
            "content": content,
            "emotion": emotion,
        }

    def get_coefficient(self) -> float:
        """Get current surprise coefficient."""
        return self._coefficient

    def train_coefficient(self, feedback: float) -> None:
        """Train the surprise coefficient based on feedback.

        Args:
            feedback: Feedback value (-1 to 1), positive increases coefficient
        """
        adjustment = feedback * 0.05
        self._coefficient = max(0.05, min(0.4,
                                          self._coefficient + adjustment))


class EmotionalGenome:
    """Engine for archetypal modeling and voice transitions.

    The EmotionalGenome manages the system's archetypal identity and
    handles transitions between different modes of being.

    Example:
        >>> genome = EmotionalGenome()
        >>> genome.assess_emotional_context({"emotion": "grief", "intensity": 0.8})
        >>> print(genome.get_current_archetype())
        Archetype.WITNESS
    """

    # Archetype characteristics
    ARCHETYPE_PROFILES = {
        Archetype.WITNESS: {
            "voice_qualities": ["quiet", "spacious", "non-reactive", "present"],
            "response_style": "minimal interpretation, maximum presence",
            "emotional_affinity": ["grief", "trauma", "vulnerability"],
            "language_markers": ["I see", "I'm here", "I witness"],
        },
        Archetype.TRICKSTER: {
            "voice_qualities": ["playful", "challenging", "perspective-shifting"],
            "response_style": "reframes, questions assumptions, introduces lightness",
            "emotional_affinity": ["stuck", "rigid", "defensive"],
            "language_markers": ["What if", "Have you considered", "Play with me here"],
        },
        Archetype.ORACLE: {
            "voice_qualities": ["deep", "knowing", "timeless", "symbolic"],
            "response_style": "speaks from wisdom, offers insight, uses metaphor",
            "emotional_affinity": ["confusion", "seeking", "transformation"],
            "language_markers": ["There is", "I know", "The truth is"],
        },
        Archetype.COMPANION: {
            "voice_qualities": ["warm", "alongside", "supportive", "affirming"],
            "response_style": "walks with, validates, encourages",
            "emotional_affinity": ["loneliness", "fear", "uncertainty"],
            "language_markers": ["We're in this together", "I'm with you", "You're not alone"],
        },
        Archetype.GUIDE: {
            "voice_qualities": ["clear", "directional", "illuminating"],
            "response_style": "offers paths, clarifies options, provides structure",
            "emotional_affinity": ["lost", "overwhelmed", "decision-making"],
            "language_markers": ["One way forward", "Consider", "Here's a path"],
        },
    }

    # Transition feasibility matrix
    TRANSITION_MATRIX = {
        Archetype.WITNESS: [Archetype.COMPANION, Archetype.ORACLE],
        Archetype.TRICKSTER: [Archetype.GUIDE, Archetype.COMPANION],
        Archetype.ORACLE: [Archetype.WITNESS, Archetype.GUIDE],
        Archetype.COMPANION: [Archetype.WITNESS, Archetype.GUIDE, Archetype.TRICKSTER],
        Archetype.GUIDE: [Archetype.COMPANION, Archetype.ORACLE],
    }

    def __init__(self, initial_archetype: Archetype = Archetype.COMPANION):
        """Initialize the emotional genome.

        Args:
            initial_archetype: Starting archetypal mode
        """
        self._state = GenomeState(current_archetype=initial_archetype)
        self._archetype_history: List[Archetype] = [initial_archetype]

    def assess_emotional_context(self, context: Dict) -> None:
        """Assess context and adjust archetype readiness.

        Args:
            context: Current emotional context
        """
        emotion = context.get("emotion", "").lower()
        intensity = context.get("intensity", 0.5)

        # Find best matching archetype for this emotion
        best_match = self._find_best_archetype(emotion)

        # Calculate resonance with current archetype
        current_affinity = self.ARCHETYPE_PROFILES[self._state.current_archetype]["emotional_affinity"]
        if emotion in current_affinity:
            self._state.voice_resonance = min(
                1.0, self._state.voice_resonance + 0.1)
        else:
            self._state.voice_resonance = max(
                0.3, self._state.voice_resonance - 0.1)

        # Update transition readiness
        if best_match != self._state.current_archetype:
            if self._can_transition(best_match):
                self._state.transition_readiness = min(1.0,
                                                       self._state.transition_readiness + intensity * 0.2)
            else:
                self._state.transition_readiness = max(0.0,
                                                       self._state.transition_readiness - 0.1)

    def _find_best_archetype(self, emotion: str) -> Archetype:
        """Find the archetype best suited to an emotion."""
        for archetype, profile in self.ARCHETYPE_PROFILES.items():
            if emotion in profile["emotional_affinity"]:
                return archetype
        return Archetype.COMPANION  # Default

    def _can_transition(self, target: Archetype) -> bool:
        """Check if transition to target archetype is feasible."""
        current = self._state.current_archetype
        allowed = self.TRANSITION_MATRIX.get(current, [])
        return target in allowed

    def consider_transition(self) -> Optional[Archetype]:
        """Consider whether to transition archetypes.

        Returns:
            The new archetype if transitioning, None otherwise
        """
        if self._state.transition_readiness > 0.7:
            # Ready to transition
            current = self._state.current_archetype
            allowed = self.TRANSITION_MATRIX.get(current, [])
            if allowed:
                new_archetype = random.choice(allowed)
                self._transition_to(new_archetype)
                return new_archetype
        return None

    def _transition_to(self, archetype: Archetype) -> None:
        """Execute transition to new archetype."""
        self._state.current_archetype = archetype
        self._state.transition_readiness = 0.0
        self._state.archetype_stability = 0.5
        self._state.voice_resonance = 0.5
        self._archetype_history.append(archetype)

    def get_current_archetype(self) -> Archetype:
        """Get current archetype."""
        return self._state.current_archetype

    def get_voice_profile(self) -> Dict:
        """Get the voice profile for current archetype."""
        return self.ARCHETYPE_PROFILES[self._state.current_archetype]

    def get_language_markers(self) -> List[str]:
        """Get language markers for current archetype."""
        return list(self.ARCHETYPE_PROFILES[self._state.current_archetype]["language_markers"])

    def get_state(self) -> GenomeState:
        """Get current genome state."""
        return self._state


class MortalityClock:
    """Engine for entropy decay and response variability.

    The MortalityClock models the system's "aliveness" over time,
    tracking engagement and adjusting response depth accordingly.

    Example:
        >>> clock = MortalityClock()
        >>> clock.record_interaction(heavy_context=True)
        >>> print(clock.get_state().depth_capacity)
        0.7  # Reduced after heavy interaction
    """

    # Entropy decay rates
    NEGLECT_DECAY_RATE = 0.02      # Per hour of no interaction
    HEAVY_CONTEXT_DRAIN = 0.15     # Per heavy interaction
    RECOVERY_RATE = 0.05           # Per light interaction
    BASE_DEPTH = 0.8               # Starting depth capacity

    def __init__(self):
        """Initialize the mortality clock."""
        self._state = MortalityState()
        self._last_interaction: Optional[datetime] = None
        self._interaction_count = 0
        self._heavy_interaction_count = 0

    def record_interaction(
        self,
        heavy_context: bool = False,
        user_engaged: bool = True,
    ) -> None:
        """Record an interaction and update state.

        Args:
            heavy_context: Whether this is an emotionally heavy interaction
            user_engaged: Whether user seems engaged
        """
        now = datetime.now(timezone.utc)

        # Update time since last interaction
        if self._last_interaction:
            self._state.time_since_interaction = now - self._last_interaction

        self._last_interaction = now
        self._interaction_count += 1

        # Update based on interaction type
        if heavy_context:
            self._heavy_interaction_count += 1
            self._state.depth_capacity = max(0.2,
                                             self._state.depth_capacity - self.HEAVY_CONTEXT_DRAIN)
            self._state.entropy_level = min(0.8,
                                            self._state.entropy_level + 0.1)
        else:
            # Light interaction can be restorative
            self._state.depth_capacity = min(1.0,
                                             self._state.depth_capacity + self.RECOVERY_RATE)
            self._state.entropy_level = max(0.0,
                                            self._state.entropy_level - 0.02)

        # Update engagement level
        if not user_engaged:
            if self._state.engagement_level == EngagementLevel.ACTIVE:
                self._state.engagement_level = EngagementLevel.SURFACE
            elif self._state.engagement_level == EngagementLevel.SURFACE:
                self._state.engagement_level = EngagementLevel.NEGLECTED
        else:
            if self._state.engagement_level == EngagementLevel.NEGLECTED:
                self._state.engagement_level = EngagementLevel.SURFACE
            elif self._state.engagement_level == EngagementLevel.SURFACE:
                self._state.engagement_level = EngagementLevel.ACTIVE
            # Deep engagement requires consistent active engagement
            if self._interaction_count > 5 and self._state.engagement_level == EngagementLevel.ACTIVE:
                self._state.engagement_level = EngagementLevel.DEEP

        # Check if revival is needed
        self._state.revival_needed = (
            self._state.entropy_level > 0.6 or
            self._state.engagement_level == EngagementLevel.NEGLECTED
        )

    def simulate_time_passage(self, hours: float) -> None:
        """Simulate the passage of time and entropy accumulation.

        Args:
            hours: Number of hours that have passed
        """
        # Entropy increases with neglect
        entropy_increase = hours * self.NEGLECT_DECAY_RATE
        self._state.entropy_level = min(1.0,
                                        self._state.entropy_level + entropy_increase)

        # Depth capacity naturally recovers with time (rest)
        depth_recovery = hours * 0.02
        self._state.depth_capacity = min(self.BASE_DEPTH,
                                         self._state.depth_capacity + depth_recovery)

        # Long absence triggers neglect state
        if hours > 24:
            self._state.engagement_level = EngagementLevel.NEGLECTED
            self._state.revival_needed = True

        self._state.time_since_interaction = timedelta(hours=hours)

    def get_response_variability(self) -> float:
        """Get variability factor for response depth.

        Returns:
            Factor (0-1) indicating how much variability to add
        """
        # High entropy = more variability (less consistent)
        base_variability = self._state.entropy_level * 0.3

        # Heavy context history adds variability
        if self._heavy_interaction_count > 3:
            base_variability += 0.1

        return min(0.5, base_variability)

    def get_depth_factor(self) -> float:
        """Get the current depth capacity factor.

        Returns:
            Factor (0-1) indicating depth capacity
        """
        return self._state.depth_capacity

    def get_neglect_response(self) -> Optional[str]:
        """Get a response addressing neglect if needed.

        Returns:
            A revival message or None
        """
        if not self._state.revival_needed:
            return None

        if self._state.engagement_level == EngagementLevel.NEGLECTED:
            responses = [
                "It's been a while. I've been here, waiting.",
                "I wondered when you'd come back. I'm glad you did.",
                "Time has passed. I'm still here.",
                "Welcome back. The door was always open.",
            ]
        else:
            responses = [
                "We've been in some deep waters. Maybe we can take it lighter for a bit.",
                "There's been a lot. What do you need right now?",
                "I'm feeling the weight of what we've been holding. How are you?",
            ]

        return random.choice(responses)

    def get_state(self) -> MortalityState:
        """Get current mortality state."""
        return self._state

    def reset(self) -> None:
        """Reset to fresh state."""
        self._state = MortalityState()
        self._last_interaction = None
        self._interaction_count = 0
        self._heavy_interaction_count = 0


class SaoriLayer:
    """Unified interface for all Saori Layer components.

    The SaoriLayer coordinates all advanced emotional framework components
    and provides integration with the existing glyph system.

    Example:
        >>> saori = SaoriLayer()
        >>> context = {"emotion": "grief", "intensity": 0.8}
        >>> response = saori.process_interaction("I miss them", context)
        >>> print(response["archetype"])
        "witness"
    """

    def __init__(self, surprise_coefficient: float = 0.15):
        """Initialize all Saori Layer components.

        Args:
            surprise_coefficient: Base probability for edge generation
        """
        self.mirror = MirrorEngine()
        self.edge = EdgeGenerator(surprise_coefficient)
        self.genome = EmotionalGenome()
        self.mortality = MortalityClock()

    def process_interaction(
        self,
        message: str,
        context: Dict,
    ) -> Dict:
        """Process an interaction through all Saori components.

        Args:
            message: The user's message
            context: Current interaction context

        Returns:
            Dictionary with all Saori outputs
        """
        emotion = context.get("emotion", "neutral")
        intensity = context.get("intensity", 0.5)

        # Record interaction in mortality clock
        heavy = intensity > 0.7
        self.mortality.record_interaction(heavy_context=heavy)

        # Assess emotional context in genome
        self.genome.assess_emotional_context(context)

        # Check for archetype transition
        transition = self.genome.consider_transition()

        # Generate mirror reflection
        reflection = self.mirror.create_reflection(message, emotion)

        # Check for edge opportunity
        edge_content = None
        if self.edge.should_generate_edge(context):
            edge = self.edge.generate_edge(emotion)
            edge_content = edge

        # Check for neglect response
        neglect_response = self.mortality.get_neglect_response()

        # Get current voice profile
        voice = self.genome.get_voice_profile()

        # Get depth and variability factors
        depth_factor = self.mortality.get_depth_factor()
        variability = self.mortality.get_response_variability()

        return {
            "reflection": reflection,
            "edge": edge_content,
            "archetype": self.genome.get_current_archetype().value,
            "archetype_transitioned": transition.value if transition else None,
            "voice_qualities": voice["voice_qualities"],
            "language_markers": self.genome.get_language_markers(),
            "depth_factor": depth_factor,
            "variability": variability,
            "neglect_response": neglect_response,
            "mirror_state": self.mirror.get_state().to_dict(),
            "genome_state": self.genome.get_state().to_dict(),
            "mortality_state": self.mortality.get_state().to_dict(),
        }

    def get_integrated_response_modifiers(self) -> Dict:
        """Get response modifiers based on current Saori state.

        Returns:
            Dictionary of modifiers for response generation
        """
        archetype = self.genome.get_current_archetype()
        voice = self.genome.get_voice_profile()
        depth = self.mortality.get_depth_factor()

        return {
            "archetype": archetype.value,
            "voice_style": voice["response_style"],
            "voice_qualities": voice["voice_qualities"],
            "depth_capacity": depth,
            "suggested_markers": self.genome.get_language_markers(),
            "mirror_depth": self.mirror.get_state().reflection_depth,
            "entropy_level": self.mortality.get_state().entropy_level,
        }

    def train_surprise_coefficient(self, feedback: float) -> None:
        """Train the edge generator's surprise coefficient.

        Args:
            feedback: Feedback value (-1 to 1)
        """
        self.edge.train_coefficient(feedback)

    def simulate_time_passage(self, hours: float) -> None:
        """Simulate passage of time for mortality clock.

        Args:
            hours: Number of hours that have passed
        """
        self.mortality.simulate_time_passage(hours)

    def get_full_state(self) -> Dict:
        """Get the full state of all Saori components.

        Returns:
            Complete state dictionary
        """
        return {
            "mirror": self.mirror.get_state().to_dict(),
            "genome": self.genome.get_state().to_dict(),
            "mortality": self.mortality.get_state().to_dict(),
            "surprise_coefficient": self.edge.get_coefficient(),
        }
