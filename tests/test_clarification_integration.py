import json
from pathlib import Path

import pytest

import main_response_engine as mre
from emotional_os.adapter.clarification_trace import ClarificationTrace


def test_acknowledgement_and_biasing(tmp_path: Path):
    store = tmp_path / "mem_integ.jsonl"
    ct = ClarificationTrace(store_path=store)

    # Monkeypatch the engine's clarify trace singleton to use our test store
    mre._clarify_trace = ct

    original = "how are you?"

    # Baseline response for the original phrase
    baseline = mre.process_user_input(original, {})

    # Now simulate a system response followed by a user clarification that sets corrected intent
    clarification = "No, I meant how are you feeling?"
    ctx = {"last_user_input": original, "last_system_response": baseline, "inferred_intent": "emotional_checkin"}

    resp = mre.process_user_input(clarification, ctx)
    # Acknowledgement prefix should be present
    assert "Thanks for clarifying" in resp

    # Now call the original phrase again; lookup should bias phase to initiatory
    biased = mre.process_user_input(original, {})
    assert biased != baseline
    # initiatory templates include 'tell me' or 'can you tell me more'
    assert ("tell me" in biased.lower()) or ("can you tell me more" in biased.lower())
