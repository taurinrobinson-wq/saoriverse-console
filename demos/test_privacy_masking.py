#!/usr/bin/env python3
"""
Test that the privacy-safe logging format works correctly.
This creates a test exchange and verifies the new format is used.
"""

import json
import hashlib
import tempfile
from pathlib import Path
from emotional_os.learning.hybrid_learner_v2 import HybridLearnerWithUserOverrides


def hash_user_id(user_id: str) -> str:
    """Hash user ID for privacy."""
    return hashlib.sha256(user_id.encode()).hexdigest()[:16]


def test_privacy_safe_logging():
    """Test that new exchanges log in privacy-safe format."""

    # Create temporary directory for test data
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Initialize learner with test paths
        learner = HybridLearnerWithUserOverrides(
            shared_lexicon_path=tmpdir / "shared_lexicon.json",
            user_overrides_dir=tmpdir / "user_overrides",
            learning_log_path=tmpdir / "hybrid_learning_log.jsonl"
        )

        # Create test exchange data
        user_id = "test_user_1"
        user_input = "I'm feeling deeply moved by the beauty of nature. There's something transcendent about watching the sunset."
        ai_response = "That's a beautiful observation. The interplay of light and shadow often stirs profound emotions in us."

        emotional_signals = [
            {"signal": "nature", "keyword": "nature",
                "confidence": 0.9, "gate": "Gate 6"},
            {"signal": "transcendence", "keyword": "transcendent",
                "confidence": 0.85, "gate": "Gate 4"},
            {"signal": "joy", "keyword": "beauty",
                "confidence": 0.8, "gate": "Gate 2"},
        ]

        glyphs = [
            {"glyph_name": "Nature's Touch", "confidence": 0.88},
            {"glyph_name": "Transcendent Moment", "confidence": 0.82},
        ]

        # Log the exchange using the modified method
        learner._log_exchange(
            user_id=hash_user_id(user_id),
            user_input=user_input,
            ai_response=ai_response,
            emotional_signals=emotional_signals,
            glyphs=glyphs
        )

        # Read back the logged entry
        with open(tmpdir / "hybrid_learning_log.jsonl", 'r') as f:
            logged_entry = json.loads(f.readline())

        print("✅ TEST: Privacy-Safe Logging Format")
        print("=" * 70)
        print("\n📝 Logged Entry Structure:")
        print(json.dumps(logged_entry, indent=2))

        # Verify format is correct (privacy-safe)
        print("\n🔍 Verification Checks:")
        checks = {
            "❌ NO raw user_input field": "user_input" not in logged_entry,
            "❌ NO ai_response field": "ai_response" not in logged_entry,
            "✅ HAS user_id_hash field": "user_id_hash" in logged_entry,
            "✅ HAS signals field": "signals" in logged_entry,
            "✅ HAS gates field": "gates" in logged_entry,
            "✅ HAS glyph_names field": "glyph_names" in logged_entry,
            "✅ signals is list": isinstance(logged_entry.get("signals"), list),
            "✅ gates is list": isinstance(logged_entry.get("gates"), list),
            "✅ Contains expected signals": "nature" in logged_entry.get("signals", []),
            "✅ Contains expected gates": "Gate 6" in logged_entry.get("gates", []),
            "✅ Contains expected glyphs": "Nature's Touch" in logged_entry.get("glyph_names", []),
        }

        all_pass = True
        for check_name, result in checks.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {check_name}")
            if not result:
                all_pass = False

        # Test user lexicon format
        print("\n" + "=" * 70)
        print("🔍 User Lexicon Privacy Format Test:")
        print("=" * 70)

        user_overrides = {
            "signals": {},
            "trust_score": 0.5,
            "contributions": 0
        }

        learner._learn_to_user_lexicon(
            user_overrides=user_overrides,
            user_input=user_input,
            ai_response=ai_response,
            emotional_signals=emotional_signals
        )

        if "nature" in user_overrides.get("signals", {}):
            nature_signal = user_overrides["signals"]["nature"]
            print("\n📝 User Lexicon Entry for 'nature' signal:")
            print(json.dumps(nature_signal, indent=2))

            # Verify format
            lexicon_checks = {
                "❌ NO full messages in example_contexts": all(
                    "user_input" not in ctx for ctx in nature_signal.get("example_contexts", [])
                ),
                "✅ HAS example_contexts (not examples)": "example_contexts" in nature_signal,
                "✅ example_contexts have keyword field": all(
                    "keyword" in ctx for ctx in nature_signal.get("example_contexts", [])
                ),
                "✅ example_contexts have associated_signals": all(
                    "associated_signals" in ctx for ctx in nature_signal.get("example_contexts", [])
                ),
                "✅ example_contexts have gates": all(
                    "gates" in ctx for ctx in nature_signal.get("example_contexts", [])
                ),
            }

            print("\nLexicon Verification Checks:")
            for check_name, result in lexicon_checks.items():
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{status}: {check_name}")
                if not result:
                    all_pass = False

        # Summary
        print("\n" + "=" * 70)
        if all_pass:
            print("✅ ALL TESTS PASSED - Privacy masking working correctly!")
            print("\n📋 SUMMARY:")
            print("  • Raw user_input: NOT logged (✅ Privacy Protected)")
            print("  • AI response: NOT logged (✅ Privacy Protected)")
            print("  • Signals: Logged (✅ Learning Preserved)")
            print("  • Gates: Logged (✅ Learning Preserved)")
            print("  • User lexicon: Stores signal context only (✅ Privacy Protected)")
        else:
            print("❌ SOME TESTS FAILED - Review output above")
        # Assert instead of returning so pytest doesn't see a non-None return value
        assert all_pass, "Some privacy masking checks failed; see output above"


if __name__ == "__main__":
    try:
        test_privacy_safe_logging()
        exit(0)
    except AssertionError as e:
        print(f"\n❌ Test assertion failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
