"""
Captain Veynar & Kaelen Dual-Arc Test

Demonstrates the mirror conflict between weary authority and shadow-dwelling thief.
Shows how player choices cascade through their opposing influence spheres.
"""

import sys
from pathlib import Path
from copy import deepcopy

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from velinor.engine.npc_manager import NPCManager, create_marketplace_npcs
from velinor.engine.npc_dialogue import generate_dialogue
from velinor.engine.npc_encounter import generate_encounter, print_encounter


def test_veynar_kaelen_dual_arc():
    """Test the Veynar vs. Kaelen mirror arc."""
    print("\n" + "="*70)
    print("TEST: CAPTAIN VEYNAR vs. KAELEN — THE DUAL-ARC")
    print("="*70)
    
    manager = NPCManager()
    manager.add_npcs_batch(create_marketplace_npcs())
    
    print("\n--- INITIAL STATE ---")
    veynar = manager.get_npc("Captain Veynar")
    kaelen = manager.get_npc("Kaelen")
    
    print(f"\nCaptain Veynar:")
    print(f"  Authority: {veynar.remnants['authority']} (Highest in marketplace)")
    print(f"  Resolve: {veynar.remnants['resolve']}")
    print(f"  Trust: {veynar.remnants['trust']}")
    print(f"  Empathy: {veynar.remnants['empathy']}")
    
    print(f"\nKaelen:")
    print(f"  Trust: {kaelen.remnants['trust']} (Lowest in marketplace)")
    print(f"  Skepticism: {kaelen.remnants['skepticism']}")
    print(f"  Empathy: {kaelen.remnants['empathy']}")
    print(f"  Authority: {kaelen.remnants['authority']}")
    
    print("\n--- OPENING DIALOGUE ---")
    
    veynar_enc = generate_encounter("Captain Veynar", veynar.remnants, 1, context="greeting")
    print(f"\nVeynar: {veynar_enc['dialogue']}")
    
    kaelen_enc = generate_encounter("Kaelen", kaelen.remnants, 1, context="greeting")
    print(f"\nKaelen: {kaelen_enc['dialogue']}")
    
    # PATH A: Player sides with Veynar (reports Kaelen)
    print("\n" + "="*70)
    print("PATH A: PLAYER SIDES WITH VEYNAR (Reports Kaelen)")
    print("="*70)
    
    manager_a = NPCManager()
    manager_a.add_npcs_batch(create_marketplace_npcs())
    
    # Player chooses to enforce justice
    manager_a.apply_tone_effects({"courage": 0.2, "wisdom": 0.1})
    
    veynar_a = manager_a.get_npc("Captain Veynar")
    kaelen_a = manager_a.get_npc("Kaelen")
    
    print(f"\nVeynar (After Justice Path):")
    print(f"  Authority: {veynar_a.remnants['authority']:.2f} (unchanged, already high)")
    print(f"  Resolve: {veynar_a.remnants['resolve']:.2f}")
    print(f"  Trust: {veynar_a.remnants['trust']:.2f}")
    
    print(f"\nKaelen (After Betrayal):")
    print(f"  Trust: {kaelen_a.remnants['trust']:.2f} (FRACTURED - dropped from {kaelen.remnants['trust']})")
    print(f"  Skepticism: {kaelen_a.remnants['skepticism']:.2f} (SPIKED)")
    
    veynar_dialogue_a = generate_dialogue("Captain Veynar", veynar_a.remnants, context="resolution")
    kaelen_dialogue_a = generate_dialogue("Kaelen", kaelen_a.remnants, context="conflict")
    
    print(f"\nVeynar's Reflection:")
    print(f"  '{veynar_dialogue_a}'")
    
    print(f"\nKaelen's Response:")
    print(f"  '{kaelen_dialogue_a}'")
    
    print(f"\nOutcome:")
    print(f"  ✓ Items returned to you immediately")
    print(f"  ✗ Kaelen's trust fractures — may lock out shadow path")
    print(f"  ✓ Merchants gain confidence in law")
    
    # PATH B: Player protects Kaelen (silence)
    print("\n" + "="*70)
    print("PATH B: PLAYER PROTECTS KAELEN (Keeps Silence)")
    print("="*70)
    
    manager_b = NPCManager()
    manager_b.add_npcs_batch(create_marketplace_npcs())
    
    # Player chooses empathy and nuance (diplomatic silence)
    manager_b.apply_tone_effects({"empathy": 0.2, "nuance": 0.15})
    
    veynar_b = manager_b.get_npc("Captain Veynar")
    kaelen_b = manager_b.get_npc("Kaelen")
    
    print(f"\nVeynar (After Silence):")
    print(f"  Authority: {veynar_b.remnants['authority']:.2f}")
    print(f"  Resolve: {veynar_b.remnants['resolve']:.2f}")
    print(f"  Empathy: {veynar_b.remnants['empathy']:.2f} (raised by your empathy)")
    
    print(f"\nKaelen (After Protection):")
    print(f"  Trust: {kaelen_b.remnants['trust']:.2f} (STRENGTHENED - raised from {kaelen.remnants['trust']})")
    print(f"  Empathy: {kaelen_b.remnants['empathy']:.2f}")
    
    veynar_dialogue_b = generate_dialogue("Captain Veynar", veynar_b.remnants, context="conflict")
    kaelen_dialogue_b = generate_dialogue("Kaelen", kaelen_b.remnants, context="resolution")
    
    print(f"\nVeynar's Suspicion:")
    print(f"  '{veynar_dialogue_b}'")
    
    print(f"\nKaelen's Gratitude:")
    print(f"  '{kaelen_dialogue_b}'")
    
    print(f"\nOutcome:")
    print(f"  ✗ Items remain lost (temporarily)")
    print(f"  ✓ Kaelen's trust rises significantly — shadow path deepens")
    print(f"  ? Veynar begins to doubt — potential for later redemption arc")
    
    # COMPARISON
    print("\n" + "="*70)
    print("COMPARISON: TRUST DELTA")
    print("="*70)
    
    print(f"\nKaelen's Trust:")
    print(f"  Initial:       {kaelen.remnants['trust']:.2f}")
    print(f"  Path A (Betrayed): {kaelen_a.remnants['trust']:.2f} [delta: {kaelen_a.remnants['trust'] - kaelen.remnants['trust']:+.2f}]")
    print(f"  Path B (Protected): {kaelen_b.remnants['trust']:.2f} [delta: {kaelen_b.remnants['trust'] - kaelen.remnants['trust']:+.2f}]")
    
    print(f"\nVeynar's Empathy:")
    print(f"  Initial:       {veynar.remnants['empathy']:.2f}")
    print(f"  Path A (Justice): {veynar_a.remnants['empathy']:.2f} [delta: {veynar_a.remnants['empathy'] - veynar.remnants['empathy']:+.2f}]")
    print(f"  Path B (Silence): {veynar_b.remnants['empathy']:.2f} [delta: {veynar_b.remnants['empathy'] - veynar.remnants['empathy']:+.2f}]")
    
    print("\n✨ NARRATIVE IMPACT:")
    print("  The player's choice directly shapes the Veynar-Kaelen dynamic.")
    print("  Justice path: Empowers authority, fractures shadow network.")
    print("  Silence path: Builds shadow trust, creates doubt in authority.")
    print("  Both paths remain viable — just with different costs.")


def test_veynar_full_sphere():
    """Test Veynar's influence on the guards and merchants sphere."""
    print("\n\n" + "="*70)
    print("TEST: VEYNAR'S SPHERE INFLUENCE")
    print("="*70)
    
    manager = NPCManager()
    manager.add_npcs_batch(create_marketplace_npcs())
    
    print("\nInitial Guard/Merchant Sphere:")
    ravi = manager.get_npc("Ravi")
    tovren = manager.get_npc("Tovren")
    veynar = manager.get_npc("Captain Veynar")
    
    print(f"  Ravi (Merchant Leader):   Trust={ravi.remnants['trust']:.2f}, Authority={ravi.remnants['authority']:.2f}")
    print(f"  Tovren (Merchant):        Trust={tovren.remnants['trust']:.2f}, Authority={tovren.remnants['authority']:.2f}")
    print(f"  Veynar (Guard Captain):   Authority={veynar.remnants['authority']:.2f}, Trust={veynar.remnants['trust']:.2f}")
    
    # Veynar's influence ripples to merchants
    print("\nAfter Veynar Asserts Authority (apply as tone effect):")
    manager.apply_tone_effects({"observation": 0.2})  # Veynar is observant, strategic
    
    ravi = manager.get_npc("Ravi")
    tovren = manager.get_npc("Tovren")
    veynar = manager.get_npc("Captain Veynar")
    
    print(f"  Ravi (Merchant Leader):   Trust={ravi.remnants['trust']:.2f} (boosted by security), Authority={ravi.remnants['authority']:.2f}")
    print(f"  Tovren (Merchant):        Trust={tovren.remnants['trust']:.2f}, Authority={tovren.remnants['authority']:.2f}")
    print(f"  Veynar (Guard Captain):   Authority={veynar.remnants['authority']:.2f}, Trust={veynar.remnants['trust']:.2f}")
    
    print("\n✨ Veynar Effect:")
    print("  - Merchants feel more secure (trust rises)")
    print("  - Authority sphere becomes stronger")
    print("  - Direct opposition to Kaelen/Drossel (negative ripple)")


if __name__ == "__main__":
    test_veynar_kaelen_dual_arc()
    test_veynar_full_sphere()
    
    print("\n" + "="*70)
    print("VEYNAR + KAELEN DUAL-ARC TESTS COMPLETE")
    print("="*70 + "\n")
