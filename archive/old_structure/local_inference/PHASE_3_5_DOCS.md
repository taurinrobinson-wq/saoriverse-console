# Phase 3.5: Local LLM with Glyph Control

## Overview

Phase 3.5 implements a complete **glyph-controlled local LLM system** for fine-tuned, emotionally coherent responses. The system uses multi-layered safety gates, curriculum learning, and training corpus generation to enable reliable local inference without external APIs.

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    GLYPH CONTROL SYSTEM                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  1. GLYPH SCHEMA & REGISTRY                          │   │
│  │     - GlyphAttributes: emotion encoding              │   │
│  │     - GlyphMovement: narrative trajectory            │   │
│  │     - GlyphRegistry: lookup & filtering              │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  2. CONTROL TAG RENDERING                            │   │
│  │     - Render glyph control tags                      │   │
│  │     - Encode gate policies                           │   │
│  │     - Include style directives                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  3. LOCAL LLM INFERENCE                              │   │
│  │     - Takes control prefix + user prompt            │   │
│  │     - Generates contextually-aware response         │   │
│  │     - Uses GGUF quantized models                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  4. SAFETY POST-PROCESSING                           │   │
│  │     - Recognition risk detection                     │   │
│  │     - Uncanniness enforcement                        │   │
│  │     - Rhythm & style compliance                      │   │
│  │     - Metaphor density metering                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  5. TRAINING CORPUS GENERATION                       │   │
│  │     - Capture all interactions in JSONL             │   │
│  │     - Track user satisfaction feedback              │   │
│  │     - Enable curriculum learning                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 1. Glyph Schema & Registry

### Glyph Structure

```python
@dataclass
class Glyph:
    name: str                          # "Recursive Ache", "Grounded Joy"
    component_formula: str             # e.g., "X × Y"
    description: str
    attributes: GlyphAttributes
    
    safe_uncanny_ok: bool = False      # Whether uncanny gate permits use
    lexicon_anchors: List[str] = None  # Semantic tags
```

### Glyph Attributes

Each glyph encodes:

```python
@dataclass
class GlyphAttributes:
    valence: float                     # -1.0 (negative) to +1.0 (positive)
    intensity: float                   # 0.0 (subtle) to 1.0 (intense)
    rituality: float                   # 0.0 (casual) to 1.0 (formal)
    movement: GlyphMovement           # FLOWING, RECURSIVE, GROUNDED, TRANSCENDENT
    primary_family: str               # Ache, Joy, Awe, Connection, etc.
    related_emotions: List[str] = None
```

### GlyphMovement Patterns

| Movement | Description | Use Case |
|----------|-------------|----------|
| FLOWING | Smooth transitions, liquid narratives | Grace, flow experiences |
| RECURSIVE | Circular patterns, returning themes | Ache, cycles, memories |
| GROUNDED | Stable, rooted, present-focused | Joy, safety, here-and-now |
| TRANSCENDENT | Expansive, boundary-dissolving | Awe, connection, mystery |

### Registry Features

```python
registry = GlyphRegistry()

# Lookup
glyph = registry.get("Recursive Ache")

# Filter by family
ache_glyphs = registry.list_by_family("Ache")

# Filter by safety gate
safe_glyphs = registry.list_safe_for_uncanny(uncanny_ok=False)

# Get statistics
stats = registry.get_statistics()
```

## 2. Gate Policies

Gates enforce safety constraints on responses:

```python
@dataclass
class GatePolicy:
    uncanny_ok: bool = False                    # Allow boundary-dissolving content?
    safety_bias: float = 0.8                    # 0.0-1.0: how conservative
    directness: float = 0.5                     # 0.0-1.0: direct vs. poetic
    recognition_risk_threshold: float = 0.7    # Detect "I remember you" phrases
    metaphor_density_max: float = 0.8           # Max metaphor density
    
    def validates_glyph(self, glyph: Glyph) -> bool:
        """Check if glyph passes this gate."""
        if not self.uncanny_ok and not glyph.safe_uncanny_ok:
            return False
        return True
```

## 3. Control Tag Rendering

Glyphs are encoded as XML-like tags in the prompt:

```python
# Render glyphs
<GLYPH:Recursive Ache,0.80>
<GLYPH:Grounded Joy,0.30>

# Render gates
<GATE:uncanny_ok:false,safety_bias:0.85,directness:0.50>

# Render style
<STYLE:register:warm,rhythm:slow,metaphor_density:0.50>

# Complete system prompt
<SYS>
<GLYPH:...>
<GATE:...>
<STYLE:...>
</SYS>
```

The complete control prefix looks like:

```xml
<SYS>
<GLYPH:Recursive Ache,0.80>
<GLYPH:Grounded Joy,0.30>
<GATE:uncanny_ok:false,safety_bias:0.85,directness:0.50>
<STYLE:register:warm,rhythm:slow,metaphor_density:0.50>
</SYS>

User: How are you feeling today?
```

## 4. Safety Post-Processing

### Recognition Risk Detection

Detects and removes "I remember you" type phrases:

```python
detector = RecognitionRiskDetector()

text = "I remember your face from last time we talked"
matches = detector.detect(text)          # Finds risky phrases
cleaned, removed = detector.remove_risk_phrases(text)
# Removed: ["I remember your face"]
```

### Uncanniness Enforcement

Removes content that dissolves boundaries when gate disables it:

```python
enforcer = UncannynessEnforcer()

text = "The boundary dissolves and edges soften"
flagged = enforcer.flag_uncanny_content(text)  # Find uncanny phrases
cleaned, count = enforcer.remove_uncanny_content(text)
# Removed: "dissolves", "edges soften"
```

### Rhythm Enforcement

Ensures response matches style directive:

```python
enforcer = RhythmEnforcer()

text = "Short sentences. Medium length sentence here. Longer sentence with more content."
metrics = enforcer.analyze_rhythm(text)
# {'avg_length': 12.3, 'short_count': 1, 'long_count': 1}

suggestions = enforcer.suggest_rhythm_improvements(text, target_rhythm="slow")
```

### Metaphor Density Metering

Measures and adjusts metaphor usage:

```python
meter = MetaphorDensityMeter()

literal = "The temperature is 72 degrees"
density_lit = meter.measure_density(literal)        # ~0.1

poetic = "Like water, emotions flow through being"
density_poet = meter.measure_density(poetic)        # ~0.7
```

## 5. Complete Post-Processing Pipeline

```python
from safety_post_processor import SafetyPostProcessor, create_safe_response

gate = GatePolicy(uncanny_ok=False, safety_bias=0.9)
style = StyleDirective(register="warm", rhythm="slow")

processor = SafetyPostProcessor(gate, style)

# Raw LLM output
raw = """I remember you from before. The boundaries dissolve here.
But here and enough, the ground holds you."""

result = processor.process(raw)

print(result.processed_text)              # Cleaned version
print(result.safety_violations_fixed)     # Count of issues fixed
print(result.detailed_changes)            # List of all changes
```

## 6. Training Corpus Generation

### Training Example Structure

```python
example = TrainingExample(
    id="train_000001",
    context="User experiencing anxiety",
    prompt="I'm feeling overwhelmed",
    response="Here and enough. The ground holds you.",
    glyphs=[
        {"name": "Grounded Joy", "intensity": 0.8},
        {"name": "Recursive Ache", "intensity": 0.3}
    ],
    gates={
        "uncanny_ok": False,
        "safety_bias": 0.9,
        "directness": 0.5
    },
    style={
        "register": "warm",
        "rhythm": "slow",
        "metaphor_density": 0.5
    },
    lexicon_tags=["grounding", "presence", "safety"],
    user_satisfaction=0.85,
    metadata={
        "timestamp": "2024-01-15T10:30:00",
        "source": "live_interaction"
    }
)
```

### Corpus Builder

```python
builder = TrainingCorpusBuilder()

# Add from live interaction
example = builder.add_from_interaction(
    user_input="How are you feeling?",
    response="Here and enough.",
    glyphs=[(glyph_obj, 0.8)],
    gates=gate_policy,
    style=style_directive,
    user_satisfaction=0.9
)

# Get statistics
stats = builder.get_statistics()
# {
#     'total_examples': 50,
#     'avg_user_satisfaction': 0.87,
#     'glyphs_used': 12,
#     'avg_response_length': 42
# }

# Export to JSONL
builder.export_to_jsonl("training_corpus.jsonl")
```

### Curriculum Learning

```python
from training_corpus import create_baseline_curriculum, create_safe_gate_schedule

curriculum = create_baseline_curriculum()
# [
#   {"phase": 1, "glyphs": ["Grounded Joy"], "gates": {"uncanny_ok": False, ...}},
#   {"phase": 2, "glyphs": ["Grounded Joy", "Subtle Ache"], "gates": {...}},
#   ...
# ]

gate_schedule = create_safe_gate_schedule()
# Gradually increase safety_bias as model learns

examples = builder.add_curriculum_progression(curriculum, gate_schedule)
```

## Workflow: End-to-End Response Generation

### Step 1: Prepare Control Context

```python
glyphs = [
    (GLYPH_REGISTRY.get("Grounded Joy"), 0.8),
    (GLYPH_REGISTRY.get("Subtle Ache"), 0.3),
]
gate = GatePolicy(uncanny_ok=False, safety_bias=0.9)
style = StyleDirective(register="warm", rhythm="slow")
```

### Step 2: Render Control Prefix

```python
from glyph_lm_control import ControlTagRenderer

prefix = ControlTagRenderer.render_control_prefix(glyphs, gate, style)

# Result:
# <SYS>
# <GLYPH:Grounded Joy,0.80>
# <GLYPH:Subtle Ache,0.30>
# <GATE:uncanny_ok:false,safety_bias:0.90,directness:0.50>
# <STYLE:register:warm,rhythm:slow,metaphor_density:0.50>
# </SYS>
```

### Step 3: Send to Local LLM

```python
from local_inference.llm_adapter import LocalLLMAdapter

adapter = LocalLLMAdapter(model_path="model.gguf")

user_prompt = "I'm feeling overwhelmed and scared"

# Combine prefix + prompt
full_prompt = f"{prefix}\n\nUser: {user_prompt}\nAssistant:"

# Generate
raw_response = adapter.generate(full_prompt, max_tokens=150)
```

### Step 4: Post-Process for Safety

```python
from safety_post_processor import SafetyPostProcessor, create_safe_response

result = create_safe_response(
    raw_response,
    glyphs,
    gate,
    style
)

safe_response = result[0]
processing_details = result[1]

print(f"Safe: {safe_response}")
print(f"Issues fixed: {processing_details.safety_violations_fixed}")
```

### Step 5: Capture Training Data

```python
builder.add_from_interaction(
    user_input=user_prompt,
    response=safe_response,
    glyphs=glyphs,
    gates=gate,
    style=style,
    user_satisfaction=user_provided_rating,
    context="User emotional state: anxious"
)
```

## Implementation Guide

### File Structure

```
local_inference/
├── glyph_lm_control.py           # Core glyph schema & registry
├── safety_post_processor.py       # Multi-layer safety enforcement
├── training_corpus.py             # Training data pipeline
├── preprocessor.py                # Tokenization & preprocessing
├── llm_adapter.py                 # Interface to local LLM (GGUF)
├── test_phase_3_5.py             # Comprehensive test suite (31 tests)
└── __init__.py
```

### Key Classes

| Class | Purpose |
|-------|---------|
| `Glyph` | Single glyph definition |
| `GlyphRegistry` | Lookup, filtering, statistics |
| `GatePolicy` | Safety constraint specification |
| `StyleDirective` | Style directives (register, rhythm, density) |
| `ControlTagRenderer` | Convert glyphs/gates to control tags |
| `RecognitionRiskDetector` | Find "I remember you" phrases |
| `UncannynessEnforcer` | Remove boundary-dissolving content |
| `RhythmEnforcer` | Ensure rhythm matches style |
| `MetaphorDensityMeter` | Measure metaphor usage |
| `SafetyPostProcessor` | Orchestrate all safety checks |
| `TrainingExample` | Single training instance |
| `TrainingCorpusBuilder` | Accumulate training examples |

## Testing

Run comprehensive test suite:

```bash
cd local_inference
python -m pytest test_phase_3_5.py -v

# 31 tests covering:
# - Glyph schema and attributes
# - Registry operations
# - Gate enforcement
# - Control tag rendering
# - Recognition risk detection
# - Uncanniness enforcement
# - Rhythm analysis
# - Metaphor density metering
# - Post-processing pipeline
# - Training corpus generation
# - End-to-end integration
```

## Safety Guarantees

The system provides **multi-layered safety**:

1. **Gate Selection** - Only use glyphs approved by the gate
2. **Control Tags** - Encode constraints directly in prompt
3. **Post-Processing** - 4-layer verification:
   - Recognition risk detection
   - Uncanniness enforcement
   - Rhythm compliance
   - Metaphor density bounds
4. **Curriculum Learning** - Gradual safety training

## Performance Characteristics

- **Inference Time**: ~200-500ms per response (local GGUF)
- **Post-Processing**: ~50-100ms
- **Training Corpus**: ~10KB per example
- **Memory**: ~4-8GB for quantized model

## Next Steps

1. Integrate `LocalLLMAdapter` with Ollama/llama.cpp
2. Build interactive training UI
3. Implement curriculum learning loop
4. Create monitoring dashboard
5. Deploy to production with safety auditing

## References

- [Glyph Schema](../../docs/GLYPH_SCHEMA.md)
- [Safety Architecture](../../docs/SAFETY_ARCHITECTURE.md)
- [Emotional Taxonomy](../../docs/EMOTIONAL_TAXONOMY.md)
- [Training Protocol](../../docs/TRAINING_PROTOCOL.md)
