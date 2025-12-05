"""Test the redesigned response generation - User-driven with glyph validation."""
import sys
sys.path.insert(0, "src")

from emotional_os_glyphs.dynamic_response_composer import DynamicResponseComposer

composer = DynamicResponseComposer()

print("=" * 90)
print("USER-DRIVEN RESPONSE GENERATION (Glyph as Validator)")
print("=" * 90)

test_cases = [
    {
        "input": "I'm feeling so stressed today",
        "description": "Emphasized present-tense stress, TODAY qualifier (not past/future)",
        "glyph": {
            "glyph_name": "Still Insight",
            "description": "Quiet revelation. Truth that arrives without noise.",
            "gate": "Gate 6",
        }
    },
    {
        "input": "I've been feeling anxious lately",
        "description": "Continuous tense (I've been), temporal qualifier (lately)",
        "glyph": {
            "glyph_name": "Boundary Containment",
            "description": "The sacred yes and no. Limits that protect what matters.",
            "gate": "Gate 1",
        }
    },
    {
        "input": "I'm sad",
        "description": "Minimal info - present tense but NO context, temporal specificity, or relational element",
        "glyph": {
            "glyph_name": "Ache of Recognition",
            "description": "Sorrow witnessed. The pain of being truly seen.",
            "gate": "Gate 3",
        }
    },
    {
        "input": "I feel really overwhelmed with all the work and family stuff",
        "description": "Emphasized (really), present tense, WITH context (work, family)",
        "glyph": {
            "glyph_name": "Spiral Containment",
            "description": "The complexity you're in has a structure. Spirals are patterns, not chaos.",
            "gate": "Gate 2",
        }
    },
]

for i, test in enumerate(test_cases, 1):
    print(f"\nTEST {i}: {test['description']}")
    print(f"{'=' * 90}")
    print(f"User: {test['input']}")
    print(f"Glyph: {test['glyph']['glyph_name']}")
    
    response = composer.compose_response(
        input_text=test["input"],
        glyph=test["glyph"],
        feedback_detected=False,
        conversation_context={},
    )
    
    print(f"\nResponse:")
    print(f"{response}")
    
    # Analysis
    print(f"\nAnalysis:")
    print(f"  ✓ Acknowledges user's PRESENT TENSE" if "feeling" in response.lower() or "experiencing" in response.lower() else "  ✗ Missing present-tense acknowledgment")
    print(f"  ✓ Identifies missing elements" if any(word in response.lower() for word in ["what", "where", "who", "when", "how"]) else "  ✗ No clarifying questions")
    print(f"  ✓ Uses glyph to validate" if any(word in response.lower() for word in ["real", "matters", "meaningful"]) else "  ✗ Not validating with glyph")
    print()

print("=" * 90)
print("KEY DIFFERENCES FROM PREVIOUS APPROACH:")
print("=" * 90)
print("""
BEFORE (Wrong):
- Glyph description was PRIMARY driver
- All responses similar regardless of user message content
- Didn't recognize temporal aspects (present vs past tense)
- Didn't recognize emphasis ("so", "really")

AFTER (Correct):
- User's message is PRIMARY driver
- Parse: actor (I), verb (feeling/experiencing), tense (present), modifiers (so/really), temporal (today)
- Acknowledge what user said with precision
- Use glyph as validator/container, not generator
- Ask clarifying questions targeting missing elements
- Each response is unique to user input + emotional state + missing information
""")
