#!/usr/bin/env python3
"""
Stress testing and edge case validation for FeelingSystem.

Tests:
- High-volume interactions (5000+)
- Large user populations (500+ users)
- Memory pressure scenarios (1000+ memories)
- Rapid state transitions
- Boundary conditions
"""

import pytest
import time
from datetime import datetime, timedelta, timezone
from emotional_os.core.feeling_system import FeelingSystem, reset_feeling_system


class TestHighVolumeInteractions:
    """Test FeelingSystem under high interaction volumes."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Reset system before each test."""
        reset_feeling_system()

    def test_1000_interactions_single_user(self) -> None:
        """Process 1000 interactions from a single user."""
        system = FeelingSystem(storage_path=None)
        signals = {"joy": 0.5, "sadness": 0.3, "trust": 0.7}
        
        start_time = time.time()
        for i in range(1000):
            result = system.process_interaction(
                user_id="user_001",
                interaction_text=f"Message {i}: " + "x" * 100,
                emotional_signals=signals,
                context={"batch": i // 100}
            )
            assert result is not None
            assert "timestamp" in result
        
        elapsed = time.time() - start_time
        print(f"1000 single-user interactions: {elapsed:.2f}s ({elapsed/1000*1000:.1f}ms/interaction)")
        assert elapsed < 5.0, f"Should complete in <5s, took {elapsed:.2f}s"

    def test_5000_interactions_distributed_users(self) -> None:
        """Process 5000 interactions across 10 users."""
        system = FeelingSystem(storage_path=None)
        signals = {"joy": 0.6, "sadness": 0.2, "trust": 0.8}
        users = [f"user_{i:03d}" for i in range(10)]
        
        start_time = time.time()
        for i in range(5000):
            user = users[i % len(users)]
            result = system.process_interaction(
                user_id=user,
                interaction_text=f"Interaction {i}",
                emotional_signals=signals,
            )
            assert result is not None
        
        elapsed = time.time() - start_time
        print(f"5000 multi-user interactions: {elapsed:.2f}s ({elapsed/5000*1000:.1f}ms/interaction)")
        assert elapsed < 20.0, f"Should complete in <20s, took {elapsed:.2f}s"

    def test_large_user_population(self) -> None:
        """Process interactions with 500 different users."""
        system = FeelingSystem(storage_path=None)
        signals = {"joy": 0.5, "sadness": 0.2, "trust": 0.6}
        num_users = 500
        
        start_time = time.time()
        for i in range(1000):
            user_id = f"user_{i % num_users:06d}"
            result = system.process_interaction(
                user_id=user_id,
                interaction_text=f"Message to {user_id}",
                emotional_signals=signals,
            )
            assert result is not None
        
        elapsed = time.time() - start_time
        print(f"1000 interactions with 500 users: {elapsed:.2f}s ({elapsed/1000*1000:.1f}ms/interaction)")
        assert len(system.relational.bonds) > 400
        assert elapsed < 15.0


class TestMemoryPressure:
    """Test FeelingSystem under memory pressure conditions."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Reset system before each test."""
        reset_feeling_system()

    def test_1000_memory_limit(self) -> None:
        """Store 1000 memories and trigger pruning."""
        system = FeelingSystem(storage_path=None)
        
        start_time = time.time()
        for i in range(1200):
            system.memory.store_memory(
                user_id=f"user_{i % 20:03d}",
                interaction_summary=f"Memory {i}",
                emotional_state="neutral",
                intensity=0.5,
                relational_phase="exploration",
                valence=0.5
            )
        
        elapsed = time.time() - start_time
        
        # Should be pruned to max_memories
        assert len(system.memory.memories) <= system.memory.config.max_memories
        print(f"Stored 1200 memories (auto-pruned): {len(system.memory.memories)} final, {elapsed:.2f}s")

    def test_rapid_memory_access(self) -> None:
        """Rapidly access and iterate over large memory sets."""
        system = FeelingSystem(storage_path=None)
        
        # Store 500 memories
        for i in range(500):
            system.memory.store_memory(
                user_id=f"user_{i % 20:03d}",
                interaction_summary=f"Memory {i}",
                emotional_state="joy",
                intensity=0.6,
                relational_phase="bonding",
                valence=0.7
            )
        
        # Rapid iteration
        start_time = time.time()
        for _ in range(1000):
            _ = len(system.memory.memories)
            _ = [m for m in system.memory.memories if m.emotional_state == "joy"]
        
        elapsed = time.time() - start_time
        print(f"1000 iterations on 500 memories: {elapsed:.2f}s")
        assert elapsed < 5.0


class TestRapidStateTransitions:
    """Test FeelingSystem under rapid state changes."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Reset system before each test."""
        reset_feeling_system()

    def test_rapid_emotional_state_changes(self) -> None:
        """Rapidly shift emotional signals."""
        system = FeelingSystem(storage_path=None)
        
        emotional_profiles = [
            {"joy": 1.0, "sadness": 0.0, "trust": 0.9},
            {"joy": 0.0, "sadness": 1.0, "trust": 0.1},
            {"joy": 0.5, "sadness": 0.5, "anger": 0.8},
            {"fear": 0.9, "trust": 0.1},
        ]
        
        start_time = time.time()
        for i in range(500):
            signals = emotional_profiles[i % len(emotional_profiles)]
            result = system.process_interaction(
                user_id="user_001",
                interaction_text="Rapid state change",
                emotional_signals=signals,
            )
            assert result is not None
        
        elapsed = time.time() - start_time
        print(f"500 rapid emotional transitions: {elapsed:.2f}s")
        assert elapsed < 10.0

    def test_alternating_user_interactions(self) -> None:
        """Rapidly alternate between different user interactions."""
        system = FeelingSystem(storage_path=None)
        signals = {"joy": 0.5, "trust": 0.6}
        
        start_time = time.time()
        for i in range(1000):
            user = f"user_{(i // 2) % 50:03d}"  # Alternate frequently
            result = system.process_interaction(
                user_id=user,
                interaction_text=f"Message to {user}",
                emotional_signals=signals,
            )
            assert result is not None
        
        elapsed = time.time() - start_time
        print(f"1000 alternating user interactions: {elapsed:.2f}s")
        assert elapsed < 12.0


class TestBoundaryConditions:
    """Test edge cases and boundary conditions."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Reset system before each test."""
        reset_feeling_system()

    def test_zero_intensity_emotions(self) -> None:
        """Process interactions with zero-intensity emotions."""
        system = FeelingSystem(storage_path=None)
        
        for _ in range(100):
            result = system.process_interaction(
                user_id="user_001",
                interaction_text="Zero intensity",
                emotional_signals={"joy": 0.0, "sadness": 0.0},
            )
            assert result is not None

    def test_max_intensity_emotions(self) -> None:
        """Process interactions with maximum-intensity emotions."""
        system = FeelingSystem(storage_path=None)
        
        for _ in range(100):
            result = system.process_interaction(
                user_id="user_001",
                interaction_text="Max intensity",
                emotional_signals={"joy": 1.0, "sadness": 1.0, "anger": 1.0},
            )
            assert result is not None

    def test_extreme_emotion_combinations(self) -> None:
        """Test contradictory and extreme emotion combinations."""
        system = FeelingSystem(storage_path=None)
        
        extreme_signals = [
            {"joy": 1.0, "sadness": 1.0},  # Max joy and sadness
            {"fear": 1.0, "trust": 1.0},   # Max fear and trust
            {"anger": 1.0, "joy": 1.0},    # Angry and happy
        ]
        
        for signals in extreme_signals:
            for _ in range(50):
                result = system.process_interaction(
                    user_id="user_001",
                    interaction_text="Extreme combination",
                    emotional_signals=signals,
                )
                assert result is not None

    def test_very_long_interaction_text(self) -> None:
        """Process interaction with very long text."""
        system = FeelingSystem(storage_path=None)
        
        long_text = "x" * 10000  # 10KB text
        result = system.process_interaction(
            user_id="user_001",
            interaction_text=long_text,
            emotional_signals={"joy": 0.5},
        )
        assert result is not None
        assert "interaction_summary" in result

    def test_many_emotional_signal_dimensions(self) -> None:
        """Process interaction with many emotional dimensions (realistic)."""
        system = FeelingSystem(storage_path=None)
        
        # Use realistic signal distribution: many emotions but lower intensity
        many_signals = {f"emotion_{i}": (0.5 / 20) for i in range(20)}  # 20 emotions at 0.025 each
        result = system.process_interaction(
            user_id="user_001",
            interaction_text="Many dimensions",
            emotional_signals=many_signals,
        )
        assert result is not None

    def test_unicode_and_special_characters(self) -> None:
        """Process interactions with unicode and special characters."""
        system = FeelingSystem(storage_path=None)
        
        unicode_texts = [
            "Hello 世界 🌍",
            "Привет мир",
            "مرحبا بالعالم",
            "😀😔😡😨😍",
            "Special chars: !@#$%^&*()",
            "\n\t\r\0escaped\0chars",
        ]
        
        for text in unicode_texts:
            result = system.process_interaction(
                user_id="user_001",
                interaction_text=text,
                emotional_signals={"joy": 0.5},
            )
            assert result is not None

    def test_rapid_successive_calls_same_user(self) -> None:
        """Call process_interaction 100 times in rapid succession."""
        system = FeelingSystem(storage_path=None)
        signals = {"joy": 0.5, "trust": 0.6}
        
        start_time = time.time()
        for i in range(100):
            result = system.process_interaction(
                user_id="user_001",
                interaction_text=f"Message {i}",
                emotional_signals=signals,
            )
            assert result is not None
        
        elapsed = time.time() - start_time
        print(f"100 rapid same-user interactions: {elapsed:.2f}s ({elapsed/100*1000:.1f}ms/interaction)")
        assert elapsed < 2.0


class TestSystemStability:
    """Test overall system stability under stress."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Reset system before each test."""
        reset_feeling_system()

    def test_combined_stress_scenario(self) -> None:
        """Combined stress test with high volume, many users, and memory pressure."""
        system = FeelingSystem(storage_path=None)
        
        num_users = 100
        num_interactions = 2000
        signals = {"joy": 0.6, "sadness": 0.2, "trust": 0.7}
        
        start_time = time.time()
        for i in range(num_interactions):
            user = f"user_{i % num_users:04d}"
            result = system.process_interaction(
                user_id=user,
                interaction_text=f"Stress test interaction {i}",
                emotional_signals=signals,
            )
            assert result is not None
            
            # Intermittently store memories
            if i % 4 == 0:
                system.memory.store_memory(
                    user_id=user,
                    interaction_summary=f"Summary {i}",
                    emotional_state="neutral",
                    intensity=0.5,
                    relational_phase="exploration",
                    valence=0.5
                )
        
        elapsed = time.time() - start_time
        
        print(f"\nCombined stress test results:")
        print(f"  Interactions: {num_interactions} in {elapsed:.2f}s ({elapsed/num_interactions*1000:.1f}ms each)")
        print(f"  Users: {len(system.relational.bonds)}")
        print(f"  Memories: {len(system.memory.memories)}")
        print(f"  Avg time per interaction: {elapsed/num_interactions*1000:.2f}ms")
        
        assert len(system.relational.bonds) > 90
        assert elapsed < 25.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
