import importlib.util
import os
import sys

# ensure fixtures are importable
HERE = os.path.dirname(__file__)
FIX = os.path.abspath(os.path.join(HERE, "fixtures"))
if FIX not in sys.path:
    sys.path.insert(0, FIX)

spec_sp = importlib.util.spec_from_file_location("signal_parser", os.path.join(FIX, "signal_parser.py"))
signal_parser = importlib.util.module_from_spec(spec_sp)
spec_sp.loader.exec_module(signal_parser)
parse_input = signal_parser.parse_input


def _conf_for(result, tag):
    infos = result.get("glyph_overlays_info") or []
    for i in infos:
        if i.get("tag") == tag:
            return float(i.get("confidence", 0.0))
    return 0.0


def test_negation_reduces_confidence():
    # "I am not angry" should produce a very low anger confidence due to negation window
    r = parse_input("I am not angry")
    anger_conf = _conf_for(r, "anger")
    assert anger_conf > 0.0
    assert anger_conf < 0.2, f"Expected low anger confidence with negation, got {anger_conf}"


def test_mixed_emotions_both_detected():
    # both emotion tokens present should yield reasonably high confidences
    r = parse_input("I'm angry and sad")
    anger_conf = _conf_for(r, "anger")
    sad_conf = _conf_for(r, "sadness")
    assert anger_conf >= 0.5, f"anger confidence too low: {anger_conf}"
    assert sad_conf >= 0.4, f"sadness confidence too low: {sad_conf}"


def test_sarcasm_example_detects_unseen():
    # Sarcasm is not modeled, but the lexical cue 'ignored' should still be detected
    r = parse_input("Oh great, I just love being ignored")
    unseen_conf = _conf_for(r, "feeling_unseen")
    assert unseen_conf >= 0.5, f"feeling_unseen not detected strongly enough: {unseen_conf}"
