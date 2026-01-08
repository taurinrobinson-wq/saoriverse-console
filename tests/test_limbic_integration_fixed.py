from emotional_os.supabase.supabase_integration import (
    HybridEmotionalProcessor,
    SaoriResponse,
)


class DummySupabase:
    def process_message(self, message, conversation_context=None, conversation_style=None, mode=None):
        # Return a simple SaoriResponse-like object
        return SaoriResponse(
            reply="Baseline reply: I understand.", glyph=None, parsed_glyphs=[], upserted_glyphs=[], log={}
        )


class DummyLimbicEngine:
    def process_emotion_with_limbic_mapping(self, text: str):
        # Return the expected limbic result shape
        return {
            "emotion": "joy",
            "glyphs": ["sun", "smile"],
            "ritual_sequence": ["blink", "breath", "brace"],
            "chiasmus": {"pattern": "A-B-A"},
        }


def test_happy_path_decorates_reply():
    supabase = DummySupabase()
    limbic = DummyLimbicEngine()
    processor = HybridEmotionalProcessor(supabase_integrator=supabase, use_local_fallback=False, limbic_engine=limbic)

    res = processor.process_emotional_input("I feel happy today", prefer_ai=True, privacy_mode=False)

    assert isinstance(res, dict)
    assert res.get("limbic_decorated") is True
    assert res.get("response") is not None
    assert "I understand" in res.get("response") or res.get("response") != "Baseline reply: I understand."


def test_safety_path_prevents_decoration():
    supabase = DummySupabase()
    limbic = DummyLimbicEngine()
    processor = HybridEmotionalProcessor(supabase_integrator=supabase, use_local_fallback=False, limbic_engine=limbic)

    # Message contains a trauma lexicon word 'assault' which should trigger safety
    message = "I survived an assault and don't know what to do"
    res = processor.process_emotional_input(message, prefer_ai=True, privacy_mode=False)

    assert isinstance(res, dict)
    # Decoration should be skipped when safety flag is raised
    assert res.get("limbic_decorated") is False
    assert res.get("response") == "Baseline reply: I understand."


def test_edge_case_missing_limbic_engine():
    supabase = DummySupabase()
    processor = HybridEmotionalProcessor(supabase_integrator=supabase, use_local_fallback=False, limbic_engine=None)

    res = processor.process_emotional_input("A neutral message", prefer_ai=True, privacy_mode=False)

    assert isinstance(res, dict)
    assert res.get("limbic_decorated") is False
    assert res.get("response") == "Baseline reply: I understand."
