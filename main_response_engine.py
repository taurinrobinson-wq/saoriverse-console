"""Thin wrapper exposing the canonical response entrypoint.

This module forwards to `src.response_generator.process_user_input` but
also exposes a top-level `_clarify_trace` slot tests can monkeypatch. When
set, the wrapper ensures the underlying engine uses the same trace
instance so integration tests can inject a test store.
"""

from typing import Any, Dict, Optional

import src.response_generator as _rg

# Exposed hook used by tests to inject a ClarificationTrace instance.
# Default to the engine's own trace object.
_clarify_trace = getattr(_rg, "_clarify_trace", None)


def process_user_input(user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
	# Ensure the response_generator uses the injected clarification trace
	try:
		if _clarify_trace is not None and getattr(_rg, "_clarify_trace", None) is not _clarify_trace:
			_rg._clarify_trace = _clarify_trace
	except Exception:
		pass
	return _rg.process_user_input(user_input, context)


__all__ = ["process_user_input", "_clarify_trace"]
