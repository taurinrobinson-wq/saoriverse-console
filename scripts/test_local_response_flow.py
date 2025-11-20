#!/usr/bin/env python3
"""
Quick test harness: parse a sample emotionally charged message using
`parse_input` (local parser) and then compose a response with
`DynamicResponseComposer.compose_multi_glyph_response`.

Usage: python3 scripts/test_local_response_flow.py
"""
import sys
import json
from pprint import pprint

# Ensure project root is on path when run from repo root
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

try:
    from emotional_os.core.signal_parser import parse_input
except Exception as e:
    print("Failed to import parse_input:", e)
    raise

try:
    from emotional_os.glyphs.dynamic_response_composer import DynamicResponseComposer
except Exception as e:
    print("Failed to import DynamicResponseComposer:", e)
    raise

SAMPLE = """
I keep trying to study but my mind goes blank. I feel so frustrated and ashamed —
like I'm carrying my parent's voice in my head saying I'm not good enough. I want
to be able to enjoy learning but I get blocked and anxious every time.
"""


def main():
    print("Sample input:\n", SAMPLE)
    print('\nRunning local parse_input()...')
    analysis = parse_input(SAMPLE, 'emotional_os/parser/signal_lexicon.json',
                           db_path='emotional_os/glyphs/glyphs.db', conversation_context={'messages': []})

    print('\nParse analysis (summary):')
    # Show only key fields
    summary = {
        'voltage_response': analysis.get('voltage_response'),
        'gates': analysis.get('gates'),
        'glyphs_count': len(analysis.get('glyphs', [])),
        'top_glyphs': [g.get('glyph_name') for g in analysis.get('glyphs', [])[:5]]
    }
    pprint(summary)

    top_glyphs = analysis.get('glyphs', [])

    composer = DynamicResponseComposer()
    print('\nComposed response (multi-glyph, top_n=5):\n')
    response = composer.compose_multi_glyph_response(
        SAMPLE, top_glyphs, conversation_context={'messages': []}, top_n=5)
    print(response)


if __name__ == '__main__':
    main()
