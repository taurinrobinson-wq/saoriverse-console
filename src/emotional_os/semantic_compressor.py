"""Semantic compression layer: extract emotional domains and produce a concise, attuned reflection.

This module implements a deterministic extractor and compressor that turns
lexical + structural cues into a short two-sentence human-sounding reply.
"""
from typing import Dict
import re


class SemanticCompressor:
    def __init__(self):
        # domain keys we may populate
        self.domain_keys = [
            "exhaustion",
            "stress",
            "blocked_joy",
            "contrast",
            "temporal_pressure",
            "disappointment",
        ]

    def extract_domains(self, message: str, affect: Dict | None = None) -> Dict[str, bool]:
        """Return a dict of detected emotional domains (booleans).

        message: raw user message text
        affect: optional affect dict with keys like `valence` to help disambiguate
        """
        text = (message or "").lower()
        domains = {k: False for k in self.domain_keys}

        # exhaustion
        if re.search(r"\b(tired|exhausted|weary|drained)\b", text):
            domains["exhaustion"] = True

        # stress
        if re.search(r"\b(stress|stressed|pressure|overwhelm|overwhelmed)\b", text):
            domains["stress"] = True
        if affect and isinstance(affect, dict):
            try:
                if float(affect.get("valence", 0.0)) < -0.2:
                    domains["stress"] = True
            except Exception:
                pass

        # blocked access to joy
        if re.search(r"\b(can(?:'t| not) (?:enjoy|feel|access))\b", text) or "can't even enjoy" in text:
            domains["blocked_joy"] = True

        # contrast: mentions that something should be different
        if re.search(r"\b(should|supposed to|suppose to|ought to|supposedly)\b", text) or re.search(r"\b(though|but)\b", text):
            domains["contrast"] = True

        # temporal pressure
        if re.search(r"\b(in \d+ (?:days|hours)|soon|coming up|two days|tomorrow)\b", text):
            domains["temporal_pressure"] = True

        # disappointment: inability to enjoy + can't / could not
        if re.search(r"\b(can(?:'t| not) .*enjoy|disappoint|disappointed)\b", text):
            domains["disappointment"] = True

        return domains

    def compress(self, domains: Dict[str, bool], message: str | None = None) -> str:
        """Produce a concise two-sentence reflection from the domains.

        The first sentence synthesizes emotional geometry; the second offers presence.
        """
        parts = []

        if domains.get("exhaustion"):
            parts.append("you're worn down")

        if domains.get("stress"):
            parts.append("the stress is piling on")

        if domains.get("blocked_joy"):
            parts.append("and you can't seem to access the good parts")

        if domains.get("contrast"):
            parts.append("even though this time is supposed to feel different")

        if domains.get("temporal_pressure"):
            parts.append("and the closeness of it all adds pressure")

        if not parts:
            # Fallback short reflection using a minimal echo of the message
            short = (message or "").strip()
            if short:
                first = f"That sounds really hard — {short.split('.\n')[0][:120]}"
            else:
                first = "You're carrying a lot right now."
            second = "I'm here with you if you want to talk it through."
            return f"{first}. {second}"

        # Join parts into a natural first sentence
        first_sentence = ", ".join(parts).strip()
        # Capitalize first letter and end with period
        if not first_sentence.endswith("."):
            first_sentence = first_sentence[0].upper() + first_sentence[1:] + "."

        second_sentence = "I'm here with you if you want to talk it through."
        return f"{first_sentence} {second_sentence}"
