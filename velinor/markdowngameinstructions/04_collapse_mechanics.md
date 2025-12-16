# Collapse Mechanics: Dynamic Environment & World Events

## Overview
The marketplace is in **constant flux** — buildings collapse, paths open, areas become inaccessible. This is represented through:
- Background image swaps (intact → collapsed)
- Map overlay updates with red X markers
- NPC reactions (static vs. reactive)
- Glyph resonance tied to collapse events
- First-time map introduction during collapse
##

## Collapse Event Structure

### Trigger Conditions
- **Scripted Events**: Happen at specific story beats
- **Dice Rolls**: Random chance during exploration (optional)
- **Resonance Spikes**: Certain glyph combinations trigger environmental response
- **Time-Based**: Collapse after player has visited an area multiple times

### Visual Changes

#### Background Image Swap

```text
```

Before Collapse:   marketplace_intact.png
                   - Open stalls, clear pathways
                   - Buildings stand, mostly whole
                   - Marketplace feels bustling but fragile

After Collapse:    marketplace_collapsed.png
                   - Buildings partially or fully ruined
                   - Rubble in pathways, new barriers
                   - Same perspective/vanishing points (critical for immersion)
                   - Atmosphere: dust, danger, quiet

```



**Design Note**: Matched perspective between intact/collapsed versions ensures players feel like they're in the *same space*, just transformed.

#### Map Overlay Integration
```sql
```sql
```
Sidebar Map Update:
1. Player position marked with glowing dot
2. Red ❌ appears on collapsed sector(s)
3. Optional: Green ✧ appears where new path opens
4. Affected areas gray out or become visibly blocked

This is the FIRST TIME the map appears in gameplay.
```



##

## NPC Reactions: Static vs. Reactive

### Static NPCs (Desensitized)

**Behavior**: Foreground image unchanged, NPCs remain motionless

```markdown
**Visual**: Nima stands exactly as before, no flinch

**Dialogue Response**:
"Looks like you really are new to the city.
You get used to it. We barely notice it now."

**Glyph Trigger**: [Aelitḧ] (stillness, acceptance)

```text
```text
```



**Variants (Choose Based on NPC Personality)**:
- Resigned: "Another wall falls, another path closes. We've stopped counting."
- Wry: "The city exhales. We breathe with it."
- Ritualized: "Collapse is just another rhythm."

### Reactive NPCs (Still Affected)

**Behavior**: Foreground image swaps to alternate (widened eyes, shifted posture, hands raised)

```markdown

**Visual**: Ravi's eyes widen, hand goes to chest

**Dialogue Response**:
"Did you feel that? The ground almost gave way!
It still shakes me every time."

**Glyph Trigger**: [Thalen̈] (longing) or [Querrä] (inquiry)

```text
```




**Variants**:
- Fearful: "I thought that was it. I thought we were finally coming down."
- Empathetic: "Are you alright? New arrivals always find this unsettling."
- Determined: "Another collapse means new opportunities. Stay alert."
##

## Player Dialogue Options During Collapse

### Immediate Reaction (Before NPC Speaks)

```markdown
**Player Shock Options**:

Option A: "What was that? Are you two okay!?"
- Glyph: [Thalen̈] (longing, concern)
- Shows: Player is sensitive, caring, but inexperienced
- NPC reads this as: "They're definitely new"

Option B: "I'm surprised you didn't even flinch."
- Glyph: [Querrä] (inquiry, observation)
- Shows: Player notices the disconnect between event and reaction
- NPC reads this as: "They're perceptive, already learning"

Option C: [Remain silent]
- Glyph: [Aelitḧ] (stillness, witness)
- Shows: Player is absorbing, not panicking
```text
```text
```



### NPC Closing Line (All Paths Converge)

```markdown

**Shared Dialogue**:
"We must be going. A new passageway may have opened up in the collapse.
We suggest you keep track of your surroundings.
The only constant here is change."

**Subtext**:
- Collapse is opportunity, not just disaster
- Paying attention matters

```text
```




**Tone Variants**:
- Ominous: "The city devours itself. Best not to be caught in its mouth."
- Hopeful: "Collapse opens doors. Keep your eyes sharp for what emerges."
- Ritualized: "The city remembers. We walk the broken paths. You will learn."
##

## Map Appearance & First Introduction

### Context
This collapse event is the **first time the player sees the map**. It's not just a UI element — it's a world-building moment.

### Map Visual Elements

```
┌─────────────────────────────────────┐
│   MARKETPLACE SECTORS               │
├─────────────────────────────────────┤
│  [Open Stalls] [Shrine]             │
│    ●(you)                           │
│  [Guard Post] ❌ [Collapsed Area]   │
│  [Healer]     [Black Market]        │
└─────────────────────────────────────┘

Legend:
● = Player position (glowing)
❌ = Collapsed/blocked area (red)
```text
```text
```



### Map Introduction Dialogue

```markdown

**NPC Points to Map**:
"She points to a worn cloth map, worn at the edges.
A red mark appears where the collapse occurred.

'This shows the sectors. See? Where we just were — now blocked.
But here, where the dust settles — a new passage, maybe.'

**Map appears in sidebar, persistent for rest of gameplay**

```


##

## Collapse Effects on Gameplay

### Accessibility Changes
- **Closed Areas**: Certain NPCs or items no longer accessible until area rebuilds
- **New Routes**: Alternative paths emerge, leading to new encounters
- **Temporary Blocks**: Some areas reopen after time/player action
- **Permanent Shifts**: Major collapses reshape the map for rest of game

### Glyph Impact
- **[Ruuñ] (Collapse)**: Glyphs associated with destruction, endings, letting go
- **[Sha'rú] (Repair)**: Glyphs associated with rebuilding, finding new paths
- **[Querrä] (Inquiry)**: Glyphs that trigger when player questions the city's changes
- **Combination Effects**: [Ruuñ] + [Sha'rú] together trigger resonance with NPCs who understand both loss and rebuilding

### NPC Behavior Shifts
- **Before Collapse**: NPCs in one area, dialogue about that sector
- **After Collapse**: NPCs may relocate or adopt new dialogue
- **Trust Implications**: If player helped an NPC before collapse, that NPC remembers (trust carries forward)
##

## Optional: Collapse Frequency & Progression

### Early Game (Rare)
- 1-2 major collapse events
- NPCs not yet accustomed to player's presence
- Collapse feels shocking to all

### Mid Game (Occasional)
- Collapses happen during key story beats
- Some NPCs show resignation, others still react
- Player begins to understand the pattern

### Late Game (Constant)
- Marketplace is visibly more unstable
- Most NPCs barely react anymore
- Map shows larger blocked areas
- New paths become crucial to navigation
##

## Implementation Checklist

- [ ] Create background image pairs (intact & collapsed versions)
- [ ] Ensure perspective consistency between pairs
- [ ] Build static vs. reactive foreground image variants for each NPC
- [ ] Write dialogue lines for both archetype responses
- [ ] Design map overlay graphics
- [ ] Integrate map reveal into collapse event flow
- [ ] Implement glyph triggers for collapse resonance
- [ ] Test visual swap smoothness in Streamlit
- [ ] Create collapse event module for easy reuse
