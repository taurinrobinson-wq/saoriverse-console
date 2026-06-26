# Story Structure Restructuring - Complete

## Overview
Both Malrik and Elenya's story arcs have been restructured to present the narrative in **chronological gameplay order** rather than chronological story time:

- **Acts 1-4** (PRESENT-DAY): What player experiences first
- **Acts 5-8** (PAST MEMORY): Unlocked through emotional progression and glyph accumulation

---

## MALRIK Story Arc

### NEW STRUCTURE (Post-Restructure)

#### **Present-Day Acts (1-4)** - Entry Point
**Act 1: Two Strangers with a Shared Gravity** (post_collapse_years)
- **Segment 0** (ENTRY): "The Archivist's Study" - GATE-FREE intro
  - NPC: "You've come seeking something. Everyone who enters here seeks something."
  - Choices unlock: `malrik_intro_complete`
- **Segment 1**: "In Passing" - Marketplace encounter, body memory
- **Segment 2**: "The Weight of Certainty" - Malrik as Archivist, need for order
- **Segment 3**: "Archives and Ache" - Recognition without remembrance

**Act 2: The Broken Lantern** (post_collapse_present)
- 3 dialogue segments exploring Skeptics vs Mystics conflict
- Glyph-triggered scenes

**Act 3: The Restoration** (post_collapse_present)
- 3 segments showing emotional reconnection
- Coherence/empathy-gated content

**Act 4: What They Hold Now** (post_collapse_present_forward)
- 1 climactic segment
- Bridge to memory unlock

#### **Past Memory Acts (5-8)** - Unlocked Through Glyphs
**Act 5: The Professor and the Older Student** (pre_collapse)
- How Malrik first encountered Elenya at university
- His discomfort with her presence; her challenge to his worldview

**Act 6: The Lighthouse** (pre_collapse)
- Sanctuary they both discovered
- Shared space where differences dissolve

**Act 7: The Love They Never Named** (pre_collapse)
- Deepest intimacy before collapse
- Philosophical and emotional union

**Act 8: The Cataclysm** (collapse_event)
- The moment everything broke
- Final moment together before forgetting

---

## ELENYA Story Arc

### NEW STRUCTURE (Post-Restructure)

#### **Present-Day Acts (1-4)** - Entry Point
**Act 1: The High Seer** (post_collapse_years)
- **Segment 0** (ENTRY): "The Seer's Sanctuary" - GATE-FREE intro
  - NPC: "Welcome. I've been expecting you—though I didn't know when."
  - Choices unlock: `elenya_intro_complete`
- **Segment 1**: "Compassion Without Possession" - Teaches what she cannot practice
- **Segment 2**: "The Trembling Voice" - Something in her responds to Malrik
- **Segment 3**: "What the Body Knows" - Embodied recognition

**Act 2: The Broken Lantern** (post_collapse_present)
- 2 dialogue segments exploring Mystics vs Skeptics
- Spiritual themes in present-day conflict

**Act 3: The Restoration** (post_collapse_present)
- 3 segments showing her teaching journey
- Discovery of what she chose to forget

**Act 4: What She Holds Now** (post_collapse_present_forward)
- 1 climactic segment
- Spiritual resolution, memory doorway

#### **Past Memory Acts (5-8)** - Unlocked Through Glyphs
**Act 5: The Older Student and the Professor** (pre_collapse)
- Elenya encounters Malrik's teaching
- Her fascination with his need for structure

**Act 6: The Lighthouse** (pre_collapse)
- Same sanctuary, viewed through her eyes
- Where she decided to love him

**Act 7: The Love She Didn't Expect** (pre_collapse)
- Their deepest connection
- Her choice to let this matter

**Act 8: The Cataclysm** (collapse_event)
- The breaking
- Her deliberate choice to sever the memory

---

## Key Features

### ✅ Segment Zero Entry Points
Both NPCs have a **gate-free introductory segment** at the top of Act 1:
- No required gates, stats, glyphs, or coherence
- Unlocks basic `intro_complete` gate
- Small stat bumps (0.05-0.1)
- TONE-labeled choices (T/O/N/E)

### ✅ Progressive Revelation
1. **Acts 1-4**: Player builds TONE stats in present-day
2. **Acts 2-3**: Glyph-triggered scenes hint at deeper connection
3. **Act 4**: Emotional climax opens door to memory
4. **Acts 5-8**: Memory unlocked gradually as glyphs accumulate + coherence builds + empathy grows

### ✅ Preserve Segment IDs
All segment IDs maintain their original form (e.g., `malrik_act5_seg1_...` in new Act 1) to:
- Track content provenance
- Support debugging
- Enable future migrations

### ✅ Dual Narrative
- **Surface Story** (Acts 1-4): Two people discovering inexplicable connection
- **Deep Story** (Acts 5-8): The love they forgot and must choose to remember

---

## Gate Progression Needed

For Acts 5-8 to unlock progressively, should add gates like:

```json
"requiredGates": [
  {
    "gateType": "tone_stat",
    "requirement": "empathy",
    "threshold": 0.6,
    "description": "Must have felt deeply in present-day story"
  },
  {
    "gateType": "coherence",
    "requirement": "coherence",
    "threshold": 0.5,
    "description": "Must have integrated present-day experiences"
  },
  {
    "gateType": "custom",
    "requirement": "glyphs_accumulated",
    "threshold": 3,
    "description": "Must have encountered enough story glyphs"
  }
]
```

---

## Testing Checklist

### Dialogue Entry
- [ ] Approach Malrik → press E → Segment 0 appears
- [ ] Approach Elenya → press E → Segment 0 appears
- [ ] No gate/stat/glyph requirements blocking entry

### Narrative Flow
- [ ] Complete Act 1 segments in order
- [ ] Act 2 segments follow naturally
- [ ] Acts 5-8 locked initially (gate requirements)

### Stats Display
- [ ] Top-right shows correct NPC (Malrik or Elenya)
- [ ] All 8 REMNANTS display with values
- [ ] Stats update as dialogue choices made

### Memory Unlock Progression
- [ ] Accumulate glyphs through play
- [ ] Build empathy/coherence in Acts 1-4
- [ ] Acts 5-8 gates gradually unlock
- [ ] Memory story progressively reveals

---

## Files Modified

1. **MalrikStoryGates.json** (977 lines)
   - Acts reordered: old [1,2,3,4,5,6,7,8] → new [5,6,7,8,1,2,3,4]
   - All segment IDs preserved
   - Segment Zero moved to Act 1, index 0
   
2. **ElenyaStoryGates.json** (939 lines)
   - Acts reordered: old [1,2,3,4,5,6,7,8] → new [5,6,7,8,1,2,3,4]
   - All segment IDs preserved
   - Segment Zero moved to Act 1, index 0

3. **Python Scripts (for future reference)**
   - `restructure_acts.py` - Reordered acts and updated actNumber fields
   - `move_segment_zero.py` - Relocated Segment Zero to Act 1

---

## Next Phase: Gate Enhancement

To fully implement progressive memory unlock:

1. Add coherence thresholds to Acts 5-8
2. Add glyph-count requirements to later memory acts
3. Add empathy/observation thresholds for emotional readiness
4. Implement influence gates for NPC relationship progression

This ensures memory revelation is **earned through emotional growth**, not immediately accessible.
