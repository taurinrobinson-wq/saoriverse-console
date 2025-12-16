# Dynamic Glyph Evolution Integration

## Overview

The system now automatically creates new glyphs during live conversations through the hybrid
processor. This document explains how the components work together.

## Architecture

```text
```

┌─────────────────────────────────────────────────────────────────┐
│                    USER-AI DIALOGUE                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
▼ ┌────────────────────────────────────┐
        │  HYBRID PROCESSOR WITH EVOLUTION   │
        │                                    │
        │  ✓ Adaptive Signal Extraction      │
        │  ✓ Lexicon Learning               │
        │  ✓ Pattern Detection              │
        │  ✓ Glyph Generation               │
        └────────────────────────────────────┘
                   │                │
┌──────────▼────────┐    ┌──▼──────────────────┐
        │ HYBRID LEARNER    │    │ DYNAMIC GLYPH       │
        │                  │    │ EVOLUTION           │
        │ • User Overrides  │    │                    │
        │ • Shared Lexicon  │    │ • Detects Patterns │
        │ • Quality Filter  │    │ • Generates Glyphs │
        │ • Learning Log    │    │ • Tracks Discovery │
        └──────────────────┘    └─────┬──────────────┘
                                      │
┌─────────────▼────────────┐
                        │   NEW GLYPHS AVAILABLE   │
                        │   FOR SYSTEM USE         │
                        └──────────────────────────┘

```



## Components

### 1. **HybridProcessorWithEvolution** (`hybrid_processor_with_evolution.py`)

The main integration layer that orchestrates the entire pipeline:

```python

from hybrid_processor_with_evolution import create_integrated_processor

processor = create_integrated_processor( hybrid_learner=learner, adaptive_extractor=extractor,
user_id="user_123" )

result = processor.process_user_message( user_message="I feel a deep connection but it's
terrifying", ai_response="That vulnerability is the doorway...", )

# Result includes:

# - Signals extracted

# - Lexicon updates

# - New glyphs generated

```text
```

### 2. **DynamicGlyphEvolution** (`dynamic_glyph_evolution.py`)

Handles the core glyph generation logic:

- **Pattern Detection**: Identifies co-occurrence of emotional dimensions
- **Glyph Creation**: Generates new glyphs when patterns are significant
- **Tracking**: Maintains registry of conversation-discovered glyphs
- **Export**: Makes glyphs available for system integration

### 3. **HybridLearnerWithUserOverrides** (existing)

Learns from conversations:

- **User Overrides**: Personal emotional vocabulary per user
- **Shared Lexicon**: Quality-filtered contributions for all users
- **Quality Filtering**: Prevents toxic content poisoning shared lexicon
- **Trust Scoring**: Rates user contributions

### 4. **AdaptiveSignalExtractor** (existing)

Discovers new emotional dimensions:

- **Dynamic Dimensions**: Discovers beyond the original 8
- **Pattern Learning**: Learns from poetry and conversation
- **Scaling**: Grows with each interaction

## Flow: Dialogue → Glyphs

### Step 1: User-AI Exchange

```
User: "I feel deeply seen and yet exposed"
```text
```text
```

### Step 2: Signal Extraction (Adaptive)

```python

signals = extractor.extract_signals(combined_text)

# Returns: [
#   {"signal": "love", "strength": 0.9},
#   {"signal": "vulnerability", "strength": 0.8},

```text
```

### Step 3: Hybrid Learning

```python
learner.learn_from_exchange( user_id="user_123", user_input="...", ai_response="...",
emotional_signals=signals, )

# Updates:

# - User's personal lexicon (fast)

# - Shared lexicon (if quality passes)

```text
```text
```

### Step 4: Pattern Detection

```python

patterns = evolution._detect_patterns_in_exchange( user_input, ai_response, signals )

# Returns: [
#   {
#     "signal_pair": ["love", "vulnerability"],
#     "co_occurrence_count": 1,
#     "keywords": ["deeply", "seen", "exposed"],
#   }

```text
```

### Step 5: Glyph Generation

```python
new_glyphs = evolution._generate_glyphs_from_patterns(patterns, ...)

# Creates glyphs like:

# {
#   "id": "glyph_dialogue_user_123_abc_1",
#   "name": "Open-Hearted Love",
#   "symbol": "♥🌱",
#   "core_emotions": ["love", "vulnerability"],
#   "associated_keywords": ["deeply", "seen", "exposed"],
#   "combined_frequency": 300,
#   "response_cue": "Honor the courage of opening one's heart",
#   "created_from_conversation": true,

```text
```text
```

### Step 6: Glyph Integration

```python


# Glyphs automatically:

# - Saved to conversation_glyphs.json

# - Available for next dialogue turns

# - Exported to system database

```text
```

## Usage Examples

### Basic Integration

```python
from hybrid_processor_with_evolution import create_integrated_processor from
emotional_os.learning.hybrid_learner_v2 import HybridLearnerWithUserOverrides from
emotional_os.learning.adaptive_signal_extractor import AdaptiveSignalExtractor

# Initialize components
learner = HybridLearnerWithUserOverrides() extractor = AdaptiveSignalExtractor(adaptive=True,
use_discovered=True)

# Create integrated processor
processor = create_integrated_processor( hybrid_learner=learner, adaptive_extractor=extractor,
user_id="user_123", )

# Process dialogue
result = processor.process_user_message( user_message="I want to understand my grief",
ai_response="Grief is love with nowhere to go...", )

# Check results
print(f"New glyphs: {len(result['pipeline_stages']['glyph_generation']['new_glyphs_generated'])}")
```text
```text
```

### Processing Multiple Turns

```python

conversation_id = "conv_session_001"

# Turn 1
result1 = processor.process_user_message( user_message="I feel lost", ai_response="Feeling lost is
the beginning of finding yourself", conversation_id=conversation_id, )

# Turn 2
result2 = processor.process_user_message( user_message="But there's also beauty in the uncertainty",
ai_response="Yes, that uncertain beauty is where growth happens", conversation_id=conversation_id, )

# Get conversation summary
summary = processor.get_conversation_summary(conversation_id)

```text
```

### Accessing Generated Glyphs

```python

# Get all glyphs from current session
all_glyphs = processor.get_all_generated_glyphs()

# Get glyphs from specific conversation
conv_glyphs = processor.evolution.get_conversation_glyphs(
    conversation_id="conv_session_001"
)

# Get user-specific glyphs
user_glyphs = processor.evolution.get_conversation_glyphs(
    user_id="user_123"
)

# Print recent glyphs
```text
```text
```

### Exporting Glyphs for System Use

```python


# Export session glyphs
result = processor.export_session_glyphs(
    output_file="/path/to/session_glyphs.json"
)

# Result: {"success": true, "count": 15, "file": "..."}

# Or use evolution directly
export_result = processor.evolution.export_glyphs_for_system(
    output_file="/path/to/all_glyphs.json"

```text
```

### Session Summary

```python

# Print comprehensive summary
processor.print_session_summary()

# Output:

# ════════════════════════════════════════════════════════════════════════════════

# HYBRID PROCESSOR SESSION SUMMARY

# ════════════════════════════════════════════════════════════════════════════════
# Total conversations processed: 3

# Total turns processed: 8

# Total new glyphs generated: 5
# NEW GLYPHS GENERATED:
#   1. ♥❤ Intimate Connection (love + intimacy)
#   2. ♥🌱 Open-Hearted Love (love + vulnerability)
#   3. ♥🌹 Sensual Devotion (love + sensuality)
#   4. 🌱✨ Vulnerable Wonder (vulnerability + wonder)
# 5. 🌿🎻 Natural Longing (nature + longing)
```text
```text
```

## Configuration

### Minimum Frequency for Glyph Creation

```python

evolution = DynamicGlyphEvolution( hybrid_learner=learner, min_frequency_for_glyph=300,  # Default:
300 co-occurrences

```text
```

### Emotion-Symbol Mapping

Customize emoji symbols for different emotions:

```python
evolution.emotion_symbols = {
    "love": "♥",
    "intimacy": "❤",
    "vulnerability": "🌱",
    "joy": "☀",
    # ... add more
```text
```text
```

### Pattern Detection Tuning

Adjust keywords and thresholds in `_detect_patterns_in_exchange()`:

```python


# In dynamic_glyph_evolution.py, DynamicGlyphEvolution class
signal_keywords = {
    ("love", "intimacy"): ["love", "intimacy", "close", "tender", "embrace"],
    ("love", "vulnerability"): ["open", "honest", "bare", "risk"],
    # ... customize for your use case

```text
```

## Lexicon Expansion

The system automatically expands the lexicon through:

1. **User Learning**: Personal vocabulary per user
2. **Shared Learning**: Quality-filtered contributions for all users
3. **Adaptive Discovery**: New dimensions discovered from pattern analysis
4. **Glyph Patterns**: Co-occurrence patterns create new emotional territories

Example progression:

```
Initial: 8 hardcoded dimensions After poetry processing: 18+ adaptive dimensions
```text
```text
```

## Quality & Safety

### Quality Filtering for Shared Lexicon

The hybrid learner applies quality checks:

- ✓ Meaningful content (3+ words)
- ✓ No toxic keywords
- ✓ Reasonable length (< 5000 chars)
- ✓ Not repetitive templates
- ✓ Shows emotional engagement

```python

is_quality, reason = learner._is_quality_exchange( user_input, ai_response, signals )

```text
```

### User Trust Scoring

Each user has a trust score:

- Starts at 0.5 (neutral)
- Increases with quality contributions
- Decreases with poor contributions
- Affects weight in shared lexicon

## Storage

### Conversation Glyphs Registry

```
learning/
├── conversation_glyphs.json      # All discovered glyphs
│   {
│     "glyphs": [ {...}, ... ],
│     "metadata": {
│       "total_discovered": 45,
│       "last_updated": "2025-11-03T14:32:00"
│     }
│   }
├── user_overrides/
│   ├── user_123_lexicon.json     # User-specific learning
│   └── user_456_lexicon.json
├── generated_glyphs/
│   └── session_glyphs.json       # Exported for system
```text
```text
```

## Metrics & Monitoring

Track evolution progress:

```python


# Session metrics
print(f"Glyphs in session: {len(processor.generated_glyphs)}")
print(f"Conversations: {len(set(c['conversation_id'] for c in processor.conversation_history))}")
print(f"Total turns: {len(processor.conversation_history)}")

# Lexicon size
lexicon = processor.evolution._load_lexicon()
print(f"Active dimensions: {len(lexicon.get('signals', {}))}")

# User glyphs
user_glyphs = processor.evolution.get_conversation_glyphs(user_id="user_123")
print(f"Glyphs for user: {len(user_glyphs)}")

# Glyph frequencies
top_glyphs = sorted(
    processor.generated_glyphs,
    key=lambda g: g.get("combined_frequency", 0),
    reverse=True
)[:5]
for glyph in top_glyphs:

```text
```

## Next Steps

1. **Database Integration**: Export glyphs to system database
2. **Real-time Recognition**: Use generated glyphs in signal matching
3. **User Persistence**: Save user glyphs across sessions
4. **Visualization**: Display glyph generation in real-time
5. **Pattern Analysis**: Analyze which patterns lead to most meaningful glyphs
6. **A/B Testing**: Test different thresholds and symbol mappings

## Troubleshooting

### No Glyphs Generated

**Problem**: Running many conversations but no new glyphs are created.

**Causes**:

- Patterns not meeting frequency threshold (default: 300)
- Signals not being extracted properly
- Same signal pairs repeating (need new combinations)

**Solutions**:

- Lower `min_frequency_for_glyph` threshold
- Check signal extraction: `processor.evolution._load_lexicon()`
- Add more diverse conversation topics

### Glyphs Not Being Saved

**Problem**: Glyphs generated but not persisting.

**Check**:

- Verify `learning/` directory exists and is writable
- Check logs: `tail -f learning/hybrid_learning_log.jsonl`
- Ensure JSON serialization: `processor.export_session_glyphs("test.json")`

### Poor Signal Extraction

**Problem**: Signals not matching user input.

**Solutions**:

- Verify adaptive extractor is initialized
- Check lexicon has signal definitions
- Test extraction: `extractor.extract_signals("your text")`

## Advanced: Custom Glyph Generation

Create custom glyph generation logic:

```python
class CustomGlyphEvolution(DynamicGlyphEvolution): def _create_pattern_name(self, signal1, signal2):
        # Your custom naming logic
return f"Custom: {signal1} meets {signal2}"

def _create_pattern_symbol(self, signal1, signal2):
        # Your custom symbol selection
return "✨🔮"

# Use it
evolution = CustomGlyphEvolution(hybrid_learner) processor = HybridProcessorWithEvolution(...,
evolution)
```

## References

- `dynamic_glyph_evolution.py`: Core glyph generation
- `hybrid_processor_with_evolution.py`: Integration layer
- `emotional_os/learning/hybrid_learner_v2.py`: Learning system
- `emotional_os/learning/adaptive_signal_extractor.py`: Signal extraction
- `learning/conversation_glyphs.json`: Generated glyphs registry
