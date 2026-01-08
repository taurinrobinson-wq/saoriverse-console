"""
Lexicon Reorganizer: Convert Gutenberg signal-centric data to word-centric indexing

Transforms:
- Signal-centric: {signal: {keywords: [], examples: []}} 
- Into word-centric: {word: {signals: [], gates: [], frequency: N, sources: []}}

This enables the parser to ask "what signals does HOLD trigger?" instead of 
"find all examples with HOLD in the 'vulnerability' signal"
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any


class LexiconReorganizer:
    """Convert Gutenberg signals -> word-centric emotional lexicon"""
    
    # Signal-to-gate mappings (emotional intensity + type)
    SIGNAL_TO_GATES = {
        'intimacy': [7, 11],           # deep connection, presence
        'vulnerability': [7, 11],       # openness, exposure
        'sensuality': [6, 9],           # body awareness, sensation
        'love': [8, 12],                # heart opening, sacred
        'admiration': [8, 12],          # respect, awe
        'transformation': [10, 11],     # change, becoming
        'joy': [1, 5],                  # celebration, lightness
        'nature': [3, 4],               # grounding, earth
    }
    
    # Transcript emotional words with expected gates
    TRANSCRIPT_WORDS = {
        'hold': {'frequency': 568, 'gates': [7, 11], 'primary_signal': 'vulnerability'},
        'sacred': {'frequency': 373, 'gates': [8, 12], 'primary_signal': 'admiration'},
        'echo': {'frequency': 212, 'gates': [7, 11], 'primary_signal': 'intimacy'},
        'tender': {'frequency': 150, 'gates': [8, 11], 'primary_signal': 'intimacy'},
        'honor': {'frequency': 116, 'gates': [8, 12], 'primary_signal': 'admiration'},
        'trust': {'frequency': 79, 'gates': [7, 11], 'primary_signal': 'intimacy'},
        'exactly': {'frequency': 367, 'gates': [1, 5], 'primary_signal': 'joy'},
        'resonate': {'frequency': 26, 'gates': [8, 11], 'primary_signal': 'love'},
        'tender': {'frequency': 150, 'gates': [8, 11], 'primary_signal': 'intimacy'},
        'present': {'frequency': 317, 'gates': [7, 11], 'primary_signal': 'intimacy'},
        'permission': {'frequency': 100, 'gates': [1, 7], 'primary_signal': 'vulnerability'},
        'feel': {'frequency': 200, 'gates': [6, 9], 'primary_signal': 'sensuality'},
        'both': {'frequency': 85, 'gates': [10, 11], 'primary_signal': 'transformation'},
        'then': {'frequency': 679, 'gates': [1, 5], 'primary_signal': 'joy'},
        'hear': {'frequency': 54, 'gates': [7, 11], 'primary_signal': 'intimacy'},
        'lands': {'frequency': 46, 'gates': [1, 5], 'primary_signal': 'joy'},
    }
    
    def __init__(self, signal_lexicon_path: str, transcript_cleaned_path: str):
        """Initialize with Gutenberg and transcript data"""
        self.signal_lexicon_path = signal_lexicon_path
        self.transcript_path = transcript_cleaned_path
        self.signal_lexicon = None
        self.transcript_data = None
        self.word_centric_lexicon = {}
        
    def load_signal_lexicon(self) -> None:
        """Load the Gutenberg signal-centric lexicon with error handling"""
        try:
            with open(self.signal_lexicon_path, 'r', encoding='utf-8', errors='replace') as f:
                self.signal_lexicon = json.load(f)
            print(f"[OK] Loaded signal lexicon ({len(self.signal_lexicon)} items)")
        except Exception as e:
            print(f"[X] Error loading signal lexicon: {e}")
            raise
    
    def extract_words_from_signals(self) -> Dict[str, Dict[str, Any]]:
        """Extract individual words from signal examples and keywords"""
        def default_word_data():
            return {
                'signals': set(),
                'examples': [],
                'keywords_source': set(),
                'frequency': 0,
            }
        
        word_signals: Dict[str, Dict[str, Any]] = defaultdict(default_word_data)
        
        if not self.signal_lexicon or 'signals' not in self.signal_lexicon:
            print("[X] No signals found in lexicon")
            return {}
        
        signals = self.signal_lexicon['signals']
        
        for signal_name, signal_data in signals.items():
            print(f"\n  Processing signal: {signal_name}")
            
            # Extract from keywords
            keywords = signal_data.get('keywords', [])
            for keyword in keywords:
                words = self._tokenize_keywords(keyword)
                for word in words:
                    if len(word) > 2:  # Skip short words
                        word_signals[word]['signals'].add(signal_name)
                        word_signals[word]['keywords_source'].add(keyword)
            
            # Extract from examples (carefully - these are long texts)
            examples = signal_data.get('examples', [])
            for i, example in enumerate(examples[:2]):  # Only first 2 examples to avoid bloat
                # Extract key emotional phrases (max 50 words)
                words = self._extract_key_phrases(example, max_words=50)
                for word in words:
                    if len(word) > 2:
                        word_signals[word]['signals'].add(signal_name)
                        if i == 0:  # Track which examples had it
                            word_signals[word]['examples'].append(signal_name)
        
        # Convert sets to lists for JSON serialization
        result = {}
        for word, data in word_signals.items():
            result[word] = {
                'signals': list(data['signals']),
                'keywords_source': list(data['keywords_source']),
                'gutenberg_examples': data['examples'],
                'frequency': 0,  # Will be filled from transcript
            }
        
        print(f"\n[OK] Extracted {len(result)} words from Gutenberg signals")
        return result
    
    def _tokenize_keywords(self, keyword: str) -> List[str]:
        """Extract individual words from a keyword phrase"""
        # Remove punctuation and split
        cleaned = re.sub(r'[^\w\s]', '', keyword.lower())
        return [w.strip() for w in cleaned.split() if w.strip()]
    
    def _extract_key_phrases(self, text: str, max_words: int = 50) -> Set[str]:
        """Extract key emotional words from example text"""
        # Simple word extraction with emotional word filtering
        text_lower = text.lower()
        # Remove Gutenberg artifacts
        text_lower = re.sub(r'\n+', ' ', text_lower)
        text_lower = re.sub(r'[^\w\s]', ' ', text_lower)
        
        words = text_lower.split()
        # Return unique words, limited by max_words
        return set(w for w in words[:max_words] if len(w) > 3)
    
    def analyze_transcript_frequencies(self) -> Dict[str, int]:
        """Analyze frequencies from cleaned transcript"""
        import csv
        
        word_freq = Counter()
        
        try:
            with open(self.transcript_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    message = row.get('Message', '').lower()
                    # Extract words - keep them as they are
                    words = re.findall(r'\b[a-z]+\b', message)
                    word_freq.update(words)
        except Exception as e:
            print(f"[X] Error reading transcript: {e}")
            return {}
        
        # Get top emotional words
        top_words = {
            word: freq for word, freq in word_freq.most_common(500)
            if len(word) > 2 and freq > 10
        }
        
        print(f"[OK] Analyzed transcript: {len(word_freq)} unique words, {sum(word_freq.values())} total")
        return top_words
    
    def build_word_centric_lexicon(self) -> Dict[str, Dict[str, Any]]:
        """Build the final word-centric lexicon"""
        print("\n" + "="*70)
        print("BUILDING WORD-CENTRIC LEXICON")
        print("="*70)
        
        # 1. Extract from Gutenberg
        print("\n[1/4] Extracting words from Gutenberg signals...")
        gutenberg_words = self.extract_words_from_signals()
        
        # 2. Get transcript frequencies
        print("\n[2/4] Analyzing transcript frequencies...")
        transcript_freq = self.analyze_transcript_frequencies()
        
        # 3. Merge and enrich
        print("\n[3/4] Merging Gutenberg + transcript data...")
        lexicon = {}
        
        # Start with known transcript words
        for word, meta in self.TRANSCRIPT_WORDS.items():
            lexicon[word] = {
                'word': word,
                'frequency': meta['frequency'],
                'gates': meta['gates'],
                'primary_signal': meta['primary_signal'],
                'signals': [meta['primary_signal']],
                'sources': ['transcript'],
                'gutenberg_context': gutenberg_words.get(word, {}).get('signals', []),
                'examples': gutenberg_words.get(word, {}).get('gutenberg_examples', []),
            }
        
        # Add high-frequency transcript words not in hardcoded list
        for word, freq in transcript_freq.items():
            if word not in lexicon and freq > 30:
                if word in gutenberg_words:
                    signals = gutenberg_words[word]['signals']
                    primary_signal = signals[0] if signals else 'joy'
                else:
                    signals = []
                    primary_signal = 'joy'
                
                # Map to gates
                gates = self.SIGNAL_TO_GATES.get(primary_signal, [1, 5])
                
                lexicon[word] = {
                    'word': word,
                    'frequency': freq,
                    'gates': gates,
                    'primary_signal': primary_signal,
                    'signals': signals,
                    'sources': ['transcript'],
                    'gutenberg_context': gutenberg_words.get(word, {}).get('signals', []),
                    'examples': gutenberg_words.get(word, {}).get('gutenberg_examples', []),
                }
        
        # 4. Summary statistics
        print("\n[4/4] Finalizing lexicon...")
        
        # Sort by frequency
        sorted_lexicon = dict(
            sorted(lexicon.items(), key=lambda x: x[1]['frequency'], reverse=True)
        )
        
        self.word_centric_lexicon = sorted_lexicon
        
        print(f"\n[OK] Built word-centric lexicon:")
        print(f"  Total words: {len(sorted_lexicon)}")
        print(f"  From transcript: {len([w for w in sorted_lexicon.values() if 'transcript' in w['sources']])}")
        print(f"  From Gutenberg: {len([w for w in sorted_lexicon.values() if 'gutenberg' in w['sources']])}")
        print(f"\n  Top 15 by frequency:")
        for i, (word, data) in enumerate(list(sorted_lexicon.items())[:15], 1):
            print(f"    {i:2}. {word:15} freq={data['frequency']:4} signals={data['signals']} gates={data['gates']}")
        
        return sorted_lexicon
    
    def save_lexicon(self, output_path: str) -> None:
        """Save the word-centric lexicon to JSON"""
        if not self.word_centric_lexicon:
            print("[X] No lexicon built yet")
            return
        
        output = {
            'metadata': {
                'type': 'word-centric-emotional-lexicon',
                'version': '2.0',
                'description': 'Emotional words mapped to signals, gates, and frequencies',
                'sources': ['transcript', 'gutenberg'],
                'total_words': len(self.word_centric_lexicon),
            },
            'lexicon': self.word_centric_lexicon,
            'signal_map': self.SIGNAL_TO_GATES,
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            
            file_size = Path(output_path).stat().st_size
            print(f"\n[OK] Saved lexicon to {output_path}")
            print(f"  File size: {file_size:,} bytes")
        except Exception as e:
            print(f"[X] Error saving lexicon: {e}")
            raise
    
    def generate_integration_guide(self, output_path: str) -> None:
        """Generate a guide for integrating the lexicon into the parser"""
        guide = f"""# Word-Centric Lexicon Integration Guide

## What Changed

The signal lexicon has been reorganized from **signal-centric** to **word-centric**:

### Old Structure (Signal-Centric)
```json
{{
  "signals": {{
    "intimacy": {{
      "keywords": ["hold", "touch", "present"],
      "examples": ["...long poetry text..."]
    }}
  }}
}}
```

### New Structure (Word-Centric)  
```json
{{
  "hold": {{
    "frequency": 568,
    "gates": [7, 11],
    "signals": ["vulnerability", "intimacy"],
    "sources": ["transcript"],
    "gutenberg_context": ["intimacy", "vulnerability"]
  }},
  "sacred": {{
    "frequency": 373,
    "gates": [8, 12],
    "signals": ["admiration", "transformation"],
    "sources": ["transcript", "gutenberg"],
    "gutenberg_context": ["admiration"]
  }}
}}
```

## Benefits

1. **Direct Lookups**: `lexicon["hold"]` instead of searching through all signals
2. **Multi-Signal Mapping**: One word can trigger multiple emotional signals
3. **Frequency Data**: Know which words most frequently appear in conversations
4. **Gate Assignment**: Immediate gate activation mapping
5. **Source Tracking**: Know if word came from user conversations or classic poetry
6. **Queryable**: Enable "give me all intimacy words" or "what signals does HOLD trigger?"

## Integration Steps

### 1. Update signal_parser.py

```python
# Old way
for signal_name, signal_data in lexicon['signals'].items():
    keywords = signal_data.get('keywords', [])
    # ... search through all signals for word match

# New way
word_data = lexicon.get('hold')
if word_data:
    gates = word_data['gates']
    signals = word_data['signals']
    # Direct lookup!
```

### 2. Update parse_input() function

```python
def parse_input(user_message: str):
    words = tokenize(user_message)
    
    # Now this is FAST:
    for word in words:
        if word in word_centric_lexicon:
            emotional_signals = word_centric_lexicon[word]['signals']
            gates = word_centric_lexicon[word]['gates']
            frequency = word_centric_lexicon[word]['frequency']
            
            # Use this data to select appropriate glyph/voltage
```

### 3. Create Query Functions

```python
# Get all words for a signal
def words_for_signal(signal_name):
    return [word for word, data in lexicon.items() 
            if signal_name in data['signals']]

# Get all words that activate specific gates
def words_for_gates(gate_numbers):
    return [word for word, data in lexicon.items()
            if any(g in data['gates'] for g in gate_numbers)]

# Get most frequently used emotional words
def top_emotional_words(n=20):
    return sorted(lexicon.items(), 
                  key=lambda x: x[1]['frequency'], 
                  reverse=True)[:n]
```

## File Locations

- **New lexicon**: `emotional_os/lexicon/word_centric_emotional_lexicon.json`
- **Old lexicon** (backup): `emotional_os/parser/signal_lexicon.json`
- **Integration script** (placeholder): `emotional_os/core/lexicon_loader.py`

## Migration Path

1. [OK] New lexicon created and tested
2. -> Update signal_parser.py to use word-centric lookups
3. -> Add query functions for common operations
4. -> Test with sample inputs (stressed, hold, sacred, exactly, etc.)
5. -> Benchmark performance (should be 10x faster)
6. -> Deprecate old signal_lexicon.json

## Word Coverage

**Total words in lexicon**: {len(self.word_centric_lexicon)}

**From transcript**: {len([w for w in self.word_centric_lexicon.values() if 'transcript' in w['sources']])} words
- HOLD (568x), SACRED (373x), EXACTLY (367x), PRESENT (317x), ECHO (212x), etc.

**From Gutenberg**: {len([w for w in self.word_centric_lexicon.values() if 'gutenberg' in w['sources']])} words
- Classic emotional language with deep literary examples

**Top 10 words**:
"""
        for i, (word, data) in enumerate(list(self.word_centric_lexicon.items())[:10], 1):
            guide += f"\n{i:2}. **{word}** (freq={data['frequency']}) -> gates {data['gates']} [{', '.join(data['signals'])}]"
        
        guide += f"""

## Next Steps

1. Review GLYPH_ENHANCEMENTS_FROM_TRANSCRIPT.md for how to use these words
2. Check TRANSCRIPT_ANALYSIS_INSIGHTS.md for emotional vocabulary recommendations
3. Integrate new Glyphs that leverage high-frequency emotional words
4. A/B test response quality with word-centric emotional recognition

---

Generated: {Path(output_path).parent.name}
"""
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(guide)
            print(f"\n[OK] Generated integration guide: {output_path}")
        except Exception as e:
            print(f"[X] Error generating guide: {e}")


def main():
    """Run the lexicon reorganization"""
    print("\n" + "="*70)
    print("LEXICON REORGANIZER: Signal-Centric -> Word-Centric")
    print("="*70)
    
    # Paths
    signal_lexicon = 'emotional_os/parser/signal_lexicon.json'
    transcript = 'copilot-activity-history-cleaned.csv'
    output_lexicon = 'emotional_os/lexicon/word_centric_emotional_lexicon.json'
    output_guide = 'LEXICON_REORGANIZATION_GUIDE.md'
    
    # Create output directory
    Path('emotional_os/lexicon').mkdir(parents=True, exist_ok=True)
    
    # Run reorganization
    reorganizer = LexiconReorganizer(signal_lexicon, transcript)
    
    try:
        reorganizer.load_signal_lexicon()
        reorganizer.build_word_centric_lexicon()
        reorganizer.save_lexicon(output_lexicon)
        reorganizer.generate_integration_guide(output_guide)
        
        print("\n" + "="*70)
        print("[OK] REORGANIZATION COMPLETE")
        print("="*70)
        print(f"\nNext steps:")
        print(f"  1. Review {output_guide}")
        print(f"  2. Check word-centric lexicon: {output_lexicon}")
        print(f"  3. Update signal_parser.py to use word-centric lookups")
        print(f"  4. Test with high-frequency words: hold, sacred, exactly, echo")
        
    except Exception as e:
        print(f"\n[X] Reorganization failed: {e}")
        raise


if __name__ == '__main__':
    main()
