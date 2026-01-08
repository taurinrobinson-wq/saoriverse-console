import os

# Global toggle for Sanctuary Mode
SANCTUARY_MODE: bool = os.getenv("SANCTUARY_MODE", "true").lower() in ("1", "true", "yes", "on")

# Default locale for resources (can be extended per user)
DEFAULT_LOCALE: str = os.getenv("SANCTUARY_LOCALE", "US")

# If true, append crisis resources when strong risk signals are detected
# Default to False: resources are opt-in and consent-driven by default
INCLUDE_CRISIS_RESOURCES: bool = os.getenv("SANCTUARY_INCLUDE_CRISIS", "false").lower() in ("1", "true", "yes", "on")

# If true, redact personally identifiable info from stored logs
REDACT_PII_FOR_STORAGE: bool = os.getenv("SANCTUARY_REDACT_PII", "true").lower() in ("1", "true", "yes", "on")
