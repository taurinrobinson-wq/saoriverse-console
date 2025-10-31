from typing import Optional
import json
import os

from .config import SANCTUARY_MODE, DEFAULT_LOCALE, INCLUDE_CRISIS_RESOURCES
from .templates import SanctuaryTemplates
from .sanctuary_handler import classify_risk, build_consent_prompt, get_crisis_resources
from .redaction import redact_text

# Load trauma lexicon once
_TRAUMA_LEXICON_PATH = os.path.join(os.path.dirname(__file__), "trauma_lexicon.json")
try:
    with open(_TRAUMA_LEXICON_PATH, "r", encoding="utf-8") as f:
        _TRAUMA_LEXICON = json.load(f)
except Exception:
    _TRAUMA_LEXICON = {"categories": {}}


def is_sensitive_input(text: str) -> bool:
    """Return True if input likely contains sensitive/trauma topics."""
    lowered = text.lower()
    for words in _TRAUMA_LEXICON.get("categories", {}).values():
        for w in words:
            if w in lowered:
                return True
    return False


def ensure_sanctuary_response(
    input_text: str,
    base_response: str,
    tone: Optional[str] = None,
    locale: str = DEFAULT_LOCALE
) -> str:
    """
    Wrap any response with Sanctuary posture if enabled or if input is sensitive.
    - Always compassionate welcome
    - Gentle boundaries
    - Non-intrusive consent prompt when risk is detected (no automatic routing)
    """
    sanctuary = SanctuaryTemplates.build_response(tone=tone, include_crisis=False, locale=locale)

    # Conservative risk classification; if any risk detected, offer a consent prompt rather than auto-escalating
    risk = classify_risk(input_text)
    consent_prompt = ""
    if risk != "none":
        consent_prompt = "\n\n" + build_consent_prompt(risk, locale)

    # If config explicitly allows appending crisis resources, include them AFTER user consent text.
    resources_block = ""
    if INCLUDE_CRISIS_RESOURCES and risk == "high":
        label, details = get_crisis_resources(locale)
        resources_block = f"\n\n{label}: {details}"

    if not base_response:
        return sanctuary + consent_prompt + resources_block

    # Combine sanctuary framing + consent prompt + original response
    return f"{sanctuary}{consent_prompt}\n\n{base_response}{resources_block}"


def sanitize_for_storage(text: str) -> str:
    """Apply redaction when persisting content (PII/sensitive)."""
    return redact_text(text)
