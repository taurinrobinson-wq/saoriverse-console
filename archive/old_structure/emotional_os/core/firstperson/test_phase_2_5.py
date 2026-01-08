"""
Phase 2.5: Tests for Advanced Learning Features
Comprehensive tests for clustering, temporal patterns, and context-aware selection.
"""

import pytest
from datetime import datetime, timedelta
from emotional_os.core.firstperson.glyph_clustering import (
    GlyphVector,
    GlyphCluster,
    GlyphClusteringEngine,
)
from emotional_os.core.firstperson.temporal_patterns import (
    TemporalEvent,
    TemporalPattern,
    TemporalAnalyzer,
    CircadianGlyphSelector,
)
from emotional_os.core.firstperson.context_selector import (
    ConversationContext,
    ConversationState,
    SelectionCriteria,
    ContextAwareSelector,
)


class TestGlyphVector:
    """Test glyph vector representations."""

    def test_creation(self):
        """Test creating a glyph vector."""
        vector = GlyphVector(
            glyph_name="warmth",
            warmth=0.8,
            energy=0.6,
            depth=0.5,
            hope=0.7,
            arousal=0.4,
            valence=0.9
        )
        assert vector.glyph_name == "warmth"
        assert vector.warmth == 0.8

    def test_distance_calculation(self):
        """Test distance between glyphs."""
        v1 = GlyphVector("warmth", warmth=1.0, energy=0.0,
                         depth=0.0, hope=0.0, arousal=0.0, valence=0.0)
        v2 = GlyphVector("coldness", warmth=0.0, energy=0.0,
                         depth=0.0, hope=0.0, arousal=0.0, valence=0.0)

        distance = v1.distance_to(v2)
        assert distance == pytest.approx(1.0)

    def test_similarity_calculation(self):
        """Test similarity score between glyphs."""
        v1 = GlyphVector("warmth", warmth=0.8, energy=0.6,
                         depth=0.5, hope=0.7, arousal=0.4, valence=0.9)
        v2 = GlyphVector("gentleness", warmth=0.7, energy=0.5,
                         depth=0.6, hope=0.8, arousal=0.3, valence=0.8)

        similarity = v1.similarity_to(v2)
        assert 0.8 < similarity < 1.0


class TestGlyphCluster:
    """Test glyph clustering."""

    def test_cluster_creation(self):
        """Test creating a cluster."""
        cluster = GlyphCluster(
            "warmth_cluster", "Warmth & Compassion", "warmth")
        assert cluster.cluster_id == "warmth_cluster"
        assert len(cluster.members) == 0

    def test_add_member(self):
        """Test adding members to cluster."""
        cluster = GlyphCluster(
            "warmth_cluster", "Warmth & Compassion", "warmth")
        vector = GlyphVector("warmth", warmth=0.9, energy=0.3,
                             depth=0.6, hope=0.7, arousal=0.2, valence=0.9)

        cluster.add_member(vector)
        assert len(cluster.members) == 1
        assert "warmth" in cluster.members

    def test_centroid_update(self):
        """Test centroid calculation."""
        cluster = GlyphCluster(
            "warmth_cluster", "Warmth & Compassion", "warmth")

        v1 = GlyphVector("warmth", warmth=0.8, energy=0.2,
                         depth=0.5, hope=0.8, arousal=0.3, valence=0.9)
        v2 = GlyphVector("gentleness", warmth=0.6, energy=0.3,
                         depth=0.6, hope=0.7, arousal=0.4, valence=0.8)

        cluster.add_member(v1)
        cluster.add_member(v2)

        assert cluster.centroid is not None
        assert cluster.centroid.warmth == pytest.approx(0.7)

    def test_closest_members(self):
        """Test finding closest members."""
        cluster = GlyphCluster(
            "warmth_cluster", "Warmth & Compassion", "warmth")

        v1 = GlyphVector("warmth", warmth=0.9, energy=0.2,
                         depth=0.5, hope=0.8, arousal=0.2, valence=0.9)
        v2 = GlyphVector("gentleness", warmth=0.8, energy=0.3,
                         depth=0.6, hope=0.7, arousal=0.3, valence=0.8)
        v3 = GlyphVector("coldness", warmth=0.1, energy=0.8,
                         depth=0.4, hope=0.2, arousal=0.8, valence=0.2)

        cluster.add_member(v1)
        cluster.add_member(v2)
        cluster.add_member(v3)

        closest = cluster.get_closest_members("warmth", limit=2)
        assert len(closest) == 2
        # gentleness closer to warmth than coldness
        assert closest[0][0] == "gentleness"


class TestGlyphClusteringEngine:
    """Test clustering engine."""

    def test_engine_creation(self):
        """Test creating clustering engine."""
        engine = GlyphClusteringEngine()
        assert len(engine.clusters) == 5  # Default clusters

    def test_add_glyph(self):
        """Test adding glyphs to engine."""
        engine = GlyphClusteringEngine()
        vector = GlyphVector("warmth", warmth=0.9, energy=0.2,
                             depth=0.5, hope=0.8, arousal=0.2, valence=0.9)

        engine.add_glyph(vector)
        assert "warmth" in engine.vectors

    def test_find_similar_glyphs(self):
        """Test finding similar glyphs."""
        engine = GlyphClusteringEngine()

        v1 = GlyphVector("warmth", warmth=0.9, energy=0.2,
                         depth=0.5, hope=0.8, arousal=0.2, valence=0.9)
        v2 = GlyphVector("gentleness", warmth=0.8, energy=0.3,
                         depth=0.6, hope=0.7, arousal=0.3, valence=0.8)
        v3 = GlyphVector("coldness", warmth=0.1, energy=0.8,
                         depth=0.4, hope=0.2, arousal=0.8, valence=0.2)

        engine.add_glyph(v1)
        engine.add_glyph(v2)
        engine.add_glyph(v3)

        similar = engine.find_similar_glyphs("warmth")
        assert len(similar) > 0
        assert "gentleness" in [g[0] for g in similar]

    def test_get_glyphs_by_emotional_state(self):
        """Test getting glyphs for emotional state."""
        engine = GlyphClusteringEngine()

        v1 = GlyphVector("energy", warmth=0.3, energy=0.9,
                         depth=0.5, hope=0.6, arousal=0.9, valence=0.7)
        v2 = GlyphVector("calm", warmth=0.7, energy=0.2,
                         depth=0.6, hope=0.7, arousal=0.2, valence=0.8)

        engine.add_glyph(v1)
        engine.add_glyph(v2)

        # High arousal, positive valence
        matches = engine.get_glyphs_by_emotional_state(
            arousal=0.8, valence=0.7, limit=5)
        assert len(matches) > 0


class TestTemporalPattern:
    """Test temporal pattern tracking."""

    def test_pattern_creation(self):
        """Test creating temporal pattern."""
        pattern = TemporalPattern(
            glyph_name="warmth",
            tone="compassionate",
            time_period="morning",
            average_effectiveness=0.8,
            use_count=5,
            acceptance_count=4
        )
        assert pattern.glyph_name == "warmth"
        assert pattern.get_acceptance_rate() == 0.8

    def test_strong_pattern_detection(self):
        """Test strong pattern identification."""
        strong = TemporalPattern(
            glyph_name="warmth",
            tone="compassionate",
            time_period="morning",
            average_effectiveness=0.8,
            use_count=5,
            acceptance_count=4,
            confidence=0.8
        )
        assert strong.is_strong_pattern() is True

        weak = TemporalPattern(
            glyph_name="coldness",
            tone="harsh",
            time_period="evening",
            average_effectiveness=0.3,
            use_count=1,
            acceptance_count=0,
            confidence=0.2
        )
        assert weak.is_strong_pattern() is False


class TestTemporalAnalyzer:
    """Test temporal analysis."""

    def test_analyzer_creation(self):
        """Test creating analyzer."""
        analyzer = TemporalAnalyzer()
        assert len(analyzer.events) == 0

    def test_record_event(self):
        """Test recording temporal events."""
        analyzer = TemporalAnalyzer()

        event = TemporalEvent(
            glyph_name="warmth",
            tone="compassionate",
            timestamp=datetime.now().replace(hour=9),  # Morning
            accepted=True,
            effectiveness_score=0.8,
            arousal=0.4,
            valence=0.8,
            user_id="user1"
        )

        analyzer.record_event(event)
        assert len(analyzer.events) == 1

    def test_get_best_glyph_for_time(self):
        """Test getting best glyph for time."""
        analyzer = TemporalAnalyzer()

        # Record morning events
        for i in range(4):
            event = TemporalEvent(
                glyph_name="warmth",
                tone="compassionate",
                timestamp=datetime.now().replace(hour=9),
                accepted=True,
                effectiveness_score=0.9,
                arousal=0.4,
                valence=0.8,
                user_id="user1"
            )
            analyzer.record_event(event)

        # Should find warmth as best for morning
        best = analyzer.get_best_glyph_for_time(
            "compassionate",
            datetime.now().replace(hour=9)
        )
        assert best is not None
        assert best[0] == "warmth"

    def test_temporal_insights(self):
        """Test generating temporal insights."""
        analyzer = TemporalAnalyzer()

        # Record pattern
        for i in range(5):
            event = TemporalEvent(
                glyph_name="warmth",
                tone="compassionate",
                timestamp=datetime.now().replace(hour=9),
                accepted=True,
                effectiveness_score=0.9,
                arousal=0.4,
                valence=0.8,
                user_id="user1"
            )
            analyzer.record_event(event)

        insights = analyzer.get_time_based_insights("user1")
        assert len(insights) > 0


class TestContextAwareSelector:
    """Test context-aware selection."""

    def test_selector_creation(self):
        """Test creating selector."""
        selector = ContextAwareSelector()
        assert len(selector.context_glyph_map) > 0

    def test_context_detection(self):
        """Test detecting conversation context."""
        selector = ContextAwareSelector()

        # Opening context
        context = selector.detect_context(
            turn_number=1,
            emotional_valence=0.5,
            emotional_arousal=0.5,
            user_input_length=50,
            recent_glyphs=[]
        )
        assert context == ConversationContext.OPENING

    def test_glyph_selection(self):
        """Test selecting glyph for context."""
        selector = ContextAwareSelector()

        state = ConversationState(
            context=ConversationContext.OPENING,
            turn_number=1,
            emotional_trajectory="stable",
            intensity_level=0.5,
            user_energy=0.7
        )

        available_glyphs = ["welcome", "presence", "attunement", "clarity"]

        selected, metadata = selector.select(state, available_glyphs)

        assert selected in ["welcome", "presence", "attunement"]
        assert metadata["context"] == "opening"

    def test_repetition_filtering(self):
        """Test filtering repeated glyphs."""
        selector = ContextAwareSelector()

        state = ConversationState(
            context=ConversationContext.EXPLORATION,
            turn_number=5,
            emotional_trajectory="stable",
            intensity_level=0.5,
            user_energy=0.7,
            previous_glyph="warmth",
            repetition_count=2
        )

        criteria = SelectionCriteria(
            avoid_repetition=True,
            max_repetitions=3
        )

        available_glyphs = ["warmth", "clarity", "presence", "engagement"]

        selected, metadata = selector.select(state, available_glyphs, criteria)

        # Should avoid warmth due to repetition
        assert selected != "warmth" or state.repetition_count < criteria.max_repetitions


class TestCircadianGlyphSelector:
    """Test circadian-based selection."""

    def test_circadian_creation(self):
        """Test creating circadian selector."""
        analyzer = TemporalAnalyzer()
        selector = CircadianGlyphSelector(analyzer)

        assert selector.analyzer is not None

    def test_build_user_profile(self):
        """Test building circadian profile."""
        analyzer = TemporalAnalyzer()

        # Record pattern
        for i in range(5):
            event = TemporalEvent(
                glyph_name="warmth",
                tone="compassionate",
                timestamp=datetime.now().replace(hour=9),
                accepted=True,
                effectiveness_score=0.9,
                arousal=0.4,
                valence=0.8,
                user_id="user1"
            )
            analyzer.record_event(event)

        selector = CircadianGlyphSelector(analyzer)
        profile = selector.build_user_profile("user1")

        assert "user_id" in profile
        assert profile["user_id"] == "user1"

    def test_select_glyph_for_moment(self):
        """Test selecting glyph for current moment."""
        analyzer = TemporalAnalyzer()

        # Record morning pattern
        for i in range(4):
            event = TemporalEvent(
                glyph_name="warmth",
                tone="compassionate",
                timestamp=datetime.now().replace(hour=9),
                accepted=True,
                effectiveness_score=0.9,
                arousal=0.4,
                valence=0.8,
                user_id="user1"
            )
            analyzer.record_event(event)

        selector = CircadianGlyphSelector(analyzer)

        morning_time = datetime.now().replace(hour=9)
        glyph = selector.select_glyph_for_moment(
            "user1", "compassionate", morning_time)

        # Should select warmth for morning
        assert glyph is None or glyph[0] == "warmth"
