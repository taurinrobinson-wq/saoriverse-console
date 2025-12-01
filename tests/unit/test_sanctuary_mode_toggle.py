import pytest

from emotional_os.core import signal_parser as sp


def test_parse_input_uses_sanctuary_when_enabled(monkeypatch):
    # Make generate_contextual_response deterministic and fast
    monkeypatch.setattr(sp, "generate_contextual_response", lambda *a, **k: ("BASE_RESPONSE", {}))
    # Replace ensure_sanctuary_response so we can detect it's invoked
    monkeypatch.setattr(
        sp, "ensure_sanctuary_response", lambda input_text, base_response, tone=None: "SANCTUARY_WRAPPED"
    )

    # Force sanctuary mode on
    monkeypatch.setattr(sp, "SANCTUARY_MODE", True)

    result = sp.parse_input("I feel tired and small", "velonix_lexicon.json", db_path=":memory:")
    assert result["voltage_response"] == "SANCTUARY_WRAPPED"


def test_parse_input_does_not_wrap_when_disabled(monkeypatch):
    # Ensure contextual response is deterministic
    monkeypatch.setattr(sp, "generate_contextual_response", lambda *a, **k: ("BASE_RESPONSE", {}))
    # Ensure ensure_sanctuary_response would produce a different value if called
    monkeypatch.setattr(
        sp, "ensure_sanctuary_response", lambda input_text, base_response, tone=None: "SANCTUARY_WRAPPED"
    )

    # Force sanctuary mode off and ensure input is not considered sensitive
    monkeypatch.setattr(sp, "SANCTUARY_MODE", False)
    monkeypatch.setattr(sp, "is_sensitive_input", lambda t: False)

    result = sp.parse_input("I feel tired and small", "velonix_lexicon.json", db_path=":memory:")
    # Since SANCTUARY_MODE is False and is_sensitive_input is False, ensure the sanctuary wrapper was NOT applied
    assert result["voltage_response"] != "SANCTUARY_WRAPPED"
