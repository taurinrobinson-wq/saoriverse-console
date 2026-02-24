"""
Enhanced Affect Parser - Integrates NRC Lexicon, TextBlob, SpaCy, and Regex patterns.

This module provides advanced emotion detection for the glyph-informed chat system.
It combines multiple approaches for robust affect analysis:

1. NRC Emotion Lexicon - 10,000+ words with emotion associations
2. TextBlob Polarity & Subjectivity - Fast sentiment analysis
3. SpaCy Dependency Parsing - Context-aware analysis
4. Regex Patterns - High-confidence pattern matching
5. Intensifier Handling - Negation and emphasis detection
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class EmotionDimension(Enum):
    """NRC Emotion lexicon categories."""
    ANGER = "anger"
    ANTICIPATION = "anticipation"
    DISGUST = "disgust"
    FEAR = "fear"
    JOY = "joy"
    NEGATIVE = "negative"
    POSITIVE = "positive"
    SADNESS = "sadness"
    SURPRISE = "surprise"
    TRUST = "trust"


@dataclass
class EnhancedAffectAnalysis:
    """Rich affect analysis result."""
    # Primary emotion
    primary_emotion: str  # anger, joy, sadness, fear, surprise, disgust, trust, anticipation
    emotion_confidence: float  # 0-1
    
    # Dimensions (from AffectParser)
    valence: float  # -1 (negative) to +1 (positive)
    arousal: float  # 0 (calm) to 1 (intense)
    dominance: float  # 0 (low control) to 1 (high control) - NEW
    
    # Sentiment (from TextBlob)
    sentiment_polarity: float  # -1 to +1
    sentiment_subjectivity: float  # 0 (objective) to 1 (subjective)
    
    # NRC scores for all 10 emotions
    nrc_scores: Dict[str, float]  # emotion -> confidence
    
    # Modifiers
    is_negated: bool = False  # Statement has negation
    has_intensifier: bool = False  # Strong emphasis
    sarcasm_likely: bool = False  # Potential sarcasm detected
    
    # Confidence metrics
    method_agreement: float = 0.0  # How well different methods agree (0-1)
    overall_confidence: float = 0.0  # Final confidence (0-1)
    
    # Human-readable summary
    explanation: str = ""


class EnhancedAffectParser:
    """Advanced affect parser with NRC + TextBlob + SpaCy."""
    
    def __init__(self, use_nrc: bool = True, use_textblob: bool = True, use_spacy: bool = True):
        """Initialize enhanced parser with optional components.
        
        Args:
            use_nrc: Use NRC emotion lexicon (requires nrc_lexicon data)
            use_textblob: Use TextBlob sentiment analysis
            use_spacy: Use SpaCy dependency parsing (requires spacy model)
        """
        self.use_nrc = use_nrc
        self.use_textblob = use_textblob
        self.use_spacy = use_spacy
        
        # Load NRC lexicon if available
        self.nrc_lexicon = {}
        if use_nrc:
            self._load_nrc_lexicon()
        
        # Load TextBlob if available
        self.textblob_available = False
        if use_textblob:
            try:
                from textblob import TextBlob
                self.TextBlob = TextBlob
                self.textblob_available = True
                logger.info("✓ TextBlob loaded")
            except ImportError:
                logger.warning("TextBlob not available: pip install textblob")
        
        # SpaCy model will be loaded lazily when needed to avoid side-effects
        # at module import time (prevents Streamlit hot-reload churn).
        self.spacy_model = None
        self.use_spacy = use_spacy
        
        # Intensifiers and negation markers
        self.intensifiers = {
            "very", "extremely", "incredibly", "absolutely", "completely",
            "totally", "definitely", "certainly", "clearly", "obviously",
            "really", "so", "much", "far", "deeply", "profoundly"
        }
        
        self.negation_words = {
            "not", "no", "never", "neither", "nobody", "nothing",
            "nowhere", "couldn't", "wouldn't", "shouldn't", "can't",
            "won't", "don't", "doesn't", "didn't", "isn't", "aren't",
            "wasn't", "weren't", "haven't", "hasn't"
        }
        
        self.sarcasm_markers = [
            ("yeah right", 0.9),
            ("sure", 0.6),
            ("oh great", 0.8),
            ("fantastic", 0.7),
            ("wonderful", 0.7),
            ("perfect", 0.6),
            ("lovely", 0.6),
        ]
    
    def _load_nrc_lexicon(self):
        """Load NRC Emotion Lexicon.
        
        NRC Lexicon: https://saifmohammad.com/WebPages/NRC-Emotion-Lexicon.htm
        Format: word -> {emotion: binary_value}
        """
        try:
            import json
            from pathlib import Path
            
            # Try to load from common locations
            nrc_paths = [
                Path("data/NRC-Emotion-Lexicon-Wordlevel-v0.92.txt"),
                Path("./NRC-Emotion-Lexicon-Wordlevel-v0.92.txt"),
                Path("../data/nrc_lexicon.json"),
            ]
            
            for nrc_path in nrc_paths:
                if nrc_path.exists():
                    if nrc_path.suffix == ".json":
                        with open(nrc_path) as f:
                            self.nrc_lexicon = json.load(f)
                    else:
                        # Parse NRC text format
                        self._parse_nrc_text_file(nrc_path)
                    logger.info(f"✓ NRC lexicon loaded: {len(self.nrc_lexicon)} words")
                    return
            
            logger.warning("NRC lexicon file not found. Using fallback basic lexicon.")
            self._create_fallback_nrc()
            
        except Exception as e:
            logger.warning(f"Error loading NRC lexicon: {e}. Using fallback.")
            self._create_fallback_nrc()
    
    def _parse_nrc_text_file(self, filepath):
        """Parse NRC text file format (word\temotion\t0/1)."""
        try:
            with open(filepath, encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split("\t")
                    if len(parts) >= 3:
                        word, emotion, value = parts[0], parts[1], int(parts[2])
                        if word not in self.nrc_lexicon:
                            self.nrc_lexicon[word] = {}
                        if value == 1:
                            self.nrc_lexicon[word][emotion] = 1.0
        except Exception as e:
            logger.exception(f"Error parsing NRC file: {e}")
    
    def _create_fallback_nrc(self):
        """Create minimal fallback NRC lexicon."""
        fallback = {
            # Joy words
            "happy": {"joy": 1.0, "positive": 1.0},
            "joy": {"joy": 1.0, "positive": 1.0},
            "love": {"joy": 1.0, "positive": 1.0, "trust": 1.0},
            "beautiful": {"joy": 1.0, "positive": 1.0},
            "excellent": {"joy": 1.0, "positive": 1.0},
            
            # Sadness words
            "sad": {"sadness": 1.0, "negative": 1.0},
            "grief": {"sadness": 1.0, "negative": 1.0},
            "mourn": {"sadness": 1.0, "negative": 1.0},
            "lonely": {"sadness": 1.0, "negative": 1.0},
            "depressed": {"sadness": 1.0, "negative": 1.0},
            
            # Fear words
            "afraid": {"fear": 1.0, "negative": 1.0},
            "scared": {"fear": 1.0, "negative": 1.0},
            "panic": {"fear": 1.0, "negative": 1.0},
            "terror": {"fear": 1.0, "negative": 1.0},
            
            # Anger words
            "angry": {"anger": 1.0, "negative": 1.0},
            "furious": {"anger": 1.0, "negative": 1.0},
            "rage": {"anger": 1.0, "negative": 1.0},
            "hate": {"anger": 1.0, "negative": 1.0},
            
            # Disgust words
            "disgusted": {"disgust": 1.0, "negative": 1.0},
            "gross": {"disgust": 1.0, "negative": 1.0},
            "vile": {"disgust": 1.0, "negative": 1.0},
            
            # Trust words
            "trust": {"trust": 1.0, "positive": 1.0},
            "confidence": {"trust": 1.0, "positive": 1.0},
            "believe": {"trust": 1.0, "positive": 1.0},
            
            # Anticipation words
            "expect": {"anticipation": 1.0, "positive": 0.5},
            "hope": {"anticipation": 1.0, "positive": 1.0},
            "looking forward": {"anticipation": 1.0, "positive": 1.0},
            
            # Surprise words
            "surprised": {"surprise": 1.0},
            "amazed": {"surprise": 1.0},
            "shocked": {"surprise": 1.0},
        }
        self.nrc_lexicon = fallback
        logger.info("Fallback NRC lexicon created")
    
    def analyze_affect(self, text: str) -> EnhancedAffectAnalysis:
        """Analyze affect using all available methods.
        
        Args:
            text: User input text
        
        Returns:
            Comprehensive EnhancedAffectAnalysis
        """
        if not text:
            return self._create_neutral_analysis()
        
        text_lower = text.lower()
        
        # 1. NRC Analysis
        nrc_scores = self._analyze_nrc(text_lower)
        
        # 2. TextBlob Analysis
        textblob_polarity = 0.0
        textblob_subjectivity = 0.5
        if self.textblob_available:
            textblob_polarity, textblob_subjectivity = self._analyze_textblob(text)
        
        # 3. SpaCy Analysis (for dependency parsing / negation detection)
        if self.use_spacy:
            try:
                # Lazy-load spaCy model when first needed
                if self.spacy_model is None:
                    try:
                        from emotional_os.utils.nlp_loader import get_spacy_model
                    except Exception:
                        from src.emotional_os.utils.nlp_loader import get_spacy_model  # type: ignore
                    self.spacy_model = get_spacy_model()
            except Exception:
                self.spacy_model = None
        
        # 4. Pattern Analysis
        is_negated = self._has_negation(text_lower)
        has_intensifier = self._has_intensifier(text_lower)
        sarcasm_likely = self._detect_sarcasm(text_lower)
        
        # 5. Derive primary emotion from NRC
        primary_emotion, primary_confidence = self._get_primary_emotion(nrc_scores)
        
        # 6. Calculate dimensions
        valence = self._calculate_valence(nrc_scores, textblob_polarity, is_negated)
        arousal = self._calculate_arousal(nrc_scores, has_intensifier)
        dominance = self._calculate_dominance(text_lower, nrc_scores)
        
        # 7. Agreement between methods
        method_agreement = self._calculate_method_agreement(
            valence, textblob_polarity, nrc_scores
        )
        
        # 8. Overall confidence
        overall_confidence = (primary_confidence + method_agreement) / 2
        
        # 9. Generate explanation
        explanation = self._generate_explanation(
            primary_emotion, valence, arousal, sarcasm_likely, is_negated
        )
        
        return EnhancedAffectAnalysis(
            primary_emotion=primary_emotion,
            emotion_confidence=primary_confidence,
            valence=valence,
            arousal=arousal,
            dominance=dominance,
            sentiment_polarity=textblob_polarity,
            sentiment_subjectivity=textblob_subjectivity,
            nrc_scores=nrc_scores,
            is_negated=is_negated,
            has_intensifier=has_intensifier,
            sarcasm_likely=sarcasm_likely,
            method_agreement=method_agreement,
            overall_confidence=overall_confidence,
            explanation=explanation
        )
    
    def _analyze_nrc(self, text: str) -> Dict[str, float]:
        """Analyze text using NRC emotion lexicon."""
        emotions = {
            "anger": 0.0,
            "anticipation": 0.0,
            "disgust": 0.0,
            "fear": 0.0,
            "joy": 0.0,
            "negative": 0.0,
            "positive": 0.0,
            "sadness": 0.0,
            "surprise": 0.0,
            "trust": 0.0,
        }
        
        words = text.split()
        word_count = len(words)
        
        for word in words:
            word_clean = word.strip(".,!?;:'\"")
            if word_clean in self.nrc_lexicon:
                word_emotions = self.nrc_lexicon[word_clean]
                for emotion, value in word_emotions.items():
                    emotions[emotion] += value
        
        # Normalize by word count
        if word_count > 0:
            for emotion in emotions:
                emotions[emotion] /= word_count
        
        return emotions
    
    def _analyze_textblob(self, text: str) -> Tuple[float, float]:
        """Analyze sentiment using TextBlob."""
        try:
            blob = self.TextBlob(text)
            return blob.sentiment.polarity, blob.sentiment.subjectivity
        except Exception as e:
            logger.warning(f"TextBlob analysis failed: {e}")
            return 0.0, 0.5
    
    def _has_negation(self, text: str) -> bool:
        """Check if text contains negation."""
        # First, try spaCy-based negation detection if model available
        try:
            if self.spacy_model is None and self.use_spacy:
                try:
                    from emotional_os.utils.nlp_loader import get_spacy_model
                except Exception:
                    from src.emotional_os.utils.nlp_loader import get_spacy_model  # type: ignore
                self.spacy_model = get_spacy_model()

            if self.spacy_model is not None:
                doc = self.spacy_model(text)
                for token in doc:
                    # token.dep_ == 'neg' is a common pattern for negation
                    if token.dep_.lower() == "neg" or token.lower_ in self.negation_words:
                        return True
        except Exception:
            pass

        # Fallback simple word-based check
        words = text.split()
        for word in words:
            if word.strip(".,!?;:'\"") in self.negation_words:
                return True
        return False
    
    def _has_intensifier(self, text: str) -> bool:
        """Check if text has intensifier words."""
        words = text.split()
        for word in words:
            if word.strip(".,!?;:'\"") in self.intensifiers:
                return True
        # Check for multiple exclamation marks
        if text.count("!") >= 2:
            return True
        return False
    
    def _detect_sarcasm(self, text: str) -> bool:
        """Detect likely sarcasm patterns."""
        for marker, confidence in self.sarcasm_markers:
            if marker in text:
                return confidence > 0.5
        
        # Capitalized words might indicate sarcasm
        words = text.split()
        capitalized_count = sum(1 for w in words if w.isupper() and len(w) > 1)
        if capitalized_count >= len(words) * 0.3:  # 30% capitalized
            return True
        
        return False
    
    def _get_primary_emotion(self, nrc_scores: Dict[str, float]) -> Tuple[str, float]:
        """Get primary emotion from NRC scores."""
        # Exclude positive/negative, focus on basic emotions
        basic_emotions = {
            k: v for k, v in nrc_scores.items()
            if k not in ("positive", "negative")
        }
        
        if not basic_emotions or max(basic_emotions.values()) == 0:
            return "neutral", 0.5
        
        primary = max(basic_emotions, key=basic_emotions.get)
        confidence = min(basic_emotions[primary], 1.0)
        
        return primary, confidence
    
    def _calculate_valence(
        self,
        nrc_scores: Dict[str, float],
        textblob_polarity: float,
        is_negated: bool
    ) -> float:
        """Calculate valence from multiple sources."""
        # NRC-based: positive - negative
        nrc_valence = nrc_scores.get("positive", 0.0) - nrc_scores.get("negative", 0.0)
        
        # Combine with TextBlob polarity
        combined = (nrc_valence + textblob_polarity) / 2
        
        # Adjust for negation
        if is_negated and combined > 0:
            combined *= 0.5  # Reduce positive valence if negated
        
        # Clamp to -1 to 1
        return max(-1.0, min(1.0, combined))
    
    def _calculate_arousal(self, nrc_scores: Dict[str, float], has_intensifier: bool) -> float:
        """Calculate arousal/activation level."""
        # High-arousal emotions
        high_arousal_emotions = ["anger", "fear", "joy", "surprise"]
        arousal = sum(
            nrc_scores.get(emotion, 0.0)
            for emotion in high_arousal_emotions
        ) / len(high_arousal_emotions)
        
        # Boost if intensifier present
        if has_intensifier:
            arousal = min(1.0, arousal * 1.3)
        
        return max(0.0, min(1.0, arousal))
    
    def _calculate_dominance(self, text: str, nrc_scores: Dict[str, float]) -> float:
        """Calculate sense of control/dominance."""
        # Trust and anticipation indicate higher dominance
        dominance_emotions = nrc_scores.get("trust", 0.0) + nrc_scores.get("anticipation", 0.0)
        dominance = dominance_emotions / 2
        
        # Fear and sadness indicate lower dominance
        low_dominance_emotions = nrc_scores.get("fear", 0.0) + nrc_scores.get("sadness", 0.0)
        dominance -= low_dominance_emotions / 2
        
        return max(0.0, min(1.0, 0.5 + dominance))
    
    def _calculate_method_agreement(
        self,
        valence: float,
        textblob_polarity: float,
        nrc_scores: Dict[str, float]
    ) -> float:
        """Calculate how well different methods agree."""
        # Agreement between valence and TextBlob polarity
        polarity_agreement = 1.0 - abs(valence - textblob_polarity) / 2
        
        # Agreement between NRC and TextBlob
        nrc_polarity = nrc_scores.get("positive", 0.0) - nrc_scores.get("negative", 0.0)
        nrc_agreement = 1.0 - abs(nrc_polarity - textblob_polarity) / 2
        
        return (polarity_agreement + nrc_agreement) / 2
    
    def _generate_explanation(
        self,
        primary_emotion: str,
        valence: float,
        arousal: float,
        sarcasm_likely: bool,
        is_negated: bool
    ) -> str:
        """Generate human-readable explanation."""
        parts = []
        
        if sarcasm_likely:
            parts.append("likely sarcasm detected")
        
        if is_negated:
            parts.append("contains negation")
        
        parts.append(f"primary emotion: {primary_emotion}")
        
        if valence > 0.5:
            parts.append("positive tone")
        elif valence < -0.5:
            parts.append("negative tone")
        else:
            parts.append("neutral tone")
        
        if arousal > 0.6:
            parts.append("high intensity")
        elif arousal < 0.4:
            parts.append("low intensity")
        
        return "; ".join(parts)
    
    def _create_neutral_analysis(self) -> EnhancedAffectAnalysis:
        """Create neutral analysis for empty input."""
        return EnhancedAffectAnalysis(
            primary_emotion="neutral",
            emotion_confidence=1.0,
            valence=0.0,
            arousal=0.0,
            dominance=0.5,
            sentiment_polarity=0.0,
            sentiment_subjectivity=0.5,
            nrc_scores={e.value: 0.0 for e in EmotionDimension},
            overall_confidence=1.0,
            explanation="empty or neutral input"
        )


# Factory function
def create_enhanced_affect_parser(use_nrc=True, use_textblob=True, use_spacy=True) -> EnhancedAffectParser:
    """Create an enhanced affect parser instance."""
    return EnhancedAffectParser(use_nrc=use_nrc, use_textblob=use_textblob, use_spacy=use_spacy)
