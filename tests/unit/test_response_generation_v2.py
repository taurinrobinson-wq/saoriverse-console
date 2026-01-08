#!/usr/bin/env python3
"""
Test: ArchetypeResponseGeneratorV2 - GENERATION VS SELECTION

Verify that responses are:
1. Unique (not identical closing questions)
2. Contextual (specific to user content, not generic)
3. Varied (different structures, phrasing)
4. Coherent (follow principles but feel fresh)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from emotional_os.learning.archetype_response_generator_v2 import ArchetypeResponseGeneratorV2


def print_section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def test_response_uniqueness_and_context():
    """Test that responses are unique and context-specific, not generic repetition."""
    
    print_section("RESPONSE GENERATION TEST - UNIQUENESS & CONTEXT")
    
    generator = ArchetypeResponseGeneratorV2()
    
    # Scenario: 6-turn dialogue (simplified from scenario 2)
    dialogue = [
        {
            "turn": 1,
            "user": "I feel fragile today, like even small things overwhelm me. Work has been relentless lately—this week alone I've felt pummeled by back-to-back client meetings and impossible deadlines.",
            "prior": None,
        },
        {
            "turn": 3,
            "user": "It's not even the hours, honestly. I could handle that. It's that I feel like I'm drowning in something without a clear anchor. I don't know if the work means anything anymore. Like... what's it all for? I used to care about advocacy—helping people navigate complex legal systems—but now I feel like I'm just grinding through.",
            "prior": "I feel fragile today, like even small things overwhelm me. Work has been relentless lately.",
        },
        {
            "turn": 5,
            "user": "That's the thing. I lost sight of why it mattered in the first place. The advocacy part used to feel fulfilling, but now I'm just drowning out everything else. I've had this little creative spark lately—I've been thinking about art, about making things—but I feel guilty for even considering that when I'm supposed to be focused on the work.",
            "prior": "I don't know if the work means anything anymore. Like... what's it all for? I used to care about advocacy.",
        },
    ]
    
    print("\nGenerating responses for 3 turns of dialogue...\n")
    
    responses = []
    for turn_info in dialogue:
        turn = turn_info["turn"]
        user_input = turn_info["user"]
        prior = turn_info["prior"]
        
        print(f"\n--- TURN {turn} ---")
        print(f"User: {user_input[:80]}...")
        
        response = generator.generate_archetype_aware_response(
            user_input=user_input,
            prior_context=prior,
        )
        
        print(f"\nGenerated Response:\n{response}\n")
        responses.append(response)
    
    # ANALYSIS: Check uniqueness
    print_section("UNIQUENESS ANALYSIS")
    
    print("\n✓ Response uniqueness check:")
    print(f"  Total responses: {len(responses)}")
    print(f"  Unique responses: {len(set(responses))}")
    
    if len(set(responses)) == len(responses):
        print("  [OK] All responses are unique (no exact duplicates)")
    else:
        print("  [WARN] Some responses are duplicated")
    
    # Extract closings (final sentences/questions)
    closings = [r.split("?")[-1].split(".")[-1].strip() if "?" in r else r.split(".")[-1].strip() for r in responses]
    print(f"\nClosing questions uniqueness:")
    for i, closing in enumerate(closings):
        print(f"  Turn {dialogue[i]['turn']}: '{closing[:60]}...'")
    
    if len(set(closings)) == len(closings):
        print("\n  [OK] All closing questions are unique")
    else:
        print("\n  [WARN] Some closing questions are repeated")
    
    # ANALYSIS: Check contextuality
    print_section("CONTEXTUALITY ANALYSIS")
    
    print("\nResponse-to-context matching:")
    
    # Turn 1: Should mention fragility, overwhelm, relentlessness
    turn1_mentions = sum(1 for word in ["fragile", "overwhelm", "relentless", "weight", "burden"] 
                         if word in responses[0].lower())
    print(f"\nTurn 1 (Overwhelm): {turn1_mentions} contextual terms mentioned")
    if turn1_mentions >= 2:
        print("  [OK] Response incorporates specific user language")
    else:
        print("  [WARN] Response might be too generic")
    
    # Turn 3: Should mention purpose, meaning, advocacy, work stress
    turn3_mentions = sum(1 for word in ["purpose", "meaning", "advocacy", "work", "stress", "question"] 
                         if word in responses[1].lower())
    print(f"\nTurn 3 (Existential): {turn3_mentions} contextual terms mentioned")
    if turn3_mentions >= 3:
        print("  [OK] Response incorporates specific user content")
    else:
        print("  [WARN] Response might be missing key concepts")
    
    # Turn 5: Should mention creative, art, advocacy, guilt
    turn5_mentions = sum(1 for word in ["creative", "art", "advocacy", "meaningful", "spark"] 
                         if word in responses[2].lower())
    print(f"\nTurn 5 (Creative Alternative): {turn5_mentions} contextual terms mentioned")
    if turn5_mentions >= 2:
        print("  [OK] Response bridges creative and professional themes")
    else:
        print("  [WARN] Response might not address both themes")
    
    # ANALYSIS: Check structure variety
    print_section("STRUCTURE VARIETY ANALYSIS")
    
    print("\nResponse structures (opening patterns):")
    for i, response in enumerate(responses):
        turn = dialogue[i]["turn"]
        # Identify opening structure
        if response.startswith("The "):
            structure = "Opens with 'The' + observation"
        elif response.startswith("What "):
            structure = "Opens with 'What' + question"
        elif response.startswith("When "):
            structure = "Opens with 'When' + circumstance"
        elif response.startswith("You"):
            structure = "Opens with 'You' + direct address"
        else:
            structure = f"Opens with '{response.split()[0]}' + {response.split()[1] if len(response.split()) > 1 else '...'}"
        
        print(f"  Turn {turn}: {structure}")
    
    # Check if structures vary
    opening_words = [r.split()[0] for r in responses if r.split()]
    if len(set(opening_words)) >= 2:
        print("\n  [OK] Responses vary in opening structure")
    else:
        print("\n  [WARN] Responses have similar opening structures")
    
    # ANALYSIS: Check for principle application
    print_section("PRINCIPLE APPLICATION ANALYSIS")
    
    print("\nPrinciples evident in responses:")
    print("\nTurn 1 (Should validate overwhelm + name experience):")
    if any(word in responses[0].lower() for word in ["named", "relentlessness", "burden", "pummeled"]):
        print("  [✓] Validates and names the overwhelm experience specifically")
    else:
        print("  [?] Check if overwhelm is adequately addressed")
    
    print("\nTurn 3 (Should bridge work stress to existential question):")
    if any(word in responses[1].lower() for word in ["underneath", "question", "meaning", "buried"]):
        print("  [✓] Bridges work stress to deeper existential question")
    else:
        print("  [?] Check if bridge is clear")
    
    print("\nTurn 5 (Should hold complexity of advocacy + creativity):")
    if any(word in responses[2].lower() for word in ["both", "multiple", "tension", "alongside", "creative"]):
        print("  [✓] Acknowledges complexity of dual values/interests")
    else:
        print("  [?] Check if complexity is addressed")
    
    print_section("TEST COMPLETE")
    print("\n✓ If all [OK] marks above, response generation is working correctly")
    print("✗ If [WARN] or [?] marks, refinement needed")


if __name__ == "__main__":
    try:
        test_response_uniqueness_and_context()
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
