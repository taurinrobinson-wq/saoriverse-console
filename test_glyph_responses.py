"""Test the improved response generation with glyph descriptions."""
import sys
sys.path.insert(0, "src")

from emotional_os_glyphs.dynamic_response_composer import DynamicResponseComposer

# Create composer instance
composer = DynamicResponseComposer()

# Test case: User input "I'm feeling stressed today" with "Still Insight" glyph
glyph = {
    "glyph_name": "Still Insight",
    "description": "Quiet revelation. Truth that arrives without noise.",
    "gate": "Gate 6",
}

user_input = "I'm feeling stressed today about all the work piling up. I don't know where to start."

# Generate response using the improved method
response = composer.compose_response(
    input_text=user_input,
    glyph=glyph,
    feedback_detected=False,
    conversation_context={},
)

print("=" * 70)
print("IMPROVED RESPONSE GENERATION TEST")
print("=" * 70)
print(f"\nGlyph: {glyph['glyph_name']}")
print(f"Description: {glyph['description']}")
print(f"\nUser Input: {user_input}")
print(f"\nGenerated Response:\n{response}")
print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
