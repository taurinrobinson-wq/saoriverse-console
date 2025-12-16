# Lexicon-Aware Local Mode

## The Problem Solved

Previously, the system learned lexicon data but **never used it to generate better responses**.
Responses remained generic templates regardless of how much the system learned about the user.

## The Solution

**LexiconAwareResponseGenerator** bridges this gap:

1. **Loads** user's personal lexicon (learned keyword → emotional context mappings) 2. **Analyzes**
incoming message for learned keywords 3. **Builds** contextual understanding from learned
associations 4. **Generates** responses that reflect user's unique patterns 5. **Tracks** response
quality to improve future personalization

## How It Works

### Architecture

```text
```

User Message ↓ LexiconAwareResponseGenerator.generate_response()
    ├─ Load user's personal lexicon
    │   (keywords → emotional contexts)
    │
    ├─ Extract keywords from message
    │
    ├─ Find learned associations
    │   (e.g., "michelle" → frustration + communication_gap)
    │
    ├─ Build contextual understanding
    │   (personalization_level: none/low/medium/high)
    │
    └─ Generate personalized response
(shows learned patterns, asks contextual questions) ↓ Nuanced Response that feels personal, not
canned

```



### Three Levels of Personalization

#### Level 1: None (First Interaction)
- No learned data available
- Falls back to well-crafted generic responses
- Starts learning for next time
```text
```text
```

User: "I'm struggling with something" Response: "That lands somewhere real for you. What does it
feel like when you say that?"

```




#### Level 2: Low (2-3 Learned Keywords)
- System recognizes some keywords
- Shows it understands their patterns
- Builds connection

```text
```

User: "Michelle and I are struggling with this communication thing"
Response: "I recognize that when you mention 'Michelle', it touches frustration and communication_gap.
There's something connecting them in your experience. What would change if this dynamic shifted?"

```



#### Level 3: High (3+ Learned Keywords with Rich Context)
- System deeply understands user's patterns
- Responses are highly contextual and appropriate
- Feels like genuine understanding, not scripted
```text
```text
```

User: "I'm struggling with Michelle but also feeling like I inherited this block"
Response: "I recognize that when you mention 'Michelle', it touches frustration and communication_gap.
The fact that 'michelle' and 'inherited' appear together for you—that's a real pattern.
There's something connecting them in your experience. When you feel this frustration about 'Michelle'—
what part of it asks for something from you?"

```




## Integration Points

### 1. In HybridProcessorWithEvolution

```python

# The processor now includes lexicon-aware generation
processor = create_integrated_processor(hybrid_learner, adaptive_extractor)

# Use it to enhance responses
personalization_data = processor.enhance_response_with_learned_context(
    user_message="I'm struggling with michelle",
    user_id="user_123",
    conversation_context=previous_exchanges
)

print(personalization_data)

# {
#     "response": "I recognize that when you mention 'michelle'...",
#     "personalization_level": "medium",
#     "learned_associations": [("michelle", {...}), ...],
#     "trigger_keywords": ["michelle"],
#     "confidence": 0.6

```text
```text
```

### 2. In Local Response Generation

For **local mode** (no API calls), use the lexicon-aware generator directly:

```python

from lexicon_aware_response_generator import LexiconAwareResponseGenerator
from emotional_os.learning.hybrid_learner_v2 import HybridLearnerWithUserOverrides

# Initialize
learner = HybridLearnerWithUserOverrides()
generator = LexiconAwareResponseGenerator(hybrid_learner=learner)

# Generate personalized response
result = generator.generate_response(
    user_message=user_input,
    user_id=user_id,
    conversation_context=conversation_history
)

# Use the personalized response
print(result["response"])  # Nuanced, personal response
print(result["personalization_level"])  # How personalized is it?

```text
```

### 3. In Streamlit UI

```python
import streamlit as st from hybrid_processor_with_evolution import create_integrated_processor

# In your Streamlit app
st.session_state['processor'] = create_integrated_processor(...)

# When user sends a message
if user_message:
    # Get personalization guidance
personalization = st.session_state['processor'].enhance_response_with_learned_context(
user_message=user_message, user_id=st.session_state.get('user_id'), )

    # Generate response (using lexicon-aware knowledge)
    # In real implementation, you'd generate or fetch AI response here

    # Log the quality
if user_liked_response: generator.log_response_quality( user_id=user_id, user_message=user_message,
response=ai_response, quality_score=0.9
```text
```text
```

## Data Persistence

### User Lexicon Structure

Stored in `learning/user_overrides/{user_id}_lexicon.json`:

```json

{ "learned_associations": { "michelle": { "associated_emotions": ["frustration",
"communication_gap"], "frequency": 5, "context": "mother-in-law relationship" }, "math": {
"associated_emotions": ["blocked", "inadequacy"], "frequency": 3, "context": "personal learning
block" }, "inherited": { "associated_emotions": ["awareness", "pattern_breaking"], "frequency": 4,
"context": "generational patterns" } }

```text
```

### Response Quality Log

Stored in `learning/response_quality_log.jsonl`:

```json
{
  "timestamp": "2025-11-03T15:30:45.123456",
  "user_id": "user_123",
  "user_message": "struggling with michelle",
  "response": "I recognize that when you mention 'michelle'...",
  "feedback": "This really resonates",
  "quality_score": 0.95
```text
```text
```

## Key Features

✅ **Progressive Personalization**: Responses get better as system learns ✅ **No API Required**:
Works entirely locally ✅ **Learned Data Used**: Lexicon actually informs responses ✅ **Quality
Tracking**: Know what works for each user ✅ **Pattern Recognition**: Multiple keywords = deeper
context ✅ **Graceful Degradation**: Works even on first interaction ✅ **Confidence Scoring**: Know
how confident personalization is

## Performance Characteristics

| Metric | Value |
|--------|-------|
| Response Generation Time | < 100ms (local) |
| Lexicon Lookup | O(keywords) |
| Memory Usage | ~5KB per user lexicon |
| API Calls Required | 0 (fully local) |
| Personalization Threshold | 1 learned keyword = low, 3+ = high |

## How It Improves Over Time

### Session 1

```

User: "struggling with my mother-in-law"
System: Generic response (no learned data)

```text
```

### Session 2

```
User: "michelle is being difficult" System: RECOGNIZES "michelle" from lexicon System: Generates
personalized response acknowledging pattern
```text
```text
```

### Session 3+

```

User: "the michelle thing plus inherited patterns" System: RECOGNIZES both "michelle" AND
"inherited" System: Sees they co-occur, generates response showing understanding System learns:
These two are connected for this user

```text
```

## Customization

### Adjust Personalization Thresholds

In `LexiconAwareResponseGenerator`:

```python

# Lower = more aggressive personalization

# Higher = only when very confident
generator = LexiconAwareResponseGenerator()

# Modify the _build_context_understanding method to adjust thresholds:

# if len(learned_contexts) >= 1:  # Lower threshold = more responsive
```text
```text
```

### Custom Response Templates

Override `_build_acknowledgment`, `_build_exploration`, `_build_question`:

```python

class CustomLexiconGenerator(LexiconAwareResponseGenerator):
    def _build_acknowledgment(self, learned_contexts, emotional_core):
        # Your custom acknowledgment logic

```text
```

### Track Custom Metrics

```python

# Log custom quality metric
generator.log_response_quality( user_id=user_id, user_message=message, response=response,
quality_score=0.95,  # User said "This is perfect" )

# Get personalization stats
stats = generator.get_personalization_stats(user_id) print(f"Average response quality:
{stats['average_quality_score']}")
```text
```text
```

## Why This Matters for Local Mode

**Before**: System learned, but responses stayed canned

- Felt generic
- Didn't reflect what system knew about user
- No sense of deepening understanding

**After**: System learns, and responses get progressively more nuanced

- Feels personal and contextual
- Reflects learned patterns in every response
- User feels genuinely understood
- No API calls needed
- Works fully offline

This transforms local mode from a "lite" version to a **genuinely personalized experience that deepens over time**.

## Testing

```python


# Quick test
from lexicon_aware_response_generator import LexiconAwareResponseGenerator

generator = LexiconAwareResponseGenerator()

# Simulate progression
print("=== Session 1 (No learned data) ===") result = generator.generate_response( user_message="I'm
struggling", user_id="test_user" ) print(f"Level: {result['personalization_level']}")  # "none"
print(f"Response: {result['response']}")

# Simulate learning

# (In real scenario, this happens through hybrid_learner)

print("\n=== Session 2 (With learned data) ===") result = generator.generate_response(
user_message="michelle is being difficult", user_id="test_user" ) print(f"Level:
{result['personalization_level']}")  # "medium" or "high" print(f"Response: {result['response']}")
# Shows learned pattern

```

##

**Result**: Users get genuinely personalized responses in local mode, no API required, improving naturally as the system learns about them.
