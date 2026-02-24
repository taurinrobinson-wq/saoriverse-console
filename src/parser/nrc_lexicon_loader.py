"""Minimal NRC lexicon loader shim.

Provides a tiny `nrc` object with a `lexicon` and `analyze_text(text)` method.
This is a pragmatic, lightweight fallback implementation so the repo can
use NRC-style emotion lookups without an external dependency.

It performs simple keyword matching and returns a dict of emotion->score.
"""
from __future__ import annotations

import re
from typing import Dict


class _SimpleNRC:
    def __init__(self):
        # Minimal emotion keyword sets; extend as needed
        self.lexicon = {
            "anger": ["angry", "mad", "furious", "irritated", "annoyed"],
            "anticipation": ["expect", "await", "anticipat", "looking forward"],
            "disgust": ["disgust", "gross", "repulsed"],
            "fear": ["scared", "afraid", "fear", "anxious", "panic"],
            "joy": ["happy", "joy", "glad", "delighted", "excited"],
            "negative": ["bad", "terrible", "awful", "horrible"],
            "positive": ["good", "great", "wonderful", "nice"],
            "sadness": ["sad", "unhappy", "mourn", "grief", "cry"],
            "surprise": ["surprise", "surprised", "unexpected"],
            "trust": ["trust", "trusted", "rely", "depend"],
        }
        # Flattened set for quick membership tests
        self._keywords = {e: set(w for w in words) for e, words in self.lexicon.items()}
        self.loaded = True

    def analyze_text(self, text: str) -> Dict[str, float]:
        """Return a simple score map of emotions detected in `text`.

        Scores are 0..1 based on keyword hit counts normalized by total keywords
        found for each emotion.
        """
        lower = text.lower()
        words = re.findall(r"\w+", lower)
        word_set = set(words)
        scores: Dict[str, float] = {}
        for emotion, keys in self._keywords.items():
            hits = sum(1 for k in keys if k in lower or k in word_set)
            if hits:
                # crude score: hits / number of keywords for emotion
                scores[emotion] = hits / max(1, len(keys))
        return scores


# Robust NRC loader with optional file-backed lexicon and a lightweight fallback.
from pathlib import Path
from typing import Dict, List


class NRC:
    def __init__(self):
        self.lexicon: Dict[str, List[str]] = {}
        self.loaded: bool = False
        self._init()

    def _init(self):
        possible = [
            Path("data/lexicons/nrc_emotion_lexicon.txt"),
            Path("data/lexicons/nrc_lexicon_cleaned.json"),
            Path("emotional_os/lexicon/nrc_emotion_lexicon.txt"),
            # repo-root lexicons/ directory (user-provided attachment)
            Path(__file__).parent.parent.parent / "lexicons" / "nrc_emotion_lexicon.txt",
            Path("lexicons/nrc_emotion_lexicon.txt"),
        ]

        found = None
        for p in possible:
            if p.exists():
                found = p
                break

        if found:
            try:
                if found.suffix == ".json":
                    import json

                    with open(found, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    # Accept either {word: [emotions]} or {"lexicon": {word: [emotions]}}
                    if isinstance(data, dict) and "lexicon" in data:
                        self.lexicon = {k.lower(): v for k, v in data["lexicon"].items()}
                    else:
                        self.lexicon = {k.lower(): v for k, v in data.items()}
                else:
                    # TSV loader: word \t emotion \t value (1 means associated)
                    with open(found, "r", encoding="utf-8") as f:
                        for line in f:
                            parts = line.strip().split("\t")
                            if len(parts) != 3:
                                continue
                            word, emotion, value = parts
                            if value.strip() != "1":
                                continue
                            word = word.lower()
                            self.lexicon.setdefault(word, [])
                            if emotion not in self.lexicon[word]:
                                self.lexicon[word].append(emotion)

                if self.lexicon:
                    self.loaded = True
            except Exception:
                # Fall through to fallback behavior
                self.lexicon = {}
                self.loaded = False

        # Lightweight fallback: a few high-signal keywords mapped to emotions.
        if not self.lexicon:
            self.lexicon = {
                "happy": ["joy", "positive"],
                "joy": ["joy", "positive"],
                "sad": ["sadness", "negative"],
                "sadness": ["sadness", "negative"],
                "angry": ["anger", "negative"],
                "fear": ["fear", "negative"],
                "surprised": ["surprise"],
                "disgusted": ["disgust"],
                "love": ["joy", "positive", "trust"],
                "hate": ["anger", "negative"],
            }
            # Even when using fallback, mark loaded True so callers can use analyze_text
            self.loaded = True

    def analyze_text(self, text: str) -> Dict[str, float]:
        import re
        from collections import Counter

        words = re.findall(r"\b\w+\b", text.lower())
        counts = Counter()
        total = 0
        for w in words:
            emotions = self.lexicon.get(w)
            if emotions:
                total += 1
                for e in emotions:
                    counts[e] += 1

        if total == 0:
            return {}

        return {k: v / total for k, v in counts.items()}


# Export singleton for compatibility
nrc = NRC()
"""
NRC Emotion Lexicon Loader

Loads the NRC (National Research Council) Emotion Lexicon from a TSV file.
Format: word \t emotion \t value (binary: 0 or 1)

The lexicon maps words to 10 emotion/sentiment dimensions:
- anger, anticipation, disgust, fear, joy, negative, positive, sadness, surprise, trust
"""

import os
from pathlib import Path
from typing import Dict, List, Set, Optional
from functools import lru_cache

# Try to find the NRC lexicon file from multiple possible locations
_NRC_POSSIBLE_PATHS = [
    "data/lexicons/nrc_emotion_lexicon.txt",
    "data/lexicons/nrc_lexicon_cleaned.json",
    "emotional_os/lexicon/nrc_emotion_lexicon.txt",
    Path(__file__).parent.parent.parent / "data" / "lexicons" / "nrc_emotion_lexicon.txt",
    Path(__file__).parent.parent.parent / "data" / "lexicons" / "nrc_lexicon_cleaned.json",
    Path(__file__).parent.parent.parent / "lexicons" / "nrc_emotion_lexicon.txt",
    Path("lexicons/nrc_emotion_lexicon.txt"),
    # Legacy velinor path (some projects store the lexicon under velinor/data)
]

class NRCLexicon:
    """Load and query NRC Emotion Lexicon"""
    
    def __init__(self, lexicon_path: Optional[str] = None):
        """Initialize NRC lexicon from file
        
        Args:
            lexicon_path: Path to NRC lexicon file. If None, searches default locations.
        """
        self.lexicon_path = lexicon_path
        self.lexicon: Dict[str, Dict[str, int]] = {}
        self.word_emotions: Dict[str, List[str]] = {}
        # Indicates whether the lexicon loaded successfully and contains entries
        self.loaded: bool = False
        self._load_lexicon()
    
    def _find_lexicon_file(self) -> Optional[str]:
        """Find NRC lexicon file from possible locations"""
        # Try using PathManager first for consistent resolution
        try:
            from emotional_os.core.paths import get_path_manager
            pm = get_path_manager()
            nrc_path = pm.nrc_lexicon()
            if nrc_path.exists():
                return str(nrc_path)
        except Exception:
            pass
        
        # Fall back to legacy path search
        for path in _NRC_POSSIBLE_PATHS:
            if isinstance(path, str):
                path = Path(path)
            if path.exists():
                return str(path)
        return None
    
    def _load_lexicon(self) -> None:
        """Load NRC lexicon from TSV or JSON file"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Determine which file to load
            lexicon_file = self.lexicon_path or self._find_lexicon_file()
            
            if not lexicon_file:
                logger.warning(
                    "NRC lexicon file not found. Searched: "
                    + ", ".join(str(p) for p in _NRC_POSSIBLE_PATHS)
                )
                self.lexicon = {}
                self.word_emotions = {}
                return
            
            lexicon_file = Path(lexicon_file)
            logger.debug(f"Loading NRC lexicon from: {lexicon_file}")
            
            if lexicon_file.suffix == ".json":
                self._load_json(lexicon_file)
            else:
                self._load_tsv(lexicon_file)
                
            if self.lexicon:
                logger.debug(f"NRC lexicon loaded successfully: {len(self.lexicon)} words")
                self.loaded = True
            else:
                logger.warning(f"NRC lexicon loaded but is empty: {lexicon_file}")
                self.loaded = False
                
        except Exception as e:
            logger.debug(f"Failed to load NRC lexicon: {e}")
            self.lexicon = {}
            self.word_emotions = {}
    
    def _load_tsv(self, filepath: Path) -> None:
        """Load NRC lexicon from TSV format
        
        Format: word \t emotion \t value (0 or 1)
        Only includes entries where value = 1
        """
        self.lexicon = {}
        self.word_emotions = {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split('\t')
                    if len(parts) != 3:
                        continue
                    
                    word, emotion, value = parts
                    value = int(value)
                    
                    # Only include entries marked as 1 (has this emotion)
                    if value == 1:
                        if word not in self.lexicon:
                            self.lexicon[word] = {}
                        self.lexicon[word][emotion] = value
                        
                        # Also track word -> emotions mapping for quick lookup
                        if word not in self.word_emotions:
                            self.word_emotions[word] = []
                        if emotion not in self.word_emotions[word]:
                            self.word_emotions[word].append(emotion)
            
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"NRC Lexicon loaded: {len(self.lexicon)} words")
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error loading NRC TSV lexicon: {e}")
            raise
    
    def _load_json(self, filepath: Path) -> None:
        """Load NRC lexicon from JSON format"""
        import json
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.lexicon = data.get("lexicon", {})
        self.word_emotions = data.get("word_emotions", {})
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"NRC Lexicon loaded from JSON: {len(self.lexicon)} words")
    
    def get_emotions(self, word: str) -> List[str]:
        """Get list of emotions associated with a word"""
        return self.word_emotions.get(word.lower(), [])
    
    def get_emotion_values(self, word: str) -> Dict[str, int]:
        """Get all emotion values for a word"""
        return self.lexicon.get(word.lower(), {})
    
    def has_emotion(self, word: str, emotion: str) -> bool:
        """Check if word has a specific emotion"""
        return emotion in self.word_emotions.get(word.lower(), [])
    
    def find_words_with_emotion(self, emotion: str) -> List[str]:
        """Find all words that have a specific emotion"""
        result = []
        for word, emotions in self.word_emotions.items():
            if emotion in emotions:
                result.append(word)
        return result
    
    def get_emotion_score(self, text: str) -> Dict[str, float]:
        """Calculate emotion scores for a text
        
        Counts occurrences of words associated with each emotion.
        Returns normalized scores (0.0 - 1.0) for each emotion.
        """
        import re
        from collections import Counter
        
        # Tokenize text into words
        words = re.findall(r'\b\w+\b', text.lower())
        
        emotion_counts = Counter()
        found_emotional_words = 0
        
        for word in words:
            emotions = self.get_emotions(word)
            if emotions:
                found_emotional_words += 1
                for emotion in emotions:
                    emotion_counts[emotion] += 1
        
        # Normalize scores
        if found_emotional_words == 0:
            return {}
        
        return {
            emotion: count / found_emotional_words 
            for emotion, count in emotion_counts.items()
        }

    def analyze_text(self, text: str) -> Dict[str, float]:
        """Compatibility wrapper expected by other modules: returns emotion scores for text."""
        return self.get_emotion_score(text)


# Global NRC lexicon instance (lazy-loaded)
_nrc_instance: Optional[NRCLexicon] = None

def get_nrc() -> NRCLexicon:
    """Get the global NRC lexicon instance (lazy-loaded)"""
    global _nrc_instance
    if _nrc_instance is None:
        _nrc_instance = NRCLexicon()
    return _nrc_instance


# Export the global instance for backward compatibility
nrc = get_nrc()
