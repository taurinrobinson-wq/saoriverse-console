import json
from pathlib import Path

from emotional_os.adapter.clarification_trace import ClarificationTrace


def test_jsonl_only_store_includes_ids_and_truncation(tmp_path: Path):
    jsonl = tmp_path / "fallback.jsonl"
    ct = ClarificationTrace(store_path=jsonl)

    original = "o" * 600
    clarification = "No, I meant " + ("x" * 1200)
    ctx = {
        "last_user_input": original,
        "last_system_response": "Please say more",
        "conversation_id": "conv-123",
        "user_id": "tester",
    }

    ok = ct.detect_and_store(clarification, context=ctx)
    assert ok is True

    data = jsonl.read_text(encoding="utf8").strip().splitlines()
    assert len(data) >= 1
    rec = json.loads(data[-1])
    # ids should be preserved
    assert rec.get("conversation_id") == "conv-123"
    assert rec.get("user_id") == "tester"
    # truncation should enforce limits
    assert len(rec.get("original_input", "")) <= 500
    assert len(rec.get("user_clarification", "")) <= 1000
