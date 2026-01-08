"""
REMNANTS Simulation Test Suite
================================

Tests different decision sequences and shows how they affect NPC personality evolution.
Demonstrates various playstyles and their consequences.
"""

import json
import sys
from pathlib import Path
from copy import deepcopy

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from velinor.engine.npc_manager import NPCManager, create_marketplace_npcs, create_marketplace_influence_map


def print_header(text):
    """Print a formatted header."""
    print()
    print("=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_npc_state(npc_manager, title):
    """Print current NPC states."""
    print(f"\n{title}")
    print("-" * 70)
    
    for npc_name, npc in npc_manager.npcs.items():
        traits = npc.remnants
        # Get top 3 traits
        sorted_traits = sorted(traits.items(), key=lambda x: x[1], reverse=True)[:3]
        traits_str = ", ".join([f"{t[0]}: {t[1]:.2f}" for t in sorted_traits])
        print(f"  {npc_name:12} | {traits_str}")


def test_aggressive_playstyle():
    """Test: Aggressive/Bold player (high courage, narrative presence)."""
    print_header("TEST 1: AGGRESSIVE PLAYSTYLE")
    print("Player prioritizes: Courage, Narrative Presence")
    
    manager = NPCManager()
    npcs = create_marketplace_npcs()
    manager.add_npcs_batch(npcs)
    influence_map = create_marketplace_influence_map()
    for from_npc, ripples in influence_map.items():
        for to_npc, ripple_value in ripples.items():
            manager.set_influence(from_npc, to_npc, ripple_value)
    
    # Save initial state (use deepcopy to avoid reference sharing)
    initial_state = {name: deepcopy(npc.to_dict()) for name, npc in manager.npcs.items()}
    
    print_npc_state(manager, "INITIAL STATE:")
    
    # Aggressive sequence
    encounters = [
        {"courage": 0.2, "narrative_presence": 0.15},      # Bold choice
        {"courage": 0.15, "narrative_presence": 0.1},      # Assertive choice
        {"courage": 0.2},                                   # Direct action
        {"courage": 0.1, "observation": -0.1},             # Reckless choice
        {"narrative_presence": 0.2},                        # Take spotlight
    ]
    
    manager.simulate_encounters(encounters)
    print_npc_state(manager, f"AFTER {len(encounters)} AGGRESSIVE CHOICES:")
    
    # Show changes
    print("\nCHANGES FROM INITIAL STATE:")
    print("-" * 70)
    for npc_name in manager.npcs.keys():
        initial = initial_state[npc_name]['remnants']
        current = manager.npcs[npc_name].remnants
        
        changes = {}
        for trait in initial.keys():
            delta = current[trait] - initial[trait]
            if abs(delta) > 0.05:  # Only show meaningful changes (> 0.05)
                changes[trait] = delta
        
        if changes:
            change_str = ", ".join([f"{t}: {v:+.2f}" for t, v in sorted(changes.items(), key=lambda x: abs(x[1]), reverse=True)])
            print(f"  {npc_name:12} | {change_str}")
    
    return manager, initial_state


def test_cautious_playstyle():
    """Test: Cautious/Observant player (high wisdom, observation)."""
    print_header("TEST 2: CAUTIOUS PLAYSTYLE")
    print("Player prioritizes: Wisdom, Observation")
    
    manager = NPCManager()
    npcs = create_marketplace_npcs()
    manager.add_npcs_batch(npcs)
    influence_map = create_marketplace_influence_map()
    for from_npc, ripples in influence_map.items():
        for to_npc, ripple_value in ripples.items():
            manager.set_influence(from_npc, to_npc, ripple_value)
    
    # Save initial state (use deepcopy to avoid reference sharing)
    initial_state = {name: deepcopy(npc.to_dict()) for name, npc in manager.npcs.items()}
    
    print_npc_state(manager, "INITIAL STATE:")
    
    # Cautious sequence
    encounters = [
        {"wisdom": 0.2, "observation": 0.15},              # Careful observation
        {"observation": 0.2},                              # Watch everything
        {"wisdom": 0.15, "courage": -0.1},                 # Play it safe
        {"observation": 0.2, "empathy": -0.1},             # Detached analysis
        {"wisdom": 0.2},                                   # Think before acting
    ]
    
    manager.simulate_encounters(encounters)
    print_npc_state(manager, f"AFTER {len(encounters)} CAUTIOUS CHOICES:")
    
    # Show changes
    print("\nCHANGES FROM INITIAL STATE:")
    print("-" * 70)
    for npc_name in manager.npcs.keys():
        initial = initial_state[npc_name]['remnants']
        current = manager.npcs[npc_name].remnants
        
        changes = {}
        for trait in initial.keys():
            delta = current[trait] - initial[trait]
            if abs(delta) > 0.05:
                changes[trait] = delta
        
        if changes:
            change_str = ", ".join([f"{t}: {v:+.2f}" for t, v in sorted(changes.items(), key=lambda x: abs(x[1]), reverse=True)])
            print(f"  {npc_name:12} | {change_str}")
    
    return manager, initial_state


def test_empathetic_playstyle():
    """Test: Empathetic/Compassionate player (high empathy, trust)."""
    print_header("TEST 3: EMPATHETIC PLAYSTYLE")
    print("Player prioritizes: Empathy, Trust")
    
    manager = NPCManager()
    npcs = create_marketplace_npcs()
    manager.add_npcs_batch(npcs)
    influence_map = create_marketplace_influence_map()
    for from_npc, ripples in influence_map.items():
        for to_npc, ripple_value in ripples.items():
            manager.set_influence(from_npc, to_npc, ripple_value)
    
    # Save initial state (use deepcopy to avoid reference sharing)
    initial_state = {name: deepcopy(npc.to_dict()) for name, npc in manager.npcs.items()}
    
    print_npc_state(manager, "INITIAL STATE:")
    
    # Empathetic sequence
    encounters = [
        {"empathy": 0.2},                                   # Show compassion
        {"empathy": 0.15, "trust": 0.1},                   # Trust someone
        {"empathy": 0.2, "narrative_presence": -0.1},      # Support others
        {"trust": 0.2},                                    # Give benefit of doubt
        {"empathy": 0.15, "observation": -0.15},           # Feel, don't analyze
    ]
    
    manager.simulate_encounters(encounters)
    print_npc_state(manager, f"AFTER {len(encounters)} EMPATHETIC CHOICES:")
    
    # Show changes
    print("\nCHANGES FROM INITIAL STATE:")
    print("-" * 70)
    for npc_name in manager.npcs.keys():
        initial = initial_state[npc_name]['remnants']
        current = manager.npcs[npc_name].remnants
        
        changes = {}
        for trait in initial.keys():
            delta = current[trait] - initial[trait]
            if abs(delta) > 0.05:
                changes[trait] = delta
        
        if changes:
            change_str = ", ".join([f"{t}: {v:+.2f}" for t, v in sorted(changes.items(), key=lambda x: abs(x[1]), reverse=True)])
            print(f"  {npc_name:12} | {change_str}")
    
    return manager, initial_state


def test_mixed_playstyle():
    """Test: Mixed strategy (balanced decisions)."""
    print_header("TEST 4: MIXED PLAYSTYLE")
    print("Player uses varied strategy: Bold, Cautious, Empathetic mixed")
    
    manager = NPCManager()
    npcs = create_marketplace_npcs()
    manager.add_npcs_batch(npcs)
    influence_map = create_marketplace_influence_map()
    for from_npc, ripples in influence_map.items():
        for to_npc, ripple_value in ripples.items():
            manager.set_influence(from_npc, to_npc, ripple_value)
    
    # Save initial state (use deepcopy to avoid reference sharing)
    initial_state = {name: deepcopy(npc.to_dict()) for name, npc in manager.npcs.items()}
    
    print_npc_state(manager, "INITIAL STATE:")
    
    # Mixed sequence
    encounters = [
        {"courage": 0.1, "observation": 0.15},             # Bold observation
        {"empathy": 0.15, "wisdom": 0.1},                  # Careful compassion
        {"narrative_presence": 0.1, "empathy": 0.1},       # Lead with heart
        {"observation": 0.15, "trust": -0.1},              # Investigate suspiciously
        {"courage": 0.15, "wisdom": 0.1},                  # Brave but careful
    ]
    
    manager.simulate_encounters(encounters)
    print_npc_state(manager, f"AFTER {len(encounters)} MIXED CHOICES:")
    
    # Show changes
    print("\nCHANGES FROM INITIAL STATE:")
    print("-" * 70)
    for npc_name in manager.npcs.keys():
        initial = initial_state[npc_name]['remnants']
        current = manager.npcs[npc_name].remnants
        
        changes = {}
        for trait in initial.keys():
            delta = current[trait] - initial[trait]
            if abs(delta) > 0.01:
                changes[trait] = delta
        
        if changes:
            change_str = ", ".join([f"{t}: {v:+.2f}" for t, v in sorted(changes.items(), key=lambda x: abs(x[1]), reverse=True)])
            print(f"  {npc_name:12} | {change_str}")
    
    return manager, initial_state


def compare_playstyles():
    """Compare how different NPCs respond to different playstyles."""
    print_header("SUMMARY: MOST AFFECTED NPC BY PLAYSTYLE")
    print("Testing each playstyle independently and measuring NPC changes\n")
    
    playstyles = [
        ("Aggressive", test_aggressive_playstyle),
        ("Cautious", test_cautious_playstyle),
        ("Empathetic", test_empathetic_playstyle),
        ("Mixed", test_mixed_playstyle),
    ]
    
    results = {}
    for style_name, test_func in playstyles:
        manager, initial_state = test_func()
        
        # Calculate most affected NPC
        max_change = 0
        most_affected = None
        for npc_name in manager.npcs.keys():
            initial = initial_state[npc_name]['remnants']
            current = manager.npcs[npc_name].remnants
            
            total_change = sum(abs(current[trait] - initial[trait]) for trait in initial.keys())
            if total_change > max_change:
                max_change = total_change
                most_affected = npc_name
        
        results[style_name] = (most_affected, max_change)
    
    print_header("MOST AFFECTED NPC BY PLAYSTYLE")
    print()
    for style, (npc, change) in results.items():
        if npc:
            print(f"  {style:15} | {npc:10} (total shift: {change:.2f})")
        else:
            print(f"  {style:15} | (all equal)")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  REMNANTS SIMULATION TEST SUITE")
    print("  Testing NPC personality evolution under different playstyles")
    print("=" * 70)
    
    # Run individual tests
    test_aggressive_playstyle()
    test_cautious_playstyle()
    test_empathetic_playstyle()
    test_mixed_playstyle()
    
    print_header("TEST SUITE COMPLETE")
    print("\n[OK] All simulations completed successfully!")
    print("   No permanent changes made to NPC system.")
    print("   All test data is isolated and temporary.")


if __name__ == "__main__":
    main()
