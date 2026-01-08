"""
Comprehensive test of the signal parsing -> response generation pipeline.
Tests the ENTIRE flow from user input to glyph selection to response generation.
"""
import sys
sys.path.insert(0, "src")

from emotional_os.core.signal_parser import parse_input
from emotional_os.core.paths import get_path_manager

# Get paths
pm = get_path_manager()
lexicon_path = str(pm._resolve_path(
    "emotional_os/lexicon/word_centric_emotional_lexicon_expanded.json",
    "word_centric_emotional_lexicon_expanded.json"
))
db_path = str(pm.glyph_db())

print("=" * 80)
print("END-TO-END PIPELINE TEST: User Input -> Glyph Selection -> Response Generation")
print("=" * 80)

test_inputs = [
    "I'm feeling really stressed today about all the work piling up and I don't know where to start.",
    "I've been feeling this deep sadness lately. It's grief but I don't know what I'm grieving.",
    "I need to set better boundaries but I'm afraid of disappointing people.",
    "I'm happy about the new job but also sad to leave my old team.",
]

for i, user_input in enumerate(test_inputs, 1):
    print(f"\n{'=' * 80}")
    print(f"TEST CASE {i}")
    print(f"{'=' * 80}")
    print(f"\nUser Input: {user_input}\n")
    
    try:
        # Run the full pipeline
        result = parse_input(
            input_text=user_input,
            lexicon_path=lexicon_path,
            db_path=db_path,
            conversation_context={},
        )
        
        # Extract results
        voltage_response = result.get("voltage_response", "[ERROR]")
        best_glyph = result.get("best_glyph", {})
        glyph_name = best_glyph.get("glyph_name", "UNKNOWN") if isinstance(best_glyph, dict) else "UNKNOWN"
        response_source = result.get("response_source", "unknown")
        
        print(f"Selected Glyph: {glyph_name}")
        print(f"Response Source: {response_source}")
        print(f"\nGenerated Response:")
        print(f"{voltage_response}")
        
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'=' * 80}")
print("END-TO-END TEST COMPLETE")
print("Responses should now reference glyph descriptions and user-specific content!")
print("=" * 80)
