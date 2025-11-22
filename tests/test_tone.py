import pytest
from emotional_os.glyphs.tone import update_tone_state, get_clarifier


@pytest.mark.parametrize(
    "inputs,expected_tone",
    [
        (
            [
                "Hello sir, could you assist me?",
                "Please clarify further.",
                "That would be most helpful.",
                "Thank you kindly."
            ],
            "formal"
        ),
        (
            [
                "hey what's up",
                "lol that's funny",
                "yo can you help",
                "cool thanks"
            ],
            "casual"
        ),
        (
            [
                "I'm feeling anxious.",
                "Not sure what's going on.",
                "It's been a weird day."
            ],
            "neutral"
        ),
        (
            [
                "Hello sir, could you assist me?",   # formal
                "lol that's funny",                  # casual
                "yo can you help",                   # casual
                "cool thanks"                         # casual
            ],
            "casual"  # majority of last 4 inputs are casual
        ),
    ]
)
def test_tone_adaptation(inputs, expected_tone):
    history = []
    tone_state = None
    for inp in inputs:
        tone_state = update_tone_state(history, inp)
    assert tone_state == expected_tone
    clar = get_clarifier(tone_state)
    assert clar.startswith(
        "I hear"), f"Clarifier should start with 'I hear': {clar}"
