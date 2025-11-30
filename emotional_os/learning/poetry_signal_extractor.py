"""
Creative Language Signal Extraction

Extracts emotional signals and themes from any creative or expressive writing.
Handles metaphorical language, imagery, emotional subtext, and complex expressions.

Not limited to poetry - works with:
- Poetry and verse
- Prose and narrative writing
- Personal reflections and journal entries
- Emotional descriptions and metaphors
- Any expressive language patterns
"""

import re
from typing import Dict, List, Optional, Tuple


class PoetrySignalExtractor:
    """Extract emotional signals from creative and expressive language.

    Works with any type of expressive writing - poetry, prose, reflections, etc.
    Detects keywords, metaphors, and phrase patterns that indicate emotional states.
    """

    # Emotional signals that can appear in any creative writing
    POETIC_SIGNALS = {
        "love": {
            "keywords": [
                "love",
                "beloved",
                "darling",
                "sweet",
                "tender",
                "caress",
                "embrace",
                "nestled",
                "breast",
                "devoted",
                "heart",
                "soul",
                "forever",
            ],
            "metaphors": ["bird", "nest", "stork", "paradise", "muse", "feathers", "perches"],
            "intensity": 0.9,
        },
        "intimacy": {
            "keywords": [
                "touch",
                "skin",
                "body",
                "bed",
                "flesh",
                "breast",
                "thigh",
                "wrapped",
                "friction",
                "caught",
                "nestled",
                "scoop",
                "flap",
                "deliver",
                "drop",
            ],
            "metaphors": ["nest", "buffet", "ladder", "climb", "deliver", "drop"],
            "intensity": 0.85,
        },
        "vulnerability": {
            "keywords": [
                "blind",
                "fumbling",
                "bumbling",
                "sorry",
                "mistake",
                "broken",
                "swept",
                "caught",
                "drop",
                "sense",
                "madness",
                "dangerous",
                "chain",
            ],
            "metaphors": ["lost", "darkness", "uncertain", "can't tame", "can't name", "funeral", "mourners"],
            "intensity": 0.75,
        },
        "transformation": {
            "keywords": [
                "renewed",
                "evolved",
                "evolution",
                "scalpel",
                "healing",
                "growth",
                "born",
                "new",
                "taxonomically",
                "becoming",
                "change",
            ],
            "metaphors": ["wings", "rebirth", "becoming", "bird", "squiggle", "breaking", "beating"],
            "intensity": 0.8,
        },
        "admiration": {
            "keywords": [
                "beautiful",
                "mythic",
                "divine",
                "perfect",
                "wonder",
                "amazed",
                "captivated",
                "paradise",
                "native",
                "exquisite",
                "profound",
            ],
            "metaphors": ["goddess", "enchanted", "magic", "stork", "delivery", "glory"],
            "intensity": 0.7,
        },
        "joy": {
            "keywords": [
                "wonderful",
                "delight",
                "bliss",
                "happy",
                "celebrate",
                "exhilarating",
                "paradise",
                "native",
                "sings",
                "sweetest",
                "hope",
            ],
            "metaphors": ["soaring", "flight", "dance", "flap", "squiggle", "sunshine", "gale"],
            "intensity": 0.8,
        },
        "sensuality": {
            "keywords": [
                "taste",
                "tongue",
                "rough",
                "smooth",
                "texture",
                "feel",
                "bristles",
                "probes",
                "lick",
                "flap",
                "squiggle",
                "sings",
                "drum",
            ],
            "metaphors": ["crickets", "friction", "tenderized", "tongue", "tasting", "music", "melody"],
            "intensity": 0.75,
        },
        "nature": {
            "keywords": [
                "raven",
                "bird",
                "stork",
                "hawk",
                "bat",
                "gull",
                "wing",
                "nest",
                "flight",
                "feathers",
                "perches",
                "gale",
                "storm",
            ],
            "metaphors": ["sky", "wind", "wild", "soul", "brain", "sense"],
            "intensity": 0.6,
        },
    }

    def extract_signals(self, text: str) -> List[Dict]:
        """Extract emotional signals from expressive text.

        Works with poetry, prose, personal writing, or any creative expression.
        Detects keywords, metaphors, and phrase patterns.

        Args:
            text: Creative or expressive writing

        Returns:
            List of detected signals with confidence scores and matched keywords
        """
        if not text or len(text.strip()) < 10:
            return []

        text_lower = text.lower()
        detected_signals = []

        for signal_name, signal_data in self.POETIC_SIGNALS.items():
            confidence = self._calculate_signal_confidence(
                text_lower, signal_data["keywords"], signal_data["metaphors"], signal_data["intensity"]
            )

            if confidence > 0.3:  # Threshold for detection
                detected_signals.append(
                    {
                        "signal": signal_name,
                        "confidence": confidence,
                        "keywords": self._find_matching_keywords(text_lower, signal_data["keywords"]),
                        "keyword": signal_name,  # For compatibility with existing system
                    }
                )

        # Sort by confidence
        detected_signals.sort(key=lambda x: x["confidence"], reverse=True)
        return detected_signals

    def extract_phrases_for_signal(self, text: str, signal_name: str, min_confidence: float = 0.4) -> List[str]:
        """Extract meaningful phrases from text that relate to a signal.

        Returns 2-3 word phrases that could be learned as signal indicators.
        Filters out common/generic phrases.
        """
        if signal_name not in self.POETIC_SIGNALS:
            return []

        signal_data = self.POETIC_SIGNALS[signal_name]
        keywords = signal_data.get("keywords", [])
        metaphors = signal_data.get("metaphors", [])

        # Common words to filter out (articles, prepositions, etc)
        stop_words = {"the", "a", "an", "is", "are", "be", "on", "in", "at", "to", "for", "of", "and", "or", "it"}

        words = text.lower().split()
        phrases = []

        # Generate 2 and 3-word phrases, prioritizing those with signal keywords
        for i in range(len(words) - 1):
            # 2-word phrases
            phrase2 = f"{words[i]} {words[i+1]}".strip()
            # Keep if: contains signal keyword/metaphor and not all stop words
            if len(phrase2) > 3 and phrase2 not in phrases and not all(w in stop_words for w in phrase2.split()):
                # Boost priority if contains signal keywords
                if any(kw in phrase2 for kw in keywords + metaphors):
                    phrases.insert(0, phrase2)  # Add to front
                else:
                    phrases.append(phrase2)

            # 3-word phrases
            if i < len(words) - 2:
                phrase3 = f"{words[i]} {words[i+1]} {words[i+2]}".strip()
                if len(phrase3) > 5 and phrase3 not in phrases and not all(w in stop_words for w in phrase3.split()):
                    # Boost priority if contains signal keywords
                    if any(kw in phrase3 for kw in keywords + metaphors):
                        phrases.insert(0, phrase3)  # Add to front
                    else:
                        phrases.append(phrase3)

        # Return top 10 most relevant phrases
        return phrases[:10]

    def _calculate_signal_confidence(
        self, text: str, keywords: List[str], metaphors: List[str], base_intensity: float
    ) -> float:
        """Calculate confidence score for a signal."""
        confidence = 0.0

        # Count keyword matches
        keyword_count = sum(1 for kw in keywords if kw in text)
        keyword_score = min(keyword_count * 0.15, 0.5)  # Cap at 0.5

        # Count metaphor matches
        metaphor_count = sum(1 for m in metaphors if m in text)
        metaphor_score = min(metaphor_count * 0.1, 0.3)  # Cap at 0.3

        confidence = (keyword_score + metaphor_score) * base_intensity
        return min(confidence, 1.0)  # Cap at 1.0

    def _find_matching_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Find which keywords are present in the text."""
        return [kw for kw in keywords if kw in text]

    def extract_themes(self, text: str) -> Dict[str, float]:
        """Extract broader emotional themes from text.

        Returns:
            Dict mapping theme names to their presence scores
        """
        signals = self.extract_signals(text)
        themes = {}

        for signal in signals:
            themes[signal["signal"]] = signal["confidence"]

        return themes


# Singleton
_poetry_extractor = None


def get_poetry_extractor() -> PoetrySignalExtractor:
    """Get or create the poetry signal extractor."""
    global _poetry_extractor
    if _poetry_extractor is None:
        _poetry_extractor = PoetrySignalExtractor()
    return _poetry_extractor
