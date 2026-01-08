from main_response_engine import process_user_input


def test_process_user_input_initiatory():
    out = process_user_input("I just met someone who really sees me.", {"emotion": "longing", "intensity": "high"})
    # Engine now favors short, inquisitive responses — accept either style.
    assert ("tell me" in out.lower()) or ("what about" in out.lower()) or "spark" in out or "opening" in out


def test_process_user_input_archetypal():
    out = process_user_input("We’ve been talking for a while and it's been heavy.")
    assert ("what about" in out.lower()) or ("tell me" in out.lower()) or "hold" in out or "honoring" in out
