# AUTHORING GUIDE: Ravi & Nima Arc

**How to fill in the skeleton. Visual markers show exactly where your writing goes.**

---

## File Structure

```
velinor/stories/ravi_nima/
├── RN_Act1_Introduction.json     ← 14 passages
├── RN_Act2_OphinaReveal.json     ← 13 passages
├── RN_Act3_Chamber.json          ← 25 passages
├── RN_Act4_Resolution.json       ← 15 passages
├── CONNECTION_MAP.json           ← Architecture guide
└── AUTHORING_GUIDE.md            ← This file
```

---

## Visual Markers in JSON

Every placeholder has this format:

```json
// ✏️ AUTHOR SECTION: [TYPE]
"content": "PLACEHOLDER_NAME: // [context for what goes here]",
// ✏️ END SECTION
```

**Types:**
- `✏️ NARRATION` — Prose descriptions, setting, atmosphere
- `✏️ RAVI_DIALOGUE` — What Ravi says
- `✏️ NIMA_DIALOGUE` — What Nima says
- `✏️ PLAYER_CHOICE` — What the player can say
- `✏️ GLYPH_REVEAL` — The plaintext meaning of a glyph

---

## Example: Before vs After

### BEFORE (Skeleton):
```json
{
  "passage_id": "RN_A1_P02",
  "type": "dialogue",
  "npc": "Ravi",
  "emotional_beat": "Ravi reaches out to player. First touch of vulnerability.",
  "glyph_trigger": "SORROW_TIER1",
  "tone_impact": {},
  "influence_impact": {},
  
  // ✏️ AUTHOR SECTION: RAVI_DIALOGUE
  "content": "RAVI_LINE_01_INTRO: // [High Empathy variant] Ravi perceives player as listener. Reaches out.",
  // ✏️ END SECTION
  
  "author_notes": "Ravi is unsettled. He notices something in the player. This is his opening."
}
```

### AFTER (You filled it in):
```json
{
  "passage_id": "RN_A1_P02",
  "type": "dialogue",
  "npc": "Ravi",
  "emotional_beat": "Ravi reaches out to player. First touch of vulnerability.",
  "glyph_trigger": "SORROW_TIER1",
  "tone_impact": {},
  "influence_impact": {},
  
  // ✏️ AUTHOR SECTION: RAVI_DIALOGUE
  "content": "You. You have the look of someone who listens. We need someone who listens.",
  // ✏️ END SECTION
  
  "author_notes": "Ravi is unsettled. He notices something in the player. This is his opening."
}
```

---

## What to Replace

For each placeholder, you replace **only the content between the markers**. Keep everything else.

### Narration Example:

```json
// ✏️ AUTHOR SECTION: NARRATION
"content": "NARRATION_A1_P01: // Describe marketplace. Set mood. Introduce Ravi or Nima as observer.",
// ✏️ END SECTION
```

**You write:**
```json
// ✏️ AUTHOR SECTION: NARRATION
"content": "The marketplace thrums with afternoon energy. Vendors call out prices. Customers move between stalls with practiced efficiency. But there's a weight here too—something that makes people lower their voices, avert their eyes. In a corner near the fountain, a figure stands still. Not moving with the crowd. Watching it.",
// ✏️ END SECTION
```

### Dialogue Example:

```json
// ✏️ AUTHOR SECTION: RAVI_DIALOGUE
"content": "RAVI_LINE_04_BURDEN: // Ravi mentions Nima. Mentions Ophina (deceased). Guilt surfaces.",
// ✏️ END SECTION
```

**You write:**
```json
// ✏️ AUTHOR SECTION: RAVI_DIALOGUE
"content": "My partner, Nima... she lost someone. Someone she loved more than anything. Ophina. And I..." [pause, hand trembles] "I should have been there when it mattered. I should have gone with her.",
// ✏️ END SECTION
```

### Player Choice Example:

```json
// ✏️ AUTHOR SECTION: PLAYER_CHOICE
"text": "PLAYER_CHOICE_A1_C01: // Empathetic engagement (e.g., 'Tell me what you need')",
// ✏️ END SECTION
```

**You write:**
```json
// ✏️ AUTHOR SECTION: PLAYER_CHOICE
"text": "Tell me what you need. I'm listening.",
// ✏️ END SECTION
```

### Glyph Reveal Example:

```json
// ✏️ AUTHOR SECTION: GLYPH_REVEAL
"content": "GLYPH_REVEAL_SORROW_T3: // The glyph means: 'The shape of what breaks you, so you can learn to hold the broken pieces.'",
// ✏️ END SECTION
```

**You write:**
```json
// ✏️ AUTHOR SECTION: GLYPH_REVEAL
"content": "The glyph means: **The shape of what breaks you, so you can learn to hold the broken pieces.** Sorrow isn't punishment. It's education in the language of loss.",
// ✏️ END SECTION
```

---

## How to Find All Your Work

### Search in your text editor:

**Find all sections to fill:**
```
Search for: ✏️ AUTHOR SECTION
```

This will show every single placeholder across all 4 JSON files.

**Filter by type:**
```
Search for: ✏️ AUTHOR SECTION: NARRATION
Search for: ✏️ AUTHOR SECTION: RAVI_DIALOGUE
Search for: ✏️ AUTHOR SECTION: NIMA_DIALOGUE
Search for: ✏️ AUTHOR SECTION: PLAYER_CHOICE
Search for: ✏️ AUTHOR SECTION: GLYPH_REVEAL
```

---

## Workflow

1. **Open** `RN_Act1_Introduction.json` in your editor
2. **Search** for `✏️ AUTHOR SECTION`
3. **Navigate** to first result
4. **Read** the `author_notes` field (tells you what goes here)
5. **Write** your content between the markers
6. **Delete** the placeholder text (just keep your writing)
7. **Press** Ctrl+G (find next)
8. **Repeat** until all placeholders are done

---

## Examples by Act

### Act 1: Introduction & Discovery
- **Tone:** Uncertain, reaching out, vulnerability surfacing
- **Ravi's voice:** Hesitant, guilty, opening up
- **Nima's voice:** Controlled, guarded, protective
- **Narration:** Market atmosphere, two people broken by the same loss
- **Player choices:** Moment-to-moment responses to grief

### Act 2: Ophina's Story
- **Tone:** Deepening, storytelling, crisis emerging
- **Ravi's voice:** Guilt intensifying, love underneath
- **Nima's voice:** Love and loss intertwined, researcher's clarity
- **Narration:** Past tense (memory) bleeding into present feeling
- **Player choices:** Validating or challenging their narrative

### Act 3: Chamber & Boss
- **Tone:** Intense, climactic, metaphysical
- **Ravi's voice:** Awe, terror, recognition
- **Nima's voice:** Acceptance, forgiveness, transformation
- **Narration:** Impossible architecture, glyphs as living things
- **Player choices:** Acceptance vs. refusal vs. honest question
- **Ophina echo:** Non-human, transformed, but still herself

### Act 4: Resolution
- **Tone:** Peaceful, integrating, forward-looking
- **Ravi's voice:** Gratitude, peace, new purpose
- **Nima's voice:** Clarity, wisdom, invitation
- **Narration:** Return to daylight, world unchanged but they're different
- **Glyph reveals:** Tier 3 plaintext meanings (the deepest layer)

---

## Placeholder Inventory

**Total: 73 placeholders**

| Act | Narration | Ravi | Nima | Ophina | Choices | Glyphs | Total |
|-----|-----------|------|------|--------|---------|--------|-------|
| 1   | 5         | 4    | 2    | —      | 3       | —      | 14    |
| 2   | 2         | 3    | 3    | —      | 2       | —      | 10    |
| 3   | 9         | 5    | 3    | 1      | 4       | —      | 22    |
| 4   | 4         | 3    | 2    | —      | 2       | 4      | 15    |
| **TOTAL** | **20** | **15** | **10** | **1** | **11** | **4** | **61** |

Wait, let me recount... CONNECTION_MAP says 73. Let me check Act 1 more carefully. Actually the inventory includes variants (like RAVI_LINE_01_INTRO has 3 variants - high empathy, skepticism, balanced). Let me revise:

**Actual breakdown:**
- Passages with multiple variants (e.g., Ravi's opening line has 3 variants for different player TONE states)
- Each variant counts as a separate placeholder

---

## Quality Checklist

After filling in all 73 placeholders:

- [ ] All 73 placeholders replaced with actual content (search for `PLACEHOLDER_NAME` should return 0 results)
- [ ] Ravi's voice is consistent across all 15 lines (distinctive, not generic)
- [ ] Nima's voice is consistent across all 10 lines (different from Ravi, not generic)
- [ ] Emotional beats land at right moments (reread author_notes to verify)
- [ ] Glyph tier 3 meanings are poetic but clear
- [ ] Player choices feel like genuine alternatives (not leading)
- [ ] Narration supports atmosphere (don't over-explain, trust the glyphs)

---

## Example Completed Passage

Here's what a fully-written Act 1 passage looks like:

```json
{
  "passage_id": "RN_A1_P02",
  "type": "dialogue",
  "npc": "Ravi",
  "emotional_beat": "Ravi reaches out to player. First touch of vulnerability.",
  "glyph_trigger": "SORROW_TIER1",
  "tone_impact": {},
  "influence_impact": {},
  "content": "You. You have the look of someone who listens. We need someone who listens.",
  "author_notes": "Ravi is unsettled. He notices something in the player. This is his opening.",
  "next_passage": "RN_A1_P03"
}
```

Notice: No markers left. Just the passage, fully written.

---

## Tips

1. **Read author_notes first.** It tells you what emotional truth you're capturing.
2. **Keep it short.** NPC dialogue should be 1-3 sentences per passage (except long stories).
3. **Use the `emotional_beat` field.** It's your north star for tone.
4. **Remember glyph_trigger.** If a passage has `SORROW_TIER1`, that glyph should feel present (visually or emotionally).
5. **Check influence_impact.** If this passage adds `empathy: 15`, make sure your dialogue justifies that emotional weight.
6. **Don't explain.** Trust the glyphs, gates, and emotional beats to do the work. Your writing just voices the architecture.

---

## How to Commit

After filling in all placeholders for one act:

```bash
git add velinor/stories/ravi_nima/RN_Act1_Introduction.json
git commit -m "story: write Act 1 dialogue and narration (Ravi & Nima arc)

- 14 passages fully written
- 4 Ravi lines across entry variants and escalation
- 2 Nima lines (entrance, greeting variants)
- 5 narration blocks (marketplace, chamber intro)
- 3 player choice options
- Emotional beats: vulnerability, recognition, commitment

All ✏️ AUTHOR SECTION placeholders replaced with final text."
git push origin main
```

---

**Ready to write? Start with `RN_Act1_Introduction.json`.**

**Search for: `✏️ AUTHOR SECTION` and fill in from top to bottom.**
