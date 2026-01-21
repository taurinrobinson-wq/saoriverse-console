# QUICK START: How to Find & Fill Your Writing Sections

## TL;DR

1. **Open** any of the 4 JSON files (RN_Act1_Introduction.json, etc.)
2. **Search** for: `PLACEHOLDER_NAME:`
3. **Replace** that entire line with your actual writing
4. **Done!** That's one placeholder filled.

---

## The Sections Look Like This

### Original Placeholder (Template):

```json
{
  "passage_id": "RN_A1_P02",
  "type": "dialogue",
  "npc": "Ravi",
  "emotional_beat": "Ravi reaches out to player. First touch of vulnerability.",
  "glyph_trigger": "SORROW_TIER1",
  "tone_impact": {},
  "influence_impact": {},
  "content": "RAVI_LINE_01_INTRO: // [High Empathy variant] Ravi perceives player as listener. Reaches out.",
  "author_notes": "Ravi is unsettled. He notices something in the player. This is his opening.",
  "next_passage": "RN_A1_P03"
}
```

**👆 The line with `RAVI_LINE_01_INTRO:` is where you write.**

---

### After You Fill It (Example):

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

**That's it.** The placeholder is gone. Just your actual dialogue remains.

---

## Search & Replace Patterns

### Find All Placeholders:
```
Search: PLACEHOLDER_NAME:
Search: RAVI_LINE_
Search: NIMA_LINE_
Search: NARRATION_
Search: PLAYER_CHOICE_
Search: GLYPH_REVEAL_
```

Each search shows you every section of that type across all 4 files.

---

## What Each Section Needs

### NARRATION (description, prose)

**Example placeholder:**
```
"content": "NARRATION_A1_P01: // Describe marketplace. Set mood. Introduce Ravi or Nima as observer."
```

**Your writing would be:**
```
"content": "The marketplace thrums with afternoon activity. Vendors call out prices. Customers move between stalls with practiced efficiency. But something feels off here. There's a weight to the air—something that makes people lower their voices, avert their eyes."
```

---

### RAVI_DIALOGUE (what Ravi says)

**Example placeholder:**
```
"content": "RAVI_LINE_04_BURDEN: // Ravi reveals he carries guilt. Mentions Nima & Ophina."
```

**Your writing would be:**
```
"content": "My partner, Nima... she lost someone. Someone precious. Ophina. And I..." [his hand trembles slightly] "I should have been there when it mattered most. I should have gone with her."
```

---

### NIMA_DIALOGUE (what Nima says)

**Example placeholder:**
```
"content": "NIMA_LINE_14_REALIZATION: // Nima: 'She's not lost. She's just gone where we can't follow. Yet.'"
```

**Your writing would be:**
```
"content": "She's not lost. She's just gone where we can't follow yet. But if we understand what called her there... maybe we will."
```

---

### PLAYER_CHOICE (what player can say)

**Example placeholder:**
```
"text": "PLAYER_CHOICE_A1_C01: // Empathetic engagement (e.g., 'Tell me what you need')"
```

**Your writing would be:**
```
"text": "Tell me what you need. I'm here to listen."
```

---

### GLYPH_REVEAL (tier 3 plaintext meaning)

**Example placeholder:**
```
"content": "GLYPH_REVEAL_SORROW_T3: // [Plaintext meaning - the breaking that teaches]"
```

**Your writing would be:**
```
"content": "**The breaking that teaches.** Sorrow is not punishment—it's education in the language of loss. What shatters you reveals what mattered most."
```

---

## The `author_notes` Field

Read this BEFORE you write. It tells you:
- What emotional truth to capture
- Whose voice this is
- What's happening contextually
- Tone/energy guidance

**Example:**
```json
"author_notes": "Ravi is unsettled. He notices something in the player. This is his opening."
```

This tells you:
- Ravi is anxious/uncertain
- He's initiating contact (reaching out)
- This is his first line (sets tone for whole arc)
- The player has something Ravi recognizes (good listener)

---

## Act-by-Act Breakdown

### Act 1: Introduction & Discovery
- **How many placeholders?** 14 passages = ~12 sections
- **Who writes:** All three voices (Ravi, Nima, Player)
- **Tone:** Uncertain, vulnerable, reaching out
- **Narration focus:** Market atmosphere, two broken people

### Act 2: Ophina's Story
- **How many placeholders?** 13 passages = ~10 sections
- **Who writes:** Mainly Ravi & Nima (storytelling)
- **Tone:** Nostalgic, guilty, loved, determined
- **Narration focus:** Memory bleeding into present feeling

### Act 3: Chamber & Boss
- **How many placeholders?** 25 passages = ~18 sections
- **Who writes:** All three + Ophina's echo
- **Tone:** Intense, climactic, metaphysical
- **Narration focus:** Impossible architecture, glyph movements, Velinor presence

### Act 4: Resolution
- **How many placeholders?** 15 passages = ~12 sections
- **Who writes:** Mainly Ravi & Nima + Glyph meanings
- **Tone:** Peaceful, integrating, forward-looking
- **Narration focus:** Return to daylight, transformation complete

---

## Making Replacements (VS Code)

1. **Press Ctrl+H** to open Find & Replace
2. **Find:** `PLACEHOLDER_NAME: // [description]`
3. **Replace:** `Your actual dialogue here`
4. **Click:** Replace (or Replace All if confident)
5. **Press Ctrl+H** again to close

---

## How to Know You're Done

For each placeholder:
- [ ] Placeholder name removed (no more `RAVI_LINE_01_INTRO:`)
- [ ] Your writing fills that `"content"` field
- [ ] It makes sense in context (check `author_notes`)
- [ ] Character voice is consistent with other lines by same NPC
- [ ] Emotional beat lands (check `emotional_beat` field)

---

## Total Placeholders to Fill

| Type | Count | Acts | Examples |
|------|-------|------|----------|
| Narration | 20 | All | Market intro, chamber descent, glyph reveals |
| Ravi dialogue | 15 | All | Openings, guilt, transformation, gratitude |
| Nima dialogue | 10 | All | Greeting, revelation, acceptance, realization |
| Ophina echo | 1 | Act 3 | Boss encounter presence |
| Player choices | 11 | All | Empathy/skeptic/honest paths |
| Glyph tier 3 | 4 | Act 4 | Sorrow, Remembrance, Legacy (+ Transcendence tier 2) |
| **TOTAL** | **61** | | |

---

## Quick Tips

1. **Read author_notes first.** It's your creative brief.
2. **Keep dialogue short.** 1-3 sentences per line (except long stories).
3. **Trust the structure.** The emotional beats, glyph triggers, and tone impacts do the heavy lifting. Your dialogue just voices it.
4. **Stay in character.** Ravi sounds different from Nima. Keep voices distinct.
5. **Use sensory details** in narration. Show, don't tell.
6. **Don't explain the glyphs.** Players will learn through emotional moments. Tier 3 meanings should feel like poetic clarifications, not lessons.

---

## Example: One Complete Passage

### Template:
```json
{
  "passage_id": "RN_A1_P02",
  "type": "dialogue",
  "npc": "Ravi",
  "emotional_beat": "Ravi reaches out to player. First touch of vulnerability.",
  "glyph_trigger": "SORROW_TIER1",
  "tone_impact": {"Empathy": 15},
  "influence_impact": {"Ravi": 0.3},
  "content": "RAVI_LINE_01_INTRO: // [High Empathy variant] Ravi perceives player as listener. Reaches out.",
  "author_notes": "Ravi is unsettled. He notices something in the player. This is his opening.",
  "next_passage": "RN_A1_P03"
}
```

### Filled In (Your Version):
```json
{
  "passage_id": "RN_A1_P02",
  "type": "dialogue",
  "npc": "Ravi",
  "emotional_beat": "Ravi reaches out to player. First touch of vulnerability.",
  "glyph_trigger": "SORROW_TIER1",
  "tone_impact": {"Empathy": 15},
  "influence_impact": {"Ravi": 0.3},
  "content": "You have the look of someone who listens. We... we need someone who listens.",
  "author_notes": "Ravi is unsettled. He notices something in the player. This is his opening.",
  "next_passage": "RN_A1_P03"
}
```

**Notice:** Only the `"content"` line changed. Everything else stays exactly the same. The system knows this is Ravi (because `"npc": "Ravi"`), knows the emotional weight (+15 Empathy), knows the influence gain (+0.3 Ravi), knows the glyph is triggered, knows where it goes next. Your job is just to make Ravi's voice real.

---

## Next Steps

1. **Open** `RN_Act1_Introduction.json` in your editor
2. **Search** for `RAVI_LINE_01_INTRO:`
3. **Read** the `author_notes` for that passage
4. **Write** Ravi's actual dialogue
5. **Move** to next placeholder (Ctrl+G to find next)
6. **Repeat** until Act 1 is done
7. **Commit:** `git add RN_Act1_Introduction.json && git commit -m "story: write Act 1 dialogue and narration"`
8. **Move** to Act 2, then 3, then 4

---

## Questions?

- **What if my dialogue is longer than I thought?** That's fine! Keep it in the `"content"` field. The system can handle multi-sentence passages.
- **What if I want to write variations?** The structure already has variant branches (RAVI_LINE_01/02/03 for empathy/skepticism/balanced). Fill them all for richer paths.
- **What if I change my mind?** It's in git. Just revert, rewrite, and re-commit.
- **How do I know if it's "good"?** Playtest it. Load the JSON, run the arc 3+ times, see if the emotional beats land.

---

**You've got this. Start with Act 1. Ravi's opening. Go.**
