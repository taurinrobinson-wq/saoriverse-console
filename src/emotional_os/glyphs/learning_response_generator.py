"""Minimal LearningResponseGenerator used by tests.

This provides a small implementation that crafts a learning response
given a glyph candidate and emotional analysis. It's intentionally
lightweight to avoid heavy dependencies during collection.
"""
from typing import Any, Dict


class LearningResponseGenerator:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    def generate_learning_response(
        self,
        glyph_candidate: Dict[str, Any],
        original_input: str,
        emotional_tone: str,
        emotional_terms: Dict[str, Any],
        nrc_analysis: Dict[str, float],
    ) -> str:
        # Compose a concise supportive learning response that mentions
        # the candidate glyph and reflects the user's language.
        name = glyph_candidate.get("glyph_name", "that feeling")
        desc = glyph_candidate.get("description", "")
        return (
            f"I hear {emotional_tone}. It sounds like {name}: {desc}. "
            "Would you like to teach me more about how that feels?"
        )


__all__ = ["LearningResponseGenerator"]


def create_training_response(
    glyph_candidate: dict, original_input: str, emotional_tone: str, emotional_terms: dict, nrc_analysis: dict
) -> str:
    gen = LearningResponseGenerator()
    return gen.generate_learning_response(
        glyph_candidate=glyph_candidate,
        original_input=original_input,
        emotional_tone=emotional_tone,
        emotional_terms=emotional_terms,
        nrc_analysis=nrc_analysis,
    )

__all__.append("create_training_response")
