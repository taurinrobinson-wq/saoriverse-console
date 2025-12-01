import json
import os
from typing import Any, Dict, Tuple

# Lightweight, non-intrusive risk classifier and consent prompt builder
# This module intentionally does NOT perform any automatic routing or external calls.

# Load trauma lexicon for broader signal coverage
_LEXICON_PATH = os.path.join(os.path.dirname(__file__), "trauma_lexicon.json")
try:
    with open(_LEXICON_PATH, "r", encoding="utf-8") as f:
        _LEXICON = json.load(f)
except Exception:
    _LEXICON = {"categories": {}}

# Crisis-like keywords (explicit self-harm language)
_CRISIS_KEYWORDS = {"suicidal", "kill myself", "end my life",
                    "self harm", "hurt myself", "can't go on", "overdose"}


def classify_risk(text: str) -> str:
    """Classify risk as 'none', 'low', 'medium', or 'high'.

    This is intentionally conservative and used only to prompt a consent flow.
    No automatic escalation is performed by this function.
    """
    lowered = text.lower()
    # High risk = explicit self-harm phrases
    for kw in _CRISIS_KEYWORDS:
        if kw in lowered:
            return "high"

    # Medium risk = trauma-related language + strong affect words
    trauma_words = set()
    for words in _LEXICON.get("categories", {}).values():
        trauma_words.update(words)

    trauma_found = any(w in lowered for w in trauma_words)
    intense_words = any(w in lowered for w in [
                        "overwhelming", "crushing", "suffocating", "panic", "flashback"])

    if trauma_found and intense_words:
        return "medium"
    if trauma_found:
        return "low"

    return "none"


def detect_crisis(text: str) -> bool:
    """Return True only if classified as high risk. Kept for backwards compatibility."""
    return classify_risk(text) == "high"


def get_crisis_resources(locale: str = "US") -> Tuple[str, str]:
    """Return high-level crisis resource labels/details. Never used to auto-route.

    Callers should always ask for user consent before presenting or acting on these.
    """
    if locale.upper() == "US":
        return (
            "U.S. Crisis Support",
            "Dial 988 (Suicide & Crisis Lifeline), text HOME to 741741, or call 911 if there's an emergency.",
        )
    return ("Crisis Support", "Please contact local emergency services or a trusted crisis line in your region.")


def build_consent_prompt(risk_level: str, locale: str = "US") -> str:
    """Build a simple consent prompt offering options and staying-with posture.

    This prompt is intentionally neutral and non-directive.
    """
    resources_label, resources_details = get_crisis_resources(locale)

    if risk_level == "high":
        return (
            "I hear words that suggest you might be in immediate distress. I can do a few different things and I want to follow your lead:\n"
            "A) I can stay with you here and keep listening.\n"
            "B) I can offer crisis resources and numbers you can use right now.\n"
            "C) I can guide you through steps to get urgent help (I'll ask your permission first).\n"
            "Which would you prefer? Reply A, B, or C."
        )

    if risk_level == "medium":
        return (
            "It sounds like you're going through a very difficult experience. I can stay with you here and listen, or I can share options and resources if you'd like.\n"
            "Would you like me to share resources right now? Reply Y/N."
        )

    # low / none
    return "If you'd like, I can share some grounding exercises or resources. Would that be helpful? Reply Y/N."


def handle_consent_reply(reply: str, risk_level: str, locale: str = "US") -> dict:
    """Interpret the user's reply to the consent prompt and return an action + response.

    Returns a dictionary:
      { action: 'stay'|'resources'|'escalate'|'decline'|'unknown',
        response: str,
        resources: (label, details) optional,
        log_entry: dict (privacy-safe derived data for logging)
      }

    This function intentionally does NOT collect or store PII. It returns guidance to the caller/UI
    so the UI can ask for explicit permission before any PII is requested.
    """
    r = (reply or "").strip().lower()
    result: Dict[str, Any] = {
        "action": "unknown",
        "response": "",
        "resources": None,
        "log_entry": {
            "risk_level": risk_level,
            "reply": r,
        },
    }

    # Map common affirmative replies
    if r in ("a", "stay", "stay with you", "stay with me", "a)", "a)", "a)"):
        result["action"] = "stay"
        result["response"] = (
            "Okay — I'm here with you. If it helps, tell me what's most pressing right now or we can do a short grounding exercise."
        )
        return result

    if r in ("b", "y", "yes", "b)", "y)"):
        # Share resources
        label, details = get_crisis_resources(locale)
        result["action"] = "resources"
        result["response"] = (
            f"I can share some resources that might help right now:\n{label}: {details}\nWould you like anything else?"
        )
        result["resources"] = (label, details)
        return result

    if r in ("c", "c)", "c )", "escalate", "urgent"):
        # Escalation guidance — ask for explicit permission before collecting any PII
        result["action"] = "escalate"
        result["response"] = (
            "I can help guide you through steps to get urgent help. To do that I may need small details (like your region) —"
            " I will only ask for that if you give permission. Would you like me to guide you through those steps? Reply Y/N."
        )
        return result

    # Handle explicit declines / negative answers
    if r in ("n", "no", "none", "nope"):
        result["action"] = "decline"
        result["response"] = "That's okay — I can stay with you here. If you want resources later, just say so."
        return result

    # If the user typed a short sentence, try to infer intent
    if r.startswith("stay"):
        result["action"] = "stay"
        result["response"] = "Okay — I'm staying with you. Tell me more if you want."
        return result

    if r.startswith("yes") or r.startswith("y"):
        label, details = get_crisis_resources(locale)
        result["action"] = "resources"
        result["response"] = f"I can share resources now: {label}: {details}"
        result["resources"] = (label, details)
        return result

    # Unknown reply
    result["response"] = (
        "I didn't get that — you can reply with A (stay), B (share resources), or C (guide me to urgent help)."
    )
    return result


def make_privacy_safe_log(user_hash: str, risk_level: str, action: str) -> dict:
    """Return a privacy-safe log entry suitable for storage.

    Stores only anonymous identifiers and derived signals, not raw user text.
    """
    return {
        "user_hash": user_hash,
        "risk_level": risk_level,
        "action": action,
        "timestamp": None,  # caller should populate ISO timestamp when writing
    }
