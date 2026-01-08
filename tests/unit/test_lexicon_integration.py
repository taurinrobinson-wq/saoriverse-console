#!/usr/bin/env python3
"""Quick test of lexicon integration"""

from emotional_os.lexicon.lexicon_loader import get_lexicon

# Load the lexicon
lexicon = get_lexicon()
print("✓ Lexicon loaded successfully")

# Test some key words
test_words = ['hold', 'sacred', 'exactly', 'echo', 'tender', 'gentle', 'safe', 'depth']

print("\nTesting key emotional words:")
for word in test_words:
    signals = lexicon.get_signals(word)
    gates = lexicon.get_gates(word)
    freq = lexicon.get_frequency(word)
    print(f"{word:12} → signals: {signals}, gates: {gates}, freq: {freq}")

# Test text analysis
print("\nAnalyzing sample text...")
text = "I hold this moment sacred and I feel safe being tender with you"
analysis = lexicon.analyze_emotional_content(text)
print(f"Emotional words found: {len(analysis['emotional_words'])} words")
for word_data in analysis['emotional_words']:
    print(f"  {word_data['word']}: {word_data['signals']} (gates: {word_data['gates']}, freq: {word_data['frequency']})")

print(f"\nPrimary signals detected: {analysis['primary_signals']}")
print(f"Gate activations: {analysis['gate_activations']}")
print(f"Emotional intensity: {analysis['intensity']:.2f}")

print("\n✓ Integration test complete!")
