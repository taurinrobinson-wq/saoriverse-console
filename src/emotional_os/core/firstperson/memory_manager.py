"""Memory Rehydration Module for FirstPerson.

Fetches and injects conversation anchors into parser context on session
initialization. Enables continuity by reminding the system of recent emotional
themes and memories from past conversations.

Key functions:
- rehydrate_memory: Fetch recent anchors and inject into context
- build_memory_context: Create context-ready memory structure
- format_memory_for_parser: Format anchors as parser-compatible signals
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from .supabase_manager import SupabaseManager, ThemeAnchor


class MemoryManager:
    """Manages conversation memory rehydration for session continuity."""

    def __init__(self, user_id: str):
        """Initialize memory manager.

        Args:
            user_id: User identifier for data isolation
        """
        self.user_id = user_id
        self.supabase = SupabaseManager(user_id=user_id)
        self.rehydrated_anchors: List[ThemeAnchor] = []
        self.memory_context: Dict[str, Any] = {}

    def rehydrate_memory(self, limit: int = 20) -> Dict[str, Any]:
        """Fetch recent anchors and prepare memory context for injection.

        Args:
            limit: Maximum number of anchors to retrieve (default 20)

        Returns:
            Dictionary with rehydrated memory context ready for parser
        """
        # Fetch recent anchors from Supabase
        self.rehydrated_anchors = self.supabase.get_recent_anchors(limit=limit)

        if not self.rehydrated_anchors:
            # Return empty context if no anchors available
            return self._build_empty_context()

        # Build context structure from anchors
        self.memory_context = self._build_memory_context()

        return self.memory_context

    def _build_memory_context(self) -> Dict[str, Any]:
        """Build context structure from rehydrated anchors.

        Returns:
            Dictionary with memory context ready for injection
        """
        if not self.rehydrated_anchors:
            return self._build_empty_context()

        # Group anchors by theme
        themes_by_anchor = {}
        for anchor in self.rehydrated_anchors:
            if anchor.theme not in themes_by_anchor:
                themes_by_anchor[anchor.theme] = []
            themes_by_anchor[anchor.theme].append(anchor)

        # Build narrative memory summary
        memory_summary = self._build_narrative_summary(themes_by_anchor)

        # Build theme frequency data
        theme_frequencies = self._build_theme_frequencies(themes_by_anchor)

        # Build temporal context
        temporal_context = self._build_temporal_context()

        return {
            "status": "rehydrated",
            "memory_timestamp": datetime.now(timezone.utc).isoformat(),
            "anchor_count": len(self.rehydrated_anchors),
            "unique_themes": len(themes_by_anchor),
            "narrative_memory": memory_summary,
            "theme_frequencies": theme_frequencies,
            "temporal_patterns": temporal_context,
            "memory_salience": self._calculate_memory_salience(),
        }

    def _build_narrative_summary(
        self, themes_by_anchor: Dict[str, List[ThemeAnchor]]
    ) -> str:
        """Build narrative summary of memory anchors.

        Args:
            themes_by_anchor: Anchors grouped by theme

        Returns:
            Natural language summary of memory
        """
        if not themes_by_anchor:
            return ""

        # Sort themes by frequency
        sorted_themes = sorted(
            themes_by_anchor.items(),
            key=lambda x: sum(a.frequency for a in x[1]),
            reverse=True,
        )

        # Take top 3 themes for narrative
        narrative_parts = []
        for theme, anchors in sorted_themes[:3]:
            total_freq = sum(a.frequency for a in anchors)
            # Get most recent anchor for this theme
            latest_anchor = max(
                anchors, key=lambda a: a.last_detected_at, default=None
            )

            if latest_anchor:
                narrative_parts.append(
                    f"You've been dealing with {theme} ({total_freq} times): '{latest_anchor.anchor}'"
                )

        return " | ".join(narrative_parts) if narrative_parts else "No prior memory."

    def _build_theme_frequencies(
        self, themes_by_anchor: Dict[str, List[ThemeAnchor]]
    ) -> Dict[str, int]:
        """Build theme frequency data.

        Args:
            themes_by_anchor: Anchors grouped by theme

        Returns:
            Dictionary mapping theme to total frequency
        """
        return {
            theme: sum(a.frequency for a in anchors)
            for theme, anchors in themes_by_anchor.items()
        }

    def _build_temporal_context(self) -> Dict[str, Any]:
        """Build temporal context from memory.

        Returns:
            Dictionary with temporal context (patterns, timing)
        """
        if not self.supabase.is_available():
            return {"status": "unavailable"}

        # Get temporal patterns from Supabase
        patterns = self.supabase.get_temporal_patterns()

        if not patterns:
            return {"status": "no_patterns"}

        # Group patterns by time of day
        patterns_by_time = {}
        for pattern in patterns:
            time_of_day = pattern.time_of_day
            if time_of_day not in patterns_by_time:
                patterns_by_time[time_of_day] = []
            patterns_by_time[time_of_day].append(
                {
                    "theme": pattern.theme,
                    "frequency": pattern.frequency,
                    "intensity": pattern.avg_intensity,
                }
            )

        return {
            "status": "patterns_available",
            "by_time_of_day": patterns_by_time,
            "peak_stress_time": self._find_peak_stress_time(patterns),
        }

    def _find_peak_stress_time(self, patterns: List) -> Optional[str]:
        """Find the time of day with highest emotional intensity.

        Args:
            patterns: List of TemporalPattern objects

        Returns:
            Time of day string with highest stress, or None
        """
        if not patterns:
            return None

        # Find pattern with highest intensity and frequency
        peak_pattern = max(
            patterns, key=lambda p: p.avg_intensity * p.frequency, default=None
        )

        return peak_pattern.time_of_day if peak_pattern else None

    def _calculate_memory_salience(self) -> float:
        """Calculate how salient/important memory is (0-1 scale).

        Returns:
            Salience score based on recency and frequency
        """
        if not self.rehydrated_anchors:
            return 0.0

        # Calculate recency score (most recent anchor)
        now = datetime.now(timezone.utc)
        most_recent = self.rehydrated_anchors[0]
        # Parse ISO format timestamp
        try:
            recent_date = datetime.fromisoformat(
                most_recent.last_detected_at.replace("Z", "+00:00")
            )
            hours_ago = (now - recent_date).total_seconds() / 3600
            # Recency: full weight if < 24h, decay over week
            recency_score = max(0.0, 1.0 - (hours_ago / 168))
        except Exception:
            recency_score = 0.5

        # Calculate frequency score (total frequency normalized)
        total_frequency = sum(a.frequency for a in self.rehydrated_anchors)
        # Frequency: capped at 5 for normalization
        frequency_score = min(1.0, total_frequency / 10)

        # Combined salience (60% recency, 40% frequency)
        salience = (recency_score * 0.6) + (frequency_score * 0.4)

        return round(salience, 2)

    def _build_empty_context(self) -> Dict[str, Any]:
        """Build empty context for new users or when no history available.

        Returns:
            Empty but valid memory context structure
        """
        return {
            "status": "new_session",
            "memory_timestamp": datetime.now(timezone.utc).isoformat(),
            "anchor_count": 0,
            "unique_themes": 0,
            "narrative_memory": "This is our first conversation.",
            "theme_frequencies": {},
            "temporal_patterns": {"status": "no_history"},
            "memory_salience": 0.0,
        }

    def format_memory_for_parser(self) -> Dict[str, Any]:
        """Format rehydrated memory as signal-parser compatible structure.

        Returns:
            Dictionary formatted for signal parser injection
        """
        if not self.memory_context:
            # Rehydrate first if not done
            self.rehydrate_memory()

        # Create parser-compatible signal format
        signals = []

        # Create meta-signal for memory context
        for anchor in self.rehydrated_anchors:
            signal = {
                "type": "memory",
                "signal_type": "emotional_theme_anchor",
                "theme": anchor.theme,
                "anchor": anchor.anchor,
                "frequency": anchor.frequency,
                "confidence": anchor.confidence,
                "source": "memory_rehydration",
                "created_at": anchor.last_detected_at,
                "metadata": {
                    "status": anchor.status,
                    "context": anchor.context,
                },
            }
            signals.append(signal)

        return {
            "memory_signals": signals,
            "memory_context": self.memory_context,
            "ready_for_injection": True,
        }

    def get_top_themes(self, limit: int = 5) -> List[str]:
        """Get top themes from rehydrated memory.

        Args:
            limit: Number of themes to return

        Returns:
            List of theme names sorted by frequency
        """
        if not self.memory_context or not self.memory_context.get(
            "theme_frequencies"
        ):
            return []

        theme_freqs = self.memory_context.get("theme_frequencies", {})
        sorted_themes = sorted(
            theme_freqs.items(), key=lambda x: x[1], reverse=True
        )

        return [theme for theme, _ in sorted_themes[:limit]]

    def get_memory_summary(self) -> str:
        """Get human-readable memory summary.

        Returns:
            Natural language summary of user's memory
        """
        if not self.memory_context:
            return "No memory available yet."

        return self.memory_context.get(
            "narrative_memory", "Memory context unavailable."
        )


def rehydrate_memory(user_id: str, limit: int = 20) -> Dict[str, Any]:
    """Module-level function to rehydrate memory.

    Args:
        user_id: User identifier
        limit: Maximum number of anchors to retrieve

    Returns:
        Memory context ready for injection
    """
    manager = MemoryManager(user_id=user_id)
    return manager.rehydrate_memory(limit=limit)


def format_memory_for_parser(user_id: str) -> Dict[str, Any]:
    """Module-level function to format memory for parser injection.

    Args:
        user_id: User identifier

    Returns:
        Parser-compatible memory signal structure
    """
    manager = MemoryManager(user_id=user_id)
    manager.rehydrate_memory()
    return manager.format_memory_for_parser()


def get_memory_summary(user_id: str) -> str:
    """Module-level function to get memory summary.

    Args:
        user_id: User identifier

    Returns:
        Natural language memory summary
    """
    manager = MemoryManager(user_id=user_id)
    manager.rehydrate_memory()
    return manager.get_memory_summary()
