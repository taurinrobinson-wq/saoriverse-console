"""Enhanced Response Composer - Integrates Sprint 5 Advanced Prosody

This module wraps the existing DynamicResponseComposer to make its responses
emotionally more resonant by:

1. Detecting high-emotion inputs
2. Generating emotionally-matched responses using advanced linguistic patterns
3. Applying prosody directives for voice synthesis
4. Logging interactions for learning

The goal: transform generic template responses into emotionally intelligent ones.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from emotional_os.glyphs.dynamic_response_composer import DynamicResponseComposer

try:
    from spoken_interface.advanced_prosody import AdvancedProsodyPlanner
    HAS_ADVANCED_PROSODY = True
except ImportError:
    HAS_ADVANCED_PROSODY = False
    AdvancedProsodyPlanner = None

logger = logging.getLogger(__name__)


class EnhancedResponseComposer(DynamicResponseComposer):
    """Extends DynamicResponseComposer with advanced emotional responsiveness.

    When compose_multi_glyph_response is called, this version:
    1. Analyzes emotional intensity of input
    2. Generates response via base composer
    3. Applies advanced prosody for voice synthesis
    4. Returns response with prosody metadata
    """

    def __init__(self, reward_model: Optional[Any] = None):
        """Initialize with optional prosody planner.

        Args:
            reward_model: Optional reward model for response ranking
        """
        super().__init__(reward_model=reward_model)

        self.prosody_planner = None
        if HAS_ADVANCED_PROSODY and AdvancedProsodyPlanner:
            try:
                self.prosody_planner = AdvancedProsodyPlanner()
                logger.info("Advanced prosody planner initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize advanced prosody: {e}")

        # Track emotional patterns for continuity
        self.last_emotional_state = None

    def compose_multi_glyph_response(
        self,
        input_text: str,
        glyphs: List[Dict[str, Any]],
        conversation_context: Optional[Dict[str, Any]] = None,
        top_n: int = 5,
        include_prosody: bool = True,
        **kwargs
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Compose response with optional prosody enhancement.

        Args:
            input_text: User's message
            glyphs: Activated glyphs
            conversation_context: Prior messages
            top_n: Top N glyphs to consider
            include_prosody: Whether to apply prosody enhancement
            **kwargs: Additional arguments passed to parent

        Returns:
            (response_text, prosody_directives) if include_prosody else (response_text, None)
        """
        # Detect emotional state from input FIRST
        emotional_state = self._detect_emotional_intensity(input_text, glyphs)

        # Check if this is vague high-emotion input (e.g., "this is bullshit" without context)
        if self._is_vague_emotional_input(input_text, emotional_state):
            # Use curiosity-first response instead of assuming affect
            response_text = self._get_curiosity_response(
                input_text, emotional_state)
            prosody_directives = None
            if include_prosody and self.prosody_planner:
                try:
                    prosody_directives = self._apply_prosody_to_response(
                        response_text=response_text,
                        emotional_state=emotional_state,
                        user_input=input_text
                    )
                except Exception as e:
                    logger.warning(f"Prosody application failed: {e}")
            self.last_emotional_state = emotional_state
            return (response_text, prosody_directives)

        # Get base response from parent composer (note: parameter is input_text, not user_input)
        try:
            response_text = super().compose_multi_glyph_response(
                input_text=input_text,
                glyphs=glyphs,
                conversation_context=conversation_context,
                top_n=top_n,
                **kwargs
            )
        except Exception as e:
            logger.warning(f"Base composition failed: {e}")
            response_text = "I'm here with you."

        # Apply prosody if we have a planner and high emotion
        prosody_directives = None
        if include_prosody and self.prosody_planner and emotional_state.get("high_emotion"):
            try:
                prosody_directives = self._apply_prosody_to_response(
                    response_text=response_text,
                    emotional_state=emotional_state,
                    user_input=input_text
                )
            except Exception as e:
                logger.warning(f"Prosody application failed: {e}")

        # Store emotional state for continuity
        self.last_emotional_state = emotional_state

        return (response_text, prosody_directives)

    def _detect_emotional_intensity(
        self,
        user_input: str,
        glyphs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Detect emotional intensity and characteristics from input.

        Args:
            user_input: User's message
            glyphs: Activated glyphs

        Returns:
            Dictionary with emotional analysis
        """
        emotional_state = {
            "high_emotion": False,
            "intensity": 0.5,  # 0-1
            "tone": "neutral",
            "voltage": 0.5,
            "attunement": 0.5,
            "certainty": 0.5
        }

        # Check for high-intensity language markers
        intensity_markers = {
            # Expletives & strong expressions
            "fucking": 0.9,
            "bullshit": 0.85,
            "freakin'": 0.8,
            "damn": 0.75,
            "hell": 0.7,
            "crap": 0.7,
            "shit": 0.85,
            # Intensifiers
            "seriously": 0.7,
            "just": 0.6,
            "really": 0.6,
            "so": 0.6,
            "super": 0.7,
            "absolutely": 0.7,
            "definitely": 0.6,
            "completely": 0.7,
            "totally": 0.7,
            "literally": 0.6,
            # Negative emotions
            "stressful": 0.8,
            "stressed": 0.8,
            "anxious": 0.8,
            "worried": 0.7,
            "overwhelmed": 0.9,
            "frustrated": 0.8,
            "angry": 0.85,
            "furious": 0.9,
            "devastated": 0.9,
            "heartbroken": 0.85,
            "depressed": 0.85,
            "miserable": 0.8,
            "terrible": 0.75,
            "awful": 0.75,
            "horrible": 0.75,
            # Positive emotions
            "thrilled": 0.8,
            "excited": 0.75,
            "amazing": 0.7,
            "wonderful": 0.7,
            "fantastic": 0.75,
            "love": 0.7,
        }

        input_lower = user_input.lower()
        max_intensity = 0.5
        detected_tone = "neutral"

        # Scan for intensity markers
        for marker, intensity in intensity_markers.items():
            if marker in input_lower:
                max_intensity = max(max_intensity, intensity)

                # Infer tone from markers
                if any(w in marker for w in ["fucking", "bullshit", "shit", "damn", "hell", "crap"]):
                    detected_tone = "frustrated"  # Expletives usually indicate frustration/anger
                elif any(w in marker for w in ["stress", "anxious", "worried", "overwhelm"]):
                    detected_tone = "anxious"
                elif any(w in marker for w in ["angry", "furious", "frustrated"]):
                    detected_tone = "frustrated"
                elif any(w in marker for w in ["thrilled", "excited", "amazing", "wonderful"]):
                    detected_tone = "excited"
                elif any(w in marker for w in ["devastated", "heartbroken"]):
                    detected_tone = "sad"

        # Check glyph activations for emotional context
        if glyphs:
            glyph_names = [g.get("glyph_name", "").lower() for g in glyphs]

            # Map glyphs to tones
            if any("ache" in name or "sorrow" in name for name in glyph_names):
                detected_tone = "sad"
            elif any("anxious" in name or "trepid" in name for name in glyph_names):
                detected_tone = "anxious"
            elif any("anger" in name or "fury" in name for name in glyph_names):
                detected_tone = "frustrated"
            elif any("excite" in name or "joy" in name for name in glyph_names):
                detected_tone = "excited"

        # Determine if emotion is "high" (needs advanced prosody)
        high_emotion = max_intensity > 0.65 and detected_tone != "neutral"

        return {
            "high_emotion": high_emotion,
            "intensity": max_intensity,
            "tone": detected_tone,
            "voltage": max_intensity,  # Arousal ~ intensity
            # Higher intensity = more engaged
            "attunement": 0.7 + (0.3 * max_intensity),
            "certainty": 0.6,  # Usually uncertain in high-emotion moments
            "markers_found": True if max_intensity > 0.5 else False
        }

    def _apply_prosody_to_response(
        self,
        response_text: str,
        emotional_state: Dict[str, Any],
        user_input: str
    ) -> Dict[str, Any]:
        """Apply advanced prosody directives to response.

        Args:
            response_text: The response to enhance
            emotional_state: Detected emotional state
            user_input: Original user input

        Returns:
            Prosody directives dictionary
        """
        if not self.prosody_planner:
            return {}

        try:
            # Generate prosody plan
            prosody_plan = self.prosody_planner.plan_advanced_prosody(
                text=response_text,
                voltage=emotional_state.get("voltage", 0.5),
                tone=emotional_state.get("tone", "neutral"),
                attunement=emotional_state.get("attunement", 0.7),
                certainty=emotional_state.get("certainty", 0.6)
            )

            # Convert to serializable format
            return {
                "base_rate": prosody_plan.base_rate,
                "pitch_contour": [
                    {"time_ratio": t, "semitone_shift": s}
                    for t, s in prosody_plan.pitch_contour
                ],
                "energy_contour": [
                    {"time_ratio": t, "energy_scale": e}
                    for t, e in prosody_plan.energy_contour
                ],
                "emphasis_points": [
                    {
                        "word_index": ep.word_index,
                        "type": str(ep.type),
                        "intensity": ep.intensity
                    }
                    for ep in prosody_plan.emphasis_points
                ],
                "micro_pauses": [
                    {
                        "position": mp.position,
                        "duration_ms": mp.duration_ms,
                        "purpose": mp.purpose
                    }
                    for mp in prosody_plan.micro_pauses
                ],
                "breath_style": str(prosody_plan.breath_style),
                "breathiness": prosody_plan.breathiness,
                "emotional_state": emotional_state
            }

        except Exception as e:
            logger.warning(f"Prosody plan generation failed: {e}")
            return {}

    def compose(self, candidates: List[Dict[str, Any]]) -> Optional[str]:
        """Compose from candidates (parent method returns str, not Dict).

        Args:
            candidates: List of response candidates

        Returns:
            Best response text
        """
        # Get base selection from parent (note: parent compose_multi_glyph_response returns string)
        try:
            best_response = super().compose_multi_glyph_response(
                input_text=" ".join([c.get("text", "") for c in candidates]),
                glyphs=[]
            )
        except Exception as e:
            logger.warning(f"Composition failed: {e}")
            best_response = candidates[0].get("text", "") if candidates else ""

        return best_response

    def _is_vague_emotional_input(self, user_input: str, emotional_state: Dict[str, Any]) -> bool:
        """Detect if input is emotionally charged but contextually vague.

        Vague high-emotion input:
        - Very short (≤5 words) with expletives/intensifiers
        - No specific subject matter
        - High emotional intensity but lacks concrete context

        Examples: "this is bullshit", "what a freakin day", "shit"
        """
        # Only flag high-emotion input as potentially vague
        if not emotional_state.get("high_emotion") or emotional_state.get("intensity", 0) < 0.65:
            return False

        words = user_input.lower().split()

        # Count expletives and intensifiers
        expletives = {"bullshit", "shit", "fuck", "fucking",
                      "damn", "hell", "crap", "whatever"}
        intensifiers = {"really", "so", "very", "super", "extremely",
                        "absolutely", "freakin", "freakin'", "what"}

        expletive_count = sum(
            1 for w in words if w.strip('.,!?') in expletives)
        intensifier_count = sum(
            1 for w in words if w.strip('.,!?\'') in intensifiers)

        # Short messages with expletives/intensifiers = likely vague
        if len(words) <= 5 and (expletive_count > 0 or intensifier_count > 1):
            # Check for specific subjects that ground the complaint
            concrete_subjects = {
                "work", "project", "situation", "person", "meeting",
                "team", "boss", "friend", "family", "school", "code", "test",
                "deadline", "presentation", "system", "app", "feature", "bug",
                "client", "manager", "user", "rule", "policy", "file", "commit"
            }
            has_specific_subject = any(
                w.strip('.,!?') in concrete_subjects for w in words)

            if not has_specific_subject:
                return True

        # Vague pronouns without clear referent
        if any(phrase in user_input.lower() for phrase in ["this is", "that's", "it's all"]):
            if not any(concrete in user_input.lower()
                       for concrete in ["work", "person", "situation", "problem", "meeting",
                                        "project", "team", "my", "me", "we", "happening"]):
                return True

        return False

    def _get_curiosity_response(self, user_input: str, emotional_state: Dict[str, Any]) -> str:
        """Generate curiosity-first response for vague high-emotion input.

        When someone says "this is bullshit" without context, ask what they mean.

        Args:
            user_input: The user's message
            emotional_state: Detected emotional state

        Returns:
            A curiosity-first response acknowledging emotion but asking for context
        """
        tone = emotional_state.get("tone", "frustrated")

        # Tone-specific curiosity responses
        curiosity_responses = {
            "frustrated": [
                "What's getting to you?",
                "I feel that. What's the main thing?",
                "Yeah, talk to me. What's going on?",
                "That frustration is clear. What's at the core?",
                "What's the most frustrating part?",
                "That's intense. Tell me what's behind it.",
                "Yeah? What's fueling that?",
                "Oh yeah? What's got you heated?",
            ],
            "anxious": [
                "What's worrying you most?",
                "I hear the stress. What's the pressure about?",
                "That's real tension. What's driving it?",
                "What feels most fragile right now?",
                "Talk to me. What's the concern?",
            ],
            "angry": [
                "Oh yeah? What's got you heated?",
                "That's real. What happened?",
                "I hear the anger. What's going on?",
                "That's intense. Tell me what's behind it.",
                "Yeah? What's fueling that?",
            ],
            "sad": [
                "That sounds heavy. What's underneath it?",
                "I hear the sadness. What's the loss?",
                "What's hurting?",
                "That pain is real. What's at the core?",
                "What are you grieving?",
            ],
            "excited": [
                "Tell me more! What's the story?",
                "I love the energy. What's happening?",
                "What's got you so animated?",
            ],
        }

        import random
        responses = curiosity_responses.get(tone, [
            "Tell me more. What's happening?",
            "I'm listening. What's going on?",
            "Help me understand.",
            "What do you mean?",
        ])

        return random.choice(responses)


# Convenience function for integrating into existing code
def create_enhanced_composer(reward_model: Optional[Any] = None) -> EnhancedResponseComposer:
    """Factory for creating enhanced composer.

    Args:
        reward_model: Optional reward model

    Returns:
        EnhancedResponseComposer instance
    """
    return EnhancedResponseComposer(reward_model=reward_model)


if __name__ == "__main__":
    # Test the enhanced composer
    import json

    composer = create_enhanced_composer()

    # Simulate a stressful interaction
    glyphs = [
        {"glyph_name": "Ache of Recognition", "voltage": 0.7},
        {"glyph_name": "Tension Hold", "voltage": 0.8},
    ]

    user_input = "what a freakin' stressful day this has been!"

    response, prosody = composer.compose_multi_glyph_response(
        input_text=user_input,
        glyphs=glyphs,
        include_prosody=True
    )

    print(f"User: {user_input}")
    print(f"\nResponse: {response}")
    print(f"\nProsody Directives:")
    print(json.dumps(prosody, indent=2, default=str))
