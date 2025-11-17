import os
import json
from datetime import datetime

from learning.clarification_memory import record_correction, suggest_for_input, DEFAULT_PATH
from tools.supabase_integration import create_local_processor


def test_clarification_roundtrip():
    # Use a unique trigger so we don't collide with existing memory
    trigger = f"pytest-clarify-{datetime.utcnow().isoformat()}"
    # Record a correction into the clarification memory
    record_correction(
        trigger=trigger,
        clarified_as='test_intent',
        original_input=trigger,
        system_response='debug-response',
        user_clarification='test_intent',
        metadata={'source': 'pytest'}
    )

    # Ensure suggest_for_input can find it
    suggestion = suggest_for_input(trigger, min_count=1)
    assert suggestion is not None, "suggest_for_input should return the recorded suggestion"
    assert suggestion.get('suggestion') == 'test_intent'

    # Create local processor and process the trigger
    proc = create_local_processor()
    res = proc.process_emotional_input(
        trigger, prefer_ai=False, privacy_mode=True)

    # Expect the clarification to be surfaced in the result
    assert 'clarification_applied' in res or 'clarification_provenance' in res, "Clarification should be applied/surfaced"
    # If provenance exists, check basic fields
    prov = res.get('clarification_provenance')
    if prov:
        assert prov.get('trigger') is not None
        assert prov.get('suggestion') == 'test_intent'
        assert 'applied_at' in prov

    # Cleanup is intentionally a no-op (append-only memory). This test appends a single record.
