"""
Adaptive Signal Extractor with Dynamic Dimension Discovery

Starts with base emotional dimensions derived from your poem, but
dynamically discovers and learns new emotional dimensions from
the poetry corpus being processed.

This allows the system to:
1. Preserve your core 8 dimensions (love, intimacy, etc.)
2. Discover new dimensions like: nostalgia, melancholy, transcendence, longing, etc.
3. Learn keywords and patterns specific to each poet/collection
4. Adapt the signal extraction as it processes more poetry
"""

import json
import re
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path
from collections import defaultdict


class AdaptiveSignalExtractor:
    """Extract emotional signals with dynamic dimension discovery."""

    # Your original 8 base dimensions (preserved as foundation)
    BASE_SIGNALS = {
        "love": {
            "keywords": ["love", "beloved", "darling", "sweet", "tender", "caress", "embrace", "nestled", "breast", "devoted", "heart", "soul", "forever"],
            "metaphors": ["bird", "nest", "stork", "paradise", "muse", "feathers", "perches"],
            "intensity": 0.9
        },
        "intimacy": {
            "keywords": ["touch", "skin", "body", "bed", "flesh", "breast", "thigh", "wrapped", "friction", "caught", "nestled"],
            "metaphors": ["nest", "buffet", "ladder", "climb", "deliver", "drop"],
            "intensity": 0.85
        },
        "vulnerability": {
            "keywords": ["blind", "fumbling", "bumbling", "sorry", "mistake", "broken", "swept", "caught", "drop", "sense", "madness", "dangerous"],
            "metaphors": ["lost", "darkness", "uncertain", "funeral", "mourners"],
            "intensity": 0.75
        },
        "transformation": {
            "keywords": ["renewed", "evolved", "evolution", "scalpel", "healing", "growth", "born", "new", "becoming", "change"],
            "metaphors": ["wings", "rebirth", "becoming", "bird", "breaking", "beating"],
            "intensity": 0.8
        },
        "admiration": {
            "keywords": ["beautiful", "mythic", "divine", "perfect", "wonder", "amazed", "captivated", "paradise", "exquisite", "profound"],
            "metaphors": ["goddess", "enchanted", "magic", "stork", "delivery", "glory"],
            "intensity": 0.7
        },
        "joy": {
            "keywords": ["wonderful", "delight", "bliss", "happy", "celebrate", "exhilarating", "sings", "sweetest", "hope"],
            "metaphors": ["soaring", "flight", "dance", "flap", "sunshine", "gale"],
            "intensity": 0.8
        },
        "sensuality": {
            "keywords": ["taste", "tongue", "rough", "smooth", "texture", "feel", "bristles", "probes", "lick", "drum"],
            "metaphors": ["crickets", "friction", "tenderized", "tongue", "tasting", "music", "melody"],
            "intensity": 0.75
        },
        "nature": {
            "keywords": ["raven", "bird", "stork", "hawk", "bat", "gull", "wing", "nest", "flight", "feathers", "perches", "gale", "storm"],
            "metaphors": ["sky", "wind", "wild", "soul", "brain", "sense"],
            "intensity": 0.6
        }
    }

    # Common emotional dimensions discovered in poetry (optional additions)
    DISCOVERED_SIGNALS = {
        "nostalgia": {
            "keywords": ["remember", "memory", "once", "past", "ancient", "long ago", "days of old", "when", "used to", "forgotten", "lost time"],
            "metaphors": ["echo", "shadow", "ghost", "fading", "twilight", "autumn"],
            "intensity": 0.7
        },
        "melancholy": {
            "keywords": ["sad", "sorrow", "weep", "tears", "lament", "mourn", "gray", "bleak", "desolate", "forlorn", "despair"],
            "metaphors": ["rain", "winter", "death", "darkness", "void", "abyss"],
            "intensity": 0.8
        },
        "transcendence": {
            "keywords": ["eternal", "infinite", "divine", "sublime", "sacred", "spirit", "soul", "awakening", "enlightenment", "ascend"],
            "metaphors": ["heaven", "light", "sky", "cosmos", "transcendent", "beyond"],
            "intensity": 0.85
        },
        "longing": {
            "keywords": ["yearning", "desire", "want", "need", "long for", "ache", "hunger", "thirst", "reach", "pursue", "seek"],
            "metaphors": ["reaching", "distance", "ocean", "unreachable", "mirage"],
            "intensity": 0.75
        },
        "despair": {
            "keywords": ["hopeless", "lost", "forsaken", "abandoned", "void", "emptiness", "meaningless", "numb", "hollow", "dying"],
            "metaphors": ["abyss", "void", "extinction", "drowning", "suffocation"],
            "intensity": 0.9
        },
        "serenity": {
            "keywords": ["peace", "calm", "still", "quiet", "silence", "tranquil", "serene", "restful", "gentle", "soothe"],
            "metaphors": ["stillness", "lake", "dawn", "breath", "sanctuary"],
            "intensity": 0.7
        },
        "rebellion": {
            "keywords": ["rebel", "resist", "defy", "break free", "rage", "fierce", "untamed", "wild", "destroy", "revolution"],
            "metaphors": ["fire", "storm", "breaking chains", "thunder", "wildfire"],
            "intensity": 0.85
        },
        "wonder": {
            "keywords": ["amazed", "astonished", "bewildered", "curious", "fascinated", "awe", "marvel", "strange", "mysterious", "unknown"],
            "metaphors": ["magic", "discovery", "enchantment", "mystery", "labyrinth"],
            "intensity": 0.75
        },
        "resilience": {
            "keywords": ["strength", "endure", "persist", "overcome", "survive", "persist", "unbroken", "rising", "standing firm"],
            "metaphors": ["stone", "oak", "mountain", "phoenix", "rising tide"],
            "intensity": 0.8
        },
        "solitude": {
            "keywords": ["alone", "lonely", "isolated", "singular", "separate", "withdrawn", "remote", "solitary", "apart"],
            "metaphors": ["island", "wilderness", "silent", "edge of world", "alone on mountain"],
            "intensity": 0.7
        }
    }

    def __init__(self, adaptive: bool = True, use_discovered: bool = True, persistence_path: str = None, **kwargs):
        """Initialize the adaptive extractor.

        Args:
            adaptive: If True, learns new dimensions as processing
            use_discovered: If True, includes pre-discovered dimensions
        """
        # Backwards-compatible: accept persistence_path kwarg if callers pass it
        self.adaptive = adaptive
        self.persistence_path = persistence_path
        self.signals = self.BASE_SIGNALS.copy()

        if use_discovered:
            self.signals.update(self.DISCOVERED_SIGNALS)

        # Track new dimensions discovered during processing
        self.learned_dimensions: Dict[str, Dict] = {}
        self.keyword_frequency: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int))

        # If a persistence path was provided, attempt to load previously
        # learned dimensions so runtime callers that pass a persistence
        # argument remain compatible with older code.
        if self.persistence_path:
            try:
                p = Path(self.persistence_path)
                if p.exists():
                    with open(p, 'r', encoding='utf-8') as fh:
                        data = json.load(fh)
                        if isinstance(data, dict):
                            # Merge into learned_dimensions
                            self.learned_dimensions.update(data)
            except Exception:
                # Non-fatal: if loading fails continue with empty learned_dimensions
                pass

    def extract_signals(self, text: str, chunk_id: Optional[str] = None) -> List[Dict]:
        """Extract emotional signals from text with dimension discovery.

        Args:
            text: The text to extract signals from
            chunk_id: Optional identifier for tracking origin

        Returns:
            List of detected signals with confidence scores
        """
        signals = []
        text_lower = text.lower()

        # Check against all known signals (base + discovered + learned)
        all_signals = {**self.signals, **self.learned_dimensions}

        for signal_name, signal_config in all_signals.items():
            keywords = signal_config.get("keywords", [])
            metaphors = signal_config.get("metaphors", [])
            base_intensity = signal_config.get("intensity", 0.7)

            # Check for keywords
            keyword_matches = sum(1 for kw in keywords if kw in text_lower)
            metaphor_matches = sum(1 for m in metaphors if m in text_lower)

            if keyword_matches > 0 or metaphor_matches > 0:
                # Calculate confidence based on match frequency
                total_matches = keyword_matches + \
                    (metaphor_matches * 0.7)  # Metaphors weighted less
                confidence = min(0.95, base_intensity + (total_matches * 0.05))

                signals.append({
                    "signal": signal_name,
                    "confidence": confidence,
                    "keyword_matches": keyword_matches,
                    "metaphor_matches": metaphor_matches,
                    "matched_keywords": [kw for kw in keywords if kw in text_lower],
                    "matched_metaphors": [m for m in metaphors if m in text_lower],
                })

                # Track for learning
                for kw in keywords:
                    if kw in text_lower:
                        self.keyword_frequency[signal_name][kw] += 1

        # Sort by confidence
        signals = sorted(signals, key=lambda x: x["confidence"], reverse=True)

        return signals

    def discover_new_dimensions_from_corpus(self, texts: List[str]) -> Dict[str, Dict]:
        """Discover new emotional dimensions from a corpus of texts.

        Analyzes patterns across multiple texts to identify recurring
        emotional themes not captured by existing dimensions.

        Args:
            texts: List of text chunks to analyze

        Returns:
            Dictionary of newly discovered dimensions
        """
        if not self.adaptive:
            return {}

        new_dimensions = {}

        # Look for common thematic words across texts
        word_frequency = defaultdict(int)
        word_contexts = defaultdict(list)

        emotional_keywords = [
            # Emotions related to time
            "time", "before", "after", "when", "then", "now", "eternal", "moment",
            # Emotions related to absence
            "absence", "missing", "gone", "lost", "forgotten", "fading",
            # Emotions related to connection
            "together", "apart", "union", "separation", "bond", "distance",
            # Emotions related to struggle
            "struggle", "fight", "resist", "persist", "endure", "survive",
            # Emotions related to depth
            "deep", "profound", "surface", "beneath", "hidden", "revealed",
            # Emotions related to seasons
            "spring", "summer", "autumn", "winter", "season", "cycle",
        ]

        for text in texts:
            text_lower = text.lower()
            for keyword in emotional_keywords:
                if keyword in text_lower:
                    word_frequency[keyword] += 1
                    # Extract surrounding context (20 chars before/after)
                    matches = re.finditer(rf'\b{keyword}\b', text_lower)
                    for match in matches:
                        start = max(0, match.start() - 20)
                        end = min(len(text), match.end() + 20)
                        context = text[start:end].strip()
                        word_contexts[keyword].append(context)

        # Identify frequently occurring keywords that might indicate new dimensions
        for keyword, frequency in word_frequency.items():
            if frequency >= len(texts) * 0.3:  # Appears in 30%+ of texts
                # This might be a dimension
                related_keywords = self._find_related_keywords(
                    keyword, word_contexts)

                if len(related_keywords) >= 3:  # Need at least 3 related keywords
                    new_dim_name = self._generate_dimension_name(
                        keyword, related_keywords)
                    if new_dim_name not in self.signals and new_dim_name not in new_dimensions:
                        new_dimensions[new_dim_name] = {
                            "keywords": [keyword] + related_keywords[:5],
                            "metaphors": [],  # Will be filled in with more processing
                            "intensity": 0.7,
                            "discovered": True,
                            "source_keyword": keyword,
                            "frequency": frequency
                        }

        # Add discovered dimensions to learned dimensions
        self.learned_dimensions.update(new_dimensions)

        # Persist learned dimensions if a persistence path was provided
        if self.persistence_path and new_dimensions:
            try:
                p = Path(self.persistence_path)
                p.parent.mkdir(parents=True, exist_ok=True)
                with open(p, 'w', encoding='utf-8') as fh:
                    json.dump(self.learned_dimensions, fh, indent=2)
            except Exception:
                # Non-fatal: ignore persistence failures
                pass

        return new_dimensions

    def _find_related_keywords(self, keyword: str, contexts: Dict[str, List[str]]) -> List[str]:
        """Find keywords semantically related to a given keyword."""
        related = []

        if keyword in contexts:
            all_words = set()
            for context in contexts[keyword]:
                words = re.findall(r'\b\w+\b', context.lower())
                all_words.update(words)

            # Remove common stop words and the keyword itself
            stop_words = {"the", "a", "an", "and", "or", "but",
                          "in", "of", "to", "for", "is", "was", "are"}
            related = [
                w for w in all_words if w not in stop_words and w != keyword]

        return related[:5]

    def _generate_dimension_name(self, keyword: str, related: List[str]) -> str:
        """Generate a name for a newly discovered dimension."""
        # Simple heuristic: use keyword or combine with most related word
        if len(related) > 0:
            # Create a compound name from keyword and most common related word
            name = f"{keyword}_{related[0]}"
        else:
            name = keyword

        # Make it a single word
        return name.replace(" ", "_").lower()

    def get_all_dimensions(self) -> Dict[str, int]:
        """Get count of all available dimensions (base + discovered + learned)."""
        base_count = len(self.BASE_SIGNALS)
        discovered_count = len(self.DISCOVERED_SIGNALS)
        learned_count = len(self.learned_dimensions)

        return {
            "base": base_count,
            "discovered": discovered_count,
            "learned": learned_count,
            "total": base_count + discovered_count + learned_count
        }

    def export_learned_dimensions(self, output_path: str) -> None:
        """Export newly learned dimensions to JSON file."""
        with open(output_path, 'w') as f:
            json.dump(self.learned_dimensions, f, indent=2)

    def get_dimension_report(self) -> Dict:
        """Generate report of all available dimensions and their coverage."""
        counts = self.get_all_dimensions()

        report = {
            "total_dimensions": counts["total"],
            "breakdown": {
                "base_dimensions": counts["base"],
                "pre_discovered_dimensions": counts["discovered"],
                "newly_learned_dimensions": counts["learned"]
            },
            "base_signals": list(self.BASE_SIGNALS.keys()),
            "discovered_signals": list(self.DISCOVERED_SIGNALS.keys()),
            "learned_signals": list(self.learned_dimensions.keys()),
            "keyword_statistics": {
                dim: len(kw_dict)
                for dim, kw_dict in self.keyword_frequency.items()
            }
        }

        return report
