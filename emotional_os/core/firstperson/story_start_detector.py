"""Story-Start Detection Module for FirstPerson.

Detects ambiguous pronouns and temporal markers that indicate a story beginning
or emotional loop that needs clarification.

Key functions:
- detect_pronoun_ambiguity: Finds unclear pronouns ("they," "it," "this")
- detect_temporal_markers: Finds repetition markers ("again," "always," "never")
- generate_clarifier: Creates a clarifying prompt based on detected ambiguity
- analyze_story_start: Orchestrates detection and returns structured result
"""

import re
from typing import Dict, List, Optional, Tuple


class StoryStartDetector:
    """Detects ambiguous pronouns and temporal markers in user input."""

    # Ambiguous pronouns that often lack clear antecedents
    AMBIGUOUS_PRONOUNS = {
        "they": "Who are you referring to when you say 'they'?",
        "them": "Who are you referring to when you say 'them'?",
        "their": "Whose perspective are you sharing when you say 'their'?",
        "it": "What are you referring to when you say 'it'?",
        "this": "What specifically do you mean by 'this'?",
        "that": "What do you mean by 'that'?",
        "these": "Which people or things are you referring to?",
        "those": "Which people or things are you referring to?",
        "he": "Who specifically are you talking about?",
        "she": "Who specifically are you talking about?",
        "him": "Who specifically are you referring to?",
        "her": "Who specifically are you referring to?",
    }

    # Temporal markers indicating loops or repetition
    TEMPORAL_MARKERS = {
        "again": {
            "marker": "again",
            "type": "repetition",
            "clarifier": "How often does this come up?",
        },
        "always": {
            "marker": "always",
            "type": "frequency",
            "clarifier": "Can you think of a time when this wasn't true?",
        },
        "never": {
            "marker": "never",
            "type": "absolute",
            "clarifier": "Has there ever been an exception?",
        },
        "constantly": {
            "marker": "constantly",
            "type": "frequency",
            "clarifier": "How long has this been happening?",
        },
        "every time": {
            "marker": "every time",
            "type": "frequency",
            "clarifier": "Is there ever a time when this doesn't happen?",
        },
        "every day": {
            "marker": "every day",
            "type": "temporal",
            "clarifier": "What time of day does this usually occur?",
        },
        "every night": {
            "marker": "every night",
            "type": "temporal",
            "clarifier": "Is there a pattern to when this happens?",
        },
        "keeps happening": {
            "marker": "keeps happening",
            "type": "repetition",
            "clarifier": "What do you think keeps triggering this?",
        },
    }

    def __init__(self):
        """Initialize the story-start detector."""
        self.last_detected = None

    def detect_pronoun_ambiguity(self, text: str) -> List[Dict[str, any]]:
        """Detect ambiguous pronouns in the input text.

        Args:
            text: User input to analyze

        Returns:
            List of detected ambiguous pronouns with positions and clarifiers
        """
        lower_text = text.lower()
        findings = []

        for pronoun, clarifier in self.AMBIGUOUS_PRONOUNS.items():
            # Use word boundaries to avoid matching substrings
            pattern = r"\b" + re.escape(pronoun) + r"\b"
            matches = list(re.finditer(pattern, lower_text))

            for match in matches:
                # Get context around the pronoun (20 chars before and after)
                start = max(0, match.start() - 20)
                end = min(len(text), match.end() + 20)
                context = text[start:end]

                findings.append(
                    {
                        "pronoun": pronoun,
                        "position": match.start(),
                        "context": context.strip(),
                        "clarifier": clarifier,
                    }
                )

        return findings

    def detect_temporal_markers(self, text: str) -> List[Dict[str, any]]:
        """Detect temporal markers indicating loops or repetition.

        Args:
            text: User input to analyze

        Returns:
            List of detected temporal markers with positions and clarifiers
        """
        lower_text = text.lower()
        findings = []

        for marker_key, marker_info in self.TEMPORAL_MARKERS.items():
            marker = marker_info["marker"]
            pattern = r"\b" + re.escape(marker) + r"\b"
            matches = list(re.finditer(pattern, lower_text))

            for match in matches:
                # Get context around the marker
                start = max(0, match.start() - 20)
                end = min(len(text), match.end() + 20)
                context = text[start:end]

                findings.append(
                    {
                        "marker": marker,
                        "type": marker_info["type"],
                        "position": match.start(),
                        "context": context.strip(),
                        "clarifier": marker_info["clarifier"],
                    }
                )

        return findings

    def analyze_story_start(
        self, text: str, max_clarifiers: int = 2
    ) -> Dict[str, any]:
        """Analyze text for story-start signals (ambiguity + temporal markers).

        Args:
            text: User input to analyze
            max_clarifiers: Maximum number of clarifiers to return (prevent overwhelm)

        Returns:
            Dictionary with detected signals and recommended clarifiers
        """
        pronouns = self.detect_pronoun_ambiguity(text)
        temporal = self.detect_temporal_markers(text)

        # Combine and prioritize by position
        all_findings = []
        all_findings.extend([{**p, "category": "pronoun"} for p in pronouns])
        all_findings.extend([{**t, "category": "temporal"} for t in temporal])

        # Sort by position in text (earliest first)
        all_findings.sort(key=lambda x: x["position"])

        # Select top clarifiers (mix of pronouns and temporal)
        selected = []
        seen_types = set()

        for finding in all_findings:
            if len(selected) >= max_clarifiers:
                break

            # Avoid redundant clarifiers
            finding_type = f"{finding['category']}_{finding.get('pronoun') or finding.get('marker')}"
            if finding_type not in seen_types:
                selected.append(finding)
                seen_types.add(finding_type)

        # Generate clarifiers
        clarifiers = [f["clarifier"] for f in selected]

        result = {
            "has_ambiguity": len(pronouns) > 0,
            "has_temporal_loop": len(temporal) > 0,
            "is_story_start": len(pronouns) > 0 or len(temporal) > 0,
            "pronouns_detected": pronouns,
            "temporal_detected": temporal,
            "recommended_clarifiers": clarifiers,
            "clarifier_count": len(clarifiers),
            "raw_findings": all_findings,
        }

        self.last_detected = result
        return result

    def generate_clarifying_prompt(
        self, analysis: Dict[str, any], include_count: int = 2
    ) -> Optional[str]:
        """Generate a natural clarifying prompt from analysis results.

        Args:
            analysis: Result from analyze_story_start()
            include_count: Number of clarifiers to include in the prompt

        Returns:
            Natural language clarifying prompt, or None if no clarification needed
        """
        if not analysis["is_story_start"]:
            return None

        clarifiers = analysis["recommended_clarifiers"][:include_count]

        if not clarifiers:
            return None

        # Build a natural prompt
        if len(clarifiers) == 1:
            prompt = f"{clarifiers[0]}"
        else:
            # Combine multiple clarifiers naturally
            prompt = " ".join(clarifiers)

        return prompt


# Singleton instance for module-level use
_detector = StoryStartDetector()


def analyze_story_start(text: str, max_clarifiers: int = 2) -> Dict[str, any]:
    """Module-level function to analyze story-start signals.

    Args:
        text: User input to analyze
        max_clarifiers: Maximum number of clarifiers to return

    Returns:
        Dictionary with detected signals and recommended clarifiers
    """
    return _detector.analyze_story_start(text, max_clarifiers)


def generate_clarifying_prompt(
    text: str, include_count: int = 2
) -> Optional[str]:
    """Module-level function to generate clarifying prompt.

    Args:
        text: User input to analyze
        include_count: Number of clarifiers to include

    Returns:
        Natural language clarifying prompt or None
    """
    analysis = _detector.analyze_story_start(text)
    return _detector.generate_clarifying_prompt(analysis, include_count)
