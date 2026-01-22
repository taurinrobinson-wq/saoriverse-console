# Velinor Infusion Session 2: Quick Implementation Map

## What Was Added

### New Glyphs

#### Glyph of Shared Dawn (ID #76)
- **Domain**: Joy
- **Type**: Presence + Joy hybrid
- **NPCs**: Sera the Herb Novice & Korrin the Gossip
- **Location**: Market courtyard at first light
- **Trigger Gate**: Empathy 50+ OR Trust 50+; Coherence 50+; 2+ encounters with each NPC
- **Mechanic**: Three-path encounter (Observe / Approach / Expose)
- **Tool Unlock**: Grounded Presence (requires Sera/Korrin influence 0.5+ each + Presence 70+)
- **Files Modified**: 
  - Glyph_Organizer.csv (row 76)
  - Glyph_Organizer.json (entry 76)

#### Glyph of Severed Covenant
- **Domain**: Ache
- **Type**: Ache + Legacy hybrid
- **NPCs**: Archivist Malrik & High Seer Elenya
- **Location**: Archive chamber (primary) / Shrine (secondary)
- **Trigger Gate**: Coherence 70+; Empathy 70+ OR Integration 70+; 4+ encounters each; Glyph of Fractured Memory + Glyph of Measured Step
- **Mechanic**: Five-stage revelation (Subtle Recognition → Body Remembers → Archive Revelation → Elenya's Admission → Facilitated Encounter)
- **Tool Unlock**: None (but unlocks alternative ending variation)
- **Status**: Currently referenced in story_arcs.md; needs glyph entry creation in data files

---

## NPC Profile Modifications

### Sera the Herb Novice

**Pre-Infusion Profile** (lines 128-165 in MARKETPLACE_NPC_ROSTER.md):
- Role: Shrine acolyte, Empathy-aligned
- Traits: Gentle, curious, shy initially, warm once trust built
- Tools: Flicker Ritual, Healing Salve
- Resonance Triggers: High Empathy, Low Empathy, Pairing with Nima

**Post-Infusion Additions**:
- New Appearance Detail: "After the Shared Dawn encounter, she carries herself with slightly more openness"
- New Personality Note: "Post-Shared Dawn: slightly more grounded, less tentative, more willing to laugh"
- New TONE Affinity: Added Presence (post-Shared Dawn)
- New Tool: Grounded Presence (unlocked post-encounter if high influence with both)
- New Sample Dialogues: Post-Shared Dawn reflection lines (3 new options)
- New Quest Hooks: Shared Dawn encounter, Post-Shared Dawn reflection dialogue
- New Resonance Trigger: "Pairing with Korrin (Post-Shared Dawn)"
- New Influence Modifications: Path A (+0.20), Path B (+0.10), Path C (-0.15)

### Korrin the Gossip

**Pre-Infusion Profile** (lines 240-285 in MARKETPLACE_NPC_ROSTER.md):
- Role: Informant, rumor-spreader, Observation-aligned
- Traits: Nervous, always seeking angles, not malicious
- Tools: Rumor of Routes, Gossip Protection
- Resonance Triggers: High Observation, High Trust (near impossible), Fractured with Merchants

**Post-Infusion Additions**:
- New Appearance Detail: "Post-Shared Dawn, the scarf is noticeably brighter; sits more still sometimes, eyes softer"
- New Personality Note: "Post-Shared Dawn: slightly less manic, more capable of genuine quiet, more protective of things that matter"
- New TONE Affinity: Added Presence (post-Shared Dawn)
- New Tool: Sacred Silence (unlocked post-Shared Dawn if high influence; paradoxically, gossip-man becomes keeper of confidences)
- New Sample Dialogues: Post-Shared Dawn reflection lines (3 new options)
- New Quest Hooks: Shared Dawn encounter, Post-Shared Dawn reflection dialogue
- New Resonance Trigger: "Pairing with Sera (Post-Shared Dawn)" with important note about Trust ceiling increase
- New Influence Modifications: Path A (+0.25, strongest), Path B (+0.10), Path C (-0.20, most severe loss)
- **Key Change**: Post-Shared Dawn, Trust can reach 0.65 instead of ceiling at 0.50

### Malrik & Elenya Updates

**New Plot Layer**:
- Pre-collapse relationship (optional discovery)
- Memory severance (Elenya's deliberate choice)
- Five-stage revelation progression
- Facilitated encounter at endgame
- Alternative ending branch participation

**Files Modified**:
- MARKETPLACE_NPC_ROSTER.md: Added references to Malrik & Elenya profiles (existing entries, now with new depth)
- story_arcs.md: New full section "The Severed Bond: Malrik & Elenya Pre-Collapse Memory Arc"

---

## System Mechanics Changes

### TONE Stat System

**New Gating**:
- **Empathy** 50+ (Shared Dawn primary gate)
- **Trust** 50+ (Shared Dawn alternative gate)
- **Coherence** 50+ (Shared Dawn secondary gate)
- **Coherence** 70+ (Severed Bond primary gate; optional arc gate)

**New Tool Requirements**:
- **Grounded Presence**: Presence 70+ + Sera/Korrin influence 0.5+ each
- **Sacred Silence**: High influence with Korrin post-Shared Dawn + Trust progression

**New Influence Dynamics**:
- Sera/Korrin influence changes based on player choice path (three outcomes per encounter)
- Malrik/Elenya influence increases post-revelation (both +0.25 if facilitated)

### Coherence Implications

**Shared Dawn**:
- Encounter itself maintains/slightly increases coherence
- If exposed: Coherence -3 (community fracture)

**Severed Bond**:
- Arc requires Coherence 70+ to unlock
- Facilitated encounter: Coherence +5 (integration of necessary loss)
- Ending branch shifts toward Legacy/Acceptance (less toward Transcendence)

---

## Story Progression Integration

### When Content Becomes Available

**Phase 2 (Marketplace - Mid-Game)**:
- Shared Dawn encounter becomes possible
- Triggers: After 2+ meetings with Sera, 2+ meetings with Korrin, Empathy/Trust 50+, Coherence 50+

**Phase 3 (Collapse - Pivot)**:
- Severed Bond revelation arc becomes possible  
- Triggers: After Coherence 70+, Empathy 70+/Integration 70+, 4+ encounters with Malrik, 4+ encounters with Elenya

**Phase 4 (Endings - Late Game)**:
- Both arcs inform final NPC interactions and ending branches
- Malrik/Elenya revelation unlocks alternative final passage
- Glyph of Severed Covenant key to Legacy ending branch

---

## Documentation References

**Primary Files**:
- Story details: `story_arcs.md` (new "Shared Dawn" and "Severed Bond" sections)
- NPC details: `MARKETPLACE_NPC_ROSTER.md` (Sera lines 128+, Korrin lines 240+)
- System details: `TONE_STAT_SYSTEM.md` (new "New Content Integration" section)
- Master reference: `VELINOR_MASTER_DOC.md` (updated Glyph, NPC, Phase sections)

**Data Files** (need updates):
- `glyphs_complete.json` — Add Glyph #76 Shared Dawn (done in Organizer files; needs engine integration)
- `npc_profiles.json` — Add tool entries for Grounded Presence, Sacred Silence
- `trait_profiles.json` — Already exists; new traits don't need addition (Presence/Joy/Empathy already defined)

**Testing Files**:
- `test_npc_manager.py` — Test new tool mechanics
- `test_glyph_system.py` — Test glyph unlock conditions
- `test_coherence_system.py` — Test new coherence gates

---

## Quick Links for Implementation

### For Engine Developers

1. **Glyph Integration**:
   - Read: `Glyph_Organizer.json` entry for Glyph #76
   - Implement: Unlock conditions (Empathy/Trust/Coherence gates)
   - Implement: Three-path encounter system
   - Implement: Tool unlock logic for Grounded Presence

2. **NPC Response Updates**:
   - Read: Sera profile (lines 128+) and Korrin profile (lines 240+) in MARKETPLACE_NPC_ROSTER.md
   - Implement: New response pools for post-Shared Dawn dialogues
   - Implement: Influence calculation based on three paths
   - Implement: Tool mechanics for Sacred Silence

3. **Story Integration**:
   - Read: `story_arcs.md` "Shared Dawn" and "Severed Bond" sections
   - Implement: Encounter scripts with choice gates
   - Implement: Dialogue branch system for private reflections
   - Implement: Alternative ending passage (Malrik/Elenya contribution)

### For Writers

1. **Dialogue Frameworks**:
   - Sera's post-encounter lines: "That morning... I forgot what it felt like to be surprised."
   - Korrin's post-encounter lines: "People always want information from me... She just wanted to sit."
   - Malrik's archive admission: "There are gaps in my records... personal fragments... about someone."
   - Elenya's revelation: "There was someone... I made a choice... I severed the memory deliberately."

2. **Tone & Pacing**:
   - Shared Dawn: Quiet, intimate, observed, not declared
   - Severed Bond: Gradual recognition, careful admission, honest grief
   - Both arcs: Emphasis on what's felt but not named, what's lost but honored

### For QA / Testing

1. **Gate Verification**:
   - Verify Shared Dawn trigger gates (Empathy/Trust/Coherence minimum thresholds)
   - Verify Severed Bond trigger gates (Coherence 70+, encounter counts)
   - Verify influence calculations for each player choice path

2. **Ripple Effects**:
   - Verify Nima notices Sera's change
   - Verify Kaelen comments on Korrin's shift
   - Verify community gossip spreads if encounter exposed
   - Verify Malrik/Elenya dialogue changes post-revelation

3. **Tools & Mechanics**:
   - Verify Grounded Presence unlocks at correct influence threshold
   - Verify Sacred Silence tool functions correctly
   - Verify new glyphs appear in glyph system
   - Verify ending branches recognize new glyph possession

---

## Key Principles

1. **Heat is Emotional, Not Explicit**: Both arcs add warmth through genuine recognition, not through sexual content.

2. **Catalyst, Not Resolution**: Sera/Korrin encounter is fleeting but transformative. It's not a romance beginning; it's a moment of reawakening.

3. **Necessary Trauma**: Malrik/Elenya revelation honors the idea that some painful choices are survival choices. Memory severance isn't evil; it's love.

4. **Witness is Healing**: Both arcs emphasize the power of being seen, of sitting with another's reality, of honoring what's been lost.

5. **Emotional Architecture**: All mechanics (glyphs, traits, influence, gates) work together to make the player's emotional journey feel real and consequential.
