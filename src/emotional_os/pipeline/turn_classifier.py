"""Turn classifier for FirstPerson pipeline.

Deterministically classifies user message into turn type:
- disclosure: User shares a struggle or feeling
- gratitude: User expresses thanks
- meta: User asks about system/process
- closure: User signals conversation end
- correction: User corrects or reframes prior statement
"""

import re
from typing import Optional


class TurnClassifier:
    """Classify turn type from user message."""

    DISCLOSURE_MARKERS = {
        "i feel",
        "i'm",
        "i am",
        "struggling",
        "exhausted",
        "frustrated",
        "overwhelmed",
        "worried",
        "anxious",
        "sad",
        "lonely",
        "stressed",
        "tired",
        "don't know how",
        "can't seem to",
        "having trouble",
        "having difficulty",
        "battling",
        "fighting",
    }

    GRATITUDE_MARKERS = {
        "thank you",
        "thanks",
        "grateful",
        "appreciate",
        "that helped",
        "i'm better",
        "i feel better",
    }

    META_MARKERS = {
        "how do you",
        "can you",
        "do you",
        "what do you",
        "how do i",
        "why do you",
        "are you",
    }

    CLOSURE_MARKERS = {
        "goodbye",
        "bye",
        "gotta go",
        "talk soon",
        "i'm good",
        "i'm better",
        "thanks for",
        "that helps",
    }

    CORRECTION_MARKERS = {
        "actually",
        "wait",
        "i meant",
        "no that's",
        "not quite",
        "i should say",
        "let me rephrase",
        "i misspoke",
    }

    def classify(
        self,
        message: str,
        conversation_history: Optional[list] = None,
        user_id: Optional[str] = None,
    ) -> dict:
        """Classify a message into a turn type.

        Args:
            message: User's message text.
            conversation_history: Prior messages [{role, content}, ...].
            user_id: User identifier (for context, not required).

        Returns:
            {
                "turn_type": str,  # "disclosure" | "gratitude" | "meta" | "closure" | "correction"
                "confidence": float,  # 0.0-1.0
                "emotional_signal": Optional[str],  # "grief", "exhaustion", "joy", etc.
                "reasoning": str,
            }
        """
        message_lower = message.lower().strip()
        history = conversation_history or []

        # Check each marker set
        disclosure_score = self._score_markers(message_lower, self.DISCLOSURE_MARKERS)
        gratitude_score = self._score_markers(message_lower, self.GRATITUDE_MARKERS)
        meta_score = self._score_markers(message_lower, self.META_MARKERS)
        closure_score = self._score_markers(message_lower, self.CLOSURE_MARKERS)
        correction_score = self._score_markers(
            message_lower, self.CORRECTION_MARKERS
        )

        # Decide turn type based on highest score
        scores = {
            "disclosure": disclosure_score,
            "gratitude": gratitude_score,
            "meta": meta_score,
            "closure": closure_score,
            "correction": correction_score,
        }

        turn_type = max(scores, key=scores.get)
        confidence = scores[turn_type]

        # Detect emotional signal
        emotional_signal = self._detect_emotional_signal(message_lower)

        # Build reasoning
        reasoning = self._build_reasoning(
            turn_type, message_lower, scores, emotional_signal
        )

        return {
            "turn_type": turn_type,
            "confidence": confidence,
            "emotional_signal": emotional_signal,
            "reasoning": reasoning,
        }

    def _score_markers(self, text: str, markers: set) -> float:
        """Score how many markers are present (0.0-1.0)."""
        if not markers:
            return 0.0

        matched = sum(1 for marker in markers if marker in text)
        return min(1.0, matched / len(markers))

    def _detect_emotional_signal(self, text: str) -> Optional[str]:
        """Detect primary emotional signal from text."""
        signals = {
            "exhaustion": [
                "exhausted",
                "tired",
                "weary",
                "drained",
                "worn out",
                "burned out",
            ],
            "grief": ["loss", "lost", "grief", "mourning", "died", "death"],
            "joy": [
                "happy",
                "excited",
                "amazed",
                "wonderful",
                "amazing",
                "grateful",
            ],
            "stress": ["stress", "overwhelmed", "pressure", "anxious", "worry"],
            "isolation": ["alone", "lonely", "isolated", "nobody", "no one"],
        }

        for signal_name, keywords in signals.items():
            if any(kw in text for kw in keywords):
                return signal_name

        return None

    def _build_reasoning(
        self, turn_type: str, text: str, scores: dict, emotional_signal: Optional[str]
    ) -> str:
        """Build human-readable reasoning."""
        parts = [f"turn_type={turn_type} (confidence={scores[turn_type]:.2f})"]

        if emotional_signal:
            parts.append(f"emotional_signal={emotional_signal}")

        # Add details about why this turn type won
        if turn_type == "disclosure":
            if any(
                m in text for m in ["i feel", "i'm", "struggling", "tired", "worried"]
            ):
                parts.append("has_personal_disclosure=true")
        elif turn_type == "gratitude":
            if any(m in text for m in ["thank you", "grateful", "that helped"]):
                parts.append("has_thanks=true")
        elif turn_type == "meta":
            if any(
                m in text for m in ["how do you", "can you", "do you", "are you"]
            ):
                parts.append("has_system_question=true")
        elif turn_type == "closure":
            if any(m in text for m in ["goodbye", "bye", "gotta go", "thanks for"]):
                parts.append("has_closure_marker=true")
        elif turn_type == "correction":
            if any(m in text for m in ["actually", "wait", "i meant", "not quite"]):
                parts.append("has_correction_marker=true")

        return " | ".join(parts)
