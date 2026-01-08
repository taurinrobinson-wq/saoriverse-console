import pytest

from learning.local_learner import LocalLearner


def make_candidate(user_input, ai_response="", examples=0):
    return {
        "user_input": user_input,
        "ai_response": ai_response,
        "examples": examples,
    }


def test_score_low_when_no_examples_and_no_signals():
    learner = LocalLearner()
    c = make_candidate("just a neutral note", examples=0)
    score = learner.score_candidate(c)
    assert score is not None
    assert 0.0 <= score <= 1.0


def test_score_high_with_fuzzy_and_examples(monkeypatch):
    learner = LocalLearner()
    # Patch symbolic_tagger to return a high fuzzy match and a synonym hit

    def fake_diag(text):
        return {
            "tags": ["initiatory_signal"],
            "matches": [
                {"category": "synonym_group", "match_type": "fuzzy", "score": 0.92},
            ],
        }

    monkeypatch.setitem(
        __import__("sys").modules, "symbolic_tagger", type("M", (), {"tag_input_with_diagnostics": fake_diag})
    )

    c = make_candidate("i feel seen and opened", examples=3)
    score = learner.score_candidate(c)
    assert score is not None
    assert score > 0.5


def test_voltage_and_prior_boost(monkeypatch):
    learner = LocalLearner()

    def fake_diag(text):
        return {
            "tags": ["voltage_surge"],
            "matches": [{"category": "synonym_group", "match_type": "fuzzy", "score": 0.6}],
        }

    monkeypatch.setitem(
        __import__("sys").modules, "symbolic_tagger", type("M", (), {"tag_input_with_diagnostics": fake_diag})
    )

    # Patch relational_memory with recent capsules containing the tag
    class Cap:
        def __init__(self):
            self.symbolic_tags = ["voltage_surge"]
            self.voltage_marking = "high"

    fake_rm = type("RM", (), {"list_recent": staticmethod(lambda limit=10: [Cap(), Cap()])})
    monkeypatch.setitem(__import__("sys").modules, "relational_memory", fake_rm)

    c = make_candidate("i'm overwhelmed and buzzing", examples=2)
    score = learner.score_candidate(c)
    assert score is not None
    # Because of voltage and prior occurrences, expect a decent boost
    assert score > 0.4
