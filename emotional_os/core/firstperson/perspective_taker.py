"""Phase 3.1: Perspective-Taking Module

Detects relational contexts and generates reflections that invite users
to consider other perspectives. Core Phase 3 capability for encouraging
empathy practice.

Supports three variation types:
- Empathy: "How might they see this?"
- Boundary-setting: "What do you need here?"
- Self-care: "How could you care for yourself?"
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Tuple
import re
import logging

logger = logging.getLogger(__name__)


class PerspectiveVariation(Enum):
    """Types of perspective reflections offered."""
    EMPATHY = "empathy"           # Understanding the other's viewpoint
    BOUNDARY = "boundary"         # Self-boundary and autonomy
    SELF_CARE = "self-care"      # User's own wellbeing


@dataclass
class RelationalContext:
    """Detected relational context in user input."""
    subject: str                  # Who the input is about (e.g., "Cindy", "my boss")
    # Nature of relationship (friend, family, work, etc.)
    relationship: str
    verb: str                    # What the subject did/said
    # User's role in the context (listener, responder, etc.)
    user_role: str
    confidence: float            # Confidence in this detection (0.0-1.0)
    raw_phrase: str              # Original text snippet


@dataclass
class PerspectiveReflection:
    """A perspective-taking reflection to offer the user."""
    variation: PerspectiveVariation
    reflection_text: str
    prompt_question: str
    context: RelationalContext
    confidence: float


class PerspectiveTaker:
    """Detects relational contexts and generates perspective reflections."""

    # Patterns to detect relational contexts
    RELATIONAL_PATTERNS = {
        r"(?P<subject>\w+)\s+(?:said|told|thinks?|believes|said that|mentioned|explained)",
        r"(?P<subject>\w+)\s+(?:is|was|are|were)\s+(?:mad|upset|angry|happy|sad|frustrated|confused)",
        r"my\s+(?P<subject>\w+)\s+(?:said|told|thinks?)",
        r"(?P<subject>\w+)\s+(?:kept|keeps|didn't|don't)\s+",
        r"(?P<subject>\w+)'s?\s+(?:way|perspective|response|issue|problem)",
    }

    # Subject categories for relationship inference
    FAMILY_SUBJECTS = {"mom", "dad", "mother", "father", "sister", "brother",
                       "grandma", "grandpa", "wife", "husband", "spouse", "kid", "kids"}
    WORK_SUBJECTS = {"boss", "manager",
                     "colleague", "coworker", "client", "team"}
    FRIEND_SUBJECTS = {"friend", "best friend", "boyfriend", "girlfriend"}

    # Perspective reflection templates
    EMPATHY_TEMPLATES = [
        "How do you think {subject} might see this?",
        "What might {subject}'s perspective be on this?",
        "If you stepped into {subject}'s shoes, what might they be experiencing?",
        "From {subject}'s viewpoint, what could be happening here?",
        "How might {subject} understand or interpret what you've described?",
        "What could {subject} be feeling or needing right now?",
    ]

    BOUNDARY_TEMPLATES = [
        "What do you need from {subject} in this situation?",
        "What boundary might help you here?",
        "How could you be more clear about what you need?",
        "What would caring for yourself in this look like?",
        "What's one thing you could do differently to protect your own wellbeing?",
        "How could you honor your own needs here?",
    ]

    SELF_CARE_TEMPLATES = [
        "How could you support yourself through this?",
        "What would feel nourishing for you right now?",
        "What's one way you could practice self-compassion?",
        "How might you extend to yourself the understanding you'd give a friend?",
        "What small thing could you do for yourself today?",
        "How could you soften toward yourself in this?",
    ]

    def __init__(self, user_id: Optional[str] = None):
        """Initialize perspective taker.

        Args:
            user_id: Optional user identifier for logging
        """
        self.user_id = user_id
        self.context_history: List[RelationalContext] = []
        self.reflection_history: List[PerspectiveReflection] = []

    def detect_relational_context(self, text: str) -> Optional[RelationalContext]:
        """Detect relational context from user input.

        Args:
            text: User input text

        Returns:
            RelationalContext if detected, else None
        """
        text_lower = text.lower()

        # Try pattern matching
        for pattern in self.RELATIONAL_PATTERNS:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                subject = match.group("subject").strip(
                ) if "subject" in match.groupdict() else None
                if subject:
                    relationship = self._infer_relationship(subject)
                    verb = self._extract_verb(text_lower)
                    user_role = self._infer_user_role(text_lower, subject)

                    context = RelationalContext(
                        subject=subject,
                        relationship=relationship,
                        verb=verb,
                        user_role=user_role,
                        confidence=0.7,  # Pattern match confidence
                        raw_phrase=match.group(0)
                    )

                    self.context_history.append(context)
                    logger.info(
                        f"Detected relational context: {subject} ({relationship})")
                    return context

        return None

    def generate_reflection(
        self,
        context: RelationalContext,
        variation: Optional[PerspectiveVariation] = None
    ) -> PerspectiveReflection:
        """Generate perspective reflection from relational context.

        Args:
            context: Detected relational context
            variation: Preferred variation type; if None, cycle through all three

        Returns:
            PerspectiveReflection with question and text
        """
        # Choose variation if not specified
        if variation is None:
            # Cycle through variations based on history length
            variations = list(PerspectiveVariation)
            variation = variations[len(
                self.reflection_history) % len(variations)]

        # Generate reflection based on variation
        subject_display = context.subject.capitalize()

        if variation == PerspectiveVariation.EMPATHY:
            template = self._choose_template(self.EMPATHY_TEMPLATES)
        elif variation == PerspectiveVariation.BOUNDARY:
            template = self._choose_template(self.BOUNDARY_TEMPLATES)
        else:  # SELF_CARE
            template = self._choose_template(self.SELF_CARE_TEMPLATES)

        prompt_question = template.format(subject=subject_display)

        # Build reflection text
        reflection_text = self._build_reflection_text(context, variation)

        reflection = PerspectiveReflection(
            variation=variation,
            reflection_text=reflection_text,
            prompt_question=prompt_question,
            context=context,
            confidence=context.confidence
        )

        self.reflection_history.append(reflection)
        return reflection

    def _infer_relationship(self, subject: str) -> str:
        """Infer relationship category from subject.

        Args:
            subject: The subject string

        Returns:
            Relationship category: "family", "work", "friend", or "other"
        """
        subject_lower = subject.lower()

        if any(s in subject_lower for s in self.FAMILY_SUBJECTS):
            return "family"
        elif any(s in subject_lower for s in self.WORK_SUBJECTS):
            return "work"
        elif any(s in subject_lower for s in self.FRIEND_SUBJECTS):
            return "friend"

        return "other"

    def _extract_verb(self, text: str) -> str:
        """Extract the action verb from the text.

        Args:
            text: Input text

        Returns:
            Verb string
        """
        verb_pattern = r"(?:said|told|thinks?|believes?|mentioned|kept|didn't|don't|was|were)\s+(\w+)"
        match = re.search(verb_pattern, text)
        return match.group(1) if match else "said"

    def _infer_user_role(self, text: str, subject: str) -> str:
        """Infer user's role in the context.

        Args:
            text: Input text
            subject: The other person in the context

        Returns:
            User role: "listener", "responder", "observer", etc.
        """
        if any(word in text.lower() for word in ["told me", "asked me", "asked if i"]):
            return "listener"
        elif any(word in text.lower() for word in ["i said", "i told", "i responded"]):
            return "responder"
        elif any(word in text.lower() for word in ["they", "they said", "they did"]):
            return "observer"

        return "participant"

    def _choose_template(self, templates: List[str]) -> str:
        """Choose a template from list (simple round-robin).

        Args:
            templates: List of template strings

        Returns:
            Selected template
        """
        # Use history length to rotate through templates
        index = len(self.reflection_history) % len(templates)
        return templates[index]

    def _build_reflection_text(
        self,
        context: RelationalContext,
        variation: PerspectiveVariation
    ) -> str:
        """Build contextual reflection text.

        Args:
            context: Relational context
            variation: Variation type

        Returns:
            Reflection text
        """
        subject = context.subject.capitalize()

        if variation == PerspectiveVariation.EMPATHY:
            if context.relationship == "family":
                return f"It sounds like {subject} has their own experience in this too."
            elif context.relationship == "work":
                return f"{subject} might be operating from a different context or priority."
            else:
                return f"There might be something happening for {subject} that you can't quite see from here."

        elif variation == PerspectiveVariation.BOUNDARY:
            if context.user_role == "listener":
                return "You don't have to carry this alone or figure it all out right now."
            elif context.user_role == "responder":
                return "You have the right to be clear about what you can and cannot do."
            else:
                return "Your own wellbeing matters in this situation."

        else:  # SELF_CARE
            if context.relationship == "family":
                return "Family dynamics can be tender. How do you want to care for yourself here?"
            elif context.relationship == "work":
                return "You can set boundaries at work while still being professional."
            else:
                return "This is an opportunity to practice gentleness with yourself."

    def generate_all_variations(
        self,
        context: RelationalContext
    ) -> Dict[str, PerspectiveReflection]:
        """Generate all three variation types for a context.

        Useful for templates or teaching moments.

        Args:
            context: Relational context

        Returns:
            Dict mapping variation names to PerspectiveReflection objects
        """
        result = {}
        for variation in PerspectiveVariation:
            reflection = self.generate_reflection(context, variation)
            result[variation.value] = reflection

        return result

    def should_offer_reflection(self, text: str) -> Tuple[bool, Optional[RelationalContext]]:
        """Determine if perspective reflection is warranted.

        Args:
            text: User input

        Returns:
            Tuple of (should_offer, detected_context)
        """
        context = self.detect_relational_context(text)

        if not context:
            return False, None

        # Confidence threshold
        if context.confidence < 0.6:
            return False, context

        # Don't offer too frequently (check history)
        if len(self.reflection_history) > 0:
            last_variation = self.reflection_history[-1].variation
            if last_variation == PerspectiveVariation.EMPATHY:
                # Mix it up with boundary or self-care next
                return True, context

        return True, context
