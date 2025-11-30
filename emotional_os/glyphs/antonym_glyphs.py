#!/usr/bin/env python3
"""
Antonym Glyphs Helper Module

Simple high-level API for accessing antonym glyphs throughout the system.

Usage:
    from emotional_os.glyphs.antonym_glyphs import (
        get_antonym_for_voltage_pair,
        find_antonym_by_emotion,
        search_antonyms,
        get_indexed_antonyms
    )

    # Find antonym for a glyph's voltage pair
    antonym = get_antonym_for_voltage_pair("γ × γ")

    # Search for antonyms by emotion
    results = find_antonym_by_emotion("comfort")

    # Search by any text
    results = search_antonyms("sorrow")
"""

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Get the directory of this file
MODULE_DIR = Path(__file__).parent
ANTONYM_INDEX_PATH = MODULE_DIR / "antonym_glyphs_indexed.json"

# Global indexer instance (lazy loaded)
_indexer = None


def _ensure_indexed() -> bool:
    """Ensure antonym glyphs are indexed."""
    global _indexer

    if _indexer is not None:
        return True

    try:
        if not ANTONYM_INDEX_PATH.exists():
            logger.warning("Antonym glyphs index not found. Run antonym_glyphs_indexer.py first.")
            return False

        with open(ANTONYM_INDEX_PATH, "r", encoding="utf-8") as f:
            _indexer = json.load(f)

        logger.info(f"✓ Loaded antonym glyphs index with {len(_indexer.get('antonym_glyphs', []))} entries")
        return True

    except Exception as e:
        logger.error(f"Error loading antonym glyphs index: {e}")
        return False


def get_indexed_antonyms() -> Optional[Dict]:
    """Get the full indexed antonym glyphs dictionary.

    Returns:
        dict: Full indexed data or None if not available
    """
    if _ensure_indexed():
        return _indexer
    return None


def get_all_antonym_glyphs() -> List[Dict]:
    """Get all antonym glyphs.

    Returns:
        List[dict]: All antonym glyphs
    """
    if not _ensure_indexed():
        return []

    return _indexer.get("antonym_glyphs", [])


def find_antonym_by_voltage_pair(voltage_pair: str) -> Optional[Dict]:
    """Find antonym by voltage pair.

    Args:
        voltage_pair: Voltage pair like "γ × γ"

    Returns:
        dict: Antonym glyph if found
    """
    if not _ensure_indexed():
        return None

    indexes = _indexer.get("indexes", {})
    by_pairing = indexes.get("by_pairing", {})

    return by_pairing.get(voltage_pair)


def find_antonym_by_emotion(emotion: str) -> Optional[Dict]:
    """Find antonym by base emotion name.

    Args:
        emotion: Emotion name (e.g., "comfort", "joy", "grief")

    Returns:
        dict: Antonym glyph if found
    """
    if not _ensure_indexed():
        return None

    indexes = _indexer.get("indexes", {})
    by_emotion = indexes.get("by_base_emotion", {})

    return by_emotion.get(emotion.lower())


def find_antonym_by_name(name: str) -> Optional[Dict]:
    """Find antonym by glyph name.

    Args:
        name: Glyph name (e.g., "Gentle Holding", "Pressure Release")

    Returns:
        dict: Antonym glyph if found
    """
    if not _ensure_indexed():
        return None

    indexes = _indexer.get("indexes", {})
    by_name = indexes.get("by_name", {})

    return by_name.get(name.lower())


def search_antonyms(query: str) -> List[Dict]:
    """Search antonym glyphs by any text field.

    Args:
        query: Search string

    Returns:
        List[dict]: Matching antonym glyphs
    """
    if not _ensure_indexed():
        return []

    query_lower = query.lower()
    results = []

    for antonym in _indexer.get("antonym_glyphs", []):
        base_emotion = antonym.get("Base Emotion", "").lower()
        name = antonym.get("Name", "").lower()
        description = antonym.get("Description", "").lower()
        pairing = antonym.get("Pairing", "").lower()

        if query_lower in base_emotion or query_lower in name or query_lower in description or query_lower in pairing:
            results.append(antonym)

    return results


def suggest_emotional_opposite(emotion: str) -> Optional[Dict]:
    """Get the emotional opposite of a given emotion.

    Args:
        emotion: Emotion name

    Returns:
        dict: Antonym glyph representing the opposite
    """
    if not _ensure_indexed():
        return None

    # Try direct lookup first
    antonym = find_antonym_by_emotion(emotion)
    if antonym:
        return antonym

    # Try search if direct lookup fails
    results = search_antonyms(emotion)
    if results:
        return results[0]

    return None


def get_antonym_by_emotional_pair(emotion1: str, emotion2: str) -> Optional[Dict]:
    """Find antonym representing the opposite of an emotional pair.

    Args:
        emotion1: First emotion
        emotion2: Second emotion

    Returns:
        dict: Antonym glyph if found
    """
    if not _ensure_indexed():
        return None

    # Search for antonyms related to either emotion
    query = f"{emotion1} {emotion2}"
    results = search_antonyms(query)

    if results:
        return results[0]

    # Fall back to first emotion
    return find_antonym_by_emotion(emotion1)


def get_antonym_metadata() -> Dict:
    """Get metadata about the antonym glyphs index.

    Returns:
        dict: Metadata with counts and info
    """
    if not _ensure_indexed():
        return {}

    return _indexer.get("metadata", {})


def list_antonym_emotions() -> List[str]:
    """List all available antonym base emotions.

    Returns:
        List[str]: All base emotions in the antonym system
    """
    if not _ensure_indexed():
        return []

    indexes = _indexer.get("indexes", {})
    by_emotion = indexes.get("by_base_emotion", {})

    return sorted(list(by_emotion.keys()))


def list_antonym_pairings() -> List[str]:
    """List all available antonym voltage pairings.

    Returns:
        List[str]: All voltage pairings in the antonym system
    """
    if not _ensure_indexed():
        return []

    indexes = _indexer.get("indexes", {})
    by_pairing = indexes.get("by_pairing", {})

    return sorted(list(by_pairing.keys()))


def list_antonym_names() -> List[str]:
    """List all available antonym glyph names.

    Returns:
        List[str]: All glyph names in the antonym system
    """
    if not _ensure_indexed():
        return []

    indexes = _indexer.get("indexes", {})
    by_name = indexes.get("by_name", {})

    return sorted(list(by_name.keys()))


def get_antonym_by_id(index: int) -> Optional[Dict]:
    """Get antonym glyph by index position.

    Args:
        index: Position in antonym glyphs list

    Returns:
        dict: Antonym glyph at that position
    """
    if not _ensure_indexed():
        return None

    glyphs = _indexer.get("antonym_glyphs", [])
    if 0 <= index < len(glyphs):
        return glyphs[index]

    return None


def get_total_antonym_count() -> int:
    """Get total number of antonym glyphs in the system.

    Returns:
        int: Total antonym glyphs
    """
    if not _ensure_indexed():
        return 0

    metadata = _indexer.get("metadata", {})
    return metadata.get("total_antonym_glyphs", 0)


def format_antonym_for_display(antonym: Dict) -> str:
    """Format an antonym glyph for display in UI.

    Args:
        antonym: Antonym glyph dictionary

    Returns:
        str: Formatted string for display
    """
    if not antonym:
        return ""

    return f"**{antonym.get('Base Emotion')}** ({antonym.get('Pairing')})\n*{antonym.get('Name')}*\n\n{antonym.get('Description')}"


# Initialize on import
if not _ensure_indexed():
    logger.debug("Antonym glyphs will be indexed on first access")


def main():
    """Test the helper functions."""
    print("\n" + "=" * 80)
    print("ANTONYM GLYPHS HELPER - QUICK TEST")
    print("=" * 80)

    # Test basic functions
    print(f"\n✓ Total antonyms available: {get_total_antonym_count()}")
    print(f"✓ Available emotions: {len(list_antonym_emotions())}")
    print(f"✓ Available pairings: {len(list_antonym_pairings())}")

    # Test search
    print("\n" + "─" * 80)
    print("SEARCH TEST")
    print("─" * 80)

    results = search_antonyms("comfort")
    print(f"\n🔍 Search for 'comfort': {len(results)} result(s)")
    if results:
        antonym = results[0]
        print(f"\n{format_antonym_for_display(antonym)}")

    # Test lookup
    print("\n" + "─" * 80)
    print("LOOKUP TEST")
    print("─" * 80)

    antonym = find_antonym_by_emotion("joy")
    if antonym:
        print("\n✓ Found antonym for 'joy':")
        print(f"{format_antonym_for_display(antonym)}")
    else:
        print("\n✗ No antonym found for 'joy'")

    # Test opposite pair
    print("\n" + "─" * 80)
    print("OPPOSITE PAIR TEST")
    print("─" * 80)

    opposite = suggest_emotional_opposite("grief")
    if opposite:
        print("\n✓ Emotional opposite of 'grief':")
        print(f"{format_antonym_for_display(opposite)}")

    print("\n" + "=" * 80)
    print("✓ Tests complete!")
    print("=" * 80)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(name)s] - %(message)s")
    main()
