# Quick Reference: Choice Consequences API

## Add a Choice with Consequences

```python
story.add_choice(
    from_passage_name="current_scene",
    choice_text="What player clicks",
    to_passage_name="next_scene",
    tone_effects={
        "courage": 0.2,
        "wisdom": -0.1
    },
    npc_resonance={
        "Ravi": 0.15,
        "Nima": -0.05
    }
)
```

## Complete Choice Example

```python
story.add_choice(
    from_passage_name="market_arrival",
    choice_text="Step toward the figures",
    to_passage_name="meet_ravi_nima",
    tone_effects={
        "courage": 0.2,
        "narrative_presence": 0.15
    },
    npc_resonance={
        "Ravi": 0.1,
        "Nima": -0.1
    }
)
```

## Parameters

| Parameter | Type | Required | Example |
|-----------|------|----------|---------|
| `from_passage_name` | string | Yes | `"market_arrival"` |
| `choice_text` | string | Yes | `"Step toward them"` |
| `to_passage_name` | string | Yes | `"meet_ravi_nima"` |
| `tone_effects` | dict | No | `{"courage": 0.2}` |
| `npc_resonance` | dict | No | `{"Ravi": 0.1}` |

## TONE Attributes

- `courage` - boldness, direct action
- `wisdom` - caution, observation, patience
- `empathy` - understanding, compassion
- `observation` - paying attention, noticing
- `narrative_presence` - visibility, reputation

## Common Effect Values

```python
# Small (minor/neutral)
0.05    # 5% change

# Medium (notable)
0.15    # 15% change
0.2     # 20% change

# Large (major)
0.25    # 25% change

# Negative (drawback)
-0.1    # -10% change
-0.15   # -15% change
```

## Usage Patterns

### Aggressive Choice
```python
tone_effects={"courage": 0.2, "narrative_presence": 0.15},
npc_resonance={"Ravi": 0.1, "Nima": -0.1}
```

### Cautious Choice
```python
tone_effects={"wisdom": 0.2, "courage": -0.1},
npc_resonance={"Nima": 0.15, "Ravi": -0.1}
```

### Social/Empathetic Choice
```python
tone_effects={"empathy": 0.15},
npc_resonance={"Ravi": 0.15, "Nima": 0.1}
```

### Observant Choice
```python
tone_effects={"observation": 0.2, "wisdom": 0.1},
npc_resonance={"Nima": 0.15}
```

### Neutral/Transition
```python
# No parameters - pure navigation
```

## How Resonance Works

**Positive resonance** (+):
- Builds relationship with that NPC
- Unlocks friendly dialogue options
- NPC becomes more helpful
- Compounds over multiple aligned choices

**Negative resonance** (-):
- Damages relationship
- Locks out alliance options
- NPC becomes less cooperative
- Can lead to alternative story paths

**Threshold gating:**
```
Resonance < 0.0  → Hostile path
Resonance 0-0.2  → Neutral path
Resonance > 0.2  → Friendly path
```

## Current Story: Act 1 Mapping

### Market Arrival → 4 Choices
1. Aggressive (Ravi+, Nima-) → courage+
2. Cautious (Nima+, Ravi-) → wisdom+
3. Social (Both+) → empathy+
4. Observant (Nima+) → observation+

### Relationship Paths
- **Ravi path:** Build through directness, empathy
- **Nima path:** Build through wisdom, observation
- **Both:** Build through shared understanding

### Quest Branches
- **Thieves' Cache:** High courage, NPCs disapprove
- **Prepare:** High wisdom, NPCs approve

## JSON Structure

All choice data is stored:

```json
{
  "name": "market_arrival",
  "choices": [
    {
      "text": "Step toward the figures",
      "target": "meet_ravi_nima",
      "tone_effects": {
        "courage": 0.2,
        "narrative_presence": 0.15
      },
      "npc_resonance": {
        "Ravi": 0.1,
        "Nima": -0.1
      }
    }
  ]
}
```

## Tips

✓ Make effects match the choice narrative  
✓ Balance positive and negative effects  
✓ Use NPC preferences for consistency  
✓ Compound effects across multiple choices  
✓ Create meaningful trade-offs (courage vs wisdom)  

✗ Don't make all choices balance perfectly  
✗ Avoid effects without narrative reason  
✗ Don't ignore NPC personality in effects  
✗ Keep numbers reasonable (0.05 to 0.25)  

## Workflow

1. Write the choice text
2. Identify the narrative meaning
3. What tone does this reveal?
4. How does each NPC feel?
5. Assign appropriate values
6. Test the cumulative effect

## Full Guides

- [CHOICE_CONSEQUENCES_GUIDE.md](CHOICE_CONSEQUENCES_GUIDE.md) - Deep dive
- [SCENE_COMPOSITION_GUIDE.md](SCENE_COMPOSITION_GUIDE.md) - Backgrounds/NPCs
- [README.md](README.md) - Complete system

---

**Example: Three Paths, Different Consequences**

Same narrative point, three different choices:

```python
# Path 1: Trust immediately (Ravi)
story.add_choice(
    from_passage_name="meet_ravi",
    choice_text="Tell them everything",
    tone_effects={"empathy": 0.2},
    npc_resonance={"Ravi": 0.25}
)

# Path 2: Stay guarded (Nima)
story.add_choice(
    from_passage_name="meet_ravi",
    choice_text="Ask questions first",
    tone_effects={"wisdom": 0.2, "observation": 0.1},
    npc_resonance={"Nima": 0.25}
)

# Path 3: Leave (Kaelen)
story.add_choice(
    from_passage_name="meet_ravi",
    choice_text="Walk away",
    tone_effects={"narrative_presence": -0.1},
    npc_resonance={"Ravi": -0.15, "Nima": -0.1, "Kaelen": 0.1}
)
```

Each leads to different story progression based on resonance!
