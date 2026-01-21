# 🌌 Velinor's Awakening: Influence & Cascading System

## Overview

Velinor is the sleeping consciousness beneath Remnants. As the player collects glyphs, Velinor gradually wakes up, and her influence expands from isolated NPC interactions to a fully connected network where every action reverberates through all NPCs.

This document defines the **mathematical and mechanical framework** for that awakening.

---

## The Three-Stat Economy

### 1. TONE (Player)
- Player's emotional state
- Set by: gameplay decisions, dialogue choices, reflection moments
- Range: 0–100 per emotion (fear, grief, joy, trust, presence, ache, sovereignty)
- Purpose: interfaces with NPC REMNANTS to produce dialogue and reactions

### 2. REMNANTS (NPCs)
- NPC internal state
- Modified by:
  - Direct player interaction (TONE interface)
  - Cascading effects from other NPCs (Velinor influence multiplier)
- Per NPC: ~7 traits (fear, grief, joy, trust, presence, ache, sovereignty)
- Purpose: determines NPC personality, available dialogue, and story branches

### 3. Velinor's Consciousness (Global Influence)
- Ranges: **0.001 (asleep)** → **0.010 (fully awake)**
- Increases: every glyph unlock
- Effect: multiplier on cross-NPC cascade effects
- Purpose: game narrative progression (world becomes more interconnected)

---

## The Influence Budget

**Total increase available across entire game: 0.009**

This 0.009 is distributed across 113 glyphs (36 + 70 + 7) using weighted tiers:

### Weight Tiers

| Tier | Narrative | Weight | Items | Per-Item Value | Total Gain |
|------|-----------|--------|-------|-----------------|-----------|
| **Fragment** | micro-insight | 1× | 36 | 0.0000225 | 0.00081 |
| **Base Glyph** | emotional truth | 4× | 70 | 0.00009 | 0.00630 |
| **Transcendence** | coherence event | 12× | 7 | 0.00027 | 0.00189 |

**Math check**: 36 + 280 + 84 = 400 weight units → 0.009 ÷ 400 = 0.0000225 per unit ✓

### Progression Curve

```
Velinor's Consciousness Over Time

0.010 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 🌟 Endgame
      ║
      ║ Transcendence unlocks (×0.00027 each)
      ║ World feels alive and remembering
0.008 ║━━━━━━━━━━━ 🌕 Consciousness Surge
      ║
      ║ Base glyphs unlock (×0.00009 each)
      ║ NPCs begin recognizing each other
0.005 ║━━━━━━ 🌒 Mid-Game Awakening
      ║
      ║ Fragments unlock (×0.0000225 each)
      ║ Subtle hints of connection
0.002 ║━ 🌑 Early Game
      ║
0.001 ╳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 🌑 Game Start (Asleep)
      0            36           106            113
         Fragments    Base Glyphs  Transcendence
```

---

## How Cascading Works

### Stage 1: Player Makes a Choice

```
Player TONE: fear = 75
Player to Malrik: "I'm afraid of what we've lost"
```

### Stage 2: Direct NPC Effect

```
Malrik REMNANTS before: { fear: 20, grief: 40 }

Interface (TONE → REMNANTS):
  Malrik fear += 15 (direct response)
  Malrik grief += 8  (thematic resonance)

Malrik REMNANTS after: { fear: 35, grief: 48 }

✓ Malrik's dialogue now reflects heightened fear
```

---

## Implementation: glyph_cipher_engine.py

### Data Structure

```python
class VelinorState:
    """Tracks Velinor's consciousness and cascade effects"""
    
    consciousness: float  # 0.001 → 0.010
    glyphs_unlocked: dict  # {glyph_id: unlock_timestamp}
    influence_by_tier: dict  # {
        "fragment": sum of fragment influence gains,
        "base": sum of base glyph influence gains,
        "transcendence": sum of transcendence influence gains
    }
```

---

## Game State Persistence

### Save File Structure

```json
{
  "player": {
    "tone": {"fear": 45, "grief": 60, "joy": 30, ...},
    "discovered_glyphs": ["velinor-base-001", "velinor-fragment-003", ...]
  },
  "velinor": {
    "consciousness": 0.00412,
    "influence_stage": "stirring",
    "glyphs_unlocked": 47,
    "progress": {
      "fragments": 15,
      "base": 28,
      "transcendence": 4
    }
  },
  "npcs": {
    "Malrik": {
      "remnants": {"fear": 55, "grief": 42, ...},
      "glyphs_given": ["velinor-base-001", "velinor-base-003", ...],
      "opinion_of_player": 0.68
    },
    ...
  }
}
```

---

## Integration: npc_response_engine.py

When generating an NPC response, apply cascading logic:

```python
def generate_response(npc: str, player_tone: dict, game_state: GameState) -> str:
    """
    Generate NPC response considering:
    1. Direct TONE → REMNANTS mapping
    2. NPC's current REMNANTS state
    3. Velinor's influence multiplier
    4. Cascade effects from recent choices
    """
    
    # Step 1: Get direct response (TONE → REMNANTS)
    direct_response = map_tone_to_response(npc, player_tone)
    
    # Step 2: Apply cascade effects from Velinor
    velinor_influence = game_state.velinor.consciousness
    cascade_effects = get_cascade_effects(npc, player_tone, velinor_influence)
    
    # Step 3: Modify NPC REMNANTS by cascade
    for affected_npc, trait_changes in cascade_effects.items():
        for trait, amount in trait_changes.items():
            game_state.npcs[affected_npc].remnants[trait] += amount
    
    # Step 4: Generate response considering new REMNANTS state
    full_response = augment_with_cascade_awareness(direct_response, cascade_effects, velinor_influence)
    
    # Step 5: Unlock glyph if conditions met
    if meets_emotional_gate_requirements(player_tone, npc):
        glyph_result = unlock_glyph(glyph_id, npc, player_tone)
        velinor_influence += glyph_result.influence_gain
    
    return full_response
```
