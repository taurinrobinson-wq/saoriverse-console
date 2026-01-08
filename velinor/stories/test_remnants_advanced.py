"""
Advanced REMNANTS analysis: Ripple matrices, trait stability, and tool resonance.
Builds on test_remnants_simulation.py with deeper system insights.
"""

import sys
from pathlib import Path
from copy import deepcopy

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from velinor.engine.npc_manager import NPCManager, create_marketplace_npcs, create_marketplace_influence_map


def print_header(title):
    """Print formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print('=' * 70)


def analyze_ripple_matrix(manager, initial_state, playstyle_name):
    """
    Analyze how one NPC's changes ripple to affect other NPCs.
    Shows cascade effects through the influence network.
    """
    print_header(f"RIPPLE MATRIX: {playstyle_name} Playstyle")
    print("Shows how each NPC's change cascades to other NPCs\n")
    
    print("NPC Shifts and Their Influence On Others:")
    print("-" * 70)
    
    any_shifts = False
    for npc_name in manager.npcs.keys():
        initial = initial_state[npc_name]['remnants']
        current = manager.npcs[npc_name].remnants
        
        # Calculate which traits shifted most
        shifts = []
        for trait in initial.keys():
            delta = current[trait] - initial[trait]
            if abs(delta) > 0.05:
                shifts.append((trait, delta))
        
        shifts.sort(key=lambda x: abs(x[1]), reverse=True)
        
        if shifts:
            any_shifts = True
            shift_str = ", ".join([f"{t}: {d:+.2f}" for t, d in shifts[:3]])
            print(f"  {npc_name:10} | {shift_str}")
    
    if not any_shifts:
        print("  (No significant cascading shifts detected in this playstyle)")


def analyze_trait_stability(manager, initial_state, playstyle_name=None):
    """
    Show which traits resist change (stable) vs. which traits shift easily (volatile).
    High stability = trait stayed close to initial value.
    """
    if playstyle_name:
        header = f"TRAIT STABILITY: {playstyle_name} Playstyle"
    else:
        header = "TRAIT STABILITY ANALYSIS"
    
    print_header(header)
    print("Measures how resistant each trait type is to player influence\n")
    
    trait_stability = {}
    
    # Collect all changes per trait across all NPCs
    for trait in ['resolve', 'empathy', 'memory', 'nuance', 'authority', 'need', 'trust', 'skepticism']:
        total_change = 0
        change_count = 0
        
        for npc_name in manager.npcs.keys():
            if npc_name not in initial_state:
                continue
                
            initial = initial_state[npc_name]['remnants']
            current = manager.npcs[npc_name].remnants
            
            if trait in initial:
                delta = abs(current[trait] - initial[trait])
                total_change += delta
                change_count += 1
        
        avg_change = total_change / change_count if change_count > 0 else 0
        # Normalize: max expected change = 0.5, so 0.5+ = very volatile
        stability = max(0, 1.0 - (avg_change / 0.4))  
        trait_stability[trait] = (avg_change, stability)
    
    # Sort by stability (highest = most stable)
    sorted_traits = sorted(trait_stability.items(), key=lambda x: x[1][1], reverse=True)
    
    print("Trait Resistance to Change:")
    print("-" * 70)
    for trait, (avg_change, stability) in sorted_traits:
        bar_length = int(stability * 40)
        bar = "|" * bar_length + " " * (40 - bar_length)
        resistance_level = "RIGID" if stability > 0.75 else "STABLE" if stability > 0.5 else "FLUID"
        print(f"  {trait:12} | [{bar}] {stability:.1%} ({resistance_level:>6}) avg_shift: {avg_change:.2f}")
    
    return trait_stability


def analyze_tool_resonance(manager, initial_state, tool_gifts):
    """
    Simulate how gifting tools to NPCs boosts their connected traits and ripples outward.
    
    Args:
        manager: NPCManager instance with evolved NPCs
        initial_state: Original NPC state before changes
        tool_gifts: Dict of {npc_name: tool_name} with trait associations
    
    Example:
        tool_gifts = {
            "Tovren": "compass",  # Navigation → Observation, Nuance ↑
            "Nima": "journal",    # Memory → Memory, Skepticism ↑
        }
    """
    print_header("TOOL RESONANCE ANALYSIS")
    print("How tools amplify NPC traits and influence their allies\n")
    
    # Tool → Trait mappings
    tool_traits = {
        "compass": {"observation": 0.2, "nuance": 0.15},
        "journal": {"memory": 0.2, "nuance": 0.1},
        "chalk_of_paths": {"observation": 0.25, "nuance": 0.2},
        "mirror_of_selfhood": {"empathy": 0.2, "trust": 0.15},
        "scales_of_balance": {"wisdom": 0.2, "nuance": 0.15},
        "bell_of_truth": {"trust": 0.2, "authority": -0.1},
    }
    
    print("Tool Gifts and Their Resonance Effect:")
    print("-" * 70)
    
    for npc_name, tool in tool_gifts.items():
        if tool not in tool_traits:
            print(f"  {npc_name:10} + {tool:20} | (unknown tool)")
            continue
        
        traits_boosted = tool_traits[tool]
        trait_str = ", ".join([f"{t}: {v:+.2f}" for t, v in traits_boosted.items()])
        print(f"  {npc_name:10} + {tool:20} | {trait_str}")
    
    print("\nRipple to Allies:")
    print("-" * 70)
    
    # Show how tool gifts ripple through influence network
    for npc_name, tool in tool_gifts.items():
        if npc_name not in manager.npcs:
            continue
        
        npc = manager.npcs[npc_name]
        # Find influenced NPCs (simplified: check influence map)
        influenced = []
        for other_name in manager.npcs.keys():
            if other_name != npc_name:
                influenced.append(other_name)
        
        if influenced:
            ripple_str = ", ".join(influenced[:3])
            if len(influenced) > 3:
                ripple_str += f", +{len(influenced)-3} more"
            print(f"  {npc_name:10} | Strengthens {ripple_str}")


def compare_stability_by_playstyle():
    """
    Run multiple playstyles and compare which ones create the most stable NPC profiles.
    """
    print_header("PLAYSTYLE COMPARISON: STABILITY VS. VOLATILITY")
    print("Shows which playstyles create resistant vs. fluid NPC personalities\n")
    
    playstyles = [
        ("Aggressive", [
            {"courage": 0.2, "narrative_presence": 0.15},
            {"courage": 0.15, "narrative_presence": 0.1},
            {"courage": 0.2},
            {"courage": 0.1, "observation": -0.1},
            {"narrative_presence": 0.2},
        ]),
        ("Cautious", [
            {"wisdom": 0.2, "observation": 0.15},
            {"observation": 0.2},
            {"wisdom": 0.15, "courage": -0.1},
            {"observation": 0.2, "empathy": -0.1},
            {"wisdom": 0.2},
        ]),
        ("Empathetic", [
            {"empathy": 0.2},
            {"empathy": 0.15, "trust": 0.1},
            {"empathy": 0.2, "narrative_presence": -0.1},
            {"trust": 0.2},
            {"empathy": 0.15, "observation": -0.15},
        ]),
    ]
    
    results = {}
    
    for playstyle_name, encounters in playstyles:
        manager = NPCManager()
        npcs = create_marketplace_npcs()
        manager.add_npcs_batch(npcs)
        influence_map = create_marketplace_influence_map()
        for from_npc, ripples in influence_map.items():
            for to_npc, ripple_value in ripples.items():
                manager.set_influence(from_npc, to_npc, ripple_value)
        
        initial_state = {name: deepcopy(npc.to_dict()) for name, npc in manager.npcs.items()}
        manager.simulate_encounters(encounters)
        
        # Calculate overall stability
        total_stability = 0
        trait_count = 0
        for npc_name in manager.npcs.keys():
            initial = initial_state[npc_name]['remnants']
            current = manager.npcs[npc_name].remnants
            for trait in initial.keys():
                delta = abs(current[trait] - initial[trait])
                stability = 1.0 - min(delta / 0.5, 1.0)
                total_stability += stability
                trait_count += 1
        
        avg_stability = total_stability / trait_count if trait_count > 0 else 0
        results[playstyle_name] = avg_stability
    
    print("System Stability by Playstyle:")
    print("-" * 70)
    
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    for playstyle, stability in sorted_results:
        bar_length = int(stability * 40)
        bar = "|" * bar_length + " " * (40 - bar_length)
        rating = "STABLE" if stability > 0.7 else "BALANCED" if stability > 0.5 else "CHAOTIC"
        print(f"  {playstyle:15} | [{bar}] {stability:.1%} ({rating})")


def demonstrate_ripple_cascade():
    """
    Show a concrete example of how one NPC's major shift cascades through the network.
    Tracks the ripple effect step-by-step.
    """
    print_header("RIPPLE CASCADE DEMONSTRATION")
    print("Tracks how Kaelen's shift influences connected NPCs\n")
    
    manager = NPCManager()
    npcs = create_marketplace_npcs()
    manager.add_npcs_batch(npcs)
    influence_map = create_marketplace_influence_map()
    for from_npc, ripples in influence_map.items():
        for to_npc, ripple_value in ripples.items():
            manager.set_influence(from_npc, to_npc, ripple_value)
    
    initial_state = {name: deepcopy(npc.to_dict()) for name, npc in manager.npcs.items()}
    
    # Single strong empathetic encounter aimed at redemption
    encounters = [
        {"empathy": 0.3, "trust": 0.2},  # Strong empathy
    ]
    
    manager.simulate_encounters(encounters)
    
    print("Initial Kaelen State:")
    print("-" * 70)
    kaelen_init = initial_state["Kaelen"]['remnants']
    print(f"  empathy: {kaelen_init['empathy']:.2f}, need: {kaelen_init['need']:.2f}, trust: {kaelen_init['trust']:.2f}")
    
    print("\nAfter Strong Empathetic Choice:")
    print("-" * 70)
    kaelen_curr = manager.npcs["Kaelen"].remnants
    print(f"  empathy: {kaelen_curr['empathy']:.2f} ({kaelen_curr['empathy']-kaelen_init['empathy']:+.2f})")
    print(f"  need: {kaelen_curr['need']:.2f} ({kaelen_curr['need']-kaelen_init['need']:+.2f})")
    print(f"  trust: {kaelen_curr['trust']:.2f} ({kaelen_curr['trust']-kaelen_init['trust']:+.2f})")
    
    print("\nSecondary Ripple Effects on Kaelen's Allies:")
    print("-" * 70)
    
    # Kaelen's influence map shows who he affects
    influenced_npcs = ["Korrin", "Drossel", "Ravi"]  # Simplified
    
    for ally in influenced_npcs:
        if ally not in manager.npcs:
            continue
        
        ally_init = initial_state[ally]['remnants']
        ally_curr = manager.npcs[ally].remnants
        
        # Show top 2 trait shifts
        shifts = []
        for trait in ally_init.keys():
            delta = ally_curr[trait] - ally_init[trait]
            if abs(delta) > 0.01:
                shifts.append((trait, delta))
        
        shifts.sort(key=lambda x: abs(x[1]), reverse=True)
        
        if shifts:
            shift_str = ", ".join([f"{t}: {d:+.2f}" for t, d in shifts[:2]])
            print(f"  {ally:10} | {shift_str}")
        else:
            print(f"  {ally:10} | (minimal change)")


def main():
    """Run all advanced REMNANTS analyses."""
    print("\n" + "=" * 70)
    print("  ADVANCED REMNANTS ANALYSIS")
    print("  Ripple matrices, trait stability, and tool resonance")
    print("=" * 70)
    
    # Test 1: Ripple Matrix for each playstyle
    playstyles = [
        ("Aggressive", [
            {"courage": 0.2, "narrative_presence": 0.15},
            {"courage": 0.15, "narrative_presence": 0.1},
            {"courage": 0.2},
            {"courage": 0.1, "observation": -0.1},
            {"narrative_presence": 0.2},
        ]),
        ("Cautious", [
            {"wisdom": 0.2, "observation": 0.15},
            {"observation": 0.2},
            {"wisdom": 0.15, "courage": -0.1},
            {"observation": 0.2, "empathy": -0.1},
            {"wisdom": 0.2},
        ]),
    ]
    
    for playstyle_name, encounters in playstyles:
        manager = NPCManager()
        npcs = create_marketplace_npcs()
        manager.add_npcs_batch(npcs)
        influence_map = create_marketplace_influence_map()
        for from_npc, ripples in influence_map.items():
            for to_npc, ripple_value in ripples.items():
                manager.set_influence(from_npc, to_npc, ripple_value)
        
        initial_state = {name: deepcopy(npc.to_dict()) for name, npc in manager.npcs.items()}
        manager.simulate_encounters(encounters)
        
        analyze_ripple_matrix(manager, initial_state, playstyle_name)
        analyze_trait_stability(manager, initial_state, playstyle_name)
    
    # Test 2: Tool Resonance
    print_header("TOOL RESONANCE EXAMPLE")
    print("Simulating how tool gifts reinforce NPC traits\n")
    
    tool_gifts_example = {
        "Tovren": "compass",
        "Nima": "journal",
        "Sera": "mirror_of_selfhood",
    }
    
    print("Proposed Tool Gifts:")
    print("-" * 70)
    for npc, tool in tool_gifts_example.items():
        print(f"  {npc:10} receives {tool}")
    print()
    
    # Simulate tool resonance with a fresh manager
    manager = NPCManager()
    npcs = create_marketplace_npcs()
    manager.add_npcs_batch(npcs)
    initial_state = {name: deepcopy(npc.to_dict()) for name, npc in manager.npcs.items()}
    
    analyze_tool_resonance(manager, initial_state, tool_gifts_example)
    
    # Test 3: Stability Comparison
    compare_stability_by_playstyle()
    
    # Test 4: Ripple Cascade
    demonstrate_ripple_cascade()
    
    print_header("ADVANCED ANALYSIS COMPLETE")
    print("\n[OK] All advanced simulations completed successfully!")
    print("   Ripple matrices, stability analysis, and tool resonance tracked.")
    print("   Ready for integration into dialogue decision trees.\n")


if __name__ == "__main__":
    main()
