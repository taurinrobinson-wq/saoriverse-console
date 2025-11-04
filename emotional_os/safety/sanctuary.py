import json
import os
from typing import Optional

from .config import DEFAULT_LOCALE, INCLUDE_CRISIS_RESOURCES
from .redaction import redact_text
from .sanctuary_handler import build_consent_prompt, classify_risk, get_crisis_resources
from .templates import SanctuaryTemplates
from difflib import SequenceMatcher
import re

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

    # If the base_response already contains key sanctuary phrases, avoid repeating the full
    # sanctuary framing. This prevents duplication when dynamic composers already include
    # compassionate openers or gentle-boundary language.

    # Heuristic 1: exact sentinel phrase match (fast path)
    sentinel_phrases = [
        "I'm here with you",
        "What you're sharing matters",
        "You get to set the pace",
        "Your experience deserves care",
        "If this brings up a lot, we can slow down"
    ]

    base_lower = base_response.lower() if base_response else ""
    contains_sanctuary_text = any(phrase.lower() in base_lower for phrase in sentinel_phrases)

    # Heuristic 2: try pattern and token heuristics to catch common paraphrases.
    # This captures cases like "I'm here for you" (vs "I'm here with you")
    # or short rephrasings that SequenceMatcher struggles to match.
    # Use regexes for common patterns and a token-distance fallback.
    def similar(a: str, b: str) -> float:
        try:
            return SequenceMatcher(None, a, b).ratio()
        except Exception:
            return 0.0

    fuzzy_match_found = False
    try:
        # quick regex-based paraphrase checks
        # e.g., "i'm here for you", "i am here for you", "i'm here with you"
        if re.search(r"i('?m| am) here (with|for) you", base_lower):
            fuzzy_match_found = True
        # other common compassionate fragments
        if not fuzzy_match_found and any(phrase.lower() in base_lower for phrase in [
            "you get to set the pace",
            "what you're sharing matters",
            "your experience deserves care",
            "we can slow down"
        ]):
            fuzzy_match_found = True
        # token proximity fallback: both 'here' and 'you' nearby
        if not fuzzy_match_found and 'here' in base_lower and 'you' in base_lower:
            try:
                idx_here = base_lower.index('here')
                idx_you = base_lower.index('you')
                if abs(idx_here - idx_you) < 40:
                    fuzzy_match_found = True
            except Exception:
                pass

        canonical_ack = SanctuaryTemplates.compassionate_acknowledgment(tone)
        canonical_bound = SanctuaryTemplates.gentle_boundaries()
        # Compare base response to canonical ack and boundaries; if similar enough, treat as containing sanctuary text
        # Use lower thresholds because base responses are often much shorter than the canonical blocks.
        if similar(base_lower, canonical_ack.lower()) > 0.45 or similar(base_lower, canonical_bound.lower()) > 0.45:
            fuzzy_match_found = True
        else:
            # Also compare shorter sentinel fragments with fuzzy threshold
            for frag in sentinel_phrases:
                if similar(base_lower, frag.lower()) > 0.5:
                    fuzzy_match_found = True
                    break
    except Exception:
        fuzzy_match_found = False

    if contains_sanctuary_text or fuzzy_match_found:
        # The base response already expresses sanctuary posture; append consent/resources only.
        return f"{base_response}{consent_prompt}{resources_block}"

    # Default: prepend full sanctuary framing to ensure compassionate context
    return f"{sanctuary}{consent_prompt}\n\n{base_response}{resources_block}"


def sanitize_for_storage(text: str) -> str:
    """Apply redaction when persisting content (PII/sensitive)."""
    return redact_text(text)
