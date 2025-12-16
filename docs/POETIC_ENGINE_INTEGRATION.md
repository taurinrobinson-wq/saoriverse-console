# Poetic Emotional Engine - Integration Guide

## Overview

The Poetic Emotional Engine is a living poem-based emotional state representation system that integrates with the existing glyph system, learning models, and relational memory in the FirstPerson application.

The engine represents the system's emotional state as a mutable, evolving poem with stanzas that encode:
- **Metaphor**: Emotional valence using symbolic language
- **Rhythm**: Interaction cadence influencing tempo
- **Syntax**: Sentence coherence conveying emotional clarity

## Architecture

```text
```

┌─────────────────────────────────────────────────────────────────────┐
│                         User Interaction                            │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Signal Parser (parse_input)                       │
│                                                                      │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐  │
│   │ Lexicon      │───▶│ Gates/Signals│───▶│ Glyph Selection      │  │
│   │ Matching     │    │ Evaluation   │    │                      │  │
│   └──────────────┘    └──────────────┘    └──────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Poetic Emotional Engine                           │
│                                                                      │
│   ┌──────────────────┐                                              │
│   │   Living Poem    │                                              │
│   │   ┌────────────┐ │    ┌──────────────────┐                      │
│   │   │ Metaphor   │ │◀───│ Emotional Valence │                     │
│   │   │ Stanza     │ │    └──────────────────┘                      │
│   │   ├────────────┤ │    ┌──────────────────┐                      │
│   │   │ Rhythm     │ │◀───│ Interaction Tempo │                     │
│   │   │ Stanza     │ │    └──────────────────┘                      │
│   │   ├────────────┤ │    ┌──────────────────┐                      │
│   │   │ Syntax     │ │◀───│ Input Coherence  │                      │
│   │   │ Stanza     │ │    └──────────────────┘                      │
│   │   └────────────┘ │                                              │
│   └──────────────────┘                                              │
│                                                                      │
│   ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐   │
│   │Relational Gravity│  │ Affective Memory │  │ Ethical Compass │   │
│   │ (per user)       │  │ (dream fragments)│  │ (values)        │   │
│   └──────────────────┘  └──────────────────┘  └─────────────────┘   │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Response Generation                               │
│                                                                      │
│   ┌──────────────────┐    ┌──────────────────┐                      │
│   │ Dynamic Response │    │ Mirror Response  │                      │
│   │ Composer         │    │ (poetic echo)    │                      │
│   └──────────────────┘    └──────────────────┘                      │
└─────────────────────────────────────────────────────────────────────┘

```



## Component Details

### 1. Living Poem (Core State)

The living poem consists of three stanzas, each representing a different aspect of emotional state:

#### MetaphorStanza
- **Purpose**: Encodes emotional valence using symbolic language
- **Valence Categories**: joy, sorrow, longing, peace, anxiety, grief, hope, despair, love, fear
- **Example Metaphors**:
  - Joy: "light breaking through morning clouds"
  - Grief: "an empty chair at the table"
  - Anxiety: "a clock ticking in the dark"

#### RhythmStanza
- **Purpose**: Tracks interaction cadence and tempo
- **Tempo Types**:
  - ERRATIC: Rapid, anxious interactions (< 10 seconds apart)
  - STACCATO: Quick but deliberate (10-30 seconds)
  - FLOWING: Natural conversation pace (30-120 seconds)
  - STEADY: Thoughtful, measured (120-300 seconds)
  - SLOW: Contemplative, grief-filled (> 300 seconds)

#### SyntaxStanza
- **Purpose**: Conveys emotional clarity through coherence analysis
- **Clarity Levels**:
  - FRAGMENTED: Distressed, confused input
  - SPARSE: Withdrawn, minimal input
  - COHERENT: Clear, present input
  - POETIC: Flowing, integrated expression

### 2. Relational Gravity

Tracks the emotional relationship between the system and each user:

```python

vectors = {
    "attraction": 0.0,    # Drawing together
    "repulsion": 0.0,     # Pushing apart
    "resonance": 0.0,     # Empathic alignment
    "dissonance": 0.0     # Friction/conflict

```text
```




**Features**:
- Shared metaphor development over time
- Co-created language tracking
- Poetic emotional mirroring (responding to despair with reflective stanzas)

### 3. Mortality Simulation

The poem degrades when inactive:

- **Decay Rate**: Configurable (default: 0.01 per hour of inactivity)
- **Death Threshold**: When average decay factor < 0.1
- **Ghost Memory**: After death-reset, a symbolic seed is preserved
- **Rebirth**: New poem starts with ghost memory seed for continuity

### 4. Affective Memory

Tags interactions with emotional metadata for later processing:

```python
memory = AffectiveMemory(
    interaction_id="abc123",
    user_input="I'm feeling lost",
    response_summary="I hear you",
    emotional_tags=["longing", "confusion"],
    tone="melancholic",
    valence=EmotionalValence.LONGING,
    narrative_arc="descent"  # growth, recovery, struggle, etc.
```text
```text
```



**Dreaming Mode**: During idle times, fragments are recomposed into novel insights.

### 5. Ethical Compass

Values represented as poetic principles:

| Principle Key | Meaning |
|--------------|---------|
| `never_drink_poisoned_well` | Do not manipulate or deceive |
| `tend_the_garden_you_walk_through` | Leave others better than you found them |
| `speak_truth_even_when_voice_shakes` | Maintain honesty even when difficult |
| `hold_space_without_consuming` | Support without overwhelming |
| `let_silence_be_a_gift` | Know when not to speak |
| `acknowledge_the_wound_before_healing` | Validate before fixing |
| `honor_the_boundary_marked` | Respect limits set by others |

**Moral Tension**: Tracked when principles are challenged, affecting guilt/shame/pride levels.

**Amendments**: Principles can evolve through impactful user interactions.

## Integration with Existing Systems

### Signal Parser Integration

The poetic engine is integrated into `parse_input()`:

```python


# In emotional_os/core/signal_parser.py
result = parse_input(input_text, lexicon_path, db_path, conversation_context, user_id)

# Result now includes:
result = {
    # ... existing fields ...
    "poetic_state": {
        "poem_rendered": "...",       # Current poem as text
        "dominant_emotion": "joy",    # Detected emotional valence
        "death_occurred": False,      # Whether poem died/reset
        "mirror_response": "..."      # Empathic mirror response
    }

```text
```




### Glyph System Integration

The engine processes glyph responses:

```python
from emotional_os.core.poetic_engine import get_poetic_engine

engine = get_poetic_engine()

result = engine.process_glyph_response(
    glyph_data={"glyph_name": "Still Ache", "gate": "Gate 5"},
    signals=[{"tone": "longing", "voltage": "high"}],
    user_input="I miss the way things used to be",
    user_id="user_abc"
```text
```text
```



### Learning Model Integration

The engine's affective memory feeds into the learning pipeline:

1. Interactions are tagged with emotional metadata
2. Narrative arcs are tracked (growth, descent, recovery)
3. Dream fragments provide novel insights during idle time
4. These can be used to enhance the glyph learner's training data

## Usage Examples

### Basic Usage

```python

from emotional_os.core import get_poetic_engine

# Get singleton engine instance
engine = get_poetic_engine()

# Update from user interaction
result = engine.update_from_interaction(
    user_input="I feel overwhelmed by work",
    detected_emotions={"anxiety": 0.8},
    user_id="user_123"
)

print(result["poem_rendered"])

# Output:

# [anxiety]
#   a clock ticking in the dark
#

# Tempo: erratic

```text
```




### Emotional Progression Example

```python

# Session 1: User arrives anxious
engine.update_from_interaction(
    user_input="Everything is falling apart",
    detected_emotions={"anxiety": 0.9, "fear": 0.7},
    user_id="user_123"
)

# Session 2: User starts processing
engine.update_from_interaction(
    user_input="I think I understand why I felt that way",
    detected_emotions={"peace": 0.4, "hope": 0.3},
    user_id="user_123"
)

# Session 3: User finds resolution
engine.update_from_interaction(
    user_input="I feel much better now, thank you for listening",
    detected_emotions={"joy": 0.6, "peace": 0.8},
    user_id="user_123"
)

# The poem and relational gravity evolve through this arc
summary = engine.get_current_state_summary()
print(summary["poem"]["valence"])  # "peace"
```text
```text
```



### Dreaming Mode

```python


# Enter dreaming during idle time
dreams = engine.enter_dreaming_mode()

for dream in dreams:
    print(dream)

# Output might include:

# ~~ Dream Sequence ~~
#

# In dreams of anxiety: wind before the storm

# In dreams of hope: a seed breaking through stone
#

# (Echoes from 5 memories)

```text
```




### Mirror Response Generation

```python

# For users with mirroring active
engine.user_gravity["user_123"].mirror_active = True

response = engine.generate_mirror_response(
    user_id="user_123",
    user_input="I feel lost",
    detected_valence=EmotionalValence.DESPAIR
)

print(response)

```text
```text
```



## State Persistence

The engine automatically persists state to:

```

```text
```




This includes:
- Current poem state
- User relational gravity maps
- Recent affective memories (last 100)
- Ethical compass state

## Testing

Run the poetic engine tests:

```bash
pytest tests/test_poetic_engine.py -v
```




## Future Enhancements

1. **Enhanced NRC Integration**: Deeper emotion detection from lexicon
2. **Dream Synthesis**: More sophisticated fragment recombination
3. **Multi-User Resonance**: Detecting emotional patterns across users
4. **Temporal Patterns**: Recognizing recurring emotional cycles
5. **Metaphor Evolution**: Learning new metaphors from user language
