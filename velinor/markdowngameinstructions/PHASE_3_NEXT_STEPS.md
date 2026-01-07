# Phase 3 Implementation Next Steps

## What Just Shipped

✅ **Skill Registry Complete** - 62 skills across 7 categories  
✅ **Glyph-to-Skill Mapping** - All 73 glyphs mapped, 63 teaching skills  
✅ **Prerequisite Chains** - 3-level max dependency structure  
✅ **REMNANTS Integration** - Each skill has trait modulation  
✅ **Documentation** - Complete guides and quick reference  

**Status:** Infrastructure ready for Phase 3b (dialogue routing and implementation)

---

## Phase 3b: Dialogue Bank Creation

### What is a Dialogue Bank?

For every NPC × every glyph combination, create 4 dialogue variants that respond to player's current skill level:

```
bank_a_untrained:    "You don't have the foundation yet"
bank_b_partial:      "You're getting there, you understand some of it"
bank_c_ready:        "You're ready for this teaching"
bank_d_overqualified: "You already know this, let me push you further"
```

### Example: Malrik Teaching Glyph of Mirage Echo

**Bank A (Untrained - No previous skills from Malrik)**
```
MALRIK: You arrive dusty and uncertain.
MALRIK: "The desert teaches deception first. You must learn to see 
        through illusion—the heat's shimmer, the mind's tricks, 
        the stories we tell ourselves about who we are."
MALRIK: "This Glyph shows you the difference between what you see 
        and what is. Come."
QUEST_OFFER: Learn Illusion Discernment through the Glyph of Mirage Echo
QUEST_GATES: None (entry-level skill)
```

**Bank B (Partial - Malrik taught you 1-2 things before)**
```
MALRIK: You enter, Malrik looks up from his scrolls.
MALRIK: "Ah, you return. You carry something new from your time 
        in the world. I see it in how you move—more intention now."
MALRIK: "Good. That foundation will serve you here. The Mirage Echo 
        goes deeper than the surface deceptions. It teaches you to 
        recognize your own mythology about the desert."
QUEST_OFFER: Deepen your understanding of Illusion Discernment
QUEST_GATES: Must have learned at least one Malrik skill
```

**Bank C (Ready - All prerequisites met)**
```
MALRIK: You enter the archive. Malrik smiles faintly.
MALRIK: "You've learned the language of boundaries, the cadence of 
        measured steps. Now you have the tools to hear what the 
        Mirage Echo actually teaches."
MALRIK: "Most who come here are just learning to see. You're ready 
        to understand why they see falsely. Come."
QUEST_OFFER: Master Illusion Discernment with the Glyph of Mirage Echo
QUEST_GATES: Must have learned both measured_movement and 
              distortion_recognition
```

**Bank D (Overqualified - You know more than expected)**
```
MALRIK: You enter. Malrik sets down his work with visible interest.
MALRIK: "You've learned from others. I can tell—you carry 
        collective_tending and communal_celebration alongside my 
        teachings about collapse. That's rare."
MALRIK: "The Mirage Echo teaches isolation, usually. But in your 
        hands, with what you've learned from Tala... let me show 
        you something I haven't shown another."
QUEST_OFFER: Integrate your broader understanding into deeper 
              knowledge of Illusion Discernment
QUEST_GATES: Must have 3+ skills from different NPCs + prerequisites
SPECIAL: Offers unique variant dialogue integrating player's cross-NPC skills
```

---

## Phase 3c: Dialogue Router Implementation

### Logic Flow

```python
def select_dialogue_bank(npc, glyph, player_resume):
    """Select which dialogue bank variant to use."""
    
    skill_required = glyph.skill_required  # e.g., "measured_movement"
    skill_taught = glyph.skill_taught      # e.g., "illusion_discernment"
    
    # Check what player already knows from THIS NPC
    npc_skills_learned = count_skills_from_npc(player_resume, npc)
    
    # Check if player has prerequisites from ANY NPC
    has_prerequisite = has_skill(player_resume, skill_required)
    
    # Check if player is overqualified
    is_overqualified = (
        has_skill(player_resume, skill_taught) or
        (npc_skills_learned >= 3 and 
         count_unique_npc_mentors(player_resume) >= 2)
    )
    
    # Select bank
    if is_overqualified:
        return f"dialogue_banks/{npc}/bank_d_overqualified"
    
    elif has_prerequisite:
        return f"dialogue_banks/{npc}/bank_c_ready"
    
    elif npc_skills_learned >= 1:
        return f"dialogue_banks/{npc}/bank_b_partial"
    
    else:
        return f"dialogue_banks/{npc}/bank_a_untrained"
```

### Implementation Steps

1. **Create dialogue_banks.py module**
   - Load all NPC dialogue banks from JSON
   - Cache in memory for quick access
   - Handle missing bank gracefully (fallback to generic)

2. **Create dialogue_router.py class**
   - `DialogueRouter` takes player_resume and glyph
   - `select_bank()` method implements logic above
   - Log bank selection for debugging/analytics

3. **Integrate with NPC.interact()**
   - Before offering quest: `router.select_bank(npc, glyph, player.resume)`
   - Load and display dialogue from selected bank
   - After quest completion: update `player.resume['skills_acquired']`

---

## Phase 3d: Quest Gatekeeper

### What Blocks Player from Attempting Glyph

```python
def can_attempt_glyph(player_resume, glyph):
    """Check if player meets prerequisites."""
    
    if not glyph.skill_required:
        return True  # Entry-level, no prereq
    
    return has_skill(player_resume, glyph.skill_required)

def attempt_glyph(player, npc, glyph):
    """Try to begin glyph quest."""
    
    if not can_attempt_glyph(player.resume, glyph):
        prerequisite = glyph.skill_required
        prerequisite_npc = find_npc_teaching_skill(prerequisite)
        
        # Show redirection dialogue
        npc.say(f"""
            You're not ready for this yet. The {glyph.name} requires 
            you to first learn {prerequisite_npc.skill_taught_name} 
            from {prerequisite_npc.name}.
            
            Go. Come back when you've learned what you need.
        """)
        return False
    
    else:
        # Proceed with quest
        return start_glyph_quest(player, npc, glyph)
```

### Gatekeeper Messages

**Redirect to Single Prerequisite:**
```
"The Glyph of Boundary Stone requires measured_movement first. 
 Seek out Malrik again and ask about the Glyph of Measured Step."
```

**Suggest Entry-Level Skills:**
```
"You're ready for entry-level teachings. Consider learning from:
 - Malrik (illusion_discernment via Glyph of Mirage Echo)
 - Tala (communal_celebration via Glyph of Shared Feast)
 - Helia (silent_witnessing via Glyph of Tender Witness)"
```

**After Skill Acquired:**
```
"You've learned measured_movement. Now you're ready for Malrik's 
 deeper teachings. The Glyph of Boundary Stone awaits you."
```

---

## Phase 3e: Skill Tracker & Player Resume Manager

### Track Skill Acquisition

```python
class SkillTracker:
    """Manages player's skill acquisitions and REMNANTS effects."""
    
    def acquire_skill(self, player, skill_id, npc, glyph):
        """Record new skill and apply effects."""
        
        # 1. Record in resume
        player.resume['skills_acquired'].append({
            'skill_id': skill_id,
            'skill_name': SKILL_REGISTRY[skill_id]['name'],
            'learned_from': npc.name,
            'date_acquired': current_session,
            'via_glyph': glyph.name
        })
        
        # 2. Apply REMNANTS effects
        remnants_effects = SKILL_REGISTRY[skill_id]['remnants_effects']
        for trait, delta in remnants_effects.items():
            player.remnants[trait] += delta
        
        # 3. Unlock advanced skills
        for dependent_skill_id in find_dependents(skill_id):
            player.available_skills.add(dependent_skill_id)
        
        # 4. Update NPC relationship
        npc.add_relationship_event({
            'type': 'skill_taught',
            'skill': skill_id,
            'date': current_session
        })
        
        # 5. Show acquisition cutscene
        show_skill_acquisition_sequence(player, skill_id, npc)
```

### Skill Acquisition Cutscene

```
[Player completes Glyph of Mirage Echo quest]

MALRIK: "You see it now. The difference between shimmer and shadow. 
        Between the world's true form and what our fear makes of it."

MALRIK: "That is illusion_discernment. You carry it with you now."

[SKILL ACQUIRED: Illusion Discernment]

[REMNANTS EFFECTS APPLIED: memory +0.1, presence +0.1]

[NEW SKILLS AVAILABLE: collapse_navigation, truth_discernment]

PLAYER'S INNER VOICE: "Something has shifted. I see the desert 
                      differently now. Not more clearly, but more 
                      honestly. I see what the sand is hiding, and 
                      why..."

[Press Space to continue]
```

### Resume Manager

```python
class PlayerResumeManager:
    """Manages player's skill resume and relationship history."""
    
    def get_skills_by_category(self, player):
        """Return skills grouped by REMNANTS category."""
        # Used for UI display, dialogue routing, NPC evaluation
        pass
    
    def get_npc_specialization_match(self, player, npc):
        """How many of this NPC's skills has player learned?"""
        # Used to determine dialogue bank
        pass
    
    def get_unique_mentors(self, player):
        """How many different NPCs has player learned from?"""
        # Used for overqualified dialogue variant
        pass
    
    def serialize_for_save(self, player):
        """Convert resume to JSON for save file."""
        pass
    
    def load_from_save(self, save_file):
        """Restore resume from save file."""
        pass
```

---

## Integration Checklist

### Phase 1 Dependencies
- [ ] `tone_mapper.py` - For dialogue emotional tone routing
- [ ] `remnants_block_modifiers.py` - For applying REMNANTS effects
- [ ] `velinor_dialogue_orchestrator_v2.py` - For dialogue orchestration

### Phase 2 Dependencies
- [ ] `Glyph_Organizer_Expanded.csv` - For glyph metadata including skill_taught, skill_required
- [ ] `Glyph quest logic` - For quest gating and completion detection

### Phase 3 New Files
- [ ] Create `dialogue_banks.json` - All NPC dialogue variants
- [ ] Create `dialogue_router.py` - Bank selection logic
- [ ] Create `quest_gatekeeper.py` - Prerequisite checking
- [ ] Create `skill_tracker.py` - Skill acquisition handling
- [ ] Create `player_resume_manager.py` - Resume tracking and queries

### Integration Points
- [ ] NPC.attempt_glyph() → check with quest_gatekeeper
- [ ] NPC.interact() → select dialogue bank with dialogue_router
- [ ] Complete glyph quest → skill_tracker.acquire_skill()
- [ ] Load/save game → player_resume_manager

---

## Testing Strategy

### Unit Tests
```python
# test_dialogue_router.py
def test_untrained_player_gets_bank_a()
def test_partial_training_gets_bank_b()
def test_prerequisite_met_gets_bank_c()
def test_overqualified_gets_bank_d()

# test_quest_gatekeeper.py
def test_entry_level_always_allowed()
def test_prerequisite_blocks_quest()
def test_redirect_message_includes_correct_npc()

# test_skill_tracker.py
def test_skill_acquisition_updates_resume()
def test_remnants_effects_applied()
def test_dependent_skills_unlocked()
```

### Integration Tests
```python
# test_skill_progression.py
def test_malrik_complete_progression():
    """Play through Malrik's 5 glyphs in order."""
    player = Player()
    
    # Learn illusion_discernment
    assert can_attempt_glyph(player, malrik_glyph_1)
    complete_glyph(player, malrik, malrik_glyph_1)
    assert has_skill(player, 'illusion_discernment')
    
    # Cannot learn collapse_navigation yet (requires illusion_discernment + distortion)
    assert not can_attempt_glyph(player, malrik_glyph_3)
    
    # Learn distortion_recognition from different glyph
    complete_glyph(player, malrik, malrik_glyph_2)
    assert has_skill(player, 'distortion_recognition')
    
    # Now can learn collapse_navigation
    assert can_attempt_glyph(player, malrik_glyph_3)
    complete_glyph(player, malrik, malrik_glyph_3)
    
    # Verify dialogue progressed through banks
    assert malrik.last_dialogue_bank == 'bank_c_ready'
```

### Acceptance Tests
```python
# test_user_stories.py
def test_vocational_apprenticeship():
    """Test the core game loop."""
    player = Player()
    
    # Act 1: Arrival at Malrik's Archive
    # - Cannot understand full teachings yet
    # - Learns illusion_discernment (entry-level)
    
    # Act 2: Spreading Out
    # - Learns from Tala (communal_celebration)
    # - Learns from Helia (silent_witnessing)
    # - Dialogue acknowledges cross-training
    
    # Act 3: Return to Malrik
    # - Malrik recognizes broader knowledge
    # - Offers deeper variant of Mirage Echo
    # - References skills learned elsewhere
    
    # Verify game feels like becoming someone through work + mentorship
    assert player_feels_like_apprentice(player)
```

---

## Estimated Implementation Timeline

- **Phase 3b (Dialogue Banks):** 2-3 weeks
  - Write dialogue for 32 NPCs × ~5 glyphs each × 4 variants = ~640 dialogue scenes
  - Can parallelize with multiple writers
  - Can generate templates/outlines first

- **Phase 3c (Dialogue Router):** 2-3 days
  - Relatively simple logic
  - Main complexity is integration with existing dialogue system

- **Phase 3d (Quest Gatekeeper):** 2-3 days
  - Similar complexity to router
  - Must coordinate with Phase 2 quest completion logic

- **Phase 3e (Skill Tracker):** 3-5 days
  - Integrate REMNANTS effects application
  - Handle save/load persistence
  - Create cutscene sequences

- **Integration & Testing:** 1-2 weeks
  - Test all combinations (32 NPCs × 73 glyphs × player backgrounds)
  - Fix edge cases in dialogue routing
  - Balance skill prerequisites (some may be too restrictive)

---

## Success Criteria

### ✅ Skill System is Complete When:
1. Player can attempt glyphs only with prerequisites met
2. Dialogue changes based on what player has learned
3. NPC acknowledges player's broader training from other mentors
4. Skill acquisition unlocks dependent skills
5. REMNANTS traits change when skills acquired
6. Player resume tracks complete apprenticeship history
7. Game feels like vocational apprenticeship, not traditional RPG
8. Overqualified dialogue variant exists and feels special
9. Save/load preserves skill progression
10. 90%+ of glyph × NPC combinations have meaningful dialogue

---

## Questions for User

Before proceeding to Phase 3b, need clarification:

1. **Dialogue Tone:** Should dialogue vary by NPC personality as well as skill level?
   - Example: Does Malrik speak differently to overqualified player than Tala does?

2. **Overqualified Variant:** Should it unlock unique quests or just acknowledge growth?
   - Example: Can player learn variant techniques after mastering skill?

3. **Skill Display:** Should player see skill tree in UI?
   - Or discover through dialogue that new skills are available?

4. **Cross-Training Dialogue:** How much should NPC reference skills from other mentors?
   - Minimal: "You've learned other things"
   - Moderate: "I see you learned measured_movement from me and joy from Tala"
   - Extensive: "That communal_celebration you learned will actually help here..."

5. **Skill Reset:** Can player reset skills, or is progression permanent?

---

**Next Step:** Await user decision on which NPC to write dialogue banks for first (recommend: Malrik, then Tala).

---

Generated: January 6, 2026  
Status: ✅ Ready for Phase 3b  
