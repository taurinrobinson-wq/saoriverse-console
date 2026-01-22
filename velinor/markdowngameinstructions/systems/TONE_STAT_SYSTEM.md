# TONE Stat System

## Overview

The TONE stat system is the emotional core mechanic of Velinor: Remnants of the Tone. Every player
choice invisibly adjusts one or more TONE stats, shaping how NPCs respond, which glyphs unlock, and
which ending branches become available.

TONE stands for:

- **T** — Trust
- **O** — Observation
- **N** — Narrative Presence
- **E** — Empathy

These stats are never displayed to the player—they work silently in the background, creating
emergent gameplay where emotional resonance becomes mechanical.

##

## Core TONE Mechanics

### Trust (T)

- **Definition**: Hidden measure of how reliable the player feels to NPCs. Impacts whether guarded characters open up.
- **Increases When**: The player listens, keeps promises, sacrifices for others, shows restraint, protects secrets.
- **Decreases When**: The player betrays confidences, breaks promises, steals, or acts selfishly.
- **NPC Response**: High Trust → NPCs gift tools (Map of Echopaths), share memories, reduce suspicion. Low Trust → NPCs withhold information, refuse aid, spread distrust across their sphere.

### Observation (O)

- **Definition**: Tracks perception and wisdom. Governs subtle discoveries—gestures, glyph traces, hidden paths, NPC tells.
- **Increases When**: The player notices details, waits and watches, avoids impulsive choices, reads NPCs carefully.
- **Decreases When**: The player rushes, ignores clues, misses glyph signatures, acts blindly.
- **NPC Response**: High Observation → Glyph chambers reveal hidden exits, NPCs notice the player's attentiveness and soften. Low Observation → Player falls into traps, misses warnings, vulnerable to Kaelen's thefts.

### Narrative Presence (N)

- **Definition**: Reflects charisma and agency. Determines how boldly the player steps into encounters and how story branches unfold.
- **Increases When**: The player steps forward, engages directly, risks vulnerability, makes bold choices, inscribes glyphs.
- **Decreases When**: The player hesitates, withdraws, hides, chooses passivity.
- **NPC Response**: High Narrative Presence → Ravi tests the player with challenges, Drossel respects boldness, solo quests unlock. Low Narrative Presence → NPCs dismiss the player, opportunities close.

### Empathy (E)

- **Definition**: The heart of Velinor. Unlocks grief glyphs, deepens resonance, and allows NPCs to share fragile fragments.
- **Increases When**: The player listens to pain, validates loss, sits with grief, chooses vulnerability over performance, comforts others.
- **Decreases When**: The player dismisses suffering, rushes through emotional moments, prioritizes efficiency over connection.
- **NPC Response**: High Empathy → Nima shares secret knowledge, Sera teaches rituals, grief glyphs glow brighter. Low Empathy → Nima remains closed, shrine keepers distrust the player.

##

## Hidden Stat Framework

### Resonance (Overarching Stat)

- Reflects how attuned the player is to Velinor's emotional lattice.
- Increases when all four TONE stats are balanced and high.
- Unlocks the "Fragments Freed" ending when Resonance is sufficiently harmonized.
- Determines access to deeper NPC memories and glyph chambers.

##

## Example Stat Impacts: Marketplace Scene

**Player Thought**: "They're staring at me. What should I do?"

| Choice | Trust Impact | Observation Impact | Narrative Presence Impact | Empathy Impact |
|--------|---|---|---|---|
| Step toward the figures | +1 Trust | -1 Observation | +2 Narrative Presence | +1 Empathy |
| Keep your distance | +1 Wisdom | +2 Observation | -1 Narrative Presence | -1 Empathy |
| Explore the stalls | +1 Wisdom | +1 Observation | +1 Narrative Presence | +2 Empathy |
| Freeze and observe | Neutral | +2 Observation | Neutral | +1 Empathy |

##

## Integration with NPC Resonance

Each NPC has a private resonance score with the player based on TONE stats.

### Ravi's Resonance Triggers

- **High Trust**: Ravi gifts Map of Echopaths, warns of collapses.
- **High Narrative Presence**: Ravi tests the player with small challenges.
- **Low Trust**: Ravi becomes distant, his sphere (merchants) grows guarded.

### Nima's Resonance Triggers

- **High Observation**: Nima offers cryptic warnings about hidden dangers.
- **High Empathy**: Nima softens, shares pre-collapse memories.
- **High Trust + Empathy**: Nima reveals secret knowledge, teaches Bonded Gesture.
- **Low Empathy**: Nima remains closed; future encounters require emotional repair.

##

## Glyph Access Through TONE

Different glyphs respond to different TONE profiles:

| Glyph Category | TONE Requirement | Example Glyphs |
|---|---|---|
| Sovereignty Glyphs | High Observation, Medium Trust | Infrasensory Oblivion, Interruptive Restraint |
| Grief Glyphs | High Empathy, High Trust | Held Ache, Dislocated Attachment |
| Defiance Glyphs | High Narrative Presence, Low Empathy | Preemptive Severance, Collapse Embraced |
| Memory Glyphs | Balanced TONE (Resonance) | Sorrow, Remembrance, Legacy |

##

## TONE and Ending Branches

The final encounter with Saori and Velinor branches based on accumulated TONE profiles:

| Ending Path | TONE Requirements |
|---|---|
| **System Online** | High Trust, High Observation, Low Empathy |
| **Collapse Embraced** | High Narrative Presence, Low Trust, High Defiance |
| **Fragments Freed (Reconciliation)** | High Empathy, Balanced Resonance, High Trust |
| **Cycle Broken** | High Narrative Presence, High Empathy, High Defiance |
| **Sacred Withholding** | Selective high stats; player withholds key glyphs |
| **Second Thoughts** | Undecided TONE profile; ambiguity honored |

##

## Player Agency Through Hidden Stats

Because TONE stats are hidden, players don't optimize for them—they feel them. A player naturally
high in Empathy will make different choices than one high in Observation, and both will experience
genuinely different gameplay:

- **Empathy-focused player**: NPCs open up, glyphs bloom, world feels alive with connection.
- **Observation-focused player**: Discover hidden paths, see through deceptions (Kaelen's tricks fail), find secret chambers.
- **Narrative Presence player**: Bold encounters open, solo quests unlock, NPCs respect decisiveness.
- **Trust-focused player**: Networks deepen, ripple effects compound, sphere mechanics reward consistency.

This creates emergent narrative without the player feeling constrained by mechanical choices. The
stats serve the story, not the reverse.

##

## Integration Checklist

- [ ] Implement TONE stat tracking system in game engine
- [ ] Create hidden stat display (dev console only)
- [ ] Tie each NPC dialogue to TONE thresholds
- [ ] Map glyph unlock conditions to TONE combinations
- [ ] Design Kaelen's theft mechanic around Observation
- [ ] Script NPC resonance ripple effects based on sphere weights
- [ ] Create ending branch gating based on TONE profiles
- [ ] Test emergent gameplay with varying TONE profiles

---

## New Content Integration: Sera/Korrin & Malrik/Elenya

### Glyph of Shared Dawn — Trait & Gate Requirements

**Trigger Gates**:
- **Empathy** 50+ OR **Trust** 50+ (primary gate)
- **Presence** encounters with both Sera (2+) AND Korrin (2+)
- **Coherence** 50+ (player must be emotionally oriented enough to recognize the moment)

**Post-Encounter Trait Activation**:
- **Presence** trait unlocks new dialogue branch tier with both NPCs
- **Joy** trait deepens understanding of the catalytic nature of the encounter
- **Empathy** increases by 1-2 depending on player response path

**NPC Influence Gating (Post-Encounter)**:
- Sera influence 0.5+ AND Korrin influence 0.5+ → Unlocks "Grounded Presence" tool
- Grounded Presence tool requires Presence 70+ to use effectively
- Using tool allows player to sense NPC emotional authenticity across all marketplace encounters

### Glyph of Severed Covenant — Trait & Gate Requirements

**Trigger Gates** (Optional Arc):
- **Coherence** 70+ (player must recognize the emotional architecture)
- **Empathy** 70+ OR **Integration** 70+ (player must understand necessary trauma)
- 4+ encounters with Malrik (Archive sequences)
- 4+ encounters with Elenya (Shrine/ritual sequences)
- **Possession** of Glyph of Fractured Memory AND Glyph of Measured Step

**Post-Revelation Trait Activation**:
- **Legacy** trait unlocks new dialogue tier with both NPCs (understanding inherited loss)
- **Ache** trait deepens with Malrik (grief given articulation)
- **Presence** trait deepens with Elenya (witness to deliberate severance)

**Integration with Ending Paths**:
- If Malrik/Elenya revelation discovered AND both have high influence (0.85+): Unlocks alternative final passage where both contribute to player's emotional resolution
- Glyph of Severed Covenant becomes key to **Legacy** ending branch (recognizing what was lost and choosing to honor it)
- Both NPCs' final dialogue reflects integration of past into present identity

### Coherence Implications

**Shared Dawn Encounter**:
- Players with high **Joy** + high **Presence** already have balanced coherence
- If player exposes relationship: Coherence -3 (community fracture creates internal conflict)

**Malrik/Elenya Revelation**:
- Players must achieve Coherence 70+ to unlock arc (gated to emotionally integrated players)
- Discovering and facilitating encounter: Coherence +5 (integration of necessary loss)
- Ending path shifts toward **Legacy** or **Acceptance** branches
