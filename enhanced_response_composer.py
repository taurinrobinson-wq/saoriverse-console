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

        # Detect emotional state from input
        emotional_state = self._detect_emotional_intensity(input_text, glyphs)

        # Apply prosody if we have a planner and high emotion
        prosody_directives = None
        if include_prosody and self.prosody_planner and emotional_state.get("high_emotion"):
            try:
                prosody_directives = self._apply_prosody_to_response(
                    response_text=response_text,
                    emotional_state=emotional_state,
                    user_input=user_input
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
            "freakin'": 0.8,
            "fucking": 0.9,
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
            "thrilled": 0.8,
            "excited": 0.75,
            "amazing": 0.7,
            "wonderful": 0.7,
        }

        input_lower = user_input.lower()
        max_intensity = 0.5
        detected_tone = "neutral"

        # Scan for intensity markers
        for marker, intensity in intensity_markers.items():
            if marker in input_lower:
                max_intensity = max(max_intensity, intensity)

                # Infer tone from markers
                if any(w in marker for w in ["stress", "anxious", "worried", "overwhelm"]):
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
