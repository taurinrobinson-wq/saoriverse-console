import importlib

# Rebind cleaned implementations from tools so imports from the
# top-level `ritual_capsule_processor` module resolve to the
# canonical classes in `tools.ritual_capsule_processor`.
_tools = importlib.import_module('tools.ritual_capsule_processor')

GlyphObject = _tools.GlyphObject
RitualCapsuleProcessor = _tools.RitualCapsuleProcessor

# NOTE: A temporary runtime shim was used during early repairs to add a
# `to_dict` method onto `GlyphObject`. The shim has been removed now that
# `tools.ritual_capsule_processor` provides a proper implementation.
# If defensive behavior is required, prefer explicit checks rather than
# mutating classes from another module.
