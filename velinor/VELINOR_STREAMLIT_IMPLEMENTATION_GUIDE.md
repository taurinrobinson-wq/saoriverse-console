# Velinor Streamlit Prototype Implementation Guide

**Last Updated**: Current  
**Status**: Ready for Implementation  
**Scope**: Complete Streamlit prototype architecture with emotional OS integration

---

## Quick Summary

This guide consolidates 6000+ lines of design conversation into an actionable blueprint for building the Velinor Streamlit prototype. It contains everything needed to implement a working emotional narrative sandbox.

---

## Part 1: Core Architecture

### 1.1 Layout Structure

**Main Display Panel**
```
[ Background Image: Scene-specific (marketplace, forest, chamber, etc.) ]
[ NPC Overlay: Transparent PNG of character + emotional glyphs ]
[ Dialogue Box: Italicized thought/dialogue at bottom ]
[ Choice Buttons: 2x2 grid + optional 5th action button ]
```

**Right Sidebar**
- TONE stats (live updating)
- REMNANTS readout (NPC perception)
- Glyphs panel (expander)
- Skills panel (expander)
- Debug mode toggle

### 1.2 State Machine

```
Scenes:
- marketplace_arrival
- npc_encounter
- glyph_hub_discovery
- transcendence_chamber
- final_chamber
- ending

Modes:
- narrative (standard dialogue/choice flow)
- glyph_input (selecting glyphs for chamber door)
- chamber (fighting glyph beast)
- dialogue_special (optional revelations)
```

---

## Part 2: TONE System Implementation

### 2.1 TONE Stats

The player's emotional signature. All four stats influence how NPCs respond.

```python
TONE = {
    "trust": float,              # Reliability, keeping promises
    "observation": float,         # Perception, noticing details
    "narrative_presence": float,  # Charisma, bold choices
    "empathy": float,             # Heart, vulnerability, grief
    "resonance": float            # Overarching harmonic balance
}
```

**Range**: -1.0 to 1.0 for TONE stats, 0.0 to 1.0 for resonance

### 2.2 Tone Effects Template

Every choice in a scene applies a tone_effect dict:

```python
choice = {
    "text": "Step toward the figures",
    "tone_effects": {
        "trust": +0.2,
        "observation": -0.1,
        "narrative_presence": +0.3,
        "empathy": +0.1
    }
}
```

### 2.3 TONE → NPC Response Mapping

```
Player Trust (+) → NPC trust ↑, resolve ↑, skepticism ↓
Player Observation (+) → NPC nuance ↑, memory ↑, authority ↓
Player Narrative Presence (+) → NPC authority ↑, resolve ↑, nuance ↓
Player Empathy (+) → NPC empathy ↑, need ↑, resolve ↓
Player Resonance (balanced) → All NPC traits stabilize
```

---

## Part 3: REMNANTS System Implementation

### 3.1 REMNANTS Traits (NPC Personalities)

Eight traits that define how each NPC interprets the player and world.

```python
REMNANTS = {
    "resolve": float,      # How firm/principled (0.0-1.0)
    "empathy": float,      # Capacity to care
    "memory": float,       # How past shapes choices
    "nuance": float,       # Subtlety, complexity (NOT narrative presence)
    "authority": float,    # Relationship to boundaries
    "need": float,         # What they seek from player
    "trust": float,        # Baseline openness
    "skepticism": float    # Tendency to doubt
}
```

### 3.2 NPC Profile Examples

**Ravi** (Thoughtful Scholar)
- resolve: 0.7 | empathy: 0.8 | memory: 0.9 | nuance: 0.8
- authority: 0.6 | need: 0.7 | trust: 0.6 | skepticism: 0.5

**Nima** (Cautious Empath)
- resolve: 0.5 | empathy: 0.9 | memory: 0.6 | nuance: 0.9
- authority: 0.3 | need: 0.8 | trust: 0.4 | skepticism: 0.8

**Veynar** (Firm Guard)
- resolve: 0.8 | empathy: 0.4 | memory: 0.7 | nuance: 0.5
- authority: 0.9 | need: 0.6 | trust: 0.5 | skepticism: 0.7

**Kaelen** (Distant Thief)
- resolve: 0.6 | empathy: 0.3 | memory: 0.4 | nuance: 0.4
- authority: 0.5 | need: 0.9 | trust: 0.2 | skepticism: 0.9

### 3.3 NPC Perception Shifts

When player takes action:

```python
update_npc_perception(
    npc_name="Ravi",
    trust_delta=+0.2,
    affinity_delta=+0.1,
    understanding_delta=+0.15,
    emotion="warm"
)
```

---

## Part 4: Glyph System

### 4.1 Glyph Structure

```python
Glyph = {
    "name": str,
    "domain": str,  # Collapse, Legacy, Sovereignty, Trust, Ache, Presence, Joy
    "description": str,
    "obtained": bool,
    "unlock_condition": str,  # Story beat or TONE threshold
    "emotional_effect": str,  # Which TONE stat it affects
    "npc_resonance": {npc_name: resonance_value}
}
```

### 4.2 Glyph Domains

| Domain | Definition | Vibe |
|--------|-----------|------|
| **Collapse** | Memory distortion, fear, fracture | Dark, unsettling |
| **Legacy** | Family, ancestry, ritual inheritance | Solemn, binding |
| **Sovereignty** | Boundaries, choice, clarity | Resolute, sharp |
| **Trust** | Community, restoration, interdependence | Warm, rebuilding |
| **Ache** | Loss, grief, betrayal | Tender, heavy |
| **Presence** | Touch, silence, witness | Intimate, grounding |
| **Joy** | Play, reunion, creative spark | Bright, playful |

### 4.3 Glyph UI Representation

In sidebar glyph expander:

```
🟩 Sorrow (obtained)     - Domain: Ache
⬜ Presence (locked)     - Domain: Presence
🟨 Wisdom (in progress)  - Domain: Legacy
⬜ Trust (locked)        - Domain: Trust
```

**Colors**: Gray (locked), Green (obtained), Yellow (active), Blue (fused)

### 4.4 Chamber Glyph Door Logic

- 8-glyph multi-door chambers
- Page 1: Glyphs 0-3
- Page 2: Glyphs 4-7
- Player must input correct sequence to unlock
- Wrong input = hint system activates

---

## Part 5: Transcendence Chambers

### 5.1 Chamber Simplification (Prototype)

Replace combat complexity with **state-driven encounter**:

```
1. Player enters chamber → Background changes to interior
2. NPC overlay disappears → Transcendence glyph overlay appears
3. Dialogue: "The air fractures..."
4. Show "Attack" button
5. Each click → fight_counter++
6. At fight_counter == 15 → "Obtain Glyph" button appears
7. On click → Update glyph, change background, trigger next beat
```

### 5.2 Flicker System

As player completes transcendence chambers, Velinor appears in increasing coherence:

```
Chamber 1 → Faint shimmer
Chamber 2 → Silhouette
Chamber 3 → Whisper of movement
Chamber 4 → Half-formed figure
Chamber 5 → Nearly tangible
Final → Middle-aged woman (present day Velinor)
```

**Key**: Young Velinor in flickers, older Velinor in final chamber = emotional dissonance

---

## Part 6: NPC System

### 6.1 NPC Dialogue

Dialogue influenced by:
- Player TONE stats
- NPC REMNANTS traits
- Dialogue history
- Story beats

### 6.2 NPC Perception Panel (Sidebar)

```
Ravi
├─ Trust: +0.3
├─ Affinity: +0.2
├─ Understanding: +0.4
├─ Emotion: warm
└─ Last: 2 scenes ago
```

### 6.3 Saori (Special NPC)

**Role**: Glyph giver, guardian, reluctant witness

**Early Game**: Gives first glyphs without explaining Velhara/Corelink

**Mid-Game**: Avoids questions about flickers and "strange hubs"

**Late Game**: Final revelation scene in the chamber

---

## Part 7: Story Implementation Structure

### 7.1 Scene Definition Format

```json
{
  "scene_id": "marketplace_arrival",
  "background": "marketplace_day.png",
  "npc": "Ravi",
  "npc_overlay": "ravi_neutral.png",
  "dialogue": "They're staring at me. What should I do?",
  "choices": [
    {
      "text": "Step toward the figures",
      "tone_effects": {"trust": 0.2, "observation": -0.1, "narrative_presence": 0.3, "empathy": 0.1},
      "npc_delta": {"trust": 0.1, "affinity": 0.2},
      "next_scene": "ravi_dialogue_1"
    },
    {
      "text": "Keep your distance",
      "tone_effects": {"observation": 0.2, "narrative_presence": -0.1},
      "npc_delta": {"understanding": 0.15},
      "next_scene": "marketplace_exploration"
    }
  ]
}
```

### 7.2 Story Arc Tracking

```
Act I: Arrival & First Encounters
└─ Marketplace scene
└─ NPC introductions (Ravi, Nima, Veynar, Kaelen)
└─ First glyph discovery (Saori gives Glyph of First Fracture)

Act II: Hub Discovery & Mystery
└─ Player finds Corelink hubs
└─ Asks Saori about them
└─ Saori avoids answering
└─ Transcendence chambers unlock

Act III: Chamber Progression & Flickers
└─ Each chamber clears → Velinor flickers increase in clarity
└─ Player mentions flickers to Saori
└─ Saori's avoidance becomes more desperate
└─ Late chapters: Flickers almost tangible

Act IV: Final Chamber & Reckoning
└─ Player encounters middle-aged Velinor
└─ Saori's silence in final chamber
└─ Ending branches based on final choices
```

---

## Part 8: Debug & Cheats

**Sidebar Debug Panel** (toggle with checkbox)

```
Show:
☑ Raw TONE values
☑ Raw REMNANTS for each NPC
☑ Story variables
☑ Fight counter (in chamber)

Quick Set:
[ Max All TONE ]
[ Reset All TONE ]
[ Unlock All Glyphs ]
[ Jump to Scene... ]
```

---

## Part 9: UI Components Reference

### 9.1 TONE Stats Display

```python
st.sidebar.markdown("### 🎼 TONE")
for stat_name, value in tone_dict.items():
    color = "🟢" if value > 0.3 else "🟡" if value > -0.3 else "🔴"
    st.sidebar.markdown(f"{color} **{stat_name.title()}**: {value:+.2f}")
```

### 9.2 Glyph List Display

```python
st.sidebar.markdown("### ✨ Glyphs")
for glyph_name, glyph in glyphs.items():
    if glyph.obtained:
        st.sidebar.markdown(f"🟢 **{glyph_name}**")
    else:
        st.sidebar.markdown(f"⬜ {glyph_name}")
```

### 9.3 Choice Buttons Layout

```python
col1, col2 = st.columns(2)
with col1:
    if st.button("Choice 1"):
        apply_choice(choice_1)
with col2:
    if st.button("Choice 2"):
        apply_choice(choice_2)

col3, col4 = st.columns(2)
with col3:
    if st.button("Choice 3"):
        apply_choice(choice_3)
with col4:
    if st.button("Choice 4"):
        apply_choice(choice_4)

if has_special_action:
    if st.button("Special Action"):
        apply_special()
```

---

## Part 10: Philosophical Foundation

### 10.1 The Core Principle

> **Velinor is a world where emotional truth shapes reality, and every system — narrative, mechanical, and aesthetic — expresses the journey from fracture to coherence.**

### 10.2 Oneness of Person & Environment

- **TONE** = The person (inner state)
- **REMNANTS** = The environment (outer response)
- **Ripple effects** = The interdependence

When player's TONE shifts → NPCs' REMNANTS shift → World changes

### 10.3 Fixed Points & Inevitable Events

Certain story beats **cannot be avoided** because they are the emotional anchors the entire narrative depends on. The player's choices shape *how* they happen, not *if* they happen.

---

## Part 11: Implementation Checklist

- [ ] Create `streamlit_state.py` with ToneStats, REMNANTS, Glyph, NPC classes
- [ ] Create `streamlit_app.py` with main game loop and scene management
- [ ] Create `streamlit_ui.py` with all UI rendering functions
- [ ] Create `story_scenes.json` with all scene definitions
- [ ] Create `glyph_organizer.json` with all glyphs
- [ ] Implement TONE effect application
- [ ] Implement NPC perception updates
- [ ] Implement scene transitions
- [ ] Implement dialogue choice branching
- [ ] Implement glyph unlock conditions
- [ ] Implement transcendence chamber logic
- [ ] Implement flicker progression
- [ ] Add debug panel
- [ ] Write integration tests (8 minimum)
- [ ] Test all TONE/REMNANTS mappings
- [ ] Verify all story beats flow correctly

---

## Part 12: Next Steps

1. **Week 1**: Complete core state machine & UI framework
2. **Week 2**: Implement first 3 scenes + NPC system
3. **Week 3**: Implement glyph system + transcendence chambers
4. **Week 4**: Add Saori's arc + flickers + final chamber
5. **Week 5**: Ending branches + polish + testing

---

## Reference Files

- [TONE_STAT_SYSTEM.md](TONE_STAT_SYSTEM.md) - Official TONE definitions
- [Velinor_improvements_full.md](Velinor_improvements_full.md) - Full design conversation
- [velinor/streamlit_state.py](../streamlit_state.py) - Current state classes
- [velinor/streamlit_app.py](../streamlit_app.py) - Game loop
- [velinor/streamlit_ui.py](../streamlit_ui.py) - UI components

---

**This is your north star. Everything else follows from this structure.**
