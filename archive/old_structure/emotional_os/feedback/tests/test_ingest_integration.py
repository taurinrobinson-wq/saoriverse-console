import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from emotional_os.feedback import api, store


def test_post_creates_feedback_file(tmp_path, monkeypatch):
    # Redirect store.FEEDBACK_PATH to a temp file so tests do not touch repo files
    test_file = tmp_path / "feedback.jsonl"
    monkeypatch.setattr(store, "FEEDBACK_PATH", str(test_file))

    client = TestClient(api.app)
    payload = {"message": "Testing feedback", "rating": 5, "metadata": {"test": True}}
    resp = client.post("/ingest", json=payload)
    assert resp.status_code == 200

    # Ensure file exists and contains one or more lines; last line should match
    assert test_file.exists()
    text = test_file.read_text(encoding="utf-8").strip()
    assert text != ""
    lines = [l for l in text.splitlines() if l.strip()]
    assert len(lines) >= 1
    parsed = json.loads(lines[-1])
    assert parsed["message"] == "Testing feedback"
    assert parsed["rating"] == 5
