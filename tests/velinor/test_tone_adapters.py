from tone_adapters import generate_archetypal_response, generate_initiatory_response


def test_generate_initiatory_default():
    r = generate_initiatory_response()
    # New tone favors short, inquisitive prompts. Accept previous cues too.
    assert ("tell me" in r.lower()) or ("what about" in r.lower()) or "spark" in r or "opening" in r


def test_generate_archetypal_default():
    r = generate_archetypal_response()
    # Accept inquisitive/holding phrasing.
    assert ("what about" in r.lower()) or ("tell me" in r.lower()) or "hold" in r or "honor" in r or "important" in r
