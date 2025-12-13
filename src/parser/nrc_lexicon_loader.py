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
            else:
                logger.warning(f"NRC lexicon loaded but is empty: {lexicon_file}")
                
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
