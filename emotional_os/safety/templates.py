from typing import Optional


class SanctuaryTemplates:
    """Pre-approved compassionate responses for Sanctuary Mode."""

    @staticmethod
    def compassionate_acknowledgment(tone: Optional[str] = None) -> str:
        base = (
            "I'm here with you. What you're sharing matters, and you won't be rejected or shamed for it. "
            "Your experience deserves care and gentle attention."
        )
        tone_map = {
            "grief": " It's okay to feel the full weight of this.",
            "containment": " You don't have to carry it all alone right now.",
            "insight": " You're noticing something true—go slowly and be kind to yourself.",
            "joy": " Your joy is welcome here, too.",
            "longing": " The ache you feel points to what matters most.",
        }
        return base + tone_map.get((tone or "").lower(), "")

    @staticmethod
    def gentle_boundaries() -> str:
        return (
            "If this brings up a lot, we can slow down or focus on one small piece at a time. "
            "You get to set the pace."
        )

    @staticmethod
    def crisis_footer(locale: str = "US") -> str:
        if locale.upper() == "US":
            return (
                "\n\nIf you're in immediate danger or thinking about harming yourself, consider reaching out right now: "
                "Dial 988 (U.S. Suicide & Crisis Lifeline), text HOME to 741741, or call 911 if there's an emergency."
            )
        # Generic fallback
        return (
            "\n\nIf you're in immediate danger or considering self-harm, please reach out to your local emergency services "
            "or a trusted crisis line in your region."
        )

    @staticmethod
    def build_response(tone: Optional[str], include_crisis: bool, locale: str = "US") -> str:
        parts = [
            SanctuaryTemplates.compassionate_acknowledgment(tone),
            SanctuaryTemplates.gentle_boundaries(),
        ]
        if include_crisis:
            parts.append(SanctuaryTemplates.crisis_footer(locale))
        return " ".join(parts)
