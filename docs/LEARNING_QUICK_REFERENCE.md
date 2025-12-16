# Dynamic Learning System - Quick Reference

## The Big Picture

```text
```

Playwright writes dialogue scenes ↓ Organizer extracts rules and principles ↓ System applies
principles to generate responses ↓ Responses are logged and analyzed ↓ System learns new patterns ↓
Library grows, responses improve

```



## The Three Layers at a Glance

### 1. Archetype Library
**Stores learned patterns**
```text
```text
```

What you need: Library of conversation archetypes File:
emotional_os/learning/conversation_archetype.py What it does:

- Stores patterns (ReliefToGratitude, OverwhelmToClarity, etc.)
- Matches incoming user input to best pattern (0-1 score)
- Tracks usage and success rates
- Persists to JSON

Example archetype: { "name": "ReliefToGratitude", "entry_cues": ["relief", "grateful", "hug",
"precious", ...], "response_principles": ["Validate warmly", "Balance emotions", ...],
"continuity_bridges": ["Connect to prior overwhelm", ...], "tone_guidelines": ["Warm language",
"Gentle pacing", ...], "success_weight": 0.95 }

```




### 2. Response Generator
**Applies principles to generate responses**

```sql
```

What you need: Generate fresh responses from principles
File: emotional_os/learning/archetype_response_generator.py
What it does:

- Finds best-matching archetype for user input
- Extracts response principles from that archetype
- Generates response following those principles
- NOT template selection — actual generation

Input: "I feel relieved after that difficult conversation"
Archetype: ReliefToGratitude
Principles: [Validate warmly, Balance emotions, Ask gentle question]
Output: "That takes courage. Sounds like something shifted.
         What helped you get there?"

```



### 3. Conversation Learner
**Extracts patterns from conversations**
```sql
```sql
```

What you need: Auto-extract new archetypes from successful conversations
File: emotional_os/learning/conversation_learner.py
What it does:

- Analyzes conversation turns
- Detects emotional arc (e.g., OverwhelmToRelief)
- Extracts entry cues from user language
- Parses how system responded successfully
- Creates new archetype or refines existing one

Input: 6-turn conversation between user and system
Analysis:

- Emotional arc: ReliefToGratitude
- Entry cues: ["heavy", "hug", "melted away", "wonderful"]
- Response principles: ["Validate emotion first", "Balance mixed emotions"]
- Continuity bridges: ["Connect to prior overwhelm"]
- Tone guidelines: ["Warm language", "Mirror metaphors"]
Output: New archetype added to library

```




## Quick Start Code

### Generate a Response

```python
from emotional_os.learning import get_archetype_response_generator

generator = get_archetype_response_generator()
response = generator.generate_archetype_aware_response(
    user_input="I'm feeling grateful despite the stress",
    prior_context="Yesterday was really overwhelming",
)
```sql
```sql
```

### Learn from a Conversation

```python

from emotional_os.learning import get_conversation_learner

learner = get_conversation_learner()
conversation_turns = [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
]

new_archetype = learner.learn_from_conversation(
    turns=conversation_turns,
    user_rating=0.95,  # 1.0 = excellent
)

```text
```

### Check the Library

```python
from emotional_os.learning import get_archetype_library

library = get_archetype_library()

# See all archetypes
print(f"Total: {len(library.archetypes)}")

# Find best match for input
best = library.get_best_match("I feel relieved and grateful") print(f"Best match: {best.name if best
else 'None'}")

# Get all matches above threshold
matches = library.get_all_matches( user_input="I'm overwhelmed but grateful", threshold=0.3 ) for
archetype, score in matches:
```text
```text
```

## Pre-Loaded Archetype: ReliefToGratitude

Your dialogue scene → System extracted this archetype

**When it triggers**: Keywords like relief, grateful, hug, precious, melted away, wonderful + mixed emotions + life change

**How it responds**:

1. Validates the positive moment warmly
2. Acknowledges mixed emotions (joy + sorrow)
3. Gently asks about the deeper feeling
4. References prior context if available
5. Uses warm, metaphorical language

**Example responses**:

- Input: "My child hugged me and I felt relieved after a heavy day"
- Response: "That moment with your child sounds genuinely special. What does that connection feel like for you?"

- Input: "I'm grateful but also feeling the weight of losing time with them"
- Response: "What you're sharing feels like joy mixed with sorrow. That complexity is real. What would help you hold both right now?"

## How to Add More Archetypes

### Step 1: Write a Dialogue Scene

```

User: "I've been so stressed about my performance review, but I just found out I got the raise."

System: "That's huge. That weight lifted off. How does it feel?"

User: "Like I can finally breathe. But now I feel guilty that it took this to relax."

System: "The relief and the guilt can coexist. What's underneath

```text
```

### Step 2: System Learns

```
Conversation → Learner analyzes → New archetype created
```text
```text
```

### Step 3: System Uses It

Next similar input automatically uses learned principles

## Archetype Structure

Every archetype has these components:

```json

{
  "name": "ArchetypeName",
  "entry_cues": ["keyword1", "keyword2", "..."],
  "response_principles": [
    "Principle 1",
    "Principle 2",
    "..."
  ],
  "continuity_bridges": [
    "How to reference prior context",
    "How to carry themes forward",
    "..."
  ],
  "tone_guidelines": [
    "Language style",
    "Pacing",
    "Emotional calibration",
    "..."
  ],
  "pattern_template": "Optional flow description",
  "success_weight": 0.95,
  "usage_count": 5,
  "success_count": 5

```text
```

## Files to Know

| Path | Purpose |
|------|---------|
| `emotional_os/learning/conversation_archetype.py` | Core storage & matching |
| `emotional_os/learning/archetype_response_generator.py` | Response generation |
| `emotional_os/learning/conversation_learner.py` | Pattern extraction |
| `emotional_os/learning/archetype_library.json` | Persisted patterns |
| `test_learning_module.py` | Test suite |
| `LEARNING_MODULE_GUIDE.md` | Full documentation |

## Testing

```bash

# Run complete test
python test_learning_module.py

# View the archetype library
cat emotional_os/learning/archetype_library.json | python -m json.tool

# Test a single response
python -c " from emotional_os.learning import get_archetype_response_generator gen =
get_archetype_response_generator() resp = gen.generate_archetype_aware_response( 'I feel relieved
and grateful' ) print(resp) "
```

## Key Insight

**Template-based**: Select from A, B, C, or D
**Principle-driven**: Follow these rules to generate something fresh

That's the difference. The system learns **how** to respond, not **what** to say.

##

**You now have a learning system. Next: integrate it into the main pipeline so it starts improving automatically with every conversation.**
