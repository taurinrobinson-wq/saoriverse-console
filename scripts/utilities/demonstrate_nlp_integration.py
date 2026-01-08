#!/usr/bin/env python3
"""
Demonstration of Enhanced NLP Integration
Shows the improvements from integrating NRC, TextBlob, and spaCy into emotion processing.
"""

import json
from parser.enhanced_emotion_processor import analyze_emotion_enhanced

from emotional_os.glyphs.signal_parser import parse_input


def demonstrate_enhancement():
    """Demonstrate the enhanced emotion processing capabilities."""

    test_inputs = [
        "I feel anxious and worried about everything",
        "I'm so happy and excited about this new opportunity",
        "This makes me really sad and disappointed",
        "I'm angry and frustrated with the situation",
        "I feel peaceful and content right now",
    ]

    print("FP Enhanced NLP Integration Demonstration")
    print("=" * 50)

    for i, text in enumerate(test_inputs, 1):
        print(f'\n📝 Test {i}: "{text}"')
        print("-" * 40)

        # Show enhanced emotion analysis
        enhanced_analysis = analyze_emotion_enhanced(text)
        print("🔍 Enhanced Analysis:")
        print(
            f"   Dominant Emotion: {enhanced_analysis['dominant_emotion']} (confidence: {enhanced_analysis['confidence']:.2f})"
        )
        print(f"   NRC Emotions: {enhanced_analysis['nrc_emotions']}")
        print(
            f"   TextBlob Sentiment: polarity={enhanced_analysis['textblob_sentiment']['polarity']:.2f}, subjectivity={enhanced_analysis['textblob_sentiment']['subjectivity']:.2f}"
        )
        print(f"   Recommended Gates: {enhanced_analysis['recommended_gates']}")

        # Show integrated parsing results
        result = parse_input(text, "velonix_lexicon.json")

        print("⚡ Integrated Processing:")
        print(f"   Signals Detected: {len(result['signals'])}")
        for signal in result["signals"]:
            source = signal.get("source", "traditional")
            conf = signal.get("confidence", "N/A")
            print(f"     - {signal['keyword']} ({source}, conf: {conf})")

        print(f"   Gates Activated: {result['gates']}")
        print(f"   Response Source: {result['response_source']}")

        # Show response preview
        response_preview = (
            result["voltage_response"][:100] + "..."
            if len(result["voltage_response"]) > 100
            else result["voltage_response"]
        )
        print(f'   Response Preview: "{response_preview}"')

    print("\n" + "=" * 50)
    print("✨ Integration Benefits:")
    print("   • Multi-source emotion detection (NRC + TextBlob + spaCy)")
    print("   • Confidence-weighted signal generation")
    print("   • Enhanced gate routing based on emotional context")
    print("   • Fallback optimization for edge cases")
    print("   • Privacy-preserving offline processing")


if __name__ == "__main__":
    demonstrate_enhancement()
