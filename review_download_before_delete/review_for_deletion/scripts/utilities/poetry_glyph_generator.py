#!/usr/bin/env python3
"""
Direct Glyph Generator from Poetry Lexicon Data

Creates glyphs directly from the discovered emotional patterns in the
Project Gutenberg poetry lexicon. Works with the actual lexicon structure.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


class PoetryGlyphGenerator:
    """Generate glyphs from poetry-extracted lexicon data."""
    
    def __init__(self, lexicon_path: str = "learning/user_overrides/gutenberg_bulk_lexicon.json"):
        """Initialize with lexicon data."""
        self.lexicon_path = Path(lexicon_path)
        self.lexicon = {}
        self.signals = {}
        self.glyphs = []
        self._load_lexicon()
    
    def _load_lexicon(self):
        """Load the lexicon file."""
        if not self.lexicon_path.exists():
            print(f"✗ Lexicon not found at {self.lexicon_path}")
            return
        
        try:
            with open(self.lexicon_path, 'r') as f:
                self.lexicon = json.load(f)
            self.signals = self.lexicon.get('signals', {})
            print(f"✓ Loaded lexicon with {len(self.signals)} emotional dimensions")
            for signal_name, signal_data in self.signals.items():
                freq = signal_data.get('frequency', 0)
                keywords_count = len(signal_data.get('keywords', []))
                print(f"  - {signal_name}: {keywords_count} keywords, frequency {freq}")
        except Exception as e:
            print(f"✗ Failed to load lexicon: {e}")
    
    def extract_glyph_patterns(self) -> List[Dict]:
        """Extract emotional patterns that should become glyphs."""
        patterns = []
        
        if not self.signals:
            print("✗ No signals data available")
            return []
        
        # Get dimension names sorted by frequency
        dimensions = sorted(
            self.signals.keys(),
            key=lambda d: self.signals[d].get('frequency', 0),
            reverse=True
        )
        
        print(f"\n[GLYPH PATTERN EXTRACTION]")
        print(f"Dimensions (by frequency):")
        for dim in dimensions:
            freq = self.signals[dim].get('frequency', 0)
            print(f"  - {dim}: {freq}")
        
        # Create 2-way combinations
        print(f"\nExtracting combinations...")
        for i, dim1 in enumerate(dimensions):
            for dim2 in dimensions[i+1:]:
                signal1 = self.signals[dim1]
                signal2 = self.signals[dim2]
                
                # Get keywords for this combination
                keywords1 = set(signal1.get('keywords', []))
                keywords2 = set(signal2.get('keywords', []))
                
                # Combined frequency
                freq = signal1.get('frequency', 0) + signal2.get('frequency', 0)
                
                # Only include if frequency >= 300 (significant)
                if freq >= 300:
                    pattern = {
                        "dimensions": [dim1, dim2],
                        "combined_frequency": freq,
                        "keywords": list(keywords1 | keywords2)[:10],
                        "source_dims": {
                            dim1: signal1.get('frequency', 0),
                            dim2: signal2.get('frequency', 0)
                        }
                    }
                    patterns.append(pattern)
        
        # Sort by frequency
        patterns.sort(key=lambda p: p['combined_frequency'], reverse=True)
        
        print(f"\nExtracted {len(patterns)} patterns with frequency >= 300")
        return patterns
    
    def create_glyphs_from_patterns(self, patterns: List[Dict]) -> List[Dict]:
        """Create glyph definitions from patterns."""
        glyphs = []
        
        print(f"\n[GLYPH CREATION]")
        
        for i, pattern in enumerate(patterns[:20]):  # Top 20 patterns
            glyph = self._pattern_to_glyph(pattern, i+1)
            glyphs.append(glyph)
        
        print(f"Created {len(glyphs)} glyphs")
        self.glyphs = glyphs
        return glyphs
    
    def _pattern_to_glyph(self, pattern: Dict, glyph_num: int) -> Dict:
        """Convert a pattern into a glyph definition."""
        
        dims = pattern['dimensions']
        freq = pattern['combined_frequency']
        keywords = pattern['keywords']
        
        # Create meaningful glyph name
        glyph_name = self._create_name(dims)
        glyph_symbol = self._create_symbol(dims)
        glyph_id = f"glyph_poetry_{glyph_num:02d}"
        
        # Create response cue and narrative
        response_cue = self._create_response_cue(dims, keywords)
        narrative = self._create_narrative(dims)
        
        glyph = {
            "id": glyph_id,
            "name": glyph_name,
            "symbol": glyph_symbol,
            "core_emotions": dims,
            "associated_keywords": keywords[:8],
            "combined_frequency": freq,
            "response_cue": response_cue,
            "narrative_hook": narrative,
            "created_from_pattern": True,
            "source": "gutenberg_poetry"
        }
        
        return glyph
    
    def _create_name(self, dimensions: List[str]) -> str:
        """Create a meaningful name from dimensions."""
        
        named_combinations = {
            ("love", "nature"): "Nature's Love",
            ("love", "joy"): "Celebration",
            ("love", "transformation"): "Love's Becoming",
            ("love", "sensuality"): "Passion",
            ("love", "admiration"): "Devotion",
            ("nature", "joy"): "Natural Joy",
            ("nature", "transformation"): "Seasonal Wisdom",
            ("nature", "sensuality"): "Earth's Sensuality",
            ("transformation", "joy"): "Joyful Becoming",
            ("transformation", "admiration"): "Inspiring Change",
            ("joy", "admiration"): "Admiring Joy",
            ("joy", "sensuality"): "Sensual Delight",
            ("vulnerability", "love"): "Open Heart",
            ("vulnerability", "transformation"): "Metamorphosis",
            ("intimacy", "love"): "Deep Connection",
            ("intimacy", "joy"): "Joy of Connection",
        }
        
        key = tuple(sorted(dimensions))
        default_name = " & ".join([d.title() for d in dimensions])
        # Check both orderings for 2-element tuples
        if len(key) == 2:
            reverse_key = (key[1], key[0])
            if key in named_combinations:
                return named_combinations[key]
            elif reverse_key in named_combinations:
                return named_combinations[reverse_key]
        return default_name
    
    def _create_symbol(self, dimensions: List[str]) -> str:
        """Create a symbol for the glyph."""
        
        symbols = {
            "love": "♥",
            "intimacy": "❤",
            "vulnerability": "🌱",
            "transformation": "🦋",
            "admiration": "⭐",
            "joy": "☀",
            "sensuality": "🌹",
            "nature": "🌿",
        }
        
        sym_list = [symbols.get(d, "◆") for d in dimensions]
        return "".join(sym_list)
    
    def _create_response_cue(self, dimensions: List[str], keywords: List[str]) -> str:
        """Create a response cue."""
        
        if "love" in dimensions and "nature" in dimensions:
            return "Celebrate love found in natural beauty"
        elif "transformation" in dimensions:
            return f"Honor the becoming, the change within"
        elif "joy" in dimensions:
            return f"Welcome the joy that emerges"
        else:
            return f"Acknowledge the {' and '.join(dimensions)} here"
    
    def _create_narrative(self, dimensions: List[str]) -> str:
        """Create a narrative hook."""
        
        if "love" in dimensions:
            return f"A story of love through {dimensions[-1]}"
        elif "transformation" in dimensions:
            return f"The journey of becoming"
        elif "nature" in dimensions:
            return f"What the earth teaches us"
        else:
            return f"The interplay of {' and '.join(dimensions)}"
    
    def print_glyphs(self, limit: int = 15):
        """Print glyphs in a readable format."""
        
        if not self.glyphs:
            print("No glyphs generated")
            return
        
        print("\n" + "=" * 80)
        print("[GENERATED GLYPHS FROM POETRY]")
        print("=" * 80)
        
        for i, glyph in enumerate(self.glyphs[:limit], 1):
            print(f"\n{i}. {glyph['symbol']} {glyph['name']}")
            print(f"   ID: {glyph['id']}")
            print(f"   Emotions: {', '.join(glyph['core_emotions'])}")
            print(f"   Keywords: {', '.join(glyph['associated_keywords'][:5])}")
            print(f"   Frequency: {glyph['combined_frequency']}")
            print(f"   Response: {glyph['response_cue']}")
    
    def save_glyphs(self, output_path: str = "generated_glyphs_from_poetry.json"):
        """Save glyphs to JSON file."""
        
        if not self.glyphs:
            print("No glyphs to save")
            return
        
        output_file = Path(output_path)
        
        try:
            with open(output_file, 'w') as f:
                json.dump(self.glyphs, f, indent=2)
            
            print(f"\n✓ Saved {len(self.glyphs)} glyphs to {output_file}")
            print(f"  File size: {output_file.stat().st_size / 1024:.1f} KB")
        except Exception as e:
            print(f"✗ Failed to save glyphs: {e}")


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate glyphs from poetry lexicon")
    parser.add_argument("--lexicon", default="learning/user_overrides/gutenberg_bulk_lexicon.json",
                       help="Path to lexicon file")
    parser.add_argument("--output", default="generated_glyphs_from_poetry.json",
                       help="Output file for generated glyphs")
    parser.add_argument("--limit", type=int, default=15,
                       help="Number of glyphs to display")
    
    args = parser.parse_args()
    
    print("[POETRY GLYPH GENERATOR]")
    print("=" * 80)
    
    generator = PoetryGlyphGenerator(args.lexicon)
    
    if not generator.signals:
        print("✗ No signal data found. Exiting.")
        return 1
    
    # Extract patterns
    patterns = generator.extract_glyph_patterns()
    
    if not patterns:
        print("✗ No patterns extracted")
        return 1
    
    # Create glyphs
    glyphs = generator.create_glyphs_from_patterns(patterns)
    
    if glyphs:
        generator.print_glyphs(args.limit)
        generator.save_glyphs(args.output)
        print("\n✓ Glyph generation complete!")
        return 0
    else:
        print("✗ Failed to create glyphs")
        return 1


if __name__ == "__main__":
    sys.exit(main())
