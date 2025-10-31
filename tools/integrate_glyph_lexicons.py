"""
Integration script to load glyph lexicon data and enhance signal parsing
Converts CSV glyph definitions into signal keywords and descriptions

Refactored to expose a `main()` entrypoint so the script can be imported as a module
from a compatibility stub at repository root.
"""

import csv
import json
from collections import defaultdict

def load_glyph_lexicon_from_csv(csv_path: str) -> dict:
    """Load glyph definitions from CSV file"""
    glyphs = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            glyph_name = row['glyph_name'].strip()
            description = row['description'].strip()
            voltage_pair = row['voltage_pair'].strip()
            gate = row['gate'].strip()

            glyphs[glyph_name] = {
                'voltage_pair': voltage_pair,
                'description': description,
                'gate': gate
            }
    return glyphs

def generate_keywords_from_glyph_name(glyph_name: str) -> list:
    """Extract keywords from glyph names like 'Recursive Ache', 'Joy in Stillness'"""
    words = glyph_name.lower().split()
    return words

def generate_keywords_from_description(description: str) -> list:
    """Extract meaningful keywords from glyph description"""
    # Common emotional keywords in descriptions
    keywords = []

    description_lower = description.lower()

    emotional_words = {
        'ache': ['ache', 'longing', 'yearning', 'desire'],
        'grief': ['grief', 'mourning', 'sorrow', 'loss'],
        'joy': ['joy', 'delight', 'happiness', 'bliss'],
        'stillness': ['stillness', 'still', 'quiet', 'silence', 'peace'],
        'recognition': ['recognition', 'seen', 'witnessed', 'mirrored'],
        'boundary': ['boundary', 'boundaries', 'protected', 'contained'],
        'insight': ['insight', 'clarity', 'knowing', 'truth', 'reveals'],
        'devotion': ['devotion', 'vow', 'offering', 'sacred']
    }

    for category, words in emotional_words.items():
        for word in words:
            if word in description_lower:
                keywords.append(word)

    return list(set(keywords))

def create_glyph_signal_mapping(glyphs: dict) -> dict:
    """Create a mapping of glyph names to their keywords"""
    mapping = {}

    for glyph_name, glyph_data in glyphs.items():
        keywords = set()

        # Add words from glyph name
        keywords.update(generate_keywords_from_glyph_name(glyph_name))

        # Add keywords from description
        keywords.update(generate_keywords_from_description(glyph_data['description']))

        # Store mapping
        mapping[glyph_name] = {
            'keywords': list(keywords),
            'description': glyph_data['description'],
            'voltage_pair': glyph_data['voltage_pair'],
            'gate': glyph_data['gate']
        }

    return mapping

def enhance_signal_lexicon(original_lexicon_path: str, glyph_mapping: dict, output_path: str) -> None:
    """Enhance existing signal lexicon with glyph-based keywords"""

    # Load existing signal lexicon
    with open(original_lexicon_path, 'r', encoding='utf-8') as f:
        signal_lexicon = json.load(f)

    # Create reverse mapping: from glyph keywords to signals
    glyph_to_signals = defaultdict(list)

    # Add glyph names and descriptions as potential signals
    glyph_keywords = {}
    for glyph_name, mapping_data in glyph_mapping.items():
        # Map glyph name components to voltage signals
        for keyword in mapping_data['keywords']:
            if keyword not in glyph_keywords:
                glyph_keywords[keyword] = []
            # We'll use the gate/voltage to determine appropriate signal
            glyph_keywords[keyword].append({
                'glyph': glyph_name,
                'gate': mapping_data['gate'],
                'voltage': mapping_data['voltage_pair']
            })

    # Now enhance the signal lexicon with these new mappings
    # For now, just save the original with additions
    enhanced_lexicon = signal_lexicon.copy()

    # Add new keywords from glyphs (being selective to avoid over-matching)
    glyph_specific_keywords = {
        'recursive': 'ε',      # Spiraling/deepening insight
        'devotion': 'α',       # Sacred/vow
        'ecstasy': 'α',        # Joyful spiritual states
        'exalted': 'α',        # Lifted/elevated emotion
        'contained': 'β',      # Boundaries/held
        'stillness': 'δ',      # Peace/quiet
        'recognition': 'Ω',    # Being seen
        'clarity': 'ε',        # Insight/truth
        'bliss': 'λ',          # Ultimate joy
        'saturational': 'λ',   # Complete fulfillment
        'jubilant': 'λ',       # Celebratory
        'ceremonial': 'θ',     # Sacred/ritual
        'reverent': 'θ',       # Respectful/sacred
        'equilibrium': 'δ',    # Balance/still
        'cascade': 'ε',        # Flowing/spiraling
        'mirrored': 'Ω',       # Reflected/seen
        'sanctuary': 'β',      # Protected space
    }

    # Only add if not already present
    for keyword, signal in glyph_specific_keywords.items():
        if keyword not in enhanced_lexicon:
            enhanced_lexicon[keyword] = signal

    # Write enhanced lexicon
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enhanced_lexicon, f, indent=2, ensure_ascii=False)

    print(f"✓ Enhanced signal lexicon saved to {output_path}")
    print(f"  Original keywords: {len(signal_lexicon)}")
    print(f"  Enhanced keywords: {len(enhanced_lexicon)}")
    print(f"  New keywords added: {len(enhanced_lexicon) - len(signal_lexicon)}")

def create_glyph_name_index(glyph_mapping: dict, output_path: str) -> None:
    """Create an index of glyph names and their properties for quick lookup"""

    glyph_index = {}
    for glyph_name, mapping_data in glyph_mapping.items():
        glyph_index[glyph_name.lower()] = {
            'canonical_name': glyph_name,
            'description': mapping_data['description'],
            'keywords': mapping_data['keywords'],
            'gate': mapping_data['gate'],
            'voltage_pair': mapping_data['voltage_pair']
        }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(glyph_index, f, indent=2, ensure_ascii=False)

    print(f"✓ Glyph index created: {output_path}")
    print(f"  Total glyphs indexed: {len(glyph_index)}")

def main(csv_path: str = "glyph_lexicon_rows.csv",
         signal_lexicon_path: str = "parser/signal_lexicon.json",
         output_signal_path: str = "parser/signal_lexicon.json",
         glyph_index_path: str = "parser/glyph_index.json"):
    print("Loading glyph lexicon from CSV...")
    glyphs = load_glyph_lexicon_from_csv(csv_path)
    print(f"✓ Loaded {len(glyphs)} glyphs")

    print("\nCreating glyph signal mapping...")
    glyph_mapping = create_glyph_signal_mapping(glyphs)

    print("\nEnhancing signal lexicon...")
    enhance_signal_lexicon(signal_lexicon_path, glyph_mapping, output_signal_path)

    print("\nCreating glyph index...")
    create_glyph_name_index(glyph_mapping, glyph_index_path)

    print("\n✓ Integration complete!")

if __name__ == "__main__":
    main()
