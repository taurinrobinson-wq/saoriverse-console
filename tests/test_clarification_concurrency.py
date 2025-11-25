import sqlite3
import json
import os
import time
from pathlib import Path
import concurrent.futures

import pytest

from emotional_os.adapter import clarification_store, clarification_trace


def test_concurrent_inserts_use_fallback_under_timeout(tmp_path, monkeypatch):
    """Fire multiple concurrent clarification inserts with a short insert timeout.

    Expectation: all calls return True, and total stored records (DB rows + JSONL lines)
    equals the number of attempts.
    """
    N = 20

    db_path = tmp_path / "concurrent_clar.db"
    jsonl_path = tmp_path / "disambiguation_memory.jsonl"

    # create store (initializes DB)
    store = clarification_store.ClarificationStore(db_path=db_path)

    # ensure small insert timeout so worker often falls back
    monkeypatch.setenv("CLARIFICATION_DB_INSERT_TIMEOUT", "0.05")

    # ensure the store used by ClarificationTrace is our store
    monkeypatch.setattr(clarification_trace,
                        "get_default_store", lambda: store, raising=False)

    trace = clarification_trace.ClarificationTrace(store_path=jsonl_path)

    context_template = {
        "last_system_response": "Could you say more?",
        "conversation_id": "concurrent-test",
        "user_id": "tester",
    }

    def send(i):
        ui = f"No, I meant clarification {i}"
        ctx = dict(context_template)
        ctx["last_user_input"] = f"I said thing {i}"
        try:
            return trace.detect_and_store(ui, context=ctx)
        except Exception as e:
            return e

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        futures = [ex.submit(send, i) for i in range(N)]
        for f in concurrent.futures.as_completed(futures, timeout=10):
            results.append(f.result())

    # all results should be True (not exceptions)
    assert all(
        r is True for r in results), f"Some calls failed: {[r for r in results if r is not True]}"

    # give background fallback writes a moment
    time.sleep(0.2)

    # count JSONL lines
    jsonl_count = 0
    if jsonl_path.exists():
        jsonl_count = len([ln for ln in jsonl_path.read_text(
            encoding="utf8").splitlines() if ln.strip()])

    # count DB rows
    conn = sqlite3.connect(str(store.db_path), timeout=1,
                           check_same_thread=False)
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(1) FROM clarifications")
        row = cur.fetchone()
        db_count = row[0] if row and row[0] is not None else 0
    finally:
        conn.close()

        # Collect triggers from JSONL and DB and assert we have N unique triggers stored
        jsonl_triggers = set()
        if jsonl_path.exists():
            for ln in jsonl_path.read_text(encoding="utf8").splitlines():
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    rec = json.loads(ln)
                except Exception:
                    continue
                if rec.get("trigger"):
                    jsonl_triggers.add(rec.get("trigger"))

        db_triggers = set()
        conn = sqlite3.connect(
            str(store.db_path), timeout=1, check_same_thread=False)
        try:
            cur = conn.cursor()
            cur.execute("SELECT trigger FROM clarifications")
            for row in cur.fetchall():
                if row and row[0]:
                    db_triggers.add(row[0])
        finally:
            conn.close()

        union = jsonl_triggers.union(db_triggers)
        assert len(
            union) == N, f"Expected {N} unique stored triggers, found {len(union)} (jsonl={len(jsonl_triggers)}, db={len(db_triggers)})"
