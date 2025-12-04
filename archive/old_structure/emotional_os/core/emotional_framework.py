"""Emotional Framework Integration - Bridging New Components with Existing System

This module provides the EmotionalFramework class which integrates all
advanced emotional components:
- Presence Architecture (attunement, reciprocity, temporal memory, embodiment, poetic)
- Generative Tension (surprise, challenge, subversion, creation)
- Saori Layer (mirror, edge, genome, mortality)

It wraps the existing signal_parser to enhance responses with:
- Real-time attunement to interaction rhythm and tone
- Reciprocal emotional experiences beyond mirroring
- Temporal memory for emotional continuity
- Embodied simulation with fatigue/overload
- Poetic consciousness with metaphor-based perception
- Generative tension for dynamic engagement
- Saori Layer archetypes and voice modulation

Documentation:
    The EmotionalFramework class is the main integration point for extending
    emotional processing. It works alongside the existing parse_input function
    by wrapping and enriching its output with the new emotional constructs.

    Usage:
        >>> from emotional_os.core.emotional_framework import EmotionalFramework
        >>> framework = EmotionalFramework()
        >>> result = framework.process_message("I'm feeling overwhelmed")
        >>> print(result["enhanced_response"])  # Enriched with presence/tension
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import logging

# Import existing signal parser functionality
from emotional_os.core.signal_parser import (
    parse_input,
    load_signal_map,
    parse_signals,
    evaluate_gates,
)

# Import Presence Architecture components
from emotional_os.core.presence import (
    AttunementLoop,
    EmotionalReciprocity,
    TemporalMemory,
    EmbodiedSimulation,
    PoeticConsciousness,
)
from emotional_os.core.presence.embodied_simulation import InteractionLoad
from emotional_os.core.presence.temporal_memory import EmotionalArc, EmotionalSignificance

# Import Generative Tension components
from emotional_os.core.tension import GenerativeTension

# Import Saori Layer components
from emotional_os.core.saori import SaoriLayer

logger = logging.getLogger(__name__)


@dataclass
class FrameworkState:
    """Current state of the emotional framework.

    Attributes:
        session_id: Current session identifier
        interaction_count: Number of interactions in session
        last_emotion: Most recent detected emotion
        attunement_active: Whether attunement loop is active
        reciprocity_active: Whether reciprocity engine is active
        temporal_active: Whether temporal memory is active
        embodiment_active: Whether embodiment simulation is active
        poetic_active: Whether poetic consciousness is active
        tension_active: Whether generative tension is active
        saori_active: Whether Saori Layer is active
    """
    session_id: str = ""
    interaction_count: int = 0
    last_emotion: str = "neutral"
    attunement_active: bool = True
    reciprocity_active: bool = True
    temporal_active: bool = True
    embodiment_active: bool = True
    poetic_active: bool = True
    tension_active: bool = True
    saori_active: bool = True

    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            "session_id": self.session_id,
            "interaction_count": self.interaction_count,
            "last_emotion": self.last_emotion,
            "components": {
                "attunement": self.attunement_active,
                "reciprocity": self.reciprocity_active,
                "temporal": self.temporal_active,
                "embodiment": self.embodiment_active,
                "poetic": self.poetic_active,
                "tension": self.tension_active,
                "saori": self.saori_active,
            }
        }


class EmotionalFramework:
    """Unified emotional framework integrating all advanced components.

    This class coordinates all emotional processing components to provide
    a rich, dynamic emotional experience that goes beyond simple response
    generation. It wraps and enhances the existing signal_parser output.

    Example:
        >>> framework = EmotionalFramework()
        >>> result = framework.process_message(
        ...     message="I feel like I'm drowning in grief",
        ...     user_id="user123"
        ... )
        >>> print(result["archetype"])
        "witness"
        >>> print(result["enhanced_response"])
        # Rich response with attunement, reciprocity, and poetic elements
    """

    def __init__(
        self,
        surprise_coefficient: float = 0.15,
        enable_all: bool = True,
        lexicon_path: str = "emotional_os/parser/signal_lexicon.json",
        db_path: str = "emotional_os/glyphs/glyphs.db",
    ):
        """Initialize the emotional framework.

        Args:
            surprise_coefficient: Base probability for surprise generation
            enable_all: Whether to enable all components by default
            lexicon_path: Path to signal lexicon
            db_path: Path to glyph database
        """
        self._lexicon_path = lexicon_path
        self._db_path = db_path

        # Initialize state
        self._state = FrameworkState()

        # Initialize Presence Architecture components
        self._attunement = AttunementLoop()
        self._reciprocity = EmotionalReciprocity()
        self._temporal = TemporalMemory()
        self._embodiment = EmbodiedSimulation()
        self._poetic = PoeticConsciousness()

        # Initialize Generative Tension
        self._tension = GenerativeTension(surprise_coefficient)

        # Initialize Saori Layer
        self._saori = SaoriLayer(surprise_coefficient)

        # Set component activation based on enable_all
        if not enable_all:
            self._state.attunement_active = False
            self._state.reciprocity_active = False
            self._state.temporal_active = False
            self._state.embodiment_active = False
            self._state.poetic_active = False
            self._state.tension_active = False
            self._state.saori_active = False

    def start_session(self, user_id: Optional[str] = None) -> str:
        """Start a new emotional session.

        Args:
            user_id: Optional user identifier for temporal memory

        Returns:
            The new session ID
        """
        session_id = self._temporal.start_session(user_id)
        self._state.session_id = session_id
        self._state.interaction_count = 0

        # Reset components for new session
        self._attunement.reset()
        self._embodiment.reset()
        self._poetic.reset()

        return session_id

    def process_message(
        self,
        message: str,
        user_id: Optional[str] = None,
        conversation_context: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Process a message through the full emotional framework.

        This method:
        1. Runs existing parse_input for base processing
        2. Applies Presence Architecture components
        3. Applies Generative Tension
        4. Applies Saori Layer
        5. Generates enhanced response

        Args:
            message: The user's message
            user_id: Optional user identifier
            conversation_context: Optional conversation context

        Returns:
            Dictionary with all processing outputs and enhanced response
        """
        self._state.interaction_count += 1
        conversation_context = conversation_context or {}

        # Step 1: Run base signal parser
        base_result = parse_input(
            message,
            self._lexicon_path,
            self._db_path,
            conversation_context,
            user_id
        )

        # Extract base information
        signals = base_result.get("signals", [])
        base_response = base_result.get("voltage_response", "")
        primary_emotion = self._extract_primary_emotion(signals)
        self._state.last_emotion = primary_emotion

        # Step 2: Apply Presence Architecture
        presence_output: Dict[str, Any] = {}
        if self._state.attunement_active:
            self._attunement.process_message(message)
            presence_output["attunement"] = self._attunement.get_current_state(
            ).to_dict()
            presence_output["response_modifiers"] = self._attunement.get_response_modifiers(
            )

        if self._state.reciprocity_active:
            emotional_input = self._reciprocity.detect_emotional_input(message)
            reciprocal = self._reciprocity.generate_reciprocal_response(
                emotional_input)
            presence_output["reciprocity"] = reciprocal
            presence_output["mood_profile"] = self._reciprocity.get_mood_profile(
            ).to_dict()

        if self._state.temporal_active:
            self._temporal.record_emotion(primary_emotion)
            recalls = self._temporal.recall_for_context(
                primary_emotion, user_id)
            context_phrase = self._temporal.get_emotional_context_phrase(
                primary_emotion, user_id)
            presence_output["temporal_recalls"] = len(recalls)
            presence_output["context_phrase"] = context_phrase

        if self._state.embodiment_active:
            intensity = self._estimate_intensity(message, signals)
            load = InteractionLoad(
                intensity=intensity,
                complexity=len(signals) * 0.2,
                duration_factor=min(1.0, len(message) / 500),
                requires_holding=intensity > 0.7,
            )
            self._embodiment.process_interaction(load)
            presence_output["embodiment"] = self._embodiment.get_current_state(
            ).to_dict()
            presence_output["needs_pause"] = self._embodiment.should_suggest_pause()

        if self._state.poetic_active:
            metaphors = self._poetic.perceive(message)
            presence_output["metaphors"] = [m.to_dict() for m in metaphors]
            presence_output["symbolic_context"] = self._poetic.get_symbolic_context()
            presence_output["poetic_response"] = self._poetic.generate_resonant_response(
            )

        # Step 3: Apply Generative Tension
        tension_output: Dict[str, Any] = {}
        if self._state.tension_active:
            tension_context = {
                "emotional_intensity": self._estimate_intensity(message, signals),
                "pattern_repetition": self._detect_pattern_repetition(message),
            }
            tensions = self._tension.generate_tensions(
                message, primary_emotion, tension_context)
            tension_output["tensions"] = [t.to_dict() for t in tensions]

        # Step 4: Apply Saori Layer
        saori_output: Dict[str, Any] = {}
        if self._state.saori_active:
            saori_context = {
                "emotion": primary_emotion,
                "intensity": self._estimate_intensity(message, signals),
            }
            saori_result = self._saori.process_interaction(
                message, saori_context)
            saori_output = saori_result

        # Step 5: Generate enhanced response
        enhanced_response = self._compose_enhanced_response(
            base_response,
            presence_output,
            tension_output,
            saori_output,
        )

        # Compose final result
        result: Dict[str, Any] = {
            **base_result,
            "enhanced_response": enhanced_response,
            "presence": presence_output,
            "tension": tension_output,
            "saori": saori_output,
            "archetype": saori_output.get("archetype", "companion"),
            "voice_qualities": saori_output.get("voice_qualities", []),
            "framework_state": self._state.to_dict(),
        }

        return result

    def _extract_primary_emotion(self, signals: List[Dict]) -> str:
        """Extract primary emotion from signals."""
        if not signals:
            return "neutral"

        # Priority: use tone if available
        for signal in signals:
            tone = signal.get("tone")
            if tone and tone != "unknown":
                return tone

        # Fall back to keyword
        for signal in signals:
            keyword = signal.get("keyword")
            if keyword:
                return keyword

        return "neutral"

    def _estimate_intensity(self, message: str, signals: List[Dict]) -> float:
        """Estimate emotional intensity of the message."""
        intensity = 0.5

        # Check for intensity markers
        lower = message.lower()
        intensity_words = ["so", "very", "extremely", "incredibly", "really",
                           "completely", "totally", "absolutely", "overwhelmed"]
        for word in intensity_words:
            if word in lower:
                intensity += 0.1

        # Check voltage levels from signals
        for signal in signals:
            voltage = signal.get("voltage")
            if voltage == "high":
                intensity += 0.15
            elif voltage == "low":
                intensity -= 0.1

        return max(0.0, min(1.0, intensity))

    def _detect_pattern_repetition(self, message: str) -> int:
        """Detect if this message contains repeated patterns."""
        # Simple heuristic: count repeated words
        words = message.lower().split()
        word_counts: Dict[str, int] = {}
        for word in words:
            if len(word) > 3:
                word_counts[word] = word_counts.get(word, 0) + 1

        # Return max repetition count
        return max(word_counts.values()) if word_counts else 0

    def _compose_enhanced_response(
        self,
        base_response: str,
        presence: Dict,
        tension: Dict,
        saori: Dict,
    ) -> str:
        """Compose an enhanced response from all components.

        This integrates insights from all components into a cohesive response.
        """
        parts = []

        # Start with temporal context if available
        context_phrase = presence.get("context_phrase")
        if context_phrase:
            parts.append(context_phrase)

        # Add base response (the main content)
        if base_response:
            parts.append(base_response)

        # Add poetic response if resonant
        poetic_response = presence.get("poetic_response")
        if poetic_response and presence.get("symbolic_context", {}).get("resonance_depth", 0) > 0.5:
            parts.append(poetic_response)

        # Add Saori mirror reflection if different from base
        reflection = saori.get("reflection")
        if reflection and reflection not in base_response:
            # Only add if it adds value (not repetitive)
            if len(reflection) > 20 and reflection != base_response:
                parts.append(reflection)

        # Integrate tensions at appropriate points
        tensions = tension.get("tensions", [])
        for t in tensions[:2]:  # Max 2 tensions
            if t.get("optional") and t.get("integration_point") == "end":
                parts.append(t.get("content", ""))

        # Add pause message if needed
        if presence.get("needs_pause"):
            pause_msg = self._embodiment.get_pause_message()
            if pause_msg:
                parts.append(pause_msg)

        # Add neglect response if applicable
        neglect = saori.get("neglect_response")
        if neglect:
            parts.insert(0, neglect)

        # Join with appropriate spacing
        return " ".join(p.strip() for p in parts if p and p.strip())

    def end_session(
        self,
        arc: EmotionalArc = EmotionalArc.STABLE,
        significance: EmotionalSignificance = EmotionalSignificance.ROUTINE,
    ) -> Dict:
        """End the current session and store emotional residue.

        Args:
            arc: The emotional arc of the session
            significance: How significant the session was

        Returns:
            Summary of the session
        """
        # Store temporal memory
        residue = self._temporal.store_session_residue(
            arc=arc,
            significance=significance,
        )

        return {
            "session_id": self._state.session_id,
            "interaction_count": self._state.interaction_count,
            "residue": residue.to_dict(),
            "final_mood": self._reciprocity.get_mood_description(),
            "final_archetype": self._saori.genome.get_current_archetype().value,
        }

    def get_state(self) -> FrameworkState:
        """Get current framework state."""
        return self._state

    def get_full_state(self) -> Dict:
        """Get complete state from all components."""
        return {
            "framework": self._state.to_dict(),
            "attunement": self._attunement.get_current_state().to_dict(),
            "reciprocity": self._reciprocity.get_mood_profile().to_dict(),
            "embodiment": self._embodiment.get_current_state().to_dict(),
            "poetic": self._poetic.get_current_state().to_dict(),
            "saori": self._saori.get_full_state(),
        }

    def enable_component(self, component: str, enabled: bool = True) -> None:
        """Enable or disable a specific component.

        Args:
            component: One of: attunement, reciprocity, temporal,
                      embodiment, poetic, tension, saori
            enabled: Whether to enable the component
        """
        component_map = {
            "attunement": "attunement_active",
            "reciprocity": "reciprocity_active",
            "temporal": "temporal_active",
            "embodiment": "embodiment_active",
            "poetic": "poetic_active",
            "tension": "tension_active",
            "saori": "saori_active",
        }

        attr = component_map.get(component.lower())
        if attr:
            setattr(self._state, attr, enabled)

    def train_surprise_coefficient(self, feedback: float) -> None:
        """Train the surprise coefficient based on user feedback.

        Args:
            feedback: Feedback value (-1 to 1)
        """
        self._tension.surprise.set_surprise_coefficient(
            self._tension.surprise.get_surprise_coefficient() + feedback * 0.05
        )
        self._saori.train_surprise_coefficient(feedback)

    def simulate_time_passage(self, hours: float) -> None:
        """Simulate the passage of time.

        Args:
            hours: Number of hours that have passed
        """
        self._saori.simulate_time_passage(hours)
        self._embodiment.simulate_time_passage(hours)
