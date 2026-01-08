#!/usr/bin/env python3
"""
Performance profiling for FeelingSystem hot paths.
Identifies bottlenecks in emotion synthesis, memory operations, and subsystem interactions.
"""

import cProfile
import pstats
import io
import sys
import os
from datetime import datetime, timedelta
from emotional_os.core.feeling_system import FeelingSystem, reset_feeling_system

def simulate_interactions(system: FeelingSystem, num_interactions: int = 1000, num_users: int = 10) -> None:
    """Simulate realistic interaction patterns."""
    users = [f"user_{i:03d}" for i in range(num_users)]
    emotional_signals = {
        "joy": 0.7,
        "sadness": 0.2,
        "anger": 0.1,
        "fear": 0.3,
        "trust": 0.8,
        "anticipation": 0.5,
    }
    
    for i in range(num_interactions):
        user = users[i % num_users]
        system.process_interaction(
            user_id=user,
            interaction_text=f"Interaction {i}: This is a test message for user {user}.",
            emotional_signals=emotional_signals,
            context={"interaction_id": i, "timestamp": datetime.now().isoformat()}
        )
        
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{num_interactions} interactions")


def profile_emotion_synthesis(system: FeelingSystem, num_calls: int = 1000) -> None:
    """Profile the emotion synthesis operation."""
    # Call process_interaction which internally uses _synthesize_emotions
    emotional_signals = {
        "joy": 0.7,
        "sadness": 0.2,
        "anger": 0.1,
        "fear": 0.3,
        "trust": 0.8,
        "anticipation": 0.5,
    }
    
    print(f"\nProfiling emotion synthesis ({num_calls} calls via process_interaction)...")
    for i in range(num_calls):
        system.process_interaction(
            user_id="profile_user",
            interaction_text="Test interaction",
            emotional_signals=emotional_signals,
            context={"test": True}
        )


def profile_memory_operations(system: FeelingSystem, num_stores: int = 500) -> None:
    """Profile memory storage and retrieval."""
    print(f"\nProfiling memory operations ({num_stores} stores)...")
    for i in range(num_stores):
        system.memory.store_memory(
            user_id=f"user_{i % 10:03d}",
            interaction_summary=f"Memory test {i}",
            emotional_state="neutral",
            intensity=0.5,
            relational_phase="exploration",
            valence=0.5
        )
        
        if (i + 1) % 100 == 0:
            print(f"  Stored {i + 1}/{num_stores} memories")


def profile_memory_retrieval(system: FeelingSystem, num_retrievals: int = 1000) -> None:
    """Profile memory operations."""
    print(f"\nProfiling memory iteration ({num_retrievals} iterations)...")
    
    for _ in range(num_retrievals):
        # Just iterate over memories
        _ = len(system.memory.memories)


def main() -> None:
    """Run performance profiling suite."""
    # Fresh system for profiling
    reset_feeling_system()
    
    system = FeelingSystem(storage_path=None)
    
    print("=" * 70)
    print("FeelingSystem Performance Profiling")
    print("=" * 70)
    
    # Profile with pstats
    pr = cProfile.Profile()
    
    print("\n[1/4] Profiling emotion synthesis (1000 calls)...")
    pr.enable()
    profile_emotion_synthesis(system, num_calls=1000)
    pr.disable()
    
    print("\n[2/4] Profiling memory storage (500 operations)...")
    pr.enable()
    profile_memory_operations(system, num_stores=500)
    pr.disable()
    
    print("\n[3/4] Profiling memory retrieval (1000 calls)...")
    pr.enable()
    profile_memory_retrieval(system, num_retrievals=1000)
    pr.disable()
    
    print("\n[4/4] Profiling main interaction loop (1000 interactions, 10 users)...")
    pr.enable()
    simulate_interactions(system, num_interactions=1000, num_users=10)
    pr.disable()
    
    # Print statistics
    print("\n" + "=" * 70)
    print("Performance Profile Summary (Top 20 Functions)")
    print("=" * 70)
    
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
    ps.print_stats(20)
    print(s.getvalue())
    
    # Also print by total time
    print("\n" + "=" * 70)
    print("Top 20 by Total Time")
    print("=" * 70)
    
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("tottime")
    ps.print_stats(20)
    print(s.getvalue())
    
    print("\n" + "=" * 70)
    print("Memory Summary")
    print("=" * 70)
    print(f"Total memories: {len(system.memory.memories)}")
    print(f"User count: {len(system.memory.user_memory_count)}")
    print(f"Mortality coherence: {system.mortality.coherence:.3f}")


if __name__ == "__main__":
    main()
