"""Shared responder/orchestrator factory adapter.

Expose `make_responder_and_orchestrator(glyphs)` for other modules to
import. Prefer an implementation from `emotional_os`/packaged modules
when available; fall back to the existing tools implementation for
backwards compatibility.
"""
from __future__ import annotations

import logging
logger = logging.getLogger(__name__)


def _import_from_emotional_os():
    try:
        # If emotional_os_learning modules are available in src, construct
        # a sensible factory using the provided classes.
        from emotional_os_learning.subordinate_bot_responder import SubordinateBotResponder
        from emotional_os_learning.dominant_bot_orchestrator import DominantBotOrchestrator
        from emotional_os_learning.proto_glyph_manager import ProtoGlyphManager

        def _make(glyphs):
            # Minimal tiers expected by SubordinateBotResponder
            class DummyTier:
                def wrap_response(self, text, ctx):
                    return text
                def attune_presence(self, text, ctx):
                    return text
                def enrich_with_poetry(self, text, ctx):
                    return text

            responder = SubordinateBotResponder(DummyTier(), DummyTier(), DummyTier(), glyph_library=glyphs)
            proto_mgr = ProtoGlyphManager()
            orchestrator = DominantBotOrchestrator(proto_mgr)
            return responder, orchestrator, proto_mgr

        return _make
    except Exception:
        return None


def _import_from_tools():
    try:
        # Tools may be on sys.path in utilities; import the function there
        from interactive_learning_ui import make_responder_and_orchestrator as f
        return f
    except Exception:
        return None


_impl = _import_from_emotional_os() or _import_from_tools()

if _impl is None:
    logger.warning("No responder factory found in emotional_os or tools; make_responder_and_orchestrator will raise if called.")


def make_responder_and_orchestrator(glyphs):
    """Create responder, orchestrator, proto_mgr triple.

    Calls into the preferred implementation found at import time. If no
    implementation is available, raises RuntimeError.
    """
    if _impl is None:
        raise RuntimeError("Responder factory not available in this environment.")
    return _impl(glyphs)
