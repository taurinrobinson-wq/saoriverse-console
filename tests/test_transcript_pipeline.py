import sys as _sys
import os
import sys
import importlib.util

# Ensure our test fixtures are importable (tests/fixtures)
HERE = os.path.dirname(__file__)
FIX = os.path.abspath(os.path.join(HERE, "fixtures"))
if FIX not in sys.path:
    sys.path.insert(0, FIX)

# Load test-local fixtures explicitly to avoid import resolution issues under pytest
spec_sp = importlib.util.spec_from_file_location(
    "signal_parser", os.path.join(FIX, "signal_parser.py"))
signal_parser = importlib.util.module_from_spec(spec_sp)
spec_sp.loader.exec_module(signal_parser)
parse_input = signal_parser.parse_input

spec_cm = importlib.util.spec_from_file_location(
    "clarification_memory", os.path.join(FIX, "clarification_memory.py"))
clar_mem = importlib.util.module_from_spec(spec_cm)
spec_cm.loader.exec_module(clar_mem)
# Make sure Python's import system will return the same module instance
_sys.modules["clarification_memory"] = clar_mem
record_correction = clar_mem.record_correction

spec_sp = importlib.util.spec_from_file_location(
    "signal_parser", os.path.join(FIX, "signal_parser.py"))
signal_parser = importlib.util.module_from_spec(spec_sp)
spec_sp.loader.exec_module(signal_parser)
parse_input = signal_parser.parse_input

# Synthetic transcript simulating emotional cues
synthetic_transcript = [
    {"speaker": "Facilitator",
        "text": "Can you share a moment that felt emotionally charged for you?"},
    {"speaker": "Participant",
        "text": "Yeah… during a group project last year, I felt completely ignored. No one asked for my input."},
    {"speaker": "Facilitator", "text": "What was that like for you?"},
    {"speaker": "Participant",
        "text": "Frustrating. I kept trying to speak up, but it was like I wasn’t even there."},
    {"speaker": "Facilitator", "text": "Did you say anything to them?"},
    {"speaker": "Participant",
        "text": "Eventually, I did. I said, 'I feel invisible.' One person apologized, but it still stung."},
    {"speaker": "Facilitator", "text": "What emotions were strongest in that moment?"},
    {"speaker": "Participant",
        "text": "Anger, mostly. And sadness. I just wanted to be seen."}
]


def test_transcript_pipeline():
    # Inject a clarification correction for a known trigger
    record_correction(
        trigger_phrase="I feel invisible",
        suggested_intent="emotional_checkin",
        confidence=1.0,
    )

    # Process each turn and verify result shape + a few expectations
    seen_forced = False
    seen_emotion = False

    for turn in synthetic_transcript:
        result = parse_input(turn["text"], speaker=turn["speaker"])
        print(f"\n[{turn['speaker']}] {turn['text']}")
        print(f"→ Forced Intent: {result.get('forced_intent')}")
        print(f"→ Dominant Emotion: {result.get('dominant_emotion')}")
        print(f"→ Tone Overlay: {result.get('tone_overlay')}")
        print(f"→ Glyph Overlays: {result.get('glyph_overlays')}")
        print(
            f"→ Clarification Provenance: {result.get('clarification_provenance')}")

        # If the line contains the trigger, we should see the forced intent
        if "I feel invisible" in turn["text"]:
            # forced intent should be applied and provenance should include record_id and confidence
            assert result["forced_intent"] == "emotional_checkin"
            prov = result.get("clarification_provenance")
            assert prov is not None and prov.get("record_id")
            assert isinstance(prov.get("confidence"), float) or isinstance(
                prov.get("confidence"), int)
            # tone overlay should come from routing table
            assert result.get("tone_overlay") == "reflective, validating"
            seen_forced = True

        # If the line mentions emotion words, assert a detected dominant emotion
        if any(k in turn["text"].lower() for k in ("anger", "sad", "frustrat", "invisible", "ignored")):
            # stricter: ensure glyph overlays exist and dominant_emotion aligns
            overlays = result.get("glyph_overlays") or []
            assert len(overlays) > 0
            assert result["dominant_emotion"] in ("anger", "sadness")
            seen_emotion = True

    assert seen_forced, "forced intent example was not observed"
    assert seen_emotion, "no emotion-bearing lines were detected"
    # Additional: confirm that final line includes both anger and sadness overlays
    final = parse_input(
        synthetic_transcript[-1]["text"], speaker=synthetic_transcript[-1]["speaker"])
    assert "anger" in final.get("glyph_overlays", [])
    assert "sadness" in final.get("glyph_overlays", [])
