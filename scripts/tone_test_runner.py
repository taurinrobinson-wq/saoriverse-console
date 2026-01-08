#!/usr/bin/env python3
"""
Semantic test runner for DraftShift tone detection and transformation.

This version performs REAL validation:
- Re-detects tone after transformation
- Checks tone-specific linguistic markers
- Ensures removal of inappropriate markers
- Ensures meaningful change (not trivial edits)
- Prints transformed text for ALL cases
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd() / "src"))

from DraftShift.core import split_sentences, detect_tone, shift_tone, TONES


# ---------------------------------------------------------------------------
# Tone marker dictionaries
# ---------------------------------------------------------------------------

VERY_FORMAL_REQUIRED = [
    "however", "regarding", "at this time", "it appears", "it would be appreciated",
    "please advise", "i would appreciate"
]

VERY_FORMAL_FORBIDDEN = [
    "thanks", "thank you", "!", "just", "really", "so much"
]

FRIENDLY_REQUIRED = [
    "thanks", "thank you", "appreciate", "happy to", "when you get a chance"
]

FRIENDLY_FORBIDDEN = [
    "awful", "idiot", "stupid", "unacceptable"
]

EMPATHETIC_REQUIRED = [
    "i understand", "i recognize", "i appreciate", "i see", "i’m concerned", "i am concerned"
]

NEUTRAL_FORBIDDEN = [
    "awful", "concerned", "appreciate", "thanks", "unreasonable", "frustrated"
]


# ---------------------------------------------------------------------------
# Semantic validation
# ---------------------------------------------------------------------------

def validate_tone(original, transformed, target, detected_after):
    """Return (passed, message) with semantic checks."""

    o = original.strip()
    t = transformed.strip().lower()

    # 1. Must not be identical
    if t == o.lower():
        return False, "No meaningful change"

    # 2. Tone must match target
    if detected_after != target:
        return False, f"Tone mismatch: expected {target}, got {detected_after}"

    # 3. Tone-specific rules
    if target == "Very Formal":
        if any(word in t for word in VERY_FORMAL_FORBIDDEN):
            return False, "Very Formal contains forbidden informal markers"
        if not any(word in t for word in VERY_FORMAL_REQUIRED):
            return False, "Very Formal missing expected formal markers"

    if target == "Friendly":
        if any(word in t for word in FRIENDLY_FORBIDDEN):
            return False, "Friendly tone still contains harsh language"
        if not any(word in t for word in FRIENDLY_REQUIRED):
            return False, "Friendly tone missing warmth markers"

    if target == "Empathetic":
        if not any(word in t for word in EMPATHETIC_REQUIRED):
            return False, "Empathetic tone missing empathy markers"

    if target == "Neutral":
        if any(word in t for word in NEUTRAL_FORBIDDEN):
            return False, "Neutral tone contains emotional language"

    return True, "OK"


# ---------------------------------------------------------------------------
# Test samples
# ---------------------------------------------------------------------------

SAMPLES = [
    {
        "name": "Aggressive Insult",
        "text": "You're really awful. I'm done talking.",
    },
    {
        "name": "Professional Critique",
        "text": "This report is insufficient and fails to address key points.",
    },
    {
        "name": "Empathetic",
        "text": "I appreciate your effort, but I'm worried about the timeline.",
    },
    {
        "name": "Neutral Statement",
        "text": "We met yesterday to discuss the proposal.",
    },
    {
        "name": "Friendly Request",
        "text": "Could you please send the files? Thanks so much!",
    },
]


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

def run_tests():
    total = 0
    passed = 0

    print("\n=== DraftShift Semantic Tone Transformation Tests ===\n")

    for sample in SAMPLES:
        print(f"Sample: {sample['name']}")
        print(f"Original: {sample['text']}")
        sentences = split_sentences(sample["text"])
        detected_before = [detect_tone(s) for s in sentences]
        print(f"Detected before: {detected_before}")

        for target in TONES:
            total += 1

            # Transform
            transformed_sentences = [shift_tone(s, target) for s in sentences]
            transformed = " ".join(transformed_sentences)

            # Re-detect tone
            detected_after = detect_tone(transformed)

            # Validate
            ok, msg = validate_tone(sample["text"], transformed, target, detected_after)

            status = "PASS" if ok else "FAIL"
            print(f"  -> Target: {target.ljust(12)} | {status} | {msg}")
            print(f"     Output: {transformed}")

            if ok:
                passed += 1

        print("")

    print(f"\nSummary: {passed}/{total} checks passed")
    print("=====================================================\n")


if __name__ == "__main__":
    run_tests()
