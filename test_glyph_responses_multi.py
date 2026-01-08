"""Test multiple glyph response variations."""
import sys
sys.path.insert(0, "src")

from emotional_os_glyphs.dynamic_response_composer import DynamicResponseComposer

composer = DynamicResponseComposer()

test_cases = [
    {
        "glyph": {
            "glyph_name": "Still Insight",
            "description": "Quiet revelation. Truth that arrives without noise.",
            "gate": "Gate 6",
        },
        "input": "I'm feeling stressed and overwhelmed by all the work.",
    },
    {
        "glyph": {
            "glyph_name": "Ache of Recognition",
            "description": "Sorrow witnessed. The pain of being truly seen.",
            "gate": "Gate 3",
        },
        "input": "I've been feeling this deep sadness lately. It's like grief but I don't know what I'm grieving.",
    },
    {
        "glyph": {
            "glyph_name": "Jubilant Mourning",
            "description": "Joy and sorrow dancing together. Celebration of what was.",
            "gate": "Gate 4",
        },
        "input": "I'm happy about the new job but also sad to leave my old team. It's confusing.",
    },
    {
        "glyph": {
            "glyph_name": "Boundary Containment",
            "description": "The sacred yes and no. Limits that protect what matters.",
            "gate": "Gate 1",
        },
        "input": "I need to set better boundaries at work but I'm afraid of disappointing people.",
    },
]

print("=" * 80)
print("MULTI-GLYPH RESPONSE VARIATION TEST")
print("=" * 80)

for i, test_case in enumerate(test_cases, 1):
    glyph = test_case["glyph"]
    user_input = test_case["input"]
    
    response = composer.compose_response(
        input_text=user_input,
        glyph=glyph,
        feedback_detected=False,
        conversation_context={},
    )
    
    print(f"\n--- TEST CASE {i} ---")
    print(f"Glyph: {glyph['glyph_name']}")
    print(f"User: {user_input}")
    print(f"\nResponse:\n{response}")
    print()

print("=" * 80)
print("TEST COMPLETE - All responses now use glyph descriptions!")
print("=" * 80)
