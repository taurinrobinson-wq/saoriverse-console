"""
PleadingFactory — Factory for Instantiating Pleading Types

Automatically selects the correct pleading class (Motion, Opposition, Reply, Declaration)
based on a 'type' field in the JSON input.
"""

from .motion import Motion
from .opposition import Opposition
from .reply import Reply
from .declaration import Declaration


class PleadingFactory:
    """
    Factory for instantiating the correct pleading class
    based on the 'type' field in the input JSON.

    Supported types:
        - motion: Motion (with optional Notice of Motion)
        - opposition: Opposition to a Motion
        - reply: Reply in support of or opposing a Motion
        - declaration: Declaration in support of a pleading
    """

    TYPES = {
        "motion": Motion,
        "opposition": Opposition,
        "reply": Reply,
        "declaration": Declaration,
    }

    def __init__(self, config_path: str, citation_path: str):
        """
        Initialize PleadingFactory with config file paths.

        Args:
            config_path: Path to california_civil.yaml
            citation_path: Path to california_civil_citation.yaml
        """
        self.config_path = config_path
        self.citation_path = citation_path

    def create(self, data: dict) -> object:
        """
        Returns an instance of the appropriate pleading class.

        Args:
            data: Dictionary with 'type' field specifying pleading type.
                  Supported types: motion, opposition, reply, declaration

        Returns:
            Instance of Motion, Opposition, Reply, or Declaration

        Raises:
            ValueError: If 'type' field is missing or unknown
        """
        pleading_type = data.get("type", "").lower().strip()

        if not pleading_type:
            raise ValueError(
                "Missing required 'type' field in data. "
                "Supported types: motion, opposition, reply, declaration"
            )

        if pleading_type not in self.TYPES:
            supported = ", ".join(self.TYPES.keys())
            raise ValueError(
                f"Unknown pleading type: '{pleading_type}'. "
                f"Supported types: {supported}"
            )

        klass = self.TYPES[pleading_type]
        return klass(self.config_path, self.citation_path)
