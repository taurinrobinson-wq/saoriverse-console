# Velinor First Demo Sequence - Complete Plan

## Executive Summary

This document outlines the complete first act of Velinor, from initial meeting with Saori through the climactic Triglyph Puzzle and Memory Field sequence. The goal is to create a cohesive narrative demo that:

- Introduces 6 core NPCs (Saori, Ravi, Nima, Willy, Kaelen, Ressa)
- Guides player collection of 3 glyphs (Sorrow, Remembrance, Legacy)
- Culminates in solving the Triglyph Puzzle to unlock the Memory Field sequence
- Reveals the tragic backstory of Ophina's loss through three memory perspectives
- Unlocks the Transcendence Glyph as the reward/end-state

---

## Dialogue Sequence with Flag Flow

### 1. **saori_desert_encounter_01.json** ← START HERE
**Scene:** Desert_Saori_Meeting  
**Required Flags:** (none)  
**Sets Flags:**
- `codex_obtained` ← MUST HAVE for next dialogue
- `met_saori`
- `saori_desert_dialogue_complete`

### 2. Travel: DesertToMarket_00 → DesertToMarket_01 → InsideMarket_00

### 3. **ravi_nima_market_discovery.json**
**Scene:** InsideMarket_00  
**Required Flags:**
- `codex_obtained` ✓ (from Saori)
- `met_saori` ✓ (from Saori)

**Sets Flags:**
- `met_ravi_and_nima`
- `ravi_nima_dialogue_01_true`
- `sorrow_glyph_location_discovered`

### 4. Travel: InsideMarket_00 → InsideMarket_01 → InsideMarket_02

### 5. **willy_concourse_ruins.json** (Part 1)
**Scene:** ConcourseRuins_00  
**Required Flags:**
- `sorrow_glyph_location_discovered` ✓ (from Ravi/Nima)

**Sets Flags:**
- `willy_dialogue_started`
- `debris_cleared_sorrow_glyph`

### 6. **willy_concourse_ruins_payment.json** (Part 2 - Immediate)
**Scene:** ConcourseRuins_00  
**Required Flags:**
- `willy_dialogue_started` ✓ (from willy_concourse_ruins)

**Sets Flags:**
- `willy_dialogue_01_true` (also: `willy_dialogue_complete`)
- `sorrow_glyph_collected`

### 7. Travel: InsideMarket_02 → InsideMarket_01 → InsideMarket_00

### 8. **kaelen_confession_01.json**
**Scene:** InsideMarket_00 (Kaelen now visible due to SceneStateController)  
**Required Flags:**
- `willy_dialogue_01_true` ✓ (from Willy pt. 2)
- `sorrow_glyph_collected` ✓ (from Willy pt. 2)

**Sets Flags:**
- `kaelen_dialogue_01_true`
- `remembrance_glyph_location_discovered`

### 9. Travel: InsideMarket_00 → (exit west) → TBD_Remembrance_Location

### 10. **Player Collects Remembrance Glyph**
**Scene:** TBD_Remembrance_Location  
**Action:** GlyphPickup system handles collection  
**Sets Flag:** `remembrance_glyph_collected`

### 11. Travel: Back to InsideMarket_00

### 12. **nima_encounter_01.json**
**Scene:** InsideMarket_00  
**Required Flags:**
- `kaelen_dialogue_01_true` ✓ (from Kaelen)
- `remembrance_glyph_collected` ✓ (from glyph pickup)

**Sets Flags:**
- `nima_dialogue_01_true` (note: was `nima_encounter_01`)
- `family_photo_seen`
- `legacy_glyph_location_discovered`

### 13. Travel: InsideMarket_00 → (south) → TBD_Legacy_Glyph_Location (hole)

### 14. **ressa_legacy_glyph_01.json** (NEW - Needs Writing)
**Scene:** TBD_Legacy_Glyph_Location  
**Required Flags:**
- `legacy_glyph_location_discovered` ✓ (from Nima)

**Sets Flags:**
- `ressa_dialogue_complete`
- `legacy_glyph_collected`

### 15. Travel: Back up from hole → back to InsideMarket_00

### 16. **ravi_encounter_01.json**
**Scene:** DesertToMarketTrek_01 (outside market)  
**Required Flags:** (UPDATE THESE)
- `willy_dialogue_01_true` ✓ (from Willy)
- `ravi_nima_dialogue_01_true` ✓ (from Ravi/Nima)
- `kaelen_dialogue_01_true` ✓ (from Kaelen)
- `nima_dialogue_01_true` ✓ (from Nima)
- `codex_obtained` ✓ (from Saori)
- `sorrow_glyph_collected` ✓ (from Willy)
- `remembrance_glyph_collected` ✓ (from glyph)
- `legacy_glyph_collected` ✓ (from Ressa)

**Sets Flags:**
- `ravi_dialogue_01_true` (also: `ravi_final_dialogue_complete`)
- `compass_obtained`
- `triglyph_panel_location_known`

### 17. Travel: DesertToMarketTrek_01 → InsideMarket_01 → (4 mountain scenes) → MachinesCave_00_URP

### 18. **Triglyph Puzzle (Interactive)**
**Scene:** MachinesCave_00_URP  
**Mechanic:** Player places 3 glyphs in machine  
**Sets Flags:**
- `triglyph_puzzle_solved`
- `cave_door_opened`

### 19. **MachinesCave_01** (Transition - door closes)
**Sets Flag:** `point_of_no_return`

### 20-22. **Memory Field Sequence** (3 visits to MachinesCave_02)
1. Ravi & Nima's Memory
2. Kaelen's Memory  
3. Ophina's Memory

**Final Sets Flags:**
- `transcendence_glyph_obtained`
- `first_demo_complete`

---

## Flag Consistency Issues & Fixes

| File | Issue | Fix |
|------|-------|-----|
| ravi_nima_market_discovery | No set_flags | Add: met_ravi_and_nima, ravi_nima_dialogue_01_true, sorrow_glyph_location_discovered |
| willy_concourse_ruins | No required/set flags | Add required: sorrow_glyph_location_discovered; Add set: willy_dialogue_started, debris_cleared_sorrow_glyph |
| willy_concourse_ruins_payment | No required/set flags | Add required: willy_dialogue_started; Add set: willy_dialogue_01_true, sorrow_glyph_collected |
| kaelen_confession_01 | Requires `completed_willy` (wrong name) | Change to: willy_dialogue_01_true; Add set: kaelen_dialogue_01_true, remembrance_glyph_location_discovered |
| nima_encounter_01 | Requires `kaelen_confessed` (wrong name) | Change to: kaelen_dialogue_01_true, remembrance_glyph_collected; Add set: nima_dialogue_01_true, family_photo_seen, legacy_glyph_location_discovered |
| ravi_encounter_01 | Overly specific required_flags | Standardize to: willy_dialogue_01_true, ravi_nima_dialogue_01_true, kaelen_dialogue_01_true, nima_dialogue_01_true, codex_obtained, sorrow_glyph_collected, remembrance_glyph_collected, legacy_glyph_collected; Add set: ravi_dialogue_01_true, compass_obtained, triglyph_panel_location_known |

---

## Assets Needed

### Scenes to Create

1. **TBD_Remembrance_Glyph_Location** - Glyph location (1-2 hrs)
2. **TBD_Legacy_Glyph_Location** - Hole with Ressa (2-3 hrs)
3. **4x Mountain Trail Scenes** - Navigation to cave (2-3 hrs)
4. **MachinesCave_00_URP** - Triglyph Puzzle room (2-3 hrs)
5. **MachinesCave_01** - Transition/lock-in room (1-2 hrs)
6. **MachinesCave_02** - Memory Field chamber (3-4 hrs with all variations)

### Dialogues to Create

1. **ressa_legacy_glyph_01.json** - Ressa's dialogue in hole (1-2 hrs)

### Visual/Interactive Systems

1. **Triglyph Puzzle UI** - Glyph placement system (2-3 hrs)
2. **Comic Panel UI Framework** - Memory Field interactive (4-5 hrs)
3. **Projection Distortion Shader** - 3-state visual effect (2-3 hrs)
4. **Glyph Materialization Animation** - Transcendence reveal (1-2 hrs)

### Audio

1. Sound effects for debris clearing, rope rescue, door mechanisms, memory field transitions
2. Ambient music for cave system and memory sequences

### Graphics

1. Comic panel artwork for 3 memory sequences (24-36 panels total)
2. Ressa NPC character model
3. Triglyph Panel 3D model
4. Transcendence Glyph model
5. Environmental assets for hole and mountain scenes

---

## Gameplay Enhancements

| Feature | Difficulty | Time | Impact |
|---------|-----------|------|--------|
| Compass Navigation UI | Low | 1-2 hrs | Guides player, improves player agency |
| Debris Clearing Interaction | Medium | 2-3 hrs | More engaging than instant clear |
| Rope Climbing Mechanic | Medium-High | 3-4 hrs | Cinematic exit from hole |
| Comic Panel Hotspots | High | 5-7 hrs | Core memory field experience |
| Triglyph Placement Animation | Medium | 2-3 hrs | Satisfying puzzle completion |
| Collapsing Board Hazard | Medium | 2-3 hrs | Environmental storytelling |
| MindLog Auto-Population | Low-Medium | 2-3 hrs | Shows story progression |
| Projection Distortion Shader | Medium | 2-3 hrs | Visual progression feedback |

**Total Enhancement Time: 19-28 hours (optional for MVP)**

---

## Timeline

### Phase 1: Flag Consistency (THIS TASK) - 2-3 hours
Update all 7 dialogue files with correct required/set flags

### Phase 2: Scene Setup (Week 1) - 6-9 hours
- Remembrance location + glyph collection
- Legacy location + Ressa dialogue
- Mountain trail navigation scenes

### Phase 3: Cave System (Week 2) - 8-10 hours
- MachinesCave_00_URP with Triglyph UI
- MachinesCave_01 transition room
- MachinesCave_02 basic setup

### Phase 4: Memory Fields (Week 3) - 12-15 hours
- Comic panel UI framework
- 3 memory sequences with 24-36 panels
- MindLog integration
- Transcendence animation

### Phase 5: Polish (Week 4) - 6-8 hours
- Audio implementation
- Gameplay enhancements (if time)
- Testing and refinement

**Total MVP: 34-45 hours**

---

## Success Criteria

- [ ] All flagsflow logically through dialogue sequence
- [ ] Player collects all 3 glyphs and keeps them
- [ ] Triglyph Puzzle requires all 3 glyphs
- [ ] Memory Fields tell coherent story across 3 perspectives
- [ ] MindLog has 30+ entries by sequence end
- [ ] No soft-locks or dead-ends
- [ ] Playable from start to finish in 30-45 minutes
- [ ] All audio is implemented
- [ ] Demo is polished and bug-free

