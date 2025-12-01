"""
Enhanced Emotion Processing with NLP Integration
Combines NRC Lexicon, TextBlob, and spaCy for sophisticated emotion-gate routing.
"""

import logging
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

# Import NLP libraries individually so a missing optional dependency
# (e.g., TextBlob) does not disable the rest of the processor.
NLP_AVAILABLE = False
NRC_AVAILABLE = False
TEXTBLOB_AVAILABLE = False
SPACY_AVAILABLE = False
# Module-level optional references (annotated as Any to satisfy mypy)
nrc: Any = None
TextBlobCls: Any = None
nlp: Any = None
try:
    from parser.nrc_lexicon_loader import nrc as _nrc

    nrc = _nrc
    NRC_AVAILABLE = True
except Exception as e:
    logging.debug(f"NRC loader not available: {e}")

try:
    from textblob import TextBlob as _TextBlob

    TextBlobCls = _TextBlob
    TEXTBLOB_AVAILABLE = True
except Exception as e:
    logging.warning(f"TextBlob not available: {e}")

try:
    import spacy

    try:
        nlp = spacy.load("en_core_web_sm")
        SPACY_AVAILABLE = True
    except Exception as e:
        logging.warning(f"spaCy model 'en_core_web_sm' not available: {e}")
        SPACY_AVAILABLE = False
except Exception as e:
    logging.warning(f"spaCy not available: {e}")

# If any of the components are present we consider enhanced NLP available.
NLP_AVAILABLE = NRC_AVAILABLE or TEXTBLOB_AVAILABLE or SPACY_AVAILABLE

logger = logging.getLogger(__name__)


class EnhancedEmotionProcessor:
    """Enhanced emotion processing using multiple NLP sources for better gate routing."""

    def __init__(self):
        # Emotion-to-gate mappings based on ECM system
        self.emotion_gate_mappings = {
            # Primary emotional gates
            "sadness": ["Gate 4", "Gate 10"],  # Grief/Loss gates
            "grief": ["Gate 4", "Gate 10"],
            "fear": ["Gate 4", "Gate 2"],  # Fear/Anxiety gates
            "anger": ["Gate 5", "Gate 4"],  # Anger/Frustration gates
            "joy": ["Gate 5", "Gate 6"],  # Joy/Creativity gates
            "trust": ["Gate 2", "Gate 4"],  # Trust/Boundary gates
            "anticipation": ["Gate 6", "Gate 5"],  # Insight/Creativity
            "surprise": ["Gate 6", "Gate 9"],  # Insight/Awareness
            "disgust": ["Gate 2", "Gate 5"],  # Boundary/Rejection
            "positive": ["Gate 5", "Gate 6"],  # General positive
            "negative": ["Gate 4", "Gate 10"],  # General negative
        }

        # Signal mappings for compatibility with existing system
        self.emotion_signal_mappings = {
            "sadness": ("θ", "medium", "grief"),
            "grief": ("θ", "high", "grief"),
            "fear": ("θ", "high", "grief"),
            "anger": ("γ", "high", "longing"),
            "joy": ("λ", "high", "joy"),
            "trust": ("β", "medium", "containment"),
            "anticipation": ("ε", "medium", "insight"),
            "surprise": ("ε", "medium", "insight"),
            "disgust": ("β", "high", "containment"),
            "positive": ("λ", "medium", "joy"),
            "negative": ("θ", "medium", "grief"),
        }

        # Polarity-based gate routing for TextBlob integration
        self.polarity_gate_mappings = {
            # Strong negative → Grief/Loss
            "very_negative": ["Gate 4", "Gate 10"],
            "negative": ["Gate 4", "Gate 2"],  # Negative → Grief/Fear
            # Neutral → Awareness/Insight
            "neutral": ["Gate 9", "Gate 6"],
            # Positive → Joy/Creativity
            "positive": ["Gate 5", "Gate 6"],
            # Strong positive → Joy/Creativity
            "very_positive": ["Gate 5", "Gate 6"],
        }

    def analyze_emotion_comprehensive(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive emotion analysis using multiple NLP sources.

        Returns dict with:
        - nrc_emotions: NRC lexicon analysis
        - textblob_sentiment: polarity and subjectivity
        - spacy_entities: named entities (for context)
        - spacy_syntax: syntactic elements (nouns, verbs, adjectives)
        - dominant_emotion: primary detected emotion
        - confidence: confidence score
        - recommended_gates: suggested ECM gates
        """
        if not NLP_AVAILABLE:
            return self._fallback_analysis(text)

        result: Dict[str, Any] = {
            "nrc_emotions": {},
            "textblob_sentiment": {"polarity": 0.0, "subjectivity": 0.0},
            "spacy_entities": [],
            "spacy_syntax": {"nouns": [], "verbs": [], "adjectives": []},
            "dominant_emotion": "neutral",
            "confidence": 0.0,
            "recommended_gates": ["Gate 9"],  # Default to awareness
            "enhanced_signals": [],
        }

        # 1. NRC Lexicon Analysis
        if nrc and nrc.loaded:
            result["nrc_emotions"] = nrc.analyze_text(text)

        # 2. TextBlob Sentiment Analysis (optional)
        if TEXTBLOB_AVAILABLE and TextBlobCls is not None:
            try:
                blob = TextBlobCls(text)
                result["textblob_sentiment"] = {
                    "polarity": blob.sentiment.polarity,
                    "subjectivity": blob.sentiment.subjectivity,
                }
            except Exception as e:
                logging.debug(f"TextBlob processing failed: {e}")

        # 3. spaCy Analysis (Entities + Syntax) — optional
        if SPACY_AVAILABLE and nlp is not None:
            try:
                doc = nlp(text)
                result["spacy_entities"] = [
                    (ent.text, ent.label_) for ent in doc.ents]
                # Extract syntactic elements for glyph matching boost
                result["spacy_syntax"] = self._extract_syntactic_elements(doc)
            except Exception as e:
                logging.debug(f"spaCy processing failed: {e}")

        # 4. Determine dominant emotion and gates
        dominant_emotion, confidence, gates = self._determine_dominant_emotion(
            result["nrc_emotions"], result["textblob_sentiment"]
        )

        result["dominant_emotion"] = dominant_emotion
        result["confidence"] = confidence
        result["recommended_gates"] = gates

        # 5. Generate enhanced signals for compatibility
        result["enhanced_signals"] = self._generate_enhanced_signals(
            dominant_emotion, confidence, text)

        return result

    def _determine_dominant_emotion(self, nrc_emotions: Dict, textblob_sentiment: Dict) -> Tuple[str, float, List[str]]:
        """
        Determine dominant emotion from multiple sources with confidence scoring.
        """
        # Weight NRC emotions by frequency
        nrc_weighted = {}
        total_nrc_words = sum(nrc_emotions.values())
        if total_nrc_words > 0:
            for emotion, count in nrc_emotions.items():
                nrc_weighted[emotion] = count / total_nrc_words

        # Convert TextBlob polarity to emotion categories
        polarity = textblob_sentiment["polarity"]
        subjectivity = textblob_sentiment["subjectivity"]

        if polarity > 0.3:
            polarity_emotion = "positive"
            polarity_confidence = min(abs(polarity), 1.0)
        elif polarity < -0.3:
            polarity_emotion = "negative"
            polarity_confidence = min(abs(polarity), 1.0)
        else:
            polarity_emotion = "neutral"
            polarity_confidence = 0.5

        # Combine NRC and TextBlob for final decision
        if nrc_weighted and max(nrc_weighted.values()) > 0.3:  # Strong NRC signal
            dominant_nrc = max(nrc_weighted.items(), key=lambda x: x[1])
            dominant_emotion = dominant_nrc[0]
            # Slightly reduce confidence for combination
            confidence = dominant_nrc[1] * 0.8
        elif polarity_confidence > 0.6:  # Strong polarity signal
            dominant_emotion = polarity_emotion
            confidence = polarity_confidence * 0.7
        else:
            dominant_emotion = "neutral"
            confidence = 0.3

        # Get recommended gates
        gates = self.emotion_gate_mappings.get(dominant_emotion, ["Gate 9"])

        return dominant_emotion, confidence, gates

    def _extract_syntactic_elements(self, doc: Any) -> Dict[str, List[str]]:
        """
        Extract syntactic elements (nouns, verbs, adjectives) for glyph matching boost.
        Focuses on emotional and meaningful terms.
        """
        syntactic_elements = {"nouns": [], "verbs": [], "adjectives": []}

        # Emotional word lists for filtering
        emotional_verbs = {
            "feel",
            "feeling",
            "felt",
            "experience",
            "experiencing",
            "overwhelm",
            "overwhelmed",
            "anxious",
            "worry",
            "worrying",
            "worried",
            "fear",
            "fearing",
            "afraid",
            "scared",
            "sad",
            "sadden",
            "saddening",
            "grieve",
            "grieving",
            "grieved",
            "mourn",
            "mourning",
            "angry",
            "anger",
            "angering",
            "frustrate",
            "frustrating",
            "frustrated",
            "rage",
            "raging",
            "happy",
            "joy",
            "joyful",
            "delight",
            "delighting",
            "delighted",
            "excited",
            "excite",
            "love",
            "loving",
            "loved",
            "hate",
            "hating",
            "hated",
            "disgust",
            "disgusting",
            "shame",
            "shaming",
            "ashamed",
            "guilt",
            "guilty",
            "guilting",
            "proud",
            "pride",
            "hope",
            "hoping",
            "hopeful",
            "despair",
            "despairing",
            "desperate",
            "trust",
            "trusting",
            "doubt",
            "doubting",
            "confuse",
            "confusing",
            "confused",
            "clarity",
            "clear",
            "clearing",
        }

        emotional_adjectives = {
            "overwhelmed",
            "overwhelming",
            "anxious",
            "nervous",
            "worried",
            "fearful",
            "afraid",
            "scared",
            "terrified",
            "sad",
            "sorrowful",
            "grieving",
            "mournful",
            "angry",
            "furious",
            "frustrated",
            "irritated",
            "rageful",
            "happy",
            "joyful",
            "delighted",
            "excited",
            "ecstatic",
            "loving",
            "hateful",
            "disgusted",
            "ashamed",
            "guilty",
            "proud",
            "hopeful",
            "desperate",
            "trusting",
            "doubtful",
            "confused",
            "clear",
            "peaceful",
            "calm",
            "restless",
            "tired",
            "exhausted",
            "energized",
            "drained",
            "heavy",
            "light",
            "burdened",
            "free",
            "trapped",
            "stuck",
            "lost",
            "found",
            "broken",
            "healed",
            "wounded",
            "scarred",
            "vulnerable",
            "strong",
        }

        for token in doc:
            if token.is_stop or token.is_punct or token.is_space:
                continue

            lemma = token.lemma_.lower()

            # Extract nouns (focus on emotional/abstract nouns)
            if token.pos_ in ["NOUN", "PROPN"]:
                # Include emotional nouns and key abstract concepts
                if (
                    lemma in emotional_verbs
                    or lemma in emotional_adjectives
                    or any(
                        emotion in lemma
                        for emotion in [
                            "pain",
                            "hurt",
                            "loss",
                            "grief",
                            "joy",
                            "love",
                            "fear",
                            "anger",
                            "anxiety",
                            "stress",
                            "peace",
                            "calm",
                            "chaos",
                            "clarity",
                            "confusion",
                            "doubt",
                            "trust",
                            "hope",
                            "despair",
                        ]
                    )
                ):
                    syntactic_elements["nouns"].append(lemma)

            # Extract verbs (focus on emotional verbs)
            elif token.pos_ == "VERB":
                if lemma in emotional_verbs:
                    syntactic_elements["verbs"].append(lemma)

            # Extract adjectives (focus on emotional adjectives)
            elif token.pos_ == "ADJ":
                if lemma in emotional_adjectives:
                    syntactic_elements["adjectives"].append(lemma)

        # Remove duplicates while preserving order
        for key in syntactic_elements:
            syntactic_elements[key] = list(
                dict.fromkeys(syntactic_elements[key]))

        return syntactic_elements

    def _generate_enhanced_signals(self, dominant_emotion: str, confidence: float, text: str) -> List[Dict[str, Any]]:
        """
        Generate enhanced signal dictionaries compatible with existing system.
        """
        signals = []

        if dominant_emotion in self.emotion_signal_mappings and confidence > 0.4:
            signal, voltage, tone = self.emotion_signal_mappings[dominant_emotion]
            signals.append(
                {
                    "keyword": dominant_emotion,
                    "signal": signal,
                    "voltage": voltage,
                    "tone": tone,
                    "confidence": confidence,
                    "source": "enhanced_nlp",
                }
            )

        # Add secondary signals for mixed emotions
        if confidence > 0.6:
            # Add related emotions with lower confidence
            related_emotions = self._get_related_emotions(dominant_emotion)
            # Limit to 2 secondary signals
            for related in related_emotions[:2]:
                if related in self.emotion_signal_mappings:
                    signal, voltage, tone = self.emotion_signal_mappings[related]
                    signals.append(
                        {
                            "keyword": related,
                            "signal": signal,
                            "voltage": "low",  # Secondary signals get lower voltage
                            "tone": tone,
                            "confidence": confidence * 0.6,  # Reduced confidence
                            "source": "enhanced_nlp_secondary",
                        }
                    )

        return signals

    def _get_related_emotions(self, emotion: str) -> List[str]:
        """Get emotionally related terms for secondary signal generation."""
        emotion_clusters = {
            "sadness": ["grief", "negative"],
            "grief": ["sadness", "negative"],
            "fear": ["negative", "surprise"],
            "anger": ["negative", "disgust"],
            "joy": ["positive", "trust"],
            "trust": ["positive", "joy"],
            "anticipation": ["positive", "surprise"],
            "surprise": ["anticipation", "fear"],
            "disgust": ["anger", "negative"],
            "positive": ["joy", "trust"],
            "negative": ["sadness", "fear", "anger"],
        }
        return emotion_clusters.get(emotion, [])

    def _fallback_analysis(self, text: str) -> Dict:
        """Fallback analysis when NLP libraries aren't available."""
        return {
            "nrc_emotions": {},
            "textblob_sentiment": {"polarity": 0.0, "subjectivity": 0.0},
            "spacy_entities": [],
            "spacy_syntax": {"nouns": [], "verbs": [], "adjectives": []},
            "dominant_emotion": "neutral",
            "confidence": 0.0,
            "recommended_gates": ["Gate 9"],
            "enhanced_signals": [],
        }

    def enhance_gate_routing(self, existing_signals: List[Dict], text: str) -> Dict:
        """
        Enhance existing gate routing with comprehensive NLP analysis.

        Returns enhanced routing information that can be merged with existing signals.
        """
        comprehensive_analysis = self.analyze_emotion_comprehensive(text)

        # Merge with existing signals
        enhanced_routing = {
            "original_signals": existing_signals,
            "enhanced_signals": comprehensive_analysis["enhanced_signals"],
            "nlp_analysis": {
                "dominant_emotion": comprehensive_analysis["dominant_emotion"],
                "confidence": comprehensive_analysis["confidence"],
                "nrc_emotions": comprehensive_analysis["nrc_emotions"],
                "textblob_polarity": comprehensive_analysis["textblob_sentiment"]["polarity"],
            },
            "recommended_gates": comprehensive_analysis["recommended_gates"],
            "routing_strategy": self._determine_routing_strategy(existing_signals, comprehensive_analysis),
        }

        return enhanced_routing

    def _determine_routing_strategy(self, existing_signals: List[Dict], analysis: Dict) -> str:
        """
        Determine the best routing strategy based on signal strength and analysis.
        """
        existing_count = len(existing_signals)
        nlp_confidence = analysis["confidence"]
        has_strong_nrc = bool(analysis["nrc_emotions"] and max(
            analysis["nrc_emotions"].values()) > 1)

        if existing_count == 0 and nlp_confidence > 0.6:
            return "nlp_primary"  # Use NLP analysis as primary
        elif existing_count > 0 and nlp_confidence > 0.7:
            return "nlp_enhancement"  # Enhance existing signals
        elif existing_count > 0:
            return "existing_primary"  # Stick with existing signals
        else:
            return "fallback"  # Use default routing


# Singleton instance
enhanced_processor = EnhancedEmotionProcessor()


def analyze_emotion_enhanced(text: str) -> Dict:
    """Convenience function for enhanced emotion analysis."""
    return enhanced_processor.analyze_emotion_comprehensive(text)


def enhance_gate_routing(existing_signals: List[Dict], text: str) -> Dict:
    """Convenience function for enhanced gate routing."""
    return enhanced_processor.enhance_gate_routing(existing_signals, text)


def extract_syntactic_elements(text: str) -> Dict[str, List[str]]:
    """Convenience function to extract syntactic elements for glyph matching boost."""
    if not NLP_AVAILABLE:
        return {"nouns": [], "verbs": [], "adjectives": []}

    doc = nlp(text)
    return enhanced_processor._extract_syntactic_elements(doc)
