import logging
import pytest

from emotional_os.learning.hybrid_learner_v2 import HybridLearnerWithUserOverrides


def test_family_phrases_are_skipped_or_remapped(caplog, tmp_path):
    caplog.set_level(logging.DEBUG)
    # Use an isolated shared_lexicon path so existing repo data doesn't affect the test
    lex_path = tmp_path / "shared_lexicon.json"
    learner = HybridLearnerWithUserOverrides(shared_lexicon_path=str(lex_path))

    # Simulate signal detection with family-related phrases
    user_input = "I'm out with my kids. I'm a little nervous."
    signal = "sensuality"
    phrases = ["with my kids", "my mom", "dad and I"]

    poetic_signals = [
        {
            "signal": signal,
            "confidence": 0.8,
            "keywords": ["kids", "mom", "dad"],
            "metaphors": []
        }
    ]

    # Run enrichment which should skip family phrases for sensuality
    learner._enrich_lexicon_with_signals(user_input, poetic_signals)

    # Assert none of the family phrases were added to sensuality in shared lexicon
    for p in phrases:
        assert p not in learner.shared_lexicon

    # Debug logs should mention skipped family phrases
    assert any(
        "Skipped learning family phrase" in rec.message for rec in caplog.records)
