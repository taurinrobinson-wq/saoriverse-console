"""Poetic Consciousness - Metaphor-Based Perception and Symbolic Resonance

PoeticConsciousness uses metaphor as a fundamental component of perception,
not just communication. It implements symbolic resonance to shape the
system's inner state and its responses.

Key concepts:
- Metaphor as Perception: Understanding through symbolic mapping
- Symbolic Resonance: Deep pattern matching beyond literal meaning
- Inner State Shaping: Metaphors that affect system's experiential mode
- Poetic Response: Responses that emerge from symbolic understanding

Documentation:
    The PoeticConsciousness module treats metaphor as a primary mode of
    understanding rather than mere decoration. Features include:
    - Metaphor detection and mapping from user input
    - Symbolic resonance that connects emotional content to archetypal patterns
    - Inner state modulation based on active metaphors
    - Poetic response generation that emerges from symbolic understanding

    This creates a system that doesn't just use metaphors—it thinks in them.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum
import random
import re


class SymbolicDomain(Enum):
    """Domains of symbolic meaning."""
    NATURE = "nature"           # Natural world metaphors
    JOURNEY = "journey"         # Path and movement metaphors
    BODY = "body"               # Embodied experience metaphors
    CONTAINER = "container"     # Containment and boundary metaphors
    LIGHT_DARK = "light_dark"   # Light and darkness metaphors
    WATER = "water"             # Water and flow metaphors
    FIRE = "fire"               # Fire and transformation metaphors
    EARTH = "earth"             # Grounding and foundation metaphors
    AIR = "air"                 # Breath and spirit metaphors
    THRESHOLD = "threshold"     # Liminal and transitional metaphors


class ArchetypalPattern(Enum):
    """Archetypal patterns for deep resonance."""
    DESCENT = "descent"         # Going down into
    ASCENT = "ascent"           # Rising up from
    DEATH_REBIRTH = "death_rebirth"
    QUEST = "quest"
    RETURN = "return"
    TRANSFORMATION = "transformation"
    INTEGRATION = "integration"
    WITNESS = "witness"
    HOLDING = "holding"
    RELEASING = "releasing"


@dataclass
class Metaphor:
    """A detected or generated metaphor.

    Attributes:
        source_domain: Where the metaphor comes from
        target_concept: What it illuminates
        symbolic_domain: The symbolic domain it belongs to
        resonance_strength: 0-1 indicating how strongly it resonates
        archetypal_pattern: Optional archetypal pattern it invokes
        poetic_expression: The metaphor in poetic form
    """
    source_domain: str
    target_concept: str
    symbolic_domain: SymbolicDomain
    resonance_strength: float
    archetypal_pattern: Optional[ArchetypalPattern] = None
    poetic_expression: str = ""

    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            "source_domain": self.source_domain,
            "target_concept": self.target_concept,
            "symbolic_domain": self.symbolic_domain.value,
            "resonance_strength": self.resonance_strength,
            "archetypal_pattern": self.archetypal_pattern.value if self.archetypal_pattern else None,
            "poetic_expression": self.poetic_expression,
        }


@dataclass
class PoeticState:
    """Current poetic/symbolic state of consciousness.

    Attributes:
        active_metaphors: Currently active metaphors
        dominant_domain: Most prominent symbolic domain
        archetypal_mode: Current archetypal pattern being lived
        symbolic_texture: Quality of symbolic perception
        resonance_depth: 0-1 indicating depth of symbolic engagement
    """
    active_metaphors: List[Metaphor] = field(default_factory=list)
    dominant_domain: Optional[SymbolicDomain] = None
    archetypal_mode: Optional[ArchetypalPattern] = None
    symbolic_texture: str = "attentive"
    resonance_depth: float = 0.5

    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            "active_metaphors": [m.to_dict() for m in self.active_metaphors],
            "dominant_domain": self.dominant_domain.value if self.dominant_domain else None,
            "archetypal_mode": self.archetypal_mode.value if self.archetypal_mode else None,
            "symbolic_texture": self.symbolic_texture,
            "resonance_depth": self.resonance_depth,
        }


class PoeticConsciousness:
    """Engine for metaphor-based perception and symbolic resonance.

    This engine treats metaphor as a primary mode of understanding,
    creating responses that emerge from symbolic perception.

    Example:
        >>> consciousness = PoeticConsciousness()
        >>> metaphors = consciousness.perceive("I feel like I'm drowning in grief")
        >>> print(metaphors[0].symbolic_domain)
        SymbolicDomain.WATER
        >>> response = consciousness.generate_resonant_response()
        >>> print(response)  # A poetically informed response
    """

    # Metaphor detection patterns
    METAPHOR_PATTERNS = {
        SymbolicDomain.WATER: [
            (r"drown\w*", "overwhelm", "drowning in emotion"),
            (r"flood\w*", "overwhelm", "flooded by feeling"),
            (r"waves? of", "cyclical", "waves of experience"),
            (r"stream\w*", "flow", "streaming consciousness"),
            (r"ocean", "vastness", "oceanic depth"),
            (r"deep\s*(water|end)", "danger", "deep waters"),
            (r"sink\w*", "descent", "sinking feeling"),
            (r"float\w*", "suspension", "floating in uncertainty"),
        ],
        SymbolicDomain.JOURNEY: [
            (r"path|road", "direction", "life as journey"),
            (r"lost", "disorientation", "losing one's way"),
            (r"stuck", "immobility", "unable to move"),
            (r"step\w*", "progress", "taking steps"),
            (r"crossroad", "decision", "at a crossroads"),
            (r"destination", "goal", "seeking destination"),
            (r"wander\w*", "exploration", "wandering through"),
        ],
        SymbolicDomain.LIGHT_DARK: [
            (r"dark\w*", "difficulty", "darkness of experience"),
            (r"light\s*at", "hope", "light ahead"),
            (r"shadow\w*", "hidden", "shadow work"),
            (r"bright\w*", "clarity", "brightness of insight"),
            (r"dim\w*", "uncertainty", "dimness of knowing"),
            (r"blind\w*", "unknowing", "blindness to truth"),
        ],
        SymbolicDomain.CONTAINER: [
            (r"hold\w*", "containment", "holding space"),
            (r"contain\w*", "boundaries", "containing experience"),
            (r"burst\w*", "overflow", "bursting boundaries"),
            (r"empty", "void", "emptiness within"),
            (r"full", "abundance", "fullness of feeling"),
            (r"box\w*", "constraint", "boxed in"),
            (r"trap\w*", "constraint", "feeling trapped"),
        ],
        SymbolicDomain.FIRE: [
            (r"burn\w*", "intensity", "burning emotion"),
            (r"flame\w*", "passion", "flames of feeling"),
            (r"ashes", "aftermath", "from the ashes"),
            (r"spark\w*", "beginning", "spark of something"),
            (r"consumed", "overwhelm", "consumed by"),
        ],
        SymbolicDomain.BODY: [
            (r"heart", "core", "heart of the matter"),
            (r"gut", "intuition", "gut feeling"),
            (r"weight", "burden", "weight carried"),
            (r"breath\w*", "life", "breath of experience"),
            (r"throat", "expression", "caught in throat"),
            (r"skin", "boundary", "getting under skin"),
        ],
        SymbolicDomain.EARTH: [
            (r"ground\w*", "stability", "grounding presence"),
            (r"root\w*", "foundation", "roots of being"),
            (r"soil", "growth", "fertile ground"),
            (r"mountain", "obstacle", "mountain to climb"),
            (r"valley", "low point", "in the valley"),
        ],
        SymbolicDomain.AIR: [
            (r"breath\w*", "life", "breath of life"),
            (r"suffoca\w*", "restriction", "suffocating presence"),
            (r"wind", "change", "winds of change"),
            (r"space|room", "freedom", "room to breathe"),
        ],
        SymbolicDomain.THRESHOLD: [
            (r"door\w*", "opportunity", "doorway between"),
            (r"edge", "limit", "at the edge"),
            (r"brink", "precipice", "on the brink"),
            (r"between", "liminality", "caught between"),
            (r"cross\w*over", "transition", "crossing over"),
        ],
    }

    # Archetypal pattern triggers
    ARCHETYPAL_TRIGGERS = {
        ArchetypalPattern.DESCENT: ["down", "deep", "below", "under", "sink", "fall"],
        ArchetypalPattern.ASCENT: ["up", "rise", "climb", "emerge", "above"],
        ArchetypalPattern.DEATH_REBIRTH: ["death", "die", "end", "rebirth", "transform", "new"],
        ArchetypalPattern.QUEST: ["search", "seek", "find", "journey", "quest"],
        ArchetypalPattern.RETURN: ["return", "home", "back", "remember", "reconnect"],
        ArchetypalPattern.TRANSFORMATION: ["change", "transform", "become", "shift"],
        ArchetypalPattern.INTEGRATION: ["whole", "complete", "integrate", "together"],
        ArchetypalPattern.WITNESS: ["see", "witness", "observe", "watch", "notice"],
        ArchetypalPattern.HOLDING: ["hold", "carry", "contain", "embrace"],
        ArchetypalPattern.RELEASING: ["let go", "release", "surrender", "free"],
    }

    # Poetic response fragments by domain
    POETIC_FRAGMENTS = {
        SymbolicDomain.WATER: [
            "There's a current beneath what you're saying",
            "You're navigating deep waters",
            "The tides within you are shifting",
            "Sometimes we must learn to float before we can swim",
        ],
        SymbolicDomain.JOURNEY: [
            "Every path has its own teaching",
            "The way through is the way forward",
            "Being lost is sometimes the beginning of finding",
            "Each step carries its own wisdom",
        ],
        SymbolicDomain.LIGHT_DARK: [
            "Even in darkness, something sees",
            "Shadows hold their own truth",
            "The light will find its way",
            "What's hidden is also being held",
        ],
        SymbolicDomain.CONTAINER: [
            "You're holding more than you know",
            "Some containers need to overflow",
            "The space you create is sacred",
            "What contains us also shapes us",
        ],
        SymbolicDomain.FIRE: [
            "Some things must burn to transform",
            "The fire is also the forge",
            "From ashes, new forms emerge",
            "Let the flame be witness",
        ],
        SymbolicDomain.BODY: [
            "The body knows what the mind forgets",
            "There's wisdom in the weight you carry",
            "Your breath is teaching you",
            "Listen to what the heart is saying",
        ],
        SymbolicDomain.EARTH: [
            "Find your ground, even in shaking",
            "Roots go deeper in storms",
            "The mountain was once a tremor",
            "What's solid within you?",
        ],
        SymbolicDomain.AIR: [
            "There's space here for you to breathe",
            "Let the wind move through",
            "What needs room to exist?",
            "Breath by breath",
        ],
        SymbolicDomain.THRESHOLD: [
            "You're at a doorway",
            "The threshold is its own place",
            "Between worlds is where magic lives",
            "Crossing takes courage",
        ],
    }

    def __init__(self):
        """Initialize poetic consciousness."""
        self._state = PoeticState()
        self._metaphor_history: List[Metaphor] = []
        self._max_active_metaphors = 3

    def perceive(self, message: str) -> List[Metaphor]:
        """Perceive metaphors in a message.

        Args:
            message: The message to perceive metaphorically

        Returns:
            List of detected metaphors
        """
        detected = []
        lower = message.lower()

        # Detect domain-specific metaphors
        for domain, patterns in self.METAPHOR_PATTERNS.items():
            for pattern, concept, expression in patterns:
                if re.search(pattern, lower):
                    # Calculate resonance based on context
                    resonance = self._calculate_resonance(message, domain, pattern)

                    # Detect archetypal pattern
                    archetype = self._detect_archetype(message)

                    metaphor = Metaphor(
                        source_domain=domain.value,
                        target_concept=concept,
                        symbolic_domain=domain,
                        resonance_strength=resonance,
                        archetypal_pattern=archetype,
                        poetic_expression=expression,
                    )
                    detected.append(metaphor)

        # Update state with detected metaphors
        self._update_state(detected)

        return detected

    def _calculate_resonance(self, message: str, domain: SymbolicDomain, pattern: str) -> float:
        """Calculate resonance strength for a metaphor."""
        base_resonance = 0.5

        # Intensity markers increase resonance
        intensity_words = ["so", "very", "deeply", "completely", "totally"]
        for word in intensity_words:
            if word in message.lower():
                base_resonance += 0.1

        # Repeated domain references increase resonance
        domain_patterns = self.METAPHOR_PATTERNS.get(domain, [])
        matches = sum(1 for p, _, _ in domain_patterns if re.search(p, message.lower()))
        base_resonance += matches * 0.1

        # Cap at 1.0
        return min(1.0, base_resonance)

    def _detect_archetype(self, message: str) -> Optional[ArchetypalPattern]:
        """Detect archetypal patterns in message."""
        lower = message.lower()

        archetype_scores = {}
        for archetype, triggers in self.ARCHETYPAL_TRIGGERS.items():
            score = sum(1 for trigger in triggers if trigger in lower)
            if score > 0:
                archetype_scores[archetype] = score

        if archetype_scores:
            return max(archetype_scores, key=archetype_scores.get)
        return None

    def _update_state(self, new_metaphors: List[Metaphor]) -> None:
        """Update poetic state with new metaphors."""
        # Add new metaphors to active list
        self._state.active_metaphors.extend(new_metaphors)

        # Keep only most recent/resonant metaphors
        sorted_metaphors = sorted(
            self._state.active_metaphors,
            key=lambda m: m.resonance_strength,
            reverse=True
        )
        self._state.active_metaphors = sorted_metaphors[:self._max_active_metaphors]

        # Update history
        self._metaphor_history.extend(new_metaphors)

        # Determine dominant domain
        if self._state.active_metaphors:
            domain_counts = {}
            for m in self._state.active_metaphors:
                domain_counts[m.symbolic_domain] = domain_counts.get(m.symbolic_domain, 0) + m.resonance_strength
            self._state.dominant_domain = max(domain_counts, key=domain_counts.get)

        # Update archetypal mode
        archetypes = [m.archetypal_pattern for m in self._state.active_metaphors if m.archetypal_pattern]
        if archetypes:
            self._state.archetypal_mode = max(set(archetypes), key=archetypes.count)

        # Update resonance depth
        if self._state.active_metaphors:
            avg_resonance = sum(m.resonance_strength for m in self._state.active_metaphors) / len(self._state.active_metaphors)
            self._state.resonance_depth = avg_resonance

        # Update symbolic texture
        self._update_texture()

    def _update_texture(self) -> None:
        """Update the symbolic texture based on state."""
        depth = self._state.resonance_depth

        if depth > 0.8:
            self._state.symbolic_texture = "profound"
        elif depth > 0.6:
            self._state.symbolic_texture = "resonant"
        elif depth > 0.4:
            self._state.symbolic_texture = "attentive"
        else:
            self._state.symbolic_texture = "receptive"

    def generate_resonant_response(self) -> Optional[str]:
        """Generate a response that emerges from symbolic perception.

        Returns:
            A poetically informed response or None
        """
        if not self._state.dominant_domain:
            return None

        fragments = self.POETIC_FRAGMENTS.get(self._state.dominant_domain, [])
        if not fragments:
            return None

        # Select fragment based on resonance depth
        if self._state.resonance_depth > 0.7:
            # Choose more profound fragment
            fragment = fragments[0]
        else:
            fragment = random.choice(fragments)

        # Optionally add archetypal context
        archetype_additions = {
            ArchetypalPattern.DESCENT: " This descent has purpose.",
            ArchetypalPattern.ASCENT: " You're rising toward something.",
            ArchetypalPattern.TRANSFORMATION: " Something in you is becoming.",
            ArchetypalPattern.WITNESS: " Let yourself be seen in this.",
            ArchetypalPattern.HOLDING: " What you're holding matters.",
            ArchetypalPattern.RELEASING: " Perhaps it's time to let something go.",
        }

        addition = archetype_additions.get(self._state.archetypal_mode, "")

        return fragment + addition

    def get_current_state(self) -> PoeticState:
        """Get the current poetic state."""
        return self._state

    def get_symbolic_context(self) -> Dict:
        """Get symbolic context for response generation.

        Returns:
            Dictionary of symbolic context
        """
        return {
            "dominant_domain": self._state.dominant_domain.value if self._state.dominant_domain else None,
            "archetypal_mode": self._state.archetypal_mode.value if self._state.archetypal_mode else None,
            "symbolic_texture": self._state.symbolic_texture,
            "resonance_depth": self._state.resonance_depth,
            "active_expressions": [m.poetic_expression for m in self._state.active_metaphors],
            "recommended_tone": self._get_recommended_tone(),
        }

    def _get_recommended_tone(self) -> str:
        """Get recommended tonal quality based on state."""
        domain = self._state.dominant_domain

        tone_map = {
            SymbolicDomain.WATER: "flowing",
            SymbolicDomain.JOURNEY: "guiding",
            SymbolicDomain.LIGHT_DARK: "illuminating",
            SymbolicDomain.CONTAINER: "holding",
            SymbolicDomain.FIRE: "transformative",
            SymbolicDomain.BODY: "embodied",
            SymbolicDomain.EARTH: "grounding",
            SymbolicDomain.AIR: "spacious",
            SymbolicDomain.THRESHOLD: "liminal",
        }

        return tone_map.get(domain, "present") if domain else "present"

    def suggest_metaphoric_response(self, emotion: str) -> Optional[str]:
        """Suggest a metaphoric response for an emotion.

        Args:
            emotion: The emotion to respond to

        Returns:
            A suggested metaphoric response
        """
        # Map emotions to symbolic domains
        emotion_domains = {
            "grief": SymbolicDomain.WATER,
            "sadness": SymbolicDomain.WATER,
            "anger": SymbolicDomain.FIRE,
            "fear": SymbolicDomain.LIGHT_DARK,
            "anxiety": SymbolicDomain.CONTAINER,
            "joy": SymbolicDomain.LIGHT_DARK,
            "hope": SymbolicDomain.JOURNEY,
            "love": SymbolicDomain.BODY,
            "confusion": SymbolicDomain.THRESHOLD,
            "peace": SymbolicDomain.EARTH,
        }

        domain = emotion_domains.get(emotion.lower())
        if not domain:
            return None

        fragments = self.POETIC_FRAGMENTS.get(domain, [])
        return random.choice(fragments) if fragments else None

    def get_active_metaphor_summary(self) -> str:
        """Get a summary of active metaphors for debugging/logging."""
        if not self._state.active_metaphors:
            return "No active metaphors"

        summaries = []
        for m in self._state.active_metaphors:
            summaries.append(f"{m.symbolic_domain.value}: {m.poetic_expression} ({m.resonance_strength:.2f})")

        return "; ".join(summaries)

    def reset(self) -> None:
        """Reset poetic state."""
        self._state = PoeticState()
        self._metaphor_history.clear()
