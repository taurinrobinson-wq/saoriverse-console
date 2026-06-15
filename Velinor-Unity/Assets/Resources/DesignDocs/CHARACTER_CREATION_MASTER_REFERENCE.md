# Character Creation System: Master Reference

## Overview

**Velinor: Remnants of the Tone** features a **rare nonbinary character option** in its character creation system. The three options (Lior, Lioren, Lior(en)) are mechanically meaningful, narratively significant, and equally valid paths through the game.

This document serves as a quick reference and integration guide for all character creation components.

---

## Quick Navigation

| Need | Document |
|------|----------|
| UI/UX mockup & character selection flow | [character_selection_design.md](character_selection_design.md) |
| Technical implementation of pronoun swapping | [dialogue_pronoun_system.md](dialogue_pronoun_system.md) |
| Detailed profiles for each character variant | [character_variants_profiles.md](character_variants_profiles.md) |
| This master reference | (current file) |

---

## The Three Paths

### Path 1: LIOR (Male Variant)

**Starting Stats:** Coherence 40 | Empathy 55 | Observation 50 | Presence 45 | Memory 35

**Archetype:** The Quiet Observer  
- Direct, reserved, occasionally vulnerable
- Learns through precise attention and competence
- Drawn to institutional order (Malrik) and ritual presence (Elenya)
- Character arc: Acceptance of loss → Recognition of what matters

**Visual:** Lean, dark hair short, practical clothing, angular features  
**Pronouns:** he/him  
**NPC First Impressions:** Malrik (respects competence), Elenya (senses grief)

---

### Path 2: LIOREN (Female Variant)

**Starting Stats:** Coherence 41 | Empathy 56 | Observation 49 | Presence 46 | Memory 35

**Archetype:** The Reflective Healer  
- Thoughtful, emotionally available, grounded in intuition
- Learns through presence and emotional resonance
- Drawn to spiritual practice (Elenya) and philosophical challenge (Velinor)
- Character arc: Grief as teaching → Wisdom and integration

**Visual:** Lean, dark hair longer/braided, ritual-influenced clothing, expressive features  
**Pronouns:** she/her  
**NPC First Impressions:** Elenya (spiritual recognition), Velinor (intellectual respect)

---

### Path 3: LIOR(EN) (Nonbinary Variant)

**Starting Stats:** Coherence 40.5 | Empathy 55.5 | Observation 49.5 | Presence 45.5 | Memory 35

**Archetype:** The Becoming One  
- Flexible, code-switching, comfortable with uncertainty
- Learns through holding paradox and refusing easy categorization
- Drawn to both institutional (Malrik) and spiritual (Elenya) worlds; transcends both
- Character arc: Fragmentation → Integration (without resolution)

**Visual:** Lean, dark hair shoulder-length/unstyled, truly androgynous clothing, neutral features  
**Pronouns:** they/them (primary) or he/him or she/her (secondary choice)  
**Secondary Mechanic:** Upon selection, player chooses secondary name (Lior, Lioren, or Lior(en)) which affects NPC address and subtle stat/dialogue shifts

---

## Core Mechanics

### 1. Character Selection Screen Flow

```
Main Menu → "New Game"
  ↓
Character Selection Screen (shows all 3 variants equally)
  ↓
Select Lior or Lioren → Proceed to confirmation
  ↓
Select Lior(en) → Secondary name choice screen
  ├─ Choose "Lior" → Lior(en) variant with Lior stats
  ├─ Choose "Lioren" → Lior(en) variant with Lioren stats
  └─ Choose "Lior(en)" → Lior(en) variant with averaged stats + "they/them"
  ↓
Confirmation ("Is this your truth?")
  ↓
Game begins at marketplace arrival scene
```

### 2. Pronoun System (Dynamic Dialogue)

All dialogue references use **pronoun tokens** that swap at runtime:

```
Raw:      "Welcome, {player_name}. {player_he_she} works well."
Lior:     "Welcome, Lior. He works well."
Lioren:   "Welcome, Lioren. She works well."
Lior(en): "Welcome, Lior(en). They work well."
```

See `dialogue_pronoun_system.md` for full technical specs.

### 3. Stat Baselines & Progression

All variants start at Coherence ~40 (severely disoriented from recent grief). Stat progression differs slightly based on choices:

| Stat | Lior | Lioren | Lior(en) | Unlock At |
|------|------|--------|---------|-----------|
| Coherence | 40 | 41 | 40.5 | Independent decisions |
| Empathy | 55 | 56 | 55.5 | Supporting others |
| Observation | 50 | 49 | 49.5 | Pattern recognition |
| Presence | 45 | 46 | 45.5 | Standing up to authority |
| Memory | 35 | 35 | 35 | Glyph discoveries |

---

## Design Philosophy

### Why Three Options?

1. **Representation**: Nonbinary identity is not a default or compromise—it's a specific, intentional choice
2. **Mechanical Depth**: Each path has distinct stat baselines, dialogue tone, and NPC dynamics
3. **Narrative Validity**: All paths tell the same themes (love, loss, autonomy) through different lenses
4. **Player Agency**: Choice reflects player's own relationship to gender and identity

### Why These Specific Variants?

- **Lior**: Male identity with clear definition
- **Lioren**: Female identity with clear definition  
- **Lior(en)**: Nonbinary identity that exists between/beyond the binary options
- **Not "default + variants"**: All three are equally primary; no hierarchy

### Why Mechanical Differences Matter

- **Stat differences are small** (±1 point) but meaningful for certain encounters
- **Dialogue tone shifts** what NPCs prioritize (Malrik notices Lior's competence; Lioren's intuition; Lior(en)'s paradox)
- **NPC attunement varies**: Some NPCs are naturally more aligned with certain variants
- **Glyph resonance differs**: Some glyphs respond more strongly to certain gender expressions

---

## Implementation Checklist

### Phase 1: Setup
- [ ] Create character selection screen UI in Streamlit
- [ ] Store character choice in game state (variant + name + pronouns)
- [ ] Create player profile data structure
- [ ] Implement pronoun token system in dialogue engine

### Phase 2: Content Integration
- [ ] Convert all existing NPC dialogue to use pronoun tokens
- [ ] Create variant-specific dialogue for key NPCs (Malrik, Elenya, Velinor)
- [ ] Test pronoun replacement across all scenes
- [ ] Verify stat baseline consistency

### Phase 3: Polish
- [ ] Add visual art for all three character variants
- [ ] Create variant-specific opening scene reactions
- [ ] Implement intimate tension moments with all NPCs (awkward pauses, vulnerable questions, boundary recognition)
- [ ] Verify glyph resonance variations
- [ ] Test endgame Corelink choice with all variants

### Phase 4: Testing
- [ ] Play through complete game as each variant
- [ ] Verify pronoun consistency across 70+ glyphs
- [ ] Test NPC dialogue variations
- [ ] Confirm stat progression feels balanced

---

## Character Stat Comparison

### Lior (Direct, Observant)
- **Strong in:** Observation, adaptability to Malrik's system
- **Weak in:** Presence (quiet, not commanding), emotional expression
- **Best for:** Players who value quiet competence, methodical learning
- **Romance:** Slow-burn; builds through respect and eventual vulnerability

### Lioren (Reflective, Intuitive)
- **Strong in:** Empathy, spiritual resonance, commanding presence
- **Weak in:** Systematic thinking (learns through intuition first)
- **Best for:** Players who value emotional depth, relational learning
- **Romance:** Faster-burn; builds through emotional recognition

### Lior(en) (Flexible, Paradoxical)
- **Strong in:** Holding multiple perspectives, refusing categorization
- **Weak in:** None specifically; balanced across all dimensions
- **Best for:** Players who value complexity, rejecting binary choices
- **Romance:** Deepest with Elenya (who also transcends categories); unique with Malrik (who must learn paradox)

---

## NPC Response Variation

### Malrik (The Archivist)

| Variant | Initial | Growth | Final |
|---------|---------|--------|-------|
| Lior | "Competent worker" | Realizes he's lonely | Learns that precision can't hold love |
| Lioren | "Technically competent; confusing" | Realizes intuition is also precision | Learns to value what he can't categorize |
| Lior(en) | "Refuses categorization" | Frustrated then intrigued | Learns that paradox is not weakness |

### Elenya (The High Seer)

| Variant | Initial | Growth | Final |
|---------|---------|--------|-------|
| Lior | "Sees his quiet pain" | Becomes safe space | Profound mentorship; boundary honored |
| Lioren | "Recognizes spiritual peer" | Becomes teacher/mentor | Mutual spiritual recognition; deep mentorship |
| Lior(en) | "Sees one who is becoming" | Becomes mirror | Sacred partnership; profound understanding |

### Velinor (The Knowledge Keeper)

**Context:** Velinor is a former co-creator of the Corelink system who sacrificed her emotional coherence to mitigate the system's collapse damage. She has been cared for by Saori for 25 years. Despite her fragmentation, she remains deeply wise and capable of profound mentorship.

| Variant | Initial | Growth | Final |
|---------|---------|---------|--------|
| Lior | "Respectful listener" | Becomes philosophical companion | Deep intellectual mentorship; boundary honored |
| Lioren | "Capable of deep work" | Becomes intellectual peer | Mutual respect and understanding; mentorship |
| Lior(en) | "Appreciates complexity" | Becomes fellow paradox-holder | Recognition of shared non-linear wisdom; mentorship |

### Saori (The Caretaker & Mentor)

**Context:** Saori and Velinor created the Corelink system as brilliant teenagers. When it catastrophically activated, Velinor sacrificed herself to mitigate the damage. Saori has spent 25 years tending to Velinor's fragmentation, preserving her history, and holding her stable. Saori represents unconditional care that transcends typical relationship categories.

**In Game Canon:** Saori gives the Codex to the player directly in a desert encounter, becoming a mentor figure who contextualizes the game's mechanical and spiritual systems.

**In GN Canon:** Saori is absent from Volume 1 but is referenced through legend and ritual. Her eventual appearance becomes a major narrative payoff.

---

## Key Design Decisions

### 1. Pronouns Are Character, Not Cosmetic

- Pronouns affect how NPCs perceive and interact with the player
- Stat baselines reflect how different gender expressions navigate the world
- Dialogue itself shifts based on pronouns (institutional respect, spiritual recognition, etc.)

### 2. Nonbinary Is Specific, Not Default

- "Lior(en)" is not a compromise or middle ground
- It's a specific identity with its own stat profile and narrative function
- Secondary name choice adds extra layer of player agency within nonbinary path

### 3. All Paths Lead to Same Themes

- Every variant grapples with love, loss, autonomy, and systems
- The game's story doesn't change; the lens through which it's viewed does
- Endgame choice (Restart vs. Abandon Corelink) is available to all variants

### 4. Visual Differentiation Without Oversexualization

- Variants differ in hair length, clothing aesthetic, and presentation
- No variants are sexualized or reduced to sexual appeal
- All variants are competent, capable, and worthy protagonists

---

## Mentorship & Intimate Tension (Variant-Specific Notes)

### Relationship Framework (Age-Gap Considerations)

All NPCs are 50-60s; protagonist is 20s. This age gap prevents romantic pursuit but creates space for:
- Deep mentorship and spiritual guidance
- Occasional awkward pauses when connection feels too intimate
- Questions about the protagonist's own capacity for love (reflective, not pursued)
- Moments of recognition that transcend romance

**Philosophy:** The NPCs care about the protagonist but respect the boundary. Intimacy is acknowledged, not acted upon.

### Variant-Specific Mentorship Dynamics

**Lior's Mentorships:**
- **Elenya:** Becomes a sanctuary figure; teaches him feeling is not weakness. Occasional moment where her tenderness toward him is noticed but not crossed.
- **Velinor:** Intellectual mentor who gradually asks personal questions. Brief moment where Lior realizes Velinor genuinely cares about her wellbeing.
- **Malrik:** Discipleship relationship; Lior learns both from Malrik's precision and observes his hidden loneliness. Moment of mutual recognition when Malrik admits vulnerability.

**Lioren's Mentorships:**
- **Elenya:** Mutual spiritual growth; Lioren is Elenya's peer-student. Moment where Elenya's hand lingers too long, then both acknowledge the boundary.
- **Velinor:** Deep intellectual partnership; Velinor asks Lioren about love and loss. She answers, and she listens with unexpected tenderness.
- **Malrik:** Lioren challenges his rigidity; Malrik is drawn to her authenticity. Moment where he nearly says something personal, then catches himself.

**Lior(en)'s Mentorships:**
- **Elenya:** Mutual recognition of existing between states. Occasional moment of profound understanding that feels almost intimate.
- **Velinor:** Both hold paradox; they understand each other's complexity. Moment where Velinor admits she's unsure if what she feels is mentorship or something else (and chooses mentorship).
- **Malrik:** Lior(en) represents everything he can't categorize. Moment where Malrik asks directly: "Have you ever loved someone? Truly?"

---

## Accessibility Notes

### For Players Exploring Identity

- Character selection offers a safe space to try on different gender expressions
- The game validates that all three paths are equally legitimate
- Choosing nonbinary early signals to the game: "I honor complexity"

### For Nonbinary Players

- Lior(en) is a full, fleshed-out character with agency and depth
- The nonbinary option is not an "extra" or "alternative"—it's primary
- Game content (romance, mechanics, NPC recognition) is fully accessible to nonbinary player

### For Cisgender Players

- Lior and Lioren offer gender-typical character expressions without stereotyping
- Stats differ minimally; gender doesn't gatekeep ability
- Players can learn about nonbinary identity through encountering Lior(en) as NPC or playing that path

---

## File Structure

```
velinor/markdowngameinstructions/character_creation/
├── character_selection_design.md (UI/UX, flow, stat baselines)
├── dialogue_pronoun_system.md (technical implementation)
├── character_variants_profiles.md (full character details)
└── CHARACTER_CREATION_MASTER_REFERENCE.md (this file)
```

---

## Integration with Existing Systems

### Player Profile Structure

```python
PLAYER = {
    "character_variant": "lior" | "lioren" | "lior(en)",
    "character_name": "Lior" | "Lioren" | "Lior(en)",
    "pronouns": "he/him" | "she/her" | "they/them",
    "stats": {
        "coherence": 40,
        "empathy": 55,
        "observation": 50,
        "presence": 45,
        "memory": 35,
    },
    "npc_attunement": {
        "malrik": 0.05,
        "elenya": 0.15,
        "velinor": 0.10,
        "ravi": 0.20,
    },
    # ... other game state fields
}
```

### Dialogue Integration

When displaying dialogue:
```
1. Load raw dialogue with tokens: "{player_name} shows {player_his_her} work."
2. Look up player pronouns: player.pronouns = "they/them"
3. Replace tokens: "Lior(en) shows their work."
4. Display: MALRIK: "Lior(en) shows their work."
```

---

## Success Metrics

### Design Goals
- ✅ Nonbinary option feels as full and complete as gendered options
- ✅ Pronouns affect gameplay (dialogue, NPC interaction, mechanics)
- ✅ All three paths tell meaningfully different stories
- ✅ No gender locks on content (romance, glyphs, endings)

### Testing Goals
- ✅ Pronoun consistency across all 70+ glyphs and 100+ NPC dialogues
- ✅ Character variant stats reflect intended differences
- ✅ NPC attunement progression feels natural for each variant
- ✅ Players report feeling their character choice was meaningful

---

This system establishes that **Velinor honors multiple truths about gender and identity** while maintaining mechanical depth, narrative significance, and player agency.

**All paths are equally valid. All paths are equally real.**
