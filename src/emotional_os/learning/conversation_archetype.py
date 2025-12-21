"""Bridge to `emotional_os_learning.conversation_archetype`.

Re-exports the implementation from `src/emotional_os_learning` so
modules importing `emotional_os.learning.conversation_archetype` get
the canonical implementation.
"""
try:
    from emotional_os_learning.conversation_archetype import *  # noqa: F401,F403
except Exception as exc:
    raise ImportError(
        "Unable to load emotional_os_learning.conversation_archetype; ensure src/emotional_os_learning is present"
    ) from exc
