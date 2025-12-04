# Dynamic Conversation Learning Module

## Overview

You've just built a **three-layer system** that enables the saoriverse console to learn from lived dialogue and evolve dynamically. This is a fundamental shift from template-based responses to principle-driven, adaptive conversation.

### The Three Layers

```
┌─────────────────────────────────────────────────────────────┐
│ 1. ARCHETYPE LIBRARY                                        │
│    Stores learned conversation patterns extracted from      │
│    successful dialogues. Each archetype is a rule set, not  │
│    a canned script.                                         │
│                                                             │
│    - Entry Cues: Keywords/signals that trigger pattern      │
│    - Response Principles: Core rules system follows         │
│    - Continuity Bridges: How to maintain context across    │
│    - Tone Guidelines: Style, pacing, emotional calibration │
│    - Success Weight: How well this archetype performs       │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. RESPONSE GENERATOR                                       │
│    Applies learned archetype principles to generate fresh   │
│    responses. NOT template rotation — actually honors the   │
│    principles extracted from your dialogue.                 │
│                                                             │
│    When user message arrives:                              │
│    1. Find best-matching archetype                          │
│    2. Extract its principles                                │
│    3. Generate response following those principles          │
│    4. Each response is unique (not template variation)      │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. CONVERSATION LEARNER                                     │
│    After each good conversation, automatically extracts     │
│    new patterns or refines existing ones. This runs         │
│    asynchronously to improve the library.                   │
│                                                             │
│    Analysis pipeline:                                       │
│    1. Detect emotional arc (e.g., OverwhelmToGratitude)    │
│    2. Extract entry cues from user's language              │
│    3. Parse how system responded successfully              │
│    4. Extract principles and tone guidelines                │
│    5. Add/merge into archetype library                      │
│    6. Update success weights based on user feedback         │
└─────────────────────────────────────────────────────────────┘
```

## The Workflow

### Phase 1: Playwright (You Write Dialogue)
You create a conversational scene showing how the system should respond:

```
User: Yesterday was so heavy, but today my child hugged me 
      and I felt like everything melted away for a moment.

System: That moment with your child sounds genuinely special. 
        What does that connection feel like for you?

User: Maybe even more so. I don't know sometimes I don't 
      feel like I'm doing enough for my kids...
```

### Phase 2: Organizer (System Extracts Rules)
The learner automatically extracts principles:

```json
{
  "archetype": "ReliefToGratitude",
  "entry_cues": ["relief", "grateful", "hug", "melted away"],
  "response_principles": [
    "Validate positive moment warmly",
    "Balance empathy across mixed emotions",
    "Invite elaboration with gentle questions"
  ],
  "continuity_bridges": [
    "Connect gratitude to prior overwhelm",
    "Carry forward themes into deeper exploration"
  ],
  "tone_guidelines": [
    "Warm and embracing language",
    "Gentle pacing with validation first",
    "Mirror user's metaphors"
  ]
}
```

### Phase 3: Application (System Uses Principles)
When user sends: *"I'm stressed but my friend just made me laugh"`

System:
1. Matches to `ReliefToGratitude` archetype
2. Applies principles: validate warmly + balance emotions + gentle question
3. Generates: *"That's the kind of moment that cuts through the weight. What did their humor touch in you?"*

Each response is **unique** because it's generated from principles, not templates.

### Phase 4: Continuous Learning
System records whether user found response helpful, updates archetype success weights, and learns from outcomes.

## Key Files

| File | Purpose |
|------|---------|
| `emotional_os/learning/conversation_archetype.py` | Core archetype storage and matching |
| `emotional_os/learning/archetype_response_generator.py` | Applies archetypes to generate responses |
| `emotional_os/learning/conversation_learner.py` | Extracts patterns from successful conversations |
| `emotional_os/learning/__init__.py` | Module exports and singleton management |
| `emotional_os/learning/archetype_library.json` | Persisted library of all learned patterns |

## API Usage

### Using the System

```python
from emotional_os.learning import (
    get_archetype_library,
    get_archetype_response_generator,
    get_conversation_learner,
)

# Generate a response using learned archetypes
generator = get_archetype_response_generator()
response = generator.generate_archetype_aware_response(
    user_input="I feel grateful but also overwhelmed",
    prior_context="Yesterday I was so stressed",
    glyph=None,  # Optional glyph for tonal calibration
)

# Learn from a conversation
learner = get_conversation_learner()
new_archetype = learner.learn_from_conversation(
    turns=[
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."},
        # ... more turns
    ],
    user_rating=0.9,  # 1.0 = excellent, 0.0 = poor
)
```

### Checking the Library

```python
library = get_archetype_library()

# Get all archetypes
archetypes = library.archetypes

# Find best match for input
best_match = library.get_best_match(
    user_input="I'm feeling better but still sad",
    prior_context="I lost someone important",
    threshold=0.3  # Minimum match score
)

# Record success for learning
library.record_usage("ReliefToGratitude", success=True)
```

## Why This Matters

### Before (Template-Based)
- System selects from 5+ template banks randomly
- Response rotation: opening_moves → movement_language → poetry_line → closing_moves
- Even "personalized" variations were still template bits assembled randomly
- No continuity across turns
- System couldn't learn from what worked

### After (Principle-Driven Learning)
- System learns rules from lived dialogue
- Each response generated fresh according to principles, not templates
- Responses maintain conversational coherence across turns
- System improves automatically as it learns from successful conversations
- Users can contribute new dialogue scenes → system learns new archetypes
- Library grows organically with real conversational patterns

## Next Steps

### To Extend the System

1. **Add More Dialogue Scenes**: You write more conversational scenes, each becomes an archetype
   
2. **Integrate with Streamlit UI**: Show users that the system is learning their conversational patterns
   
3. **Add User Feedback Loop**: Let users rate responses, which auto-updates archetype success weights
   
4. **Multi-Turn Refinement**: System improves its archetype matching across a full conversation
   
5. **Export Archetypes**: Share learned patterns as a portable library other instances can use

### To Test

```bash
# Run the test suite
python test_learning_module.py

# Check the archetype library
cat emotional_os/learning/archetype_library.json | python -m json.tool
```

## Architecture Strengths

✓ **Modular**: Each layer is independent, can be updated separately  
✓ **Auditable**: Every archetype is readable JSON, not buried in ML weights  
✓ **Expandable**: Add new archetypes without retraining  
✓ **Personalized**: Learns from YOUR dialogue, your communication style  
✓ **Transparent**: You can see exactly why system chose a response  
✓ **Adaptive**: Success weights evolve based on real outcomes  

---

**This is the foundation for truly adaptive, learning-based empathetic conversation.**

Next: Integrate this into the main response pipeline so it starts learning from every conversation automatically.
