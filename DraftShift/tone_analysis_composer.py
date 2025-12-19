"""
Tone Analysis Composer for DraftShift

Adapted from DynamicResponseComposer to analyze and suggest tone transformations
for legal correspondence instead of generating chat responses.

This system:
1. Extracts semantic entities (who, what, relationships) from text
2. Identifies emotional resonance and tone markers
3. Composes analysis insights about the current tone
4. Suggests contextual transformation strategies for target tones
5. Weaves linguistic patterns that match the desired emotional contour

Result: No two analyses are identical, analysis is contextually aware.
"""

import json
import logging
import re
import sys
import os
from typing import Any, Dict, List, Optional, Tuple

from .constants import (
    LEGAL_SIGNALS,
    TONE_NAMES,
    MESSAGE_ASSESSMENT_MARKERS,
    EMPATHY_WORDS,
    REFLECTION_WORDS,
)

logger = logging.getLogger(__name__)


class ToneAnalysisComposer:
    """Compose tone analysis and transformation insights from legal text."""

    def __init__(self):
        """Initialize linguistic resources for analysis."""
        # Tone-specific linguistic patterns for analysis
        self.tone_characteristics = {
            "Very Formal": {
                "markers": [
                    "hereby", "hereinafter", "furthermore", "notwithstanding",
                    "pursuant", "shall", "may", "aforementioned", "therein"
                ],
                "patterns": [
                    r"It is hereby",
                    r"In accordance with",
                    r"The aforementioned",
                    r"Pursuant to",
                ],
                "description": "Highly formal legal language with extensive use of archaic terms and structural formality",
            },
            "Formal": {
                "markers": [
                    "therefore", "thus", "accordingly", "considering",
                    "regarding", "subject to", "shall not"
                ],
                "patterns": [
                    r"Please be advised",
                    r"As noted",
                    r"The following",
                    r"In this regard",
                ],
                "description": "Professional and structured language with clear logical flow",
            },
            "Neutral": {
                "markers": [
                    "regarding", "mentioned", "indicated", "noted",
                    "information", "details", "accordingly"
                ],
                "patterns": [
                    r"As indicated",
                    r"Based on",
                    r"The following",
                    r"In summary",
                ],
                "description": "Objective, fact-based language without emotional coloring",
            },
            "Friendly": {
                "markers": [
                    "appreciate", "thank", "glad", "happy", "looking forward",
                    "will", "interested", "hope", "please"
                ],
                "patterns": [
                    r"I appreciate",
                    r"Thank you for",
                    r"Looking forward",
                    r"We hope",
                ],
                "description": "Warm and accessible language that builds rapport",
            },
            "Empathetic": {
                "markers": [
                    "understand", "recognize", "acknowledge", "care",
                    "support", "compassion", "concern", "feel"
                ],
                "patterns": [
                    r"I understand",
                    r"We recognize",
                    r"It's clear that",
                    r"We care about",
                ],
                "description": "Language that demonstrates understanding and emotional connection",
            },
        }

        # Transformation strategies for each tone shift
        self.transformation_strategies = {
            "to_very_formal": {
                "word_replacements": {
                    "will": "shall",
                    "should": "ought to",
                    "seems": "appears",
                    "looks like": "indicates",
                    "using": "pursuant to the use of",
                    "by": "whereby",
                    "because": "inasmuch as",
                },
                "additions": [
                    "Furthermore,",
                    "In addition,",
                    "Moreover,",
                    "Notwithstanding,",
                ],
                "insights": [
                    "Replace present tense with future formal ('will' → 'shall')",
                    "Add legal discourse markers at sentence starts",
                    "Eliminate contractions completely",
                    "Expand abbreviated terms to their full forms",
                    "Use 'herein' and 'thereof' references",
                ],
            },
            "to_formal": {
                "word_replacements": {
                    "I think": "It is my assessment that",
                    "maybe": "it is possible that",
                    "appears to be": "is",
                    "could": "may",
                    "might": "may",
                },
                "additions": [
                    "Accordingly,",
                    "Therefore,",
                    "Regarding this matter,",
                ],
                "insights": [
                    "Remove hedging language (maybe, might, could, perhaps)",
                    "Expand all contractions (don't → do not)",
                    "Use structured, logical connectors",
                    "Maintain professional distance with passive voice where appropriate",
                ],
            },
            "to_neutral": {
                "word_replacements": {
                    "unfortunately": "notably",
                    "unfortunately": "it is significant that",
                    "clearly": "it is evident that",
                },
                "additions": [],
                "insights": [
                    "Remove emotional language and judgments",
                    "Focus on facts and observations",
                    "Use passive voice for objectivity",
                    "Eliminate exclamation points and all caps",
                    "Replace emotional adjectives with neutral descriptors",
                ],
            },
            "to_friendly": {
                "word_replacements": {
                    "shall": "will",
                    "herein": "here",
                    "aforementioned": "mentioned",
                    "utilize": "use",
                    "facilitate": "help",
                    "overlooks": "may not fully consider",
                    "fails to": "did not",
                    "undue weight": "significant weight",
                },
                "additions": [
                    "I appreciate",
                    "Thank you for",
                    "We'd be glad to",
                ],
                "insights": [
                    "Replace formal language with conversational equivalents",
                    "Use 'will' instead of 'shall'",
                    "Soften critical words without removing substance",
                    "Express appreciation where appropriate",
                    "Use first-person language to build connection",
                ],
            },
            "to_empathetic": {
                "word_replacements": {
                    "clearly fails": "did not fully",
                    "obviously incorrect": "may not have considered",
                    "unacceptable": "challenging",
                    "demands": "requests",
                },
                "additions": [
                    "I understand",
                    "We recognize",
                    "It's clear you",
                ],
                "insights": [
                    "Acknowledge the other party's perspective",
                    "Replace judgmental language with understanding",
                    "Use phrases showing emotional awareness",
                    "Add validation of their concerns before correcting",
                    "Show concern for their situation while maintaining position",
                ],
            },
        }

        # Entity extraction patterns
        self.entity_patterns = {
            "recipient_type": [
                (r"(?:to |for )?(?:the )?(client|customer|recipient|you)", "recipient"),
                (r"(?:the )?(court|judge|jury|counsel)", "legal_entity"),
                (r"(?:to |for )?(?:the )?(opposing counsel|defendant|plaintiff)", "party"),
            ],
            "relationship": [
                (r"(?:regarding|concerning|about|re:)\s+(.+?)(?:\.|,|\n)", "subject"),
                (r"(?:in response to|responding to|following up on)\s+(.+?)(?:\.|,|\n)", "context"),
            ],
        }

    def analyze_tone(self, text: str, detected_tone: str = "neutral") -> Dict[str, Any]:
        """Analyze the tone of text and provide detailed insights.

        Args:
            text: Legal correspondence text to analyze
            detected_tone: Current detected tone name

        Returns:
            Dictionary with analysis results:
            - current_tone_analysis: Description of detected tone
            - tone_markers: Words/patterns that signal this tone
            - strengths: What the current tone does well
            - potential_issues: Concerns with the current tone
            - recipient_alignment: How well tone matches likely recipient
            - transformation_difficulty: Ease of transforming to target
        """
        analysis = {
            "current_tone": detected_tone,
            "current_tone_analysis": self._analyze_tone_characteristics(text, detected_tone),
            "tone_markers": self._extract_tone_markers(text, detected_tone),
            "strengths": self._identify_tone_strengths(detected_tone),
            "potential_issues": self._identify_tone_issues(detected_tone, text),
            "recipient_insights": self._analyze_recipient_context(text),
            "overall_assessment": self._assess_overall_message(text),
        }
        return analysis

    def suggest_transformation(self, text: str, from_tone: str, to_tone: str) -> Dict[str, Any]:
        """Suggest how to transform text from one tone to another.

        Args:
            text: Original text
            from_tone: Current tone name
            to_tone: Target tone name

        Returns:
            Dictionary with transformation guidance:
            - strategy: High-level transformation approach
            - key_changes: Most important changes to make
            - word_replacements: Specific word swap suggestions
            - additions: Phrases to add
            - examples: Example transformations of critical phrases
            - difficulty: Estimated effort (easy/moderate/challenging)
        """
        strategy_key = f"to_{to_tone.lower().replace(' ', '_')}"

        if strategy_key not in self.transformation_strategies:
            return {"error": f"No strategy defined for tone: {to_tone}"}

        strategy = self.transformation_strategies[strategy_key]

        # Extract critical sentences from text
        sentences = re.split(r"(?<=[.!?])\s+", text)
        critical_sentences = self._identify_critical_sentences(sentences, from_tone)

        # Generate example transformations
        examples = []
        for sent in critical_sentences[:3]:  # Top 3 examples
            transformed = self._transform_sentence(sent, strategy)
            if transformed != sent:
                examples.append({"original": sent.strip(), "transformed": transformed.strip()})

        return {
            "from_tone": from_tone,
            "to_tone": to_tone,
            "strategy": self._describe_strategy(from_tone, to_tone),
            "key_changes": strategy["insights"],
            "word_replacements": strategy["word_replacements"],
            "additions": strategy["additions"],
            "example_transformations": examples,
            "difficulty": self._estimate_difficulty(from_tone, to_tone),
            "estimated_impact": self._estimate_impact(from_tone, to_tone),
        }

    def analyze_sentence_context(
        self,
        sentence: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Deep analysis of a single sentence in context.

        Args:
            sentence: Individual sentence to analyze
            context: Optional context about the message

        Returns:
            Dictionary with sentence-level analysis
        """
        return {
            "sentence": sentence,
            "tone_indicators": self._extract_tone_markers(sentence, "unknown"),
            "emotional_language": self._identify_emotional_language(sentence),
            "formality_score": self._calculate_formality_score(sentence),
            "clarity_score": self._calculate_clarity_score(sentence),
            "potential_improvements": self._suggest_improvements(sentence),
        }

    # === Internal Analysis Methods ===

    def _analyze_tone_characteristics(self, text: str, tone: str) -> str:
        """Generate description of how text exhibits the tone."""
        if tone not in self.tone_characteristics:
            return f"Tone '{tone}' not in standard tone palette"

        characteristics = self.tone_characteristics[tone]
        marker_count = sum(1 for marker in characteristics["markers"] if marker.lower() in text.lower())
        pattern_count = sum(1 for pattern in characteristics["patterns"] if re.search(pattern, text, re.IGNORECASE))

        evidence_level = "strongly" if marker_count + pattern_count > 5 else "moderately" if marker_count + pattern_count > 2 else "minimally"

        return f"Text {evidence_level} exhibits {tone} tone. {characteristics['description']}"

    def _extract_tone_markers(self, text: str, tone: str) -> List[str]:
        """Extract words/patterns that signal the tone."""
        markers = []

        if tone in self.tone_characteristics:
            tone_markers = self.tone_characteristics[tone]["markers"]
            for marker in tone_markers:
                if marker.lower() in text.lower():
                    markers.append(marker)

        return markers[:10]  # Return top 10

    def _identify_tone_strengths(self, tone: str) -> List[str]:
        """Identify strengths of the current tone."""
        strengths_map = {
            "Very Formal": [
                "Establishes clear professional distance",
                "Conveys authority and legal precision",
                "Minimizes misinterpretation in formal contexts",
            ],
            "Formal": [
                "Maintains professionalism",
                "Clear logical structure",
                "Appropriate for legal contexts",
            ],
            "Neutral": [
                "Objective and fact-based",
                "Minimizes emotional distraction",
                "Focuses on content over tone",
            ],
            "Friendly": [
                "Builds rapport with recipient",
                "Increases willingness to cooperate",
                "Humanizes the correspondence",
            ],
            "Empathetic": [
                "Demonstrates understanding and care",
                "Encourages emotional connection",
                "Softens difficult messages",
            ],
        }
        return strengths_map.get(tone, [])

    def _identify_tone_issues(self, tone: str, text: str) -> List[str]:
        """Identify potential issues with the current tone."""
        issues = []

        if tone == "Very Formal":
            if "I" in text or "we" in text:
                issues.append("Personal pronouns reduce formal distance")
            if "!" in text:
                issues.append("Exclamation marks reduce formality")

        elif tone == "Friendly":
            formal_markers = ["shall", "herein", "aforementioned"]
            if any(marker in text.lower() for marker in formal_markers):
                issues.append("Formal language mixed with friendly tone creates inconsistency")

        elif tone == "Empathetic":
            aggressive_words = ["must", "demand", "unacceptable"]
            if any(word in text.lower() for word in aggressive_words):
                issues.append("Aggressive language conflicts with empathetic tone")

        return issues

    def _analyze_recipient_context(self, text: str) -> Dict[str, str]:
        """Analyze what the text reveals about recipient and relationship."""
        recipient_clues = {
            "recipient_type": "unknown",
            "relationship_quality": "professional",
            "power_dynamics": "unclear",
        }

        # Look for recipient type signals
        if re.search(r"dear client|dear mr|dear ms", text, re.IGNORECASE):
            recipient_clues["recipient_type"] = "formal_addressee"
        elif re.search(r"thank you|i appreciate|we value", text, re.IGNORECASE):
            recipient_clues["relationship_quality"] = "collaborative"
        elif re.search(r"demand|require|must|final notice", text, re.IGNORECASE):
            recipient_clues["power_dynamics"] = "assertive"

        return recipient_clues

    def _assess_overall_message(self, text: str) -> str:
        """Overall assessment of message character."""
        marker_counts: Dict[str, int] = {}

        for assessment_type, patterns in MESSAGE_ASSESSMENT_MARKERS.items():
            count = sum(1 for pattern in patterns if re.search(pattern, text, re.IGNORECASE))
            marker_counts[assessment_type] = count

        if marker_counts:
            dominant: str = max(marker_counts, key=lambda k: marker_counts[k])
            return dominant
        return "Mixed"

    def _identify_emotional_language(self, sentence: str) -> List[str]:
        """Identify emotional words in sentence."""
        emotional = []
        for word in EMPATHY_WORDS + REFLECTION_WORDS:
            if word.lower() in sentence.lower():
                emotional.append(word)
        return emotional

    def _calculate_formality_score(self, sentence: str) -> float:
        """Calculate formality score 0-1."""
        formal_markers = ["shall", "hereby", "aforementioned", "pursuant", "notwithstanding"]
        score = sum(1 for marker in formal_markers if marker in sentence.lower()) / 5
        return min(1.0, score)

    def _calculate_clarity_score(self, sentence: str) -> float:
        """Calculate clarity score 0-1."""
        # Simple heuristics: shorter sentences are clearer
        words = len(sentence.split())
        return 1.0 if words < 20 else 0.7 if words < 40 else 0.4

    def _suggest_improvements(self, sentence: str) -> List[str]:
        """Suggest improvements for the sentence."""
        suggestions = []

        if len(sentence.split()) > 30:
            suggestions.append("Consider breaking into shorter sentences")

        if "very" in sentence.lower():
            suggestions.append("Replace 'very' with more specific adjective")

        if sentence.endswith("!"):
            suggestions.append("Consider period instead of exclamation mark")

        return suggestions

    def _identify_critical_sentences(self, sentences: List[str], tone: str) -> List[str]:
        """Identify sentences most affected by tone."""
        # Sentences with emotional language or strong statements
        critical = []
        for sent in sentences:
            if any(
                marker in sent.lower()
                for markers in MESSAGE_ASSESSMENT_MARKERS.values()
                for marker in markers
            ):
                critical.append(sent)

        return critical[:5]

    def _transform_sentence(self, sentence: str, strategy: Dict[str, Any]) -> str:
        """Apply transformation strategy to sentence."""
        transformed = sentence

        # Apply word replacements
        for original, replacement in strategy["word_replacements"].items():
            pattern = r"\b" + re.escape(original) + r"\b"
            transformed = re.sub(pattern, replacement, transformed, flags=re.IGNORECASE)

        return transformed

    def _describe_strategy(self, from_tone: str, to_tone: str) -> str:
        """Describe the transformation strategy."""
        return f"Transform from {from_tone} to {to_tone} by adjusting formality, emotional language, and structural markers."

    def _estimate_difficulty(self, from_tone: str, to_tone: str) -> str:
        """Estimate difficulty of transformation."""
        # Adjacent tones are easier to transform
        tone_order = ["Very Formal", "Formal", "Neutral", "Friendly", "Empathetic"]

        try:
            from_idx = tone_order.index(from_tone)
            to_idx = tone_order.index(to_tone)
            distance = abs(to_idx - from_idx)

            if distance <= 1:
                return "Easy"
            elif distance == 2:
                return "Moderate"
            else:
                return "Challenging"
        except ValueError:
            return "Unknown"

    def _estimate_impact(self, from_tone: str, to_tone: str) -> str:
        """Estimate impact of transformation on message."""
        impacts = {
            "Very Formal": "Removes professional distance, may reduce authority",
            "Formal": "Adjusts formality level",
            "Neutral": "Adds or removes emotional coloring",
            "Friendly": "Increases or decreases warmth",
            "Empathetic": "Alters emotional connection",
        }
        return impacts.get(to_tone, "Changes message character")


# Factory function
def create_tone_analysis_composer() -> ToneAnalysisComposer:
    """Create a tone analysis composer instance."""
    return ToneAnalysisComposer()
