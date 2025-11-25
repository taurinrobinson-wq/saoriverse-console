import sqlite3
import json
import os
import time

from pathlib import Path

import pytest

from emotional_os.adapter import clarification_store, clarification_trace


def test_db_lock_triggers_jsonl_fallback(tmp_path, monkeypatch):
    # Prepare test DB and JSONL paths
    db_path = tmp_path / "test_clar.db"
    jsonl_path = tmp_path / "disambiguation_memory.jsonl"

    # Ensure paths are strings for sqlite
    db_path_str = str(db_path)

    # Create store (this will initialize the DB schema)
    store = clarification_store.ClarificationStore(db_path=db_path)

    # Create an exclusive lock on the DB in this test process
    conn_lock = sqlite3.connect(
        db_path_str, timeout=1, check_same_thread=False)
    try:
        # Acquire exclusive lock by beginning an exclusive transaction
        conn_lock.execute("BEGIN EXCLUSIVE")

        # Monkeypatch get_default_store in clarification_trace to return our store instance
        # Allow creating the attribute if it does not exist yet.
        monkeypatch.setattr(clarification_trace,
                            "get_default_store", lambda: store, raising=False)

        # Instantiate ClarificationTrace with jsonl fallback path
        trace = clarification_trace.ClarificationTrace(store_path=jsonl_path)

        # Prepare a correction input that matches TRIGGER_PATTERNS (starts with 'No, I meant')
        user_input = "No, I meant I was talking about my dad's silence"
        context = {
            "last_user_input": "I was talking about my dad's silence",
            "last_system_response": "Could you say more?",
            "conversation_id": "test-convo",
            "user_id": "tester",
        }

        # Call detect_and_store; because DB is locked, the worker insert should fail/timeout
        # and the code should fall back to appending to the JSONL file
        res = trace.detect_and_store(user_input, context=context)
        assert res is True

        # Give a tiny moment for background code to write fallback (if any)
        time.sleep(0.1)

        # JSONL file should exist and contain at least one JSON object with our clarification
        assert jsonl_path.exists(), "JSONL fallback file was not created"
        lines = jsonl_path.read_text(encoding="utf8").strip().splitlines()
        assert len(lines) >= 1

        last = json.loads(lines[-1])
        assert last.get("user_clarification") and "No, I meant" in last.get(
            "user_clarification")
        assert last.get("conversation_id") == "test-convo"
        assert last.get("user_id") == "tester"

    finally:
        # release lock
        try:
            conn_lock.rollback()
        except Exception:
            pass
        conn_lock.close()
