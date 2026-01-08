# REMNANTS Quick Start Guide

## What Just Happened?

When you ran the build, the system:

1. **Loaded story choices** from `story_definitions.py` (19 choices total) 2. **Extracted TONE
effects** from each choice (e.g., `{"courage": 0.2}`) 3. **Simulated NPC evolution** by applying
correlations 19 times in sequence 4. **Exported NPC state** showing final REMNANTS values

## Viewing NPC Evolution

### Final NPC State (Right Now)

Open `npc_state.json`:

```json
{
  "npc_profiles": {
    "Ravi": {
      "name": "Ravi",
      "remnants": {
        "resolve": 0.3,
        "empathy": 1.0,    ← Maxed out!
        "memory": 1.0,
        "nuance": 0.8,
        "authority": 0.2,
        "need": 1.0,       ← Maxed out!
        "trust": 1.0,
        "skepticism": 0.0
      }
    }
  }
}
```


**What this means:** Over the course of 19 story choices, Ravi became extremely empathetic, memory-focused, and needy. His Resolve and Authority dropped dramatically.

### Understanding the Summary

```
🧑‍🤝‍🧑 NPC REMNANTS Evolution:
   • Ravi: empathy: 1.00, memory: 1.00, need: 1.00
   • Nima: empathy: 1.00, memory: 1.00, need: 1.00
   • Kaelen: empathy: 1.00, memory: 1.00, need: 1.00
```


The summary shows each NPC's **top 3 dominant traits** after all story choices.

**Current issue:** All NPCs are maxing out at 1.0 in the same traits. This suggests the correlation effects are too strong.

## Why Are Values Maxing Out?

Look at the story choices:

```python
story.add_choice(
    from_passage_name="market_arrival",
    choice_text="Step toward the figures",
    tone_effects={"courage": 0.2, "narrative_presence": 0.15},
)
```


**What happens:**
- Courage +0.2 for player
- This raises all NPCs' Resolve +0.2 and Authority +0.2
- But also lowers Nuance -0.2 and Empathy -0.2

**19 times over** with mostly positive empathy/observation effects, traits eventually cap at 0.0 or 1.0.

## Tuning Effect Sizes

To see more granular NPC differences, adjust correlation weights in `npc_manager.py`:

### Current (Too Strong)

```python

# Direct effect: 1:1 (full correlation)
npc.adjust_trait(trait, delta)
```


### Better (0.5 Scale)

```python

# Soften the effect
npc.adjust_trait(trait, delta * 0.5)
```


### Softer (0.2 Scale - Recommended)

```python

# Much more subtle
npc.adjust_trait(trait, delta * 0.2)
```


### Edit This In `npc_manager.py`

Find the `apply_tone_effects()` method around line 150:

```python
def apply_tone_effects(self, tone_effects: Dict[str, float]) -> None:
    """
    Apply TONE changes to all NPCs via correlation map.
    """
    for npc in self.npcs.values():
        for tone_stat, delta in tone_effects.items():
            if tone_stat in self.TONE_CORRELATION:
                correlation = self.TONE_CORRELATION[tone_stat]

                for trait in correlation["raise"]:
                    npc.adjust_trait(trait, delta * 0.2)  # ← Add * 0.2 here

                for trait in correlation["lower"]:
                    npc.adjust_trait(trait, -delta * 0.2)  # ← And here
```


Then rebuild and check the NPC summary again.

## Viewing Detailed Evolution History

The full `npc_state.json` includes a complete history:

```json
{
  "npc_profiles": { ... },
  "influence_map": { ... },
  "evolution_history": [
    {
      "encounter": 1,
      "tone_effects": {"courage": 0.2, "narrative_presence": 0.15},
      "npc_profiles": {
        "Ravi": {
          "resolve": 0.8,
          "empathy": 0.7,
          ...
        }
      }
    },
    {
      "encounter": 2,
      "tone_effects": {"wisdom": 0.2, "courage": -0.1},
      "npc_profiles": {
        "Ravi": {
          "resolve": 0.9,
          "empathy": 0.6,
          ...
        }
      }
    }
  ]
}
```


To see this, open `npc_state.json` and scroll to the `"evolution_history"` array.

## Monitoring NPCs Through Your Story

### Before Editing Story

Current state:
- **Ravi**: Extremely empathetic, needs connection, has lost authority
- **Nima**: Similar evolution; less skeptical than starting state
- **Kaelen**: Paradoxically maxed empathy while maintaining high skepticism

### After You Edit Choices

Example: Add a harsh, aggressive choice:

```python
story.add_choice(
    from_passage_name="meet_ravi_nima",
    choice_text="Threaten them for information",
    tone_effects={
        "courage": 0.3,           # Very aggressive
        "narrative_presence": 0.2,
        "empathy": -0.2           # Lose empathy
    },
)
```


Then rebuild:

```bash
python velinor/stories/build_story.py --validate
```


You'll see NPC profiles shift. If Empathy drops overall, you should see NPCs more skeptical, less
empathetic in the summary.

## Interpreting Individual NPC Arcs

### Ravi's Arc (Initial → Current)

**Start:**
- resolve: 0.6, empathy: 0.7, trust: 0.7
- **Personality:** Warm leader, fairly steady

**Current:**
- resolve: 0.3, empathy: 1.0, need: 1.0
- **Personality:** Emotionally wide open, highly dependent, lost his conviction

**Narrative:** Over many compassionate/empathetic choices, Ravi has become vulnerable and unsure.

### Kaelen's Arc

**Start:**
- resolve: 0.4, trust: 0.2, skepticism: 0.9
- **Personality:** Shifty thief, distrustful, desperate

**Current:**
- resolve: 0.1, trust: 0.0, skepticism: 1.0
- **Personality:** Even more distrustful, completely broken

**Narrative:** Kaelen has solidified as antagonistic (or at least needs major trust-building to change).

## Next: Tuning Values

### Recommended Next Steps

1. **Scale correlation effects to 0.2x** (edit `npc_manager.py`)
   ```python
   npc.adjust_trait(trait, delta * 0.2)
   ```

2. **Rebuild and check NPC summary again**
   ```bash
   python velinor/stories/build_story.py --validate
   ```

3. **You should see more variation** between NPCs and less ceiling-hitting

4. **Then tune influence map ripples** — maybe reduce ripple strength

5. **Add story choices that have mixed effects** (some empathy, some courage) to see NPCs
differentiate

## Debugging: Print NPC State Mid-Story

Want to see how an NPC evolves after specific choices? Edit `story_definitions.py`:

```python
def build_velinor_story():
    story = StoryBuilder("Velinor: Remnants of the Tone")

    # Add passages and choices...

    # AFTER you've added all choices:

    # Check Ravi's state
    if story.npc_manager:
        ravi = story.npc_manager.get_npc("Ravi")
        print(f"Ravi's final traits: {ravi.remnants}")
```


Then rebuild to see the output.

## Files to Know

| File | Purpose |
|------|---------|
| `npc_manager.py` | REMNANTS system, correlations, NPC profiles |
| `twine_adapter.py` | Story building, NPC integration |
| `story_definitions.py` | Story choices with TONE effects |
| `npc_state.json` | Exported NPC state after build |
| `REMNANTS_SYSTEM_GUIDE.md` | Full technical documentation |
## 

**Current Status:** REMNANTS system fully working. Effect sizes need tuning. Ready for game engine integration. 🎮
