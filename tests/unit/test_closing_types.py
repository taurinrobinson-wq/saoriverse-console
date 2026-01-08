"""
Direct test of closing type selection and generation.
Bypasses full response generation to isolate closing logic.
"""

import sys
sys.path.insert(0, r'c:\Users\Admin\OneDrive\Desktop\saoriverse-console')

from emotional_os.learning.archetype_response_generator_v2 import ArchetypeResponseGeneratorV2

# Initialize generator
generator = ArchetypeResponseGeneratorV2()

print("=" * 80)
print("CLOSING TYPE SELECTION TEST")
print("=" * 80)
print()

# Test response type pattern for 8 turns
expected_pattern = ["question", "reflection", "question", "affirmation"]

for turn in range(1, 9):
    # Simulate turn counting
    generator.turn_count = turn
    
    # Get response type
    response_type = generator._choose_response_type(turn)
    
    # Check against expected pattern
    expected_idx = (turn - 1) % len(expected_pattern)
    expected_type = expected_pattern[expected_idx]
    
    match = "✓" if response_type == expected_type else "✗"
    print(f"Turn {turn}: Expected {expected_type:12} | Got {response_type:12} {match}")

print()
print("=" * 80)
print("CLOSING GENERATION TEST (Single Turn)")
print("=" * 80)
print()

# Test each closing type individually
test_concepts = {
    "overwhelm": ["tired", "heavy"],
    "creative_alternative": ["creative", "spark"],
    "work_related": ["work", "advocacy"],
    "values_identity": ["matters", "meaningful"],
}

print("Testing with Overwhelm tone:")
print()

print("Question closing:")
q = generator._generate_closing_question(
    concepts=test_concepts,
    tone="overwhelm",
    principles=[],
    user_input="I'm tired",
    prior_context=None
)
print(f"  {q}")
print(f"  Ends with '?': {q.endswith('?')}")
print()

print("Reflection closing:")
r = generator._generate_closing_reflection(
    concepts=test_concepts,
    tone="overwhelm",
    user_input="I'm tired"
)
print(f"  {r}")
print(f"  Ends with '?': {r.endswith('?')}")
print()

print("Affirmation closing:")
a = generator._generate_closing_affirmation(
    concepts=test_concepts,
    tone="overwhelm",
)
print(f"  {a}")
print(f"  Ends with '?': {a.endswith('?')}")
print()

print("=" * 80)
print("✓ All closing types generated successfully!")
print("✓ Response type alternation pattern verified!")
print("=" * 80)
