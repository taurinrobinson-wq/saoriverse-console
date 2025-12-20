"""Tiny CLI to demo EnhancedAffectParser"""
import sys
import pathlib

# Ensure repository root is on sys.path so `DraftShift` can be imported when run directly
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from DraftShift.enhanced_affect_parser import create_enhanced_affect_parser


def main():
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else sys.stdin.read().strip()
    if not text:
        print("Provide text as arguments or via stdin.")
        return

    parser = create_enhanced_affect_parser(use_nrc=True, use_textblob=False, use_spacy=False)
    result = parser.analyze_affect(text)

    print("Primary emotion:", result.primary_emotion)
    print("Confidence:", f"{result.emotion_confidence:.2f}")
    print("Valence:", f"{result.valence:.2f}")
    print("Arousal:", f"{result.arousal:.2f}")
    print("Dominance:", f"{result.dominance:.2f}")
    print("TextBlob polarity (if available):", result.sentiment_polarity)
    print("NRC scores:")
    for k, v in result.nrc_scores.items():
        print(f"  {k}: {v:.3f}")
    print("Explanation:", result.explanation)


if __name__ == '__main__':
    main()
