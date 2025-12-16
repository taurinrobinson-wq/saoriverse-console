# Story Map User Guide

## Overview

This guide explains how to use and maintain `story_map_velinor.md` - the comprehensive narrative design document for Velinor: Remnants of the Tone.
##

## What is the Story Map?

The story map is a **game bible** that organizes:
- **Branching narratives** and decision points
- **Character arcs** and relationship networks
- **Glyph systems** and progression mechanics
- **Ending branches** and consequences
- **Expansion placeholders** for future development

Think of it as the **single source of truth** for Velinor's narrative structure.
##

## Who Should Use This?

### Writers & Narrative Designers
✅ **You should reference this when:**
- Writing new NPC dialogue
- Creating quest branches
- Designing emotional encounters
- Planning story expansions
- Ensuring narrative consistency

**Your Section:** Character Relationships, Story Structure, Ending Branches
##

### Game Developers
✅ **You should reference this when:**
- Implementing TONE stat system
- Building NPC relationship mechanics
- Creating glyph collection logic
- Programming ending conditions
- Setting up choice nodes

**Your Section:** Narrative Decision Points, Glyph System, TONE mechanics
##

### Artists & Asset Creators
✅ **You should reference this when:**
- Designing character models (NPCs, Saori, Velinor)
- Creating environment art (biomes, chambers)
- Designing glyph visuals
- Building UI elements (journal, map)

**Your Section:** Character Relationships (appearance descriptions), Expansion Placeholders (locations)
##

### Project Managers
✅ **You should reference this when:**
- Planning development milestones
- Prioritizing features
- Tracking completion status
- Estimating scope

**Your Section:** How to Use This Map → For Project Managers
##

## How to Navigate the Story Map

### Table of Contents Structure

The story map is organized into **9 major sections**:

1. **Overview** - High-level premise and themes
2. **Core Narrative Arc** - Main story beats from Cataclysm to final choice
3. **Character Relationships** - NPCs, spheres of influence, relationship mechanics
4. **Story Structure & Progression** - Act-by-act breakdown with branching
5. **Glyph System** - Types, functions, fusion mechanics
6. **Ending Branches** - All 6 endings with requirements and consequences
7. **Narrative Decision Points** - Major choice nodes with ripple effects
8. **Expansion Placeholders** - Future content with [TBD] markers
9. **How to Use This Map** - Role-specific guidance

### Quick Navigation Tips

**Looking for specific content?**
- Use Ctrl+F / Cmd+F to search for keywords
- Character names are **bolded** in their first appearance
- Choice nodes are formatted as `Choice Node X:`
- Placeholders use `[PLACEHOLDER]` or `[TBD]` format

**Understanding relationships?**
- Check "Character Relationships" for NPC details
- Sphere connections show as weighted values (0.1-1.0)
- Higher weight = stronger ripple effect

**Tracking narrative flow?**
- "Story Structure & Progression" has Act-by-Act breakdowns
- "Narrative Decision Points" shows all major choice moments
- Use flowcharts (` ↓ ` and ` ├─ ` symbols) to visualize branches
##

## How to Update the Story Map

### General Guidelines

1. **Always update the "Last Updated" field** at the top of the document
2. **Maintain consistent formatting** with existing entries
3. **Add update notes** in relevant sections
4. **Cross-reference** related sections when making changes

### Adding New Content

#### Adding a New NPC

**Step 1:** Add to "Character Relationships" section

```markdown
**[Number]. [NPC Name]** ([Role/Archetype])
- Appearance: [Physical description]
- Trait: [Personality summary]
- Sphere: [Connected NPCs with weights]
- Gift: [Tool or knowledge they provide]
```text
```



**Step 2:** Add their sphere connections to related NPCs

**Step 3:** Add relevant encounters to "Story Structure"

**Step 4:** If they affect endings, update "Ending Branches"
##

#### Adding a New Quest

**Step 1:** Add to "Expansion Placeholders" → Side Quests

```markdown
- [ ] **[Quest Name]**: [Brief description]
  - Trigger: [When it becomes available]
  - NPCs involved: [List]
```text
```



**Step 2:** Add quest beats to "Story Structure & Progression"

**Step 3:** Add decision points to "Narrative Decision Points" if quest has major choices

**Step 4:** Update NPC sections if quest affects relationships
##

#### Adding a New Glyph Chamber

**Step 1:** Update "Glyph System" → Octoglyph System table

```markdown
```text
```



**Step 2:** Fill expansion placeholder in "Expansion Placeholders" → Octoglyph Chamber Details

```markdown
- [x] **[Chamber Name]**
  - Location: [Where in game world]
  - Puzzle: [Emotional/mechanical challenge]
```text
```



**Step 3:** Add chamber encounter to Act 3 in "Story Structure"
##

#### Adding a New Ending Branch

**Step 1:** Add to "Ending Branches" section

```markdown

#### [Number]. [Ending Name] ([Theme])

**Trigger:**
- [Stat requirements]
- [Player action]
- [Glyph requirements]

**Resolution:**
[Dialogue and outcome]

**Survivor Reactions:**
[How NPCs respond]

**Final Image:**
```sql
```



**Step 2:** Update "Narrative Decision Points" → Choice Node 8 with new action

**Step 3:** Update Quick Reference numbers
##

### Filling Placeholders

**When you have content for a `[PLACEHOLDER]` or `[TBD]`:**

1. **Find all instances** of that placeholder (use search)
2. **Replace with specific content** maintaining format
3. **Update checkbox** if in expansion placeholder section: `- [ ]` → `- [x]`
4. **Cross-check** related sections for consistency

**Example:**

```markdown
Before:
- [ ] **Healer's Circle** (2-3 NPCs)
  - [PLACEHOLDER for names and details]

After:
- [x] **Healer's Circle** (3 NPCs)
  - **Mirena the Bone-Setter**: Elderly, pragmatic
  - **Joran the Herbalist**: Young, optimistic
```text
```


##

### Version Control

**When to increment version:**
- **Patch (1.0 → 1.0.1)**: Typo fixes, clarifications, minor edits
- **Minor (1.0 → 1.1)**: New NPCs, quests, or chambers added
- **Major (1.0 → 2.0)**: Structural changes, new acts, or core mechanic revisions

**Update format:**

```markdown

## Update Log

### Version 1.1 (January 15, 2026)
- Added 3 NPCs to Healer's Circle
- Filled Octoglyph Chamber 2-4 placeholders
- Created "Children of Velhara" NPC category
- Updated Act 2 progression with new side quest

### Version 1.0 (December 14, 2025)
- Initial story map created
- All core systems documented
- Expansion placeholders established
```


##

## Common Use Cases

### Use Case 1: Writing New NPC Dialogue

**Goal:** Create dialogue for Sera the Herb Novice

**Steps:**
1. Open story map → "Character Relationships" → Find Sera
2. Note her traits: "Gentle, shy, responds to Empathy"
3. Check her sphere: Shrine Keepers (0.7), Healers (0.6)
4. Review her gift: Flicker Ritual
5. Check "Narrative Decision Points" for when player might encounter her
6. Write dialogue that:
   - Reflects shy personality
   - Rewards empathetic choices
   - References her connection to shrine keepers
   - Hints at Flicker Ritual reward
##

### Use Case 2: Implementing Choice Node

**Goal:** Program the Kaelen Loyalty Test

**Steps:**
1. Open story map → "Narrative Decision Points" → Find Choice Node 3
2. Note the 3 options and their consequences
3. Check "Character Relationships" → Kaelen for his sphere connections
4. Implement:
   ```python
   if player_choice == "betray_kaelen":
       kaelen.trust = -50
       player.fragments += stolen_fragments
       unlock_captain_veynar_dialogue()
   elif player_choice == "protect_kaelen":
       kaelen.trust = +50
       player.fragments -= stolen_fragments
       unlock_thieves_lair_quest()
   ```
5. Add ripple to Market Shadows sphere (0.2 weight)
##

### Use Case 3: Designing New Glyph Chamber

**Goal:** Create the "Dislocated Attachment" chamber

**Steps:**
1. Open story map → "Glyph System" → Octoglyph System table
2. Note: "Dislocated Attachment" = Love + Fear emotion
3. Check "Expansion Placeholders" → Octoglyph Chamber Details
4. Design puzzle around reconciling love and fear
5. Choose location (perhaps Hospital Ruins - fits theme)
6. Create memory echo showing Cataclysm family separation
7. Fill placeholder:
   ```markdown
   - [x] **Dislocated Attachment Chamber**
     - Location: Hospital Ruins, collapsed pediatric wing
     - Puzzle: Player must hold two conflicting glyphs (Love/Fear)
       simultaneously while navigating memory echoes
     - Memory echo: Mother choosing to disconnect child from
       Corelink to spare them pain, knowing it may kill them
   ```
##

### Use Case 4: Planning Development Milestone

**Goal:** Plan "Act 2 Complete" milestone

**Steps:**
1. Open story map → "How to Use This Map" → For Project Managers
2. Note Act 2 requirements: All biomes, triglyph chamber, side quests
3. Check "Expansion Placeholders" for what needs filling:
   - [ ] Additional biomes (currently 4, could expand to 6)
   - [ ] Side quests (currently 1, add 2-3 more)
   - [ ] Triglyph chamber must be fully functional
4. Create task list:
   - Complete Swamp, Desert, Forest, Lake environments
   - Implement triglyph fusion mechanic
   - Build Chamber of Echoed Memory
   - Add Thieves' lair quest
   - Optional: Add 1-2 more side quests from placeholders
5. Estimate: 6-8 weeks for Act 2 completion
##

## Maintaining Narrative Consistency

### Before Adding Content, Ask:

**Tone Check:**
- Does this fit Velinor's themes (memory, sacrifice, friendship)?
- Is the emotional weight appropriate?
- Does it honor the "no good ending" philosophy?

**Integration Check:**
- How does this connect to existing NPCs?
- What TONE stats does this engage?
- Does this affect any ending branches?

**Mechanical Check:**
- Is this consistent with established rules (glyph fusion, sphere weights)?
- Does this create new mechanics or use existing ones?
- How does this interact with the journal system?

### Red Flags to Avoid:

❌ **DON'T** create "perfect" solutions - all choices should have trade-offs
❌ **DON'T** ignore NPC sphere connections - relationships must ripple
❌ **DON'T** make TONE stats visible - they stay hidden to preserve authenticity
❌ **DON'T** add combat-focused content - this is about emotional confrontation
❌ **DON'T** forget to update related sections when making changes
##

## Testing with the Story Map

### Narrative Testing Checklist

Before marking content "complete," verify:

**For NPCs:**
- [ ] Dialogue reflects personality traits from story map
- [ ] Sphere connections trigger appropriate ripples
- [ ] Gift/tool is provided at correct resonance threshold
- [ ] Repair paths function if relationship breaks

**For Choice Nodes:**
- [ ] All options modify TONE stats as documented
- [ ] Consequences match story map specifications
- [ ] Related NPCs react according to sphere weights
- [ ] Journal updates with correct information

**For Glyph Chambers:**
- [ ] Emotional theme matches octoglyph stage description
- [ ] Puzzle is about refinement, not combat
- [ ] Memory echoes tie to Cataclysm or character backstory
- [ ] Unified glyph rewards correctly

**For Endings:**
- [ ] Trigger requirements match documented stats/choices
- [ ] Core dialogue (Velinor/Saori) matches exactly
- [ ] Survivor reactions match emotional lever chosen
- [ ] Final image conveys appropriate ambiguity
##

## Troubleshooting

### Problem: Content doesn't fit existing structure

**Solution:**
- Review "Core Narrative Arc" to understand main story beats
- Check if content should be main path or expansion placeholder
- Consider if this introduces new mechanics (document those first)
- If truly doesn't fit, discuss with team before forcing it in
##

### Problem: Contradicting existing lore

**Solution:**
- Search story map for all references to conflicting element
- Check "Character Relationships" and "Core Narrative Arc"
- Decide which version is canonical
- Update all instances to maintain consistency
- Add note in Update Log explaining resolution
##

### Problem: Too many placeholders to track

**Solution:**
- Use search function for `[PLACEHOLDER]` and `[TBD]` to list all
- Create separate tracking document with priority levels
- Focus on Critical Path placeholders first (main story)
- Mark lower priority placeholders for post-launch content
##

### Problem: Story map is getting too long

**Solution:**
- Consider splitting into multiple documents (e.g., separate NPC guide)
- Use the existing structure as a hub with links to detail docs
- Keep story map as overview, move deep details to appendices
- Maintain current file as "master" with cross-references
##

## Best Practices

### Do's ✅

✅ **Read the whole story map** before making significant changes
✅ **Update related sections** when adding content (NPCs affect quests, etc.)
✅ **Use consistent formatting** to maintain readability
✅ **Fill placeholders** as content is finalized
✅ **Test in-game** to verify story map accuracy
✅ **Communicate changes** to team via update log
✅ **Maintain ambiguity** in endings and choices

### Don'ts ❌

❌ **Don't bypass the story map** when making narrative decisions
❌ **Don't contradict established lore** without documenting changes
❌ **Don't create "right answer" choices** - maintain moral ambiguity
❌ **Don't forget TONE stats** when designing choices
❌ **Don't ignore NPC spheres** - relationships are interconnected
❌ **Don't make combat mandatory** - emotional confrontation is key
##

## Quick Reference Commands

### Search Keywords

| Looking for... | Search for... |
|----------------|---------------|
| All NPCs | **Character Relationships** |
| Specific NPC | NPC's name (e.g., "Kaelen") |
| Choice impacts | "Consequences:" or "→" |
| Placeholders | `[PLACEHOLDER]` or `[TBD]` |
| Endings | **Ending Branches** |
| Glyph mechanics | **Glyph System** |
| TONE stats | "TONE" or "Trust, Observation" |
| Decision points | "Choice Node" |
##

## FAQ

**Q: Do I need to read the entire story map before starting work?**
A: Not necessarily. Read the Overview and your role-specific section first, then reference other sections as needed.

**Q: What if I want to add content not covered by placeholders?**
A: Discuss with narrative lead first. If approved, add new placeholder category in "Expansion Placeholders" section before implementing.

**Q: How strict are the ending requirements?**
A: They're guidelines. Player experience may reveal need for adjustments. Document any changes in Update Log.

**Q: Can NPCs have relationships outside their documented spheres?**
A: Yes, but add the connection to the story map with appropriate weight value. All relationships must be documented.

**Q: What if testing reveals a plot hole?**
A: Document it immediately, mark affected sections with `[NEEDS REVISION]`, and bring to team for resolution.

**Q: How often should the story map be updated?**
A: Update immediately when new content is added or changed. Review/audit monthly for consistency.
##

## Resources

**Related Documents:**
- `README.md` - Game overview and quick start
- `DOCUMENTATION_INDEX.md` - Complete documentation reference
- `TONE_STAT_SYSTEM.md` - Detailed TONE mechanics
- `NPC_SPHERE_SYSTEM.md` - Relationship system details
- `VELINOR_SAORI_FINAL_ARC.md` - Final encounter details

**Story Map Sections:**
- Core Narrative Arc → Understanding main story
- Character Relationships → NPC details
- Glyph System → Collection mechanics
- Ending Branches → All possible conclusions
- Narrative Decision Points → Choice nodes
##

## Contact

**Questions about the story map?**
- Narrative Lead: [Contact info]
- Project Manager: [Contact info]
- Development Team: [Contact info]

**Reporting issues with the story map?**
Create an issue with:
- Section name
- Description of problem
- Suggested fix (if any)
- Priority level
##

**Remember:** The story map is a living document. It should evolve as Velinor evolves. Keep it updated, keep it consistent, and let it guide the creation of this emotionally resonant world.
##

**Last Updated:** December 14, 2025
**Document Version:** 1.0
**Story Map Version:** 1.0
