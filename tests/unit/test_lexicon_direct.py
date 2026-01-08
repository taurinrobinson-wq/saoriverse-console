#!/usr/bin/env python3
"""Test lexicon directly"""

from emotional_os.lexicon.lexicon_loader import get_lexicon

lexicon = get_lexicon()
print('Lexicon loaded successfully')
print(f'Total words: {len(lexicon.lexicon)}')

# Test finding emotional words
text = 'I am feeling soft and vulnerable'
found_words = lexicon.find_emotional_words_with_context(text)
print(f'\nFound {len(found_words)} emotional words for: "{text}"')
for word, data, pos in found_words:
    print(f'  - {word}: signals={data.get("signals")}, gates={data.get("gates")}')

# Test analysis
analysis = lexicon.analyze_emotional_content(text)
print(f'\nHas emotional content: {analysis["has_emotional_content"]}')
print(f'Emotional words found: {analysis["emotional_words"]}')
print(f'Primary signals: {analysis["primary_signals"]}')
print(f'Gate activations: {analysis["gate_activations"]}')

# Test another sentence
print("\n" + "="*50)
text2 = 'This moment feels sacred and tender'
found_words2 = lexicon.find_emotional_words_with_context(text2)
print(f'\nFound {len(found_words2)} emotional words for: "{text2}"')
for word, data, pos in found_words2:
    print(f'  - {word}: signals={data.get("signals")}, gates={data.get("gates")}')
