# Word-Centric Lexicon Integration Guide

## What Changed

The signal lexicon has been reorganized from **signal-centric** to **word-centric**:

### Old Structure (Signal-Centric)

```json
{
  "signals": {
    "intimacy": {
      "keywords": ["hold", "touch", "present"],
      "examples": ["...long poetry text..."]
    }
  }
}
```


### New Structure (Word-Centric)

```json
{
  "hold": {
    "frequency": 568,
    "gates": [7, 11],
    "signals": ["vulnerability", "intimacy"],
    "sources": ["transcript"],
    "gutenberg_context": ["intimacy", "vulnerability"]
  },
  "sacred": {
    "frequency": 373,
    "gates": [8, 12],
    "signals": ["admiration", "transformation"],
    "sources": ["transcript", "gutenberg"],
    "gutenberg_context": ["admiration"]
  }
}
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

**Total words in lexicon**: 457

**From transcript**: 457 words

- HOLD (568x), SACRED (373x), EXACTLY (367x), PRESENT (317x), ECHO (212x), etc.

**From Gutenberg**: 0 words

- Classic emotional language with deep literary examples

**Top 10 words**:

 1. **the** (freq=14589) -> gates [1, 5] []
 2. **you** (freq=12339) -> gates [1, 5] []
 3. **that** (freq=9404) -> gates [1, 5] [joy, transformation, admiration, love, intimacy, nature, sensuality, vulnerability]
 4. **and** (freq=8680) -> gates [1, 5] []
 5. **not** (freq=5286) -> gates [1, 5] []
 6. **taurin** (freq=4223) -> gates [1, 5] []
 7. **just** (freq=4177) -> gates [1, 5] []
 8. **with** (freq=3480) -> gates [1, 5] [joy, love, intimacy, sensuality, vulnerability]
 9. **like** (freq=3222) -> gates [8, 12] [love]
10. **but** (freq=3183) -> gates [1, 5] []

## Next Steps

1. Review GLYPH_ENHANCEMENTS_FROM_TRANSCRIPT.md for how to use these words
2. Check TRANSCRIPT_ANALYSIS_INSIGHTS.md for emotional vocabulary recommendations
3. Integrate new Glyphs that leverage high-frequency emotional words
4. A/B test response quality with word-centric emotional recognition

##

Generated:
