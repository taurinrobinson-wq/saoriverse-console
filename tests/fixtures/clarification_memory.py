import time
import uuid

# Simple in-memory clarity store for tests
_corrections = {}


def record_correction(trigger_phrase: str, suggested_intent: str, confidence: float):
    """Record a clarification correction for test purposes."""
    rid = str(uuid.uuid4())
    rec = {
        "record_id": rid,
        "trigger_phrase": trigger_phrase,
        "suggested_intent": suggested_intent,
        "confidence": confidence,
        "timestamp": time.time(),
    }
    _corrections[trigger_phrase] = rec
    return rec


def lookup_correction(text: str):
    """Return the correction record if the trigger_phrase appears in text."""
    for trig, rec in _corrections.items():
        if trig in text:
            return rec
    return None


def all_corrections():
    """Return all stored corrections (useful for debugging/tests)."""
    return dict(_corrections)
