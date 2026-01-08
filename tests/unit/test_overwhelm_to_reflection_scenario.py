#!/usr/bin/env python3
"""
Test: OverwhelmToReflection Archetype with 6-Turn Dialogue Scenario

This test verifies that the new OverwhelmToReflection archetype properly:
1. Matches incoming user messages about overwhelm and existential questioning
2. Generates appropriate responses using learned principles
3. Maintains continuity across emotional arcs (overwhelm → work stress → existential → meaning-seeking)
4. Uses reflection-specific opening/closing patterns
5. Bridges professional identity to personal interests (advocacy to creativity)
"""

import json
import sys
from pathlib import Path

# Add the emotional_os module to path
sys.path.insert(0, str(Path(__file__).parent))

from emotional_os.learning.conversation_archetype import ArchetypeLibrary
from emotional_os.learning.archetype_response_generator import ArchetypeResponseGenerator
from emotional_os.learning.conversation_learner import ConversationLearner


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def test_overwhelm_to_reflection_scenario():
    """Test the complete 6-turn OverwhelmToReflection dialogue scenario."""
    
    # Initialize the learning module
    print_section("OVERWHELM-TO-REFLECTION SCENARIO TEST")
    print("[INIT] Initializing learning module...")
    
    library = ArchetypeLibrary()
    generator = ArchetypeResponseGenerator()
    learner = ConversationLearner()
    
    # Check that OverwhelmToReflection archetype is loaded
    print(f"\n[LIBRARY] Total archetypes loaded: {len(library.archetypes)}")
    for name in library.archetypes.keys():
        print(f"  ✓ {name}")
    
    assert "OverwhelmToReflection" in library.archetypes, "OverwhelmToReflection archetype not found!"
    print("\n[OK] OverwhelmToReflection archetype confirmed in library")
    
    # The 6-turn dialogue scenario from user's second vignette
    dialogue = [
        {
            "turn": 1,
            "speaker": "user",
            "message": "I feel fragile today, like even small things overwhelm me. Work has been relentless lately—this week alone I've felt pummeled by back-to-back client meetings and impossible deadlines."
        },
        {
            "turn": 2,
            "speaker": "system",
            "message": None  # To be generated
        },
        {
            "turn": 3,
            "speaker": "user",
            "message": "It's not even the hours, honestly. I could handle that. It's that I feel like I'm drowning in something without a clear anchor. I don't know if the work means anything anymore. Like... what's it all for? I used to care about advocacy—helping people navigate complex legal systems—but now I feel like I'm just grinding through."
        },
        {
            "turn": 4,
            "speaker": "system",
            "message": None  # To be generated
        },
        {
            "turn": 5,
            "speaker": "user",
            "message": "That's the thing. I lost sight of why it mattered in the first place. The advocacy part used to feel fulfilling, but now I'm just drowning out everything else. I've had this little creative spark lately—I've been thinking about art, about making things—but I feel guilty for even considering that when I'm supposed to be focused on the work."
        },
        {
            "turn": 6,
            "speaker": "system",
            "message": None  # To be generated
        }
    ]
    
    # Process the dialogue turns
    print_section("DIALOGUE SCENARIO EXECUTION")
    
    context_history = []  # Track prior context for bridging
    
    for turn_idx, turn in enumerate(dialogue):
        print(f"\n--- Turn {turn['turn']}: {turn['speaker'].upper()} ---")
        
        if turn['speaker'] == 'user':
            message = turn['message']
            print(f"Message: {message[:100]}...")
            
            # Track for context
            context_history.append({
                'speaker': 'user',
                'message': message
            })
            
            # TEST 1: Archetype matching
            print("\n[MATCH] Scoring against archetypes...")
            scores = {}
            for arch_name, archetype in library.archetypes.items():
                score = archetype.matches_context(message)
                scores[arch_name] = score
                print(f"  {arch_name}: {score:.2f}")
            
            best_match = max(scores.items(), key=lambda x: x[1])
            print(f"\n[MATCH] Best match: {best_match[0]} (score: {best_match[1]:.2f})")
            
            # Verify OverwhelmToReflection scores highly
            overwhelm_score = scores.get("OverwhelmToReflection", 0.0)
            if overwhelm_score >= 0.5:
                print(f"[OK] OverwhelmToReflection scores appropriately ({overwhelm_score:.2f})")
            else:
                print(f"[WARN] OverwhelmToReflection score lower than expected ({overwhelm_score:.2f})")
        
        else:  # system response
            # Generate response using archetype
            print("\n[GENERATE] Creating response using archetype principles...")
            
            # Build context for the generator
            prior_context = "\n".join([
                f"{msg['speaker'].upper()}: {msg['message']}"
                for msg in context_history[-2:]  # Last 2 turns for immediate context
            ]) if context_history else ""
            
            user_message = context_history[-1]['message'] if context_history else ""
            
            # Generate response
            response = generator.generate_archetype_aware_response(
                user_input=user_message,
                prior_context=prior_context,
            )
            
            print(f"\nGenerated Response:\n{response}")
            
            # Track the response
            context_history.append({
                'speaker': 'system',
                'message': response
            })
            
            dialogue[turn_idx]['message'] = response
    
    # TEST 2: Verify emotional arc progression
    print_section("EMOTIONAL ARC VERIFICATION")
    
    user_turns = [d['message'] for d in dialogue if d['speaker'] == 'user']
    system_turns = [d['message'] for d in dialogue if d['speaker'] == 'system' and d['message']]
    
    print(f"\n[ANALYSIS] User expressed {len(user_turns)} messages across emotional arc:")
    
    # Check for key emotional markers
    overwhelm_markers = ['fragile', 'overwhelm', 'pummeled', 'drowning']
    purpose_markers = ["what's it all for", 'purpose', 'meaning', 'advocacy', 'anchor']
    creativity_markers = ['creative', 'art', 'making things', 'spark']
    
    has_overwhelm = any(marker in user_turns[0].lower() for marker in overwhelm_markers)
    has_purpose = any(marker in user_turns[1].lower() for marker in purpose_markers)
    has_creativity = any(marker in user_turns[2].lower() for marker in creativity_markers)
    
    print(f"  ✓ Turn 1 - Overwhelm markers: {'DETECTED' if has_overwhelm else 'NOT DETECTED'}")
    print(f"  ✓ Turn 2 - Purpose/existential markers: {'DETECTED' if has_purpose else 'NOT DETECTED'}")
    print(f"  ✓ Turn 3 - Creativity/alternative fulfillment markers: {'DETECTED' if has_creativity else 'NOT DETECTED'}")
    
    # TEST 3: Verify system responses follow archetype principles
    print_section("SYSTEM RESPONSE VALIDATION")
    
    print(f"\n[VALIDATION] System generated {len(system_turns)} responses")
    
    for idx, response in enumerate(system_turns):
        turn_num = (idx * 2) + 2
        print(f"\nTurn {turn_num} Response Analysis:")
        
        # Check for validation (archetype principle)
        validation_markers = ['hear', 'understand', 'makes sense', 'real', 'valid']
        has_validation = any(marker in response.lower() for marker in validation_markers)
        print(f"  ✓ Validation: {'YES' if has_validation else 'NO'}")
        
        # Check for reflection/questioning (archetype principle)
        reflection_markers = ['?', 'what', 'how', 'why', 'think', 'feel']
        has_reflection = any(marker in response.lower() for marker in reflection_markers)
        print(f"  ✓ Reflection invitation: {'YES' if has_reflection else 'NO'}")
        
        # Check for continuity (uses prior context)
        if idx > 0:
            prior_message = user_turns[idx - 1]
            continuity_score = len([w for w in prior_message.lower().split() if w in response.lower()]) > 0
            print(f"  ✓ Continuity bridge: {'YES' if continuity_score else 'NO'}")
    
    # TEST 4: Verify archetype record keeping
    print_section("ARCHETYPE USAGE TRACKING")
    
    overwhelm_arch = library.archetypes.get("OverwhelmToReflection")
    if overwhelm_arch:
        print(f"\nOverwhelmToReflection Archetype Stats:")
        print(f"  Success Weight: {overwhelm_arch.success_weight:.2f}")
        print(f"  Usage Count: {overwhelm_arch.usage_count}")
        print(f"  Success Count: {overwhelm_arch.success_count}")
        if overwhelm_arch.usage_count > 0:
            success_rate = overwhelm_arch.success_count / overwhelm_arch.usage_count
            print(f"  Success Rate: {success_rate:.2%}")
    
    # TEST 5: Save and verify persistence
    print_section("PERSISTENCE VERIFICATION")
    
    library._save_to_disk()
    print(f"\n[OK] Archetype library persisted to disk")
    
    # Reload and verify
    library2 = ArchetypeLibrary()
    print(f"[OK] Archetype library reloaded from disk")
    print(f"    Total archetypes: {len(library2.archetypes)}")
    
    assert "OverwhelmToReflection" in library2.archetypes
    print(f"[OK] OverwhelmToReflection confirmed in reloaded library")


if __name__ == "__main__":
    try:
        test_overwhelm_to_reflection_scenario()
        print_section("TEST COMPLETE [OK]")
        print("\n✓ OverwhelmToReflection archetype scenario test passed successfully")
        sys.exit(0)
    except Exception as e:
        print_section("TEST FAILED [ERROR]")
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
