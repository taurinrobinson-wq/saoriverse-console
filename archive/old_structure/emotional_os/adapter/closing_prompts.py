"""Small helper module providing closing prompts for stress responses.

Kept purposely minimal and local so tests can run offline.
"""

from __future__ import annotations

import random
from typing import List

# Gentle closing prompts to invite more sharing after an empathetic acknowledgement.
CLOSING_PROMPTS: List[str] = [
    "Do you wanna talk about it?",
    "Want to share more about what's going on?",
    "I'm here if you'd like to unpack it.",
    "Would it help to talk it through?",
    "I'm listening if you want to continue.",
]


def get_closing_prompt() -> str:
    """Return a randomly selected closing prompt.

    Deterministic behavior can be achieved in tests by seeding
    the `random` module or by mocking this function.
    """
    try:
        return random.choice(CLOSING_PROMPTS)
    except Exception:
        # Fallback to first prompt on any error
        return CLOSING_PROMPTS[0]
