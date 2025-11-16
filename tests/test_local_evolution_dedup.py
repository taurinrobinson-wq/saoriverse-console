import pytest

from scripts.utilities import hybrid_processor_with_evolution as hpe


class FakeLearner:
    def __init__(self, score_value: float = 0.9):
        self.score_value = score_value
        self.staged = []
        self.persisted_events = []

    def collect_candidate(self, candidate, source="test"):
        # simulate the event object that writer.append_event would receive
        evt = {"source": source, "event_type": "candidate",
               "payload": candidate, "confidence": candidate.get("confidence")}
        self.staged.append(evt)

    def score_candidate(self, candidate):
        return float(self.score_value)

    def persist(self):
        # move staged to persisted
        self.persisted_events.extend(self.staged)
        self.staged = []


@pytest.fixture(autouse=True)
def prevent_disk_writes(monkeypatch):
    # Prevent learning.writer.append_event from writing to disk during tests
    calls = []

    def fake_append(path, evt):
        calls.append((path, evt))

    monkeypatch.setattr(hpe, "append_event", fake_append)
    return calls


def test_identical_existing_glyph_is_rejected(prevent_disk_writes):
    fake = FakeLearner(score_value=0.95)
    evo = hpe.LocalEvolution(learner=fake, accept_threshold=0.8)

    # seed existing lexicon with normalized phrase
    evo._existing_normalized.add(evo._normalize("felt seen"))
    evo._near_dup_staging = "/tmp/near_dup_test.jsonl"

    res = evo.process_dialogue_exchange(
        user_id="u1",
        conversation_id="c1",
        user_input="felt seen",
        ai_response="",
        emotional_signals=[],
    )

    # Should not emit a new glyph (duplicate)
    assert res["new_glyphs_generated"] == []

    # Candidate should have been persisted with dedup metadata
    assert fake.persisted_events, "No persisted events found"
    payload = fake.persisted_events[0]["payload"]
    assert payload.get("dedup") is True
    assert "dedup_reason" in payload


def test_punctuation_and_spacing_normalize_to_duplicate(prevent_disk_writes):
    fake = FakeLearner(score_value=0.95)
    evo = hpe.LocalEvolution(learner=fake, accept_threshold=0.8)

    evo._existing_normalized.add(evo._normalize("felt seen"))
    evo._near_dup_staging = "/tmp/near_dup_test.jsonl"

    # Input differs by punctuation and spacing
    res = evo.process_dialogue_exchange(
        user_id="u2",
        conversation_id="c2",
        user_input="  Felt,   seen! ",
        ai_response="",
        emotional_signals=[],
    )

    assert res["new_glyphs_generated"] == []
    payload = fake.persisted_events[0]["payload"]
    assert payload.get("dedup") is True
    assert "dedup_reason" in payload


def test_new_candidate_is_accepted_and_emitted(prevent_disk_writes):
    fake = FakeLearner(score_value=0.95)
    evo = hpe.LocalEvolution(learner=fake, accept_threshold=0.8)

    # Ensure lexicon cache is empty
    evo._existing_normalized.clear()
    evo._near_dup_staging = "/tmp/near_dup_test.jsonl"

    res = evo.process_dialogue_exchange(
        user_id="u3",
        conversation_id="c3",
        user_input="I feel calm and centered",
        ai_response="",
        emotional_signals=[],
    )

    # Should emit a new glyph since it's not a duplicate and confidence >= threshold
    assert len(res["new_glyphs_generated"]) == 1

    payload = fake.persisted_events[0]["payload"]
    assert payload.get("dedup") is False
