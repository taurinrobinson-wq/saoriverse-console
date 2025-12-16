# Dialogue System Integration Quick Start

## Installation

The dialogue system is part of the REMNANTS engine. No additional dependencies needed beyond the
core system.

**Files:**
- `velinor/engine/npc_dialogue.py` — Lexicons + dialogue generation
- `velinor/engine/npc_encounter.py` — Encounter + scene generation
- `velinor/stories/test_dialogue_generation.py` — Test suite
## 

## Basic Usage

### 1. Generate Single NPC Dialogue

```python
from velinor.engine.npc_manager import NPCManager, create_marketplace_npcs
from velinor.engine.npc_dialogue import generate_dialogue

# Initialize system
manager = NPCManager()
manager.add_npcs_batch(create_marketplace_npcs())

# Get an NPC
sera = manager.get_npc("Sera")

# Generate dialogue
dialogue = generate_dialogue("Sera", sera.remnants, context="greeting")
print(dialogue)

# Output: "I see sprout in you.... like herbs, it blooms so softly."
```


### 2. Generate Player Choices

```python
from velinor.engine.npc_dialogue import generate_choices

choices = generate_choices("Sera", sera.remnants, num_choices=3)

for choice in choices:
    print(f"[{choice['trait']}] {choice['text']}")

# Output:

# [empathy] Listen deeply.

# [need] Ask for help.

# [nuance] Perhaps find middle ground.
```


### 3. Generate Full Encounter

```python
from velinor.engine.npc_encounter import generate_encounter, print_encounter

encounter = generate_encounter("Sera", sera.remnants, encounter_id=1, context="greeting")
print_encounter(encounter, full_details=True)

# Output:

# ======================================================================

# ENCOUNTER #1 - SERA

# ======================================================================

# Sera turns to face you, curious.

# I see sprout in you.... like herbs, it blooms so softly.

# Your Choices:
#   1. [EMPATHY] [########--] Listen deeply.
#   2. [NEED] [########--] Ask for help.
#   3. [NUANCE] [######----] Perhaps find middle ground.
```


### 4. Generate Full Scene (All NPCs)

```python
from velinor.engine.npc_encounter import generate_scene, print_scene

npcs_dict = {name: npc.remnants for name, npc in manager.npcs.items()}
scene = generate_scene(npcs_dict, encounter_id=1, context="greeting")

print_scene(scene, summary_only=True)

# Output shows all 9 NPCs' reactions to player
```

## 

## Integration Patterns

### Pattern A: Simple Story Beat

```python
def story_beat_marketplace_greeting():
    """Player enters marketplace and talks to Sera."""
    from velinor.engine.npc_encounter import generate_encounter, print_encounter

    manager = NPCManager()
    manager.add_npcs_batch(create_marketplace_npcs())
    sera = manager.get_npc("Sera")

    encounter = generate_encounter("Sera", sera.remnants, 1, "greeting")
    print_encounter(encounter)

    # Game waits for player choice...
    return encounter['choices']
```


### Pattern B: Decision → Trait Shift → New Dialogue

```python
def player_makes_choice(choice_trait):
    """Player picks a choice, NPCs react based on TONE effect."""
    from velinor.engine.npc_encounter import generate_scene

    # Simulate player choice as TONE effect
    # (e.g., choosing empathy adds empathy TONE)
    tone_effect = {choice_trait: 0.15}
    manager.apply_tone_effects(tone_effect)

    # Generate new scene with updated traits
    npcs_dict = {name: npc.remnants for name, npc in manager.npcs.items()}
    new_scene = generate_scene(npcs_dict, encounter_id=2, context="alliance")

    # Show all NPCs' updated reactions
    for encounter in new_scene['npcs']:
        print(f"{encounter['npc']}: {encounter['dialogue']}")
```


### Pattern C: Dialogue Sequence (5+ turns)

```python
def dialogue_sequence_kaelen_redemption():
    """Multi-turn dialogue showing Kaelen's transformation."""
    from velinor.engine.npc_encounter import generate_encounter

    manager = NPCManager()
    manager.add_npcs_batch(create_marketplace_npcs())
    kaelen = manager.get_npc("Kaelen")

    encounters = []
    contexts = ["greeting", "conflict", "alliance", "resolution"]
    tones = [
        {"empathy": 0.1},
        {"empathy": 0.15},
        {"empathy": 0.1, "trust": 0.15},
    ]

    for i, (context, tone) in enumerate(zip(contexts, tones), 1):
        manager.apply_tone_effects(tone)
        kaelen = manager.get_npc("Kaelen")

        encounter = generate_encounter("Kaelen", kaelen.remnants, i, context)
        encounters.append(encounter)

        print(f"\n[{context.upper()}]")
        print(f"Kaelen: {encounter['dialogue']}")
        print(f"Your choices: {[c['text'] for c in encounter['choices']]}")

    return encounters
```


### Pattern D: Game Engine Hook

```python
class GameEngine:
    def __init__(self):
        self.manager = NPCManager()
        self.manager.add_npcs_batch(create_marketplace_npcs())
        self.current_scene_id = 1

    def player_encounters_npc(self, npc_name, context="greeting"):
        """Hook for game engine to generate NPC dialogue."""
        from velinor.engine.npc_encounter import generate_encounter, print_encounter

        npc = self.manager.get_npc(npc_name)
        encounter = generate_encounter(npc_name, npc.remnants, self.current_scene_id, context)

        print_encounter(encounter)
        self.current_encounter = encounter

        return encounter

    def player_chooses(self, choice_index):
        """Hook: player picks a choice, update TONE + regenerate."""
        choice = self.current_encounter['choices'][choice_index]
        trait = choice['trait']

        # Apply as TONE effect
        tone_effect = {trait: 0.15}
        self.manager.apply_tone_effects(tone_effect)
        self.current_scene_id += 1

    def get_full_scene_snapshot(self):
        """Get all NPCs' current state + dialogue."""
        from velinor.engine.npc_encounter import generate_scene

        npcs_dict = {name: npc.remnants for name, npc in self.manager.npcs.items()}
        scene = generate_scene(npcs_dict, self.current_scene_id, "greeting")

        return scene

# Usage in game loop:

# engine = GameEngine()

# engine.player_encounters_npc("Sera", "greeting")

# # Player picks choice

# engine.player_chooses(0)  # Picks first choice (empathy)

# engine.player_encounters_npc("Sera", "alliance")  # Updated dialogue
```

## 

## Customization

### Add New Trait Lexicon Entry

```python
from velinor.engine.npc_dialogue import LEXICONS

# Add to existing NPC
LEXICONS["Sera"]["authority_high"] = ["guide", "lead", "inspire"]
LEXICONS["Sera"]["authority_low"] = ["defer", "follow", "obey"]
```


### Modify Temperament

```python
from velinor.engine.npc_dialogue import temperaments

def sera_custom_temperament(text):
    """More poetic version of Sera's voice."""
    return f"Sera whispers: {text} (as if speaking to roots and rain)"

temperaments["Sera"] = sera_custom_temperament
```


### Add Context Template

```python
from velinor.engine.npc_encounter import ENCOUNTER_CONTEXTS

ENCOUNTER_CONTEXTS["mystery"] = {
    "templates": [
        "{npc} emerges from the shadows.",
        "There's something strange about {npc}'s manner.",
    ]
}

# Now use: generate_encounter("Sera", remnants, 1, "mystery")
```

## 

## Output Examples

### High-Trust Ravi (Merchant)

```
Ravi says: I see believe in in you., spoken with warm merchant confidence.

Your choices:
- [RESOLVE] Stand firm.
- [AUTHORITY] Lead decisively.
- [TRUST] Offer your faith.
```


### Low-Trust Drossel (Thief Leader)

```
Drossel says: I see shadow in you., mon cher — but shadows linger.

Your choices:
- [SKEPTICISM] Doubt openly.
- [AUTHORITY] Command action.
- [RESOLVE] Perhaps hold your ground.
```


### Sera After Redemption (High Empathy)

```
Sera says: I see bloom in you.... like herbs, it blooms so softly.

Your choices:
- [EMPATHY] Listen deeply.
- [NEED] Ask for help.
- [NUANCE] Perhaps find middle ground.
```

## 

## Debugging

### Check NPC State

```python
npc = manager.get_npc("Sera")
print(npc.to_dict())

# Output:

# {
#     'name': 'Sera',
#     'remnants': {
#         'resolve': 0.3,
#         'empathy': 0.8,
#         'memory': 0.5,
#         'nuance': 0.5,
#         'authority': 0.4,
#         'need': 0.8,
#         'trust': 0.6,
#         'skepticism': 0.3
#     }

# }
```


### Generate Dialogue Without Encounter

```python
from velinor.engine.npc_dialogue import generate_dialogue

dialogue = generate_dialogue("Sera", npc.remnants)
print(f"Raw dialogue: {dialogue}")
```


### Check Dominant Trait

```python
dominant_trait, value = max(npc.remnants.items(), key=lambda x: x[1])
print(f"Dominant trait: {dominant_trait} ({value})")
```

## 

## Testing Workflow

```bash

# Run comprehensive test suite
python velinor/stories/test_dialogue_generation.py

# Run individual test
python -c "
from velinor.stories.test_dialogue_generation import test_dialogue_variety
test_dialogue_variety()
"
```

## 

## Common Patterns

### "How do I make Kaelen feel guilty?"

```python
kaelen.adjust_trait("empathy", 0.3)  # Raises empathy
kaelen.adjust_trait("trust", 0.2)    # Raises trust

# Lexicon shifts from "scheme/trick" to "redeem/listen"
```


### "How do I make Nima skeptical?"

```python
nima.adjust_trait("skepticism", 0.3)  # Already high
nima.adjust_trait("trust", -0.2)       # Lower trust

# Lexicon shifts to "shadow/hidden truth"
```


### "How do I make Sera bold?"

```python
sera.adjust_trait("resolve", 0.3)   # Raise resolve
sera.adjust_trait("authority", 0.2) # Raise authority

# Changes dominant trait → different lexicon selection
```

## 

## Performance Notes

- **Per dialogue call:** ~1ms (negligible)
- **Per scene (9 NPCs):** ~10ms
- **Memory:** Lexicons loaded once, ~20KB total
- **Scaling:** Supports unlimited NPCs (just add lexicon)

No performance bottleneck for real-time game use.
## 

## Next Steps

1. **Hook into game loop** — Use Pattern D (Game Engine) as starting point 2. **Add new NPCs** —
Create lexicon + temperament, plug into manager 3. **Implement TTS** — Feed dialogue strings to
speech synthesis 4. **Create save system** — Persist NPC remnants to load previous state 5. **Build
branching story** — Use contexts to guide narrative flow
