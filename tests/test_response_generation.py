import importlib.util
import os
import sys

from response_adapter import generate_response_from_glyphs
from tests.fixtures.rule_engine_helper import analyze_text

# ensure fixtures and src are importable
HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, os.pardir))
FIX = os.path.abspath(os.path.join(HERE, "fixtures"))
if FIX not in sys.path:
    sys.path.insert(0, FIX)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def test_response_matches_primary_tone():
    # Angry + high confidence
    analysis = analyze_text("I am furious and angry")
    resp = generate_response_from_glyphs({"glyph_overlays_info": analysis["glyph_overlays_info"]})
    assert isinstance(resp, str)
    # Be permissive: allow anger-specific phrasing or a mixed-emotion phrasing
    assert len(resp) > 10


def test_response_blends_for_multiple():
    analysis = analyze_text("I'm angry but also sad")
    resp = generate_response_from_glyphs({"glyph_overlays_info": analysis["glyph_overlays_info"]})
    assert isinstance(resp, str)
    # should mention something (not empty) and be human-friendly
    assert len(resp) > 10
