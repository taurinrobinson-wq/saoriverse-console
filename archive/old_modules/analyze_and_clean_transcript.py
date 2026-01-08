"""
Analyze Copilot transcript to:
1. Find and remove legal case references
2. Extract useful conversational patterns and lexicon
3. Identify AI response characteristics (em dash usage, length, patterns)
"""

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

# Legal keywords to detect sensitive content
LEGAL_KEYWORDS = [
    'court', 'legal', 'case', 'attorney', 'defendant', 'plaintiff',
    'lawsuit', 'litigation', 'judge', 'jury', 'trial', 'motion',
    'deposition', 'settlement', 'subpoena', 'gag order', 'witness',
    'evidence', 'counsel', 'verdict', 'conviction', 'sentence',
    'appeal', 'brief', 'filing', 'jurisdiction', 'litigation',
    'plaintiff', 'respondent', 'appellant', 'court order'
]

def is_legal_content(text):
    """Check if text contains legal case information."""
    text_lower = text.lower()
    # Check for keywords
    for keyword in LEGAL_KEYWORDS:
        if keyword in text_lower:
            return True
    # Check for common legal patterns
    if re.search(r'\b(?:vs|v\.)\s+', text):
        return True
    return False

def analyze_transcript(input_file):
    """Analyze transcript and return insights."""
    
    conversations = defaultdict(list)
    ai_messages = []
    human_messages = []
    stats = {
        'total_rows': 0,
        'ai_messages': 0,
        'human_messages': 0,
        'legal_content_rows': 0,
        'unique_conversations': set(),
        'ai_em_dash_count': 0,
        'ai_response_lengths': [],
    }
    
    legal_rows_found = []
    
    with open(input_file, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            stats['total_rows'] += 1
            conv_name = row.get('Conversation', 'Unknown')
            author = row.get('Author', '').strip()
            message = row.get('Message', '').strip()
            
            stats['unique_conversations'].add(conv_name)
            
            # Check for legal content
            if is_legal_content(message):
                stats['legal_content_rows'] += 1
                legal_rows_found.append({
                    'row': i + 2,  # +2 for header
                    'conversation': conv_name,
                    'author': author,
                    'message_preview': message[:100]
                })
            
            # Track messages
            if author == 'AI':
                stats['ai_messages'] += 1
                ai_messages.append(message)
                stats['ai_response_lengths'].append(len(message))
                stats['ai_em_dash_count'] += message.count('—')
            elif author == 'Human':
                stats['human_messages'] += 1
                human_messages.append(message)
            
            conversations[conv_name].append({
                'author': author,
                'message': message,
                'row': i + 2
            })
    
    return {
        'stats': stats,
        'conversations': conversations,
        'ai_messages': ai_messages,
        'human_messages': human_messages,
        'legal_rows': legal_rows_found
    }

def extract_patterns(ai_messages, human_messages):
    """Extract useful conversational patterns."""
    
    patterns = {
        'common_ai_phrases': [],
        'conversational_markers': [],
        'emotional_language': [],
        'relational_language': [],
    }
    
    # Extract first 5-10 words of each AI message to find patterns
    openings = Counter()
    for msg in ai_messages:
        if msg:
            opening = ' '.join(msg.split()[:3])
            if opening:
                openings[opening] += 1
    
    patterns['common_ai_phrases'] = openings.most_common(20)
    
    # Look for conversational markers
    conv_markers = []
    for msg in ai_messages[:500]:  # Sample first 500
        if any(marker in msg.lower() for marker in ['that', 'you', 'we', 'i', 'this', 'that']):
            conv_markers.append(msg[:60])
    
    # Extract emotional/relational language
    emotional_words = ['feel', 'trust', 'hold', 'echo', 'resonate', 'align', 'presence', 
                      'authentic', 'breathe', 'witness', 'sacred', 'honor', 'weave']
    relational_phrases = []
    for msg in ai_messages[:500]:
        msg_lower = msg.lower()
        for word in emotional_words:
            if word in msg_lower:
                relational_phrases.append(word)
                break
    
    patterns['emotional_language'] = Counter(relational_phrases).most_common(15)
    
    return patterns

def main():
    input_file = 'copilot-activity-history.csv'
    
    print("=" * 80)
    print("ANALYZING COPILOT TRANSCRIPT")
    print("=" * 80)
    
    # Analyze
    analysis = analyze_transcript(input_file)
    
    # Print statistics
    stats = analysis['stats']
    print(f"\n📊 STATISTICS")
    print(f"  Total rows: {stats['total_rows']}")
    print(f"  Unique conversations: {len(stats['unique_conversations'])}")
    print(f"  AI messages: {stats['ai_messages']}")
    print(f"  Human messages: {stats['human_messages']}")
    print(f"  Legal content rows found: {stats['legal_content_rows']}")
    
    # AI response characteristics
    if stats['ai_response_lengths']:
        avg_length = sum(stats['ai_response_lengths']) / len(stats['ai_response_lengths'])
        max_length = max(stats['ai_response_lengths'])
        min_length = min(stats['ai_response_lengths'])
        print(f"\n📝 AI RESPONSE CHARACTERISTICS")
        print(f"  Average length: {avg_length:.0f} characters")
        print(f"  Max length: {max_length} characters")
        print(f"  Min length: {min_length} characters")
        print(f"  Em-dash usage (total): {stats['ai_em_dash_count']}")
        print(f"  Em-dashes per message (avg): {stats['ai_em_dash_count'] / stats['ai_messages']:.2f}")
    
    # Legal content summary
    if analysis['legal_rows']:
        print(f"\n⚠️  LEGAL CONTENT DETECTED")
        print(f"  Found {len(analysis['legal_rows'])} rows with legal keywords")
        print(f"\n  Sample rows to remove:")
        for row_info in analysis['legal_rows'][:5]:
            print(f"    Row {row_info['row']}: {row_info['message_preview']}")
        if len(analysis['legal_rows']) > 5:
            print(f"    ... and {len(analysis['legal_rows']) - 5} more")
    
    # Extract patterns
    patterns = extract_patterns(analysis['ai_messages'], analysis['human_messages'])
    
    print(f"\n💬 CONVERSATIONAL PATTERNS")
    print(f"  Top 10 AI opening phrases:")
    for phrase, count in patterns['common_ai_phrases'][:10]:
        print(f"    '{phrase}...' ({count}x)")
    
    print(f"\n✨ EMOTIONAL/RELATIONAL LANGUAGE (Top 10):")
    for word, count in patterns['emotional_language']:
        print(f"    '{word}' ({count}x)")
    
    # Show conversations summary
    print(f"\n📚 CONVERSATIONS")
    for conv_name in sorted(list(stats['unique_conversations'])[:10]):
        conv_data = analysis['conversations'][conv_name]
        print(f"  {conv_name}: {len(conv_data)} messages")
    
    print("\n" + "=" * 80)
    print("To remove legal content, run: python clean_transcript.py")
    print("=" * 80)

if __name__ == '__main__':
    main()
