from emotional_os.glyphs.dynamic_response_composer import DynamicResponseComposer
from emotional_os.glyphs import tone


def test_composer_tone_adaptation_formal():
    composer = DynamicResponseComposer()
    inputs = [
        "Hello sir, could you assist me?",
        "Please clarify further.",
        "That would be most helpful.",
        "Thank you kindly."
    ]
    last = None
    for inp in inputs:
        last = composer._make_clarifying_question(inp, {})
    # The final clarifier should be from the formal pool
    assert last in tone.CLARIFIER_POOLS['formal']


def test_composer_tone_adaptation_casual():
    composer = DynamicResponseComposer()
    inputs = [
        "hey what's up",
        "lol that's funny",
        "yo can you help",
        "cool thanks"
    ]
    last = None
    for inp in inputs:
        last = composer._make_clarifying_question(inp, {})
    assert last in tone.CLARIFIER_POOLS['casual']


def test_composer_tone_includes_emotion_when_detected():
    composer = DynamicResponseComposer()
    # Provide an emotional phrase; composer should include the emotion in the clarifier
    out = composer._make_clarifying_question(
        'I am feeling anxious', {'emotional_words': ['anxious']})
    assert 'anxious' in out.lower()
