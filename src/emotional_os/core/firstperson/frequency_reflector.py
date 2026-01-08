"""Frequency Reflection Module for FirstPerson.

Detects repeated emotional themes and generates gentle reflections that
help users recognize patterns in their emotional loops.

Key functions:
- detect_theme: Extract semantic theme from input
- count_theme_frequency: Count occurrences in memory
- generate_frequency_reflection: Create reflection based on frequency
- analyze_frequency: Orchestrate detection and generation
"""

import re
from typing import Dict, List, Optional, Tuple
from collections import Counter


class FrequencyReflector:
    """Detects and reflects on repeated emotional themes."""

    # Semantic theme categories and their keywords
    THEME_PATTERNS = {
        "family_conflict": {
            "keywords": [
                "kids",
                "children",
                "parent",
                "sibling",
                "family",
                "mom",
                "dad",
                "brother",
                "sister",
                "husband",
                "wife",
                "spouse",
            ],
            "description": "family conflict",
        },
        "work_stress": {
            "keywords": [
                "work",
                "boss",
                "colleague",
                "meeting",
                "deadline",
                "job",
                "project",
                "team",
                "office",
                "client",
                "manager",
            ],
            "description": "work-related stress",
        },
        "relationship_tension": {
            "keywords": [
                "belittling",
                "ignored",
                "dismissed",
                "hurt",
                "betrayed",
                "lonely",
                "disconnected",
                "cold",
                "distant",
                "misunderstood",
            ],
            "description": "relationship tension",
        },
        "self_doubt": {
            "keywords": [
                "shame",
                "ashamed",
                "embarrassed",
                "failure",
                "failed",
                "weak",
                "stupid",
                "worthless",
                "inadequate",
                "not good enough",
            ],
            "description": "self-doubt",
        },
        "overwhelm": {
            "keywords": [
                "overwhelm",
                "overwhelmed",
                "exhausted",
                "tired",
                "burned out",
                "too much",
                "can't handle",
                "breaking down",
                "stressed",
            ],
            "description": "feeling overwhelmed",
        },
        "joy_celebration": {
            "keywords": [
                "happy",
                "joy",
                "wonderful",
                "amazing",
                "excited",
                "proud",
                "celebrated",
                "loved",
                "appreciated",
                "blessed",
            ],
            "description": "joy and celebration",
        },
        "anxiety": {
            "keywords": [
                "anxious",
                "nervous",
                "worried",
                "afraid",
                "scared",
                "panic",
                "uneasy",
                "on edge",
                "terrified",
            ],
            "description": "anxiety and fear",
        },
        "grief_loss": {
            "keywords": [
                "grief",
                "grieving",
                "loss",
                "died",
                "death",
                "gone",
                "missing",
                "mourning",
                "heartbroken",
            ],
            "description": "grief and loss",
        },
    }

    # Reflection templates based on frequency
    FREQUENCY_TEMPLATES = {
        2: {
            "verb": "come up",
            "phrase": "I notice {theme} has come up a couple of times. Does that feel true?",
        },
        3: {
            "verb": "appear",
            "phrase": "I'm noticing {theme} has come up a few times lately. Is this a pattern you're aware of?",
        },
        4: {
            "verb": "seem",
            "phrase": "It seems like {theme} is becoming more frequent. What do you think is at the root?",
        },
        5: {
            "verb": "stand out",
            "phrase": "{theme} stands out as a recurring theme in what you've shared with me. What keeps bringing it back?",
        },
    }

    def __init__(self):
        """Initialize the frequency reflector."""
        self.theme_history: List[str] = []
        self.theme_counts: Dict[str, int] = {}

    def detect_theme(self, text: str) -> Optional[str]:
        """Detect the primary emotional theme in the input.

        Args:
            text: User input to analyze

        Returns:
            Theme key if detected, None otherwise
        """
        lower_text = text.lower()
        theme_scores: Dict[str, int] = {}

        for theme_key, theme_info in self.THEME_PATTERNS.items():
            score = 0
            for keyword in theme_info["keywords"]:
                # Count keyword occurrences (whole word only)
                pattern = r"\b" + re.escape(keyword) + r"\b"
                matches = len(re.findall(pattern, lower_text))
                score += matches

            if score > 0:
                theme_scores[theme_key] = score

        # Return theme with highest score
        if theme_scores:
            return max(theme_scores, key=theme_scores.get)

        return None

    def record_theme(self, text: str) -> Optional[str]:
        """Record a detected theme to the frequency history.

        Args:
            text: User input to analyze and record

        Returns:
            Detected theme key, or None
        """
        theme = self.detect_theme(text)

        if theme:
            self.theme_history.append(theme)
            self.theme_counts[theme] = self.theme_counts.get(theme, 0) + 1

        return theme

    def get_theme_frequency(self, theme: str, window: Optional[int] = None) -> int:
        """Get frequency of a specific theme.

        Args:
            theme: Theme key to count
            window: Optional window size (count only last N entries). None = all time.

        Returns:
            Count of theme occurrences
        """
        if window:
            recent = self.theme_history[-window:]
            return recent.count(theme)

        return self.theme_counts.get(theme, 0)

    def analyze_frequency(self, text: str) -> Dict[str, any]:
        """Analyze frequency of detected theme.

        Args:
            text: User input to analyze

        Returns:
            Dictionary with theme, frequency, and reflection data
        """
        theme = self.detect_theme(text)

        if not theme:
            return {
                "detected_theme": None,
                "frequency": 0,
                "should_reflect": False,
                "reflection": None,
            }

        # Record the theme
        self.record_theme(text)

        frequency = self.get_theme_frequency(theme)
        theme_description = self.THEME_PATTERNS[theme]["description"]

        # Determine if we should reflect based on frequency
        should_reflect = frequency >= 2

        reflection = None
        if should_reflect:
            reflection = self.generate_frequency_reflection(theme, frequency)

        return {
            "detected_theme": theme,
            "theme_description": theme_description,
            "frequency": frequency,
            "should_reflect": should_reflect,
            "reflection": reflection,
            "confidence": self._calculate_confidence(theme, text),
        }

    def generate_frequency_reflection(self, theme: str, frequency: int) -> str:
        """Generate a reflection based on theme frequency.

        Args:
            theme: Theme key
            frequency: Number of times theme has appeared

        Returns:
            Natural language reflection
        """
        theme_description = self.THEME_PATTERNS[theme]["description"]

        # Select template based on frequency
        if frequency >= 5:
            template_key = 5
        elif frequency >= 4:
            template_key = 4
        elif frequency >= 3:
            template_key = 3
        else:  # 2
            template_key = 2

        template = self.FREQUENCY_TEMPLATES[template_key]["phrase"]
        reflection = template.format(theme=theme_description)

        return reflection

    def _calculate_confidence(self, theme: str, text: str) -> float:
        """Calculate confidence in theme detection.

        Args:
            theme: Detected theme
            text: User input

        Returns:
            Confidence score 0-1
        """
        lower_text = text.lower()
        keywords = self.THEME_PATTERNS[theme]["keywords"]

        matching = sum(
            1
            for kw in keywords
            if re.search(r"\b" + re.escape(kw) + r"\b", lower_text)
        )

        # Confidence = matching keywords / total keywords
        confidence = min(1.0, matching / len(keywords) if keywords else 0)
        return confidence

    def get_top_themes(self, limit: int = 3) -> List[Tuple[str, int]]:
        """Get top recurring themes.

        Args:
            limit: Number of themes to return

        Returns:
            List of (theme, count) tuples sorted by frequency
        """
        return sorted(
            self.theme_counts.items(), key=lambda x: x[1], reverse=True
        )[:limit]


# Singleton instance for module-level use
_reflector = FrequencyReflector()


def detect_theme(text: str) -> Optional[str]:
    """Module-level function to detect theme.

    Args:
        text: User input to analyze

    Returns:
        Theme key or None
    """
    return _reflector.detect_theme(text)


def analyze_frequency(text: str) -> Dict[str, any]:
    """Module-level function to analyze frequency.

    Args:
        text: User input to analyze

    Returns:
        Dictionary with frequency analysis
    """
    return _reflector.analyze_frequency(text)


def get_frequency_reflection(text: str) -> Optional[str]:
    """Module-level function to get reflection if threshold met.

    Args:
        text: User input to analyze

    Returns:
        Reflection string or None
    """
    analysis = _reflector.analyze_frequency(text)
    return analysis.get("reflection")
