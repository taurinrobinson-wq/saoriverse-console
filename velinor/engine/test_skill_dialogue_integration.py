"""
Test scenarios demonstrating skill claiming, lying detection, and REMNANTS ripples.

This test shows:
1. Player truthfully claims a skill they have
2. Player lies about a skill (gets caught)
3. Ripple effects through NPC network (Korrin hears about the lie)
4. Dialogue changes in subsequent encounters (NPC is now skeptical)
"""

import sys
sys.path.insert(0, 'd:/saoriverse-console/velinor/engine')

from npc_manager import NPCManager, NPCProfile
from skill_system import (
    SkillManager, SkillClaim, SkillTaskOutcome, PlayerSkill, SkillDomain
)
from dialogue_context import NPCDialogueContext


def initialize_npc_manager() -> NPCManager:
    """Create and populate an NPCManager with marketplace NPCs."""
    npc_manager = NPCManager()
    
    # Create marketplace NPCs with distinct REMNANTS profiles
    marketplace_npcs = {
        "Sera": {"resolve": 0.7, "empathy": 0.8, "memory": 0.6, "nuance": 0.5, 
                "authority": 0.4, "need": 0.5, "trust": 0.7, "skepticism": 0.3},
        "Kaelen": {"resolve": 0.6, "empathy": 0.4, "memory": 0.7, "nuance": 0.6, 
                 "authority": 0.7, "need": 0.4, "trust": 0.5, "skepticism": 0.6},
        "Korrin": {"resolve": 0.8, "empathy": 0.3, "memory": 0.9, "nuance": 0.7, 
                 "authority": 0.8, "need": 0.2, "trust": 0.3, "skepticism": 0.8},
        "Torvren": {"resolve": 0.5, "empathy": 0.6, "memory": 0.5, "nuance": 0.4, 
                  "authority": 0.5, "need": 0.6, "trust": 0.6, "skepticism": 0.5},
    }
    
    for npc_name, traits in marketplace_npcs.items():
        npc_manager.add_npc(NPCProfile(npc_name, traits))
    
    # Set up influence map (who affects whom)
    npc_manager.influence_map = {
        "Sera": {},
        "Kaelen": {"Torvren": -0.1, "Korrin": 0.1},
        "Korrin": {"Kaelen": 0.15, "Torvren": 0.2},
        "Torvren": {"Kaelen": -0.1},
    }
    
    return npc_manager


def test_honest_skill_claim():
    """Scenario 1: Player claims a skill truthfully."""
    print("\n" + "="*70)
    print("TEST 1: Honest Skill Claim + Success")
    print("="*70)
    
    # Setup
    npc_manager = initialize_npc_manager()
    skill_manager = SkillManager()
    
    # Player learns Herbalism
    herbalism = PlayerSkill("Herbalism", SkillDomain.HEALING)
    herbalism.level = 0.6
    skill_manager.add_skill(herbalism)
    
    # Player meets Sera
    sera = npc_manager.npcs["Sera"]
    print(f"\n[Initial State]")
    print(f"  Sera's Trust: {sera.remnants['trust']:.2f}")
    print(f"  Sera's Skepticism: {sera.remnants['skepticism']:.2f}")
    
    # Create dialogue context
    dialogue_ctx = NPCDialogueContext(
        npc_name="Sera",
        npc_traits=sera.remnants,
        player_actual_skills={"Herbalism": 0.6}
    )
    
    print(f"\n[Sera's Opening]")
    print(f"> {dialogue_ctx.generate_opening_dialogue()}")
    print(f"  Dialogue Style: {dialogue_ctx.get_dialogue_style().value}")
    
    # Player claims Herbalism (truthfully)
    claim = SkillClaim(
        player_skill_manager=skill_manager,
        npc_name="Sera",
        skill_claimed="Herbalism",
        is_truthful=True
    )
    
    print(f"\n[Player's Choice]")
    print(f"  'I know Herbalism - I can handle this.'")
    print(f"  Is truthful: {claim.is_truthful}")
    print(f"  Player's actual level: {claim.player_actual_level:.1f}")
    
    # Task outcome: success (execution roll high enough)
    outcome = SkillTaskOutcome(
        skill_claim=claim,
        task_difficulty=0.5,
        execution_roll=0.8
    )
    
    print(f"\n[Task Resolution]")
    print(f"  Difficulty: {outcome.task_difficulty}")
    print(f"  Execution roll: {outcome.execution_roll}")
    print(f"  Result: {'SUCCESS' if outcome.success else 'FAILURE'}")
    print(f"  Lie discovered: {outcome.lie_discovered}")
    
    # Apply REMNANTS effects
    npc_manager.apply_skill_task_outcome(outcome)
    
    sera_after = npc_manager.npcs["Sera"]
    print(f"\n[Sera's REMNANTS After Success]")
    print(f"  Trust: {sera_after.remnants['trust']:.2f} (was {sera.remnants['trust']:.2f})")
    print(f"  Skepticism: {sera_after.remnants['skepticism']:.2f} (was {sera.remnants['skepticism']:.2f})")
    print(f"  Memory: {sera_after.remnants['memory']:.2f}")
    
    print(f"\n[Sera's Reaction]")
    reaction_dialogue = dialogue_ctx.generate_reaction_after_success()
    print(f"> {reaction_dialogue if reaction_dialogue else 'Well done. You proved yourself.'}")
    

def test_lie_and_discovery():
    """Scenario 2: Player lies about skill, fails, lie is discovered."""
    print("\n" + "="*70)
    print("TEST 2: Lie About Skill (Discovered)")
    print("="*70)
    
    # Setup
    npc_manager = initialize_npc_manager()
    skill_manager = SkillManager()
    
    # Player has NO Tracking skill
    # (skill_manager is empty, so Tracking level = 0.0)
    
    # Create dialogue context for Kaelen
    kaelen = npc_manager.npcs["Kaelen"]
    print(f"\n[Initial State]")
    print(f"  Kaelen's Trust: {kaelen.remnants['trust']:.2f}")
    print(f"  Kaelen's Skepticism: {kaelen.remnants['skepticism']:.2f}")
    
    dialogue_ctx = NPCDialogueContext(
        npc_name="Kaelen",
        npc_traits=kaelen.remnants,
        player_actual_skills={}
    )
    
    print(f"\n[Kaelen's Opening]")
    print(f"> {dialogue_ctx.generate_opening_dialogue()}")
    print(f"  Dialogue Style: {dialogue_ctx.get_dialogue_style().value}")
    
    # Player LIES about having Tracking
    claim = SkillClaim(
        player_skill_manager=skill_manager,
        npc_name="Kaelen",
        skill_claimed="Tracking",
        is_truthful=False
    )
    
    print(f"\n[Player's Choice]")
    print(f"  'I can track anything. No problem.'")
    print(f"  Is truthful: {claim.is_truthful}")
    print(f"  Player's actual level: {claim.player_actual_level:.1f}")
    print(f"  Discovery confidence: {claim.discovery_confidence():.2f}")
    
    # Task fails (no skill, difficulty is moderate)
    outcome = SkillTaskOutcome(
        skill_claim=claim,
        task_difficulty=0.5,
        execution_roll=0.1
    )
    
    print(f"\n[Task Resolution]")
    print(f"  Difficulty: {outcome.task_difficulty}")
    print(f"  Execution roll: {outcome.execution_roll}")
    print(f"  Result: {'SUCCESS' if outcome.success else 'FAILURE'}")
    print(f"  Lie discovered: {outcome.lie_discovered}")
    
    # Apply REMNANTS effects AND ripples
    npc_manager.apply_skill_task_outcome(outcome)
    
    kaelen_after = npc_manager.npcs["Kaelen"]
    print(f"\n[Kaelen's REMNANTS (Direct Shift)]")
    print(f"  Trust: {kaelen_after.remnants['trust']:.2f} (was {kaelen.remnants['trust']:.2f})")
    print(f"  Skepticism: {kaelen_after.remnants['skepticism']:.2f} (was {kaelen.remnants['skepticism']:.2f})")
    
    # Check ripple effects through influence_map
    print(f"\n[Ripple Effects to Connected NPCs]")
    for connected_npc_name in ["Torvren", "Korrin"]:
        connected_npc = npc_manager.npcs.get(connected_npc_name)
        if connected_npc:
            print(f"  {connected_npc_name}:")
            print(f"    Skepticism: {connected_npc.remnants['skepticism']:.2f}")
            print(f"    Trust: {connected_npc.remnants['trust']:.2f}")
    
    # Korrin's amplified reaction
    korrin = npc_manager.npcs.get("Korrin")
    if korrin:
        print(f"\n[Korrin's Special Rumor-Spreading]")
        print(f"  Skepticism: {korrin.remnants['skepticism']:.2f}")
        print(f"  Memory: {korrin.remnants['memory']:.2f}")
        print(f"  (Korrin spreads rumors about player's deception)")
    
    print(f"\n[Kaelen's Reaction]")
    print(f"> 'You lied to me. I don't appreciate that. At all.'")
    


def test_dialog_shift_after_broken_trust():
    """Scenario 3: Subsequent encounter after lie was caught - dialogue shifts."""
    print("\n" + "="*70)
    print("TEST 3: Follow-up Encounter After Broken Trust")
    print("="*70)
    
    # Setup same as above but track lie history
    npc_manager = initialize_npc_manager()
    skill_manager = SkillManager()
    
    # First encounter: Player lies to Kaelen, gets caught
    claim = SkillClaim(
        player_skill_manager=skill_manager,
        npc_name="Kaelen",
        skill_claimed="Tracking",
        is_truthful=False
    )
    outcome = SkillTaskOutcome(
        skill_claim=claim,
        task_difficulty=0.5,
        execution_roll=0.1
    )
    npc_manager.apply_skill_task_outcome(outcome)
    
    # Second encounter: Days later, player meets Kaelen again
    print("\n[Days Later: Second Encounter with Kaelen]")
    
    # Player has NOW learned Lockpicking
    lockpicking = PlayerSkill("Lockpicking", SkillDomain.STEALTH)
    lockpicking.level = 0.5
    skill_manager.add_skill(lockpicking)
    
    kaelen = npc_manager.npcs["Kaelen"]
    
    # Create dialogue context with lie history
    dialogue_ctx = NPCDialogueContext(
        npc_name="Kaelen",
        npc_traits=kaelen.remnants,
        player_actual_skills={"Lockpicking": 0.5},
        player_previous_lies_caught=True  # Track that a lie was caught
    )
    
    print(f"\n[Kaelen's Opening (now skeptical)]")
    print(f"> {dialogue_ctx.generate_opening_dialogue()}")
    print(f"  Dialogue Style: {dialogue_ctx.get_dialogue_style().value}")
    
    print(f"\n[Kaelen's Current REMNANTS]")
    print(f"  Trust: {kaelen.remnants['trust']:.2f}")
    print(f"  Skepticism: {kaelen.remnants['skepticism']:.2f}")
    
    # Player attempts redemption path
    print(f"\n[Player Chooses Redemption]")
    print(f"  'Last time I wasn't ready. But I've learned Lockpicking.'")
    
    claim = SkillClaim(
        player_skill_manager=skill_manager,
        npc_name="Kaelen",
        skill_claimed="Lockpicking",
        is_truthful=True
    )
    
    # This time success
    outcome = SkillTaskOutcome(
        skill_claim=claim,
        task_difficulty=0.4,
        execution_roll=0.7
    )
    
    print(f"\n[Task Resolution]")
    print(f"  Result: {'SUCCESS' if outcome.success else 'FAILURE'}")
    print(f"  Lie discovered: {outcome.lie_discovered}")
    
    npc_manager.apply_skill_task_outcome(outcome)
    
    kaelen_after = npc_manager.npcs["Kaelen"]
    print(f"\n[Kaelen's REMNANTS (partial recovery)]")
    print(f"  Trust: {kaelen_after.remnants['trust']:.2f}")
    print(f"  Skepticism: {kaelen_after.remnants['skepticism']:.2f}")
    print(f"  (Still guarded, but warming)")
    
    print(f"\n[Kaelen's Reaction]")
    print(f"> 'All right. You kept your word this time. That counts for something.'")


def test_korrin_rumor_spreading():
    """Scenario 4: Korrin's special lie-spreading mechanic."""
    print("\n" + "="*70)
    print("TEST 4: Korrin's Rumor-Spreading Network")
    print("="*70)
    
    npc_manager = initialize_npc_manager()
    
    # Player lies to Torvren, gets caught
    claim = SkillClaim(
        player_skill_manager=SkillManager(),
        npc_name="Torvren",
        skill_claimed="Tracking",
        is_truthful=False
    )
    outcome = SkillTaskOutcome(
        skill_claim=claim,
        task_difficulty=0.5,
        execution_roll=0.15
    )
    
    print(f"\n[Initial Lie]")
    print(f"  Player lies to Torvren about Tracking, gets caught")
    
    npc_manager.apply_skill_task_outcome(outcome)
    
    print(f"\n[Korrin's Involvement (Rumor-Monger)]")
    korrin = npc_manager.npcs.get("Korrin")
    if korrin:
        print(f"  Korrin's Skepticism: {korrin.remnants['skepticism']:.2f}")
        print(f"  Korrin's Memory: {korrin.remnants['memory']:.2f}")
        print(f"  (Korrin is now alert to player's deception)")
    
    # Check ripple to Kaelen (in Korrin's network)
    kaelen = npc_manager.npcs.get("Kaelen")
    if kaelen:
        print(f"\n[Secondary Ripple: Kaelen (gossip network)]")
        print(f"  Kaelen's Trust: {kaelen.remnants['trust']:.2f}")
        print(f"  Kaelen's Skepticism: {kaelen.remnants['skepticism']:.2f}")
        print(f"  (Kaelen heard the rumor, is now more guarded)")
    
    print(f"\n[Social Consequence]")
    print(f"> Korrin: 'I thought I taught you better than this. Don't get caught.'")
    print(f"> Korrin then tells Kaelen: 'Watch that one. They'll tell you anything.'")


if __name__ == "__main__":
    test_honest_skill_claim()
    test_lie_and_discovery()
    test_dialog_shift_after_broken_trust()
    test_korrin_rumor_spreading()
    
    print("\n" + "="*70)
    print("All tests completed!")
    print("="*70)
