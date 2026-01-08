"""
Lightweight Tone Signal Parser for LiToneCheck

A simplified signal detection system focused on legal correspondence tone analysis.
Unlike the full signal_parser.py from emotional_os, this module:
- Detects tone signals without requiring glyphs.db
- Maps text patterns to emotional signals (α-Ω)
- Evaluates tone characteristics without full gate system
- Provides lightweight signal scoring for rapid analysis

Signals (7 core dimensions):
- α: Formality/Professional (formal, authoritative language)
- β: Boundary/Protective (protective, guarding interests language)
- γ: Longing/Understanding (seeking understanding, empathy language)
- θ: Concern/Cautionary (concern, caution, warning language)
- λ: Confidence/Assertiveness (confident, assertive language)
- ε: Clarity/Reasoning (clear reasoning, logical language)
- Ω: Recognition/Acknowledgment (recognizing perspective language)
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SignalScore:
    """Score for a single signal dimension."""
    signal: str  # α, β, γ, θ, λ, ε, or Ω
    signal_name: str  # Human-readable name
    score: float  # 0-1 strength
    markers: List[str]  # Words/patterns that triggered detection
    intensity: str  # "strong", "moderate", "weak"


@dataclass
class SignalAnalysis:
    """Complete signal analysis of text."""
    primary_signal: str  # Signal with highest score
    primary_signal_name: str  # Human-readable name
    scores: Dict[str, float]  # All signal scores
    all_signals: List[SignalScore]  # Detailed signal analysis
    detected_markers: Dict[str, List[str]]  # Markers by signal
    tone_profile: str  # Overall tone classification
    confidence: float  # 0-1 confidence in analysis


class ToneSignalParser:
    """Lightweight tone signal parser for legal correspondence."""

    # Signal definitions
    SIGNALS = {
        "α": "Formality/Professional",
        "β": "Boundary/Protective",
        "γ": "Longing/Understanding",
        "θ": "Concern/Cautionary",
        "λ": "Confidence/Assertiveness",
        "ε": "Clarity/Reasoning",
        "Ω": "Recognition/Acknowledgment",
    }

    # Signal pattern libraries (legal/correspondence focused)
    SIGNAL_PATTERNS = {
        "α": {  # Formality/Professional
            "strong": [
                r"\bharein\b", r"\bhereinafter\b", r"\bhereof\b", r"\btherein\b",
                r"\bthereof\b", r"\baforesaid\b", r"\baforementioned\b",
                r"pursuant to", r"in accordance with", r"notwithstanding",
                r"\bshall\b", r"\bmay\b", r"\bmust\b", r"with respect to",
                r"the following", r"accordingly", r"therefore", r"thus"
            ],
            "moderate": [
                r"formal", r"professional", r"official", r"certificate",
                r"agreement", r"contract", r"clause", r"provision",
                r"respecting", r"regarding", r"concerning"
            ],
            "weak": [
                r"please", r"kindly", r"thank you", r"sincerely"
            ]
        },
        "β": {  # Boundary/Protective
            "strong": [
                r"\bprotect\b", r"\bguard\b", r"\bboundary\b", r"\bshield\b",
                r"\bpreserve\b", r"\bdefend\b", r"\bmaintain\b", r"\breserve\b",
                r"\bsafeguard\b", r"\bensure\b", r"\brequired\b",
                r"\bmust\b", r"\brequires\b", r"\bdo not\b", r"\bcannot\b",
                r"do not allow", r"may not"
            ],
            "moderate": [
                r"careful", r"caution", r"terms", r"conditions",
                r"restrictions", r"limitations", r"requirements"
            ],
            "weak": [
                r"avoid", r"be careful", r"remember"
            ]
        },
        "γ": {  # Longing/Understanding (Empathy/Seeking understanding)
            "strong": [
                r"\bunderstand\b", r"\bappreciate\b", r"\brecognize\b",
                r"\backnowledge\b", r"\bsee\b", r"\bhear\b", r"\bwitness\b",
                r"\bempathy\b", r"\bcompassion\b", r"\bcare\b", r"\bsupport\b",
                r"I understand", r"we recognize", r"it's clear you"
            ],
            "moderate": [
                r"consider", r"perspective", r"viewpoint", r"concern",
                r"aware", r"sensitive", r"respect"
            ],
            "weak": [
                r"think", r"believe", r"feel", r"seem"
            ]
        },
        "θ": {  # Concern/Cautionary
            "strong": [
                r"\bconcern\b", r"\bcaution\b", r"\bwarning\b", r"\balert\b",
                r"\bbeware\b", r"\brisk\b", r"\bdanger\b", r"\bproblem\b",
                r"\bchallenging\b", r"\bdifficult\b", r"\bcritical\b",
                r"be aware", r"must note", r"should consider"
            ],
            "moderate": [
                r"issue", r"matter", r"situation", r"attention",
                r"note", r"important", r"significant"
            ],
            "weak": [
                r"question", r"possibly", r"may"
            ]
        },
        "λ": {  # Confidence/Assertiveness
            "strong": [
                r"\bconfident\b", r"\bcertain\b", r"\bclear\b", r"\bdecisive\b",
                r"\bassertion\b", r"\binsist\b", r"\bdemand\b", r"\brequire\b",
                r"\bwill\b", r"\bmust\b", r"\bshall\b", r"\bdefinitely\b",
                r"\babsolutely\b", r"\bcertainly\b"
            ],
            "moderate": [
                r"confident", r"believe", r"convinced", r"evident",
                r"clear", r"obvious", r"surely"
            ],
            "weak": [
                r"think", r"seem", r"appear"
            ]
        },
        "ε": {  # Clarity/Reasoning
            "strong": [
                r"therefore", r"\bthus\b", r"\bhence\b", r"\bconsequently\b",
                r"as a result", r"\bbecause\b", r"\bsince\b", r"\breason\b",
                r"\blogic\b", r"\bevidence\b", r"\bproof\b", r"\bdemonstrate\b",
                r"clearly shows", r"indicates"
            ],
            "moderate": [
                r"reason", r"example", r"analysis", r"review",
                r"detail", r"explain", r"clarify"
            ],
            "weak": [
                r"suggests", r"appears", r"seems"
            ]
        },
        "Ω": {  # Recognition/Acknowledgment
            "strong": [
                r"\brecognize\b", r"\backnowledge\b", r"\bsee\b", r"\bhear\b",
                r"\bwitness\b", r"\bvalidate\b", r"\brecognition\b",
                r"we see you", r"your voice", r"your perspective",
                r"your concerns"
            ],
            "moderate": [
                r"aware", r"note", r"mention", r"point",
                r"statement", r"expressed", r"shared"
            ],
            "weak": [
                r"understand", r"know", r"recognize"
            ]
        }
    }

    def __init__(self):
        """Initialize the tone signal parser."""
        logger.info("✅ Tone Signal Parser initialized")

    def analyze_text(self, text: str) -> SignalAnalysis:
        """Analyze text for tone signals.

        Args:
            text: Legal correspondence text to analyze

        Returns:
            SignalAnalysis with detailed signal breakdown
        """
        text_lower = text.lower()

        # Calculate scores for each signal
        scores: Dict[str, float] = {}
        all_signals: List[SignalScore] = []
        detected_markers: Dict[str, List[str]] = {}

        for signal, name in self.SIGNALS.items():
            score, markers = self._calculate_signal_score(signal, text_lower)
            scores[signal] = score
            detected_markers[signal] = markers

            # Determine intensity
            if score > 0.6:
                intensity = "strong"
            elif score > 0.3:
                intensity = "moderate"
            else:
                intensity = "weak"

            signal_score = SignalScore(
                signal=signal,
                signal_name=name,
                score=score,
                markers=markers,
                intensity=intensity,
            )
            all_signals.append(signal_score)

        # Determine primary signal
        primary = max(all_signals, key=lambda x: x.score)

        # Determine tone profile based on top signals
        tone_profile = self._determine_tone_profile(all_signals)

        # Calculate overall confidence
        confidence = (primary.score + sum(s.score for s in all_signals) / len(all_signals)) / 2

        return SignalAnalysis(
            primary_signal=primary.signal,
            primary_signal_name=primary.signal_name,
            scores=scores,
            all_signals=all_signals,
            detected_markers=detected_markers,
            tone_profile=tone_profile,
            confidence=min(1.0, confidence),
        )

    def analyze_sentence(self, sentence: str) -> SignalScore:
        """Analyze a single sentence for primary signal.

        Args:
            sentence: Single sentence to analyze

        Returns:
            Primary SignalScore for that sentence
        """
        analysis = self.analyze_text(sentence)
        return max(analysis.all_signals, key=lambda x: x.score)

    def detect_signal_markers(self, text: str, signal: str) -> List[str]:
        """Get all markers detected for a specific signal.

        Args:
            text: Text to search
            signal: Signal code (α-Ω)

        Returns:
            List of detected markers
        """
        if signal not in self.SIGNALS:
            return []

        text_lower = text.lower()
        markers = []

        for strength_level in ["strong", "moderate", "weak"]:
            patterns = self.SIGNAL_PATTERNS[signal].get(strength_level, [])
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    matches = re.findall(pattern, text_lower)
                    markers.extend(matches)

        return list(set(markers))  # Remove duplicates

    def get_signal_combinations(self, analysis: SignalAnalysis) -> List[Tuple[str, float]]:
        """Get top signal combinations for tone profile.

        Args:
            analysis: SignalAnalysis result

        Returns:
            List of (signal_code + signal_code, combined_score) tuples
        """
        signals_sorted = sorted(analysis.all_signals, key=lambda x: x.score, reverse=True)
        top_two = signals_sorted[:2]

        if len(top_two) == 2:
            combo = top_two[0].signal + top_two[1].signal
            combined_score = (top_two[0].score + top_two[1].score) / 2
            return [(combo, combined_score)]
        elif len(top_two) == 1:
            return [(top_two[0].signal, top_two[0].score)]
        return []

    # === Internal Methods ===

    def _calculate_signal_score(self, signal: str, text: str) -> Tuple[float, List[str]]:
        """Calculate signal score for given text.

        Returns:
            (score, markers) tuple
        """
        if signal not in self.SIGNAL_PATTERNS:
            return 0.0, []

        detected_markers = []
        score = 0.0

        # Check strong patterns (weighted 1.0)
        for pattern in self.SIGNAL_PATTERNS[signal].get("strong", []):
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            if matches > 0:
                score += matches * 0.4  # Strong patterns contribute heavily
                detected_markers.extend(re.findall(pattern, text, re.IGNORECASE))

        # Check moderate patterns (weighted 0.6)
        for pattern in self.SIGNAL_PATTERNS[signal].get("moderate", []):
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            if matches > 0:
                score += matches * 0.2  # Moderate patterns contribute less
                detected_markers.extend(re.findall(pattern, text, re.IGNORECASE))

        # Check weak patterns (weighted 0.3)
        for pattern in self.SIGNAL_PATTERNS[signal].get("weak", []):
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            if matches > 0:
                score += matches * 0.1  # Weak patterns contribute minimally
                detected_markers.extend(re.findall(pattern, text, re.IGNORECASE))

        # Normalize score to 0-1 range
        score = min(1.0, score / 5)  # Normalize assuming 5 strong matches is max

        return score, list(set(detected_markers))[:10]  # Top 10 unique markers

    def _determine_tone_profile(self, signals: List[SignalScore]) -> str:
        """Determine overall tone profile from signal scores.

        Returns:
            Tone profile name
        """
        # Sort by score
        sorted_signals = sorted(signals, key=lambda x: x.score, reverse=True)

        if len(sorted_signals) == 0:
            return "Neutral"

        top_signal = sorted_signals[0]

        # Define tone profiles based on dominant signals
        profiles = {
            "α": "Very Formal",
            "β": "Professional/Protective",
            "γ": "Empathetic/Understanding",
            "θ": "Cautious/Concerned",
            "λ": "Confident/Assertive",
            "ε": "Clear/Reasoned",
            "Ω": "Acknowledging/Validating",
        }

        return profiles.get(top_signal.signal, "Neutral")


# Factory function
def create_tone_signal_parser() -> ToneSignalParser:
    """Create a tone signal parser instance."""
    return ToneSignalParser()
