from typing import Tuple

# Simple keyword-based signal detection for potential crisis
CRISIS_KEYWORDS = {"suicidal", "kill myself", "end my life", "self harm", "hurt myself", "can't go on", "overdose"}


def detect_crisis(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in CRISIS_KEYWORDS)


def get_crisis_resources(locale: str = "US") -> Tuple[str, str]:
    """
    Returns a tuple of (label, details).
    Keep content high-level and non-directive beyond immediate safety.
    """
    if locale.upper() == "US":
        return (
            "U.S. Crisis Support",
            "Dial 988 (Suicide & Crisis Lifeline), text HOME to 741741, or call 911 for emergencies.",
        )
    return ("Crisis Support", "Please contact your local emergency services or a trusted crisis line in your region.")
