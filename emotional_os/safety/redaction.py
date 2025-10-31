import re

EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_PATTERN = re.compile(r"\b\+?\d[\d\s().-]{7,}\b")

# Limited sensitive-term redaction to avoid storing explicit details
SENSITIVE_TERMS = [
    "assault", "abuse", "coercion", "nonconsensual", "violation", "grooming",
]

REPLACEMENTS = {
    EMAIL_PATTERN: "[redacted-email]",
    PHONE_PATTERN: "[redacted-phone]",
}


def redact_text(text: str) -> str:
    """Redact PII and sensitive terms for storage or logs."""
    redacted = text
    for pattern, replacement in REPLACEMENTS.items():
        redacted = pattern.sub(replacement, redacted)

    # Replace sensitive terms with neutral markers
    for term in SENSITIVE_TERMS:
        redacted = re.sub(rf"\b{re.escape(term)}\b", "[sensitive]", redacted, flags=re.IGNORECASE)

    return redacted
