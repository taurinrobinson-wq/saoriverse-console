#!/usr/bin/env python3
"""Test Phase 1 modules import and initialization"""
import sys
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 70)
print("Phase 1 Module Integration Test")
print("=" * 70)

# Test 1: Import LLM Transformer
print("\n1. Testing LLM Transformer module...")
try:
    from DraftShift.llm_transformer import get_transformer, LLMTransformer
    print("   ✅ Import successful")
    transformer = get_transformer()
    status = transformer.get_status()
    print(f"   ✅ Transformer initialized: {status}")
    print(f"      - LLM Available: {status['llm_available']}")
    print(f"      - Fallback Mode: {status['fallback_mode']}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Import Civility Scorer
print("\n2. Testing Civility Scorer module...")
try:
    from DraftShift.civility_scorer import get_scorer, CivilityScorer, CivilityLevel
    print("   ✅ Import successful")
    scorer = get_scorer()
    print("   ✅ Scorer initialized")
    # Test scoring
    test_score = scorer.score_sentence(
        "Please advise on the next steps.",
        "neutral",
        {}
    )
    print(f"   ✅ Test score result: {test_score['score']}/100 ({test_score['level'].name})")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Import Risk Alerts
print("\n3. Testing Risk Alerts module...")
try:
    from DraftShift.risk_alerts import get_alert_generator, AlertSeverity
    print("   ✅ Import successful")
    generator = get_alert_generator()
    print("   ✅ Alert generator initialized")
    # Test alerts
    test_alerts = generator.scan_sentence("You obviously failed to understand.", 1)
    print(f"   ✅ Test scan found {len(test_alerts)} alerts")
    for alert in test_alerts:
        print(f"      - [{alert.severity.name}] {alert.message}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Integration test with DraftShift.core
print("\n4. Testing integration with DraftShift.core...")
try:
    from DraftShift.core import split_sentences, detect_tone
    test_text = "This is excellent work. However, you should reconsider."
    sentences = split_sentences(test_text)
    print(f"   ✅ Split into {len(sentences)} sentence(s)")
    
    # Get civility scores for all sentences
    scorer = get_scorer()
    for i, sent in enumerate(sentences):
        tone = detect_tone(sent)
        score_result = scorer.score_sentence(sent, tone)
        print(f"      Sentence {i+1}: tone={tone}, civility_score={score_result['score']}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Phase 1 Integration Test Complete")
print("=" * 70)
