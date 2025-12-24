"""Domain extractor for FirstPerson pipeline.

Extracts emotional domains (exhaustion, stress, blocked_joy, etc.) from message and affect.
Each domain is a float in [0.0, 1.0] indicating presence/intensity.
"""

from typing import Optional


class DomainExtractor:
    """Extract emotional domains from message and affect metadata."""

    # Lexical markers for each domain
    DOMAIN_MARKERS = {
        "exhaustion": [
            "exhausted",
            "tired",
            "weary",
            "drained",
            "worn out",
            "burned out",
            "depleted",
            "no energy",
            "weight",
            "carrying",
            "burden",
            "heavy",
        ],
        "stress": [
            "stress",
            "stressed",
            "pressure",
            "overwhelmed",
            "anxious",
            "worried",
            "concern",
            "tension",
            "tight",
        ],
        "blocked_joy": [
            "can't feel",
            "numb",
            "blocked",
            "can't enjoy",
            "dulled",
            "disconnected",
            "empty",
            "hollow",
            "void",
        ],
        "contrast": [
            "everyone else",
            "different from",
            "stuck in place",
            "watching",
            "rushing by",
            "out of sync",
            "misaligned",
        ],
        "temporal_pressure": [
            "in two days",
            "deadline",
            "soon",
            "coming up",
            "running out",
            "limited time",
            "before",
            "christmas",
            "new year",
        ],
        "disappointment": [
            "disappointed",
            "let down",
            "expected",
            "not what",
            "failed",
            "didn't work",
            "didn't happen",
        ],
        "isolation": [
            "alone",
            "lonely",
            "isolated",
            "nobody",
            "no one",
            "on my own",
            "by myself",
        ],
    }

    # Affect tone to domain mappings (tone -> primary domain boost)
    TONE_TO_DOMAIN = {
        "exhausted": {"exhaustion": 0.8},
        "tired": {"exhaustion": 0.7},
        "overwhelmed": {"stress": 0.8, "exhaustion": 0.5},
        "sardonic": {"disappointment": 0.6},
        "sad": {"isolation": 0.6, "disappointment": 0.5},
        "uncertain": {"stress": 0.5},
        "warm": {"blocked_joy": 0.0},  # Positive tone negates blocked_joy
    }

    def extract(
        self, message: str, affect: Optional[dict] = None
    ) -> dict:
        """Extract emotional domains from message and affect.

        Args:
            message: User's message text.
            affect: Optional {tone, valence, arousal} from pipeline.

        Returns:
            {
                "exhaustion": float,
                "stress": float,
                "blocked_joy": float,
                "contrast": float,
                "temporal_pressure": float,
                "disappointment": float,
                "isolation": float,
            }
        """
        affect = affect or {}
        message_lower = message.lower() if message else ""

        # Initialize domains
        domains = {
            "exhaustion": 0.0,
            "stress": 0.0,
            "blocked_joy": 0.0,
            "contrast": 0.0,
            "temporal_pressure": 0.0,
            "disappointment": 0.0,
            "isolation": 0.0,
        }

        # 1. Score each domain by lexical markers
        for domain, markers in self.DOMAIN_MARKERS.items():
            matched = sum(1 for marker in markers if marker in message_lower)
            if matched > 0:
                # 1 marker: 0.5, 2: 0.7, 3+: 0.9
                domains[domain] = min(0.9, 0.5 + (matched * 0.1))

        # 2. Boost domains based on affect tone
        tone = affect.get("tone", "").lower() if isinstance(affect, dict) else ""
        if tone in self.TONE_TO_DOMAIN:
            boosts = self.TONE_TO_DOMAIN[tone]
            for domain, boost in boosts.items():
                domains[domain] = min(1.0, domains[domain] + boost)

        # 3. Use valence to adjust blocked_joy
        valence = 0.0
        try:
            valence = float(affect.get("valence", 0.0)) if isinstance(affect, dict) else 0.0
        except (ValueError, TypeError):
            valence = 0.0

        # Negative valence increases blocked_joy risk
        if valence < 0.4:
            domains["blocked_joy"] = min(1.0, domains["blocked_joy"] + 0.3)

        # Positive valence decreases blocked_joy
        if valence > 0.6:
            domains["blocked_joy"] = max(0.0, domains["blocked_joy"] - 0.4)

        # 4. Normalize all domains to [0.0, 1.0]
        for domain in domains:
            domains[domain] = max(0.0, min(1.0, domains[domain]))

        return domains
