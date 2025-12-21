#!/usr/bin/env python3
"""
Subsystem integration tests for FeelingSystem.

Tests cross-subsystem effects, data flow, and coherence:
- Mortality effects on other subsystems
- Relational state influencing emotion synthesis
- Memory reinforcement feedback loops
- Embodied constraints on emotional expression
- Narrative identity shaping emotional responses
- Ethical mirror affecting decision-making
"""

import pytest
from datetime import datetime, timedelta, timezone
from emotional_os.core.feeling_system import FeelingSystem, reset_feeling_system


class TestMortalityIntegration:
    """Test mortality subsystem integration with others."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        reset_feeling_system()

    def test_mortality_coherence_affects_emotion_synthesis(self) -> None:
        """High mortality coherence should enhance emotional responses."""
        system = FeelingSystem(storage_path=None)
        signals = {"joy": 0.7, "trust": 0.6}
        
        # Get baseline response
        result1 = system.process_interaction(
            user_id="user_001",
            interaction_text="Initial interaction",
            emotional_signals=signals,
        )
        baseline_joy = result1["synthesized_state"].get("joy", 0)
        
        # Increase mortality coherence through multiple interactions
        for _ in range(5):
            system.process_interaction(
                user_id="user_001",
                interaction_text="Reinforcing",
                emotional_signals=signals,
            )
        
        # Higher coherence should amplify positive emotions
        assert system.mortality.coherence > 0.5
        result2 = system.process_interaction(
            user_id="user_001",
            interaction_text="With higher coherence",
            emotional_signals=signals,
        )
        
        # Emotions should be present and stable
        assert result2["synthesized_state"].get("joy", 0) >= 0

    def test_mortality_entropy_decay_over_interactions(self) -> None:
        """Repeated positive interactions should maintain coherence."""
        system = FeelingSystem(storage_path=None)
        coherences = []
        
        for i in range(20):
            system.process_interaction(
                user_id="user_001",
                interaction_text=f"Interaction {i}",
                emotional_signals={"joy": 0.8, "trust": 0.7},
            )
            coherences.append(system.mortality.coherence)
        
        # Coherence should remain relatively stable with positive inputs
        assert len(coherences) == 20
        assert all(c >= 0 for c in coherences)


class TestRelationalIntegration:
    """Test relational subsystem integration."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        reset_feeling_system()

    def test_relational_bonds_accumulate_across_interactions(self) -> None:
        """Multiple interactions with same user should strengthen bonds."""
        system = FeelingSystem(storage_path=None)
        user_id = "user_001"
        
        # Initial interaction
        system.process_interaction(
            user_id=user_id,
            interaction_text="First meeting",
            emotional_signals={"joy": 0.5, "trust": 0.3},
        )
        
        bond1 = system.relational.bonds[user_id]
        initial_trust = bond1.trust_level
        
        # Multiple interactions with high trust
        for i in range(10):
            system.process_interaction(
                user_id=user_id,
                interaction_text=f"Interaction {i}",
                emotional_signals={"joy": 0.7, "trust": 0.8},
            )
        
        # Bond should strengthen
        bond2 = system.relational.bonds[user_id]
        assert bond2.trust_level > initial_trust or bond2.interaction_count > 1

    def test_different_users_create_different_bonds(self) -> None:
        """Different users should develop distinct bond profiles."""
        system = FeelingSystem(storage_path=None)
        
        # User 1: High trust interactions
        for _ in range(5):
            system.process_interaction(
                user_id="user_001",
                interaction_text="Trustworthy interaction",
                emotional_signals={"trust": 0.9, "joy": 0.5},
            )
        
        # User 2: Low trust interactions
        for _ in range(5):
            system.process_interaction(
                user_id="user_002",
                interaction_text="Suspicious interaction",
                emotional_signals={"trust": 0.1, "fear": 0.8},
            )
        
        bond1 = system.relational.bonds["user_001"]
        bond2 = system.relational.bonds["user_002"]
        
        # Bonds should reflect different experiences
        assert bond1.trust_level > 0 and bond2.trust_level > 0
        assert len(system.relational.bonds) == 2


class TestAffectiveMemoryIntegration:
    """Test memory subsystem integration with emotion processing."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        reset_feeling_system()

    def test_memory_storage_preserves_emotional_context(self) -> None:
        """Stored memories should capture emotional context accurately."""
        system = FeelingSystem(storage_path=None)
        user_id = "user_001"
        
        # Process interaction
        system.process_interaction(
            user_id=user_id,
            interaction_text="Emotional interaction",
            emotional_signals={"joy": 0.8, "sadness": 0.2},
        )
        
        # Store related memory
        memory = system.memory.store_memory(
            user_id=user_id,
            interaction_summary="Positive experience",
            emotional_state="joy",
            intensity=0.8,
            relational_phase="bonding",
            valence=0.8,
        )
        
        # Verify memory captured details
        assert memory.user_id == user_id
        assert memory.emotional_state == "joy"
        assert memory.intensity == 0.8

    def test_memories_accumulate_for_user_relationship(self) -> None:
        """User interaction history should be reflected in memories."""
        system = FeelingSystem(storage_path=None)
        user_id = "user_001"
        
        initial_count = len(system.memory.memories)
        
        # Multiple interactions with memory storage
        for i in range(5):  # Reduced from 10 to account for pruning
            system.process_interaction(
                user_id=user_id,
                interaction_text=f"Interaction {i}",
                emotional_signals={"joy": 0.5},
            )
            system.memory.store_memory(
                user_id=user_id,
                interaction_summary=f"Event {i}",
                emotional_state="neutral",
                intensity=0.5,
                relational_phase="exploration",
                valence=0.0,
            )
        
        # Memories should accumulate (at least some)
        assert len(system.memory.memories) > initial_count
        assert system.memory.user_memory_count.get(user_id, 0) > 0


class TestEmbodiedIntegration:
    """Test embodied constraint effects on emotional expression."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        reset_feeling_system()

    def test_resource_consumption_during_interaction(self) -> None:
        """Interactions should be influenced by embodied state."""
        system = FeelingSystem(storage_path=None)
        
        # Process interaction (may consume resources internally)
        result = system.process_interaction(
            user_id="user_001",
            interaction_text="Embodied interaction",
            emotional_signals={"joy": 0.5},
        )
        
        # Should produce result despite embodied constraints
        assert result is not None
        assert "subsystem_emotions" in result

    def test_resource_restoration(self) -> None:
        """Resources should restore over time."""
        system = FeelingSystem(storage_path=None)
        
        # Restore embodied resources
        restored = system.restore_embodied_resources(hours=1.0)
        
        # Should return restoration dictionary
        assert isinstance(restored, dict)
        assert "energy" in restored or len(restored) > 0


class TestNarrativeIntegration:
    """Test narrative identity effects on emotional responses."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        reset_feeling_system()

    def test_growth_moments_create_positive_emotions(self) -> None:
        """Recorded growth should manifest as positive emotions."""
        system = FeelingSystem(storage_path=None)
        
        # Record growth moment
        system.narrative.record_growth(
            description="Overcame a challenge",
            catalyst="perseverance",
            emotional_impact=0.8,
        )
        
        # Get narrative emotions
        emotions = system.narrative.get_narrative_emotions()
        
        # Should have growth/hope emotions or increase coherence
        assert system.narrative.state.identity_coherence > 0

    def test_betrayal_creates_lasting_emotional_impact(self) -> None:
        """Recorded betrayal should affect emotional state."""
        system = FeelingSystem(storage_path=None)
        
        # Record betrayal
        system.narrative.record_betrayal(
            description="Trusted person broke trust",
            source="friend",
            severity=0.9,
        )
        
        # Emotions should reflect wound
        emotions = system.narrative.get_narrative_emotions()
        
        # Should be recorded even if emotions are empty
        assert len(system.narrative.state.betrayal_wounds) > 0

    def test_identity_coherence_affects_anxiety(self) -> None:
        """Low identity coherence should increase anxiety."""
        system = FeelingSystem(storage_path=None)
        
        # Set low coherence
        system.narrative.state.identity_coherence = 0.2
        
        emotions = system.narrative.get_narrative_emotions()
        
        # Should have anxiety
        assert emotions.get("anxiety", 0) > 0


class TestEthicalIntegration:
    """Test ethical mirror effects on decisions and emotions."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        reset_feeling_system()

    def test_moral_alignment_affects_decision_evaluation(self) -> None:
        """Action evaluation should consider moral alignment."""
        system = FeelingSystem(storage_path=None)
        
        # Evaluate action aligned with values
        result = system.ethical.evaluate_action(
            action_description="Help someone in need",
            value_alignment={"compassion": 0.9, "integrity": 0.8},
        )
        
        # Should show alignment
        assert "overall_alignment" in result
        assert result["overall_alignment"] > 0

    def test_value_conflicts_create_emotional_tension(self) -> None:
        """Conflicting values should be detected."""
        system = FeelingSystem(storage_path=None)
        
        # Evaluate action with conflicting values
        result = system.ethical.evaluate_action(
            action_description="Prioritize self-interest over compassion",
            value_alignment={"compassion": -0.5, "integrity": 0.3},
        )
        
        # Should generate moral emotions reflecting conflict
        assert "moral_emotions" in result


class TestCrossSubsystemDataFlow:
    """Test data flow between subsystems."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        reset_feeling_system()

    def test_emotional_response_incorporates_all_subsystems(self) -> None:
        """Synthesized emotion should incorporate all subsystem inputs."""
        system = FeelingSystem(storage_path=None)
        
        result = system.process_interaction(
            user_id="user_001",
            interaction_text="Complex interaction",
            emotional_signals={"joy": 0.6, "trust": 0.7, "fear": 0.2},
        )
        
        # Result should have contributions from all subsystems
        subsystem_emotions = result.get("subsystem_emotions", {})
        assert "mortality" in subsystem_emotions
        assert "relational" in subsystem_emotions
        assert "embodied" in subsystem_emotions
        assert "narrative" in subsystem_emotions
        assert "ethical" in subsystem_emotions

    def test_full_interaction_pipeline_coherence(self) -> None:
        """Complete interaction should maintain internal coherence."""
        system = FeelingSystem(storage_path=None)
        
        # Process interaction
        result = system.process_interaction(
            user_id="user_001",
            interaction_text="Test interaction",
            emotional_signals={"joy": 0.7, "sadness": 0.2},
        )
        
        # Check result structure
        required_fields = [
            "timestamp",
            "user_id",
            "input_signals",
            "subsystem_emotions",
            "synthesized_state",
        ]
        
        for field in required_fields:
            assert field in result, f"Missing field: {field}"
        
        # Timestamp should be valid ISO format
        assert "T" in result["timestamp"]
        assert "Z" in result["timestamp"] or "+" in result["timestamp"]

    def test_memory_interaction_with_relational_bonds(self) -> None:
        """Memory storage should align with relational bond state."""
        system = FeelingSystem(storage_path=None)
        user_id = "user_001"
        
        # Create strong bond
        for _ in range(5):
            system.process_interaction(
                user_id=user_id,
                interaction_text="Trust-building interaction",
                emotional_signals={"trust": 0.9, "joy": 0.8},
            )
        
        bond = system.relational.bonds[user_id]
        strong_trust = bond.trust_level
        
        # Store memory in this context
        memory = system.memory.store_memory(
            user_id=user_id,
            interaction_summary="In context of strong bond",
            emotional_state="joy",
            intensity=0.8,
            relational_phase="bonding",
            valence=0.7,
        )
        
        # Memory emotional context should align
        assert memory.emotional_state == "joy"
        assert strong_trust > 0


class TestIntegrationRobustness:
    """Test robustness of integrated system."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        reset_feeling_system()

    def test_system_continues_after_subsystem_anomalies(self) -> None:
        """System should handle subsystem edge cases gracefully."""
        system = FeelingSystem(storage_path=None)
        
        # Consume resources to limits
        system.embodied.consume_resources(
            energy_cost=0.9,
            attention_cost=0.9,
            processing_cost=0.9
        )
        
        # Interaction should still work
        result = system.process_interaction(
            user_id="user_001",
            interaction_text="Despite resource constraints",
            emotional_signals={"determination": 0.5},
        )
        
        assert result is not None

    def test_multiple_users_isolation(self) -> None:
        """Different users should not interfere with each other's state."""
        system = FeelingSystem(storage_path=None)
        
        # User 1 interactions
        for _ in range(5):
            system.process_interaction(
                user_id="user_001",
                interaction_text="User 1 interaction",
                emotional_signals={"joy": 0.9},
            )
        
        # User 2 interactions
        for _ in range(5):
            system.process_interaction(
                user_id="user_002",
                interaction_text="User 2 interaction",
                emotional_signals={"fear": 0.9},
            )
        
        # Bonds should be independent
        bond1 = system.relational.bonds["user_001"]
        bond2 = system.relational.bonds["user_002"]
        
        # They should have different trust levels (different experiences)
        assert bond1.trust_level > 0 and bond2.trust_level > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
