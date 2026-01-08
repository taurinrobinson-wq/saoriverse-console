"""
Centralized path management for Emotional OS.

Provides flexible path resolution with sensible defaults and fallbacks.
Handles both local and cloud deployments.
"""

import os
from pathlib import Path
from typing import Optional


class PathManager:
    """Manages all file paths for the Emotional OS system."""

    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize path manager.

        Args:
            base_dir: Base directory for all paths. If None, uses current working directory.
        """
        if base_dir is None:
            # Try to detect project root
            self.base_dir = self._find_project_root()
        else:
            self.base_dir = Path(base_dir)

    @staticmethod
    def _find_project_root() -> Path:
        """Find the project root by looking for key markers."""
        current = Path.cwd()
        markers = ["emotional_os", "parser", "learning"]  # Project markers

        # Search up to 5 directories
        for _ in range(5):
            if any((current / marker).exists() for marker in markers):
                return current
            current = current.parent

        return Path.cwd()

    # Lexicon files
    def word_lexicon(self) -> Path:
        """Path to word-centric emotional lexicon."""
        return self._resolve_path(
            "data/word_centric_emotional_lexicon_expanded.json",
            "emotional_os/lexicon/word_centric_emotional_lexicon_expanded.json",
            "src/emotional_os_lexicon/word_centric_emotional_lexicon_expanded.json"
        )

    def nrc_lexicon(self) -> Path:
        """Path to NRC emotion lexicon."""
        return self._resolve_path(
            "data/lexicons/nrc_emotion_lexicon.txt",
            "data/lexicons/nrc_lexicon_cleaned.json",
            "emotional_os/lexicon/nrc_emotion_lexicon.txt"
        )

    def suicidality_protocol(self) -> Path:
        """Path to suicidality protocol config."""
        return self._resolve_path(
            "emotional_os/core/suicidality_protocol.json",
            "src/emotional_os/core/suicidality_protocol.json",
            "data/config/suicidality_protocol.json"
        )

    def signal_lexicon(self) -> Path:
        """Path to base signal lexicon."""
        return self._resolve_path(
            "parser/signal_lexicon.json", "data/lexicons/signal_lexicon.json", "emotional_os/parser/signal_lexicon.json"
        )

    def learned_lexicon(self) -> Path:
        """Path to learned lexicon (gets updated)."""
        return self._resolve_path(
            "parser/learned_lexicon.json",
            "data/lexicons/learned_lexicon.json",
            "emotional_os/parser/learned_lexicon.json",
        )

    def pattern_history(self) -> Path:
        """Path to pattern learning history."""
        return self._resolve_path(
            "learning/pattern_history.json",
            "data/lexicons/pattern_history.json",
            "emotional_os/deploy/learning/pattern_history.json",
        )

    # Glyph database
    def glyph_db(self) -> Path:
        """Path to glyph database."""
        return self._resolve_path("glyphs.db", "data/glyphs.db")

    # Poetry data (for training)
    def poetry_data_dir(self) -> Path:
        """Path to poetry data directory."""
        return self._resolve_path_dir("poetry_data", "data/poetry_data", "scripts/utilities/poetry_data")

    def poetry_index_db(self) -> Path:
        """Path to poetry index database."""
        poetry_dir = self.poetry_data_dir()
        return poetry_dir / "poetry_index.db"

    # Learning system
    def learning_db(self) -> Path:
        """Path to learning system database."""
        return self._resolve_path("data/learning.db", "learning/learning.db")

    # Safety and configuration
    def safety_config(self) -> Path:
        """Path to safety configuration."""
        return self._resolve_path("emotional_os/safety/config.json", "config/safety_config.json")

    # Utilities
    def _resolve_path(self, *candidates: str) -> Path:
        """
        Resolve the first existing path from candidates.

        Args:
            *candidates: List of path candidates (relative to base_dir)

        Returns:
            Path to first existing file, or first candidate if none exist
        """
        for candidate in candidates:
            full_path = self.base_dir / candidate
            if full_path.exists():
                return full_path

        # If none exist, return first candidate (will be created if needed)
        return self.base_dir / candidates[0]

    def _resolve_path_dir(self, *candidates: str) -> Path:
        """Resolve the first existing directory from candidates."""
        for candidate in candidates:
            full_path = self.base_dir / candidate
            if full_path.is_dir():
                return full_path

        # If none exist, return first candidate
        return self.base_dir / candidates[0]

    def ensure_dir(self, path: Path) -> Path:
        """Ensure directory exists."""
        path.mkdir(parents=True, exist_ok=True)
        return path

    def __repr__(self) -> str:
        return f"PathManager(base_dir={self.base_dir})"


# Global instance
_path_manager: Optional[PathManager] = None


def get_path_manager(base_dir: Optional[str] = None) -> PathManager:
    """Get or create the global path manager."""
    global _path_manager
    if _path_manager is None:
        _path_manager = PathManager(base_dir)
    return _path_manager


def reset_path_manager() -> None:
    """Reset the global path manager (useful for testing)."""
    global _path_manager
    _path_manager = None


# Convenience functions
def signal_lexicon_path() -> Path:
    """Get path to signal lexicon."""
    return get_path_manager().signal_lexicon()


def learned_lexicon_path() -> Path:
    """Get path to learned lexicon."""
    return get_path_manager().learned_lexicon()


def pattern_history_path() -> Path:
    """Get path to pattern history."""
    return get_path_manager().pattern_history()


def glyph_db_path() -> Path:
    """Get path to glyph database."""
    return get_path_manager().glyph_db()


def poetry_data_dir_path() -> Path:
    """Get path to poetry data directory."""
    return get_path_manager().poetry_data_dir()
