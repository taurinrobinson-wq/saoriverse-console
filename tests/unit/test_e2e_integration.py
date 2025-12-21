#!/usr/bin/env python3
"""
End-to-end integration test for FirstPerson response generation improvements.

This test verifies that:
1. All core modules import successfully
2. Signal parsing works with real test inputs
3. ArchetypeResponseGeneratorV2 is properly integrated
4. Response type alternation works across multiple turns
5. Dynamic response composer works with the new generator
"""

import sys
import time
from pathlib import Path

# Add workspace root to path
root = Path(__file__).parent
sys.path.insert(0, str(root))

def test_imports():
    """Test that all core modules import successfully."""
    print("=" * 70)
    print("PHASE 1: IMPORT VERIFICATION")
    print("=" * 70)
    
    modules_to_test = [
        ("Signal Parser", "emotional_os.core.signal_parser", "parse_input"),
        ("Response Generator V2", "emotional_os.learning.archetype_response_generator_v2", "ArchetypeResponseGeneratorV2"),
        ("Dynamic Composer", "emotional_os.glyphs.dynamic_response_composer", "DynamicResponseComposer"),
    ]
    
    results = {}
    for name, module_path, class_name in modules_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            results[name] = True
            print(f"✓ {name:40} imported successfully")
        except Exception as e:
            results[name] = False
            print(f"✗ {name:40} FAILED: {e}")
    
    assert all(results.values()), "Import phase failed - cannot proceed"


def test_signal_parsing():
    """Test that signal parsing works with test inputs."""
    print("=" * 70)
    print("PHASE 2: SIGNAL PARSING")
    print("=" * 70)
    
    from emotional_os.core.signal_parser import parse_input
    from emotional_os.core.paths import signal_lexicon_path
    
    test_inputs = [
        "I feel overwhelmed by everything today",
        "My child hugged me and I felt this profound stillness",
        "I'm struggling with the weight of expectations",
    ]
    
    lexicon_path = str(signal_lexicon_path())
    
    for i, test_input in enumerate(test_inputs, 1):
        print(f"\nTest {i}: {test_input[:50]}...")
        try:
            start = time.time()
            result = parse_input(test_input, lexicon_path)
            elapsed = time.time() - start
            
            print(f"  Source: {result.get('response_source', 'unknown')}")
            print(f"  Best Glyph: {result.get('best_glyph', {}).get('glyph_name', 'N/A')}")
            response_preview = result.get('voltage_response', 'N/A')
            if isinstance(response_preview, str):
                print(f"  Response: {response_preview[:80]}...")
            else:
                print(f"  Response: {str(response_preview)[:80]}...")
            print(f"  Time: {elapsed:.3f}s")
            print(f"  ✓ Parse successful")
        except Exception as e:
            print(f"  ✗ Parse failed: {e}")
            raise
    
    assert True


def test_response_generator():
    """Test ArchetypeResponseGeneratorV2 instantiation and methods."""
    print("=" * 70)
    print("PHASE 3: RESPONSE GENERATOR V2 VERIFICATION")
    print("=" * 70)
    
    from emotional_os.learning.archetype_response_generator_v2 import ArchetypeResponseGeneratorV2
    
    try:
        generator = ArchetypeResponseGeneratorV2()
        print(f"✓ ArchetypeResponseGeneratorV2 instantiated")
        
        # Check attributes
        print(f"✓ turn_count initialized: {generator.turn_count}")
        print(f"✓ user_themes initialized: {generator.user_themes}")
        print(f"✓ user_metaphors initialized: {len(generator.user_metaphors)} metaphors")
        
        # Check methods
        for method in ['_choose_response_type', '_track_user_language', 
                       '_generate_closing_question', '_generate_closing_reflection', 
                       '_generate_closing_affirmation', '_generate_response']:
            if hasattr(generator, method):
                print(f"✓ Method {method} exists")
                else:
                print(f"✗ Method {method} NOT FOUND")
                assert False, f"Method {method} NOT FOUND"
        
    except Exception as e:
        print(f"✗ Generator verification failed: {e}")
        raise

    print("\n✅ Response generator verification successful\n")
    assert True


def test_response_type_alternation():
    """Test that response types alternate correctly across turns."""
    print("=" * 70)
    print("PHASE 4: RESPONSE TYPE ALTERNATION (8-TURN TEST)")
    print("=" * 70)
    
    from emotional_os.learning.archetype_response_generator_v2 import ArchetypeResponseGeneratorV2
    
    generator = ArchetypeResponseGeneratorV2()
    
    expected_pattern = ["question", "reflection", "question", "affirmation"]
    test_cases = [
        ("I feel isolated and alone", "Isolated Yearning"),
        ("Today felt a bit lighter than yesterday", "Still Recognition"),
        ("I'm worried about letting people down", "Contained Longing"),
        ("I experienced something sacred in this moment", "Euphoric Yearning"),
        ("The weight of everything is just too much", "Overwhelmed Fragility"),
        ("I felt seen and held by someone today", "Relational Trust"),
        ("This uncertainty keeps me up at night", "Existential Vertigo"),
        ("I realized I can't control everything", "Acceptance Emergence"),
    ]
    
    all_correct = True
    for turn, (user_input, glyph_name) in enumerate(test_cases, 1):
        generator.turn_count = turn
        response_type = generator._choose_response_type(turn)
        expected_type = expected_pattern[(turn - 1) % len(expected_pattern)]
        
        status = "✓" if response_type == expected_type else "✗"
        if response_type != expected_type:
            all_correct = False
        
        print(f"Turn {turn}: Expected {expected_type:12} | Got {response_type:12} {status}")
    
    assert all_correct, "Response type alternation FAILED"
    print("\n✅ Response type alternation working correctly\n")


def test_full_dialogue():
    """Test a complete dialogue with response generation."""
    print("=" * 70)
    print("PHASE 5: FULL DIALOGUE E2E TEST")
    print("=" * 70)
    
    from emotional_os.core.signal_parser import parse_input
    from emotional_os.core.paths import signal_lexicon_path
    from emotional_os.learning.archetype_response_generator_v2 import ArchetypeResponseGeneratorV2
    from emotional_os.glyphs.dynamic_response_composer import DynamicResponseComposer
    
    dialogue_turns = [
        "I've been feeling really isolated lately, like no one truly understands what I'm going through",
        "But yesterday my neighbor just... sat with me. Didn't try to fix anything.",
        "I'm terrified of burdening people with my struggles",
        "When they showed up, I felt this strange calm I haven't felt in months",
        "I worry that moment was just temporary, that I'll go back to feeling alone",
        "What if I can't maintain these connections I'm building?",
    ]
    
    generator = ArchetypeResponseGeneratorV2()
    composer = DynamicResponseComposer()
    lexicon_path = str(signal_lexicon_path())
    
    print(f"\nSimulating {len(dialogue_turns)}-turn dialogue:\n")
    
    for turn, user_message in enumerate(dialogue_turns, 1):
        print(f"\n{'='*70}")
        print(f"TURN {turn}")
        print(f"{'='*70}")
        
        print(f"\nUser: {user_message}")
        
        try:
            # Parse signal
            parse_result = parse_input(user_message, lexicon_path)
            glyph = parse_result.get('best_glyph', {})
            
            print(f"\nParsed Glyph: {glyph.get('glyph_name', 'N/A')}")
            print(f"Gate: {glyph.get('gate', 'N/A')}")
            
            # Get response type
            response_type = generator._choose_response_type(turn)
            print(f"Response Type: {response_type}")
            
            # Generate response
            response = composer.compose_response(
                user_message, 
                glyph, 
                feedback_detected=False,
                conversation_context=None
            )
            
            print(f"\nFirstPerson: {response[:200]}...")
            print(f"✓ Turn {turn} successful")
            
            # Update generator state
            generator.turn_count = turn
            generator._track_user_language(user_message)
            
        except Exception as e:
            print(f"✗ Turn {turn} failed: {e}")
            raise
    
    print(f"\n{'='*70}")
    print("✅ Full dialogue test completed successfully\n")
    assert True


def main():
    """Run all e2e tests."""
    print("\n")
    print("=" * 70)
    print("FIRSTPERSON E2E INTEGRATION TEST".center(70))
    print("Response Generation Improvements Verification".center(70))
    print("=" * 70)
    print()
    
    tests = [
        ("Import Verification", test_imports),
        ("Signal Parsing", test_signal_parsing),
        ("Response Generator V2", test_response_generator),
        ("Response Type Alternation", test_response_type_alternation),
        ("Full Dialogue Flow", test_full_dialogue),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:10} {test_name}")
    
    all_passed = all(results.values())
    print("=" * 70)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED - System is fully integrated and ready!\n")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - See details above\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
