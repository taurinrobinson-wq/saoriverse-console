# Velinor: Ink Narrative Engine - README

**Project:** Velinor: Remnants of the Tone - Act I Vertical Slice  
**Platform:** Ink (Inkle's narrative scripting language)  
**Status:** 🟢 Ready to Write  
**Current Focus:** Act I story content development  

---

## Overview

This folder contains the Ink-based narrative engine for Velinor. It's a complete, playable story structure with mechanical systems baked in:

- **TONE system:** 4 emotional stats that drive all dialogue
- **Coherence:** Emotional harmony calculation (gates determine what's accessible)
- **Influence:** NPC relationship tracking with cascade mechanics
- **Glyphs:** 3-tier emotional artifact system
- **Flows:** All major scenes scaffolded, ready for content

---

## File Structure

```
velinor-story/
├── main.ink                    # Entry point (includes all files)
├── tone_system.ink            # TONE variables, coherence formula
├── npc_profiles.ink           # All NPC dialogue (Saori, Ravi, Nima)
├── glyph_reveals.ink          # 3-tier glyph system (3 glyphs implemented)
├── gates.ink                  # Gate checking functions
├── utilities.ink              # Math helpers, state export
├── marketplace.ink            # Hub scenes, locations
└── README.md                  # This file
```

### What's Each File For?

**main.ink**
- Entry point, includes all sub-files
- Routes to first scene
- Contains testing menu (optional)

**tone_system.ink**
- All 21 TONE + Influence variables
- Coherence calculation
- TONE adjustment functions
- Cascade influence system

**npc_profiles.ink**
- Saori encounter (fully written, multi-path)
- Ravi dialogue (fully written, 6 variations)
- Nima dialogue (fully written, 5 variations)
- All NPCs show correct emotional depth + gating

**glyph_reveals.ink**
- 3 glyphs fully implemented (Promise Held, Collapse Moment, Fierce Joy)
- Each shows 3-tier system (hint → context → plaintext)
- Tier 3 locked behind emotional gates
- Ready to expand to 118 glyphs

**gates.ink**
- `check_coherence_gate(threshold)`
- `check_tone_gate(stat, threshold)`
- `check_influence_gate(npc, threshold)`
- Helper functions for gating dialogue

**utilities.ink**
- Math: `absolute()`, `round()`, `clamp()`, `average()`
- Coherence calculation engine
- TONE stat lookup functions
- Flavor text generators
- JSON export template

**marketplace.ink**
- Central hub (decision point)
- 5 locations (market stalls, shrine, collapsed building, archive, rest)
- NPC encounters (Rasha, Nordia, Vera, Malrik, Sealina)
- All scaffolded, most need content expansion

---

## Quick Start

### 1. Install Ink Editor (5 min)

**Option A: Inky Desktop (Recommended)**
- Download: https://github.com/inkle/inky/releases
- Install, launch
- Open `main.ink`
- Click "Build", then "Play"

**Option B: VS Code**
- Install "Ink" extension
- Open `main.ink`
- Right-click → "Run Story"

**Option C: Web Editor**
- https://www.inklestudios.com/ink/web-editor/
- Paste `main.ink` content
- Click Build → Play

### 2. First Playthrough (45 min)

1. Open `main.ink` in editor
2. Click Build
3. Click Play
4. Go through: Saori → Marketplace → Ravi/Nima → Final stats
5. Make different choices on second playthrough
6. Watch TONE stats change and coherence shift
7. Try to unlock deep NPC dialogue (requires high coherence + influence)

### 3. Explore the System

Test the TEST_SCENE_SELECT menu:
- Uncomment `-> TEST_SCENE_SELECT` at end of main.ink
- Play story again
- Jump directly to any scene
- Test individual dialogues without full playthroughs
- Check how gates work

---

## How It Works

### TONE Stats (4 Emotional Dimensions)

| Stat | Meaning | Increases When |
|------|---------|-----------------|
| **Empathy** | Compassion, openness | "I want to help" choices |
| **Skepticism** | Critical thinking | "Why should I believe?" choices |
| **Integration** | Holding contradictions | "Both are right" choices |
| **Awareness** | Self-understanding | "I need to understand myself" choices |

**Example Choice Impact:**
```
Choice: "I want to help you rebuild, together"
  → Empathy +8
  → Integration +5
  → Awareness +3
  → Coherence recalculates
```

### Coherence (Emotional Harmony)

```
Formula: Coherence = 100 - average_deviation(E, S, I, A)

High (80+): Integrated, can hold multiple truths
Medium (50-80): Growing balance
Low (0-50): Fragmented, conflicted
```

**Why it matters:** Gates require coherence thresholds. Deep NPC dialogue is locked unless you're emotionally integrated.

### Gates (What's Accessible)

Three types of gates control dialogue:

**1. Coherence Gate**
```ink
{coherence >= 70:
    [Deep dialogue appears]
- else:
    [Surface dialogue appears]
}
```

**2. TONE Gate**
```ink
{tone_empathy >= 70:
    [Empathetic dialogue appears]
- else:
    [Neutral dialogue appears]
}
```

**3. Influence Gate**
```ink
{influence_ravi >= 0.6:
    [Ravi shares personal story]
- else:
    [Ravi is cautious]
}
```

### Glyphs (Emotional Artifacts)

Each glyph reveals in 3 tiers:

**Tier 1 (Hint):** Always visible, emotional signal only  
**Tier 2 (Context):** After meeting relevant NPC, narrative meaning emerges  
**Tier 3 (Plaintext):** Emotionally gated, full emotional truth unlocks  

**Example: The Promise Held**
```
Tier 1: ◈ (soft blue circles) - "Something constant is present"
Tier 2: Ravi speaks → "Companionship held steadily"
Tier 3: (Req: Coherence 70+, Empathy 70+, Influence[Ravi] 0.6+)
        Full meaning: "To be held in another's attention..."
```

### Influence (Relationship Tracking)

Each NPC has influence 0.0-1.0 (default 0.5):
- **Increases:** When choices align with NPC's values
- **Decreases:** When you contradict their stance
- **Cascades:** When Ravi's influence rises, Nima's rises partially (they're partners)

---

## Story Structure (What's Where)

### ACT I: Arrival & Calibration

**Fixed Beats (Already Written):**
1. **Saori Encounter** (npc_profiles.ink)
   - 4 different paths based on emotional approach
   - Introduces TONE system organically
   - Sets up glyph collection motivation

2. **Marketplace Hub** (marketplace.ink)
   - Central location, 5 locations to explore
   - Introduction to community
   - Feel of functional post-collapse society

3. **Ravi Dialogue** (npc_profiles.ink)
   - Grieving parent, marketplace anchor
   - 3 conversation paths (skeptical, empathetic, reflective)
   - Influence mechanics demonstrated
   - Glyph "The Promise Held" appears

4. **Nima Dialogue** (npc_profiles.ink)
   - Protective, authenticity-testing
   - Requires trust-building
   - Shows how coherence affects dialogue

**Fluid Elements (Outlined, Expandable):**
- Other marketplace NPCs (Rasha, Nordia, Vera, Malrik, Sealina)
- 5 location explorations
- Optional encounters
- Branching based on player choices

---

## Writing Guide

### How to Add New Dialogue

**1. Create a new knot:**
```ink
=== my_new_scene ===
The scene description goes here.

* [Choice 1 text] 
    ~ adjust_tone("empathy", 8)
    -> next_knot
    
* [Choice 2 text]
    ~ adjust_tone("skepticism", 8)
    -> next_knot
```

**2. Add gating if needed:**
```ink
=== my_gated_dialogue ===
{coherence >= 70:
    [Deep dialogue]
- else:
    [Surface dialogue]
}
```

**3. Include influence tracking:**
```ink
=== npc_dialogue ===
* [Agree with NPC values]
    ~ cascade_influence("npc_name", 0.15)
    -> response
    
* [Disagree]
    ~ cascade_influence("npc_name", -0.1)
    -> response
```

**4. Add TONE adjustments:**
```ink
* [Act with empathy]
    ~ adjust_tone("empathy", 8)
    ~ adjust_tone("awareness", 3)
    ~ coherence = calculate_coherence()
    -> next_scene
```

### Dialogue Template (For Consistency)

```ink
=== npc_encounter ===
[Scene setup - 2-3 sentences]

[NPC introduction and initial mood]

* [Empathy option - shows care/vulnerability]
    ~ adjust_tone("empathy", 8)
    ~ cascade_influence("npc_name", 0.1)
    ~ coherence = calculate_coherence()
    -> npc_responds_warmly
    
* [Skepticism option - asks hard questions]
    ~ adjust_tone("skepticism", 8)
    ~ cascade_influence("npc_name", -0.05)
    ~ coherence = calculate_coherence()
    -> npc_respects_doubt
    
* [Integration option - holds both sides]
    ~ adjust_tone("integration", 10)
    ~ cascade_influence("npc_name", 0.15)
    ~ coherence = calculate_coherence()
    -> npc_sees_you

=== npc_responds_warmly ===
[Dialogue that feels opened, vulnerable]
-> continue

=== npc_respects_doubt ===
[Dialogue that respects skepticism, less personal]
-> continue

=== npc_sees_you ===
[Dialogue that honors synthesis, deepest connection]
-> continue
```

---

## Testing Checklist

Before moving on to next scene, verify:

- [ ] All choices lead somewhere (no dangling branches)
- [ ] TONE stats track correctly (check at end)
- [ ] Coherence updates after each choice
- [ ] Influence cascades properly (test in gates.ink functions)
- [ ] Dialogue changes based on gates (test multiple playthroughs)
- [ ] Glyphs appear at right moments
- [ ] NPC personality consistent across scenes
- [ ] No undefined variables or broken links

---

## Playtesting

See **PLAYTESTING_GUIDE_INK.md** for:
- How to test gates
- How to test glyphs tiers
- How to test cascading influence
- Scenarios (high coherence, low coherence, stat-focused)
- Debugging tips
- How to export to JSON for backend

---

## Word Count & Scope

**Current State:**
- Saori encounter: ~1,200 words
- Ravi dialogue: ~2,000 words
- Nima dialogue: ~1,800 words
- Marketplace scenes: ~3,000 words (scaffolded)
- Glyph system: ~1,500 words
- **Total: ~10,000 words (rough draft, needs Polish)**

**Target for Act I:**
- **Total: 15,000-20,000 words**
- This is 2-3x current, achievable in 2-3 weeks of focused writing

**Reading time:** 45-60 minutes for one playthrough

---

## Next Phase: Acts II, III, IV, V

Once Act I is solid:

1. **Archive Arc (Act II):** Malrik & Elenya romance, factional debate
2. **Exploration (Act III):** 5 biome zones, optional NPC encounters
3. **Descent (Act IV):** Underground, Saori & Velinor revelation
4. **Chamber (Act V):** Final choice, 6 ending variants

Each act would be new Ink file or new section in main.ink.

---

## Integration with Backend

When ready to connect to Python API:

1. **Export JSON:**
   - In Inky: File → PlayButton → Export JSON
   - Name: `velinor_act_i.json`

2. **Drop in Python:**
   - Copy to `velinor/stories/`
   - Update `engine/twine_adapter.py` to load new JSON

3. **Test API:**
   - Start Python server
   - Call `/api/game/start`
   - Game state should include TONE stats, glyphs, influence

4. **Frontend Integration:**
   - React reads game state from API
   - Displays TONE stats in StatusHud
   - Shows glyphs in GlyphDisplay component
   - Updates dialogue in DialogueBox

---

## Resources

**Ink Documentation:** https://github.com/inkle/ink/blob/master/Documentation/WritingWithInk.md

**Inky Editor:** https://github.com/inkle/inky

**Ink Web Editor:** https://www.inklestudios.com/ink/web-editor/

**Velinor Project Docs:**
- `INK_EVALUATION_AND_MIGRATION.md` — Why Ink, migration plan
- `PLAYTESTING_GUIDE_INK.md` — How to test, debug, iterate
- `VELINOR_COMPREHENSIVE_DOCUMENTATION.md` — Full game design reference
- `FIRSTPERSON_E2E_ARCHITECTURE.md` — How FirstPerson integrates

---

## Quick Commands

**Compile & Run:**
```bash
# In Inky: Click Build → Play button

# In VS Code with Ink extension:
# Right-click on file → Run Story

# Via command line (if Ink is installed):
inklecpp main.ink -o output.json
```

**Export for Backend:**
```
In Inky: File → Play → Export JSON
Save as: velinor_act_i.json
```

---

## Status Summary

✅ **Complete:**
- TONE system (variables, calculations, adjustments)
- Coherence formula (fully functional)
- Gate system (coherence, TONE, influence)
- Influence tracking with cascade
- Glyph 3-tier system (3 example glyphs)
- Saori encounter (fully written, 4 paths)
- Ravi dialogue (fully written, 6 variations)
- Nima dialogue (fully written, 5 variations)
- Marketplace hub (scaffolded)
- Testing infrastructure (TEST_SCENE_SELECT, stat checking)

🟡 **Partial:**
- Marketplace locations (5 locations, most scaffolded, need content)
- Additional NPCs (dialogue templates, need expansion)
- Additional glyphs (data exists, need tiers written)

🔴 **Not Started:**
- Acts II, III, IV, V
- 115+ additional glyphs
- Ending passages (6 variants)
- Multiplayer support (designed but not written)
- UI animations (React side, not Ink side)

---

## Contact & Questions

Goal: Complete, playable Act I in **4 weeks**.

This Ink project is ready. The work ahead is *content writing*—dialogue, passages, glyph moments, ending narratives.

No technical blockers. No missing infrastructure.

**Just write. The foundation is solid.**

---

**Last Updated:** February 24, 2026  
**Version:** 1.0 Launchable  
**Status:** 🚀 Ready for production
