#!/usr/bin/env python3
"""
Simple verification script for DraftShift integration (ASCII only - no Unicode).
Tests core components without special characters for Windows compatibility.
"""

import sys
sys.path.insert(0, '.')

print("=" * 60)
print("DraftShift Integration Verification")
print("=" * 60)

# Test 1: Module Imports
print("\n1. Testing module imports...")
try:
    import DraftShift
    print("   [OK] DraftShift package")
except Exception as e:
    print(f"   [FAIL] DraftShift package: {e}")

try:
    import DraftShift.core
    print("   [OK] draftshift.core")
except Exception as e:
    print(f"   [FAIL] draftshift.core: {e}")

try:
    import DraftShift.constants
    print("   [OK] draftshift.constants")
except Exception as e:
    print(f"   [FAIL] draftshift.constants: {e}")

try:
    import DraftShift.enhanced_affect_parser
    print("   [OK] draftshift.enhanced_affect_parser")
except Exception as e:
    print(f"   [FAIL] draftshift.enhanced_affect_parser: {e}")

try:
    import DraftShift.tone_analysis_composer
    print("   [OK] draftshift.tone_analysis_composer")
except Exception as e:
    print(f"   [FAIL] draftshift.tone_analysis_composer: {e}")

try:
    import DraftShift.tone_signal_parser
    print("   [OK] draftshift.tone_signal_parser")
except Exception as e:
    print(f"   [FAIL] draftshift.tone_signal_parser: {e}")

# Test 2: Enhanced Affect Parser
print("\n2. Testing Enhanced Affect Parser...")
try:
    from DraftShift.enhanced_affect_parser import create_enhanced_affect_parser
    parser = create_enhanced_affect_parser()
    analysis = parser.analyze_affect("This is wonderful!")
    print(f"   [OK] Parser instantiated")
    print(f"   [OK] Analysis: emotion={analysis.primary_emotion}, valence={analysis.valence:.2f}")
except Exception as e:
    print(f"   [FAIL] Error: {e}")

# Test 3: Tone Analysis Composer
print("\n3. Testing Tone Analysis Composer...")
try:
    from DraftShift.tone_analysis_composer import create_tone_analysis_composer
    composer = create_tone_analysis_composer()
    analysis = composer.analyze_tone("This agreement is hereby binding.")
    print(f"   [OK] Composer instantiated")
    print(f"   [OK] Tone analysis: {analysis.get('overall_assessment', 'analyzed')}")
except Exception as e:
    print(f"   [FAIL] Error: {e}")

# Test 4: Tone Signal Parser
print("\n4. Testing Tone Signal Parser...")
try:
    from DraftShift.tone_signal_parser import create_tone_signal_parser
    parser = create_tone_signal_parser()
    analysis = parser.analyze_text("I understand your concerns and will help resolve this.")
    print(f"   [OK] Signal parser instantiated")
    print(f"   [OK] Primary signal: {analysis.primary_signal_name}")
    print(f"   [OK] Tone profile: {analysis.tone_profile}")
except Exception as e:
    print(f"   [FAIL] Error: {e}")

# Test 5: Enhanced detect_tone()
print("\n5. Testing Enhanced detect_tone()...")
try:
    from DraftShift import core
    analysis = core.detect_tone("This is very formal and professional language.")
    print(f"   [OK] detect_tone result: {analysis}")
except Exception as e:
    print(f"   [FAIL] Error: {e}")

# Test 6: Tool Status
print("\n6. Testing Tool Status...")
try:
    from DraftShift import get_tool_status
    status = get_tool_status()
    if isinstance(status, dict):
        print(f"   [OK] Tool status retrieved: {len(status)} keys")
        for tool, available in status.items():
            print(f"       - {tool}: {available}")
except Exception as e:
    print(f"   [FAIL] Error: {e}")

print("\n" + "=" * 60)
print("Verification Complete!")
print("=" * 60)
print("\nStatus: Basic components verified.")
print("Documentation: See draftshift/Docs/ folder for guides if present.")
