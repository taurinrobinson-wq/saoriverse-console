"""Local configuration helpers and feature guards.

This module centralizes small flags used to disable remote AI in
local/dev environments. Defaults are conservative (remote disabled).
"""
import os


def use_remote_ai() -> bool:
    """Return True when remote AI usage is explicitly allowed.

    Priority: environment variable `ALLOW_REMOTE_AI` ("1" to opt-in).
    This keeps local runs safe by default.
    """
    return os.environ.get("ALLOW_REMOTE_AI", "0") == "1"


USE_REMOTE_AI = use_remote_ai()
