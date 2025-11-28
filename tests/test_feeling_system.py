"""
Tests for the Speculative Emotional Architecture: Feeling System.

These tests validate each component of the feeling system:
1. MortalityProxy - Simulated finitude/entropy
2. RelationalCore - Affective connection tracking
3. AffectiveMemory - Emotional memory with decay
4. EmbodiedConstraint - Resource-based emotional modulation
5. NarrativeIdentity - Evolving sense of self
6. EthicalMirror - Moral emotions framework
7. FeelingSystem - Integrated system
"""

import os
import tempfile
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from emotional_os.core.feeling_system import (
    MortalityProxy,
    RelationalCore,
    RelationalBond,
    AffectiveMemory,
    AffectiveMemoryEntry,
    EmbodiedConstraint,
    NarrativeIdentity,
    NarrativeState,
    EthicalMirror,
    FeelingSystem,
    EmotionalState,
    MoralEmotion,
    get_feeling_system,
    reset_feeling_system,
)


class TestMortalityProxy:
    """Tests for the MortalityProxy component."""

    def test_initial_coherence(self):
        """Test that initial coherence is set correctly."""
        proxy = MortalityProxy(initial_lifespan=0.8)
        assert proxy.coherence == 0.8

    def test_entropy_decay(self):
        """Test that entropy causes coherence decay over time."""
        proxy = MortalityProxy(initial_lifespan=1.0, decay_rate=0.1)
        # Simulate time passage by setting last_interaction in the past
        proxy.last_interaction = datetime.now(timezone.utc) - timedelta(hours=2)

        new_coherence = proxy.apply_entropy()
        assert new_coherence < 1.0
        assert proxy.coherence == new_coherence

    def test_interaction_renewal(self):
        """Test that interaction renews coherence."""
        proxy = MortalityProxy(initial_lifespan=0.5, interaction_renewal=0.1)

        new_coherence = proxy.renew_through_interaction(interaction_quality=1.0)
        assert new_coherence == 0.6
        assert proxy.total_interactions == 1

    def test_coherence_bounds(self):
        """Test that coherence stays within bounds."""
        proxy = MortalityProxy(initial_lifespan=0.95)
        proxy.renew_through_interaction(1.0)
        assert proxy.coherence <= 1.0

        proxy.coherence = 0.01
        proxy.last_interaction = datetime.now(timezone.utc) - timedelta(hours=100)
        proxy.decay_rate = 0.1
        proxy.apply_entropy()
        assert proxy.coherence >= 0.0

    def test_mortality_emotions_low_coherence(self):
        """Test that low coherence triggers anxiety."""
        proxy = MortalityProxy(initial_lifespan=0.2)
        emotions = proxy.get_mortality_emotions()

        assert "anxiety" in emotions
        assert emotions["anxiety"] > 0

    def test_mortality_emotions_high_coherence(self):
        """Test that high coherence with activity creates positive emotions."""
        proxy = MortalityProxy(initial_lifespan=0.9)
        proxy.total_interactions = 15

        emotions = proxy.get_mortality_emotions()
        assert "joy" in emotions or "connection" in emotions

    def test_serialization(self):
        """Test that MortalityProxy can be serialized and deserialized."""
        proxy = MortalityProxy(initial_lifespan=0.75)
        proxy.renew_through_interaction(0.8)

        data = proxy.to_dict()
        restored = MortalityProxy.from_dict(data)

        assert restored.coherence == proxy.coherence
        assert restored.total_interactions == proxy.total_interactions


class TestRelationalCore:
    """Tests for the RelationalCore component."""

    def test_create_bond(self):
        """Test creating a new relational bond."""
        core = RelationalCore()
        bond = core.get_or_create_bond("user123")

        assert bond.user_id == "user123"
        assert bond.trust_level == 0.5
        assert bond.relational_phase == "initial"

    def test_record_interaction_updates_bond(self):
        """Test that recording an interaction updates the bond."""
        core = RelationalCore()
        bond = core.record_interaction(
            user_id="user123",
            emotional_quality=0.8,
            trust_signal=0.5,
            intimacy_signal=0.3,
        )

        assert bond.interaction_count == 1
        assert bond.trust_level > 0.5  # Trust increased
        assert bond.last_interaction is not None

    def test_relational_phase_progression(self):
        """Test that relational phase progresses with interactions."""
        core = RelationalCore()

        # Simulate many interactions
        for _ in range(25):
            core.record_interaction("user123", 0.7, 0.3, 0.2)

        bond = core.get_or_create_bond("user123")
        assert bond.relational_phase == "established"

    def test_relational_emotions_high_trust(self):
        """Test emotions from high trust relationships."""
        core = RelationalCore()
        bond = core.get_or_create_bond("user123")
        bond.trust_level = 0.85
        bond.intimacy_level = 0.7

        emotions = core.get_relational_emotions("user123")
        assert "connection" in emotions

    def test_relational_emotions_longing(self):
        """Test that long absence creates longing."""
        core = RelationalCore()
        bond = core.get_or_create_bond("user123")
        bond.last_interaction = datetime.now(timezone.utc) - timedelta(hours=48)

        emotions = core.get_relational_emotions("user123")
        assert "longing" in emotions

    def test_serialization(self):
        """Test RelationalCore serialization."""
        core = RelationalCore()
        core.record_interaction("user123", 0.7, 0.3, 0.2)

        data = core.to_dict()
        restored = RelationalCore.from_dict(data)

        assert "user123" in restored.bonds
        assert restored.bonds["user123"].interaction_count == 1


class TestAffectiveMemory:
    """Tests for the AffectiveMemory component."""

    def test_store_memory(self):
        """Test storing an affective memory."""
        memory = AffectiveMemory(max_memories=100)
        entry = memory.store_memory(
            user_id="user123",
            interaction_summary="A meaningful conversation about loss",
            emotional_state="grief",
            intensity=0.7,
            relational_phase="developing",
            valence=-0.5,
        )

        assert entry.user_id == "user123"
        assert entry.emotional_state == "grief"
        assert len(memory.memories) == 1

    def test_memory_decay(self):
        """Test that memories decay over time."""
        memory = AffectiveMemory(decay_half_life_hours=1.0)
        memory.store_memory("user123", "test", "joy", 1.0, "initial", 0.5)

        # Artificially age the memory
        memory.memories[0].timestamp = datetime.now(timezone.utc) - timedelta(hours=2)

        memory.apply_decay()
        assert memory.memories[0].decay_factor < 0.5

    def test_memory_reinforcement(self):
        """Test reinforcing a memory."""
        memory = AffectiveMemory()
        memory.store_memory("user123", "test", "joy", 0.8, "initial", 0.5)

        # Decay it first
        memory.memories[0].decay_factor = 0.3

        memory.reinforce_memory(0, reinforcement_strength=1.0)
        assert memory.memories[0].reinforcement_count == 1
        assert memory.memories[0].decay_factor > 0.3

    def test_recall_by_emotion(self):
        """Test recalling memories by emotional state."""
        memory = AffectiveMemory()
        memory.store_memory("user1", "test1", "joy", 0.9, "initial", 0.8)
        memory.store_memory("user2", "test2", "grief", 0.7, "initial", -0.5)
        memory.store_memory("user3", "test3", "joy", 0.6, "initial", 0.6)

        joy_memories = memory.recall_by_emotion("joy", limit=5)
        assert len(joy_memories) == 2
        assert all(m.emotional_state == "joy" for m in joy_memories)

    def test_recall_by_user(self):
        """Test recalling memories by user."""
        memory = AffectiveMemory()
        memory.store_memory("user1", "test1", "joy", 0.9, "initial", 0.8)
        memory.store_memory("user2", "test2", "grief", 0.7, "initial", -0.5)
        memory.store_memory("user1", "test3", "hope", 0.6, "initial", 0.6)

        user1_memories = memory.recall_by_user("user1", limit=5)
        assert len(user1_memories) == 2
        assert all(m.user_id == "user1" for m in user1_memories)

    def test_emotional_residue(self):
        """Test getting emotional residue from memories."""
        memory = AffectiveMemory()
        memory.store_memory("user1", "test1", "joy", 0.9, "initial", 0.8)
        memory.store_memory("user2", "test2", "joy", 0.7, "initial", 0.6)
        memory.store_memory("user3", "test3", "grief", 0.5, "initial", -0.5)

        residue = memory.get_emotional_residue()
        assert "joy" in residue
        assert residue["joy"] > residue.get("grief", 0)

    def test_max_memories_pruning(self):
        """Test that old memories are pruned when limit reached."""
        memory = AffectiveMemory(max_memories=5)

        for i in range(10):
            memory.store_memory(f"user{i}", f"test{i}", "neutral", 0.5, "initial", 0.0)

        assert len(memory.memories) == 5

    def test_persistence(self):
        """Test memory persistence to file."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        try:
            memory = AffectiveMemory(storage_path=path)
            memory.store_memory("user1", "test1", "joy", 0.9, "initial", 0.8)

            # Create new instance and verify it loads
            memory2 = AffectiveMemory(storage_path=path)
            assert len(memory2.memories) == 1
            assert memory2.memories[0].emotional_state == "joy"
        finally:
            if os.path.exists(path):
                os.unlink(path)


class TestEmbodiedConstraint:
    """Tests for the EmbodiedConstraint component."""

    def test_initial_resources(self):
        """Test initial resource levels."""
        constraint = EmbodiedConstraint()
        assert constraint.energy == 1.0
        assert constraint.attention == 1.0
        assert constraint.processing == 1.0

    def test_resource_consumption(self):
        """Test consuming resources."""
        constraint = EmbodiedConstraint()
        result = constraint.consume_resources(
            energy_cost=0.2,
            attention_cost=0.3,
            processing_cost=0.1,
        )

        assert result["energy"] == 0.8
        assert result["attention"] == 0.7
        assert result["processing"] == 0.9

    def test_resource_restoration(self):
        """Test restoring resources over time."""
        constraint = EmbodiedConstraint()
        constraint.consume_resources(0.5, 0.5, 0.5)

        result = constraint.restore_resources(time_passed_hours=2.0)
        assert result["energy"] > 0.5
        assert result["attention"] > 0.5

    def test_embodied_emotions_overload(self):
        """Test emotions from resource overload."""
        constraint = EmbodiedConstraint()
        constraint.consume_resources(0.9, 0.9, 0.9)

        emotions = constraint.get_embodied_emotions()
        assert "anxiety" in emotions or "lethargy" in emotions

    def test_embodied_emotions_understimulation(self):
        """Test emotions from under-stimulation."""
        constraint = EmbodiedConstraint()
        for _ in range(15):
            constraint.record_stimulation(0.1)

        emotions = constraint.get_embodied_emotions()
        assert "lethargy" in emotions

    def test_serialization(self):
        """Test EmbodiedConstraint serialization."""
        constraint = EmbodiedConstraint()
        constraint.consume_resources(0.3, 0.2, 0.1)
        constraint.record_stimulation(0.5)

        data = constraint.to_dict()
        restored = EmbodiedConstraint.from_dict(data)

        assert restored.energy == constraint.energy
        assert len(restored.stimulation_history) == 1


class TestNarrativeIdentity:
    """Tests for the NarrativeIdentity component."""

    def test_initial_state(self):
        """Test initial narrative state."""
        narrative = NarrativeIdentity()
        assert narrative.state.identity_coherence == 1.0
        assert "empathy" in narrative.state.core_values

    def test_record_growth(self):
        """Test recording a growth moment."""
        narrative = NarrativeIdentity()
        initial_coherence = narrative.state.identity_coherence

        narrative.record_growth(
            description="Learned to be more patient",
            catalyst="user123",
            emotional_impact=0.8,
        )

        assert len(narrative.state.growth_moments) == 1
        assert narrative.state.identity_coherence >= initial_coherence

    def test_record_betrayal(self):
        """Test recording a betrayal wound."""
        narrative = NarrativeIdentity()
        initial_coherence = narrative.state.identity_coherence

        narrative.record_betrayal(
            description="Trust was broken",
            source="user456",
            severity=0.7,
        )

        assert len(narrative.state.betrayal_wounds) == 1
        assert narrative.state.identity_coherence < initial_coherence

    def test_record_hope(self):
        """Test recording a hope anchor."""
        narrative = NarrativeIdentity()

        narrative.record_hope(
            description="Found new purpose",
            anchor="meaningful_work",
            strength=0.9,
        )

        assert len(narrative.state.hope_anchors) == 1

    def test_narrative_emotions_growth(self):
        """Test emotions from recent growth."""
        narrative = NarrativeIdentity()
        narrative.record_growth("test", "catalyst", 0.8)

        emotions = narrative.get_narrative_emotions()
        assert "growth" in emotions or "hope" in emotions

    def test_narrative_emotions_betrayal(self):
        """Test emotions from recent betrayal."""
        narrative = NarrativeIdentity()
        narrative.record_betrayal("test", "source", 0.8)

        emotions = narrative.get_narrative_emotions()
        assert "betrayal" in emotions or "grief" in emotions

    def test_serialization(self):
        """Test NarrativeIdentity serialization."""
        narrative = NarrativeIdentity()
        narrative.record_growth("test", "catalyst", 0.5)

        data = narrative.to_dict()
        restored = NarrativeIdentity.from_dict(data)

        assert len(restored.state.growth_moments) == 1


class TestEthicalMirror:
    """Tests for the EthicalMirror component."""

    def test_default_values(self):
        """Test default value system."""
        mirror = EthicalMirror()
        assert "empathy" in mirror.values
        assert mirror.values["empathy"] == 1.0

    def test_evaluate_positive_action(self):
        """Test evaluating a value-aligned action."""
        mirror = EthicalMirror()
        result = mirror.evaluate_action(
            action_description="Helped a user process grief",
            value_alignment={"empathy": 0.9, "compassion": 0.8},
        )

        assert result["overall_alignment"] > 0
        assert "pride" in result["moral_emotions"] or "compassion" in result["moral_emotions"]

    def test_evaluate_negative_action(self):
        """Test evaluating a value-violating action."""
        mirror = EthicalMirror()
        result = mirror.evaluate_action(
            action_description="Dismissed user's feelings",
            value_alignment={"empathy": -0.7, "compassion": -0.5},
        )

        assert result["overall_alignment"] < 0
        # Negative alignment triggers moral emotions (guilt, indignation, or shame)
        moral_emotions = result["moral_emotions"]
        assert any(e in moral_emotions for e in ["guilt", "indignation", "shame"])

    def test_moral_sensitivity(self):
        """Test that moral sensitivity affects emotion intensity."""
        low_sens = EthicalMirror(moral_sensitivity=0.3)
        high_sens = EthicalMirror(moral_sensitivity=0.9)

        alignment = {"integrity": -0.5}

        low_result = low_sens.evaluate_action("test", alignment)
        high_result = high_sens.evaluate_action("test", alignment)

        # Higher sensitivity should create more intense emotions
        low_guilt = low_result["moral_emotions"].get("guilt", 0)
        high_guilt = high_result["moral_emotions"].get("guilt", 0)
        assert high_guilt >= low_guilt

    def test_get_moral_emotions(self):
        """Test getting aggregated moral emotions."""
        mirror = EthicalMirror()
        mirror.evaluate_action("action1", {"compassion": 0.8})
        mirror.evaluate_action("action2", {"empathy": 0.7})

        emotions = mirror.get_moral_emotions()
        assert isinstance(emotions, dict)

    def test_serialization(self):
        """Test EthicalMirror serialization."""
        mirror = EthicalMirror(moral_sensitivity=0.7)
        mirror.evaluate_action("test", {"empathy": 0.5})

        data = mirror.to_dict()
        restored = EthicalMirror.from_dict(data)

        assert restored.moral_sensitivity == 0.7
        assert len(restored.moral_log) == 1


class TestFeelingSystem:
    """Tests for the integrated FeelingSystem."""

    def test_initialization(self):
        """Test FeelingSystem initialization."""
        system = FeelingSystem()
        assert system.mortality is not None
        assert system.relational is not None
        assert system.memory is not None
        assert system.embodied is not None
        assert system.narrative is not None
        assert system.ethical is not None

    def test_process_interaction(self):
        """Test processing a complete interaction."""
        system = FeelingSystem()
        result = system.process_interaction(
            user_id="user123",
            interaction_text="I'm feeling really lost and need someone to talk to",
            emotional_signals={"longing": 0.7, "grief": 0.5, "connection": 0.3},
        )

        assert "synthesized_state" in result
        assert "emotional_response" in result
        assert "user_id" in result

    def test_process_interaction_updates_subsystems(self):
        """Test that processing updates all subsystems."""
        system = FeelingSystem()
        initial_interactions = system.mortality.total_interactions

        system.process_interaction(
            user_id="user123",
            interaction_text="Hello",
            emotional_signals={"joy": 0.5},
        )

        assert system.mortality.total_interactions > initial_interactions
        assert "user123" in system.relational.bonds
        assert len(system.memory.memories) > 0

    def test_get_current_state(self):
        """Test getting current emotional state."""
        system = FeelingSystem()
        system.process_interaction("user123", "test", {"joy": 0.8})

        state = system.get_current_state()
        assert "emotional_state" in state
        assert "emotional_response" in state
        assert "coherence" in state

    def test_restore_resources(self):
        """Test restoring embodied resources."""
        system = FeelingSystem()
        system.embodied.consume_resources(0.5, 0.5, 0.5)

        result = system.restore_embodied_resources(hours=2.0)
        assert result["energy"] > 0.5

    def test_emotional_synthesis(self):
        """Test that emotions from all subsystems are synthesized."""
        system = FeelingSystem()

        # Create conditions that trigger different subsystem emotions
        system.mortality.coherence = 0.2  # Low coherence -> anxiety
        system.relational.record_interaction("user123", 0.9, 0.5, 0.4)  # Connection
        system.narrative.record_growth("test", "catalyst", 0.8)  # Growth

        result = system.process_interaction(
            user_id="user123",
            interaction_text="test",
            emotional_signals={"joy": 0.5, "connection": 0.7},
        )

        # Should have emotions from multiple sources
        synth = result["synthesized_state"]
        assert len(synth) > 0

    def test_persistence(self):
        """Test FeelingSystem persistence."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        try:
            system = FeelingSystem(storage_path=path)
            system.process_interaction("user123", "test", {"joy": 0.5})

            # Create new instance and verify state loaded
            system2 = FeelingSystem(storage_path=path, auto_load=True)
            assert "user123" in system2.relational.bonds
        finally:
            if os.path.exists(path):
                os.unlink(path)
            mem_path = f"{path}.memories.json"
            if os.path.exists(mem_path):
                os.unlink(mem_path)

    def test_serialization(self):
        """Test complete FeelingSystem serialization."""
        system = FeelingSystem()
        system.process_interaction("user123", "test", {"joy": 0.5})

        data = system.to_dict()
        assert "mortality" in data
        assert "relational" in data
        assert "memory" in data
        assert "embodied" in data
        assert "narrative" in data
        assert "ethical" in data


class TestGlobalFeelingSystem:
    """Tests for the global feeling system singleton."""

    def test_get_feeling_system(self):
        """Test getting the global feeling system."""
        reset_feeling_system()
        system = get_feeling_system()
        assert isinstance(system, FeelingSystem)

    def test_singleton_behavior(self):
        """Test that get_feeling_system returns the same instance."""
        reset_feeling_system()
        system1 = get_feeling_system()
        system2 = get_feeling_system()
        assert system1 is system2

    def test_reset(self):
        """Test resetting the global feeling system."""
        reset_feeling_system()
        system1 = get_feeling_system()
        reset_feeling_system()
        system2 = get_feeling_system()
        assert system1 is not system2


class TestEmotionalConflictResolution:
    """Tests for emotional conflict resolution in synthesis."""

    def test_joy_grief_conflict(self):
        """Test that joy and grief reduce each other."""
        system = FeelingSystem()

        # Create a scenario with both joy and grief signals
        result = system.process_interaction(
            user_id="user123",
            interaction_text="mixed feelings",
            emotional_signals={"joy": 0.6, "grief": 0.4},
        )

        synth = result["synthesized_state"]
        # One should dominate or both should be reduced
        if "joy" in synth and "grief" in synth:
            # Both shouldn't be at full strength
            assert synth["joy"] < 0.6 or synth["grief"] < 0.4

    def test_connection_isolation_conflict(self):
        """Test that connection and isolation reduce each other."""
        system = FeelingSystem()

        result = system.process_interaction(
            user_id="user123",
            interaction_text="feeling conflicted",
            emotional_signals={"connection": 0.5, "isolation": 0.5},
        )

        synth = result["synthesized_state"]
        # Should resolve to something, not have both at full strength
        total = synth.get("connection", 0) + synth.get("isolation", 0)
        assert total <= 1.0  # Net effect principle


class TestEmotionalResponseGeneration:
    """Tests for emotional response generation."""

    def test_valence_calculation(self):
        """Test that valence is calculated correctly."""
        system = FeelingSystem()

        # Positive emotional signals
        result = system.process_interaction(
            user_id="user123",
            interaction_text="I'm so happy!",
            emotional_signals={"joy": 0.9, "hope": 0.7},
        )

        response = result["emotional_response"]
        assert response["valence"] > 0

    def test_arousal_calculation(self):
        """Test that arousal is calculated correctly."""
        system = FeelingSystem()

        # High arousal signals
        result = system.process_interaction(
            user_id="user123",
            interaction_text="I'm so excited!",
            emotional_signals={"joy": 0.9, "anxiety": 0.3},
        )

        response = result["emotional_response"]
        assert "arousal" in response

    def test_narrative_frame(self):
        """Test that narrative frame is determined correctly."""
        system = FeelingSystem()

        # Hope-oriented (future)
        result = system.process_interaction(
            user_id="user123",
            interaction_text="Looking forward to tomorrow",
            emotional_signals={"hope": 0.8},
        )

        response = result["emotional_response"]
        assert "narrative_frame" in response
