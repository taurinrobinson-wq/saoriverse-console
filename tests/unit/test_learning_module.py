#!/usr/bin/env python3
"""
Test: Dynamic Learning Module

Demonstrates the three-layer learning architecture:
1. Learn from your dialogue
2. Generate responses using learned principles
3. Record success for continuous refinement
"""

from emotional_os.learning import (
    get_archetype_library,
    get_archetype_response_generator,
    get_conversation_learner,
)


def test_learning_workflow():
    """Test the complete learning workflow."""
    
    print("=" * 80)
    print("DYNAMIC CONVERSATION LEARNING MODULE - TEST")
    print("=" * 80)
    
    # Step 1: Initialize the three components
    library = get_archetype_library()
    generator = get_archetype_response_generator()
    learner = get_conversation_learner()
    
    print("\n[OK] Initialized learning module with three layers:")
    print(f"  - Archetype Library: {len(library.archetypes)} patterns")
    print(f"  - Response Generator: Ready to apply patterns")
    print(f"  - Conversation Learner: Ready to extract new patterns")
    
    # Step 2: Check existing archetype
    print("\n" + "=" * 80)
    print("EXISTING ARCHETYPE: ReliefToGratitude")
    print("=" * 80)
    
    relief_archetype = library.archetypes.get("ReliefToGratitude")
    if relief_archetype:
        print(f"\nEntry Cues: {relief_archetype.entry_cues[:5]}...")
        print(f"Response Principles: {relief_archetype.response_principles[:2]}...")
        print(f"Continuity Bridges: {relief_archetype.continuity_bridges[:2]}...")
        print(f"Tone Guidelines: {relief_archetype.tone_guidelines[:2]}...")
    
    # Step 3: Test response generation with the archetype
    print("\n" + "=" * 80)
    print("TEST 1: Generate response using ReliefToGratitude archetype")
    print("=" * 80)
    
    user_input = "Yesterday was so heavy, but today my child hugged me and I felt like everything melted away for a moment."
    print(f"\nUser: {user_input}")
    
    response = generator.generate_archetype_aware_response(
        user_input=user_input,
        prior_context=None,
        glyph=None,
    )
    
    if response:
        print(f"\nSystem: {response}")
        print(f"[OK] Generated response using ReliefToGratitude principles")
    else:
        print(f"\n[FAILED] No matching archetype found")
    
    # Step 4: Test response generation without prior context
    print("\n" + "=" * 80)
    print("TEST 2: Generate response with emotional arc across turns")
    print("=" * 80)
    
    prior_context = "I've been feeling pretty overwhelmed lately, just too much on my plate."
    current_input = "But this moment with them just makes it all fade away."
    
    print(f"\nPrior context: {prior_context}")
    print(f"Current message: {current_input}")
    
    response = generator.generate_archetype_aware_response(
        user_input=current_input,
        prior_context=prior_context,
        glyph=None,
    )
    
    if response:
        print(f"\nSystem: {response}")
        print(f"[OK] Generated response with continuity bridging")
    
    # Step 5: Test learning from a conversation
    print("\n" + "=" * 80)
    print("TEST 3: Learn new patterns from conversation")
    print("=" * 80)
    
    sample_conversation = [
        {
            "role": "user",
            "content": "Yesterday was so heavy, but today my child hugged me and I felt like everything melted away for a moment."
        },
        {
            "role": "assistant",
            "content": "That sounds like such a wonderful feeling. Sounds like you needed them as much as they need you."
        },
        {
            "role": "user",
            "content": "Maybe even more so. I don't know sometimes I don't feel like I'm doing enough for my kids. Since the divorce, I barely get to see them during the week."
        },
        {
            "role": "assistant",
            "content": "What you're sharing feels like a complex tapestry of emotions. Joy mixed with sorrow. You mentioned a divorce — was that recent?"
        },
        {
            "role": "user",
            "content": "Yeah, just this year. It was big change for everyone, but I feel especially bad for the kids."
        },
        {
            "role": "assistant",
            "content": "Yeah I know what you mean. Sounds like that's all changed since the divorce. How are you holding up in it?"
        },
    ]
    
    print(f"\nAnalyzing {len(sample_conversation)} turns of conversation...")
    
    learned_archetype = learner.learn_from_conversation(
        turns=sample_conversation,
        user_rating=0.9,  # User rated this conversation highly
    )
    
    if learned_archetype:
        print(f"\n[OK] Learned new archetype: {learned_archetype}")
        print(f"  Total archetypes in library: {len(library.archetypes)}")
        
        # Show the learned pattern
        if learned_archetype in library.archetypes:
            archetype = library.archetypes[learned_archetype]
            print(f"\n  Entry Cues: {archetype.entry_cues}")
            print(f"  Response Principles: {archetype.response_principles}")
            print(f"  Continuity Bridges: {archetype.continuity_bridges}")
            print(f"  Tone Guidelines: {archetype.tone_guidelines}")
    else:
        print(f"\n[FAILED] Could not extract pattern from conversation")
    
    # Step 6: Test archetype matching
    print("\n" + "=" * 80)
    print("TEST 4: Archetype matching and scoring")
    print("=" * 80)
    
    test_input = "It's been overwhelming, but my partner gave me a hug and I felt grateful."
    print(f"\nInput: {test_input}")
    
    matches = library.get_all_matches(test_input, threshold=0.2)
    print(f"\nMatching archetypes (sorted by relevance):")
    for archetype, score in matches[:3]:
        print(f"  - {archetype.name}: {score:.2f}")
    
    # Step 7: Show library persistence
    print("\n" + "=" * 80)
    print("TEST 5: Archetype library persistence")
    print("=" * 80)
    
    print(f"\nArchetype library saved to: {library.storage_path}")
    print(f"Total archetypes: {len(library.archetypes)}")
    for name in library.archetypes.keys():
        archetype = library.archetypes[name]
        print(f"  - {name} (success_weight: {archetype.success_weight:.2f}, used: {archetype.usage_count}x)")
    
    print("\n" + "=" * 80)
    print("LEARNING MODULE TEST COMPLETE [OK]")
    print("=" * 80)


if __name__ == "__main__":
    test_learning_workflow()
