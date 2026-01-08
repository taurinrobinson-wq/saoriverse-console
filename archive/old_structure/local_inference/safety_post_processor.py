"""Gate Enforcement and Post-Processing for LLM Output.

Applies glyph-based constraints to LLM output to ensure adherence to:
- Safety policies (no uncanny when gate is off)
- Rhythm/metaphor targets
- Register consistency
- Recognition risk prevention
"""

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Optional
import re
import logging

from glyph_lm_control import GatePolicy, StyleDirective, Glyph, GLYPH_REGISTRY


logger = logging.getLogger(__name__)


@dataclass
class PostProcessResult:
    """Result of post-processing LLM output."""
    original_text: str
    processed_text: str
    modifications_made: List[str]  # List of applied fixes
    safety_violations_fixed: int
    violations_detected: List[str]


class RecognitionRiskDetector:
    """Detects and prevents "I remember you" / "I know you" phrases."""

    # Patterns that trigger recognition risk
    RECOGNITION_PATTERNS = [
        r"i\s+(?:remember|recall|know|recognize|met|saw|remember\s+you|know\s+you)",
        r"(?:we|i)\s+(?:met|spoke|talked|met\s+before|met\s+(?:earlier|before))",
        r"i\s+\w*\s*(?:recognize|recognize\s+you|remember\s+you|know\s+you)",
        r"(?:your|you)\s+(?:face|voice|presence|name)",
        r"we\s+(?:know\s+each\s+other|have\s+(?:met|spoken|talked))",
        r"(?:this|that)\s+(?:feeling|place|time)\s+(?:is\s+familiar|feels\s+familiar)",
        r"(?:we|i)\s+(?:have\s+)?(?:been|met)\s+(?:here|before)",
    ]

    # Safe alternatives to suggest
    SAFE_ALTERNATIVES = {
        "recognition": [
            "This feeling has a pattern to it.",
            "There's something familiar in the shape of this.",
            "The echo of something you've felt before.",
            "A resonance with something in your experience.",
        ],
        "knowing": [
            "I can sense...",
            "There's something here that speaks to...",
            "The shape of your experience suggests...",
            "I notice a pattern in what you're describing.",
        ],
        "memory": [
            "This resonates with something deep.",
            "There's a throughline to your story.",
            "Something in this echoes through your experience.",
            "A thread that connects through your past.",
        ],
    }

    @classmethod
    def detect(cls, text: str) -> List[Tuple[str, str]]:
        """Detect recognition-risk phrases.

        Args:
            text: Text to check

        Returns:
            List of (matched_phrase, pattern_type) tuples
        """
        matches = []
        text_lower = text.lower()

        for pattern in cls.RECOGNITION_PATTERNS:
            found = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in found:
                matches.append((match.group(0), "recognition"))

        return matches

    @classmethod
    def remove_risk_phrases(cls, text: str) -> Tuple[str, List[str]]:
        """Remove recognition-risk phrases from text.

        Args:
            text: Text to process

        Returns:
            (cleaned_text, list_of_removed_phrases)
        """
        removed = []
        processed = text

        for pattern in cls.RECOGNITION_PATTERNS:
            matches = list(re.finditer(pattern, processed, re.IGNORECASE))
            # Process matches in reverse order to maintain indices
            for match in reversed(matches):
                phrase = match.group(0)
                removed.append(phrase)
                processed = processed[:match.start()] + processed[match.end():]

        return processed, removed


class UncannynessEnforcer:
    """Enforces uncanny_ok gate by penalizing or removing uncanny content."""

    UNCANNY_PHRASES = [
        "dissolving",
        "boundary dissolves",
        "edge softens",
        "blur",
        "continuous",
        "merge",
        "fold into",
        "become one",
    ]

    @classmethod
    def flag_uncanny_content(cls, text: str) -> List[Tuple[int, int, str]]:
        """Find uncanny phrases in text.

        Returns:
            List of (start, end, phrase) tuples
        """
        flagged = []
        text_lower = text.lower()

        for phrase in cls.UNCANNY_PHRASES:
            for match in re.finditer(rf"\b{re.escape(phrase)}\b", text_lower):
                flagged.append((match.start(), match.end(), phrase))

        return flagged

    @classmethod
    def remove_uncanny_content(cls, text: str) -> Tuple[str, int]:
        """Remove uncanny phrases when uncanny_ok=False.

        Returns:
            (cleaned_text, count_removed)
        """
        flagged = cls.flag_uncanny_content(text)
        count = len(flagged)

        # Remove in reverse order to preserve indices
        processed = text
        for start, end, _ in reversed(flagged):
            processed = processed[:start] + processed[end:]

        return processed, count


class RhythmEnforcer:
    """Enforces rhythm targets (sentence length, pacing)."""

    @staticmethod
    def analyze_rhythm(text: str) -> Dict[str, any]:
        """Analyze current rhythm of text.

        Returns:
            Dict with metrics: avg_length, short_count, medium_count, long_count, variety
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return {"avg_length": 0, "variety": 0}

        lengths = [len(s.split()) for s in sentences]

        short = sum(1 for l in lengths if l < 10)
        medium = sum(1 for l in lengths if 10 <= l <= 20)
        long = sum(1 for l in lengths if l > 20)

        return {
            "avg_length": sum(lengths) / len(lengths),
            "short_count": short,
            "medium_count": medium,
            "long_count": long,
            "variety": len(set(lengths)) / len(sentences) if sentences else 0,
        }

    @staticmethod
    def suggest_rhythm_improvements(
        text: str,
        target_rhythm: str,
    ) -> List[str]:
        """Suggest rhythm adjustments.

        Args:
            text: Current text
            target_rhythm: "quick", "mixed", "slow", "contemplative"

        Returns:
            List of suggestions
        """
        metrics = RhythmEnforcer.analyze_rhythm(text)
        suggestions = []

        if target_rhythm == "quick":
            if metrics["avg_length"] > 15:
                suggestions.append(
                    "Break longer sentences into shorter ones for quicker pace.")

        elif target_rhythm == "slow":
            if metrics["avg_length"] < 12:
                suggestions.append(
                    "Combine shorter sentences for a more contemplative pace.")

        elif target_rhythm == "mixed":
            if metrics["variety"] < 0.5:
                suggestions.append(
                    "Vary sentence lengths more for natural flow.")

        return suggestions


class MetaphorDensityMeter:
    """Tracks and enforces metaphor density targets."""

    # Common metaphorical markers
    METAPHOR_INDICATORS = [
        r"\bis\b",  # "is" in metaphorical context
        r"\blike\b",
        r"\bas\b.*\bas\b",
        r"\bfold",
        r"\bflow",
        r"\becho",
        r"\bresonance",
        r"\bthread",
        r"\blight",
        r"\bshadow",
        r"\bground",
        r"\bbound",
    ]

    @classmethod
    def measure_density(cls, text: str) -> float:
        """Estimate metaphor density 0.0-1.0.

        Heuristic: ratio of metaphorical words to total words.
        """
        words = text.split()
        if not words:
            return 0.0

        metaphor_count = 0
        for pattern in cls.METAPHOR_INDICATORS:
            metaphor_count += len(re.findall(pattern, text.lower()))

        return min(1.0, metaphor_count / len(words))

    @classmethod
    def adjust_for_target_density(
        cls,
        text: str,
        target_density: float,
    ) -> str:
        """Adjust text to hit target metaphor density.

        Simple heuristic: add or remove metaphorical phrases.
        """
        current = cls.measure_density(text)

        if current < target_density * 0.8:
            # Add more metaphorical language
            enhancements = [
                " Like water finding its path, ",
                " The ground of this is ",
                " What echoes here is ",
            ]
            # Simple insertion (more sophisticated approach needed for production)
            text = text.replace(" . ", enhancements[0] + ". ")

        elif current > target_density * 1.2:
            # Reduce metaphorical language
            for pattern in cls.METAPHOR_INDICATORS:
                text = re.sub(pattern, "", text, count=1, flags=re.IGNORECASE)

        return text


class SafetyPostProcessor:
    """Comprehensive post-processing to enforce safety policies."""

    def __init__(self, gates: GatePolicy, style: StyleDirective):
        """Initialize processor with policies.

        Args:
            gates: Gate policy to enforce
            style: Style directives to enforce
        """
        self.gates = gates
        self.style = style

    def process(self, text: str) -> PostProcessResult:
        """Apply all safety/style constraints to LLM output.

        Args:
            text: Raw LLM output

        Returns:
            PostProcessResult with processed text and modifications
        """
        processed = text
        modifications = []
        violations_fixed = 0
        violations_detected = []

        # 1. Check for recognition risk
        risk_phrases = RecognitionRiskDetector.detect(processed)
        if risk_phrases:
            violations_detected.append(
                f"Recognition risk detected: {len(risk_phrases)} phrases")
            processed, removed = RecognitionRiskDetector.remove_risk_phrases(
                processed)
            if removed:
                modifications.append(
                    f"Removed {len(removed)} recognition-risk phrases")
                violations_fixed += len(removed)

        # 2. Enforce uncanny gate
        if not self.gates.uncanny_ok:
            uncanny_phrases = UncannynessEnforcer.flag_uncanny_content(
                processed)
            if uncanny_phrases:
                violations_detected.append(
                    f"Uncanny content found (gate=False): {len(uncanny_phrases)} phrases")
                processed, removed_count = UncannynessEnforcer.remove_uncanny_content(
                    processed)
                if removed_count > 0:
                    modifications.append(
                        f"Removed {removed_count} uncanny phrases")
                    violations_fixed += removed_count

        # 3. Check rhythm
        rhythm_issues = RhythmEnforcer.suggest_rhythm_improvements(
            processed, self.style.rhythm)
        if rhythm_issues:
            violations_detected.extend(rhythm_issues)

        # 4. Check metaphor density
        actual_density = MetaphorDensityMeter.measure_density(processed)
        target_density = self.style.metaphor_density

        if abs(actual_density - target_density) > 0.2:
            violations_detected.append(
                f"Metaphor density {actual_density:.2f} vs target {target_density:.2f}"
            )
            processed = MetaphorDensityMeter.adjust_for_target_density(
                processed, target_density)
            modifications.append("Adjusted metaphor density")

        # 5. Ensure non-empty output
        if not processed.strip():
            processed = text  # Fall back to original if over-processed
            violations_detected.append(
                "Over-processing removed all content; using original")

        return PostProcessResult(
            original_text=text,
            processed_text=processed,
            modifications_made=modifications,
            safety_violations_fixed=violations_fixed,
            violations_detected=violations_detected,
        )


def create_safe_response(
    base_response: str,
    glyphs: List[Glyph],
    gates: GatePolicy,
    style: StyleDirective,
) -> Tuple[str, PostProcessResult]:
    """Generate safe response by post-processing LLM output.

    Args:
        base_response: Raw response from LLM
        glyphs: List of glyphs used in generation
        gates: Gate policy
        style: Style directive

    Returns:
        (safe_response, post_process_result)
    """
    processor = SafetyPostProcessor(gates, style)
    result = processor.process(base_response)

    logger.info(
        f"Post-processing: {len(result.modifications_made)} modifications, "
        f"{result.safety_violations_fixed} violations fixed"
    )

    return result.processed_text, result
