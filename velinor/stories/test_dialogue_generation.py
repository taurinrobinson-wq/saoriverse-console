"""
Dialogue Generation Demo & Test Suite

Shows auto-generated dialogue + choices for all 9 NPCs across different playstyles.
Demonstrates how REMNANTS values drive emergent dialogue variation.

Run: python test_dialogue_generation.py
"""

import sys
from pathlib import Path
from copy import deepcopy
import random

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from velinor.engine.npc_manager import NPCManager, create_marketplace_npcs
from velinor.engine.npc_dialogue import generate_dialogue, generate_choices
from velinor.engine.npc_encounter import (
    generate_encounter, 
    generate_scene, 
    print_encounter, 
    print_scene
)


def test_dialogue_variety():
    """Show how same NPC produces different dialogue with different REMNANTS."""
    print("\n" + "="*70)
    print("TEST 1: DIALOGUE VARIETY WITH TRAIT CHANGES")
    print("="*70)
    
    manager = NPCManager()
    manager.add_npcs_batch(create_marketplace_npcs())
    
    sera = manager.get_npc("Sera")
    
    # Show Sera's base dialogue
    print(f"\n--- Sera's Base State (High Empathy: {sera.remnants['empathy']}) ---")
    for i in range(3):
        dialogue = generate_dialogue("Sera", sera.remnants, context="neutral")
        print(f"  {i+1}. {dialogue}")
    
    # Reduce Sera's empathy
    sera.adjust_trait("empathy", -0.5)
    print(f"\n--- After Empathy Drops (Low Empathy: {sera.remnants['empathy']}) ---")
    for i in range(3):
        dialogue = generate_dialogue("Sera", sera.remnants, context="neutral")
        print(f"  {i+1}. {dialogue}")


def test_full_encounters():
    """Show complete encounters with intro + dialogue + choices."""
    print("\n" + "="*70)
    print("TEST 2: FULL ENCOUNTERS (Intro + Dialogue + Choices)")
    print("="*70)
    
    manager = NPCManager()
    manager.add_npcs_batch(create_marketplace_npcs())
    
    # Generate encounters for key NPCs
    for npc_name in ["Sera", "Drossel", "Kaelen"]:
        npc = manager.get_npc(npc_name)
        encounter = generate_encounter(
            npc_name, 
            npc.remnants, 
            encounter_id=1,
            context="greeting"
        )
        print_encounter(encounter, full_details=True)


def test_scene_generation():
    """Generate full scene with all NPCs reacting."""
    print("\n" + "="*70)
    print("TEST 3: FULL SCENE (All 9 NPCs React to Player)")
    print("="*70)
    
    manager = NPCManager()
    manager.add_npcs_batch(create_marketplace_npcs())
    
    npcs_dict = {name: npc.remnants for name, npc in manager.npcs.items()}
    scene = generate_scene(npcs_dict, encounter_id=1, context="greeting")
    
    print_scene(scene, summary_only=True)


def test_dialogue_across_playstyles():
    """Show how different playstyles generate different dialogue."""
    print("\n" + "="*70)
    print("TEST 4: DIALOGUE EVOLUTION ACROSS PLAYSTYLES")
    print("="*70)
    
    manager = NPCManager()
    manager.add_npcs_batch(create_marketplace_npcs())
    
    print("\n--- AGGRESSIVE PLAYSTYLE (Courage + Narrative) ---")
    aggressive_tones = [
        {"courage": 0.2, "narrative_presence": 0.15},
        {"courage": 0.2, "narrative_presence": 0.15},
    ]
    
    for tone in aggressive_tones:
        manager.apply_tone_effects(tone)
    
    # Show Ravi and Drossel dialogue
    for npc_name in ["Ravi", "Drossel"]:
        npc = manager.get_npc(npc_name)
        dialogue = generate_dialogue(npc_name, npc.remnants)
        print(f"\n{npc_name}: {dialogue}")
    
    # Reset manager
    manager = NPCManager()
    manager.add_npcs_batch(create_marketplace_npcs())
    
    print("\n--- EMPATHETIC PLAYSTYLE (Empathy + Wisdom) ---")
    empathetic_tones = [
        {"empathy": 0.2, "wisdom": 0.1},
        {"empathy": 0.2, "wisdom": 0.1},
    ]
    
    for tone in empathetic_tones:
        manager.apply_tone_effects(tone)
    
    # Show same NPCs with different dialogue
    for npc_name in ["Ravi", "Drossel"]:
        npc = manager.get_npc(npc_name)
        dialogue = generate_dialogue(npc_name, npc.remnants)
        print(f"\n{npc_name}: {dialogue}")


def test_choices_reflect_npc_state():
    """Show how player choices adapt to NPC state."""
    print("\n" + "="*70)
    print("TEST 5: PLAYER CHOICES REFLECT NPC STATE")
    print("="*70)
    
    manager = NPCManager()
    manager.add_npcs_batch(create_marketplace_npcs())
    
    # Original state
    print("\n--- Kaelen's Base State (Low Trust, Low Empathy) ---")
    kaelen = manager.get_npc("Kaelen")
    choices = generate_choices("Kaelen", kaelen.remnants, num_choices=3)
    for i, choice in enumerate(choices, 1):
        print(f"  {i}. [{choice['trait']}] {choice['text']}")
    
    # After redemption arc (high empathy + trust)
    print("\n--- Kaelen After Redemption (High Trust, High Empathy) ---")
    kaelen.adjust_trait("trust", 0.5)
    kaelen.adjust_trait("empathy", 0.4)
    
    choices = generate_choices("Kaelen", kaelen.remnants, num_choices=3)
    for i, choice in enumerate(choices, 1):
        print(f"  {i}. [{choice['trait']}] {choice['text']}")


def test_encounter_sequence():
    """Show encounter evolution across multiple decision points."""
    print("\n" + "="*70)
    print("TEST 6: ENCOUNTER SEQUENCE (Evolution Across Decisions)")
    print("="*70)
    
    manager = NPCManager()
    manager.add_npcs_batch(create_marketplace_npcs())
    
    print("\n--- DECISION 1: Offer Empathy ---")
    manager.apply_tone_effects({"empathy": 0.15})
    
    sera = manager.get_npc("Sera")
    encounter1 = generate_encounter("Sera", sera.remnants, 1, "greeting")
    print(f"Sera: {encounter1['dialogue']}")
    choices1 = encounter1['choices']
    print("Choices:")
    for choice in choices1:
        print(f"  - [{choice['trait']}] {choice['text']}")
    
    print("\n--- DECISION 2: Continue Empathy + Wisdom ---")
    manager.apply_tone_effects({"empathy": 0.15, "wisdom": 0.1})
    
    sera = manager.get_npc("Sera")
    encounter2 = generate_encounter("Sera", sera.remnants, 2, "resolution")
    print(f"Sera: {encounter2['dialogue']}")
    choices2 = encounter2['choices']
    print("Choices:")
    for choice in choices2:
        print(f"  - [{choice['trait']}] {choice['text']}")


def test_per_npc_lexicon_consistency():
    """Verify each NPC maintains consistent lexicon voice across runs."""
    print("\n" + "="*70)
    print("TEST 7: NPC LEXICON CONSISTENCY")
    print("="*70)
    
    # Sample each NPC multiple times to show consistent lexicon
    test_npcs = ["Sera", "Drossel", "Mariel", "Nima"]
    
    for npc_name in test_npcs:
        print(f"\n--- {npc_name} (5 dialogue samples) ---")
        
        # Create fresh manager each time
        manager = NPCManager()
        manager.add_npcs_batch(create_marketplace_npcs())
        npc = manager.get_npc(npc_name)
        
        # Generate 5 dialogues
        dialogues = [
            generate_dialogue(npc_name, npc.remnants) 
            for _ in range(5)
        ]
        
        # Show dialogues
        for i, dialogue in enumerate(dialogues, 1):
            # Extract just the word used (between "feels" and next punctuation)
            words_in_dialogue = dialogue.split()
            print(f"  {i}. {dialogue}")


def test_context_variations():
    """Show how context changes dialogue tone."""
    print("\n" + "="*70)
    print("TEST 8: CONTEXT-BASED DIALOGUE VARIATIONS")
    print("="*70)
    
    manager = NPCManager()
    manager.add_npcs_batch(create_marketplace_npcs())
    
    ravi = manager.get_npc("Ravi")
    
    contexts = ["greeting", "alliance", "conflict", "resolution"]
    
    print("\n--- Ravi's Dialogue Across Contexts ---")
    for context in contexts:
        dialogue = generate_dialogue("Ravi", ravi.remnants, context)
        print(f"\n[{context.upper()}]")
        print(f"  {dialogue}")


def main():
    """Run all dialogue generation tests."""
    print("\n" + "="*70)
    print("==  AUTO-GENERATED DIALOGUE SYSTEM - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    tests = [
        ("Dialogue Variety", test_dialogue_variety),
        ("Full Encounters", test_full_encounters),
        ("Scene Generation", test_scene_generation),
        ("Playstyle Evolution", test_dialogue_across_playstyles),
        ("Choice Reflection", test_choices_reflect_npc_state),
        ("Encounter Sequence", test_encounter_sequence),
        ("Lexicon Consistency", test_per_npc_lexicon_consistency),
        ("Context Variations", test_context_variations),
    ]
    
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"\n[ERROR in {test_name}]: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("==  TEST SUITE COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
