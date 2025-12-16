# Memory Layer: Quick Reference

## What It Does

Tracks user's emotional state across multiple messages and builds understanding.

```text
```

Message 1: "I'm stressed"
              ↓
Message 2: "Too much on my mind at work"
              ↓
Message 3: "5 projects, Thursday deadline"
              ↓
SYSTEM UNDERSTANDS: Work demands → cognitive flooding → paralysis → stuck

```


##

## Key Classes

### ConversationMemory (Main)

```python

memory = ConversationMemory()

# After each user message:
memory.add_turn(
    user_input="...",
    parsed=SemanticParsing(...),
    glyphs_identified=["..."],
    missing_elements=["..."],
    clarifications_asked=["..."],
)

# Get current state:
memory.get_emotional_profile_brief()  # "HIGH: stress, overload (in work)"
memory.get_causal_narrative()  # "work → cognitive flooding → paralysis"
memory.get_next_clarifications()  # ["What triggered?", "How many things?"]

```text
```

### SemanticParsing (Input)

```python
parsed = SemanticParsing(
    actor="I",
    primary_affects=["stress"],
    secondary_affects=["paralysis"],
    tense="present",
    emphasis="so",
    domains=["work"],
    temporal_scope="today",
    thought_patterns=["flooding"],
    action_capacity="paralyzed",
    raw_input="...",
```text
```text
```

##

## Integration Example

```python

from src.emotional_os_glyphs.conversation_memory import ConversationMemory, SemanticParsing
from src.emotional_os_glyphs.dynamic_response_composer import DynamicResponseComposer

# Initialize
memory = ConversationMemory()
composer = DynamicResponseComposer()

# Per message
user_input = "I'm feeling so stressed today"

parsed = SemanticParsing(
    actor="I",
    primary_affects=["stress"],
    secondary_affects=[],
    tense="present",
    emphasis="so",
    domains=[],
    temporal_scope="today",
    thought_patterns=[],
    action_capacity="unknown",
    raw_input=user_input,
)

# Store in memory
turn = memory.add_turn(
    user_input=user_input,
    parsed=parsed,
    glyphs_identified=["Still Insight"],
    missing_elements=["causation", "somatic"],
    clarifications_asked=["What triggered this?"],
)

# Generate response using memory
response = composer.compose_response_with_memory(
    input_text=user_input,
    conversation_memory=memory,
    glyph=None,
)

```text
```

##

## Response Composition

### With Memory

```python
def compose_response_with_memory(
    input_text,
    conversation_memory,
    glyph=None,
):
    # 1. Get integrated state
    integrated_state = memory.integrated_state
    causal_chain = memory.causal_understanding

    # 2. Build acknowledgment (causal-aware)
    acknowledgment = "I hear you - work has flooded your mind..."

    # 3. Add glyph validation (if rich)
    if len(glyph_set) > 1:
        validation = "This needs organizing."

    # 4. Add targeted clarification
    clarifications = memory.get_next_clarifications()
    question = "Which of these could wait?"

    # 5. Combine
```text
```text
```

##

## Data Structure Summary

| Component | Tracks | Example |
|-----------|--------|---------|
| **Turns** | Individual messages | "I'm stressed", "At work", "5 projects" |
| **Affects** | Emotional states | stress, overload, paralysis |
| **Domains** | Context areas | work, client, relationships |
| **Triggers** | Root causes | work demands, deadline |
| **Mechanisms** | How stress manifests | cognitive flooding, paralysis |
| **Manifestations** | Results | can't prioritize, can't act |
| **Glyphs** | Wisdom layers | Still Insight, Quiet Revelation |
| **Confidence** | Understanding level | 0.7 → 0.85 → 0.95 |
| **Needs** | Missing information | "What triggered?", "Which is urgent?" |

##

## Confidence Progression

```

Turn 1: 0.7 (emotion stated, cause unknown)
Turn 2: 0.85 (mechanism revealed: work → flooding → paralysis)

```text
```

##

## Glyph Evolution

```
Turn 1: [Still Insight]
Turn 2: [Still Insight, Quiet Revelation, Fragmentation]
```text
```text
```

##

## Response Quality Scale

| Without Memory | With Memory |
|---|---|
| "What triggered that?" | "I hear you're stressed" |
| Generic | Specific to emotions |
| - | ↓ |
| "Tell me more" | "Work has flooded your mind" |
| Repetitive | Mechanism-aware |
| - | ↓ |
| "Have you prioritized?" | "Which of 5 could wait?" |
| Generic suggestion | Action-oriented |

##

## Method Reference

### ConversationMemory

- `add_turn()` - Add message and integrate
- `get_emotional_profile_brief()` - Human-readable affect summary
- `get_causal_narrative()` - Trigger → Mechanism → Manifestation chain
- `get_next_clarifications()` - Top missing elements to ask about
- `get_glyph_set()` - All glyphs identified so far
- `get_conversation_summary()` - Full JSON snapshot

### DynamicResponseComposer

- `compose_response_with_memory()` - Generate memory-informed response
- `_build_first_turn_acknowledgment()` - Initial response
- `_build_subsequent_turn_acknowledgment()` - Mechanism-aware response
- `_build_glyph_validation_from_set()` - Multi-glyph validation text
- `_build_targeted_clarifications()` - Smart question from gaps

##

## Example Conversation

```

USER: "I'm feeling so stressed today"

SYSTEM (with memory):
  parsed: stress, present, today
  stored: confident in emotion, needs cause
  response: "I hear you're feeling stress today."

USER: "I have so much on my mind at work that I can't take a step"

SYSTEM (memory enriched):
  parsed: cognitive_overload, work, paralysis, flooding
  learns: work → cognitive flooding → paralysis
  stored: confident in mechanism, confidence 0.85
  response: "I hear you - work has flooded your mind with so many
            competing demands. What you're describing needs organizing."

USER: "5 projects due this week, client presentation Thursday, haven't started"

SYSTEM (full context):
  parsed: 5 items, Thursday deadline, client, unstarted
  learns: exact problem, most urgent item, blocker
  stored: confident in specifics, confidence 0.95

```text
```

##

## Files

### Core Implementation

- `src/emotional_os_glyphs/conversation_memory.py` - Memory layer
- `src/emotional_os_glyphs/dynamic_response_composer.py` - Response methods

### Tests

- `test_memory_layer.py` - Full integration test
- `test_memory_informed_logic.py` - Logic simulation

### Documentation

- `MEMORY_LAYER_ARCHITECTURE.md` - Full design
- `MEMORY_LAYER_VISUAL_ARCHITECTURE.md` - Diagrams
- `MEMORY_LAYER_IMPLEMENTATION_SUMMARY.md` - Status
- `MEMORY_LAYER_QUICK_REFERENCE.md` - This file

##

## Quick Start

```python

# 1. Import
from conversation_memory import ConversationMemory, SemanticParsing

# 2. Create
memory = ConversationMemory()

# 3. Parse each message
parsed = SemanticParsing(
    actor="I",
    primary_affects=["stress"],
    secondary_affects=[],
    tense="present",
    emphasis="so",
    domains=[],
    temporal_scope="today",
    thought_patterns=[],
    action_capacity="unknown",
    raw_input="I'm feeling so stressed today",
)

# 4. Add to memory
memory.add_turn(
    user_input="I'm feeling so stressed today",
    parsed=parsed,
    glyphs_identified=["Still Insight"],
    missing_elements=["causation"],
    clarifications_asked=["What triggered this?"],
)

# 5. Use memory in response
response = composer.compose_response_with_memory(
    input_text=user_input,
    conversation_memory=memory,
)
```

##

## Status: READY FOR INTEGRATION ✓

All components implemented and tested:

- ✅ Memory layer stores and integrates information
- ✅ Response composer uses memory for better responses
- ✅ Confidence scores track understanding
- ✅ Glyph sets evolve as understanding deepens
- ✅ Causal chains emerge correctly
- ✅ Tests pass and demonstrate behavior

**Next Step**: Integrate with Streamlit app
