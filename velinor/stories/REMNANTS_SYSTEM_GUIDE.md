# REMNANTS System: Dynamic NPC Personality Evolution

## Overview

The **REMNANTS system** makes NPCs evolve dynamically based on player choices. Rather than static personalities, NPCs become **fragments reshaped by the player's resonance** — literally "remnants of the Tone."

When you increase a TONE stat (courage, empathy, etc.), it automatically ripples through connected NPCs' **REMNANTS traits**, creating emergent personality arcs that feel organic rather than scripted.

---

## Core Concepts

### REMNANTS Traits (What NPCs Are Made Of)

Each NPC has 8 personality traits, each ranging from **0.1 (recessive) to 0.9 (dominant)**:

No trait ever reaches absolute extremes (0.0 or 1.0) — this preserves nuance and ensures room for growth/decline.

| Trait | Meaning | Example |
|-------|---------|---------|
| **Resolve** | Firmness, conviction, backbone | High = steadfast, low = wavering |
| **Empathy** | Emotional openness, compassion | High = caring, low = callous |
| **Memory** | Recall of past, context awareness | High = sharp recall, low = forgetful |
| **Nuance** | Subtlety, shades of gray, complexity | High = nuanced, low = black-and-white |
| **Authority** | Command presence, decisiveness | High = commanding, low = uncertain |
| **Need** | Vulnerability, dependence, connection desire | High = dependent, low = self-sufficient |
| **Trust** | Confidence in others | High = trusting, low = suspicious |
| **Skepticism** | Doubt, caution, suspicion | High = doubting, low = credulous |

### TONE Stats (What The Player Has)

The player progresses through these TONE attributes:

- **Courage** - boldness, direct action, willingness to risk
- **Wisdom** - caution, observation, patience, careful choice
- **Empathy** - understanding, compassion, emotional attunement
- **Observation** - paying attention, noticing details, investigation
- **Narrative Presence** - visibility, reputation, authority in the story

---

## TONE → REMNANTS Correlation

When the player increases a TONE stat, it automatically adjusts connected NPC REMNANTS traits:

| Player Increases... | NPC Traits Raise | NPC Traits Lower |
|-------------------|-----------------|-----------------|
| **Courage** | Resolve, Narrative_Presence | Nuance, Empathy |
| **Wisdom** | Nuance, Memory | Authority |
| **Empathy** | Empathy, Need | Resolve |
| **Observation** | Nuance, Memory | Authority |
| **Narrative Presence** | Authority, Resolve | Nuance |

### Why This Works

Think of TONE and REMNANTS as **resonance frequencies**:

- A **bold player** (high Narrative Presence) makes NPCs more authoritative but less nuanced — they follow your lead, but subtlety fades.
- A **compassionate player** (high Empathy) makes NPCs more vulnerable and emotionally open, but less firm in their stance.
- An **observant player** (high Observation) makes NPCs more thoughtful and complex, but less commanding.

The correlation reflects how **player style reshapes the world**.

---

## Example: Ravi's Evolution

### Initial State
```
Ravi {
  resolve: 0.6,       ← Fairly steady
  empathy: 0.7,       ← Warm and open
  memory: 0.6,        ← Good recall
  nuance: 0.4,        ← Straightforward
  authority: 0.5,     ← Balanced
  need: 0.5,          ← Balanced
  trust: 0.7,         ← Trusting
  skepticism: 0.2     ← Open-minded
}
```

### Player Makes Bold Choice (+Courage +0.2, +Narrative_Presence +0.15)

**Direct effect on Ravi:**
- Resolve ↑ (+0.2) → 0.8 (more firm)
- Narrative_Presence ↑ (+0.15) → 0.65 (but Nuance ↓ by 0.15 → 0.25)

**Ripple effect from influence map:**
- Ravi→Nima ripple (-0.08) nudges Nima's trust down

### After Choice
```
Ravi {
  resolve: 0.8,       ← Now very firm
  empathy: 0.7,       ← Unchanged
  memory: 0.6,        ← Unchanged
  nuance: 0.25,       ← Became blunt
  authority: 0.65,    ← More commanding
  need: 0.5,          ← Unchanged
  trust: 0.7,         ← Unchanged
  skepticism: 0.2     ← Unchanged
}

Nima {
  trust: 0.22,        ← Ripple effect: lost trust
  skepticism: 0.88    ← Ripple effect: gained suspicion
  (all others unchanged)
}
```

**Narrative interpretation:** Ravi respects your boldness, becoming more authoritative but less nuanced. However, Nima senses Ravi's shift and becomes more skeptical of both of you.

---

## Ripple Effects & Influence Maps

NPCs don't exist in isolation. An **influence map** defines how one NPC's trait change affects others:

```python
influence_map = {
    "Ravi": {
        "Nima": -0.08,      # Ravi's trait change nudges Nima toward skepticism
        "Tovren": 0.1       # Ravi's warmth increases Tovren's trust
    },
    "Nima": {
        "Ravi": -0.05,      # Nima's suspicion nudges Ravi toward doubt
        "Kaelen": -0.15     # Nima's distrust intensifies Kaelen's skepticism
    }
}
```

### Example: Cascade Effect

1. **Player chooses empathy** (+0.2)
   - Ravi's Empathy ↑, Resolve ↓ (direct correlation)
   - Ravi→Nima ripple (-0.08): Nima's trust ↓
   - Nima→Ravi ripple (-0.05): Ravi's trust ↓ again
   
2. **Result:** Ravi becomes more caring but less firm. Nima becomes suspicious. The ripple creates tension even though only Ravi was directly affected.

---

## Current Marketplace Influence Map

**Ravi** (merchant leader):
- → Nima: -0.08 (caution spreads)
- → Tovren: +0.1 (openness encourages merchants)

**Nima** (shrine keeper):
- → Ravi: -0.05 (suspicion nudges doubt)
- → Kaelen: -0.15 (distrust intensifies)

**Kaelen** (shifty thief):
- → Tovren: -0.1 (mistrust spreads to practical folk)
- → Korrin: +0.05 (gossip and thieves share rumors)
- → Drossel: +0.2 (thief nature aligns with gang leader)

**Mariel** (bridge figure):
- → Ravi: +0.1 (wisdom strengthens)
- → Nima: +0.1 (insight calms)

**Sera** (healer):
- → Mariel: +0.15 (trust reciprocates)

**Drossel** (thieves' leader) — THE DARK INFLUENCE:
- → Kaelen: +0.15 (respects criminal nature)
- → Korrin: -0.1 (mistrusts even allies, gossips are loose cannons)
- → Tovren: -0.2 (presence darkens merchants' suspicion)
- → Ravi: -0.25 (criminality erodes community trust)
- → Nima: +0.05 (her suspicion resonates with his distrust)

**Narrative:** Drossel's presence creates a **shadow ripple** across the marketplace. Where Ravi and Mariel build trust, Drossel corrodes it. His influence is strongest on pragmatists (Tovren) and merchants (Ravi), weakest on those who already distrust (Nima actually aligns with him slightly).

---

## NPC Initial Profiles

### Ravi — Warm, Cautious Leader
```
resolve: 0.6, empathy: 0.7, memory: 0.6, nuance: 0.4,
authority: 0.5, need: 0.5, trust: 0.7, skepticism: 0.2
```
**Type:** Open but cautious. Trusts easily but has been burned by thieves.

### Nima — Observant Skeptic
```
resolve: 0.6, empathy: 0.6, memory: 0.7, nuance: 0.8,
authority: 0.4, need: 0.5, trust: 0.3, skepticism: 0.8
```
**Type:** Sharp-eyed, sees layers. Trusts few, understands complexity.

### Kaelen — Shifty, Redeemable
```
resolve: 0.4, empathy: 0.3, memory: 0.6, nuance: 0.5,
authority: 0.3, need: 0.7, trust: 0.2, skepticism: 0.9
```
**Type:** Low resolve, high need = thief driven by desperation, not malice.

### Tovren — Practical Merchant
```
resolve: 0.7, empathy: 0.3, memory: 0.6, nuance: 0.3,
authority: 0.6, need: 0.2, trust: 0.4, skepticism: 0.7
```
**Type:** Values observation, distrusts dreamers, self-sufficient.

### Sera — Gentle Healer
```
resolve: 0.3, empathy: 0.8, memory: 0.5, nuance: 0.6,
authority: 0.2, need: 0.8, trust: 0.6, skepticism: 0.3
```
**Type:** Highly empathetic, vulnerable, needs connection.

### Dalen — Bold Wanderer
```
resolve: 0.8, empathy: 0.4, memory: 0.5, nuance: 0.2,
authority: 0.7, need: 0.3, trust: 0.5, skepticism: 0.4
```
**Type:** Resolute, commanding, impatient with subtlety.

### Mariel — Wise Bridge
```
resolve: 0.6, empathy: 0.8, memory: 0.9, nuance: 0.7,
authority: 0.5, need: 0.4, trust: 0.7, skepticism: 0.2
```
**Type:** Combines empathy with memory; connects disparate factions.

### Korrin — Gossiping Informant
```
resolve: 0.4, empathy: 0.3, memory: 0.8, nuance: 0.7,
authority: 0.3, need: 0.5, trust: 0.3, skepticism: 0.8
```
**Type:** Sharp memory, high skepticism, loves gossip and information.

### Drossel — Thieves' Leader, Charming Yet Dangerous
```
resolve: 0.8, empathy: 0.2, memory: 0.9, nuance: 0.9,
authority: 0.9, need: 0.3, trust: 0.1, skepticism: 0.95
```
**Type:** Master manipulator with Slavic-French cadence. Firm, commanding, absolutely mistrusts everyone. Appears caring but emotionally cold. Sharp recall of grudges and betrayals. Reads subtle cues to exploit vulnerability.

**Threat Profile:**
- High Authority & Resolve → Commands gang, firm in convictions
- High Nuance & Memory → Dangerous manipulator, remembers all slights
- Low Trust & High Skepticism → Distrusts by default, sees threats everywhere
- Low Empathy → Charming facade hides internal coldness
- Low Need → Self-sufficient, relies on no one

---

## How The System Works In-Game

### Step 1: Player Makes Choice

```python
story.add_choice(
    from_passage_name="market_arrival",
    choice_text="Step boldly toward them",
    to_passage_name="meet_ravi_nima",
    tone_effects={"courage": 0.2, "narrative_presence": 0.15},
    npc_resonance={"Ravi": 0.1, "Nima": -0.1}
)
```

### Step 2: TONE Effects Applied

The game engine applies `tone_effects` to player TONE stats:
- Courage: 0 → 0.2
- Narrative Presence: 0 → 0.15

### Step 3: TONE → REMNANTS Correlation

The system automatically updates all NPCs via correlation:

**Courage +0.2 raises:**
- All NPCs' Resolve +0.2
- All NPCs' Narrative Presence +0.2

**Courage +0.2 lowers:**
- All NPCs' Nuance -0.2
- All NPCs' Empathy -0.2

**Narrative Presence +0.15 raises:**
- All NPCs' Authority +0.15
- All NPCs' Resolve +0.15

**Narrative Presence +0.15 lowers:**
- All NPCs' Nuance -0.15

### Step 4: Ripple Effects Applied

Based on `influence_map`, one NPC's change nudges others:

- Ravi's Trust ↓ (from Narrative Presence correlation)
- Ripple: Ravi→Nima (-0.08) nudges Nima's Trust -0.08, Skepticism +0.08

### Step 5: Final State

All NPCs are now updated. Different playstyles produce radically different NPC personalities:

- **Bold player** (high Courage, Narrative Presence) → NPCs more commanding, less nuanced
- **Observant player** (high Observation) → NPCs more thoughtful, less authoritative
- **Compassionate player** (high Empathy) → NPCs more vulnerable, less firm

---

## Using REMNANTS in Story Conditions

Game engine can gate story branches on NPC REMNANTS:

### Example: Ravi's Response to Player

**If Ravi.authority > 0.7 and Ravi.nuance < 0.3:**
```
"Ravi looks at you with command in his eyes. 
'Here's what we'll do. No time for questions.'"
```

**If Ravi.nuance > 0.6:**
```
"Ravi pauses, considering the complexity of the situation.
'There are layers to this I hadn't considered...'"
```

**If Ravi.skepticism > 0.5:**
```
"Ravi's expression clouds with doubt.
'I want to trust you, but something feels off.'"
```

This way, NPC dialogue **naturally reflects their evolved personality**, not pre-written branching.

---

## Threshold-Based Events

Certain story beats only unlock when REMNANTS cross thresholds:

| Condition | Story Unlock |
|-----------|--------------|
| Kaelen.trust > 0.5 | Kaelen offers thieves' cache map |
| Nima.empathy > 0.7 | Nima shares her lost family history |
| Sera.need > 0.8 | Sera asks player for personal support |
| Mariel.authority < 0.4 | Mariel asks for protection |
| Tovren.trust > 0.6 | Tovren gifts "Chalk of Paths" tool |
| Dalen.resolve > 0.8 | Dalen volunteers for dangerous mission |

---

## Simulation & Testing

The system includes a **simulation mode** that shows NPC evolution over multiple choices:

```bash
# Build story with NPC evolution simulation
python velinor/stories/build_story.py --validate
```

Output shows NPC state before and after each player choice:

```
🧑‍🤝‍🧑 NPC REMNANTS Evolution:
   • Ravi: authority: 0.65, resolve: 0.80, nuance: 0.25
   • Nima: skepticism: 0.88, trust: 0.22, memory: 0.70
   • Kaelen: resolve: 0.60, trust: 0.35, need: 0.65
   ...
```

---

## Design Principles

### 1. **Correlation, Not Causation**

REMNANTS don't cause choices; player choices cause TONE changes, which ripple into REMNANTS. The player remains the active agent.

### 2. **Subtle Accumulation**

Individual choice effects are small (0.1-0.2 range). Meaning emerges over 5-10 choices, not immediately.

### 3. **Opposing Pressures**

Ripples sometimes contradict correlations:
- Player empathy raises NPC Empathy
- But player empathy also lowers Resolve
- Other NPCs' ripples might counter the effect

Result: Realistic tension, not flat alignment.

### 4. **Personality Drift**

An NPC evolves gradually, never flipping completely. A trustworthy NPC stays mostly trustworthy, just with nuance.

### 5. **Context-Sensitive Dialogue**

Rather than branching by exact values, dialogue adapts to **relative positions**:
- Is this NPC more empathetic than skeptical?
- Is this NPC more authoritative than nuanced?
- Did this NPC just shift dramatically?

---

## Editing Profiles & Correlations

### Adjust Initial REMNANTS

In `npc_manager.py`, modify `create_marketplace_npcs()`:

```python
NPCProfile("Ravi", {
    "resolve": 0.7,      # ← Increase for firmer initial personality
    "empathy": 0.6,      # ← Decrease for less initial warmth
    "memory": 0.6,
    "nuance": 0.5,       # ← Increase for more initial complexity
    "authority": 0.5,
    "need": 0.5,
    "trust": 0.8,        # ← More trusting at start
    "skepticism": 0.1    # ← Less skeptical at start
})
```

### Add Ripple Effects

In `create_marketplace_influence_map()`:

```python
return {
    "Ravi": {
        "Nima": -0.08,      # Ravi's traits spread skepticism to Nima
        "Kaelen": 0.05      # ← NEW: Ravi's warmth slightly softens Kaelen
    }
}
```

### Tune Correlations

In `npc_manager.py` `TONE_CORRELATION`:

```python
"courage": {
    "raise": ["resolve", "narrative_presence"],
    "lower": ["nuance", "empathy"]  # ← Courage reduces nuance/empathy
}
```

---

## Common Patterns

### Pattern 1: NPC Becomes More Like Player

Player is bold (high Narrative Presence) → NPC becomes more authoritative (raised Authority).

**Use case:** Creating a leadership arc where the player's confidence inspires NPCs.

### Pattern 2: NPC Becomes More Unlike Player

Player is bold (high Narrative Presence) → NPC becomes less nuanced (lowered Nuance).

**Use case:** Creating tension where the player's boldness makes NPCs blunter, losing subtlety.

### Pattern 3: Ripple Cascade

Player affects Ravi → Ravi ripples to Nima → Nima ripples back to Ravi.

**Use case:** Creating emergent drama where NPCs shift based on each other's evolution.

### Pattern 4: Dead Ends

Player reaches extreme TONE (e.g., very bold, very unempathetic) → Some NPCs cross threshold for distrust → Story path gated off.

**Use case:** Meaningful consequences for extreme playstyles.

---

## Next Steps

1. **Test correlation values** — Run simulations with different choice sequences to tune ripple strengths.
2. **Design threshold events** — Define which REMNANTS values unlock story branches.
3. **Write NPC-aware dialogue** — Create dialogue that references current REMNANTS state, not just a fixed branching path.
4. **Expand to Acts 2-4** — Add more NPCs and influence edges as story grows.
5. **Integrate with game engine** — Wire REMNANTS queries into dialogue system and choice gating.

---

## File Reference

- **`npc_manager.py`** — REMNANTS trait system, correlation logic, NPC profiles
- **`twine_adapter.py`** — StoryBuilder integration with NPC tracking
- **`story_definitions.py`** — Story choices that trigger TONE/NPC changes
- **`sample_story.json`** — Generated story with choices and metadata
- **`npc_state.json`** — Exported NPC REMNANTS state after story simulation

---

## Technical Specs

### REMNANTS Value Range
- Minimum: 0.1 (trait recessive but never absent)
- Maximum: 0.9 (trait dominant but never absolute)
- Change per choice: typically 0.05 to 0.25
- Clamped after each update (enforced to stay in [0.1, 0.9])

### Correlation Weights
- Direct TONE effect: 1:1 (TONE change = REMNANTS change)
- Ripple effect: typically 0.05 to 0.15 (weaker than direct)
- Can be tuned per relationship in influence_map

### Simulation Complexity
- 8 NPCs × 8 traits = 64 tracked values
- Per choice: 64 direct updates + 8-16 ripples = ~100 trait adjustments
- Negligible performance cost

---

**Status:** REMNANTS system fully integrated. Ready for Acts 2-4 expansion and game engine wiring. ✨
