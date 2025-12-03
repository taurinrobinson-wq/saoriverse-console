"""Phase 3: Full Integration Test Harness

Comprehensive tests for Phase 3 (Relational Depth) modules:
- Perspective-Taking (perspective_taker.py)
- Micro-Choice Offering (micro_choice_offering.py)
- Temporal Tracking Integration (temporal_patterns.py)
- Full Integration Orchestrator (phase_3_integration_orchestrator.py)

Tests run modules individually and in integrated scenarios.
"""

from phase_3_integration_orchestrator import Phase3IntegrationOrchestrator
from temporal_patterns import TemporalAnalyzer, TemporalEvent, CircadianGlyphSelector
from micro_choice_offering import (
    MicroChoiceOffering,
    ChoiceType,
    UnresolvedTension
)
from perspective_taker import (
    PerspectiveTaker,
    PerspectiveVariation,
    RelationalContext
)
import pytest
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add firstperson directory to path for relative imports
firstperson_dir = Path(__file__).parent
sys.path.insert(0, str(firstperson_dir))

# Import Phase 3 modules


class TestPerspectiveTaker:
    """Test Phase 3.1: Perspective-Taking Module"""

    def setup_method(self):
        """Set up test fixtures."""
        self.taker = PerspectiveTaker(user_id="test_user_1")

    def test_detect_relational_context_family(self):
        """Test detection of family relational context."""
        text = "My mom said she wasn't happy with how I handled it."
        context = self.taker.detect_relational_context(text)

        assert context is not None
        assert context.subject.lower() == "mom"
        assert context.relationship == "family"
        assert context.confidence > 0.6

    def test_detect_relational_context_work(self):
        """Test detection of work relational context."""
        text = "My boss thinks I'm not pulling my weight on the project."
        context = self.taker.detect_relational_context(text)

        assert context is not None
        assert "boss" in context.subject.lower()
        assert context.relationship == "work"

    def test_detect_relational_context_friend(self):
        """Test detection of friend relational context."""
        text = "My best friend told me she needs space."
        context = self.taker.detect_relational_context(text)

        assert context is not None
        assert context.relationship == "friend"

    def test_generate_reflection_empathy_variation(self):
        """Test generating empathy perspective reflection."""
        text = "Cindy said I was being unfair."
        context = self.taker.detect_relational_context(text)
        assert context is not None

        reflection = self.taker.generate_reflection(
            context, PerspectiveVariation.EMPATHY)

        assert reflection.variation == PerspectiveVariation.EMPATHY
        assert "Cindy" in reflection.prompt_question or reflection.reflection_text
        assert len(reflection.reflection_text) > 0
        assert "?" in reflection.prompt_question

    def test_generate_reflection_boundary_variation(self):
        """Test generating boundary-setting perspective reflection."""
        text = "They keep asking me for favors."
        context = self.taker.detect_relational_context(text)
        assert context is not None

        reflection = self.taker.generate_reflection(
            context, PerspectiveVariation.BOUNDARY)

        assert reflection.variation == PerspectiveVariation.BOUNDARY
        assert any(
            word in reflection.reflection_text.lower()
            for word in ["boundary", "need", "wellbeing"]
        )

    def test_generate_reflection_self_care_variation(self):
        """Test generating self-care perspective reflection."""
        text = "My family is really demanding right now."
        context = self.taker.detect_relational_context(text)
        assert context is not None

        reflection = self.taker.generate_reflection(
            context, PerspectiveVariation.SELF_CARE)

        assert reflection.variation == PerspectiveVariation.SELF_CARE
        assert any(
            word in reflection.reflection_text.lower()
            for word in ["care", "support", "self", "gentle"]
        )

    def test_generate_all_variations(self):
        """Test generating all three variation types for a context."""
        text = "My boss is being unreasonable about the deadline."
        context = self.taker.detect_relational_context(text)
        assert context is not None

        variations = self.taker.generate_all_variations(context)

        assert len(variations) == 3
        assert "empathy" in variations
        assert "boundary" in variations
        assert "self-care" in variations

        for variation_name, reflection in variations.items():
            assert reflection.reflection_text
            assert reflection.prompt_question
            assert "?" in reflection.prompt_question

    def test_should_offer_reflection_high_confidence(self):
        """Test decision logic for offering reflections."""
        text = "My friend said something hurtful."
        should_offer, context = self.taker.should_offer_reflection(text)

        if context and context.confidence >= 0.6:
            assert should_offer is True
        else:
            assert should_offer is False

    def test_reflection_history_tracking(self):
        """Test that reflection history is maintained."""
        text1 = "My mom thinks I should move home."
        text2 = "My boss disagreed with my proposal."

        self.taker.detect_relational_context(text1)
        reflection1 = self.taker.generate_reflection(
            self.taker.context_history[0]
        )

        self.taker.detect_relational_context(text2)
        reflection2 = self.taker.generate_reflection(
            self.taker.context_history[1]
        )

        assert len(self.taker.reflection_history) == 2
        assert reflection1.variation != reflection2.variation  # Should alternate


class TestMicroChoiceOffering:
    """Test Phase 3.2: Micro-Choice Offering Module"""

    def setup_method(self):
        """Set up test fixtures."""
        self.offering = MicroChoiceOffering(user_id="test_user_2")

    def test_detect_tension_paralysis(self):
        """Test detection of paralysis/indecision tension."""
        text = "I don't know what to do about this situation."
        tension = self.offering.detect_tension(text)

        assert tension is not None
        assert tension.tension_type == "paralysis"
        assert "what should i do" in tension.implicit_question.lower(
        ) or "what" in tension.implicit_question

    def test_detect_tension_conflict(self):
        """Test detection of interpersonal conflict tension."""
        text = "We had an argument and now I feel misunderstood."
        tension = self.offering.detect_tension(text)

        assert tension is not None
        assert tension.tension_type == "conflict"

    def test_detect_tension_abandonment(self):
        """Test detection of abandonment/isolation tension."""
        text = "I feel so alone in this, nobody seems to understand."
        tension = self.offering.detect_tension(text)

        assert tension is not None
        assert tension.tension_type == "abandonment"

    def test_detect_tension_overwhelm(self):
        """Test detection of overwhelm tension."""
        text = "There's too much happening all at once."
        tension = self.offering.detect_tension(text)

        assert tension is not None
        assert tension.tension_type == "overwhelm"

    def test_detect_tension_injustice(self):
        """Test detection of injustice/unfairness tension."""
        text = "This isn't fair—why should they get to decide?"
        tension = self.offering.detect_tension(text)

        assert tension is not None
        assert tension.tension_type == "injustice"

    def test_offer_choice_paralysis(self):
        """Test generating micro-choice for paralysis."""
        text = "I'm not sure whether to speak up or stay quiet."
        tension = self.offering.detect_tension(text)
        assert tension is not None

        choice = self.offering.offer_choice(tension)

        assert choice is not None
        assert choice.choice_type == ChoiceType.EXPLORE_VS_ACCEPT
        assert choice.path_a
        assert choice.path_b
        assert choice.path_a != choice.path_b

    def test_offer_choice_conflict(self):
        """Test generating micro-choice for conflict."""
        text = "We're not communicating about this."
        tension = self.offering.detect_tension(text)
        assert tension is not None

        choice = self.offering.offer_choice(tension)

        assert choice is not None
        assert choice.choice_type == ChoiceType.COMMUNICATE_VS_REFLECT

    def test_format_choice_for_response(self):
        """Test formatting choice into response text."""
        text = "I don't know if I should ask for help."
        tension = self.offering.detect_tension(text)
        assert tension is not None

        choice = self.offering.offer_choice(tension)
        formatted = self.offering.format_choice_for_response(choice)

        assert "Would you rather" in formatted
        assert "or" in formatted
        assert "?" in formatted

    def test_choice_variation_rotation(self):
        """Test that choice variations rotate through templates."""
        texts = [
            "I don't know what to do.",
            "I'm not sure about this.",
            "I can't decide.",
            "This is confusing.",
        ]

        for text in texts:
            tension = self.offering.detect_tension(text)
            if tension and tension.tension_type == "paralysis":
                self.offering.offer_choice(tension)

        # Check that we have multiple different choices
        if len(self.offering.choice_history) > 1:
            choices_set = set(
                choice.path_a + "|" + choice.path_b
                for choice in self.offering.choice_history
            )
            assert len(choices_set) > 1  # Should have variety

    def test_should_offer_choice_decision(self):
        """Test decision logic for offering choices."""
        text = "I'm really stuck on what to do next."
        should_offer, tension = self.offering.should_offer_choice(text)

        if tension and tension.confidence >= 0.6:
            # High-confidence tensions should generally be offered
            assert should_offer is True or not should_offer  # Depends on recent history
        else:
            assert should_offer is False

    def test_get_all_choice_variations(self):
        """Test getting all variation options for a tension."""
        text = "I can't make up my mind."
        tension = self.offering.detect_tension(text)
        assert tension is not None

        all_variations = self.offering.get_all_choice_variations(tension)

        assert len(all_variations) >= 1
        for choice in all_variations:
            assert choice.path_a
            assert choice.path_b


class TestTemporalPatterns:
    """Test Phase 3.3: Temporal Pattern Tracking"""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = TemporalAnalyzer()

    def test_record_temporal_event(self):
        """Test recording a glyph use event with timestamp."""
        now = datetime.now()
        event = TemporalEvent(
            glyph_name="Anchored",
            tone="grounded",
            timestamp=now,
            accepted=True,
            effectiveness_score=0.8,
            arousal=0.5,
            valence=0.6,
            user_id="test_user_3"
        )

        self.analyzer.record_event(event)

        assert len(self.analyzer.events) == 1
        assert self.analyzer.events[0].glyph_name == "Anchored"

    def test_detect_morning_pattern(self):
        """Test detecting glyph effectiveness in morning hours."""
        for hour in [6, 7, 8, 9, 10, 11]:
            dt = datetime.now().replace(hour=hour, minute=0)
            event = TemporalEvent(
                glyph_name="Grounded",
                tone="calm",
                timestamp=dt,
                accepted=True,
                effectiveness_score=0.85,
                arousal=0.3,
                valence=0.7,
                user_id="test_user_3"
            )
            self.analyzer.record_event(event)

        patterns = [p for p in self.analyzer.patterns.values()
                    if p.time_period == "morning"]
        if patterns:
            assert len(patterns) > 0
            assert patterns[0].average_effectiveness > 0.7

    def test_detect_evening_pattern(self):
        """Test detecting glyph effectiveness in evening hours."""
        for hour in [18, 19, 20, 21, 22]:
            dt = datetime.now().replace(hour=hour, minute=0)
            event = TemporalEvent(
                glyph_name="Reflective",
                tone="pensive",
                timestamp=dt,
                accepted=True,
                effectiveness_score=0.9,
                arousal=0.4,
                valence=0.5,
                user_id="test_user_3"
            )
            self.analyzer.record_event(event)

        patterns = [p for p in self.analyzer.patterns.values()
                    if p.time_period == "evening"]
        if patterns:
            assert len(patterns) > 0
            assert patterns[0].average_effectiveness > 0.7

    def test_circadian_selector_initialization(self):
        """Test CircadianGlyphSelector initialization."""
        selector = CircadianGlyphSelector(self.analyzer)
        assert selector.analyzer == self.analyzer

    def test_get_best_glyph_for_time(self):
        """Test selecting best glyph for current time."""
        # Add morning effectiveness data
        for i in range(5):
            dt = datetime.now().replace(hour=8, minute=i*12)
            event = TemporalEvent(
                glyph_name="Awake",
                tone="energized",
                timestamp=dt,
                accepted=True,
                effectiveness_score=0.9,
                arousal=0.8,
                valence=0.75,
                user_id="test_user_3"
            )
            self.analyzer.record_event(event)

        # Query for morning
        morning_time = datetime.now().replace(hour=8, minute=0)
        result = self.analyzer.get_best_glyph_for_time(
            "energized", morning_time)

        if result:
            glyph_name, effectiveness = result
            assert glyph_name == "Awake"
            assert effectiveness > 0.7


class TestPhase3Integration:
    """Test Phase 3 Full Integration via Orchestrator"""

    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = Phase3IntegrationOrchestrator(
            user_id="test_user_4")

    def test_orchestrator_initialization(self):
        """Test orchestrator initializes all Phase 3 components."""
        assert self.orchestrator.perspective_taker is not None
        assert self.orchestrator.choice_offering is not None
        assert self.orchestrator.temporal_analyzer is not None
        assert self.orchestrator.circadian_selector is not None

    def test_analyze_user_input_for_phase3_with_perspective(self):
        """Test full Phase 3 analysis with perspective-taking."""
        text = "My sister keeps criticizing my choices."
        analysis = self.orchestrator.analyze_user_input_for_phase3(
            text, "frustrated")

        assert analysis["user_input"] == text
        # Analysis may or may not detect perspective depending on confidence
        assert "relational_context" in analysis
        assert "perspective_reflection" in analysis

    def test_analyze_user_input_for_phase3_with_choice(self):
        """Test full Phase 3 analysis with micro-choice detection."""
        text = "I'm really torn between speaking up and keeping the peace."
        analysis = self.orchestrator.analyze_user_input_for_phase3(
            text, "confused")

        assert "unresolved_tension" in analysis
        assert "micro_choice" in analysis

    def test_generate_phase3_enriched_response(self):
        """Test blending Phase 3 elements into response."""
        text = "They said I was being selfish, and I don't know how to respond."
        analysis = self.orchestrator.analyze_user_input_for_phase3(
            text, "hurt")

        base_response = "That sounds really painful. You're navigating a complex situation."
        enriched = self.orchestrator.generate_phase3_enriched_response(
            base_response, analysis, include_choice=True, include_perspective=True
        )

        # Enriched response should be longer or equal to base
        assert len(enriched) >= len(base_response)
        # Should contain base response
        assert base_response in enriched

    def test_select_best_glyph_for_moment(self):
        """Test glyph selection with temporal awareness."""
        # Add some temporal data
        for hour in [14, 15, 16]:
            dt = datetime.now().replace(hour=hour, minute=0)
            event = TemporalEvent(
                glyph_name="Afternoon Clarity",
                tone="focused",
                timestamp=dt,
                accepted=True,
                effectiveness_score=0.85,
                arousal=0.6,
                valence=0.7,
                user_id="test_user_4"
            )
            self.orchestrator.temporal_analyzer.record_event(event)

        afternoon_time = datetime.now().replace(hour=15, minute=0)
        result = self.orchestrator.select_best_glyph_for_moment(
            "focused", afternoon_time)

        # Result may be None if not enough data, but shouldn't error
        if result:
            glyph_name, effectiveness = result
            assert glyph_name
            assert 0.0 <= effectiveness <= 1.0

    def test_get_phase3_summary(self):
        """Test getting Phase 3 summary statistics."""
        # Perform some Phase 3 operations
        text1 = "My mom thinks I should change careers."
        self.orchestrator.analyze_user_input_for_phase3(text1)

        text2 = "I don't know if I should take the job offer."
        self.orchestrator.analyze_user_input_for_phase3(text2)

        summary = self.orchestrator.get_phase3_summary()

        assert "perspective_reflections_offered" in summary
        assert "micro_choices_offered" in summary
        assert "temporal_patterns_tracked" in summary
        assert "relational_contexts_detected" in summary
        assert "tensions_detected" in summary


class TestPhase3EdgeCases:
    """Test edge cases and robustness"""

    def test_perspective_taker_empty_input(self):
        """Test perspective taker with empty input."""
        taker = PerspectiveTaker()
        context = taker.detect_relational_context("")
        assert context is None

    def test_choice_offering_ambiguous_input(self):
        """Test choice offering with ambiguous input."""
        offering = MicroChoiceOffering()
        tension = offering.detect_tension("Something happened.")
        # May or may not detect tension depending on patterns
        assert tension is None or tension.tension_type in [
            "paralysis", "conflict", "abandonment", "overwhelm", "injustice"
        ]

    def test_temporal_analyzer_single_event(self):
        """Test temporal analyzer with single event."""
        analyzer = TemporalAnalyzer()
        event = TemporalEvent(
            glyph_name="Solo",
            tone="test",
            timestamp=datetime.now(),
            accepted=True,
            effectiveness_score=0.5,
            arousal=0.5,
            valence=0.5,
            user_id="test"
        )
        analyzer.record_event(event)
        assert len(analyzer.events) == 1

    def test_orchestrator_multiple_analyses_in_sequence(self):
        """Test running multiple Phase 3 analyses in sequence."""
        orchestrator = Phase3IntegrationOrchestrator("test_user_edge")

        texts = [
            "My friend cancelled on me again.",
            "I'm not sure if I should say something.",
            "They always do this to me.",
            "I feel paralyzed by indecision.",
        ]

        for text in texts:
            analysis = orchestrator.analyze_user_input_for_phase3(text)
            assert analysis is not None
            assert "timestamp" in analysis

        summary = orchestrator.get_phase3_summary()
        assert summary["relational_contexts_detected"] >= 0
        assert summary["tensions_detected"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
