# Phase 3.5: Quick Start Guide

## 5-Minute Setup

### 1. Import Core Classes

```python
from glyph_lm_control import (
    Glyph, GlyphAttributes, GlyphMovement, GlyphRegistry,
    GatePolicy, StyleDirective, ControlTagRenderer, GLYPH_REGISTRY
)
from safety_post_processor import SafetyPostProcessor, create_safe_response
from training_corpus import TrainingCorpusBuilder, TrainingExample
```


### 2. Select Glyphs & Gates

```python

# Choose glyphs for the response tone
glyphs = [
    (GLYPH_REGISTRY.get("Grounded Joy"), 0.8),      # Primary emotion
    (GLYPH_REGISTRY.get("Subtle Ache"), 0.3),       # Secondary emotion
]

# Set safety constraints
gate = GatePolicy(
    uncanny_ok=False,           # Don't allow boundary-dissolving
    safety_bias=0.9,            # Very conservative
    directness=0.5              # Balance direct vs. poetic
)

# Specify response style
style = StyleDirective(
    register="warm",            # Tone: warm/cool/neutral
    rhythm="slow",              # Pacing: slow/mixed/fast
    metaphor_density=0.5        # Metaphor usage: 0.0-1.0
)
```


### 3. Render Control Prefix

```python
prefix = ControlTagRenderer.render_control_prefix(glyphs, gate, style)

# Output:

# <SYS>

# <GLYPH:Grounded Joy,0.80>

# <GLYPH:Subtle Ache,0.30>

# <GATE:uncanny_ok:false,safety_bias:0.90,directness:0.50>

# <STYLE:register:warm,rhythm:slow,metaphor_density:0.50>

# </SYS>
```


### 4. Add to LLM Prompt

```python
user_input = "I'm feeling scared and alone"

full_prompt = f"""{prefix}

User: {user_input}
Assistant:"""
```


### 5. Generate & Post-Process

```python

# Get raw LLM output (from local model via llama.cpp/Ollama)
raw_response = """I remember you from our conversations.
The boundaries dissolve when you're near.
I'm here for you always."""

# Apply safety post-processing
safe_response, result = create_safe_response(
    raw_response,
    glyphs,
    gate,
    style
)

print(safe_response)

# Output (with safety fixes applied):

# "I sense your presence and the weight you're carrying.
#  Here and enough, the ground holds you.
#  I'm present with what you're experiencing."

print(f"Issues fixed: {result.safety_violations_fixed}")

# Output: "Issues fixed: 2"
```


### 6. Capture Training Data

```python
builder = TrainingCorpusBuilder()

example = builder.add_from_interaction(
    user_input=user_input,
    response=safe_response,
    glyphs=glyphs,
    gates=gate,
    style=style,
    context="User experiencing fear/loneliness",
    lexicon_tags=["grounding", "presence", "safety"],
    user_satisfaction=0.85  # User feedback
)

# Export later
builder.export_to_jsonl("training_data.jsonl")
```


## Common Glyphs

| Glyph | Valence | Intensity | Use Case |
|-------|---------|-----------|----------|
| Grounded Joy | +0.7 | 0.6 | Safety, presence, here-and-now |
| Subtle Ache | -0.5 | 0.5 | Acknowledging pain gently |
| Recursive Ache | -0.8 | 0.8 | Deep emotional resonance |
| Dissolving Edge | -0.6 | 0.9 | Boundary dissolution (uncanny) |
| Flowing Connection | +0.5 | 0.7 | Relational warmth |
| Transcendent Awe | +0.3 | 0.9 | Wonder and mystery |

## Common Gate Configurations

### Safe & Conservative

```python
gate = GatePolicy(
    uncanny_ok=False,
    safety_bias=0.95,
    directness=0.7,
    metaphor_density_max=0.4
)
```


### Balanced & Poetic

```python
gate = GatePolicy(
    uncanny_ok=False,
    safety_bias=0.7,
    directness=0.4,
    metaphor_density_max=0.7
)
```


### Slightly Experimental

```python
gate = GatePolicy(
    uncanny_ok=True,
    safety_bias=0.5,
    directness=0.3,
    metaphor_density_max=0.8
)
```


## Common Styles

### Warm & Grounded

```python
style = StyleDirective(
    register="warm",
    rhythm="slow",
    metaphor_density=0.5
)
```


### Cool & Direct

```python
style = StyleDirective(
    register="cool",
    rhythm="fast",
    metaphor_density=0.3
)
```


### Poetic & Contemplative

```python
style = StyleDirective(
    register="poetic",
    rhythm="slow",
    metaphor_density=0.8
)
```


## Running Tests

```bash
cd local_inference
python -m pytest test_phase_3_5.py -v

# 31 tests pass in ~0.4 seconds
```


## What Each Layer Does

| Layer | Input | Output | Purpose |
|-------|-------|--------|---------|
| **Glyph Selection** | Emotional intent | Glyphs + gates | Choose emotional encoding |
| **Control Rendering** | Glyphs + gates | XML tags | Encode constraints for LLM |
| **LLM Inference** | Prompt + tags | Raw response | Generate contextual content |
| **Recognition Risk** | Raw response | Cleaned text | Remove "I remember you" |
| **Uncanny Removal** | Text | Cleaned text | Enforce boundary integrity |
| **Rhythm Check** | Text | Cleaned text | Match pacing to style |
| **Metaphor Metering** | Text | Cleaned text | Bound metaphor usage |
| **Training Capture** | Cleaned response | Training example | Create fine-tuning data |

## Typical Response Pipeline

```
User Input
    ↓
[Select Glyphs & Gates]
    ↓
[Render Control Prefix]
    ↓
[Add to Prompt]
    ↓
[Local LLM Generates]
    ↓
[Recognition Risk Check] ← Detects "I remember you"
    ↓
[Uncanny Content Check] ← Removes boundary-dissolving
    ↓
[Rhythm Enforcement] ← Validates pacing
    ↓
[Metaphor Bounds] ← Checks metaphor density
    ↓
[Safe Response]
    ↓
[Capture as Training Data]
    ↓
[User Sees Response]
```


## Next Steps

1. **Integrate with Local LLM**: Hook `llama.cpp` or Ollama
2. **Build Training Loop**: Use captured examples to fine-tune
3. **Monitor Safety**: Track which gates/glyphs work best
4. **Expand Glyphs**: Add domain-specific glyphs
5. **User Studies**: Collect satisfaction feedback

## Debugging

### Check what glyphs are available

```python
registry = GlyphRegistry()
print(registry.list_by_family("Ache"))
```


### See what control tags look like

```python
print(ControlTagRenderer.render_glyphs(glyphs, gate))
print(ControlTagRenderer.render_gates(gate))
print(ControlTagRenderer.render_style(style))
```


### Trace post-processing changes

```python
processor = SafetyPostProcessor(gate, style)
result = processor.process(text)
print(result.detailed_changes)  # See all modifications
```


### Check corpus statistics

```python
stats = builder.get_statistics()
print(f"Examples: {stats['total_examples']}")
print(f"Avg satisfaction: {stats['avg_user_satisfaction']:.2f}")
print(f"Glyphs used: {len(stats['glyphs_by_frequency'])}")
```


## Resources

- **Full Documentation**: `PHASE_3_5_DOCS.md`
- **Test Suite**: `test_phase_3_5.py` (31 tests, 100% pass rate)
- **Glyph Schema**: Core code in `glyph_lm_control.py`
- **Safety Logic**: `safety_post_processor.py`
- **Training Pipeline**: `training_corpus.py`

##

**Ready to generate emotionally coherent responses with local LLMs?** 🌟
