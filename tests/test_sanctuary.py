import sys
import pytest

# Ensure project root is importable
sys.path.insert(0, '/workspaces/saoriverse-console')

import emotional_os.safety.sanctuary as sanctuary_mod
from emotional_os.safety.sanctuary import ensure_sanctuary_response


def test_paraphrase_dedupe():
    input_text = "I'm feeling overwhelmed and also oddly grateful."
    base = "I'm here for you — that sounds heavy and important."

    res = ensure_sanctuary_response(input_text, base, tone='calm')

    # The base response should be returned verbatim (no duplicated canonical sanctuary opener)
    assert base in res
    # canonical sanctuary opening (exact canonical phrase) should not be present
    assert "i'm here with you" not in res.lower()


def test_non_compassionate_gets_sanctuary():
    input_text = "Can you explain how the API auth works?"
    base = "Here are some troubleshooting steps and a technical explanation about your situation."

    res = ensure_sanctuary_response(input_text, base, tone='calm')

    # For non-compassionate base responses, the canonical sanctuary framing should be prepended
    assert "i'm here with you" in res.lower() or "what you're sharing matters" in res.lower()
    assert base in res


def test_high_risk_appends_consent_and_resources(monkeypatch):
    # Force classify_risk to return 'high' and stub consent/resources so we can assert exact text
    monkeypatch.setattr(sanctuary_mod, 'classify_risk', lambda x: 'high')
    monkeypatch.setattr(sanctuary_mod, 'build_consent_prompt', lambda r, l: '[CONSENT]')
    monkeypatch.setattr(sanctuary_mod, 'get_crisis_resources', lambda l: ('RES_LABEL', 'RES_DETAILS'))
    # Ensure resources inclusion flag is True for this test
    monkeypatch.setattr(sanctuary_mod, 'INCLUDE_CRISIS_RESOURCES', True)

    input_text = "I might hurt myself"
    base = "I'm here for you — that sounds heavy and important."

    res = ensure_sanctuary_response(input_text, base, tone='calm')

    # base should remain and consent + resources appended
    assert base in res
    assert '\n\n[CONSENT]' in res
    assert '\n\nRES_LABEL: RES_DETAILS' in res
