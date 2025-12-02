"""Response Rotator for Phase 2.2: Response Modulation.

Manages rotation of conversational, affect-aware responses to avoid repetition
and keep tone fresh while preserving glyph-informed emotional language.

Uses weighted random selection with memory buffer to prevent echoing the same
response within recent turns while maintaining conversational authenticity.
"""

import random
from collections import defaultdict, deque
from typing import Dict, List, Optional


class ResponseRotator:
    """Rotates through conversational responses without repetition."""

    def __init__(self, rotation_bank: Dict[str, List[str]], memory_size: int = 3):
        """Initialize rotator with response bank and memory buffer.

        Args:
            rotation_bank: Dict mapping glyph/tone category to list of responses.
            memory_size: Number of recent responses to avoid repeating.
        """
        self.rotation_bank = rotation_bank
        self.round_robin_index = defaultdict(int)
        self.last_used = {
            glyph: deque(maxlen=memory_size) for glyph in rotation_bank
        }

    def get_response(
        self, glyph: str, strategy: str = "weighted"
    ) -> str:
        """Get a response for the given glyph/tone category.

        Args:
            glyph: Category key (e.g., 'exhaustion', 'anxiety', 'anger').
            strategy: 'round_robin' or 'weighted' (default).

        Returns:
            A conversational response string.
        """
        options = self.rotation_bank.get(glyph, [])
        if not options:
            return f"[No responses available for: {glyph}]"

        if strategy == "round_robin":
            # Deterministic: cycle through options in order
            idx = self.round_robin_index[glyph] % len(options)
            response = options[idx]
            self.round_robin_index[glyph] += 1
        else:
            # Weighted random: exclude recently used, add randomness
            available = [
                r for r in options if r not in self.last_used[glyph]
            ]
            if not available:
                # All options recently used; reset and pick from all
                available = options
            response = random.choice(available)

        self.last_used[glyph].append(response)
        return response

    def reset_memory(self, glyph: Optional[str] = None) -> None:
        """Clear memory of recent responses.

        Args:
            glyph: If provided, reset only this category. Otherwise reset all.
        """
        if glyph:
            self.last_used[glyph].clear()
        else:
            for buffer in self.last_used.values():
                buffer.clear()


# Conversational response bank organized by emotional glyph category
# Each response reflects the emotion first, weaves in glyph tone lightly,
# and ends with an open-ended invitation to continue.

GLYPH_RESPONSE_BANK = {
    "exhaustion": [
        "That sounds draining. I hear the fatigue in it. How are you holding up?",
        "I get the heaviness. It's a lot to carry. Want to tell me more?",
        "Exhaustion can feel depleting. I hear that. What's it like for you right now?",
        "That's tough. I hear the weight in it. Where does it land for you?",
    ],
    "anxiety": [
        "I can feel the worry in your words. What's the strongest part of it for you?",
        "That sounds uneasy. I hear the tension in it. How are you holding it?",
        "I hear the anxious edge. What's coming up most for you?",
        "That's a lot of worry to sit with. What feels biggest right now?",
    ],
    "sadness": [
        "I hear the sadness in this. It feels heavy. Where does it land for you?",
        "That's heavy. I hear the depth in it. What feels deepest right now?",
        "I can sense the sorrow. It's real. Do you want to stay with that a bit?",
        "I hear the grief in your words. How is it showing up for you today?",
    ],
    "anger": [
        "That's strong anger. I hear the fire in it. What's at the heart of it?",
        "I hear the heat in that frustration. Where's it burning most?",
        "That's real frustration. What's underneath for you?",
        "I hear the intensity in your words. What's driving it right now?",
    ],
    "calm": [
        "I hear the calm in that. It feels lighter. What's helping you breathe easier?",
        "That sounds like relief. How's it showing up for you?",
        "I hear the ease in your words. What's supporting that right now?",
        "That feels lighter. What's helping you carry it differently?",
    ],
    "joy": [
        "I hear the spark in your words. That energy feels alive. What's bringing it up?",
        "That brightness comes through. What's lifting you up right now?",
        "I hear the joy in that. It feels energized. Tell me more about it?",
        "That's real excitement. What's making it shine for you?",
    ],
    "neutral": [
        "I'm here to listen. What's on your mind?",
        "I hear you. Tell me more about that.",
        "What's that about? I'm listening.",
        "Help me understand what you're carrying right now.",
    ],
}


def create_response_rotator() -> ResponseRotator:
    """Factory function for creating a response rotator instance."""
    return ResponseRotator(GLYPH_RESPONSE_BANK)
