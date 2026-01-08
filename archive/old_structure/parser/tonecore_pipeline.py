"""
ToneCore Parallel Pipeline
--------------------------
Refactored emotional parsing pipeline that executes all analysis components
(Signal Parser, NRC, TextBlob, spaCy) in parallel for improved performance
and enhanced emotional fidelity.

This module provides:
1. Parallel execution of all emotional analysis components
2. Standardized output schemas for each module
3. Merged emotional data with conflict resolution
4. Chord progression generation based on emotional arcs

Maintains compatibility with existing gate activation logic.
"""

import concurrent.futures
import logging
import os
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Configuration defaults (can be overridden via environment variables)
DEFAULT_SPACY_MODEL = os.environ.get("TONECORE_SPACY_MODEL", "en_core_web_sm")
DEFAULT_LEXICON_PATH = os.environ.get(
    "TONECORE_LEXICON_PATH",
    str(Path(__file__).parent / "signal_lexicon.json")
)

# Standard output schemas as dataclasses
@dataclass
class SignalParserOutput:
    """Signal Parser output schema: {keyword, signal, voltage, tone}"""
    keyword: str = ""
    signal: str = ""
    voltage: str = "medium"
    tone: str = "unknown"

    def to_dict(self) -> Dict[str, str]:
        return {
            "keyword": self.keyword,
            "signal": self.signal,
            "voltage": self.voltage,
            "tone": self.tone,
        }


@dataclass
class NRCOutput:
    """NRC Emotion Lexicon output schema: {emotion_scores: {joy, sadness, fear, etc.}}"""
    emotion_scores: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"emotion_scores": self.emotion_scores}


@dataclass
class TextBlobOutput:
    """TextBlob Sentiment Analyzer output schema: {polarity, subjectivity}"""
    polarity: float = 0.0
    subjectivity: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return {"polarity": self.polarity, "subjectivity": self.subjectivity}


@dataclass
class SpacyOutput:
    """spaCy Syntax Parser output schema: {nouns, verbs, adjectives}"""
    nouns: List[str] = field(default_factory=list)
    verbs: List[str] = field(default_factory=list)
    adjectives: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, List[str]]:
        return {
            "nouns": self.nouns,
            "verbs": self.verbs,
            "adjectives": self.adjectives,
        }


@dataclass
class MergedEmotionalData:
    """Combined output from all emotional analysis modules."""
    signal_parser: List[SignalParserOutput] = field(default_factory=list)
    nrc: NRCOutput = field(default_factory=NRCOutput)
    textblob: TextBlobOutput = field(default_factory=TextBlobOutput)
    spacy: SpacyOutput = field(default_factory=SpacyOutput)
    dominant_emotion: str = "neutral"
    confidence: float = 0.0
    emotional_arc: List[str] = field(default_factory=list)
    recommended_gates: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_parser": [s.to_dict() for s in self.signal_parser],
            "nrc": self.nrc.to_dict(),
            "textblob": self.textblob.to_dict(),
            "spacy": self.spacy.to_dict(),
            "dominant_emotion": self.dominant_emotion,
            "confidence": self.confidence,
            "emotional_arc": self.emotional_arc,
            "recommended_gates": self.recommended_gates,
        }


@dataclass
class ChordProgression:
    """Generated chord progression based on emotional data."""
    chords: List[str] = field(default_factory=list)
    emotion_sequence: List[str] = field(default_factory=list)
    arc_description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chords": self.chords,
            "emotion_sequence": self.emotion_sequence,
            "arc_description": self.arc_description,
        }


# Module availability flags
NRC_AVAILABLE = False
TEXTBLOB_AVAILABLE = False
SPACY_AVAILABLE = False

# Lazy-loaded module references
_nrc = None
_TextBlob = None
_nlp = None


def _load_nrc():
    """Lazy load NRC lexicon."""
    global _nrc, NRC_AVAILABLE
    if _nrc is not None:
        return _nrc
    try:
        from parser.nrc_lexicon_loader import nrc
        _nrc = nrc
        NRC_AVAILABLE = _nrc.loaded if _nrc else False
    except ImportError:
        NRC_AVAILABLE = False
        _nrc = None
    return _nrc


def _load_textblob():
    """Lazy load TextBlob."""
    global _TextBlob, TEXTBLOB_AVAILABLE
    if _TextBlob is not None:
        return _TextBlob
    try:
        from textblob import TextBlob
        _TextBlob = TextBlob
        TEXTBLOB_AVAILABLE = True
    except ImportError:
        TEXTBLOB_AVAILABLE = False
        _TextBlob = None
    return _TextBlob


def _load_spacy():
    """Lazy load spaCy with configurable model."""
    global _nlp, SPACY_AVAILABLE
    if _nlp is not None:
        return _nlp
    try:
        import spacy
        _nlp = spacy.load(DEFAULT_SPACY_MODEL)
        SPACY_AVAILABLE = True
    except (ImportError, OSError):
        SPACY_AVAILABLE = False
        _nlp = None
    return _nlp


class ToneCorePipeline:
    """
    Parallel emotional parsing pipeline that executes Signal Parser, NRC,
    TextBlob, and spaCy concurrently on the same input text.
    """

    # Emotion-to-gate mappings for ECM system
    EMOTION_GATE_MAPPINGS = {
        'sadness': ['Gate 4', 'Gate 10'],
        'grief': ['Gate 4', 'Gate 10'],
        'fear': ['Gate 4', 'Gate 2'],
        'anger': ['Gate 5', 'Gate 4'],
        'joy': ['Gate 5', 'Gate 6'],
        'trust': ['Gate 2', 'Gate 4'],
        'anticipation': ['Gate 6', 'Gate 5'],
        'surprise': ['Gate 6', 'Gate 9'],
        'disgust': ['Gate 2', 'Gate 5'],
        'positive': ['Gate 5', 'Gate 6'],
        'negative': ['Gate 4', 'Gate 10'],
        'neutral': ['Gate 9'],
    }

    # Emotion-to-chord function mappings
    EMOTION_CHORD_MAPPINGS = {
        'longing': {'function': 'i', 'quality': 'minor'},
        'stress': {'function': 'viio', 'quality': 'diminished'},
        'joy': {'function': 'I', 'quality': 'major'},
        'calm': {'function': 'IV', 'quality': 'major'},
        'hope': {'function': 'V', 'quality': 'major'},
        'melancholy': {'function': 'vi', 'quality': 'minor'},
        'wonder': {'function': 'III', 'quality': 'major'},
        'resolve': {'function': 'V7', 'quality': 'dominant7'},
        'sadness': {'function': 'iv', 'quality': 'minor'},
        'fear': {'function': 'viio', 'quality': 'diminished'},
        'anger': {'function': 'V', 'quality': 'major'},
        'trust': {'function': 'IV', 'quality': 'major'},
        'anticipation': {'function': 'V', 'quality': 'major'},
        'surprise': {'function': 'bVI', 'quality': 'major'},
        'disgust': {'function': 'ii', 'quality': 'minor'},
        'positive': {'function': 'I', 'quality': 'major'},
        'negative': {'function': 'i', 'quality': 'minor'},
        'neutral': {'function': 'I', 'quality': 'major'},
        'grief': {'function': 'iv', 'quality': 'minor'},
    }

    # NRC emotions to signal mappings
    NRC_TO_SIGNAL = {
        'trust': ('β', 'medium', 'containment'),
        'fear': ('θ', 'high', 'grief'),
        'negative': ('θ', 'high', 'grief'),
        'sadness': ('θ', 'medium', 'grief'),
        'disgust': ('β', 'high', 'containment'),
        'anger': ('γ', 'high', 'longing'),
        'surprise': ('ε', 'medium', 'insight'),
        'positive': ('λ', 'high', 'joy'),
        'anticipation': ('ε', 'medium', 'insight'),
        'joy': ('λ', 'high', 'joy'),
    }

    def __init__(self, enable_cache: bool = True, max_workers: int = 4):
        """
        Initialize the ToneCore pipeline.

        Args:
            enable_cache: Enable caching for module outputs (default True)
            max_workers: Maximum number of parallel workers (default 4)
        """
        self.enable_cache = enable_cache
        self.max_workers = max_workers
        self._cache: Dict[str, MergedEmotionalData] = {}

        # Pre-load modules at initialization (optional, can be lazy)
        _load_nrc()
        _load_textblob()
        _load_spacy()

    def _run_signal_parser(self, text: str) -> List[SignalParserOutput]:
        """Run Signal Parser on input text."""
        try:
            from emotional_os.core.signal_parser import load_signal_map, parse_signals
            # Use configurable lexicon path with fallback to default
            lexicon_path = DEFAULT_LEXICON_PATH
            if not os.path.exists(lexicon_path):
                # Fallback to legacy path for compatibility
                lexicon_path = "emotional_os/parser/signal_lexicon.json"
            signal_map = load_signal_map(lexicon_path)
            raw_signals = parse_signals(text, signal_map)

            outputs = []
            for sig in raw_signals:
                if isinstance(sig, dict):
                    outputs.append(SignalParserOutput(
                        keyword=sig.get('keyword', ''),
                        signal=sig.get('signal', ''),
                        voltage=sig.get('voltage', 'medium'),
                        tone=sig.get('tone', 'unknown'),
                    ))
            return outputs
        except Exception as e:
            logger.debug(f"Signal parser failed: {e}")
            return []

    def _run_nrc(self, text: str) -> NRCOutput:
        """Run NRC Emotion Lexicon analysis on input text."""
        nrc = _load_nrc()
        if not nrc or not nrc.loaded:
            return NRCOutput()

        try:
            emotions = nrc.analyze_text(text)
            return NRCOutput(emotion_scores=emotions)
        except Exception as e:
            logger.debug(f"NRC analysis failed: {e}")
            return NRCOutput()

    def _run_textblob(self, text: str) -> TextBlobOutput:
        """Run TextBlob sentiment analysis on input text."""
        TextBlob = _load_textblob()
        if not TextBlob:
            return TextBlobOutput()

        try:
            blob = TextBlob(text)
            return TextBlobOutput(
                polarity=blob.sentiment.polarity,
                subjectivity=blob.sentiment.subjectivity,
            )
        except Exception as e:
            logger.debug(f"TextBlob analysis failed: {e}")
            return TextBlobOutput()

    def _run_spacy(self, text: str) -> SpacyOutput:
        """Run spaCy syntax parsing on input text."""
        nlp = _load_spacy()
        if not nlp:
            return SpacyOutput()

        try:
            doc = nlp(text)
            nouns = []
            verbs = []
            adjectives = []

            # Emotional word sets for filtering
            emotional_verbs = {
                'feel', 'feeling', 'felt', 'experience', 'overwhelm', 'overwhelmed',
                'worry', 'worrying', 'fear', 'afraid', 'scared', 'sad', 'grieve',
                'angry', 'frustrate', 'rage', 'happy', 'joy', 'delight', 'love',
                'hate', 'shame', 'guilt', 'hope', 'despair', 'trust', 'doubt',
            }
            emotional_adjectives = {
                'overwhelmed', 'anxious', 'nervous', 'worried', 'fearful', 'afraid',
                'sad', 'sorrowful', 'angry', 'furious', 'frustrated', 'happy',
                'joyful', 'excited', 'ashamed', 'guilty', 'proud', 'hopeful',
                'desperate', 'peaceful', 'calm', 'tired', 'exhausted', 'vulnerable',
            }

            for token in doc:
                if token.is_stop or token.is_punct or token.is_space:
                    continue
                lemma = token.lemma_.lower()

                if token.pos_ in ['NOUN', 'PROPN']:
                    nouns.append(lemma)
                elif token.pos_ == 'VERB':
                    if lemma in emotional_verbs:
                        verbs.append(lemma)
                elif token.pos_ == 'ADJ':
                    if lemma in emotional_adjectives:
                        adjectives.append(lemma)

            # Remove duplicates while preserving order
            nouns = list(dict.fromkeys(nouns))
            verbs = list(dict.fromkeys(verbs))
            adjectives = list(dict.fromkeys(adjectives))

            return SpacyOutput(nouns=nouns, verbs=verbs, adjectives=adjectives)
        except Exception as e:
            logger.debug(f"spaCy analysis failed: {e}")
            return SpacyOutput()

    def analyze(self, text: str) -> MergedEmotionalData:
        """
        Run parallel emotional analysis on input text.

        Executes Signal Parser, NRC, TextBlob, and spaCy concurrently,
        then merges results with conflict resolution.

        Args:
            text: Input text to analyze

        Returns:
            MergedEmotionalData with combined analysis from all modules
        """
        if not text or not text.strip():
            return MergedEmotionalData()

        # Check cache first
        cache_key = text.strip()
        if self.enable_cache and cache_key in self._cache:
            return self._cache[cache_key]

        # Run all modules in parallel
        signal_result: List[SignalParserOutput] = []
        nrc_result = NRCOutput()
        textblob_result = TextBlobOutput()
        spacy_result = SpacyOutput()

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._run_signal_parser, text): 'signal',
                executor.submit(self._run_nrc, text): 'nrc',
                executor.submit(self._run_textblob, text): 'textblob',
                executor.submit(self._run_spacy, text): 'spacy',
            }

            for future in concurrent.futures.as_completed(futures):
                module = futures[future]
                try:
                    result = future.result()
                    if module == 'signal':
                        signal_result = result
                    elif module == 'nrc':
                        nrc_result = result
                    elif module == 'textblob':
                        textblob_result = result
                    elif module == 'spacy':
                        spacy_result = result
                except Exception as e:
                    logger.warning(f"Module {module} failed: {e}")

        # Merge results
        merged = self.mergeEmotionalData(
            signal_parser=signal_result,
            nrc=nrc_result,
            textblob=textblob_result,
            spacy=spacy_result,
        )

        # Cache result
        if self.enable_cache:
            self._cache[cache_key] = merged

        return merged

    def mergeEmotionalData(
        self,
        signal_parser: List[SignalParserOutput],
        nrc: NRCOutput,
        textblob: TextBlobOutput,
        spacy: SpacyOutput,
    ) -> MergedEmotionalData:
        """
        Normalize and combine outputs from all modules with conflict resolution
        and contextual weighting.

        Args:
            signal_parser: Signal Parser output
            nrc: NRC Emotion Lexicon output
            textblob: TextBlob sentiment output
            spacy: spaCy syntax output

        Returns:
            MergedEmotionalData with unified emotional assessment
        """
        merged = MergedEmotionalData(
            signal_parser=signal_parser,
            nrc=nrc,
            textblob=textblob,
            spacy=spacy,
        )

        # Determine dominant emotion with weighted scoring
        dominant_emotion, confidence = self._determine_dominant_emotion(
            signal_parser, nrc, textblob
        )
        merged.dominant_emotion = dominant_emotion
        merged.confidence = confidence

        # Calculate emotional arc based on NRC scores
        merged.emotional_arc = self._calculate_emotional_arc(nrc)

        # Determine recommended gates
        merged.recommended_gates = self.EMOTION_GATE_MAPPINGS.get(
            dominant_emotion, ['Gate 9']
        )

        return merged

    def _determine_dominant_emotion(
        self,
        signal_parser: List[SignalParserOutput],
        nrc: NRCOutput,
        textblob: TextBlobOutput,
    ) -> Tuple[str, float]:
        """
        Determine the dominant emotion with confidence score using weighted
        combination of all sources.

        Weighting strategy:
        - NRC lexicon: 40% weight (broad emotional vocabulary)
        - Signal parser: 35% weight (domain-specific emotional terms)
        - TextBlob polarity: 25% weight (overall sentiment direction)
        """
        emotion_scores: Dict[str, float] = {}

        # Weight 1: NRC emotions (40%)
        nrc_total = sum(nrc.emotion_scores.values())
        if nrc_total > 0:
            for emotion, count in nrc.emotion_scores.items():
                score = (count / nrc_total) * 0.4
                emotion_scores[emotion] = emotion_scores.get(emotion, 0) + score

        # Weight 2: Signal parser tones (35%)
        if signal_parser:
            tone_counts: Dict[str, int] = {}
            for sig in signal_parser:
                tone = sig.tone
                if tone and tone != 'unknown':
                    tone_counts[tone] = tone_counts.get(tone, 0) + 1

            total_tones = sum(tone_counts.values())
            if total_tones > 0:
                tone_to_emotion = {
                    'grief': 'sadness',
                    'longing': 'longing',
                    'containment': 'trust',
                    'insight': 'anticipation',
                    'joy': 'joy',
                    'devotion': 'trust',
                    'recognition': 'positive',
                }
                for tone, count in tone_counts.items():
                    emotion = tone_to_emotion.get(tone, tone)
                    score = (count / total_tones) * 0.35
                    emotion_scores[emotion] = emotion_scores.get(emotion, 0) + score

        # Weight 3: TextBlob polarity (25%)
        polarity = textblob.polarity
        if polarity > 0.3:
            emotion_scores['positive'] = emotion_scores.get('positive', 0) + 0.25
            emotion_scores['joy'] = emotion_scores.get('joy', 0) + 0.15
        elif polarity < -0.3:
            emotion_scores['negative'] = emotion_scores.get('negative', 0) + 0.25
            emotion_scores['sadness'] = emotion_scores.get('sadness', 0) + 0.15
        else:
            emotion_scores['neutral'] = emotion_scores.get('neutral', 0) + 0.15

        # Determine dominant emotion
        if not emotion_scores:
            return 'neutral', 0.3

        dominant = max(emotion_scores.items(), key=lambda x: x[1])
        return dominant[0], min(dominant[1], 1.0)

    def _calculate_emotional_arc(self, nrc: NRCOutput) -> List[str]:
        """
        Calculate emotional arc/progression based on NRC emotion scores.

        Returns a sequence of emotions ordered by intensity, representing
        the emotional journey in the text.
        """
        if not nrc.emotion_scores:
            return ['neutral']

        # Sort emotions by score descending
        sorted_emotions = sorted(
            nrc.emotion_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Return top 3 emotions as the arc
        arc = [emotion for emotion, _ in sorted_emotions[:3]]
        return arc if arc else ['neutral']

    def generate_chord_progression(
        self,
        merged_data: MergedEmotionalData,
        length: int = 4,
    ) -> ChordProgression:
        """
        Generate a sequence of emotional chords reflecting the merged emotional map.

        Uses the emotional arc from merged data to create a chord progression
        that represents the emotional journey.

        Args:
            merged_data: Merged emotional analysis data
            length: Number of chords to generate (default 4)

        Returns:
            ChordProgression with chords and emotion sequence
        """
        # Use emotional arc to determine chord sequence
        emotion_sequence = merged_data.emotional_arc[:length]

        # Pad with dominant emotion if arc is shorter than length
        while len(emotion_sequence) < length:
            emotion_sequence.append(merged_data.dominant_emotion)

        # Map emotions to chord functions
        chords = []
        for emotion in emotion_sequence:
            chord_info = self.EMOTION_CHORD_MAPPINGS.get(
                emotion,
                self.EMOTION_CHORD_MAPPINGS.get('neutral')
            )
            if chord_info:
                chords.append(chord_info['function'])

        # Generate arc description
        if len(set(emotion_sequence)) == 1:
            arc_description = f"Sustained {emotion_sequence[0]} throughout"
        elif emotion_sequence[0] != emotion_sequence[-1]:
            arc_description = f"Transition from {emotion_sequence[0]} to {emotion_sequence[-1]}"
        else:
            arc_description = f"Cyclic {emotion_sequence[0]} with variations"

        return ChordProgression(
            chords=chords,
            emotion_sequence=emotion_sequence,
            arc_description=arc_description,
        )

    def clear_cache(self):
        """Clear the analysis cache."""
        self._cache.clear()

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {"size": len(self._cache)}


# Singleton instance for convenience
_pipeline_instance: Optional[ToneCorePipeline] = None


def get_pipeline(enable_cache: bool = True) -> ToneCorePipeline:
    """Get or create the singleton ToneCore pipeline instance."""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = ToneCorePipeline(enable_cache=enable_cache)
    return _pipeline_instance


def analyze_text(text: str) -> MergedEmotionalData:
    """
    Convenience function for parallel emotional analysis.

    Args:
        text: Input text to analyze

    Returns:
        MergedEmotionalData with combined analysis from all modules
    """
    return get_pipeline().analyze(text)


def generate_chord_progression(text: str, length: int = 4) -> ChordProgression:
    """
    Convenience function to analyze text and generate chord progression.

    Args:
        text: Input text to analyze
        length: Number of chords to generate (default 4)

    Returns:
        ChordProgression based on emotional analysis
    """
    pipeline = get_pipeline()
    merged = pipeline.analyze(text)
    return pipeline.generate_chord_progression(merged, length)
