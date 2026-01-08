"""
Lexicon Loader: Unified interface for word-centric emotional lexicon

Provides quick lookups for emotional words with their signal mappings,
gate activations, and frequencies from the cleaned transcript.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from functools import lru_cache


class WordCentricLexicon:
    """Load and query the word-centric emotional lexicon"""
    
    def __init__(self, lexicon_path: str = "emotional_os/lexicon/word_centric_emotional_lexicon_expanded.json"):
        """Initialize lexicon from JSON file"""
        self.lexicon_path = lexicon_path
        self.lexicon: Dict[str, Dict[str, Any]] = {}
        self.metadata: Dict[str, Any] = {}
        self.signal_map: Dict[str, List[int]] = {}
        self._load_lexicon()
    
    def _load_lexicon(self) -> None:
        """Load the word-centric lexicon from file"""
        try:
            with open(self.lexicon_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.metadata = data.get('metadata', {})
            self.lexicon = data.get('lexicon', {})
            self.signal_map = data.get('signal_map', {})
            
            print(f"[OK] Loaded word-centric lexicon: {len(self.lexicon)} words")
        except FileNotFoundError:
            print(f"[X] Lexicon not found at {self.lexicon_path}")
            self.lexicon = {}
            self.metadata = {}
            self.signal_map = {}
    
    def get_word_data(self, word: str) -> Optional[Dict[str, Any]]:
        """Get all data for a specific word"""
        return self.lexicon.get(word.lower())
    
    def get_signals(self, word: str) -> List[str]:
        """Get emotional signals triggered by a word"""
        data = self.get_word_data(word)
        return data.get('signals', []) if data else []
    
    def get_gates(self, word: str) -> List[int]:
        """Get gate activation pattern for a word"""
        data = self.get_word_data(word)
        return data.get('gates', []) if data else []
    
    def get_frequency(self, word: str) -> int:
        """Get frequency of word in transcript"""
        data = self.get_word_data(word)
        return data.get('frequency', 0) if data else 0
    
    def find_emotional_words(self, text: str) -> Dict[str, Dict[str, Any]]:
        """Find all emotional words in text with their data
        
        Returns dict mapping word -> word_data
        Uses word boundaries to avoid partial matches
        """
        import re
        lower_text = text.lower()
        found = {}
        
        # Check each word in lexicon against text using word boundaries
        for word in self.lexicon:
            pattern = rf'\b{re.escape(word)}\b'
            if re.search(pattern, lower_text):
                found[word] = self.lexicon[word]
        
        return found
    
    def find_emotional_words_with_context(self, text: str) -> List[Tuple[str, Dict[str, Any], int]]:
        """Find emotional words with their position in text
        
        Returns list of (word, word_data, position) tuples
        Uses word boundaries to avoid partial matches
        """
        import re
        lower_text = text.lower()
        found = []
        
        for word in sorted(self.lexicon.keys(), key=len, reverse=True):  # Longest first
            # Use word boundary regex to find exact word matches
            pattern = rf'\b{re.escape(word)}\b'
            for match in re.finditer(pattern, lower_text):
                pos = match.start()
                found.append((word, self.lexicon[word], pos))
        
        # Sort by position, then by length (longest first for overlaps)
        return sorted(found, key=lambda x: (x[2], -len(x[0])))
    
    def get_top_emotional_words(self, n: int = 20) -> List[Tuple[str, int]]:
        """Get the top N most frequent emotional words"""
        sorted_words = sorted(
            self.lexicon.items(),
            key=lambda x: x[1].get('frequency', 0),
            reverse=True
        )
        return [(word, data['frequency']) for word, data in sorted_words[:n]]
    
    def words_for_signal(self, signal_name: str) -> List[str]:
        """Get all words that trigger a specific signal"""
        return [
            word for word, data in self.lexicon.items()
            if signal_name in data.get('signals', [])
        ]
    
    def words_for_gates(self, gate_numbers: List[int]) -> List[str]:
        """Get all words that activate specific gates"""
        return [
            word for word, data in self.lexicon.items()
            if any(g in data.get('gates', []) for g in gate_numbers)
        ]
    
    def analyze_emotional_content(self, text: str) -> Dict[str, Any]:
        """Analyze emotional content of text
        
        Returns comprehensive analysis including:
        - emotional_words: found words with frequencies
        - primary_signals: most active signals
        - gate_activations: gate patterns activated
        - intensity: estimated emotional intensity (0-1)
        - sources: primary emotional dimensions
        """
        emotional_words = self.find_emotional_words_with_context(text)
        
        if not emotional_words:
            return {
                'emotional_words': [],
                'primary_signals': [],
                'gate_activations': [],
                'intensity': 0.0,
                'sources': [],
                'has_emotional_content': False,
            }
        
        # Aggregate signals and gates
        all_signals = []
        all_gates = []
        total_frequency = 0
        
        for word, word_data, _ in emotional_words:
            signals = word_data.get('signals', [])
            gates = word_data.get('gates', [])
            freq = word_data.get('frequency', 0)
            
            all_signals.extend(signals)
            all_gates.extend(gates)
            total_frequency += freq
        
        # Count signal activations
        signal_counts = {}
        for sig in all_signals:
            signal_counts[sig] = signal_counts.get(sig, 0) + 1
        
        # Count gate activations
        gate_counts = {}
        for gate in all_gates:
            gate_counts[gate] = gate_counts.get(gate, 0) + 1
        
        # Calculate intensity (based on frequency and signal count)
        intensity = min(1.0, (total_frequency / 1000.0) + (len(all_signals) / 10.0))
        
        return {
            'emotional_words': [
                {
                    'word': w,
                    'frequency': wd['frequency'],
                    'signals': wd['signals'],
                    'gates': wd['gates'],
                }
                for w, wd, _ in emotional_words
            ],
            'primary_signals': sorted(
                signal_counts.items(),
                key=lambda x: x[1],
                reverse=True
            ),
            'gate_activations': sorted(
                gate_counts.items(),
                key=lambda x: x[1],
                reverse=True
            ),
            'intensity': intensity,
            'sources': list(signal_counts.keys()),
            'has_emotional_content': len(emotional_words) > 0,
            'word_count': len(emotional_words),
        }


# Global instance
_lexicon_instance: Optional[WordCentricLexicon] = None


def get_lexicon() -> WordCentricLexicon:
    """Get or create the global lexicon instance"""
    global _lexicon_instance
    if _lexicon_instance is None:
        _lexicon_instance = WordCentricLexicon()
    return _lexicon_instance


def load_lexicon(path: str) -> WordCentricLexicon:
    """Load lexicon from custom path"""
    return WordCentricLexicon(path)
