"""Phase 3.1 Integration Orchestrator.

Bridges emotional profile management, session coherence tracking, and 
preference evolution with the existing FirstPerson infrastructure.

Integrates with:
- IntegrationOrchestrator (Phase 1 core pipeline)
- RepairOrchestrator (Phase 2.3 repair module)
- PreferenceManager (Phase 2.4 preferences)
- TemporalAnalyzer (Phase 2.5 temporal patterns)
- PerspectiveTaker (Phase 3 perspective-taking)
- MicroChoiceOffering (Phase 3 micro-choice scaffolding)
- CircadianGlyphSelector (Phase 3 temporal awareness)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import logging

from emotional_profile import EmotionalProfileManager, EmotionalTone
from session_coherence import SessionCoherenceTracker
from preference_evolution import PreferenceEvolutionTracker, PreferenceType
from perspective_taker import PerspectiveTaker, PerspectiveReflection
from micro_choice_offering import MicroChoiceOffering, MicroChoice
from temporal_patterns import TemporalAnalyzer, CircadianGlyphSelector


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
    - Perspective-taking and relational depth (Phase 3)
    - Micro-choice scaffolding (Phase 3)
    - Temporal pattern awareness (Phase 3)
    """

    def __init__(self, user_id: str):
        """Initialize Phase 3.1 integration orchestrator.

        Args:
            user_id: User identifier
        """
        self.user_id = user_id

        # Initialize Phase 1-2 components
        self.profile_manager = EmotionalProfileManager(user_id)
        self.session_trackers: Dict[str, SessionCoherenceTracker] = {}
        self.preference_tracker = PreferenceEvolutionTracker(user_id)

        # Initialize Phase 3 components (Relational Depth)
        self.perspective_taker = PerspectiveTaker(user_id)
        self.choice_offering = MicroChoiceOffering(user_id)
        self.temporal_analyzer = TemporalAnalyzer()
        self.circadian_selector = CircadianGlyphSelector(
            self.temporal_analyzer)

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
    # PHASE 3: RELATIONAL DEPTH INTEGRATION
    # ========================================================================

    def analyze_user_input_for_phase3(
        self,
        user_input: str,
        detected_tone: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze user input using all Phase 3 modules.

        Detects:
        - Relational contexts (perspective-taking)
        - Unresolved tensions (micro-choice offering)
        - Temporal patterns in emotional themes

        Args:
            user_input: The user's message
            detected_tone: Optional pre-detected tone

        Returns:
            Dictionary with Phase 3 analysis results
        """
        analysis = {
            "user_input": user_input,
            "timestamp": datetime.now().isoformat(),
            "relational_context": None,
            "perspective_reflection": None,
            "unresolved_tension": None,
            "micro_choice": None,
            "temporal_insights": None,
        }

        # Phase 3.1: Perspective-taking detection
        should_offer_perspective, perspective_context = self.perspective_taker.should_offer_reflection(
            user_input
        )
        if should_offer_perspective and perspective_context:
            analysis["relational_context"] = perspective_context
            reflection = self.perspective_taker.generate_reflection(
                perspective_context)
            analysis["perspective_reflection"] = {
                "variation": reflection.variation.value,
                "text": reflection.reflection_text,
                "prompt": reflection.prompt_question,
                "confidence": reflection.confidence,
            }
            logger.info(
                f"Generated perspective reflection for user {self.user_id}")

        # Phase 3.2: Micro-choice offering detection
        should_offer_choice, tension = self.choice_offering.should_offer_choice(
            user_input)
        if should_offer_choice and tension:
            analysis["unresolved_tension"] = {
                "type": tension.tension_type,
                "emotional_state": tension.emotional_state,
                "implicit_question": tension.implicit_question,
                "confidence": tension.confidence,
            }
            choice = self.choice_offering.offer_choice(tension)
            if choice:
                analysis["micro_choice"] = {
                    "choice_type": choice.choice_type.value,
                    "path_a": choice.path_a,
                    "path_b": choice.path_b,
                    "formatted": self.choice_offering.format_choice_for_response(choice),
                    "confidence": choice.confidence,
                }
                logger.info(f"Generated micro-choice for user {self.user_id}")

        # Phase 3.3: Temporal pattern awareness
        if detected_tone:
            temporal_insights = self.temporal_analyzer.get_time_based_insights(
                self.user_id
            )
            analysis["temporal_insights"] = temporal_insights

        return analysis

    def generate_phase3_enriched_response(
        self,
        base_response: str,
        analysis: Dict[str, Any],
        include_choice: bool = True,
        include_perspective: bool = True,
    ) -> str:
        """Blend Phase 3 elements (perspective, choice, temporal awareness) into response.

        Args:
            base_response: The base glyph response text
            analysis: Output from analyze_user_input_for_phase3()
            include_choice: Whether to include micro-choice element
            include_perspective: Whether to include perspective element

        Returns:
            Enriched response combining base response with Phase 3 elements
        """
        response_parts = [base_response]

        # Add perspective-taking if available
        if include_perspective and analysis.get("perspective_reflection"):
            perspective_data = analysis["perspective_reflection"]
            response_parts.append(f"\n\n{perspective_data['prompt']}")

        # Add micro-choice if available
        if include_choice and analysis.get("micro_choice"):
            choice_data = analysis["micro_choice"]
            response_parts.append(f"\n\n{choice_data['formatted']}")

        # Note: Temporal insights are used internally for glyph selection,
        # not typically surfaced directly in response

        return "".join(response_parts)

    def select_best_glyph_for_moment(
        self,
        tone: str,
        current_time: Optional[datetime] = None
    ) -> Optional[Tuple[str, float]]:
        """Select best glyph considering circadian patterns (Phase 3.3).

        Uses temporal analyzer to pick glyphs that work best at this time of day.

        Args:
            tone: Emotional tone/category
            current_time: Optional current time; uses now() if not provided

        Returns:
            Tuple of (glyph_name, effectiveness_score) or None
        """
        if current_time is None:
            current_time = datetime.now()

        result = self.circadian_selector.select_glyph_for_moment(
            self.user_id, tone, current_time
        )
        return result

    def build_circadian_profile(self) -> Dict[str, Any]:
        """Build user's circadian/temporal glyph preference profile.

        Useful for understanding time-of-day patterns in emotional responses.

        Returns:
            Profile dictionary with temporal patterns
        """
        profile = self.circadian_selector.build_user_profile(self.user_id)
        return profile

    def get_phase3_summary(self) -> Dict[str, Any]:
        """Get summary of Phase 3 relational depth components.

        Returns:
            Summary with perspective, choice, and temporal statistics
        """
        return {
            "perspective_reflections_offered": len(self.perspective_taker.reflection_history),
            "micro_choices_offered": len(self.choice_offering.choice_history),
            "temporal_patterns_tracked": len(self.temporal_analyzer.patterns),
            "relational_contexts_detected": len(self.perspective_taker.context_history),
            "tensions_detected": len(self.choice_offering.tension_history),
            "temporal_summary": self.temporal_analyzer.get_pattern_summary(),
        }

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
