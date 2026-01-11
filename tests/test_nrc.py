#!/usr/bin/env python3
"""Test NRC lexicon loader"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from parser.nrc_lexicon_loader import nrc
    print(f"✓ NRC Lexicon loaded: {len(nrc.lexicon)} words")
    
    # Test some queries
    test_words = ["angry", "joy", "love", "hate", "afraid"]
    for word in test_words:
        emotions = nrc.get_emotions(word)
        if emotions:
            print(f"  {word}: {emotions}")
    
    print("\n✓ NRC loader working!")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
