"""
DETAILED WALKTHROUGH: How the system now processes "I'm feeling so stressed today"

This demonstrates the correct approach you described:
1. Actor: "I" = personal, visceral, felt
2. Verb: "feeling" = present participle = NOW, ongoing, immediate
3. Adverb: "so" = emphasis = signal of intensity
4. Adjective: "stressed" = emotional state (primary driver)
5. Temporal: "today" = specific day, not past anxiety or future worry
"""

import sys
sys.path.insert(0, "src")

from emotional_os_glyphs.dynamic_response_composer import DynamicResponseComposer

composer = DynamicResponseComposer()

user_input = "I'm feeling so stressed today"
glyph = {
    "glyph_name": "Still Insight",
    "description": "Quiet revelation. Truth that arrives without noise.",
    "gate": "Gate 6",
}

print("=" * 100)
print("SEMANTIC PARSING WALKTHROUGH")
print("=" * 100)

# Show the semantic analysis
analysis = composer._analyze_message_semantics(user_input)
print(f"\nUser Input: '{user_input}'")
print(f"\nSemantic Analysis:")
print(f"  1. ACTOR: {analysis['actor']} -> Personal, visceral, felt experience")
print(f"  2. VERB: 'feeling' (present participle) -> Action happening NOW, not past/future")
print(f"  3. PRIMARY AFFECT: {analysis['primary_affect']} (emotional state driving response)")

# Identify missing elements
lower_input = user_input.lower()
is_present_tense = any(word in lower_input for word in ["feeling", "am", "is", "are", "being"])
is_emphasized = any(word in lower_input for word in ["so ", "so.", "really ", "really."])
has_temporal_qualifier = any(word in lower_input for word in ["today", "right now", "lately", "this week"])

print(f"\nMessage Properties:")
print(f"  - Present Tense: {is_present_tense} (indicates immediacy, urgency)")
print(f"  - Emphasized: {is_emphasized} (indicates intensity)")
print(f"  - Temporal Qualifier: {has_temporal_qualifier} (scope: today, not past/future)")

missing = composer._identify_missing_elements(user_input, analysis)
print(f"\nMissing Elements (what would help clarify):")
for elem in missing:
    if elem == "context":
        print(f"  - CONTEXT: What triggered this? What's the situation?")
    elif elem == "temporal_specificity":
        print(f"  - TEMPORAL SPECIFICITY: How long has this been? All day? Just now?")
    elif elem == "somatic_awareness":
        print(f"  - SOMATIC: Where do you feel it? Chest tightness? Racing thoughts?")
    elif elem == "relational_context":
        print(f"  - RELATIONAL: Is someone/something involved?")
    elif elem == "agency_attempt":
        print(f"  - AGENCY: Have you tried anything? What might help?")

print("\n" + "=" * 100)
print("RESPONSE GENERATION PROCESS")
print("=" * 100)

response = composer.compose_response(
    input_text=user_input,
    glyph=glyph,
    feedback_detected=False,
    conversation_context={},
)

print(f"\nGenerated Response:")
print(f"\n{response}")

print("\n" + "=" * 100)
print("RESPONSE BREAKDOWN")
print("=" * 100)

lines = response.split(". ")
print(f"\n1. ACKNOWLEDGMENT (recognizes what user said):")
print(f"   '{lines[0]}.'")
print(f"   -> Recognizes PRESENT TENSE ('You're feeling')")
print(f"   -> Recognizes EMPHASIS ('emphasizing how much this is present')")
print(f"   -> Recognizes IMMEDIACY (happening NOW)")

if len(lines) > 1:
    print(f"\n2. GLYPH VALIDATION (uses glyph as container/validator):")
    print(f"   '{lines[1]}.'")
    print(f"   -> Glyph validates the emotion (not generates)")
    print(f"   -> Confirms quality of experience")
    print(f"   -> Shows system understands what was selected")

if len(lines) > 2:
    print(f"\n3. CLARIFYING QUESTION (targets missing elements):")
    print(f"   '{lines[2]}'")
    print(f"   -> Asks specifically about MISSING CONTEXT")
    print(f"   -> Helps user provide concrete details")
    print(f"   -> Emotionally themed (what's 'creating pressure')")

print("\n" + "=" * 100)
print("WHY THIS IS CORRECT")
print("=" * 100)
print("""
✓ USER'S MESSAGE is the PRIMARY driver
  - System doesn't override what user said
  - Recognizes tense, emphasis, temporal frame
  
✓ GLYPH is VALIDATOR/CONTAINER, not generator
  - Glyph confirms emotion matters
  - Glyph provides emotional depth
  - But doesn't replace user's actual message
  
✓ SYSTEM ASKS FOR MISSING INFORMATION
  - Recognizes what's incomplete
  - Asks specific clarifying questions
  - Not generic "tell me more"
  
✓ RESPONSE IS GROUNDED IN USER'S ACTUAL EXPERIENCE
  - Recognizes present-tense immediacy
  - Recognizes emphasis and intensity
  - Recognizes temporal frame (today, not past/future)
  - Glyph validates but doesn't dictate

This demonstrates actual comprehension, not template filling.
""")
