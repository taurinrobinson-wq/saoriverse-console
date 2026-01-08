# Auto-Generated Dialogue System Documentation

## Overview

The **Auto-Generated Dialogue System** extends the REMNANTS engine to create **emergent,
trait-driven NPC dialogue and player choices**. Instead of hand-scripting every dialogue branch,
each NPC has:

1. **Lexicon Pool** — Vocabulary tied to their personality 2. **Temperament Decorator** — Stylistic
wrapper giving them unique voice 3. **Dynamic Choice Generation** — Player options shaped by NPC
state

This ensures every playthrough feels authored but never identical.
## 

## Architecture

### 1. **Lexicon Pools** (`npc_dialogue.py`)

Each NPC has a dictionary of word pools keyed to traits. High trait values pull from `_high` pool,
low from `_low`.

**Example: Sera (Herb Novice)**

```python
"Sera": {
    "empathy_high": ["bloom", "soften", "sprout", "gentle", "nurture"],
    "empathy_low": ["fragile", "flicker", "fade", "wilt", "wither"],
}
```


- **High Empathy (>0.7):** Sera's language becomes warmer, growth-focused
- **Low Empathy (<0.7):** Dialogue becomes fragile, fading, uncertain

**Key Principle:** Lexicons stay consistent with NPC archetype. Sera always uses nature metaphors; Drossel always code-switches between French and Slavic.

### 2. **Temperament Decorators**

Each NPC has a stylistic wrapper function that modifies base dialogue:

```python
"Sera": lambda text: f"{text}... like herbs, it blooms so softly.",
"Drossel": lambda text: f"{text}, mon cher — but shadows linger.",
```


**Effect:**
- Same base text → different flavor per NPC
- Decorators can vary slightly based on trait state
  - Drossel with high trust: "mon cher — a deal is a deal."
  - Drossel with low trust: "mon cher — but shadows linger."

### 3. **Trait Mapping**

Each NPC maps which REMNANTS traits drive their dialogue variation:

| NPC | Primary Traits | Lexicon Driver |
|-----|---------------|-----------------|
| **Sera** | Empathy, Need, Trust | Empathy (high = bloom, low = fragile) |
| **Drossel** | Trust, Authority, Memory | Trust (high = mon ami, low = bratva) |
| **Kaelen** | Empathy, Need, Trust | Empathy (high = redeem, low = scheme) |
| **Mariel** | Memory, Empathy, Nuance | Memory (high = remember, low = forget) |
| **Nima** | Skepticism, Memory, Nuance | Skepticism (high = shadow, low = clarity) |
## 

## Core Functions

### `generate_dialogue(npc_name, remnants, context)`

Generates contextual NPC dialogue based on current REMNANTS state.

**Parameters:**
- `npc_name` (str): "Sera", "Drossel", etc.
- `remnants` (dict): Current trait values {empathy: 0.8, need: 0.7, ...}
- `context` (str): "neutral", "greeting", "conflict", "resolution"

**Returns:** Dialogue string

**Example Usage:**

```python
sera = manager.get_npc("Sera")
dialogue = generate_dialogue("Sera", sera.remnants, context="greeting")

# Output: "I see sprout in you.... like herbs, it blooms so softly."
```


**How it works:**
1. Find dominant trait (highest REMNANTS value) 2. Look up that trait's lexicon pool (high if >0.7,
low otherwise) 3. Pick random word from pool 4. Build contextual template ("I see {word} in you" for
greeting) 5. Apply temperament decorator (Sera's nature-soft wrapper)

### `generate_choices(npc_name, remnants, num_choices=3)`

Generate player dialogue options shaped by NPC's current state.

**Returns:** List of choice dicts

```python
[
    {"trait": "empathy", "value": 0.8, "text": "Listen deeply."},
    {"trait": "need", "value": 0.7, "text": "Ask for help."},
    {"trait": "nuance", "value": 0.6, "text": "Perhaps find middle ground."}
]
```


**Confidence-Based Choice Phrasing:**
- High (>0.7): Direct imperative — "Show compassion."
- Medium (0.5-0.7): Tentative — "Perhaps listen deeply."
- Low (<0.5): Reflective — "Consider: listen deeply."

### `generate_encounter(npc_name, remnants, encounter_id, context)`

Build complete encounter: intro + dialogue + choices.

**Returns:**

```python
{
    "encounter_id": 1,
    "npc": "Sera",
    "context": "greeting",
    "intro": "Sera turns to face you, curious.",
    "dialogue": "I see sprout in you.... like herbs, it blooms so softly.",
    "choices": [
        {"trait": "empathy", "value": 0.8, "text": "Listen deeply."},
        ...
    ],
    "dialogue_meta": {
        "dominant_trait": "empathy",
        "dominant_value": 0.8
    }
}
```


### `generate_scene(npcs_dict, encounter_id, context)`

Generate encounter data for **all NPCs** in current scene.

Useful for showing entire marketplace reaction to player choice.

**Returns:**

```python
{
    "scene_id": 1,
    "context": "greeting",
    "npcs": [encounter1, encounter2, ...],  # All 9 NPCs
    "dominant_mood": "empathy"  # Most common dominant trait
}
```

## 

## Integration with NPCManager

### Using in `simulate_encounters()`

Extend your manager to include dialogue + choices in encounter history:

```python
class NPCManager:
    ...
    def simulate_encounters_with_dialogue(self, encounters: List[Dict[str, float]]) -> List[Dict]:
        from velinor.engine.npc_encounter import generate_scene

        self.history = []

        for i, tone_effects in enumerate(encounters, start=1):
            self.apply_tone_effects(tone_effects)

            npcs_dict = {name: npc.remnants for name, npc in self.npcs.items()}
            scene = generate_scene(npcs_dict, i, context="neutral")

            snapshot = {
                "encounter": i,
                "tone_effects": tone_effects,
                "npc_profiles": {name: npc.to_dict() for name, npc in self.npcs.items()},
                "scene": scene
            }
            self.history.append(snapshot)

        return self.history
```

## 

## Examples

### Example 1: Sera's Dialogue Transformation

**Initial State (High Empathy):**

```
Ser: My empathy feels bloom.... like herbs, it blooms so softly.
```


**After Empathy Drop (Low Empathy):**

```
Sera: My need feels fragile.... like herbs, it fades to shadow.
```


Same base mechanism, completely different flavor.
## 

### Example 2: Kaelen Redemption Arc

**Hostile State (Low Empathy, Low Trust):**

```
Kaelen: I see a path in you.... said with a sly, calculating grin.

Your Choices:
  1. [SKEPTICISM] Question their motives.
  2. [NEED] Perhaps seek connection.
```


**After Redemption (High Empathy, High Trust):**

```
Kaelen: I see redeem in you.... said with genuine remorse.

Your Choices:
  1. [EMPATHY] Listen deeply.
  2. [NEED] Ask for help.
```


The mechanics stay identical; only the generated lexicon + confidence change.
## 

### Example 3: Multi-NPC Scene

```python
manager = NPCManager()
manager.add_npcs_batch(create_marketplace_npcs())
npcs_dict = {name: npc.remnants for name, npc in manager.npcs.items()}

scene = generate_scene(npcs_dict, encounter_id=1, context="greeting")

# Outputs all 9 NPCs reacting to player presence
for encounter in scene['npcs']:
    print(f"{encounter['npc']}: {encounter['dialogue']}")

# Marketplace mood is determined by most common trait
print(f"Overall mood: {scene['dominant_mood'].upper()}")
```

## 

## Customizing Lexicons

To add/modify an NPC's vocabulary:

### 1. **Existing NPC — Add New Trait Pair**

In `npc_dialogue.py`:

```python
LEXICONS["Sera"]["authority_high"] = ["guide", "lead", "direct"]
LEXICONS["Sera"]["authority_low"] = ["defer", "follow", "listen"]
```


### 2. **New NPC — Full Lexicon**

```python
LEXICONS["NewNPC"] = {
    "description": "Role + archetype",
    "empathy_high": [...],
    "empathy_low": [...],
    # Add trait pairs as needed
}

temperaments["NewNPC"] = lambda text: f"{text}, custom style here."
```


### 3. **Trait-Specific Fallback**

If an NPC doesn't have a lexicon entry for a trait, the system uses generic fallback:

```python
["something", "a path", "a moment"]
```

## 

## How Context Shapes Dialogue

The `context` parameter changes the dialogue template:

| Context | Template |
|---------|----------|
| `greeting` | "I see {word} in you." |
| `alliance` | "You ask {npc} to join you." |
| `conflict` | "I feel {word} between us now." |
| `resolution` | "Maybe we've found {word} in each other." |

**Same lexicon, different narrative frame:**
- Greeting: "I see bloom in you."
- Resolution: "Maybe we've found bloom in each other."
## 

## Design Patterns

### Pattern 1: Redemption Arc

```python

# Initial state: antagonistic
kaelen.adjust_trait("empathy", -0.3)   # Drop empathy
kaelen.adjust_trait("trust", -0.3)     # Drop trust

# After player choices: redemptive
kaelen.adjust_trait("empathy", 0.5)    # Raise empathy
kaelen.adjust_trait("trust", 0.4)      # Raise trust

# Dialogue automatically shifts from "scheme/trick" to "redeem/listen"
```


### Pattern 2: Authority Shift

```python

# Novice state: uncertain
npc.adjust_trait("authority", -0.2)

# After player empowerment: confident
npc.adjust_trait("authority", 0.3)

# Choices shift from tentative to assertive
```


### Pattern 3: Memory-Based Dialogue

```python

# Fresh state: low memory
npc.adjust_trait("memory", 0.3)

# Dialogue: "I forget... something fades."

# After historical revelation: high memory
npc.adjust_trait("memory", 0.8)

# Dialogue: "I remember... weave the threads together."
```

## 

## Performance Considerations

- **Dialogue Generation:** O(1) — single random choice from pool
- **Scene Generation:** O(9) — 9 NPCs per scene
- **Per Playthrough:** ~50 dialogues/scene × 5-10 scenes = 250-500 calls (negligible)

All generation is **deterministic** given same trait values + seed, enabling consistent testing.
## 

## Testing

Run the comprehensive test suite:

```bash
python velinor/stories/test_dialogue_generation.py
```


Tests included: 1. **Dialogue Variety** — Same NPC, trait changes → different lexicon 2. **Full
Encounters** — Complete scene with intro + dialogue + choices 3. **Scene Generation** — All 9 NPCs
react together 4. **Playstyle Evolution** — Aggressive vs. Empathetic runs produce different
dialogue 5. **Choice Reflection** — Player menu adapts to NPC state 6. **Encounter Sequence** —
Multi-turn dialogue evolution 7. **Lexicon Consistency** — Each NPC maintains recognizable voice 8.
**Context Variations** — Same NPC, different contexts → different templates
## 

## Future Enhancements

### 1. **Dynamic Lexicon Expansion**
Learn new words during gameplay. If player teaches Sera a plant name, add to lexicon.

### 2. **NPC Memory Integration**
Mariel (high memory) references past encounters in new dialogues.

### 3. **Ripple-Based Dialogue**
If Kaelen's redemption ripples to others, their dialogue acknowledges it.

### 4. **TTS Prosody Mapping**
Trait → speech rate, pitch, emphasis:
- High Resolve → clipped, decisive delivery
- High Empathy → slower, softer cadence
- High Skepticism → questioning tone, upward inflection

### 5. **Dialogue Branching by Trait Combination**
When multiple traits conflict (e.g., high Empathy + high Skepticism), generate dialogue that
*acknowledges the tension*.

```python

# Nima: Skeptical but learning to trust
"I doubt... but perhaps there's something here worth believing in."
```

## 

## Key Takeaways

✅ **Emergent without Random:** Dialogue feels organic, not dice-roll based ✅ **Replayability:**
Different trait paths → completely different conversations ✅ **Authorial Voice:** Each NPC has
distinct lexicon + temperament ✅ **Scalability:** Add NPCs by adding lexicon + decorator, no
branching needed ✅ **Integration:** Works seamlessly with REMNANTS trait evolution

The system transforms trait vectors into **narrative** — every NPC evolves not just mechanically,
but linguistically.
