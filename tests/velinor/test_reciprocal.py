import re

from emotional_os.core.signal_parser import parse_input


def test_whats_up_treated_as_conversational():
    res = parse_input("what's up", "emotional_os/parser/signal_lexicon.json")
    assert isinstance(res, dict)
    # Should be classified as conversational so we reply with a reciprocal prompt
    assert res.get("response_source") == "conversational"
    vr = res.get("voltage_response")
    assert isinstance(vr, str) and vr.strip(), f"Expected non-empty conversational response, got: {vr}"


def test_sup_treated_as_conversational():
    res = parse_input("sup", "emotional_os/parser/signal_lexicon.json")
    assert res.get("response_source") == "conversational"
    assert isinstance(res.get("voltage_response"), str)


def test_reciprocal_rotation_and_tone():
    import random as _r

    # Ensure we can observe multiple variants by varying the RNG seed
    responses = set()
    for seed in range(6):
        _r.seed(seed)
        res = parse_input("what's up", "emotional_os/parser/signal_lexicon.json")
        responses.add(res.get("voltage_response"))
    # We expect at least 2 distinct variants over several seeds
    assert len(responses) >= 2, f"Expected rotation across variants, got: {responses}"


def test_formal_tone_response():
    import random as _r

    _r.seed(0)
    res = parse_input("how are you doing", "emotional_os/parser/signal_lexicon.json")
    assert res.get("response_source") == "conversational"
    # Formal replies should contain 'How are' or similar formal phrasing
    assert "how are" in res.get("voltage_response").lower() or "how are you" in res.get("voltage_response").lower()
