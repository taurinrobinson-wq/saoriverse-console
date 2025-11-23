from typing import Optional


class SanctuaryTemplates:
    """Pre-approved compassionate responses for Sanctuary Mode."""

    @staticmethod
    def compassionate_acknowledgment(tone: Optional[str] = None) -> str:
        # Minimal acknowledgment retained (short and non-repetitive).
        # This replaces the previous long paragraph while keeping a
        # concise framing for non-compassionate responses.
        return "What you're sharing matters."

    @staticmethod
    def gentle_boundaries() -> str:
        # Deprecated: suppress the gentle-boundaries sentence so glyph-driven
        # fallbacks do not emit the long repeated message.
        return ""

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
