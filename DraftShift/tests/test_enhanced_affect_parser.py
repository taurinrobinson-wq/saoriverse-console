# Simple tests for EnhancedAffectParser
import sys
import pathlib

# Ensure repository root is on sys.path so `DraftShift` can be imported when run directly
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from DraftShift.enhanced_affect_parser import create_enhanced_affect_parser


def run_tests():
    parser = create_enhanced_affect_parser(use_nrc=True, use_textblob=False, use_spacy=False)

    cases = [
        ("I am very happy and grateful.", "positive"),
        ("This is awful, I am angry.", "negative"),
        ("I feel sad and disappointed.", "negative"),
        ("Everything is fine.", "neutral"),
    ]

    failures = []
    for text, expected in cases:
        result = parser.analyze_affect(text)
        valence = result.valence
        print(f"Text: {text!r} -> valence={valence:.2f}, primary_emotion={result.primary_emotion}")

        if expected == "positive" and valence <= 0:
            failures.append((text, expected, valence))
        if expected == "negative" and valence >= 0:
            failures.append((text, expected, valence))
        if expected == "neutral" and abs(valence) > 0.4:
            failures.append((text, expected, valence))

    if failures:
        print("\nFailures:")
        for t, exp, got in failures:
            print(f"  {t!r}: expected {exp}, got valence={got}")
        raise SystemExit(2)

    print("\nAll tests passed.")


if __name__ == '__main__':
    run_tests()
