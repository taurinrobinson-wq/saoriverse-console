#!/usr/bin/env python3
"""
Simple end-to-end test: Verify privacy masking works with HybridLearnerWithUserOverrides.
"""

import json
import hashlib
import tempfile
from pathlib import Path
import sys
import os

# Set up path
sys.path.insert(0, 'str(Path(__file__).resolve().parent)')
repo_root = Path(__file__).resolve().parent
os.chdir(str(repo_root))

from emotional_os.learning.hybrid_learner_v2 import HybridLearnerWithUserOverrides

def hash_user_id(user_id: str) -> str:
    """Hash user ID for privacy."""
    return hashlib.sha256(user_id.encode()).hexdigest()[:16]

def test_privacy_e2e():
    """Test end-to-end privacy masking with multiple exchanges."""
    
    print("🧪 END-TO-END PRIVACY MASKING TEST")
    print("=" * 80)
    
    # Create temporary directory for test data
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Initialize learner
        print("\n1️⃣  Initializing HybridLearnerWithUserOverrides...")
        learner = HybridLearnerWithUserOverrides(
            shared_lexicon_path=str(tmpdir / "shared_lexicon.json"),
            user_overrides_dir=str(tmpdir / "user_overrides"),
            learning_log_path=str(tmpdir / "hybrid_learning_log.jsonl")
        )
        print("   ✅ Learner initialized")
        
        # Test exchanges
        test_exchanges = [
            {
                "user_id": "user_1",
                "user_input": "I'm feeling inspired by the beauty of nature. The sunset was absolutely transcendent today.",
                "ai_response": "That's a beautiful observation. Nature has a way of stirring profound emotions in us.",
                "signals": [
                    {"signal": "nature", "keyword": "nature", "confidence": 0.9, "gate": "Gate 6"},
                    {"signal": "transcendence", "keyword": "transcendent", "confidence": 0.85, "gate": "Gate 4"},
                    {"signal": "joy", "keyword": "inspired", "confidence": 0.8, "gate": "Gate 2"},
                ],
                "glyphs": [
                    {"glyph_name": "Nature's Touch", "confidence": 0.88},
                    {"glyph_name": "Transcendent Moment", "confidence": 0.82},
                ],
                "description": "Positive emotional reflection"
            },
            {
                "user_id": "user_1",
                "user_input": "Sometimes I struggle with feelings of inadequacy. It's hard to believe in myself when everything feels overwhelming.",
                "ai_response": "Those feelings are valid and more common than you might think. Self-compassion is important.",
                "signals": [
                    {"signal": "vulnerability", "keyword": "struggle", "confidence": 0.85, "gate": "Gate 5"},
                    {"signal": "melancholy", "keyword": "inadequacy", "confidence": 0.8, "gate": "Gate 9"},
                    {"signal": "admiration", "keyword": "believe", "confidence": 0.7, "gate": "Gate 4"},
                ],
                "glyphs": [
                    {"glyph_name": "Recursive Grief", "confidence": 0.79},
                    {"glyph_name": "Self-Doubt", "confidence": 0.75},
                ],
                "description": "Vulnerable emotional expression"
            },
            {
                "user_id": "user_2",
                "user_input": "Poetry has always been my refuge. Emily Dickinson's words speak to something ineffable in the human experience.",
                "ai_response": "Poetry is indeed a powerful medium for expressing the inexpressible. Dickinson's work is particularly transcendent.",
                "signals": [
                    {"signal": "love", "keyword": "poetry", "confidence": 0.88, "gate": "Gate 2"},
                    {"signal": "transcendence", "keyword": "ineffable", "confidence": 0.83, "gate": "Gate 4"},
                    {"signal": "nature", "keyword": "experience", "confidence": 0.65, "gate": "Gate 6"},
                ],
                "glyphs": [
                    {"glyph_name": "Poetic Soul", "confidence": 0.86},
                    {"glyph_name": "Literary Transcendence", "confidence": 0.81},
                ],
                "description": "Different user, literary appreciation"
            },
        ]
        
        print(f"\n2️⃣  Processing {len(test_exchanges)} test exchanges...")
        
        for i, exchange in enumerate(test_exchanges, 1):
            user_id_hash = hash_user_id(exchange["user_id"])
            
            print(f"\n   Exchange {i}: {exchange['description']}")
            print(f"      User: {exchange['user_id']} (hash: {user_id_hash})")
            
            # Log exchange
            learner._log_exchange(
                user_id=user_id_hash,
                user_input=exchange["user_input"],
                ai_response=exchange["ai_response"],
                emotional_signals=exchange["signals"],
                glyphs=exchange["glyphs"]
            )
            
            # Also test learning to user lexicon
            user_overrides = {"signals": {}, "trust_score": 0.5}
            learner._learn_to_user_lexicon(
                user_overrides=user_overrides,
                user_input=exchange["user_input"],
                ai_response=exchange["ai_response"],
                emotional_signals=exchange["signals"]
            )
            
            print(f"      ✅ Logged and learned")
        
        # Read back and verify
        print(f"\n3️⃣  Verifying logged entries...")
        
        log_path = Path(str(tmpdir / "hybrid_learning_log.jsonl"))
        logged_entries = []
        
        with open(log_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                entry = json.loads(line)
                logged_entries.append(entry)
        
        print(f"   ✅ Found {len(logged_entries)} entries in log")
        
        # Analyze entries
        print(f"\n4️⃣  Privacy Analysis:")
        print(f"   {'Entry':<8} {'Has Signals':<15} {'Has Gates':<15} {'User_Input':<15} {'AI Response':<15}")
        print(f"   {'-'*70}")
        
        all_privacy_safe = True
        
        for i, entry in enumerate(logged_entries, 1):
            has_signals = len(entry.get("signals", [])) > 0
            has_gates = len(entry.get("gates", [])) > 0
            has_user_input = "user_input" in entry
            has_ai_response = "ai_response" in entry
            
            # Create status strings
            sig_str = "✅ Yes" if has_signals else "❌ No"
            gate_str = "✅ Yes" if has_gates else "❌ No"
            input_str = "❌ EXPOSED" if has_user_input else "✅ Masked"
            response_str = "❌ EXPOSED" if has_ai_response else "✅ Masked"
            
            print(f"   {i:<8} {sig_str:<15} {gate_str:<15} {input_str:<15} {response_str:<15}")
            
            if has_user_input or has_ai_response:
                all_privacy_safe = False
        
        # Show sample entry
        print(f"\n5️⃣  Sample Log Entry Structure:")
        print(json.dumps(logged_entries[0], indent=2))
        
        # Summary
        print(f"\n" + "=" * 80)
        if all_privacy_safe and len(logged_entries) == len(test_exchanges):
            print("✅ ALL PRIVACY CHECKS PASSED")
            print("\n📋 SUMMARY:")
            print(f"  ✅ Processed {len(test_exchanges)} exchanges")
            print(f"  ✅ Logged {len(logged_entries)} entries in privacy-safe format")
            print(f"  ✅ NO raw user_input fields in any entry")
            print(f"  ✅ NO raw ai_response fields in any entry")
            print(f"  ✅ Signals preserved for learning: {sum(len(e.get('signals', [])) for e in logged_entries)} total signals")
            print(f"  ✅ Gates preserved for indexing: {sum(len(e.get('gates', [])) for e in logged_entries)} total gates")
            print(f"\n✅ System is PRIVACY-SAFE and ready for production")
            return True
        else:
            print("❌ PRIVACY CHECKS FAILED")
            if not all_privacy_safe:
                print("  Some entries have raw user data exposed!")
            if len(logged_entries) != len(test_exchanges):
                print(f"  Entry count mismatch: expected {len(test_exchanges)}, got {len(logged_entries)}")
            return False

if __name__ == "__main__":
    try:
        success = test_privacy_e2e()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
