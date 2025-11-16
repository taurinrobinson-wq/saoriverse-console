from phase_modulator import detect_phase


def test_detect_initiatory_by_phrase():
    assert detect_phase("I just met someone amazing") == "initiatory"


def test_detect_archetypal_by_anchor():
    assert detect_phase("This relationship has been hard") == "archetypal"


def test_detect_by_context_tags():
    assert detect_phase(
        "blah", {"symbolic_tags": ["initiatory_signal"]}) == "initiatory"
    assert detect_phase(
        "blah", {"symbolic_tags": ["containment_request"]}) == "archetypal"
