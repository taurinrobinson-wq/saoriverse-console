# Choice Metadata & Consequence System

When you create choices in `story_definitions.py`, you can now specify how each choice affects: 1.
**Player TONE state** - emotional progression 2. **NPC relationships** - resonance/affinity with
specific characters

## Quick Example

```python
story.add_choice(
    from_passage_name="market_arrival",
    choice_text="Step toward the figures",
    to_passage_name="meet_ravi_nima",
    tone_effects={
        "courage": 0.2,              # +20% to courage
        "narrative_presence": 0.15   # +15% to presence
    },
    npc_resonance={
        "Ravi": 0.1,    # +10% resonance with Ravi
        "Nima": -0.1    # -10% resonance with Nima
    }
)
```


## How It Works

### TONE Effects

The `tone_effects` dictionary tracks how a choice affects the player's emotional state.

**Common TONE attributes:**
- `courage` - boldness, facing fears, taking action
- `wisdom` - careful thinking, observation, patience
- `empathy` - understanding, compassion, connection
- `observation` - paying attention, noticing details
- `narrative_presence` - how visible/known the player is

**Values are change factors (0.0 to 1.0+):**
- `0.2` = +20% to that tone
- `-0.1` = -10% to that tone
- `0.0` = no change

### NPC Resonance

The `npc_resonance` dictionary tracks how each choice affects the player's relationship with
specific NPCs.

**Values are change factors (0.0 to 1.0+):**
- `0.15` = +15% relationship with that NPC
- `-0.1` = -10% relationship with that NPC
- `0.0` = no relationship change

**Why it matters:**
- Some NPCs prefer courageous choices (Ravi)
- Some prefer cautious choices (Nima)
- Some prefer empathetic choices (both)
- Building resonance unlocks later dialogue options
- Low resonance can lock players out of paths

## Usage Patterns

### Choice with tone effects only

```python
story.add_choice(
    from_passage_name="scene",
    choice_text="Observe silently",
    to_passage_name="next_scene",
    tone_effects={"observation": 0.2, "wisdom": 0.1}
    # No npc_resonance - neutral to all NPCs
)
```


### Choice with resonance only

```python
story.add_choice(
    from_passage_name="scene",
    choice_text="Ask about Ravi's past",
    to_passage_name="next_scene",
    npc_resonance={"Ravi": 0.25}
    # No tone_effects - doesn't change player tone
)
```


### Choice affecting multiple NPCs

```python
story.add_choice(
    from_passage_name="scene",
    choice_text="Ask them for help",
    to_passage_name="next_scene",
    tone_effects={"empathy": 0.15},
    npc_resonance={"Ravi": 0.15, "Nima": 0.15, "Kaelen": -0.05}
    # Helps both Ravi & Nima, slightly offends Kaelen
)
```


### Neutral choice

```python
story.add_choice(
    from_passage_name="scene",
    choice_text="Sit down",
    to_passage_name="next_scene"
    # No effects - purely transitional
)
```


## Complete Example: Market Arrival Scene

Each choice affects the player differently:

```python

# Aggressive approach - high courage, but makes Nima wary
story.add_choice(
    from_passage_name="market_arrival",
    choice_text="Step toward the figures",
    to_passage_name="meet_ravi_nima",
    tone_effects={"courage": 0.2, "narrative_presence": 0.15},
    npc_resonance={"Ravi": 0.1, "Nima": -0.1}
)

# Careful approach - high wisdom, earns Nima's respect
story.add_choice(
    from_passage_name="market_arrival",
    choice_text="Retreat toward the underpass (safer)",
    to_passage_name="meet_ravi_nima",
    tone_effects={"wisdom": 0.2, "courage": -0.1},
    npc_resonance={"Ravi": -0.1, "Nima": 0.15}
)

# Social approach - empathy and presence, balanced
story.add_choice(
    from_passage_name="market_arrival",
    choice_text="Call out to them",
    to_passage_name="meet_ravi_nima",
    tone_effects={"empathy": 0.15, "narrative_presence": 0.1},
    npc_resonance={"Ravi": 0.15, "Nima": 0.05}
)

# Observant approach - wisdom and perception
story.add_choice(
    from_passage_name="market_arrival",
    choice_text="Stay still and observe",
    to_passage_name="meet_ravi_nima",
    tone_effects={"observation": 0.2, "wisdom": 0.1},
    npc_resonance={"Ravi": 0.05, "Nima": 0.15}
)
```


**Results after this choice:**
- Aggressive player: High courage, low Nima resonance
- Careful player: High wisdom, high Nima resonance
- Social player: High empathy, balanced resonance
- Observant player: High observation/wisdom, high Nima resonance

## Current Implementation: Velinor Act 1

All choices in Act 1 have been mapped with realistic consequences:

### Market Arrival (4 choices)
- Aggressive → Ravi likes it, Nima skeptical
- Cautious → Nima appreciates it, Ravi less impressed
- Social → Both respond well
- Observant → Nima respects it

### Relationship Dialogue (3 choices per path)
- **Ravi path:** Stepping forward builds trust, asking about his past deepens it
- **Nima path:** Keeping distance builds respect, asking questions shows wisdom
- **Shared:** Asking about resonance builds mutual understanding

### Quest Branching
- Going to Thieves' Cache: High courage, but Ravi/Nima disapprove
- Preparing with them: High wisdom, gains their support

## Storage in JSON

Both tone effects and NPC resonance are stored in the choices array:

```json
{
  "pid": "1",
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


The game engine reads:
- `tone_effects` → applies to player tone tracking
- `npc_resonance` → applies to NPC relationship scores
- Both are tracked throughout the game

## Design Principles

### 1. Meaningful Choices
Each choice should have consequences that reflect its nature:
- Brave choices → boost courage, impress Ravi
- Wise choices → boost wisdom, impress Nima
- Empathetic choices → boost empathy, help both

### 2. NPC Preferences
Each NPC has preferences that guide the story:
- **Ravi** (trust anchor): Values courage, directness, empathy
- **Nima** (empathy anchor): Values wisdom, observation, caution
- **Kaelen** (thief): Values boldness, self-interest, secrets

### 3. Conflicting Values
Not all choices please everyone:
- Aggressive actions build Ravi relationship, lower Nima
- Cautious actions build Nima relationship, lower Ravi
- Some NPCs stay neutral on certain choices

### 4. Cumulative Effects
Relationships build over time:
- Single choice: small change (0.1 to 0.2)
- Multiple aligned choices: compound over time
- Players shape character through their choices

## Editing Tips

### Finding the right numbers

```python

# Small effect (neutral/minor)
tone_effects={"courage": 0.05}

# Medium effect (notable)
tone_effects={"courage": 0.15}

# Large effect (major)
tone_effects={"courage": 0.25}

# Negative effect (drawback)
tone_effects={"courage": -0.1}
```


### Multi-attribute choices

```python

# Balanced approach - moderate effects
story.add_choice(
    ...
    tone_effects={
        "courage": 0.1,
        "wisdom": 0.1,
        "empathy": 0.1
    }
)

# Specialized approach - focused effects
story.add_choice(
    ...
    tone_effects={
        "courage": 0.25,
        "wisdom": -0.05
    }
)
```


### Building resonance narratively

```python

# Early meeting - establish base
story.add_choice(
    ...
    npc_resonance={"Ravi": 0.1, "Nima": 0.05}
)

# Deepening trust - larger gain
story.add_choice(
    ...
    npc_resonance={"Ravi": 0.25}
)

# Wrong direction - penalty
story.add_choice(
    ...
    npc_resonance={"Ravi": -0.15}
)
```


## Workflow

1. **Design the choice** - what does the player see? 2. **Add to passage** - define destination 3.
**Identify tone effect** - what does this reveal about the player? 4. **Identify NPC reactions** -
how does each NPC feel? 5. **Assign numbers** - magnitude of effect 6. **Test** - verify numbers
feel right 7. **Document** - comment in code for later reference

## Next Steps

- [ ] Add all tone effects to remaining Act 1 choices
- [ ] Define tone effect ranges per NPC (preferences)
- [ ] Create resonance threshold system (unlock content at X resonance)
- [ ] Test cumulative effects across multiple choices
- [ ] Design Act 2 with branching based on resonance
- [ ] Create "dead ends" for low resonance paths
## 

**Example: How Choices Compound**

Player makes these consecutive choices: 1. "Step toward figures" → Ravi +0.1, Nima -0.1 2. "Ask for
help" → Ravi +0.15, Nima +0.15 3. "Prepare with them" → Ravi +0.2, Nima +0.2

**Final Resonance:**
- Ravi: 0.1 + 0.15 + 0.2 = 0.45 (strong relationship)
- Nima: -0.1 + 0.15 + 0.2 = 0.25 (wavering, but improving)

This shapes what dialogue options appear, who player can ask for help, and what ending paths are
available!
