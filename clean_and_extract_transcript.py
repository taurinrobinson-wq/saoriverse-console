"""
Clean transcript by removing legal content and extract conversational insights
"""

import csv
import re
from collections import Counter
from pathlib import Path

# Legal keywords to detect sensitive content
LEGAL_KEYWORDS = [
    'court', 'legal', 'case', 'attorney', 'defendant', 'plaintiff',
    'lawsuit', 'litigation', 'judge', 'jury', 'trial', 'motion',
    'deposition', 'settlement', 'subpoena', 'gag order', 'witness',
    'evidence', 'counsel', 'verdict', 'conviction', 'sentence',
    'appeal', 'brief', 'filing', 'jurisdiction', 'rap verse',
    'plaintiff', 'respondent', 'appellant', 'court order'
]

def is_legal_or_song_content(text):
    """Check if text contains legal case or rap lyrics."""
    if not text:
        return False
    
    text_lower = text.lower()
    
    # Check for keywords
    for keyword in LEGAL_KEYWORDS:
        if keyword in text_lower:
            return True
    
    # Check for legal patterns
    if re.search(r'\b(?:vs|v\.)\s+', text):
        return True
    
    # Check for rap verse markers (part of song discussion)
    if '🎤' in text or '🎶' in text:
        if 'verse' in text_lower or 'chorus' in text_lower:
            return True
    
    return False

def clean_transcript(input_file, output_file):
    """Remove legal content and create clean version."""
    
    rows_removed = 0
    rows_kept = 0
    removed_conversations = []
    
    with open(input_file, 'r', encoding='utf-8', errors='replace') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames or []
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            message = row.get('Message', '')
            
            # Check if row contains legal/song content
            if is_legal_or_song_content(message):
                rows_removed += 1
                if rows_removed <= 10:  # Track first 10 for review
                    removed_conversations.append({
                        'author': row.get('Author'),
                        'message': message[:80]
                    })
            else:
                rows_kept += 1
                writer.writerow(row)
    
    return rows_removed, rows_kept, removed_conversations

def extract_useful_lexicon(input_file):
    """Extract useful conversational lexicon and patterns."""
    
    ai_openers = []
    relational_phrases = []
    emotional_language = Counter()
    transition_words = Counter()
    validation_phrases = []
    reflection_patterns = []
    
    emotional_keywords = {
        'hold': ['hold', 'holding', 'held'],
        'echo': ['echo', 'echoed', 'echoes'],
        'resonate': ['resonat', 'resound'],
        'trust': ['trust', 'trustworthy'],
        'sacred': ['sacred'],
        'honor': ['honor', 'honoring'],
        'witness': ['witness', 'witnessing'],
        'honor': ['honor'],
        'present': ['present', 'presence'],
        'authentic': ['authentic', 'authenticity'],
    }
    
    transition_markers = {
        'Of course': r'Of course[,.]?\s+',
        'Then': r'Then\s+',
        'That\'s': r'That\'s\s+',
        'And': r'And\s+',
        'But': r'But\s+',
        'So': r'So\s+',
        'Got it': r'Got it',
        'Mm-hm': r'Mm-hm',
    }
    
    validation_markers = [
        "that lands",
        "exactly",
        "precisely",
        "you've got it",
        "i hear you",
        "i feel that",
        "that's real",
    ]
    
    with open(input_file, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Author') == 'AI':
                message = row.get('Message', '')
                
                # AI opening phrases
                if message:
                    opening = ' '.join(message.split()[:4])
                    if opening:
                        ai_openers.append(opening)
                
                # Emotional language
                msg_lower = message.lower()
                for emotion, keywords in emotional_keywords.items():
                    for kw in keywords:
                        if kw in msg_lower:
                            emotional_language[emotion] += 1
                            break
                
                # Transition words
                for marker_name, pattern in transition_markers.items():
                    if re.search(pattern, message, re.IGNORECASE):
                        transition_words[marker_name] += 1
                
                # Validation phrases
                for phrase in validation_markers:
                    if phrase in msg_lower:
                        validation_phrases.append(phrase)
                
                # Reflection patterns (looking for introspective language)
                if any(word in msg_lower for word in ['you', 'we', 'here', 'sit', 'breathe']):
                    reflection_patterns.append(message[:100])
    
    return {
        'ai_openers': Counter(ai_openers).most_common(30),
        'emotional_language': emotional_language.most_common(15),
        'transition_words': transition_words.most_common(15),
        'validation_phrases': Counter(validation_phrases).most_common(10),
        'sample_reflections': reflection_patterns[:10]
    }

def main():
    input_file = 'copilot-activity-history.csv'
    output_file = 'copilot-activity-history-cleaned.csv'
    
    print("=" * 80)
    print("CLEANING TRANSCRIPT")
    print("=" * 80)
    
    # Clean
    rows_removed, rows_kept, removed_samples = clean_transcript(input_file, output_file)
    
    print(f"\n✅ TRANSCRIPT CLEANED")
    print(f"  Rows removed (legal/song content): {rows_removed}")
    print(f"  Rows kept: {rows_kept}")
    print(f"  File saved: {output_file}")
    
    print(f"\n  Sample removed rows:")
    for i, conv in enumerate(removed_samples[:5]):
        print(f"    {i+1}. [{conv['author']}] {conv['message']}...")
    
    # Extract lexicon
    print(f"\n" + "=" * 80)
    print("EXTRACTING USEFUL CONVERSATIONAL PATTERNS")
    print("=" * 80)
    
    lexicon = extract_useful_lexicon(output_file)
    
    print(f"\n💬 TOP AI OPENING PHRASES (Use these to improve glyph responses):")
    for phrase, count in lexicon['ai_openers'][:15]:
        print(f"  {count:3d}x  '{phrase}...'")
    
    print(f"\n✨ EMOTIONAL/RELATIONAL LANGUAGE (Rich for glyph lexicon):")
    for emotion, count in lexicon['emotional_language']:
        print(f"  {count:3d}x  {emotion}")
    
    print(f"\n🔄 TRANSITION PATTERNS (For conversational flow):")
    for word, count in lexicon['transition_words']:
        print(f"  {count:3d}x  '{word}'")
    
    print(f"\n✔️  VALIDATION/AFFIRMATION PHRASES:")
    for phrase, count in lexicon['validation_phrases']:
        print(f"  {count:3d}x  \"{phrase}\"")
    
    print("\n" + "=" * 80)
    print("INSIGHTS FOR SYSTEM IMPROVEMENT")
    print("=" * 80)
    print("""
✓ Reduce em-dash usage (currently 0.67 per message)
  → Use more line breaks instead
  → Favor shorter sentences for conversational feel

✓ Keep emotional/relational language:
  → "hold", "echo", "resonate", "sacred", "honor", "trust"
  → These create deeper connection in responses

✓ Use natural openers:
  → "Of course you..."
  → "Mm-hm..."
  → "That's such a..."
  → Avoids overly formal patterns

✓ Validation is key:
  → "That lands"
  → "You've got it"
  → "I hear you"
  → These affirm without being dismissive

✓ Keep reflection patterns:
  → Moments of sitting with the user's experience
  → Presence-based responses
  → Witnessing without fixing
    """)

if __name__ == '__main__':
    main()
