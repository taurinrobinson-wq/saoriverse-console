import json
from pathlib import Path

from emotional_os.feedback.feedback_store import FeedbackStore


def test_append_and_load(tmp_path):
    p = tmp_path / "fb.jsonl"
    store = FeedbackStore(p)
    store.append({"rating": 1, "text": "Good"})
    entries = store.load_all()
    assert len(entries) == 1
    assert entries[0]["rating"] == 1
    assert "timestamp" in entries[0]
