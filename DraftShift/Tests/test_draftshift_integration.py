#!/usr/bin/env python3
"""Quick integration test for DraftShift modules"""

print("=" * 60)
print("DraftShift Enhanced Module Integration Test")
print("=" * 60)

# Test 1: Import DraftShift modules
print("\n1. Testing module imports...")
try:
    import DraftShift
    print("   ✅ DraftShift package")
except Exception as e:
    print(f"   ❌ DraftShift package: {e}")

try:
    from DraftShift import core
    print("   ✅ DraftShift.core")
except Exception as e:
    print(f"   ❌ DraftShift.core: {e}")

try:
    from DraftShift import constants
    print("   ✅ DraftShift.constants")
except Exception as e:
    print(f"   ❌ DraftShift.constants: {e}")

try:
    from DraftShift.enhanced_affect_parser import create_enhanced_affect_parser
    print("   ✅ DraftShift.enhanced_affect_parser")
except Exception as e:
    print(f"   ❌ DraftShift.enhanced_affect_parser: {e}")

try:
    from DraftShift.tone_analysis_composer import create_tone_analysis_composer
    print("   ✅ DraftShift.tone_analysis_composer")
except Exception as e:
    print(f"   ❌ DraftShift.tone_analysis_composer: {e}")

try:
    from DraftShift.tone_signal_parser import create_tone_signal_parser
    print("   ✅ DraftShift.tone_signal_parser")
except Exception as e:
    print(f"   ❌ DraftShift.tone_signal_parser: {e}")

# Test 2: Create affect parser
print("\n2. Testing Enhanced Affect Parser...")
try:
    parser = create_enhanced_affect_parser()
    print("   ✅ Parser instantiated")
    
    result = parser.analyze_affect("I truly appreciate your kind attention to this matter.")
    print(f"   ✅ Analysis: emotion={result.primary_emotion}, valence={result.valence:.2f}")
    print(f"      Confidence: {result.overall_confidence:.2f}, Arousal: {result.arousal:.2f}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Create tone composer
print("\n3. Testing Tone Analysis Composer...")
try:
    composer = create_tone_analysis_composer()
    print("   ✅ Composer instantiated")
    
    # Test analyze_tone
    analysis = composer.analyze_tone("I must insist on compliance with this directive.")
    print(f"   ✅ Tone analysis: {analysis['current_tone']}")
    print(f"      Strengths: {len(analysis['strengths'])} identified")
    print(f"      Issues: {len(analysis['potential_issues'])} identified")
    
    # Test suggest_transformation
    suggestion = composer.suggest_transformation(
        "This shall be binding.", 
        "Very Formal", 
        "Friendly"
    )
    print(f"   ✅ Transformation suggestion: {suggestion.get('difficulty', 'n/a')} difficulty")
    print(f"      Key changes: {len(suggestion.get('key_changes', []))}")
    print(f"      Word replacements: {len(suggestion.get('word_replacements', {}))}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Create signal parser
print("\n4. Testing Tone Signal Parser...")
try:
    signal_parser = create_tone_signal_parser()
    print("   ✅ Signal parser instantiated")
    
    # Test analyze_text
    analysis = signal_parser.analyze_text("I understand your concerns and will help resolve this.")
    print(f"   ✅ Signal analysis: primary={analysis.primary_signal} ({analysis.primary_signal_name})")
    print(f"      Tone profile: {analysis.tone_profile}")
    print(f"      Confidence: {analysis.confidence:.2f}")
    
    # Test detect_signal_markers
    markers = signal_parser.detect_signal_markers("Therefore, we must protect our interests.", "β")
    print(f"   ✅ Detected {len(markers)} boundary protection markers")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 5: Test detect_tone with new enhancements
print("\n5. Testing Enhanced detect_tone()...")
try:
    tone1 = core.detect_tone("Thank you so much for your kind help!")
    print(f"   ✅ Friendly text -> {tone1}")
    
    tone2 = core.detect_tone("I understand your concerns and appreciate your perspective.")
    print(f"   ✅ Empathetic text -> {tone2}")
    
    tone3 = core.detect_tone("Pursuant to the aforementioned agreement.")
    print(f"   ✅ Formal text -> {tone3}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 6: Tool status
print("\n6. Testing Tool Status...")
try:
    status = core.get_tool_status()
    print("   ✅ Tool status retrieved:")
    for tool, info in status.items():
        if isinstance(info, dict) and 'loaded' in info:
            symbol = "✅" if info['loaded'] else "❌"
            print(f"      {symbol} {tool}: {info.get('loaded', False)}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
