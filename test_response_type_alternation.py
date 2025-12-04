"""
Test to verify response type alternation is working correctly.
Shows that turns alternate between question, reflection, affirmation pattern.
"""

import sys
sys.path.insert(0, r'c:\Users\Admin\OneDrive\Desktop\saoriverse-console')

from emotional_os.learning.archetype_response_generator_v2 import ArchetypeResponseGeneratorV2

# Initialize generator
generator = ArchetypeResponseGeneratorV2()

# Sample dialogue from Scenario 2
dialogue = [
    # Turn 1: User describes overwhelm
    {
        "user": "I'm just tired. Everything feels heavy right now — the work, the expectations, even the small things break me.",
        "archetype": "Overwhelm",
        "turn": 1,
    },
    # Turn 2: User adds context
    {
        "user": "And there's this creative thing that keeps calling to me, but I feel guilty even thinking about it because there's so much work.",
        "archetype": "Ambivalence",
        "turn": 2,
    },
    # Turn 3: User deepens
    {
        "user": "That's the tension. The advocacy work matters to me, but lately I don't know why anymore.",
        "archetype": "Existential",
        "turn": 3,
    },
    # Turn 4: User finds relief
    {
        "user": "Last week I had coffee with a friend and for the first time in months, someone just... got it. Held the heaviness with me.",
        "archetype": "Relief",
        "turn": 4,
    },
    # Turn 5: User returns to ambivalence
    {
        "user": "But then I came back and nothing changed. The work is still there. The pull to create is still there.",
        "archetype": "Ambivalence",
        "turn": 5,
    },
    # Turn 6: User contemplates
    {
        "user": "I don't know what I'm asking for. Maybe just to feel like I'm choosing something instead of being trapped.",
        "archetype": "Existential",
        "turn": 6,
    },
]

# Build context as we go through dialogue
prior_context = ""

print("=" * 80)
print("RESPONSE TYPE ALTERNATION TEST")
print("Expected pattern: Question > Reflection > Question > Affirmation > Question > Reflection")
print("=" * 80)
print()

for i, turn in enumerate(dialogue):
    user_input = turn["user"]
    turn_num = turn["turn"]
    archetype = turn["archetype"]
    
    print(f"TURN {turn_num}: {archetype}")
    print(f"User: {user_input[:70]}...")
    print()
    
    # Generate response
    response = generator.generate_archetype_aware_response(user_input, prior_context, None)
    
    # Determine expected response type
    expected_types = ["question", "reflection", "question", "affirmation"]
    expected_idx = (turn_num - 1) % len(expected_types)
    expected_type = expected_types[expected_idx]
    
    # Display response
    print(f"System response:")
    print(response)
    print()
    
    # Analyze closing type
    closing = response.split('\n')[-1] if response else ""
    
    # Heuristic: questions end with ?, reflections are longer statements, affirmations are short acknowledgments
    if closing.endswith("?"):
        actual_type = "question"
        marker = "[OK] QUESTION" if expected_type == "question" else "[FAIL] WRONG TYPE"
    elif (len(closing.split()) <= 6 and 
          any(word in closing.lower() for word in ["makes sense", "hear", "valid", "important", "matter", 
                                                      "care", "precious", "real", "see that", "that's"])):
        # Micro-affirmation: very short with relational language
        actual_type = "affirmation"
        marker = "[OK] AFFIRMATION" if expected_type == "affirmation" else "[FAIL] WRONG TYPE"
    elif any(word in closing.lower() for word in ["that's", "you're", "the", "there's", "so", "it's"]) and not closing.endswith("?"):
        # Reflection: longer statement starting with observation
        actual_type = "reflection"
        marker = "[OK] REFLECTION" if expected_type == "reflection" else "[FAIL] WRONG TYPE"
    else:
        actual_type = "other"
        marker = "[?] UNCLEAR"
    
    print(f"Expected: {expected_type.upper():12} | Actual: {actual_type.upper():12} {marker}")
    print()
    print("-" * 80)
    print()
    
    # Update context for next turn
    prior_context = user_input

print("=" * 80)
print("Test complete!")
print("Verify that:")
print("  1. Alternation pattern is: Question → Reflection → Question → Affirmation (repeats)")
print("  2. Turn 1, 3, 5 have questions")
print("  3. Turn 2 has reflection")
print("  4. Turn 4 has affirmation")
print("  5. Turn 6 has reflection")
print("=" * 80)
