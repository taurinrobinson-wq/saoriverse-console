"""Phase 3.1: Micro-Choice Offering Module

Detects unresolved tensions and ambiguous next steps, then offers two 
small, concrete paths forward. Encourages agency while keeping choices 
focused and manageable.

Core Phase 3 capability for offering relational scaffolding.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple, Dict
import re
import logging

logger = logging.getLogger(__name__)


class ChoiceType(Enum):
    """Categories of micro-choices."""
    EXPLORE_VS_ACCEPT = "explore_vs_accept"         # Dig deeper vs. let it be
    COMMUNICATE_VS_REFLECT = "communicate_vs_reflect"  # Reach out vs. sit with it
    # Do something vs. understand something
    ACTION_VS_INSIGHT = "action_vs_insight"
    # Set a limit vs. mend a relationship
    BOUNDARY_VS_REPAIR = "boundary_vs_repair"
    # Ask for help vs. work through alone
    SUPPORT_VS_SOLO = "support_vs_solo"


@dataclass
class UnresolvedTension:
    """Detected unresolved tension or ambiguous next step."""
    tension_type: str                # Type of tension (conflict, confusion, paralysis, etc.)
    key_phrase: str                  # The phrase that signals tension
    # Current emotional state (frustrated, confused, stuck, etc.)
    emotional_state: str
    implicit_question: str           # The unspoken question behind the tension
    confidence: float                # Confidence in this detection (0.0-1.0)


@dataclass
class MicroChoice:
    """A pair of micro-choices offered to the user."""
    path_a: str                      # First choice (action or frame)
    path_b: str                      # Second choice (action or frame)
    choice_type: ChoiceType         # Category of choice
    tension: UnresolvedTension      # The tension this addresses
    # Which variation set this is (for rotation)
    variation_index: int
    confidence: float                # Confidence in this choice pair


class MicroChoiceOffering:
    """Detects tensions and offers two-option choice scaffolding."""

    # Patterns that signal unresolved tension
    TENSION_PATTERNS = {
        "paralysis": [
            r"(?:don't know|not sure|can't decide|stuck|unclear) (?:what|how|if)",
            r"(?:should i|do i|can i) (?:\w+)",
            r"(?:confused|torn|conflicted) (?:about|on|over)"
        ],
        "conflict": [
            r"(?:they|he|she) (?:won't|don't|didn't) (?:\w+)",
            r"(?:argument|fight|disagree|don't agree)",
            r"(?:feeling|feel) (?:unheard|dismissed|misunderstood|angry)"
        ],
        "abandonment": [
            r"(?:alone|lonely|isolated|don't have|nobody)",
            r"(?:left me|left me|abandoned)",
            r"(?:can't talk|can't reach|unavailable)"
        ],
        "overwhelm": [
            r"(?:too much|overwhelming|can't|too many)",
            r"(?:everything|all of it) (?:at once|together|too)",
            r"(?:don't know where to start|where do i)"
        ],
        "injustice": [
            r"(?:not fair|unfair|unjust|shouldn't)",
            r"(?:why|how come) (?:they|he|she)",
            r"(?:deserve|didn't deserve) (?:\w+)"
        ]
    }

    # Tension-to-choice-type mapping
    TENSION_TO_CHOICE_TYPE = {
        "paralysis": ChoiceType.EXPLORE_VS_ACCEPT,
        "conflict": ChoiceType.COMMUNICATE_VS_REFLECT,
        "abandonment": ChoiceType.SUPPORT_VS_SOLO,
        "overwhelm": ChoiceType.ACTION_VS_INSIGHT,
        "injustice": ChoiceType.BOUNDARY_VS_REPAIR
    }

    # Choice templates (rotate through variations)
    CHOICE_TEMPLATES: Dict[ChoiceType, List[Tuple[str, str]]] = {
        ChoiceType.EXPLORE_VS_ACCEPT: [
            ("Explore what's underneath this feeling",
             "Let yourself sit with it for now"),
            ("Dig into why this matters to you",
             "Accept it as part of being human"),
            ("Ask yourself what you're really concerned about",
             "Honor your uncertainty"),
        ],
        ChoiceType.COMMUNICATE_VS_REFLECT: [
            ("Tell them what you're noticing", "Reflect on it privately first"),
            ("Reach out and share how you're feeling",
             "Take time to understand your own response"),
            ("Start a conversation about this",
             "Journal or think through it alone"),
        ],
        ChoiceType.ACTION_VS_INSIGHT: [
            ("Take one small action toward what you want",
             "Understand the pattern first"),
            ("Try something different this time",
             "Figure out why the pattern exists"),
            ("Make a change", "Gain clarity before moving"),
        ],
        ChoiceType.BOUNDARY_VS_REPAIR: [
            ("Set a clear boundary", "Look for ways to repair or reconnect"),
            ("Be direct about what you need", "Find common ground first"),
            ("Protect your own wellbeing here",
             "See if you can understand their side"),
        ],
        ChoiceType.SUPPORT_VS_SOLO: [
            ("Reach out and ask for support", "Work through this on your own"),
            ("Share this with someone you trust", "Sit with it yourself for now"),
            ("Let someone help you", "Figure this out independently"),
        ],
    }

    def __init__(self, user_id: Optional[str] = None):
        """Initialize micro-choice offering module.

        Args:
            user_id: Optional user identifier for logging
        """
        self.user_id = user_id
        self.tension_history: List[UnresolvedTension] = []
        self.choice_history: List[MicroChoice] = []

    def detect_tension(self, text: str) -> Optional[UnresolvedTension]:
        """Detect unresolved tension or ambiguous next step.

        Args:
            text: User input text

        Returns:
            UnresolvedTension if detected, else None
        """
        text_lower = text.lower()

        for tension_type, patterns in self.TENSION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    implicit_question = self._infer_implicit_question(
                        text_lower, tension_type)
                    emotional_state = self._infer_emotional_state(text_lower)

                    tension = UnresolvedTension(
                        tension_type=tension_type,
                        key_phrase=re.search(
                            pattern, text_lower, re.IGNORECASE).group(0),
                        emotional_state=emotional_state,
                        implicit_question=implicit_question,
                        confidence=0.75
                    )

                    self.tension_history.append(tension)
                    logger.info(
                        f"Detected tension: {tension_type} - '{implicit_question}'")
                    return tension

        return None

    def offer_choice(self, tension: UnresolvedTension) -> Optional[MicroChoice]:
        """Generate a two-option choice for the detected tension.

        Args:
            tension: Detected unresolved tension

        Returns:
            MicroChoice with two paths, or None if can't generate
        """
        choice_type = self.TENSION_TO_CHOICE_TYPE.get(
            tension.tension_type,
            ChoiceType.EXPLORE_VS_ACCEPT
        )

        # Get templates for this choice type
        templates = self.CHOICE_TEMPLATES.get(choice_type, [])
        if not templates:
            logger.warning(f"No templates for choice type: {choice_type}")
            return None

        # Rotate through templates
        variation_index = len(self.choice_history) % len(templates)
        path_a, path_b = templates[variation_index]

        choice = MicroChoice(
            path_a=path_a,
            path_b=path_b,
            choice_type=choice_type,
            tension=tension,
            variation_index=variation_index,
            confidence=tension.confidence
        )

        self.choice_history.append(choice)
        return choice

    def format_choice_for_response(self, choice: MicroChoice) -> str:
        """Format choice pair into natural language response snippet.

        Args:
            choice: MicroChoice to format

        Returns:
            Formatted choice text ready for response
        """
        return f"Would you rather {choice.path_a.lower()}, or {choice.path_b.lower()}?"

    def should_offer_choice(self, text: str) -> Tuple[bool, Optional[UnresolvedTension]]:
        """Determine if micro-choice is warranted for this input.

        Args:
            text: User input

        Returns:
            Tuple of (should_offer, detected_tension)
        """
        tension = self.detect_tension(text)

        if not tension:
            return False, None

        # Confidence threshold
        if tension.confidence < 0.6:
            return False, tension

        # Avoid over-offering (not more than every other turn)
        if len(self.choice_history) > 0:
            if len(self.tension_history) - len(self.choice_history) <= 1:
                return False, tension

        return True, tension

    def _infer_implicit_question(self, text: str, tension_type: str) -> str:
        """Infer the unspoken question behind the tension.

        Args:
            text: User input
            tension_type: Type of detected tension

        Returns:
            Implicit question string
        """
        if tension_type == "paralysis":
            return "What should I do?"
        elif tension_type == "conflict":
            return "How do I handle this disagreement?"
        elif tension_type == "abandonment":
            return "How do I get support?"
        elif tension_type == "overwhelm":
            return "Where do I even start?"
        elif tension_type == "injustice":
            return "What do I do about this unfairness?"
        else:
            return "What's my next move?"

    def _infer_emotional_state(self, text: str) -> str:
        """Infer emotional state from text.

        Args:
            text: User input

        Returns:
            Emotional state label
        """
        emotional_keywords = {
            "angry": ["angry", "furious", "enraged", "upset", "pissed"],
            "sad": ["sad", "depressed", "devastated", "heartbroken", "grieving"],
            "confused": ["confused", "lost", "disoriented", "bewildered", "unclear"],
            "frustrated": ["frustrated", "exasperated", "fed up", "irritated"],
            "scared": ["scared", "afraid", "anxious", "terrified", "worried"],
            "overwhelmed": ["overwhelmed", "flooded", "drowning", "too much"],
        }

        for state, keywords in emotional_keywords.items():
            if any(kw in text for kw in keywords):
                return state

        return "mixed"

    def get_all_choice_variations(
        self,
        tension: UnresolvedTension
    ) -> List[MicroChoice]:
        """Get all variation options for a tension.

        Useful for teaching or offering more options.

        Args:
            tension: Unresolved tension

        Returns:
            List of all possible MicroChoice variations
        """
        choice_type = self.TENSION_TO_CHOICE_TYPE.get(
            tension.tension_type,
            ChoiceType.EXPLORE_VS_ACCEPT
        )

        templates = self.CHOICE_TEMPLATES.get(choice_type, [])
        result = []

        for idx, (path_a, path_b) in enumerate(templates):
            choice = MicroChoice(
                path_a=path_a,
                path_b=path_b,
                choice_type=choice_type,
                tension=tension,
                variation_index=idx,
                confidence=tension.confidence
            )
            result.append(choice)

        return result
