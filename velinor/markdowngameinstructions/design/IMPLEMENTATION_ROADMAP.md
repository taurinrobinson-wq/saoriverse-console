# Velinor: Comprehensive Implementation Roadmap

## Document Structure Overview

This roadmap outlines a complete development path for Velinor: Remnants of the Tone, organized into
phases with clear deliverables, technical requirements, and narrative integration points.

##

## Phase 1: Core Systems Foundation (Weeks 1-3)

### 1.1 TONE Stat System Implementation

**Objective**: Build the hidden stat tracking engine.

**Deliverables**:

- [ ] TONE stat tracker class (Trust, Observation, Narrative Presence, Empathy)
- [ ] Resonance overarching stat calculation
- [ ] Stat modification system (increment/decrement based on choices)
- [ ] Dev console display for testing

**Technical Tasks**:

- Create data structure to track per-player TONE stats
- Implement stat scaling (0-100 range, 50 = neutral)
- Create thresholds (low < 33, medium 34-66, high > 66)
- Log all stat changes for debugging

**Dependencies**: Game engine foundation

**Timeline**: 3 days

**Testing**:

- Verify stat changes persist across sessions
- Test threshold logic for NPC dialogue triggers
- Validate stat calculations in dev console

##

### 1.2 NPC Resonance System

**Objective**: Track individual NPC trust/resonance with player.

**Deliverables**:

- [ ] Per-NPC resonance score tracker
- [ ] Resonance threshold logic for dialogue branching
- [ ] NPC state persistence (remembered across encounters)

**Technical Tasks**:

- Create NPC resonance class
- Link TONE stats to NPC resonance changes
- Implement encounter memory system (NPC remembers previous interactions)
- Create resonance visualization (dev tool)

**Dependencies**: TONE stat system

**Timeline**: 3 days

**Testing**:

- Verify resonance changes affect dialogue
- Test memory persistence across encounters
- Validate NPC state changes persist in saves

##

### 1.3 Dialogue System with Branching

**Objective**: Build the narrative branching engine.

**Deliverables**:

- [ ] Dialogue parser (reads dialogue trees from markdown/JSON)
- [ ] Choice system with TONE stat impacts
- [ ] Conditional dialogue based on TONE thresholds
- [ ] Dialogue history logging

**Technical Tasks**:

- Create dialogue data format (JSON or custom)
- Implement choice resolution logic
- Build stat modifier system for choices
- Create dialogue UI mockup

**Dependencies**: TONE stat system, NPC resonance system

**Timeline**: 5 days

**Testing**:

- Test all dialogue branches for Ravi (first NPC)
- Verify TONE impacts are calculated correctly
- Test dialogue memory (NPC references past choices)

##

## Phase 2: Marketplace Foundation (Weeks 4-5)

### 2.1 Marketplace Environment & Layout

**Objective**: Create the hub location.

**Deliverables**:

- [ ] Marketplace environment art/UI
- [ ] NPC spawn zones (8 distinct locations within marketplace)
- [ ] Navigation system between zones
- [ ] Red X mark system (visual asset + collision logic)

**Technical Tasks**:

- Design marketplace layout (top-down or isometric view)
- Create 8 NPC spawn points with ambient idle animations
- Implement path blockage system (red X marks block routes)
- Create visual indicators for available routes

**Dependencies**: Game engine with scene management

**Timeline**: 4 days

**Testing**:

- Verify NPC appear in correct locations
- Test path blockage visibility and function
- Validate navigation feels smooth

##

### 2.2 The Eight NPCs: Core Implementation

**Objective**: Implement all 8 marketplace NPCs with basic dialogue.

**Deliverables**:

- [ ] Ravi: Complete dialogue tree + tools
- [ ] Nima: Complete dialogue tree + tools
- [ ] Tovren: Complete dialogue tree + tools
- [ ] Sera: Complete dialogue tree + tools
- [ ] Dalen: Complete dialogue tree + tools
- [ ] Mariel: Complete dialogue tree + tools
- [ ] Korrin: Complete dialogue tree + tools
- [ ] Kaelen: Complete dialogue tree + theft mechanic

**Technical Tasks**:

- Create dialogue files for each NPC (20-30 unique lines per NPC)
- Implement NPC resonance thresholds for each character
- Script NPC-specific mechanics:
  - **Ravi**: Gift tools based on Trust
  - **Nima**: Share secrets based on Empathy
  - **Tovren**: Offer repairs based on Observation
  - **Sera**: Teach rituals based on Empathy
  - **Dalen**: Propose quests based on Narrative Presence
  - **Mariel**: Share lore based on all stats
  - **Korrin**: Reveal gossip based on Observation
  - **Kaelen**: Steal items based on Observation counter

**Dependencies**: Dialogue system, TONE stat system

**Timeline**: 8 days (1 day per NPC + testing)

**Testing**:

- Test each NPC's full dialogue tree
- Verify tool gifting works correctly
- Test Kaelen's theft logic (should fail at high Observation)

##

### 2.3 NPC Sphere of Influence System

**Objective**: Implement ripple effects across NPC networks.

**Deliverables**:

- [ ] Sphere definition system (which NPCs belong to which spheres)
- [ ] Weighted connection calculation (ripple magnitude)
- [ ] Ripple effect application (update related NPCs when one changes)
- [ ] Sphere visualization (dev tool)

**Technical Tasks**:

- Create sphere relationship map (JSON/database)
- Implement ripple calculation algorithm
- Create ripple propagation system (cascading effects)
- Build dev tool to visualize current sphere states

**Dependencies**: NPC resonance system

**Timeline**: 4 days

**Testing**:

- Fracture trust with Ravi, verify Nima's suspicion rises
- Earn Nima's trust, verify Sera softens
- Test full cascade (change one NPC, watch ripples)

##

## Phase 3: Kaelen & Thieves' Arc (Weeks 6-7)

### 3.1 Kaelen the Cloaked (Extended)

**Objective**: Implement Kaelen's complex mechanics.

**Deliverables**:

- [ ] Kaelen's encounter system
- [ ] Theft mechanic (success/failure based on Observation)
- [ ] Player choice: Report to Veynar OR protect Kaelen
- [ ] Consequence tracking

**Technical Tasks**:

- Implement observation check system
- Create item theft system (which items can be stolen)
- Build choice consequence system
- Script dialogue variations based on player choice

**Dependencies**: Kaelen NPC implementation, TONE system

**Timeline**: 4 days

**Testing**:

- High Observation → theft fails, dialogue varies
- Low Observation + high Trust → theft succeeds
- Test both choice consequences (report vs. protect)

##

### 3.2 Captain Veynar Implementation

**Objective**: Create the authority counter-sphere to Kaelen.

**Deliverables**:

- [ ] Captain Veynar NPC with unique dialogue
- [ ] Guard sphere (Veynar + guard network)
- [ ] Item recovery mechanic (if player reports Kaelen)
- [ ] Veynar-Kaelen dialogue confrontation scene

**Technical Tasks**:

- Implement Veynar's dialogue options
- Create item recovery system
- Script the confrontation scene (can be optional to witness)
- Link Veynar's resonance to Kaelen's (inverse relationship)

**Dependencies**: Kaelen implementation, NPC sphere system

**Timeline**: 3 days

**Testing**:

- Verify reporting Kaelen returns items
- Test Veynar's dialogue variations
- Validate Veynar-Kaelen sphere relationship works

##

### 3.3 Drossel the Cloaked Leader

**Objective**: Implement thieves' lair boss encounter prep.

**Deliverables**:

- [ ] Drossel NPC definition (appearance, voice cadence)
- [ ] Slavic-French accent dialogue samples
- [ ] Side-flip mechanic (visual + code)
- [ ] Optional quest trigger (if Kaelen is trusted)

**Technical Tasks**:

- Create Drossel dialogue parser (tracks dialogue count for side-flips)
- Implement horizontal flip animation (scaleX transform)
- Build optional quest gate (unlocks only if Kaelen trust > threshold)
- Create swamp environment reference (for later implementation)

**Dependencies**: NPC system, optional quest framework

**Timeline**: 3 days

**Testing**:

- Test side-flip animation timing
- Verify optional quest only appears with high Kaelen trust
- Validate Drossel dialogue feels threateningyet charming

##

## Phase 4: Glyph & Chamber Systems (Weeks 8-10)

### 4.1 Triglyph System (Sorrow, Remembrance, Legacy)

**Objective**: Implement first boss chamber system.

**Deliverables**:

- [ ] Triglyph glyph objects (3 glyphs)
- [ ] Glyph fusion mechanic (combine 3 into chamber access)
- [ ] Chamber of Echoed Memory environment
- [ ] Boss encounter logic (emotional rather than combat)
- [ ] Unified glyph reward (Triangle with tear)

**Technical Tasks**:

- Create glyph inventory system
- Implement fusion detection (when player has all 3 triglyph glyphs)
- Build chamber entrance trigger
- Create unified glyph reward system
- Script emotional confrontation sequence (vs. combat-focused)

**Dependencies**: TONE system, glyph system foundation

**Timeline**: 6 days

**Testing**:

- Verify glyph fusion works (combines 3 into 1)
- Test chamber entrance restriction (requires 3 glyphs)
- Validate unified glyph appears and tracks correctly

##

### 4.2 Octoglyph System (8-stage emotional progression)

**Objective**: Implement advanced boss chamber system.

**Deliverables**:

- [ ] 8 octoglyph glyphs (one per emotional stage)
- [ ] Honeycomb panel UI (8 hexagonal slots)
- [ ] 8 individual chamber encounters (one per glyph)
- [ ] Unified glyph reward (Octagon with void symbol)
- [ ] Glyph panel visualization & animation

**Technical Tasks**:

- Create honeycomb panel UI component
- Build glyph placement system (drag-to-slot or auto-place)
- Implement chamber unlock logic (play chambers in any order after 1st)
- Create unified glyph panel completion detection
- Script panel animation (glows, pulses, resonates as glyphs are placed)

**Dependencies**: Triglyph system, advanced environment design

**Timeline**: 8 days (2 days per octoglyph chamber structure)

**Testing**:

- Verify honeycomb panel displays correctly
- Test glyph placement and removal
- Validate unified glyph creation on completion

##

## Phase 5: Journal System (Weeks 11-12)

### 5.1 Journal UI Implementation

**Objective**: Create the in-game memory device.

**Deliverables**:

- [ ] Blank parchment page asset (transparent background)
- [ ] Left page curl overlay (transparent)
- [ ] Right page curl overlay (transparent)
- [ ] Journal UI component (React-based)
- [ ] Page navigation logic
- [ ] Sound trigger for page turns

**Technical Tasks**:

- Render/procure parchment page assets
- Create page curl overlays as transparent PNGs
- Build React journal component
- Implement page turn animation (CSS transform)
- Integrate page turn sound (velinor_pageturn.mp3)
- Create animation timing (0.6s per page turn)

**Dependencies**: React UI framework, audio system

**Timeline**: 4 days

**Testing**:

- Verify journal appears in correct corner (upper left)
- Test page turn animation smoothness
- Validate sound plays on curl click
- Test with 1-10 pages (boundary testing)

##

### 5.2 Journal Entry Generator

**Objective**: Auto-populate journal with NPC encounters.

**Deliverables**:

- [ ] Entry formatter (name, sphere, resonance fact, summary)
- [ ] Text color system (red = key facts, brown = body text)
- [ ] Dynamic entry generation on NPC encounter
- [ ] Entry storage/persistence

**Technical Tasks**:

- Create entry data structure
- Build formatter function (highlight red words)
- Script entry generation on NPC dialogue completion
- Implement entry storage in player save file
- Create entry display component (render HTML with color)

**Dependencies**: NPC system, journal UI

**Timeline**: 3 days

**Testing**:

- Verify entries generate after each NPC encounter
- Test red highlighting for key facts
- Validate entries persist across saves

##

## Phase 6: Ending Systems (Weeks 13-14)

### 6.1 Final Chamber Environment

**Objective**: Create Saori's underground Corelink chamber.

**Deliverables**:

- [ ] Chamber environment art (glowing console, void ring, picture frames)
- [ ] Console UI (8 slots for octoglyph glyphs)
- [ ] Character positioning (Saori standing, Velinor seated)
- [ ] Ambient soundscape
- [ ] Picture frame assets (Saori & Velinor aged 25 years)

**Technical Tasks**:

- Design chamber layout
- Create console UI mockup
- Build lighting system (glyphs glow differently)
- Implement character animation states (standing, seated, dissolving)
- Create ambient sound layering

**Dependencies**: Advanced environment design, character animation

**Timeline**: 5 days

**Testing**:

- Verify environment loads correctly
- Test console UI functionality
- Validate lighting feels mystical and intimate

##

### 6.2 Six Ending Paths Implementation

**Objective**: Implement all six branching endings.

**Deliverables**:

- [ ] Ending 1: System Online (Trust path)
- [ ] Ending 2: Fragments Freed (Reconciliation path)
- [ ] Ending 3: Collapse Embraced (Exposure path)
- [ ] Ending 4: Cycle Broken (Destruction path)
- [ ] Ending 5: Sacred Withholding (Ambiguity path)
- [ ] Ending 6: Second Thoughts (Interrogation path)

**Technical Tasks**:

- Create branching dialogue tree (converges to final lines)
- Implement ending-specific visual sequences
- Script NPC reactions (varies by emotional lever)
- Build post-ending survival scenes
- Create ending-specific achievement unlocks

**Dependencies**: Final chamber environment, dialogue system

**Timeline**: 10 days (1.5 days per ending)

**Testing**:

- Playtest all 6 ending paths
- Verify emotional lever changes NPC reactions
- Validate final glyphs scatter/dissolve correctly
- Test save completion state

##

## Phase 7: Integration & Polish (Weeks 15-16)

### 7.1 Sound Design & Ambience

**Objective**: Layer complete soundscape.

**Deliverables**:

- [ ] Marketplace ambient loop
- [ ] Shrine ambient loop
- [ ] Chamber ambient layer
- [ ] NPC voice tone/accent samples
- [ ] Glyph chamber sound effects
- [ ] Page turn sound (already sourced)
- [ ] Collapse sound (structural failure)
- [ ] Memory dissolution sounds (for Fragments Freed ending)

**Technical Tasks**:

- Source/create audio assets
- Implement layered ambient system (varies by location)
- Create dialogue voice layer (not full VO, but tone/accent cues)
- Build dynamic soundscape (softens when player opens journal)
- Test audio mixing levels

**Dependencies**: Audio system foundation

**Timeline**: 4 days

**Testing**:

- Verify ambient loops seamlessly repeat
- Test voice tone cues match character personalities
- Validate sound levels don't overwhelm dialogue

##

### 7.2 Full Integration Testing

**Objective**: Verify all systems work together.

**Deliverables**:

- [ ] Complete playthrough from start to ending (all 6 paths)
- [ ] TONE stat tracking across full game
- [ ] NPC sphere ripple effects during full playthrough
- [ ] Journal functionality across full game
- [ ] Save/load persistence

**Technical Tasks**:

- Create test save states (at key points)
- Run full playthrough for each ending path
- Document any breaks or inconsistencies
- Fix bugs and edge cases
- Optimize performance

**Dependencies**: All previous phases

**Timeline**: 5 days

**Testing**:

- Full playthrough for each ending
- Save/load from each phase point
- Edge case testing (rapid stat changes, missing items, etc.)

##

## Phase 8: Optional Content & Deep Dives (Weeks 17-18)

### 8.1 Secret Knowledge Events

**Objective**: Implement NPC secret moments.

**Deliverables**:

- [ ] Nima's Secret Knowledge scene (if high Empathy + Trust)
- [ ] Ravi's Withdrawal scene (if high Trust fracture)
- [ ] Mariel's lore dump (if high all stats)
- [ ] Kaelen's trust-through-sacrifice moment
- [ ] Sera's ritual teaching sequence

**Technical Tasks**:

- Script rare encounter triggers
- Build secret scene UI/animation
- Implement conditional requirements (specific stat thresholds)
- Create unique rewards (fragments, tools, dialogue options)

**Dependencies**: NPC system, dialogue system

**Timeline**: 4 days

**Testing**:

- Verify secret triggers only fire at correct thresholds
- Test secret scene dialogue flow
- Validate rewards are received correctly

##

### 8.2 Boss Chamber Variants

**Objective**: Create alternative chamber encounters (optional higher difficulty).

**Deliverables**:

- [ ] Hard mode chambers (increased emotional complexity)
- [ ] Alternate glyph placement (non-linear chamber access)
- [ ] Bonus glyphs (hidden rewards for specific paths)

**Technical Tasks**:

- Design hard mode encounter logic
- Create alternative glyph unlock conditions
- Implement bonus reward system
- Test difficulty balance

**Dependencies**: Glyph chamber system

**Timeline**: 4 days

**Testing**:

- Verify hard mode unlocks correctly
- Test bonus glyph acquisition
- Balance difficulty vs. standard mode

##

## Development Timeline Summary

| Phase | Duration | Key Deliverable |
|---|---|---|
| Phase 1: Core Systems | Weeks 1-3 | TONE, Resonance, Dialogue systems |
| Phase 2: Marketplace | Weeks 4-5 | 8 NPCs, environment, sphere system |
| Phase 3: Kaelen Arc | Weeks 6-7 | Kaelen, Veynar, Drossel |
| Phase 4: Glyphs | Weeks 8-10 | Triglyph & Octoglyph systems |
| Phase 5: Journal | Weeks 11-12 | Journal UI & entry system |
| Phase 6: Endings | Weeks 13-14 | Final chamber, 6 ending paths |
| Phase 7: Integration | Weeks 15-16 | Audio, full testing |
| Phase 8: Polish | Weeks 17-18 | Secrets, variants, balance |
| **Total** | **~4.5 months** | **Complete game** |

##

## Critical Path Dependencies

```text
```


TONE System ↓ NPC Resonance ↓ Dialogue System ↓ Marketplace NPCs
    ├── NPC Sphere System
    └── Kaelen Arc
            ├── Veynar
            └── Drossel (prep for later)
↓ Journal System
                    ├── Glyph System
                    │   ├── Triglyph Chambers
                    │   └── Octoglyph Chambers
                    │           ↓
                    └── Final Chamber
                            ├── Saori & Velinor
                            └── 6 Ending Paths

```


##

## Success Metrics

- [ ] All 6 endings are reachable and emotionally distinct
- [ ] TONE stats never surface to player (hidden completely)
- [ ] Each NPC has 3+ unique dialogue variations based on resonance
- [ ] Sphere ripple effects are felt but not mechanical
- [ ] Journal entries are auto-generated and correctly formatted
- [ ] Glyph chambers feel like emotional confrontations, not puzzles
- [ ] Final scene with Saori & Velinor hits emotional resonance in testing
- [ ] No softlock states (player can always progress)
- [ ] Audio and visuals match emotional tone (no tonal clashing)
##

## Risk Mitigation

**Risk: Dialogue branching becomes unmanageable**

- *Mitigation*: Use dialogue tree tool (Yarn/ink), maintain clear branching maps

**Risk: TONE stats feel too hidden/invisible**

- *Mitigation*: Provide subtle feedback through NPC dialogue shifts, environment changes

**Risk: Ending branches feel forced rather than organic**

- *Mitigation*: Test extensively with diverse playstyles, ensure all paths feel earned

**Risk: Performance issues with complex NPC interactions**

- *Mitigation*: Profile early, optimize sphere calculation, cache frequently-accessed data

**Risk: Audio mixing overwhelms dialogue**

- *Mitigation*: Priority mixing (dialogue > ambient > effects), test with varied audio setups
##

## Next Steps

1. **Confirm scope** with team (4.5 months is realistic but aggressive)
2. **Set up version control** and project management (GitHub, Trello, etc.)
3. **Begin Phase 1** immediately (TONE system foundation)
4. **Weekly standups** to track progress and surface blockers
5. **Playtest early and often** (phases 2-3 onward)
##

## Files Created & Referenced

- `TONE_STAT_SYSTEM.md` — Core hidden stat mechanics
- `NPC_SPHERE_SYSTEM.md` — Network resonance and ripple effects
- `MARKETPLACE_NPC_ROSTER.md` — Full NPC definitions and dialogue hooks
- `VELINOR_SAORI_FINAL_ARC.md` — Friendship, sacrifice, and 6 ending paths
- `KAELEN_VEYNAR_THIEVES_ARC.md` — (To be created)
- `BOSS_CHAMBER_SYSTEM.md` — (To be created)
- `JOURNAL_SYSTEM.md` — (To be created)
- `ENDING_SEQUENCES.md` — (To be created)
