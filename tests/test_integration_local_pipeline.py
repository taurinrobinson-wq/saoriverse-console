from main_response_engine import process_user_input
from relational_memory import list_recent
import relational_memory


def test_process_user_input_with_local_analysis():
    # Clear in-memory store
    relational_memory._CAPSULE_STORE.clear()

    local_analysis = {
        "voltage_response": "A small opening",
        "glyphs": [{"glyph_name": "OpeningGlyph"}],
        "best_glyph": {"glyph_name": "OpeningGlyph"},
    }

    out = process_user_input("I feel something shifting.", {
                             "local_analysis": local_analysis, "emotion": "wonder", "intensity": "gentle"})

    # Response should be inquisitive (short friend-like)
    assert ("tell me" in out.lower()) or (
        "what about" in out.lower()) or "opening" in out.lower()

    # A relational memory capsule should have been stored and include the glyph name
    recent = list_recent(1)
    assert len(recent) == 1
    capsule = recent[0]
    assert "OpeningGlyph" in capsule.symbolic_tags


def test_process_user_input_without_local_analysis():
    # Clear in-memory store
    relational_memory._CAPSULE_STORE.clear()

    out = process_user_input("I've been thinking a lot lately.")
    assert ("tell me" in out.lower()) or ("what about" in out.lower())

    recent = list_recent(1)
    assert len(recent) == 1
