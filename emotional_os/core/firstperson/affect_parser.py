"""Affect Parser for Phase 2.1: Emotional Attunement.

Detects emotional affect dimensions from user input to enable response modulation.
Classifies tone, valence (positive/negative), and arousal (intensity).

Dimensions:
- Tone: sardonic, warm, neutral, sad, anxious, angry, grateful, confused
- Valence: -1 (negative) to +1 (positive)
- Arousal: 0 (calm) to 1 (intense)
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class AffectAnalysis:
    """Result of affect parsing."""

    tone: str  # Primary tone category
    tone_confidence: float  # 0-1 confidence in tone classification
    valence: float  # -1 to +1, negative to positive
    arousal: float  # 0 to 1, calm to intense
    secondary_tones: list[str]  # Alternative tones (2-3 items)
    explanation: str  # Human-readable summary


class AffectParser:
    """Detects emotional affect from conversational text.

    Lightweight keyword-based approach suitable for per-message processing.
    No heavy NLP models; trades some accuracy for speed and privacy.
    """

    def __init__(self):
        """Initialize affect parser with tone lexicons."""
        self._initialize_lexicons()

    def _initialize_lexicons(self) -> None:
        """Build emotional keyword lexicons for each tone category."""
        # Tone-specific keywords (curated emotional vocabulary)
        self.tone_lexicons = {
            "warm": {
                "keywords": [
                    "love", "appreciate", "grateful", "thankful", "blessed", "wonderful",
                    "beautiful", "caring", "supportive", "kind", "compassionate", "nurture",
                    "hug", "smile", "joy", "happy", "excited", "looking forward", "can't wait",
                    "adore", "cherish", "embrace", "heartfelt", "sincere", "genuine",
                ],
                "valence": 0.8,
                "arousal": 0.4,
            },
            "sardonic": {
                "keywords": [
                    "right", "sure", "obviously", "yeah right", "great idea", "fantastic",
                    "wonderful", "perfect", "as if", "whatever", "eye roll", "seriously",
                    "oh please", "sure thing", "absolutely", "ironic", "witty", "clever",
                    "backhanded", "cutting", "wry", "sarcasm", "tongue in cheek",
                ],
                "valence": -0.4,
                "arousal": 0.3,
            },
            "sad": {
                "keywords": [
                    "sad", "depressed", "miserable", "unhappy", "lonely", "hopeless",
                    "devastated", "heartbroken", "grief", "lost", "empty", "hollow",
                    "crying", "tears", "down", "low", "blue", "melancholy", "despair",
                    "nothing matters", "pointless", "exhausted", "drain", "weary",
                ],
                "valence": -0.9,
                "arousal": 0.2,
            },
            "anxious": {
                "keywords": [
                    "anxious", "worried", "nervous", "tense", "stressed", "panic",
                    "afraid", "scared", "terrified", "overwhelmed", "uneasy", "on edge",
                    "what if", "dreading", "can't sleep", "racing thoughts", "jittery",
                    "tight", "pressure", "knot in stomach", "trembling", "hypervigilant",
                ],
                "valence": -0.7,
                "arousal": 0.8,
            },
            "angry": {
                "keywords": [
                    "angry", "furious", "rage", "mad", "outraged", "incensed",
                    "livid", "fed up", "done", "can't take it", "fed up", "sick of",
                    "hate", "despise", "disgusted", "bitter", "resentment",
                    "yelling", "aggressive", "hostile", "confrontational", "explosive",
                    "enraged", "seething", "boiling", "pissed", "infuriated",
                ],
                "valence": -0.8,
                "arousal": 0.9,
            },
            "neutral": {
                "keywords": [
                    "so", "actually", "basically", "anyway", "nothing special",
                    "fine", "okay", "alright", "seems", "appears", "suggests",
                    "likely", "probably", "perhaps", "may be", "somewhat",
                    "fairly", "quite", "reasonable", "sensible", "logical",
                ],
                "valence": 0.0,
                "arousal": 0.3,
            },
            "grateful": {
                "keywords": [
                    "thank you", "thanks", "grateful", "thankful", "appreciate",
                    "blessed", "lucky", "fortunate", "privilege", "honored",
                    "indebted", "owe you", "you came through", "lifesaver",
                    "generous", "kind", "thoughtful", "means a lot", "touched",
                ],
                "valence": 0.9,
                "arousal": 0.3,
            },
            "confused": {
                "keywords": [
                    "confused", "not sure", "unclear", "lost", "mixed up",
                    "bewildered", "perplexed", "baffled", "what", "huh",
                    "don't understand", "make sense", "explain", "how does",
                    "why is", "uncertain", "unsure", "contradictory", "confusing",
                ],
                "valence": -0.3,
                "arousal": 0.5,
            },
        }

        # Intensifiers that boost arousal
        self.intensifiers = [
            "very", "so", "really", "extremely", "absolutely", "incredibly",
            "totally", "completely", "utterly", "definitely", "certainly",
            "truly", "deeply", "profoundly", "terribly", "awfully",
        ]

        # Negation words (invert valence)
        self.negations = ["not", "no", "never",
                          "neither", "nor", "barely", "hardly"]

    def analyze_affect(self, text: str) -> AffectAnalysis:
        """Analyze emotional affect from input text.

        Args:
            text: User input to analyze

        Returns:
            AffectAnalysis with tone, valence, and arousal
        """
        if not text or not isinstance(text, str):
            return AffectAnalysis(
                tone="neutral",
                tone_confidence=0.5,
                valence=0.0,
                arousal=0.3,
                secondary_tones=[],
                explanation="No text to analyze",
            )

        text_lower = text.lower()
        text_words = re.findall(r"\b\w+\b", text_lower)

        # Score each tone category
        tone_scores = {}
        for tone, lexicon in self.tone_lexicons.items():
            score = self._calculate_tone_score(
                text_words, lexicon["keywords"], text_lower)
            tone_scores[tone] = score

        # Find primary tone
        primary_tone = max(tone_scores, key=tone_scores.get)
        primary_score = tone_scores[primary_tone]
        tone_confidence = min(1.0, primary_score / 5.0)  # Normalize to 0-1

        # Get secondary tones (top 2-3 after primary)
        sorted_tones = sorted(tone_scores.items(),
                              key=lambda x: x[1], reverse=True)
        secondary_tones = [t[0] for t in sorted_tones[1:4] if t[1] > 0]

        # Calculate valence and arousal from primary tone and modifiers
        base_valence = self.tone_lexicons[primary_tone]["valence"]
        base_arousal = self.tone_lexicons[primary_tone]["arousal"]

        valence = self._adjust_for_modifiers(base_valence, text_lower)
        arousal = self._adjust_arousal_for_intensity(base_arousal, text_words)

        # Clamp to valid ranges
        valence = max(-1.0, min(1.0, valence))
        arousal = max(0.0, min(1.0, arousal))

        explanation = self._generate_explanation(
            primary_tone, valence, arousal, tone_confidence
        )

        return AffectAnalysis(
            tone=primary_tone,
            tone_confidence=tone_confidence,
            valence=valence,
            arousal=arousal,
            secondary_tones=secondary_tones,
            explanation=explanation,
        )

    def _calculate_tone_score(self, words: list[str], keywords: list[str], text: str) -> float:
        """Score tone category based on keyword matches.

        Args:
            words: Tokenized words from text
            keywords: Keywords for this tone category
            text: Original lowercased text

        Returns:
            Score (higher = more confident in this tone)
        """
        score = 0.0

        for keyword in keywords:
            # Exact word match (check word boundaries)
            pattern = rf"\b{re.escape(keyword)}\b"
            if re.search(pattern, text):
                score += 1.5
            # Partial match (substring)
            elif keyword in text:
                score += 0.5

        # Bonus: multiple keywords from same category increases confidence
        if score > 0:
            score *= 1.2

        return score

    def _adjust_for_modifiers(self, base_valence: float, text: str) -> float:
        """Adjust valence for negation and intensifiers.

        Args:
            base_valence: Base valence from tone category
            text: Lowercased text to scan for modifiers

        Returns:
            Adjusted valence
        """
        valence = base_valence

        # Check for negation (flips positive/negative)
        # E.g., "I'm not happy" → negative even though "happy" is positive
        for negation in self.negations:
            pattern = rf"{negation}\s+\w+\s+\w*(?:happy|good|great|wonderful|love)"
            if re.search(pattern, text):
                valence = -abs(valence)  # Make negative
                break

        # Negation doesn't flip sad/angry (already negative)
        for negation in self.negations:
            pattern = rf"{negation}\s+\w+\s+\w*(?:sad|angry|upset)"
            if re.search(pattern, text):
                valence = abs(valence) * 0.5  # Soften the negativity
                break

        return valence

    def _adjust_arousal_for_intensity(self, base_arousal: float, words: list[str]) -> float:
        """Adjust arousal based on intensifiers and punctuation.

        Args:
            base_arousal: Base arousal from tone category
            words: Tokenized words

        Returns:
            Adjusted arousal (0-1)
        """
        arousal = base_arousal

        # Count intensifiers (more = higher arousal)
        intensifier_count = sum(
            1 for word in words if word in self.intensifiers)
        if intensifier_count > 0:
            arousal += 0.1 * min(intensifier_count, 3)  # Cap boost at 0.3

        # Exclamation marks (common in high-arousal text)
        # (Check original text for punctuation)
        exclamation_count = len([w for w in words if "!" in w])
        arousal += 0.15 * min(exclamation_count, 2)

        return min(1.0, arousal)  # Clamp to 1.0

    def _generate_explanation(
        self, tone: str, valence: float, arousal: float, confidence: float
    ) -> str:
        """Generate human-readable explanation of affect analysis.

        Args:
            tone: Primary tone category
            valence: -1 to +1 sentiment
            arousal: 0 to 1 intensity

        Returns:
            Explanation string
        """
        valence_label = "positive" if valence > 0.3 else (
            "negative" if valence < -0.3 else "neutral")
        arousal_label = "calm" if arousal < 0.3 else (
            "intense" if arousal > 0.7 else "moderate")

        return (
            f"Detected {tone} tone ({confidence:.0%} confidence) with "
            f"{valence_label} sentiment ({valence:+.2f}) and {arousal_label} intensity ({arousal:.2f})"
        )

    def get_tone_descriptor(self, tone: str) -> str:
        """Get human-readable descriptor for a tone.

        Args:
            tone: Tone category name

        Returns:
            Descriptor suitable for response modulation
        """
        descriptors = {
            "warm": "warmth and empathy",
            "sardonic": "wit and irony",
            "sad": "gentleness and support",
            "anxious": "reassurance and calm",
            "angry": "validation and boundaries",
            "neutral": "clarity and directness",
            "grateful": "acknowledgment",
            "confused": "clarity and explanation",
        }
        return descriptors.get(tone, "neutrality")

    def should_escalate_tone(self, arousal: float, valence: float) -> bool:
        """Determine if response should escalate emotional intensity.

        High arousal + extreme valence suggests user needs matching intensity.

        Args:
            arousal: Intensity level (0-1)
            valence: Sentiment (-1 to +1)

        Returns:
            True if response should match user's intensity
        """
        return arousal > 0.7 or abs(valence) > 0.8

    def should_soften_tone(self, arousal: float, valence: float) -> bool:
        """Determine if response should soften or calm.

        High arousal + negative valence suggests user is distressed.

        Args:
            arousal: Intensity level (0-1)
            valence: Sentiment (-1 to +1)

        Returns:
            True if response should be calming/reassuring
        """
        return arousal > 0.6 and valence < -0.5


def create_affect_parser() -> AffectParser:
    """Factory function to create affect parser instance.

    Returns:
        Initialized AffectParser
    """
    return AffectParser()
