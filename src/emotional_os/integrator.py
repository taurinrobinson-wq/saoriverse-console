"""Integrator for simple testing and wiring of emotional OS modules.

Exposes two convenience functions:
- `try_pun(context)` returns a rendered pun string or empty string
- `try_mutual_joy(context)` returns a mutual joy line

These are intentionally small so they can be imported by the rest of the
system or used in tests/examples.
"""
from .pun_interjector import PunInterjector
from .mutual_joy_handler import MutualJoyHandler


_pun = PunInterjector()
_joy = MutualJoyHandler()


def try_pun(context: dict) -> str:
    """Attempt to compose and render a pun for `context`.

    Returns an empty string when no pun should be produced.
    """
    pun = _pun.compose_pun(context)
    if not pun:
        return ""
    return _pun.render(pun)


def try_mutual_joy(context: dict) -> str:
    """Return a mutual-joy response line appropriate for `context`.

    Always returns a one-paragraph string; may be a period-safe version
    depending on the exclamation decision logic.
    """
    return _joy.choose_template(context)
