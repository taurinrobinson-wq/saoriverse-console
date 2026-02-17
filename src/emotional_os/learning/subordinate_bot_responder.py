#!/usr/bin/env python3
"""Bridge to `emotional_os_learning.subordinate_bot_responder`."""
try:
    from emotional_os_learning.subordinate_bot_responder import *  # noqa: F401,F403
except Exception as exc:
    raise ImportError(
        "Unable to load emotional_os_learning.subordinate_bot_responder; ensure src/emotional_os_learning is present"
    ) from exc
