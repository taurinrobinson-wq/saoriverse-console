import json
from pathlib import Path

import pytest

from emotional_os.adapter.clarification_trace import ClarificationTrace


def test_detect_and_store_and_jsonl_append(tmp_path: Path):
    store = tmp_path / "mem.jsonl"
    ct = ClarificationTrace(store_path=store)

    original = "how are you?"
    clarification = "No, I meant how are you feeling?"
    ctx = {"last_user_input": original, "last_system_response": "I am fine",
           "inferred_intent": "emotional_checkin"}

    assert ct.detect_and_store(clarification, ctx) is True

    # file should exist and contain one JSON line
    data = store.read_text(encoding="utf8").strip().splitlines()
    assert len(data) == 1
    rec = json.loads(data[0])
    assert rec.get("original_input") == original
    assert rec.get("user_clarification") == clarification
    assert rec.get("corrected_intent") == "emotional_checkin"


def test_lookup_returns_recent_match(tmp_path: Path):
    store = tmp_path / "mem2.jsonl"
    ct = ClarificationTrace(store_path=store)

    original = "How are you"
    clarification = "No, I meant how are you feeling"
    ctx = {"last_user_input": original, "inferred_intent": "emotional_checkin"}
    assert ct.detect_and_store(clarification, ctx)

    # lookup by original phrase
    found = ct.lookup(original)
    assert found is not None
    assert found.get("corrected_intent") == "emotional_checkin"


def test_detection_false_for_non_corrections(tmp_path: Path):
    ct = ClarificationTrace(store_path=tmp_path / "mem3.jsonl")
    assert ct.detect_and_store("I am fine", {}) is False
