# VELINOR DOCUMENTATION INDEX

Complete reference guide for all Velinor: Remnants of the Tone design documentation.
##

## Core System Documentation

### 1. **TONE_STAT_SYSTEM.md**

- **Purpose**: Define the four hidden emotional stats (Trust, Observation, Narrative Presence, Empathy)
- **Audience**: Developers, designers
- **Key Content**:
  - TONE stat definitions and impacts
  - Stat triggers and thresholds
  - NPC resonance connections
  - Glyph access requirements
  - Ending branch gating

**Start Here If**: You need to understand how player choices become mechanical impact.
##

### 2. **NPC_SPHERE_SYSTEM.md**

- **Purpose**: Define how NPCs are interconnected and how player choices ripple across networks
- **Audience**: Developers, narrative designers
- **Key Content**:
  - Sphere structure and weighted connections
  - Complete marketplace sphere map (8 NPCs + connections)
  - Ripple effect examples (fracturing trust, earning care)
  - Repair mechanics for broken relationships
  - Dynamic sphere shifts based on events

**Start Here If**: You need to understand NPC interconnection and cascade effects.
##

### 3. **MARKETPLACE_NPC_ROSTER.md**

- **Purpose**: Complete specification for all 8 marketplace NPCs
- **Audience**: Narrative designers, voice actors, character artists
- **Key Content**:
  - Appearance, age, personality for each NPC
  - Dialogue samples and resonance triggers
  - Tools/gifts each NPC offers
  - Quest hooks and optional content
  - Dynamic marketplace mechanics (red X marks, encounter rotation)

**Start Here If**: You're building NPC dialogue, designing encounters, or creating character art.
##

### 4. **VELINOR_SAORI_FINAL_ARC.md**

- **Purpose**: Complete narrative breakdown of the central relationship and all 6 endings
- **Audience**: Narrative designers, story leads, cinematics team
- **Key Content**:
  - Velinor and Saori's friendship history
  - The Cataclysm and Velinor's sacrifice
  - Final chamber layout and encounter setup
  - All 6 ending paths with dialogue variations
  - Emotional voltage analysis for each ending

**Start Here If**: You're writing the final story sequences or need to understand narrative branching.
##

## Implementation & Planning

### 5. **IMPLEMENTATION_ROADMAP.md**

- **Purpose**: Complete development schedule with phase-by-phase breakdown
- **Audience**: Project managers, tech leads, entire development team
- **Key Content**:
  - 8 phases spanning 4.5 months
  - Each phase has deliverables, technical tasks, timeline
  - Dependencies and critical path
  - Success metrics and risk mitigation

**Start Here If**: You're planning the project or need to understand development sequencing.
##

### 6. **EXECUTIVE_SUMMARY_AND_QUICKSTART.md**

- **Purpose**: High-level overview and quick-start guide for new team members
- **Audience**: Everyone (executives, developers, designers, artists)
- **Key Content**:
  - 30-second pitch
  - Three core pillars (TONE, Sphere, Glyphs)
  - Game statistics
  - Quick-start implementation order
  - Design philosophy summary

**Start Here If**: You're new to the project or need a comprehensive overview.
##

## Topic-Specific Deep Dives (To Create)

### 7. **KAELEN_VEYNAR_THIEVES_ARC.md** (Priority: HIGH)

- Kaelen the Cloaked complete specification
- Captain Veynar complete specification
- Drossel the Cloaked boss encounter
- Thieves' lair infiltration sequence
- Infiltration mechanics and puzzle design
##

### 8. **BOSS_CHAMBER_SYSTEM.md** (Priority: HIGH)

- Triglyph chamber (Sorrow, Remembrance, Legacy)
- Octoglyph chambers (all 8 emotional stages)
- Chamber design template
- Emotional encounter mechanics (vs. combat)
- Unified glyph rewards and visualization
##

### 9. **JOURNAL_SYSTEM.md** (Priority: MEDIUM)

- Journal UI mockup and asset specifications
- Page turn animation logic
- Entry auto-generation system
- Text formatting (red key facts, brown body)
- Sound design (page turn, parchment sounds)
- React/JS implementation guide
##

### 10. **ENDING_SEQUENCES.md** (Priority: HIGH)

- Complete dialogue scripts for all 6 endings
- NPC reaction variants (based on emotional lever)
- Visual sequences (glyph behavior, lighting, character animation)
- Sound design for each ending
- Camera angles and cinematics notes
##

## Reference Documents (Existing in Folder)

- `game_concept.md` — Original game vision (update with TONE system)
- `npcs.md` — General NPC framework (cross-reference with roster)
- `story_arcs.md` — Story progression (integrate with ending paths)
- `dialogue_banks.md` — Dialogue samples (feed entries into TONE implementation)
- `environments.md` — Location descriptions (add Saori's chamber)
- `achievements.md` — Achievement conditions (tie to ending paths)
##

## How to Use This Documentation

### For Narrative Designers

1. Start with **EXECUTIVE_SUMMARY_AND_QUICKSTART.md** (10 min read)
2. Read **VELINOR_SAORI_FINAL_ARC.md** (20 min, detailed)
3. Deep-dive **MARKETPLACE_NPC_ROSTER.md** (30 min, dialogue writing)
4. Reference **NPC_SPHERE_SYSTEM.md** for relationship mechanics (15 min)

### For Developers

1. Start with **EXECUTIVE_SUMMARY_AND_QUICKSTART.md** (10 min read)
2. Study **TONE_STAT_SYSTEM.md** thoroughly (25 min, design patterns)
3. Read **NPC_SPHERE_SYSTEM.md** for architecture (20 min)
4. Reference **IMPLEMENTATION_ROADMAP.md** for phasing (30 min)

### For Project Managers

1. Read **EXECUTIVE_SUMMARY_AND_QUICKSTART.md** (10 min, high-level)
2. Deep-dive **IMPLEMENTATION_ROADMAP.md** (45 min, scheduling)
3. Reference **TONE_STAT_SYSTEM.md** and **NPC_SPHERE_SYSTEM.md** for complexity estimates

### For Artists & Animators

1. Start with **EXECUTIVE_SUMMARY_AND_QUICKSTART.md** (10 min overview)
2. Read **MARKETPLACE_NPC_ROSTER.md** for character descriptions (20 min)
3. Reference **VELINOR_SAORI_FINAL_ARC.md** for final scene art direction (15 min)
##

## Key Numbers to Remember

| Metric | Count |
|---|---|
| Marketplace NPCs | 8 |
| TONE Stats | 4 (hidden) |
| Glyph Fragments | 70 |
| Triglyph Glyphs | 3 |
| Octoglyph Glyphs | 8 |
| Ending Paths | 6 |
| NPC Connections | 20+ |
| Dialogue Variations (per NPC) | 15-30 |
| Development Timeline | 4.5 months |
##

## Critical Design Principles

**Always Remember**:

1. **TONE stats are invisible** — Players never see numbers. They choose authentically.
2. **Every NPC is connected** — One choice ripples across spheres.
3. **Endings are all tragic** — No "good" ending. All paths honor something while destroying something.
4. **Memory is the theme** — Glyphs, journal, fragmentation, Saori's desperation all reinforce it.
5. **Relationship > Combat** — Emotional confrontations, not battles.
##

## Document Maintenance

**Last Updated**: December 14, 2025

**Documents Created in This Session**:

- ✅ TONE_STAT_SYSTEM.md
- ✅ NPC_SPHERE_SYSTEM.md
- ✅ MARKETPLACE_NPC_ROSTER.md
- ✅ VELINOR_SAORI_FINAL_ARC.md
- ✅ IMPLEMENTATION_ROADMAP.md
- ✅ EXECUTIVE_SUMMARY_AND_QUICKSTART.md
- ✅ DOCUMENTATION_INDEX.md (this file)

**Documents To Create**:

- ⏳ KAELEN_VEYNAR_THIEVES_ARC.md
- ⏳ BOSS_CHAMBER_SYSTEM.md
- ⏳ JOURNAL_SYSTEM.md
- ⏳ ENDING_SEQUENCES.md

**Documents To Update**:

- ⏳ game_concept.md (integrate TONE system)
- ⏳ npcs.md (cross-reference with roster)
- ⏳ story_arcs.md (integrate ending paths)
##

## Questions or Clarifications?

If any documentation is unclear, refer back to **EXECUTIVE_SUMMARY_AND_QUICKSTART.md** for the conceptual foundation, then return to the specific document.

For implementation questions, **IMPLEMENTATION_ROADMAP.md** provides phase-by-phase guidance.

For narrative questions, **VELINOR_SAORI_FINAL_ARC.md** and **MARKETPLACE_NPC_ROSTER.md** are your references.
##

## Next Steps

1. **Distribute** this documentation to entire team
2. **Schedule** team read-through (60-90 minutes)
3. **Begin Phase 1** (TONE system foundation) within 1 week
4. **Establish** weekly standups to track progress
5. **Create** branching task lists in project management tool (Trello/Asana/Linear)
##

**Welcome to Velinor. The fragments are scattered. Let's rebuild them.**
