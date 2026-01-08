"""Supabase Manager for FirstPerson Theme and Anchor Storage.

Manages persistent storage of emotional themes, anchors, and temporal patterns
in Supabase for cross-session memory and pattern analysis.

Key functions:
- record_theme_anchor: Store detected theme with metadata
- get_theme_frequency: Retrieve frequency data for theme
- get_recent_anchors: Fetch recent anchors for memory rehydration
- record_temporal_pattern: Track time-of-day patterns
- get_temporal_patterns: Retrieve patterns for a specific time
"""

import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    from supabase import create_client, Client
except ImportError:
    Client = None  # Optional dependency for testing


@dataclass
class ThemeAnchor:
    """Data class for theme anchors."""

    theme: str
    anchor: str
    frequency: int
    first_detected_at: str
    last_detected_at: str
    confidence: float
    status: str = "active"
    context: Dict[str, Any] = None


@dataclass
class ThemeHistory:
    """Data class for theme history records."""

    theme: str
    frequency_at_time: int
    detected_at: str
    context: Dict[str, Any] = None
    affect_state: Dict[str, Any] = None
    time_of_day: Optional[str] = None
    day_of_week: Optional[str] = None


@dataclass
class TemporalPattern:
    """Data class for temporal patterns."""

    theme: str
    time_of_day: str
    frequency: int
    avg_intensity: float
    day_of_week: Optional[str] = None


class SupabaseManager:
    """Manages FirstPerson data in Supabase."""

    def __init__(self, user_id: str):
        """Initialize manager with user context.

        Args:
            user_id: User identifier for data isolation
        """
        self.user_id = user_id

        # Initialize Supabase client if available
        if Client is not None:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")

            if supabase_url and supabase_key:
                self.client: Optional[Client] = create_client(
                    supabase_url, supabase_key
                )
            else:
                self.client = None
        else:
            self.client = None

    def is_available(self) -> bool:
        """Check if Supabase is available.

        Returns:
            True if Supabase client is initialized
        """
        return self.client is not None

    def record_theme_anchor(
        self,
        theme: str,
        anchor: str,
        confidence: float = 0.5,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Record or update a theme anchor.

        Args:
            theme: Theme identifier
            anchor: Memorable phrase capturing essence
            confidence: Confidence score (0-1)
            context: Additional context data

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False

        try:
            now = datetime.now(timezone.utc).isoformat()

            # Try to find existing anchor
            existing = (
                self.client.table("theme_anchors")
                .select("*")
                .eq("user_id", self.user_id)
                .eq("theme", theme)
                .eq("anchor", anchor)
                .execute()
            )

            if existing.data:
                # Update existing anchor
                self.client.table("theme_anchors").update(
                    {
                        "frequency": existing.data[0]["frequency"] + 1,
                        "last_detected_at": now,
                        "confidence": max(
                            confidence, existing.data[0].get("confidence", 0.5)
                        ),
                        "updated_at": now,
                    }
                ).eq("id", existing.data[0]["id"]).execute()
            else:
                # Create new anchor
                self.client.table("theme_anchors").insert(
                    {
                        "user_id": self.user_id,
                        "theme": theme,
                        "anchor": anchor,
                        "frequency": 1,
                        "first_detected_at": now,
                        "last_detected_at": now,
                        "confidence": confidence,
                        "context": context or {},
                        "status": "active",
                    }
                ).execute()

            return True
        except Exception as e:
            print(f"Error recording theme anchor: {e}")
            return False

    def get_theme_frequency(
        self, theme: Optional[str] = None, days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get theme frequency for user.

        Args:
            theme: Specific theme to query, or None for all themes
            days: Look back N days (default 30)

        Returns:
            List of theme frequency data
        """
        if not self.is_available():
            return []

        try:
            cutoff_date = (
                datetime.now(timezone.utc) - timedelta(days=days)
            ).isoformat()

            query = (
                self.client.table("theme_history")
                .select("theme, COUNT(*) as frequency, COUNT(DISTINCT DATE(detected_at)) as days_appeared")
                .eq("user_id", self.user_id)
                .gt("detected_at", cutoff_date)
            )

            if theme:
                query = query.eq("theme", theme)

            result = query.execute()
            return result.data or []
        except Exception as e:
            print(f"Error getting theme frequency: {e}")
            return []

    def get_recent_anchors(self, limit: int = 20) -> List[ThemeAnchor]:
        """Get recent anchors for memory rehydration.

        Args:
            limit: Maximum number of anchors to retrieve

        Returns:
            List of ThemeAnchor objects
        """
        if not self.is_available():
            return []

        try:
            result = (
                self.client.table("theme_anchors")
                .select("*")
                .eq("user_id", self.user_id)
                .eq("status", "active")
                .order("last_detected_at", desc=True)
                .limit(limit)
                .execute()
            )

            anchors = []
            for row in result.data or []:
                anchors.append(
                    ThemeAnchor(
                        theme=row["theme"],
                        anchor=row["anchor"],
                        frequency=row["frequency"],
                        first_detected_at=row["first_detected_at"],
                        last_detected_at=row["last_detected_at"],
                        confidence=row["confidence"],
                        status=row["status"],
                        context=row.get("context", {}),
                    )
                )

            return anchors
        except Exception as e:
            print(f"Error getting recent anchors: {e}")
            return []

    def record_theme_history(
        self,
        theme: str,
        conversation_id: Optional[str] = None,
        frequency_at_time: int = 1,
        context: Optional[Dict[str, Any]] = None,
        affect_state: Optional[Dict[str, Any]] = None,
        time_of_day: Optional[str] = None,
        day_of_week: Optional[str] = None,
    ) -> bool:
        """Record theme occurrence in history.

        Args:
            theme: Theme identifier
            conversation_id: Associated conversation
            frequency_at_time: How many times appeared in this session
            context: Context data
            affect_state: Emotional state data
            time_of_day: Time period ('morning', 'afternoon', 'evening', 'night')
            day_of_week: Day name

        Returns:
            True if successful
        """
        if not self.is_available():
            return False

        try:
            now = datetime.now(timezone.utc).isoformat()

            self.client.table("theme_history").insert(
                {
                    "user_id": self.user_id,
                    "conversation_id": conversation_id,
                    "theme": theme,
                    "frequency_at_time": frequency_at_time,
                    "detected_at": now,
                    "context": context or {},
                    "affect_state": affect_state or {},
                    "time_of_day": time_of_day,
                    "day_of_week": day_of_week,
                }
            ).execute()

            return True
        except Exception as e:
            print(f"Error recording theme history: {e}")
            return False

    def get_temporal_patterns(
        self, time_of_day: Optional[str] = None, theme: Optional[str] = None
    ) -> List[TemporalPattern]:
        """Get temporal patterns for user.

        Args:
            time_of_day: Specific time period to query
            theme: Specific theme to query

        Returns:
            List of TemporalPattern objects
        """
        if not self.is_available():
            return []

        try:
            query = self.client.table("temporal_patterns").select("*").eq(
                "user_id", self.user_id
            )

            if time_of_day:
                query = query.eq("time_of_day", time_of_day)

            if theme:
                query = query.eq("theme", theme)

            result = query.order("frequency", desc=True).execute()

            patterns = []
            for row in result.data or []:
                patterns.append(
                    TemporalPattern(
                        theme=row["theme"],
                        time_of_day=row["time_of_day"],
                        frequency=row["frequency"],
                        avg_intensity=row["avg_intensity"],
                        day_of_week=row.get("day_of_week"),
                    )
                )

            return patterns
        except Exception as e:
            print(f"Error getting temporal patterns: {e}")
            return []

    def record_temporal_pattern(
        self,
        theme: str,
        time_of_day: str,
        intensity: float = 0.5,
        day_of_week: Optional[str] = None,
    ) -> bool:
        """Record or update temporal pattern.

        Args:
            theme: Theme identifier
            time_of_day: Time period
            intensity: Emotional intensity (0-1)
            day_of_week: Specific day or None for all days

        Returns:
            True if successful
        """
        if not self.is_available():
            return False

        try:
            now = datetime.now(timezone.utc).isoformat()

            # Try to find existing pattern
            query = (
                self.client.table("temporal_patterns")
                .select("*")
                .eq("user_id", self.user_id)
                .eq("theme", theme)
                .eq("time_of_day", time_of_day)
            )

            if day_of_week:
                query = query.eq("day_of_week", day_of_week)
            else:
                query = query.is_("day_of_week", "null")

            existing = query.execute()

            if existing.data:
                # Update existing pattern
                record = existing.data[0]
                new_frequency = record["frequency"] + 1
                new_avg_intensity = (
                    record["avg_intensity"] * record["frequency"] + intensity
                ) / new_frequency

                self.client.table("temporal_patterns").update(
                    {
                        "frequency": new_frequency,
                        "avg_intensity": new_avg_intensity,
                        "last_observed_at": now,
                        "updated_at": now,
                    }
                ).eq("id", record["id"]).execute()
            else:
                # Create new pattern
                self.client.table("temporal_patterns").insert(
                    {
                        "user_id": self.user_id,
                        "theme": theme,
                        "time_of_day": time_of_day,
                        "day_of_week": day_of_week,
                        "frequency": 1,
                        "avg_intensity": intensity,
                    }
                ).execute()

            return True
        except Exception as e:
            print(f"Error recording temporal pattern: {e}")
            return False

    def get_recurring_patterns(self, min_frequency: int = 3) -> List[Dict[str, Any]]:
        """Get highly recurring temporal patterns (potential stress loops).

        Args:
            min_frequency: Minimum frequency to consider recurring

        Returns:
            List of recurring patterns with high emotional intensity
        """
        if not self.is_available():
            return []

        try:
            result = (
                self.client.table("temporal_patterns")
                .select("*")
                .eq("user_id", self.user_id)
                .gte("frequency", min_frequency)
                .gt("avg_intensity", 0.6)
                .order("frequency", desc=True)
                .execute()
            )

            return result.data or []
        except Exception as e:
            print(f"Error getting recurring patterns: {e}")
            return []

    def update_anchor_status(
        self, anchor_id: str, new_status: str
    ) -> bool:
        """Update status of an anchor (active, resolved, recurring).

        Args:
            anchor_id: Anchor UUID
            new_status: New status value

        Returns:
            True if successful
        """
        if not self.is_available():
            return False

        try:
            now = datetime.now(timezone.utc).isoformat()

            self.client.table("theme_anchors").update(
                {"status": new_status, "updated_at": now}
            ).eq("id", anchor_id).eq("user_id", self.user_id).execute()

            return True
        except Exception as e:
            print(f"Error updating anchor status: {e}")
            return False
