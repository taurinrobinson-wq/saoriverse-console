"""Response Templates Module for FirstPerson.

Maintains template banks for clarifying prompts and reflections with
rotation logic to avoid phrase repetition. Supports adaptive variation
based on context and user feedback patterns.

NOW WITH AGENT MOOD SUPPORT (Phase 2):
- Templates can be tagged with mood affinity
- Selection filters by agent's current mood
- Ensures responses match internal emotional state, not just user input

Key functions:
- get_clarifying_prompt: Retrieve a non-repetitive clarifying prompt
- get_frequency_reflection: Retrieve a non-repetitive reflection
- rotate_template: Select next template in rotation
- add_template: Add custom templates to banks
- get_response_for_mood: NEW - Select templates by agent mood
"""

import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class PromptCategory(Enum):
    """Categories for clarifying prompts."""

    PRONOUN_AMBIGUITY = "pronoun_ambiguity"
    TEMPORAL_MARKER = "temporal_marker"
    COMBINED_SIGNAL = "combined_signal"


class ReflectionCategory(Enum):
    """Categories for reflections based on frequency."""

    LOW_FREQUENCY = "low_frequency"  # 2 occurrences
    MEDIUM_FREQUENCY = "medium_frequency"  # 3 occurrences
    HIGH_FREQUENCY = "high_frequency"  # 4 occurrences
    VERY_HIGH_FREQUENCY = "very_high_frequency"  # 5+ occurrences


@dataclass
class Template:
    """Individual response template."""

    text: str
    category: str
    frequency_threshold: Optional[int] = None
    weight: float = 1.0  # Weight for random selection (higher = more likely)
    agent_mood: Optional[str] = None  # NEW: Mood affinity (e.g., "concerned", "listening")
    times_used: int = 0
    last_used_at: Optional[str] = None


@dataclass
class TemplateBank:
    """Bank of templates for a specific category."""

    name: str
    templates: List[Template] = field(default_factory=list)
    rotation_index: int = 0
    last_rotation_at: Optional[str] = None

    def add_template(self, text: str, weight: float = 1.0, agent_mood: Optional[str] = None) -> None:
        """Add a template to the bank.

        Args:
            text: Template text
            weight: Selection weight (higher = more likely)
            agent_mood: NEW - Mood affinity for this template
        """
        template = Template(text=text, category=self.name, weight=weight, agent_mood=agent_mood)
        self.templates.append(template)

    def get_next_template(self, use_rotation: bool = True, agent_mood: Optional[str] = None) -> Optional[Template]:
        """Get next template using rotation or weighted random selection.
        
        NEW: Can filter by agent mood.

        Args:
            use_rotation: If True, use round-robin rotation; if False, use weighted random
            agent_mood: NEW - Filter templates by mood affinity

        Returns:
            Template or None if bank is empty
        """
        if not self.templates:
            return None

        # NEW: Filter by mood if specified
        candidates = self.templates
        if agent_mood:
            candidates = [
                t for t in self.templates
                if t.agent_mood is None or t.agent_mood == agent_mood
            ]
        
        if not candidates:
            # Fall back to all templates if no mood match
            candidates = self.templates

        if use_rotation:
            # Round-robin rotation to ensure variety
            template = candidates[self.rotation_index % len(candidates)]
            self.rotation_index = (self.rotation_index + 1) % len(candidates)
        else:
            # Weighted random selection
            total_weight = sum(t.weight for t in candidates)
            choice = random.uniform(0, total_weight)
            current = 0

            for template in candidates:
                current += template.weight
                if choice <= current:
                    break
            else:
                template = candidates[-1]

        return template


class ResponseTemplates:
    """Manages response templates with rotation and variation logic."""

    def __init__(self):
        """Initialize template banks."""
        self.pronoun_clarifiers = self._init_pronoun_clarifiers()
        self.temporal_clarifiers = self._init_temporal_clarifiers()
        self.combined_clarifiers = self._init_combined_clarifiers()
        self.low_freq_reflections = self._init_low_freq_reflections()
        self.medium_freq_reflections = self._init_medium_freq_reflections()
        self.high_freq_reflections = self._init_high_freq_reflections()
        self.very_high_freq_reflections = self._init_very_high_freq_reflections()

        # Track usage for feedback-driven adaptation
        self.usage_history: List[Dict[str, Any]] = []

    def _init_pronoun_clarifiers(self) -> TemplateBank:
        """Initialize pronoun ambiguity clarifying prompts."""
        bank = TemplateBank(name="pronoun_clarifiers")

        bank.add_template("When you say 'they', who do you mean?", weight=1.5)
        bank.add_template(
            "I want to make sure I understand—who are you talking about?")
        bank.add_template(
            "Could you help me understand who you're referring to?")
        bank.add_template("Just to be clear, who do you mean by 'they'?")
        bank.add_template("I'm curious—who's involved in this situation?")
        bank.add_template("Can you name the people you're talking about?")
        bank.add_template("Who specifically are you describing?")

        return bank

    def _init_temporal_clarifiers(self) -> TemplateBank:
        """Initialize temporal marker clarifying prompts."""
        bank = TemplateBank(name="temporal_clarifiers")

        bank.add_template(
            "You mention this keeps happening—how long has this been going on?",
            weight=1.5,
        )
        bank.add_template(
            "I notice a pattern here. How often is this occurring?")
        bank.add_template("When you say 'always', how far back does that go?")
        bank.add_template(
            "Is this something recent, or has it been a longer pattern?",
            weight=1.5,
        )
        bank.add_template("Can you tell me more about the timeline of this?")
        bank.add_template("How long have you been dealing with this?")
        bank.add_template("Since when has this been happening?")

        return bank

    def _init_combined_clarifiers(self) -> TemplateBank:
        """Initialize combined signal clarifying prompts."""
        bank = TemplateBank(name="combined_clarifiers")

        bank.add_template(
            "Help me understand this better: who's involved, and how long has it been happening?",
            weight=1.5,
        )
        bank.add_template(
            "There's a lot here. Can you clarify who you're talking about and when this started?"
        )
        bank.add_template(
            "I want to get the full picture—who's doing what, and is this new or ongoing?"
        )
        bank.add_template(
            "Let me ask two things: who specifically, and how often is this happening?"
        )
        bank.add_template(
            "Can you paint a clearer picture for me? Who's in this situation, and for how long?"
        )

        return bank

    def _init_low_freq_reflections(self) -> TemplateBank:
        """Initialize 2-occurrence reflections."""
        bank = TemplateBank(name="low_freq_reflections")

        bank.add_template(
            "I notice {theme} has come up a couple of times. Does that feel right?",
            weight=1.5,
        )
        bank.add_template(
            "I'm seeing a possible pattern with {theme}. Ring any bells?")
        bank.add_template(
            "Twice now you've mentioned {theme}. Is that something you're aware of?")
        bank.add_template(
            "There's a theme emerging around {theme}. Have you noticed?")
        bank.add_template(
            "I'm picking up on {theme} showing up more than once. What do you think?"
        )

        return bank

    def _init_medium_freq_reflections(self) -> TemplateBank:
        """Initialize 3-occurrence reflections."""
        bank = TemplateBank(name="medium_freq_reflections")

        bank.add_template(
            "I'm noticing {theme} is coming up fairly regularly now. What do you make of that?",
            weight=1.5,
        )
        bank.add_template(
            "There's definitely a pattern with {theme} appearing multiple times. Does that surprise you?"
        )
        bank.add_template(
            "You've brought up {theme} several times now. Is this something that's weighing on you?"
        )
        bank.add_template(
            "{theme} seems to be a recurring thread in what you're sharing. What draws you back to it?"
        )
        bank.add_template(
            "I'm seeing {theme} pop up again. Starting to wonder if there's something there?"
        )

        return bank

    def _init_high_freq_reflections(self) -> TemplateBank:
        """Initialize 4-occurrence reflections."""
        bank = TemplateBank(name="high_freq_reflections")

        bank.add_template(
            "It seems like {theme} is becoming more frequent. What do you think is at the root?",
            weight=1.5,
        )
        bank.add_template(
            "{theme} keeps surfacing in our conversations. What would it mean to address this?"
        )
        bank.add_template(
            "I'm noticing {theme} is a pretty consistent theme now. Help me understand what that's about."
        )
        bank.add_template(
            "There's a strong pattern here with {theme}. What would need to shift for you?"
        )
        bank.add_template(
            "{theme} is showing up again and again. What do you want to do about it?"
        )

        return bank

    def _init_very_high_freq_reflections(self) -> TemplateBank:
        """Initialize 5+ occurrence reflections."""
        bank = TemplateBank(name="very_high_freq_reflections")

        bank.add_template(
            "{theme} stands out as a recurring theme in what you've shared with me. What keeps bringing it back?",
            weight=1.5,
        )
        bank.add_template(
            "There's a clear loop here with {theme}. I'm wondering—is this feeling stuck?"
        )
        bank.add_template(
            "{theme} is such a dominant thread now. How long has this been the case?"
        )
        bank.add_template(
            "This is a deeply recurring pattern with {theme}. What would help break the cycle?"
        )
        bank.add_template(
            "{theme} is almost everything in our recent conversations. That feels significant. What's happening?"
        )

        return bank

    def get_clarifying_prompt(
        self,
        signal_type: str,
        detected_content: Optional[str] = None,
        use_rotation: bool = True,
    ) -> str:
        """Get a clarifying prompt based on signal type.

        Args:
            signal_type: Type of signal ('pronoun', 'temporal', or 'combined')
            detected_content: Optional detected pronouns or markers for template formatting
            use_rotation: If True, use round-robin rotation; otherwise weighted random

        Returns:
            Clarifying prompt text
        """
        bank_map = {
            "pronoun": self.pronoun_clarifiers,
            "temporal": self.temporal_clarifiers,
            "combined": self.combined_clarifiers,
        }

        bank = bank_map.get(signal_type.lower())
        if not bank:
            return "Could you clarify that for me?"

        template = bank.get_next_template(use_rotation=use_rotation)
        if not template:
            return "Could you tell me more?"

        # Track usage
        self._track_usage(template.text, signal_type, "clarifier")

        return template.text

    def get_frequency_reflection(
        self,
        frequency: int,
        theme: str,
        use_rotation: bool = True,
    ) -> str:
        """Get a reflection based on frequency.

        Args:
            frequency: How many times theme has appeared
            theme: Emotional theme description
            use_rotation: If True, use round-robin rotation

        Returns:
            Reflection text with theme inserted
        """
        bank_map = {
            2: self.low_freq_reflections,
            3: self.medium_freq_reflections,
            4: self.high_freq_reflections,
            5: self.very_high_freq_reflections,
        }

        # Get appropriate bank based on frequency
        if frequency >= 5:
            bank = bank_map[5]
        elif frequency >= 4:
            bank = bank_map[4]
        elif frequency >= 3:
            bank = bank_map[3]
        else:  # 2
            bank = bank_map[2]

        template = bank.get_next_template(use_rotation=use_rotation)
        if not template:
            return f"I'm noticing a pattern with {theme}."

        # Format template with theme
        reflection = template.text.format(theme=theme)

        # Track usage
        self._track_usage(reflection, f"frequency_{frequency}", "reflection")

        return reflection

    def add_custom_clarifier(
        self, signal_type: str, text: str, weight: float = 1.0
    ) -> None:
        """Add a custom clarifying prompt.

        Args:
            signal_type: Type of signal ('pronoun', 'temporal', or 'combined')
            text: Prompt text
            weight: Selection weight
        """
        bank_map = {
            "pronoun": self.pronoun_clarifiers,
            "temporal": self.temporal_clarifiers,
            "combined": self.combined_clarifiers,
        }

        bank = bank_map.get(signal_type.lower())
        if bank:
            bank.add_template(text, weight=weight)

    def add_custom_reflection(
        self, frequency: int, text: str, weight: float = 1.0
    ) -> None:
        """Add a custom reflection.

        Args:
            frequency: Frequency threshold (2, 3, 4, or 5+)
            text: Reflection text (should include {theme} placeholder)
            weight: Selection weight
        """
        bank_map = {
            2: self.low_freq_reflections,
            3: self.medium_freq_reflections,
            4: self.high_freq_reflections,
            5: self.very_high_freq_reflections,
        }

        bank = bank_map.get(frequency)
        if bank:
            bank.add_template(text, weight=weight)

    def get_response_for_mood(
        self,
        agent_mood: str,
        signal_type: str = "combined",
        theme: Optional[str] = None,
        use_rotation: bool = True,
    ) -> str:
        """NEW (Phase 2): Get a response that matches agent's current mood.
        
        This ensures that the agent's internal emotional state influences
        the structure and tone of responses, not just the user's affect.

        Args:
            agent_mood: Agent's current mood ('listening', 'concerned', 'moved', etc.)
            signal_type: Type of signal to respond to ('pronoun', 'temporal', 'combined')
            theme: Emotional theme (if available)
            use_rotation: If True, use round-robin rotation

        Returns:
            Response text matched to agent mood
        """
        # Mood-to-template affinity mapping
        # These influence which response templates are selected
        mood_affinities = {
            "listening": ["thoughtful", "curious"],
            "resonating": ["attuned", "moved"],
            "concerned": ["caring", "protective"],
            "moving": ["vulnerable", "present"],
            "protective": ["grounded", "strong"],
            "reflective": ["introspective", "wondering"],
            "uncertain": ["honest", "curious"],
            "grounded": ["steady", "present"],
        }
        
        # Get the bank for this signal type
        bank_map = {
            "pronoun": self.pronoun_clarifiers,
            "temporal": self.temporal_clarifiers,
            "combined": self.combined_clarifiers,
        }
        
        bank = bank_map.get(signal_type.lower(), self.combined_clarifiers)
        
        # Get template filtered by agent mood
        template = bank.get_next_template(use_rotation=use_rotation, agent_mood=agent_mood)
        
        if not template:
            # Fallback to unfiltered selection
            template = bank.get_next_template(use_rotation=use_rotation)
        
        if not template:
            return "I'm here, and I'm listening."
        
        response = template.text
        
        # If we have a theme, inject it
        if theme and "{theme}" in response:
            response = response.format(theme=theme)
        
        # Track usage
        self._track_usage(response, f"mood_{agent_mood}", "mood_aware")
        
        return response

    def _track_usage(self, template_text: str, context: str, response_type: str) -> None:
        """Track usage of templates for adaptive learning.

        Args:
            template_text: The template that was used
            context: Context of usage (signal_type or frequency)
            response_type: Type of response ('clarifier' or 'reflection')
        """
        from datetime import datetime, timezone

        self.usage_history.append(
            {
                "template_text": template_text,
                "context": context,
                "response_type": response_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        # Keep history size manageable (last 1000 uses)
        if len(self.usage_history) > 1000:
            self.usage_history = self.usage_history[-1000:]

    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get statistics about template usage.

        Returns:
            Dictionary with usage statistics
        """
        if not self.usage_history:
            return {"total_uses": 0, "response_types": {}}

        response_types = {}
        for entry in self.usage_history:
            rt = entry["response_type"]
            response_types[rt] = response_types.get(rt, 0) + 1

        return {
            "total_uses": len(self.usage_history),
            "response_types": response_types,
            "history_size": len(self.usage_history),
        }


# Singleton instance for module-level access
_templates = ResponseTemplates()


def get_clarifying_prompt(
    signal_type: str, detected_content: Optional[str] = None, use_rotation: bool = True
) -> str:
    """Module-level function to get clarifying prompt.

    Args:
        signal_type: Type of signal ('pronoun', 'temporal', or 'combined')
        detected_content: Optional detected content for formatting
        use_rotation: If True, use round-robin rotation

    Returns:
        Clarifying prompt text
    """
    return _templates.get_clarifying_prompt(
        signal_type, detected_content, use_rotation=use_rotation
    )


def get_frequency_reflection(
    frequency: int, theme: str, use_rotation: bool = True
) -> str:
    """Module-level function to get frequency reflection.

    Args:
        frequency: How many times theme has appeared
        theme: Emotional theme description
        use_rotation: If True, use round-robin rotation

    Returns:
        Reflection text
    """
    return _templates.get_frequency_reflection(frequency, theme, use_rotation=use_rotation)


def add_custom_clarifier(signal_type: str, text: str, weight: float = 1.0) -> None:
    """Module-level function to add custom clarifier.

    Args:
        signal_type: Type of signal
        text: Prompt text
        weight: Selection weight
    """
    _templates.add_custom_clarifier(signal_type, text, weight)


def add_custom_reflection(frequency: int, text: str, weight: float = 1.0) -> None:
    """Module-level function to add custom reflection.

    Args:
        frequency: Frequency threshold
        text: Reflection text
        weight: Selection weight
    """
    _templates.add_custom_reflection(frequency, text, weight)
