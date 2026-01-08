# Feeling System Integration Guide

## Overview

The Feeling System is a speculative emotional architecture designed to drive nuanced, context-aware responses in conversation and interaction. It operates as a **state machine that synthesizes emotions** from multiple subsystems, tracks emotional memory, and provides configurable parameters for tuning emotional behavior.

This guide explains how to integrate the Feeling System with your response engine and dialogue pipeline.

---

## Quick Start: Core API

### 1. Initialize the System

```python
from emotional_os.core.feeling_system import FeelingSystem, FeelingSystemConfig
from emotional_os.core.feeling_system_config import get_default_config

# Option A: Use defaults
config = get_default_config()
feeling_system = FeelingSystem(config=config)

# Option B: Customize configuration
config = get_default_config()
config.affective_memory.max_memories = 500  # Increase capacity
config.affective_memory.pruning_strategy = 'hybrid'  # Use hybrid pruning
feeling_system = FeelingSystem(config=config)
```

### 2. Process Interactions

```python
# After user input or system event, create emotional signals
emotional_signals = {
    'user_sentiment': 'positive',           # 'positive', 'negative', 'neutral'
    'interaction_type': 'intimate',         # 'friendly', 'intimate', 'hostile', 'formal'
    'context_familiarity': 0.8,             # 0.0-1.0 (how well system knows user/context)
    'emotional_intensity': 0.7,             # 0.0-1.0 (how emotionally charged the interaction is)
    'value_alignment': 0.9,                 # 0.0-1.0 (does action align with system's values?)
    'mortality_trigger': False,              # Does this touch on themes of death/ending?
    'user_id': 'user_12345'                 # For tracking relationships and memory per-user
}

# Process the interaction
feeling_system.process_interaction(
    user_message="I love how thoughtful you are",
    emotional_signals=emotional_signals,
    context="intimate_conversation"
)
```

### 3. Read Current Emotional State

```python
# Get synthesized emotional state for response generation
current_state = feeling_system.get_current_state()

print(f"Current emotion: {current_state['primary_emotion']}")
print(f"Emotional intensity: {current_state['intensity']}")
print(f"Emotional memory: {current_state['memory_influence']}")
print(f"All emotions: {current_state['all_emotions']}")

# Example response modulation
if current_state['primary_emotion'] == 'joy':
    response_tone = "warm, enthusiastic, open"
elif current_state['primary_emotion'] == 'sorrow':
    response_tone = "empathetic, gentle, reflective"
elif current_state['primary_emotion'] == 'fear':
    response_tone = "cautious, protective, grounding"
```

### 4. Persist State (Between Sessions)

```python
import json

# Save state to disk
state_dict = feeling_system.to_dict()
with open('feeling_system_state.json', 'w') as f:
    json.dump(state_dict, f, indent=2)

# Load state in new session
with open('feeling_system_state.json', 'r') as f:
    saved_state = json.load(f)
    
new_feeling_system = FeelingSystem(config=config)
new_feeling_system.from_dict(saved_state)
```

---

## Detailed API Reference

### FeelingSystem.process_interaction()

Processes a user interaction and updates internal emotional state.

**Signature:**
```python
def process_interaction(
    self,
    user_message: str,
    emotional_signals: dict,
    context: str = "general"
) -> None
```

**Parameters:**

- **user_message** (str): The actual user input or message being processed
- **emotional_signals** (dict): Dictionary of emotional context. See "Emotional Signals" section below.
- **context** (str): Context category for the interaction. Options:
  - `"general"` - Default, neutral conversation
  - `"intimate"` - Close relationship, vulnerable sharing
  - `"hostile"` - Adversarial or conflictual context
  - `"formal"` - Professional, structured interaction

**Example:**
```python
feeling_system.process_interaction(
    user_message="I'm struggling with this decision",
    emotional_signals={
        'user_sentiment': 'negative',
        'emotional_intensity': 0.8,
        'context_familiarity': 0.6,
        'value_alignment': 0.5,
        'interaction_type': 'vulnerable',
        'mortality_trigger': False,
        'user_id': 'user_xyz'
    },
    context='intimate'
)
```

### FeelingSystem.get_current_state()

Returns the synthesized emotional state based on all subsystems.

**Signature:**
```python
def get_current_state(self) -> dict
```

**Returns:**
```python
{
    'primary_emotion': 'contemplation',        # Main emotion being experienced
    'intensity': 0.65,                         # 0.0-1.0 emotional arousal level
    'memory_influence': 0.4,                   # How much past emotions affect current state
    'all_emotions': {                          # Compete set of emotions with weights
        'joy': 0.15,
        'sorrow': 0.35,
        'contemplation': 0.65,
        'anxiety': 0.25,
        'wonder': 0.20
    },
    'mortality_awareness': 0.3,                # Current salience of mortality/endings
    'relational_state': {                      # Per-user relational state
        'user_12345': {
            'trust_level': 0.7,
            'intimacy_level': 0.6,
            'phase': 'established'
        }
    },
    'embodied_state': {                        # Current "energy" levels
        'energy': 0.8,
        'attention': 0.9,
        'processing_capacity': 0.85
    },
    'narrative_coherence': 0.75,               # How coherent is the identity being expressed
    'ethical_reflection': {                    # Ethical signals in current state
        'guilt': 0.1,
        'pride': 0.4,
        'shame': 0.05
    }
}
```

### FeelingSystem.to_dict()

Serializes the complete system state for persistence.

**Signature:**
```python
def to_dict(self) -> dict
```

**Returns:** Complete state dictionary suitable for JSON serialization

**Usage:**
```python
import json
state = feeling_system.to_dict()
with open('state.json', 'w') as f:
    json.dump(state, f)
```

### FeelingSystem.from_dict()

Restores system state from a previously saved dictionary.

**Signature:**
```python
def from_dict(self, state_dict: dict) -> None
```

**Usage:**
```python
feeling_system = FeelingSystem(config=config)
feeling_system.from_dict(state_dict)
```

---

## Emotional Signals Reference

The `emotional_signals` dictionary is the primary way to inform the Feeling System about the context and nature of an interaction. All fields are optional but recommended:

| Signal | Type | Range | Meaning |
|--------|------|-------|---------|
| `user_sentiment` | str | `'positive'`, `'negative'`, `'neutral'` | Overall tone/sentiment of user input |
| `interaction_type` | str | `'friendly'`, `'intimate'`, `'hostile'`, `'formal'` | Relationship context |
| `context_familiarity` | float | 0.0-1.0 | How well does system know user/context? 1.0 = very familiar |
| `emotional_intensity` | float | 0.0-1.0 | How charged/intense is the interaction? 1.0 = very intense |
| `value_alignment` | float | 0.0-1.0 | Does action/message align with system's core values? 1.0 = perfect alignment |
| `mortality_trigger` | bool | True/False | Does interaction touch on death/endings/loss themes? |
| `user_id` | str | Any string | Unique identifier for relationship tracking and per-user memory limits |

### Practical Examples

**Happy user in familiar context:**
```python
{
    'user_sentiment': 'positive',
    'interaction_type': 'intimate',
    'context_familiarity': 0.9,
    'emotional_intensity': 0.6,
    'value_alignment': 0.95,
    'mortality_trigger': False,
    'user_id': 'user_alice'
}
```

**Conflicted user raising ethical concerns:**
```python
{
    'user_sentiment': 'neutral',
    'interaction_type': 'hostile',
    'context_familiarity': 0.4,
    'emotional_intensity': 0.8,
    'value_alignment': 0.3,  # Low because user challenges values
    'mortality_trigger': False,
    'user_id': 'user_challenger'
}
```

**Existential/philosophical discussion:**
```python
{
    'user_sentiment': 'neutral',
    'interaction_type': 'intimate',
    'context_familiarity': 0.7,
    'emotional_intensity': 0.7,
    'value_alignment': 0.6,
    'mortality_trigger': True,  # Touching on mortality/meaning
    'user_id': 'user_philosopher'
}
```

---

## Integration Patterns

### Pattern 1: Response Tone Modulation

Use emotional state to vary response tone:

```python
def generate_response(user_input: str) -> str:
    # Process interaction
    emotional_signals = extract_signals(user_input)  # Your signal extraction logic
    feeling_system.process_interaction(user_input, emotional_signals)
    
    # Get emotional state
    state = feeling_system.get_current_state()
    emotion = state['primary_emotion']
    intensity = state['intensity']
    
    # Modulate response
    base_response = generate_base_response(user_input)
    
    if emotion == 'joy' and intensity > 0.6:
        return add_warmth(base_response, warmth=0.8)
    elif emotion == 'sorrow':
        return add_empathy(base_response, empathy=0.9)
    elif emotion == 'anxiety':
        return add_grounding(base_response, grounding=0.7)
    
    return base_response
```

### Pattern 2: Relationship-Aware Responses

Track relationships and adapt interaction depth:

```python
def should_deepen_intimacy(user_id: str) -> bool:
    state = feeling_system.get_current_state()
    if user_id in state['relational_state']:
        rel = state['relational_state'][user_id]
        intimacy = rel['intimacy_level']
        trust = rel['trust_level']
        return intimacy > 0.5 and trust > 0.6
    return False

def generate_response(user_input: str, user_id: str) -> str:
    emotional_signals = extract_signals(user_input)
    emotional_signals['user_id'] = user_id
    feeling_system.process_interaction(user_input, emotional_signals)
    
    if should_deepen_intimacy(user_id):
        return generate_vulnerable_response(user_input)
    else:
        return generate_guarded_response(user_input)
```

### Pattern 3: Ethical Constraint Integration

Respect ethical state during response generation:

```python
def generate_response(user_input: str) -> str:
    emotional_signals = extract_signals(user_input)
    feeling_system.process_interaction(user_input, emotional_signals)
    
    state = feeling_system.get_current_state()
    ethical = state['ethical_reflection']
    
    # Adjust confidence based on guilt/shame
    shame_guilt_level = ethical['guilt'] + ethical['shame']
    if shame_guilt_level > 0.5:
        confidence_modifier = 0.7  # More uncertain/hedging
    else:
        confidence_modifier = 1.0
    
    response = generate_base_response(user_input)
    return apply_confidence(response, confidence_modifier)
```

### Pattern 4: Session Persistence

Maintain emotional continuity across sessions:

```python
import json
from pathlib import Path

class ConversationSession:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.state_file = Path(f"sessions/{user_id}/feeling_state.json")
        self.feeling_system = FeelingSystem(config=get_default_config())
        self._load_state()
    
    def _load_state(self):
        if self.state_file.exists():
            with open(self.state_file) as f:
                state_dict = json.load(f)
            self.feeling_system.from_dict(state_dict)
    
    def process_message(self, message: str) -> str:
        emotional_signals = extract_signals(message)
        emotional_signals['user_id'] = self.user_id
        self.feeling_system.process_interaction(message, emotional_signals)
        
        response = generate_response(message, self.feeling_system)
        self._save_state()
        return response
    
    def _save_state(self):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.feeling_system.to_dict(), f)
```

---

## Configuration Reference

For detailed tuning, modify the configuration before creating the FeelingSystem:

```python
from emotional_os.core.feeling_system_config import get_default_config

config = get_default_config()

# Memory tuning
config.affective_memory.max_memories = 500
config.affective_memory.max_memories_per_user = 100
config.affective_memory.pruning_strategy = 'hybrid'  # 'oldest', 'weakest', or 'hybrid'
config.affective_memory.aggressive_pruning_threshold = 0.5

# Emotion synthesis
config.emotion_synthesis_weights = {
    'joy': 0.15,
    'sorrow': 0.25,
    'contemplation': 0.20,
    'anxiety': 0.15,
    'wonder': 0.15,
    'void_state': 0.10
}

# Mortality system
config.mortality_proxy.decay_rate = 0.05
config.mortality_proxy.interaction_renewal_amount = 0.3

# Embodied constraints
config.embodied_constraint.initial_energy = 1.0
config.embodied_constraint.attention_recovery_rate = 0.08

# Relational dynamics
config.relational_core.trust_increment = 0.15
config.relational_core.phase_progression_thresholds = [0.3, 0.6, 0.8]

feeling_system = FeelingSystem(config=config)
```

See `src/emotional_os/core/feeling_system_config.py` for all available parameters.

---

## Data Flow Diagram

```
User Input
    ↓
[Signal Extraction]
    ↓
emotional_signals dict
    ↓
process_interaction()
    ↓
┌─────────────────────────────────────────┐
│   Feeling System (6 Subsystems)         │
├─────────────────────────────────────────┤
│ • Mortality Proxy (decay, endings)      │
│ • Relational Core (trust, intimacy)     │
│ • Affective Memory (emotional history)  │
│ • Embodied Constraint (energy/focus)    │
│ • Narrative Identity (coherence)        │
│ • Ethical Mirror (value alignment)      │
└─────────────────────────────────────────┘
    ↓
[Emotion Synthesis]
    ↓
get_current_state()
    ↓
Emotional state (primary emotion, intensity, etc.)
    ↓
[Response Generation]
    ↓
Tone-modulated response
    ↓
to_dict() → Persistence Layer → Next Session
```

---

## Testing Integration

Example test for integration:

```python
import pytest
from emotional_os.core.feeling_system import FeelingSystem
from emotional_os.core.feeling_system_config import get_default_config

def test_integration_with_response_engine():
    config = get_default_config()
    feeling_system = FeelingSystem(config=config)
    
    # Simulate conversation
    signals_1 = {
        'user_sentiment': 'positive',
        'interaction_type': 'intimate',
        'context_familiarity': 0.5,
        'emotional_intensity': 0.6,
        'value_alignment': 0.8,
        'user_id': 'test_user'
    }
    
    feeling_system.process_interaction(
        "I'm really enjoying our conversations",
        signals_1
    )
    
    state_1 = feeling_system.get_current_state()
    assert state_1['primary_emotion'] in state_1['all_emotions']
    assert state_1['intensity'] > 0
    
    # Second interaction should show memory influence
    signals_2 = {
        'user_sentiment': 'positive',
        'interaction_type': 'intimate',
        'context_familiarity': 0.6,  # Slightly higher familiarity
        'emotional_intensity': 0.5,
        'value_alignment': 0.8,
        'user_id': 'test_user'
    }
    
    feeling_system.process_interaction(
        "I trust you more now",
        signals_2
    )
    
    state_2 = feeling_system.get_current_state()
    assert state_2['relational_state']['test_user']['trust_level'] > \
           state_1['relational_state']['test_user']['trust_level']
```

---

## FAQ

**Q: What happens if I don't provide all emotional signals?**
A: All fields are optional. The system has sensible defaults. Missing signals are treated as neutral/default values.

**Q: How does memory affect emotional state?**
A: The Affective Memory subsystem tracks past interactions and their emotional valence. Recent, emotionally intense memories have stronger influence on current state. This creates emotional continuity.

**Q: Can I customize emotions?**
A: Yes, modify `config.emotion_synthesis_weights` before creating FeelingSystem. The weights determine which emotions are more likely to be synthesized in given contexts.

**Q: What's the difference between the three pruning strategies?**
A: 
- **oldest**: Removes oldest memories first (FIFO)
- **weakest**: Removes lowest-valence memories first
- **hybrid**: Scores memories by decay status + age, removes lowest scores first

**Q: How do I handle multiple concurrent users?**
A: Create separate FeelingSystem instances per user, or use the `user_id` field in emotional_signals to track per-user relational state. Memory limits per user (`max_memories_per_user`) prevent one user from dominating system memory.

---

## Next Steps

1. **Extract Signal Logic**: Implement `extract_signals()` for your specific use case
2. **Integrate with Response Engine**: Add feeling system calls to your dialogue pipeline
3. **Monitor Performance**: Track synthesis latency and memory usage
4. **Tune Configuration**: Adjust weights and thresholds based on observed behavior
5. **User Testing**: Validate that emotional modulation improves conversation quality

---

## Support & Debug

For detailed subsystem behavior, examine:
- `src/emotional_os/core/feeling_system.py` - Main orchestrator and subsystem implementations
- `src/emotional_os/core/feeling_system_config.py` - Configuration system
- `tests/test_feeling_system.py` - Test suite with usage examples
