"""Phase 3.1 Integration Orchestrator.

Bridges emotional profile management, session coherence tracking, and 
preference evolution with the existing FirstPerson infrastructure.

Integrates with:
- IntegrationOrchestrator (Phase 1 core pipeline)
- RepairOrchestrator (Phase 2.3 repair module)
- PreferenceManager (Phase 2.4 preferences)
- TemporalAnalyzer (Phase 2.5 temporal patterns)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

from emotional_profile import EmotionalProfileManager, EmotionalTone
from session_coherence import SessionCoherenceTracker
from preference_evolution import PreferenceEvolutionTracker, PreferenceType


logger = logging.getLogger(__name__)


@dataclass
class Phase3InteractionContext:
    """Context for a single interaction spanning all Phase 3.1 components."""
    user_id: str
    session_id: str
    turn_number: int
    user_input: str
    detected_tone: str
    detected_themes: List[str]
    glyph_response: str
    user_satisfaction: Optional[float] = None
    has_frustration: bool = False
    has_breakthrough: bool = False


class Phase3IntegrationOrchestrator:
    """Orchestrates Phase 3.1 memory integration across components.

    Manages:
    - Long-term emotional profile building
    - Session coherence monitoring
    - Preference evolution tracking
    - Cross-component synchronization
    """

    def __init__(self, user_id: str):
        """Initialize Phase 3.1 integration orchestrator.

        Args:
            user_id: User identifier
        """
        self.user_id = user_id

        # Initialize Phase 3.1 components
        self.profile_manager = EmotionalProfileManager(user_id)
        self.session_trackers: Dict[str, SessionCoherenceTracker] = {}
        self.preference_tracker = PreferenceEvolutionTracker(user_id)

        # Session tracking
        self._current_session_id: Optional[str] = None
        self._session_histories: Dict[str, List[Phase3InteractionContext]] = {}

    def start_session(self, session_id: str) -> SessionCoherenceTracker:
        """Begin a new session.

        Args:
            session_id: Unique session identifier

        Returns:
            SessionCoherenceTracker for this session
        """
        self._current_session_id = session_id

        # Create coherence tracker linked to profile
        tracker = SessionCoherenceTracker(
            session_id, self.user_id, self.profile_manager)
        self.session_trackers[session_id] = tracker
        self._session_histories[session_id] = []

        logger.info(f"Started session {session_id} for user {self.user_id}")
        return tracker

    def record_interaction(
        self,
        session_id: str,
        turn_number: int,
        user_input: str,
        detected_tone: str,
        detected_themes: List[str],
        glyph_response: str,
        user_satisfaction: Optional[float] = None,
        has_frustration: bool = False,
        has_breakthrough: bool = False,
    ) -> Phase3InteractionContext:
        """Record a complete interaction across all Phase 3.1 components.

        Args:
            session_id: Session identifier
            turn_number: Turn sequence number
            user_input: User's input text
            detected_tone: Detected emotional tone (string representation)
            detected_themes: List of detected themes
            glyph_response: Glyph used in response
            user_satisfaction: Optional satisfaction rating 0.0-1.0
            has_frustration: Whether user showed frustration
            has_breakthrough: Whether user had breakthrough

        Returns:
            InteractionContext capturing the complete interaction
        """
        # Convert tone string to enum
        try:
            tone_enum = EmotionalTone[detected_tone.upper()]
        except (KeyError, AttributeError):
            tone_enum = EmotionalTone.GROUNDED  # Default fallback

        # Create interaction context
        context = Phase3InteractionContext(
            user_id=self.user_id,
            session_id=session_id,
            turn_number=turn_number,
            user_input=user_input,
            detected_tone=detected_tone,
            detected_themes=detected_themes,
            glyph_response=glyph_response,
            user_satisfaction=user_satisfaction,
            has_frustration=has_frustration,
            has_breakthrough=has_breakthrough,
        )

        # Record to session history
        if session_id not in self._session_histories:
            self._session_histories[session_id] = []
        self._session_histories[session_id].append(context)

        # Update profile manager
        self.profile_manager.record_interaction(
            tone=tone_enum,
            intensity=self._estimate_intensity(detected_tone, detected_themes),
            themes=detected_themes,
            glyph_response=glyph_response,
            user_satisfaction=user_satisfaction,
        )

        # Update session coherence tracker
        if session_id in self.session_trackers:
            self.session_trackers[session_id].record_turn(
                turn_number=turn_number,
                user_input=user_input,
                themes=detected_themes,
                emotional_tone=detected_tone,
                glyph_response=glyph_response,
                has_frustration=has_frustration,
                has_breakthrough=has_breakthrough,
            )

        # Update preference tracking
        self.preference_tracker.record_preference(
            preference_type=PreferenceType.GLYPH,
            item=glyph_response,
            score=user_satisfaction if user_satisfaction else 0.5,
        )

        # Record theme preferences
        for theme in detected_themes:
            theme_score = user_satisfaction if user_satisfaction else 0.5
            self.preference_tracker.record_preference(
                preference_type=PreferenceType.THEME,
                item=theme,
                score=theme_score,
            )

        logger.info(
            f"Recorded interaction {turn_number} in session {session_id} "
            f"for user {self.user_id}"
        )

        return context

    def end_session(
        self,
        session_id: str,
        overall_satisfaction: Optional[float] = None,
    ) -> Dict[str, Any]:
        """End current session and generate summary.

        Args:
            session_id: Session identifier
            overall_satisfaction: Optional overall session satisfaction 0.0-1.0

        Returns:
            Session summary dictionary
        """
        if session_id not in self.session_trackers:
            logger.warning(f"Session {session_id} not found")
            return {}

        # End session coherence tracking
        coherence = self.session_trackers[session_id].end_session(
            overall_satisfaction)

        # Generate reports
        coherence_report = self.session_trackers[session_id].get_coherence_report(
        )
        improvement_suggestions = self.session_trackers[session_id].suggest_improvements(
        )

        # Create session summary
        summary = {
            "session_id": session_id,
            "user_id": self.user_id,
            "start_time": coherence.start_time.isoformat(),
            "end_time": coherence.end_time.isoformat() if coherence.end_time else None,
            "duration_seconds": coherence.total_duration,
            "turn_count": coherence.turn_count,
            "coherence": coherence_report,
            "suggestions": improvement_suggestions,
            "user_satisfaction": overall_satisfaction,
        }

        logger.info(
            f"Ended session {session_id}: {coherence.quality.value} quality, "
            f"coherence score {coherence.coherence_score:.2f}"
        )

        return summary

    def get_user_insights(self) -> Dict[str, Any]:
        """Generate comprehensive insights about user based on Phase 3.1 data.

        Returns:
            Dictionary with user insights and trends
        """
        profile_export = self.profile_manager.export_profile()
        preference_report = self.preference_tracker.get_preference_report(
            lookback_days=90)

        # Get dominant themes
        dominant_themes = self.profile_manager.get_dominant_themes(limit=5)

        # Get emerging and fading preferences
        emerging = self.preference_tracker.get_emerging_preferences(
            days=30, threshold=0.2)
        fading = self.preference_tracker.get_fading_preferences(
            days=30, threshold=0.2)

        # Predict upcoming themes
        predictions = self.profile_manager.predict_upcoming_themes(
            lookahead_hours=24)

        insights = {
            "user_id": self.user_id,
            "profile_summary": {
                "primary_tones": profile_export.get("primary_tones", {}),
                "session_count": profile_export.get("session_count", 0),
            },
            "dominant_themes": [
                {"theme": t, "occurrences": c} for t, c in dominant_themes
            ],
            "emerging_preferences": [
                {"preference": p, "strength": s, "description": d}
                for p, s, d in emerging
            ],
            "fading_preferences": [
                {"preference": p, "strength": s, "description": d}
                for p, s, d in fading
            ],
            "predicted_themes": [
                {"theme": t, "probability": p} for t, p in predictions
            ],
            "preference_volatility": preference_report.get("volatility", {}),
        }

        return insights

    def get_session_recommendations(self, session_id: str) -> List[str]:
        """Get recommendations for improving future sessions.

        Args:
            session_id: Session identifier

        Returns:
            List of actionable recommendations
        """
        if session_id not in self.session_trackers:
            return []

        recommendations = []
        tracker = self.session_trackers[session_id]

        # Get coherence-based suggestions
        coherence_suggestions = tracker.suggest_improvements()
        recommendations.extend(coherence_suggestions)

        # Add preference-based recommendations
        fading_prefs = self.preference_tracker.get_fading_preferences(
            days=30, threshold=0.2)
        if fading_prefs:
            recommendations.append(
                f"Several glyphs/themes are becoming less engaging. "
                f"Consider exploring new approaches: {', '.join(p[0] for p in fading_prefs[:3])}"
            )

        emerging_prefs = self.preference_tracker.get_emerging_preferences(
            days=30, threshold=0.2)
        if emerging_prefs:
            recommendations.append(
                f"New interests emerging! Lean into these growing preferences: "
                f"{', '.join(p[0] for p in emerging_prefs[:3])}"
            )

        return recommendations

    def get_emotional_trajectory(self, days: int = 30) -> List[Dict]:
        """Get user's emotional trajectory over time.

        Args:
            days: Number of days to look back

        Returns:
            List of emotional states over time
        """
        trajectory = self.profile_manager.get_emotional_trajectory(days=days)

        return [
            {
                "timestamp": ts.isoformat(),
                "tone": tone.value,
            }
            for ts, tone in trajectory
        ]

    def compare_session_to_profile(self, session_id: str) -> Dict[str, Any]:
        """Compare current session to user's typical patterns.

        Args:
            session_id: Session identifier

        Returns:
            Comparison analysis
        """
        if session_id not in self.session_trackers:
            return {}

        coherence = self.session_trackers[session_id].coherence

        comparison = {
            "session_id": session_id,
            "profile_alignment": coherence.profile_alignment,
            "alignment_quality": self._describe_alignment(coherence.profile_alignment),
            "anomalies_detected": coherence.anomaly_count,
            "session_coherence": coherence.coherence_score,
            "session_quality": coherence.quality.value,
        }

        return comparison

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _estimate_intensity(self, tone: str, themes: List[str]) -> str:
        """Estimate emotional intensity from tone and themes.

        Args:
            tone: Emotional tone string
            themes: List of emotional themes

        Returns:
            "low", "medium", or "high"
        """
        high_intensity_tones = ["anxious",
                                "overwhelmed", "vulnerable", "frustrated"]
        high_intensity_themes = ["panic", "crisis", "overwhelm", "breakdown"]

        if tone.lower() in high_intensity_tones:
            return "high"

        if any(theme.lower() in high_intensity_themes for theme in themes):
            return "high"

        if len(themes) > 3:
            return "medium"

        return "low"

    def _describe_alignment(self, alignment_score: float) -> str:
        """Describe profile alignment quality.

        Args:
            alignment_score: Score 0.0-1.0

        Returns:
            Human-readable description
        """
        if alignment_score >= 0.8:
            return "Highly aligned - very typical pattern"
        elif alignment_score >= 0.6:
            return "Well-aligned - mostly typical"
        elif alignment_score >= 0.4:
            return "Moderately aligned - some variations"
        elif alignment_score >= 0.2:
            return "Divergent - unusual patterns"
        else:
            return "Highly divergent - very atypical"

    def export_all_data(self) -> Dict[str, Any]:
        """Export all Phase 3.1 data for backup/analysis.

        Returns:
            Complete export dictionary
        """
        return {
            "user_id": self.user_id,
            "profile": self.profile_manager.export_profile(),
            "preferences": self.preference_tracker.export_evolution(),
            "sessions": {
                sid: self.session_trackers[sid].get_coherence_report()
                for sid in self.session_trackers.keys()
            },
            "insights": self.get_user_insights(),
        }
