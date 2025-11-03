"""
Poetry-Aware Signal Extraction

Extracts emotional signals and themes from poetry and creative writing.
Handles metaphorical language, imagery, and emotional subtext.
"""

import re
from typing import Dict, List, Optional, Tuple

class PoetrySignalExtractor:
    """Extract emotional signals from poetic and creative content."""
    
    # Poetry-specific emotional keywords and themes
    POETIC_SIGNALS = {
        "love": {
            "keywords": ["love", "beloved", "darling", "sweet", "tender", "caress", "embrace", "nestled", "breast", "devoted"],
            "metaphors": ["bird", "nest", "stork", "paradise", "muse"],
            "intensity": 0.9
        },
        "intimacy": {
            "keywords": ["touch", "skin", "body", "bed", "flesh", "breast", "thigh", "wrapped", "friction", "caught", "nestled", "scoop", "flap"],
            "metaphors": ["nest", "buffet", "ladder", "climb", "deliver", "drop"],
            "intensity": 0.85
        },
        "vulnerability": {
            "keywords": ["blind", "fumbling", "bumbling", "sorry", "mistake", "broken", "swept", "caught", "drop"],
            "metaphors": ["lost", "darkness", "uncertain", "can't tame", "can't name"],
            "intensity": 0.75
        },
        "transformation": {
            "keywords": ["renewed", "evolved", "evolution", "scalpel", "healing", "growth", "born", "new", "taxonomically"],
            "metaphors": ["wings", "rebirth", "becoming", "bird", "squiggle"],
            "intensity": 0.8
        },
        "admiration": {
            "keywords": ["beautiful", "mythic", "divine", "perfect", "wonder", "amazed", "captivated", "paradise", "native"],
            "metaphors": ["goddess", "enchanted", "magic", "stork", "delivery"],
            "intensity": 0.7
        },
        "joy": {
            "keywords": ["wonderful", "delight", "bliss", "happy", "celebrate", "exhilarating", "paradise", "native"],
            "metaphors": ["soaring", "flight", "dance", "flap", "squiggle"],
            "intensity": 0.8
        },
        "sensuality": {
            "keywords": ["taste", "tongue", "rough", "smooth", "texture", "feel", "bristles", "probes", "lick", "flap", "squiggle"],
            "metaphors": ["crickets", "friction", "tenderized", "tongue", "tasting"],
            "intensity": 0.75
        },
        "nature": {
            "keywords": ["raven", "bird", "stork", "hawk", "bat", "gull", "wing", "nest", "flight"],
            "metaphors": ["sky", "wind", "wild"],
            "intensity": 0.6
        }
    }
    
    def extract_signals(self, text: str) -> List[Dict]:
        """Extract emotional signals from poetic text.
        
        Args:
            text: Poetry or creative writing
            
        Returns:
            List of detected signals with confidence scores
        """
        if not text or len(text.strip()) < 10:
            return []
        
        text_lower = text.lower()
        detected_signals = []
        
        for signal_name, signal_data in self.POETIC_SIGNALS.items():
            confidence = self._calculate_signal_confidence(
                text_lower,
                signal_data["keywords"],
                signal_data["metaphors"],
                signal_data["intensity"]
            )
            
            if confidence > 0.3:  # Threshold for detection
                detected_signals.append({
                    "signal": signal_name,
                    "confidence": confidence,
                    "keywords": self._find_matching_keywords(text_lower, signal_data["keywords"]),
                    "keyword": signal_name,  # For compatibility with existing system
                })
        
        # Sort by confidence
        detected_signals.sort(key=lambda x: x["confidence"], reverse=True)
        return detected_signals
    
    def _calculate_signal_confidence(
        self,
        text: str,
        keywords: List[str],
        metaphors: List[str],
        base_intensity: float
    ) -> float:
        """Calculate confidence score for a signal."""
        confidence = 0.0
        
        # Count keyword matches
        keyword_count = sum(1 for kw in keywords if kw in text)
        keyword_score = min(keyword_count * 0.15, 0.5)  # Cap at 0.5
        
        # Count metaphor matches
        metaphor_count = sum(1 for m in metaphors if m in text)
        metaphor_score = min(metaphor_count * 0.1, 0.3)  # Cap at 0.3
        
        confidence = (keyword_score + metaphor_score) * base_intensity
        return min(confidence, 1.0)  # Cap at 1.0
    
    def _find_matching_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Find which keywords are present in the text."""
        return [kw for kw in keywords if kw in text]
    
    def extract_themes(self, text: str) -> Dict[str, float]:
        """Extract broader emotional themes from text.
        
        Returns:
            Dict mapping theme names to their presence scores
        """
        signals = self.extract_signals(text)
        themes = {}
        
        for signal in signals:
            themes[signal["signal"]] = signal["confidence"]
        
        return themes


# Singleton
_poetry_extractor = None

def get_poetry_extractor() -> PoetrySignalExtractor:
    """Get or create the poetry signal extractor."""
    global _poetry_extractor
    if _poetry_extractor is None:
        _poetry_extractor = PoetrySignalExtractor()
    return _poetry_extractor
