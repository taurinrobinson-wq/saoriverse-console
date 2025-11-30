#!/usr/bin/env python3
"""
Glyph Generator from Extracted Poetry Data

Creates new glyphs based on emotional patterns discovered during
Project Gutenberg poetry processing. Uses the extracted signals and
learned lexicons to generate meaningful emotional symbols (glyphs).

Usage:
    python glyph_generator_from_extracted_data.py --use-cached
    python glyph_generator_from_extracted_data.py --regenerate
"""

import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

sys.path.insert(0, str(Path(__file__).parent))

# Import glyph generation tools
try:
    from emotional_os.glyphs.glyph_generator import GlyphGenerator, NewGlyph
except ImportError:
    print("Warning: GlyphGenerator not available, using simplified version")
    NewGlyph = None


@dataclass
class EmotionalPattern:
    """Represents a discovered emotional pattern from poetry."""

    dimensions: List[str]  # e.g., ["love", "transformation", "vulnerability"]
    keywords: List[str]  # e.g., ["forever", "bloom", "heart"]
    frequency: int  # How many times this pattern appeared
    example_context: str  # A sample phrase from the poetry
    poet_sources: List[str]  # Which poets contributed this pattern

    def __hash__(self):
        return hash(tuple(sorted(self.dimensions)))

    def __eq__(self, other):
        return sorted(self.dimensions) == sorted(other.dimensions)


class GlyphFromDataExtractor:
    """Extract and generate glyphs from processed poetry data."""

    def __init__(self, lexicon_path: str = "learning/user_overrides/gutenberg_bulk_lexicon.json"):
        """Initialize with processed lexicon data."""
        self.lexicon_path = Path(lexicon_path)
        self.lexicon = None
        self.patterns: Set[EmotionalPattern] = set()
        self.glyph_generator = GlyphGenerator() if NewGlyph else None
        self.generated_glyphs: List[Dict] = []

        if self.lexicon_path.exists():
            self._load_lexicon()

    def _load_lexicon(self):
        """Load the processed lexicon."""
        try:
            with open(self.lexicon_path, "r") as f:
                self.lexicon = json.load(f)
            print(f"✓ Loaded lexicon from {self.lexicon_path}")
            print(f"  - Signals: {len(self.lexicon.get('signals', {}))}")
        except Exception as e:
            print(f"✗ Failed to load lexicon: {e}")
            self.lexicon = {}

    def extract_patterns(self) -> List[EmotionalPattern]:
        """Extract emotional patterns from the lexicon."""
        if not self.lexicon:
            print("✗ No lexicon data available")
            return []

        patterns = []
        signals = self.lexicon.get("signals", {})

        # Get all signal dimensions
        dimensions = list(signals.keys())
        print(f"\n[PATTERN EXTRACTION]")
        print(f"Found {len(dimensions)} emotional dimensions")

        # Create patterns from dimension combinations
        # 2-way combinations (most common)
        for i, dim1 in enumerate(dimensions):
            for dim2 in dimensions[i + 1 :]:
                keywords = self._find_shared_keywords(signals[dim1], signals[dim2])

                if keywords:
                    frequency = sum(signals[dim1].get("frequency", 0), signals[dim2].get("frequency", 0))

                    example = self._get_best_example(dim1, dim2, signals)

                    pattern = EmotionalPattern(
                        dimensions=[dim1, dim2],
                        keywords=keywords[:5],  # Top 5
                        frequency=frequency,
                        example_context=example,
                        poet_sources=[],  # TODO: Track poet sources
                    )
                    patterns.append(pattern)

        # 3-way combinations (rare but powerful)
        for i, dim1 in enumerate(dimensions):
            for j, dim2 in enumerate(dimensions[i + 1 :], i + 1):
                for dim3 in dimensions[j + 1 :]:
                    keywords = self._find_shared_keywords(signals[dim1], signals[dim2], signals[dim3])

                    if keywords and len(keywords) >= 3:
                        frequency = sum(
                            signals[dim1].get("frequency", 0),
                            signals[dim2].get("frequency", 0),
                            signals[dim3].get("frequency", 0),
                        )

                        pattern = EmotionalPattern(
                            dimensions=[dim1, dim2, dim3],
                            keywords=keywords[:3],
                            frequency=frequency,
                            example_context=f"{dim1}+{dim2}+{dim3}",
                            poet_sources=[],
                        )
                        patterns.append(pattern)

        # Filter by frequency (minimum 5 occurrences)
        patterns = [p for p in patterns if p.frequency >= 5]
        patterns.sort(key=lambda p: p.frequency, reverse=True)

        print(f"Extracted {len(patterns)} significant patterns")
        print(f"  Top patterns:")
        for i, p in enumerate(patterns[:5]):
            print(f"    {i+1}. {' + '.join(p.dimensions)} ({p.frequency} freq, {len(p.keywords)} keywords)")

        self.patterns = set(patterns)
        return patterns

    def _find_shared_keywords(self, *signal_dicts) -> List[str]:
        """Find keywords common to multiple signals."""
        if not signal_dicts:
            return []

        # Get keywords from first signal
        first_keywords = set(signal_dicts[0].get("keywords", []))

        # Find intersection with others
        for signal_dict in signal_dicts[1:]:
            keywords = set(signal_dict.get("keywords", []))
            first_keywords &= keywords

        return sorted(list(first_keywords))

    def _get_best_example(self, dim1: str, dim2: str, signals: Dict) -> str:
        """Get a good example phrase for a pattern."""
        examples1 = signals[dim1].get("examples", [])
        examples2 = signals[dim2].get("examples", [])

        if examples1 and examples2:
            # Find shortest example from first, most relevant
            example = min(examples1, key=len)[:100]
            return example
        elif examples1:
            return examples1[0][:100]
        elif examples2:
            return examples2[0][:100]
        else:
            return f"{dim1} + {dim2}"

    def generate_glyphs(self) -> List[Dict]:
        """Generate glyphs from extracted patterns."""
        if not self.patterns:
            print("✗ No patterns available. Run extract_patterns() first.")
            return []

        print(f"\n[GLYPH GENERATION]")
        print(f"Generating glyphs from {len(self.patterns)} patterns...")

        glyphs = []

        for pattern in sorted(self.patterns, key=lambda p: p.frequency, reverse=True)[:30]:
            glyph = self._create_glyph_from_pattern(pattern)
            if glyph:
                glyphs.append(glyph)

        print(f"Generated {len(glyphs)} new glyphs")
        self.generated_glyphs = glyphs
        return glyphs

    def _create_glyph_from_pattern(self, pattern: EmotionalPattern) -> Dict:
        """Create a glyph definition from an emotional pattern."""

        # Generate glyph name from dimensions
        glyph_name = self._create_glyph_name(pattern.dimensions)

        # Create glyph symbol (can be enhanced with actual visual generation)
        symbol = self._create_glyph_symbol(pattern.dimensions)

        # Create response cue
        response_cue = self._create_response_cue(pattern.dimensions, pattern.keywords)

        # Create narrative hook
        narrative = self._create_narrative(pattern.dimensions, pattern.keywords)

        glyph = {
            "id": f"glyph_{glyph_name.lower().replace(' ', '_')}",
            "name": glyph_name,
            "symbol": symbol,
            "core_emotions": pattern.dimensions,
            "associated_keywords": pattern.keywords,
            "frequency": pattern.frequency,
            "response_cue": response_cue,
            "narrative_hook": narrative,
            "example_context": pattern.example_context,
            "source": "gutenberg_poetry_extraction",
            "created_from_pattern": True,
        }

        return glyph

    def _create_glyph_name(self, dimensions: List[str]) -> str:
        """Create a meaningful name from dimensions."""
        # Simple approach: combine dimensions with meaningful connectors
        if len(dimensions) == 2:
            d1, d2 = dimensions
            connectors = {
                ("love", "transformation"): "Becoming Love",
                ("vulnerability", "transformation"): "Metamorphosis",
                ("nature", "joy"): "Natural Bliss",
                ("nature", "transformation"): "Seasonal Wisdom",
                ("love", "vulnerability"): "Open Heart",
                ("transformation", "admiration"): "Inspiring Change",
                ("nature", "solitude"): "Wild Solitude",
                ("love", "joy"): "Celebration",
                ("melancholy", "nostalgia"): "Bittersweet Memory",
                ("despair", "transcendence"): "Dark Ascension",
                ("longing", "love"): "Yearning Heart",
                ("rebellion", "transformation"): "Revolutionary Spirit",
                ("wonder", "admiration"): "Awestruck",
                ("serenity", "nature"): "Peaceful Sanctuary",
                ("resilience", "transformation"): "Phoenix Rising",
            }

            key = tuple(sorted([d1, d2]))
            reverse_key = (d2, d1)

            if key in connectors:
                return connectors[key]
            elif reverse_key in connectors:
                return connectors[reverse_key]
            else:
                # Fallback: capitalize and join
                return f"{d1.title()} & {d2.title()}"

        elif len(dimensions) == 3:
            # Three dimensions = powerful combination
            return f"Trinity of {', '.join([d.title() for d in dimensions[:2]])}"

        else:
            return " & ".join([d.title() for d in dimensions])

    def _create_glyph_symbol(self, dimensions: List[str]) -> str:
        """Create a visual symbol representation."""
        # Map emotions to Unicode symbols
        emotion_symbols = {
            "love": "♥",
            "intimacy": "❤",
            "vulnerability": "🌱",
            "transformation": "🦋",
            "admiration": "⭐",
            "joy": "☀",
            "sensuality": "🌹",
            "nature": "🌿",
            "melancholy": "🌙",
            "nostalgia": "⌛",
            "transcendence": "✨",
            "longing": "➡",
            "despair": "⚰",
            "serenity": "🍃",
            "rebellion": "⚡",
            "wonder": "🔮",
            "resilience": "💪",
            "solitude": "🏔",
        }

        symbols = [emotion_symbols.get(d, "◆") for d in dimensions]
        return "".join(symbols)

    def _create_response_cue(self, dimensions: List[str], keywords: List[str]) -> str:
        """Create a response cue for the glyph."""

        cues = {
            ("love", "transformation"): "Honor the courage it takes to open one's heart through change",
            ("vulnerability", "transformation"): "Witness the beauty of becoming",
            ("nature", "joy"): "Celebrate the presence of natural beauty",
            ("love", "vulnerability"): "Acknowledge the strength in openness",
            ("melancholy", "nostalgia"): "Validate the sweet ache of memory",
            ("transformation", "admiration"): "Appreciate profound personal evolution",
            ("nature", "solitude"): "Respect the restoration found in solitude",
            ("rebellion", "transformation"): "Celebrate the courage to transform",
            ("wonder", "admiration"): "Share in the awe of discovery",
            ("despair", "transcendence"): "Recognize the sacred in suffering",
            ("longing", "love"): "Hold the ache of missing someone beloved",
            ("resilience", "transformation"): "Honor the strength to keep becoming",
        }

        key = tuple(sorted(dimensions))
        reverse_key = tuple(reversed(sorted(dimensions)))

        if key in cues:
            return cues[key]
        elif reverse_key in cues:
            return cues[reverse_key]
        else:
            return f"Acknowledge the {' and '.join(dimensions)} within this moment"

    def _create_narrative(self, dimensions: List[str], keywords: List[str]) -> str:
        """Create a narrative hook."""

        if "love" in dimensions:
            return f"A story of connection through {', '.join(dimensions)}"
        elif "nature" in dimensions:
            return f"The earth teaches us about {', '.join(dimensions)}"
        elif "transformation" in dimensions:
            return f"In the process of becoming {', '.join(dimensions)}"
        else:
            return f"The intersection of {' and '.join(dimensions)}"

    def save_glyphs(self, output_path: str = "generated_glyphs_from_poetry.json"):
        """Save generated glyphs to file."""
        if not self.generated_glyphs:
            print("✗ No glyphs to save")
            return

        output_file = Path(output_path)

        try:
            with open(output_file, "w") as f:
                json.dump(self.generated_glyphs, f, indent=2)
            print(f"\n✓ Saved {len(self.generated_glyphs)} glyphs to {output_file}")
        except Exception as e:
            print(f"✗ Failed to save glyphs: {e}")

    def print_summary(self):
        """Print a summary of generated glyphs."""
        if not self.generated_glyphs:
            print("No glyphs generated yet")
            return

        print("\n[GENERATED GLYPHS SUMMARY]")
        print("=" * 80)

        for i, glyph in enumerate(self.generated_glyphs[:15], 1):
            print(f"\n{i}. {glyph['symbol']} {glyph['name']}")
            print(f"   ID: {glyph['id']}")
            print(f"   Emotions: {', '.join(glyph['core_emotions'])}")
            print(f"   Keywords: {', '.join(glyph['associated_keywords'])}")
            print(f"   Frequency: {glyph['frequency']}")
            print(f"   Response: {glyph['response_cue']}")


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate glyphs from extracted poetry data")
    parser.add_argument(
        "--lexicon", default="learning/user_overrides/gutenberg_bulk_lexicon.json", help="Path to lexicon file"
    )
    parser.add_argument(
        "--output", default="generated_glyphs_from_poetry.json", help="Output file for generated glyphs"
    )
    parser.add_argument("--regenerate", action="store_true", help="Force regeneration of glyphs")

    args = parser.parse_args()

    print("[GLYPH GENERATION FROM POETRY EXTRACTION]")
    print("=" * 80)

    extractor = GlyphFromDataExtractor(args.lexicon)

    if not extractor.lexicon:
        print("✗ Failed to load lexicon. Exiting.")
        return 1

    # Extract patterns
    patterns = extractor.extract_patterns()

    if not patterns:
        print("✗ No patterns extracted. Exiting.")
        return 1

    # Generate glyphs
    glyphs = extractor.generate_glyphs()

    if glyphs:
        extractor.save_glyphs(args.output)
        extractor.print_summary()
        print("\n✓ Glyph generation complete!")
        return 0
    else:
        print("✗ Failed to generate glyphs")
        return 1


if __name__ == "__main__":
    sys.exit(main())
