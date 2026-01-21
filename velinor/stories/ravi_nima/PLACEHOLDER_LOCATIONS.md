# PLACEHOLDER LOCATIONS: Visual Map

This file shows you exactly what each placeholder looks like in the JSON files, so you know where to find and replace them.

---

## Act 1: Introduction & Discovery (14 passages)

### P01 - Marketplace Narration
**Type:** NARRATION  
**File:** RN_Act1_Introduction.json  
**Location:** Passage P01, field `content`

```json
"content": "NARRATION_A1_P01: // Describe marketplace. Set mood. Introduce Ravi or Nima as observer.",
```

**What you replace it with:**
- Sensory details (sights, sounds, atmosphere)
- Sense of melancholy or undercurrent
- Introduction to one of the NPCs
- 3-5 sentences of prose

---

### P02, P03, P04 - Ravi Opening (3 variants)
**Type:** RAVI_DIALOGUE  
**File:** RN_Act1_Introduction.json  
**Passages:** P02 (High Empathy), P03 (High Skepticism), P04 (Balanced)

```json
"content": "RAVI_LINE_01_INTRO: // [High Empathy variant] Ravi perceives player as listener. Reaches out.",
"content": "RAVI_LINE_02_INTRO: // [High Skepticism variant] Ravi defensive, questioning. Testing player.",
"content": "RAVI_LINE_03_INTRO: // [Balanced variant] Ravi cautious but hopeful. Middle path.",
```

**What you replace them with:**
- Ravi's opening line (different based on player TONE)
- High Empathy: reaches out, vulnerable
- High Skepticism: tests player, guarded
- Balanced: cautious but open

---

### P05 - Choice Point 1
**Type:** PLAYER_CHOICE (3 options)  
**File:** RN_Act1_Introduction.json  
**Passage:** P05

```json
"text": "PLAYER_CHOICE_A1_C01: // Empathetic engagement (e.g., 'Tell me what you need')",
"text": "PLAYER_CHOICE_A1_C02: // Skeptical response (e.g., 'Why should I help?')",
"text": "PLAYER_CHOICE_A1_C03: // Neutral acknowledgment (e.g., 'I'm listening')",
```

**What you replace them with:**
- C01: Compassionate response to Ravi
- C02: Questioning or cautious response
- C03: Neutral/interested response

---

### P06 - Ravi's Burden
**Type:** RAVI_DIALOGUE  
**File:** RN_Act1_Introduction.json  
**Passage:** P06

```json
"content": "RAVI_LINE_04_BURDEN: // Ravi reveals he carries guilt. Mentions Nima & Ophina.",
```

**What you replace it with:**
- Ravi goes deeper
- Mentions his partner Nima
- Mentions Ophina (deceased)
- Guilt surfaces

---

### P08-P09 - Nima Arrives + Speaks
**Type:** NARRATION + NIMA_DIALOGUE  
**File:** RN_Act1_Introduction.json  
**Passages:** P08 (narration), P09 (dialogue variant 1), P10 (dialogue variant 2)

```json
"content": "NIMA_LINE_02_ARRIVAL: // Nima arrives in marketplace. How does she move? What draws attention?",
"content": "NIMA_LINE_01_GREETING: // [High Empathy variant] Nima greets player with recognition.",
"content": "NIMA_LINE_02_GREETING: // [Different tone variant] Nima greets with complexity.",
```

**What you replace them with:**
- P08: Narration describing Nima's presence
- P09: How Nima greets (warmly perceiving player)
- P10: Alternative greeting (different tone)

---

### P13 - Choice Point 2
**Type:** PLAYER_CHOICE  
**File:** RN_Act1_Introduction.json  
**Passage:** P13

```json
"text": "PLAYER_CHOICE_A1_C04: // Acknowledge Nima directly (e.g., 'You understand too')",
```

**What you replace it with:**
- Player acknowledges Nima
- Shows the player recognizes her understanding

---

### P14 - Act 1 Transition
**Type:** NARRATION  
**File:** RN_Act1_Introduction.json  
**Passage:** P14

```json
"content": "NARRATION_A1_P14: // Transition to Act 2. Both NPCs walk with player. Ready to share.",
```

**What you replace it with:**
- Scene shifts to more private space
- Both NPCs are now present and committed
- Ready to tell story

---

## Act 2: Ophina's Story (13 passages)

### P01 - Settling
**Type:** NARRATION  
**File:** RN_Act2_OphinaReveal.json  
**Passage:** P01

```json
"content": "NARRATION_A2_P01: // Marketplace quiets. They find quiet corner. Time to talk.",
```

---

### P02-P03 - Ophina's Life Story
**Type:** RAVI_DIALOGUE + NIMA_DIALOGUE  
**File:** RN_Act2_OphinaReveal.json  
**Passages:** P02 (Ravi), P03 (Nima)

```json
"content": "RAVI_LINE_05_OPHINA_BEFORE: // Describe Ophina's personality, her light, what made her special.",
"content": "NIMA_LINE_04_OPHINA_LOVE: // Nima's perspective. She loved her differently than Ravi. Show that.",
```

**Key:** P03 reveals Nima & Ophina were romantic partners.

---

### P04 - Choice Point 1
**Type:** PLAYER_CHOICE  
**File:** RN_Act2_OphinaReveal.json  
**Passage:** P04

```json
"text": "PLAYER_CHOICE_A2_C01: // Honor the love (e.g., 'That's a beautiful love')",
"text": "PLAYER_CHOICE_A2_C02: // Challenge the narrative (e.g., 'But what if she chose to leave?')",
```

---

### P05-P09 - Guilt, Loss, Mystery
**Type:** RAVI_DIALOGUE, NIMA_DIALOGUE, NARRATION  
**File:** RN_Act2_OphinaReveal.json  
**Passages:** P05-P09

```json
"content": "RAVI_LINE_06_GUILT: // Ravi's guilt surfaces. 'I should have been there'.",
"content": "NIMA_LINE_05_ACCEPTANCE: // Nima's different response. She's accepted Ophina's choice.",
"content": "NARRATION_A2_P07: // Describe the moment of loss. Use sensory detail. Make it feel real.",
"content": "RAVI_LINE_07_GLYPHS_CALLING: // Ravi: 'The glyphs kept calling to her. We didn't understand why.'",
"content": "NIMA_LINE_06_LAST_MESSAGE: // Nima: 'She left us a message. We finally understood it.'",
```

---

### P10 - Choice Point 2
**Type:** PLAYER_CHOICE  
**File:** RN_Act2_OphinaReveal.json  
**Passage:** P10

```json
"text": "PLAYER_CHOICE_A2_C03: // Support them (e.g., 'I'll help you find her')",
"text": "PLAYER_CHOICE_A2_C04: // Hesitate or question (e.g., 'I need to understand more')",
```

---

## Act 3: Chamber & Boss (25 passages - LARGEST)

### P01-P18 - Journey to Chamber
**Type:** Mix of NARRATION, RAVI_DIALOGUE, NIMA_DIALOGUE, PLAYER_CHOICE  
**File:** RN_Act3_Chamber.json  

```json
"content": "NARRATION_A3_P01: // Describe the journey to old district. Atmosphere shifts.",
"content": "RAVI_LINE_09_JOURNEY_FEAR: // Ravi: 'I haven't been back here since...' Fear in his voice.",
"content": "NIMA_LINE_08_PREPARATION: // Nima: 'I've traced her steps. I know where she went.'",
// ... Player choices ...
"content": "NARRATION_A3_P05: // Describe the old district. Ruins, memories, weight of history.",
"content": "NARRATION_A3_P06: // They reach the entrance. Hidden. Veiled. Transcendence glyph faintly visible.",
"content": "NIMA_LINE_09_ENTRANCE: // Nima: 'This is it. This is where she found the glyphs.'",
"content": "NARRATION_A3_P08: // Descending. Stairs spiral down. Glyph symbols light as they pass.",
"content": "RAVI_LINE_10_RECOGNITION: // Ravi: 'I remember this. She described it. The Glyph Throne...'",
"content": "NARRATION_A3_P10: // Interior of chamber. 118 glyphs arranged in spiraling pattern. Throne at center.",
// ... Player choices ...
```

---

### P19-P25 - Boss Encounter & Velinor Reveal
**Type:** NARRATION, RAVI_DIALOGUE, NIMA_DIALOGUE, OPHINA_ECHO, PLAYER_CHOICE  
**File:** RN_Act3_Chamber.json  

```json
"content": "NARRATION_A3_P14: // Describe sensation of connecting to glyphs. Vertigo, awe, expansion.",
"content": "NARRATION_A3_P15: // Research moment. Details emerge about what happened to Ophina here.",
"content": "RAVI_LINE_11_UNDERSTANDING: // Ravi: 'She understood something we didn't. She went deeper than us.'",
"content": "NIMA_LINE_10_RESEARCH: // Nima: 'The data suggests she integrated with the glyph system.'",
"content": "NARRATION_A3_P18: // Throne responds. Ophina's echo rises. She's not gone. She's transformed.",
// CHOICE POINT - P20 - HIGH STAKES
"text": "PLAYER_CHOICE_A3_C05: // Accept Ophina's transformation (e.g., 'You're at peace now')",
"text": "PLAYER_CHOICE_A3_C06: // Refuse to accept (e.g., 'This isn't right. Bring her back')",
"text": "PLAYER_CHOICE_A3_C07: // Ask a deeper question (e.g., 'What does this mean?')",
// Responses to choice...
"content": "RAVI_LINE_12_RESPONSE_ACCEPT: // Ravi accepts (if player accepted). Relief and grief mixed.",
"content": "NIMA_LINE_11_RESPONSE_ACCEPT: // Nima responds (if player accepted). She's already made peace.",
// VELINOR REVEAL
"content": "NARRATION_A3_P23: // Velinor reveal. The glyphs are part of something larger. A consciousness.",
"content": "RAVI_LINE_13_VELINOR_AURA: // Ravi senses it. 'There's something here. Something alive.'",
"content": "NIMA_LINE_12_VELINOR_RECOGNITION: // Nima: 'It's what Ophina was trying to reach. It's what spoke through her.'",
```

---

## Act 4: Resolution (15 passages)

### P01-P07 - Return & Transformation
**Type:** NARRATION, NIMA_DIALOGUE, RAVI_DIALOGUE  
**File:** RN_Act4_Resolution.json  

```json
"content": "NARRATION_A4_P01: // Ascending from chamber. Stairs seem shorter now. Daylight ahead.",
"content": "NARRATION_A4_P02: // Emerge into daylight. City is normal. They are changed. Moment of stillness.",
"content": "NIMA_LINE_14_REALIZATION: // Nima: 'She's not lost. She's just gone where we can't follow. Yet.'",
"content": "RAVI_LINE_14_TRANSFORMATION: // Ravi: 'I can love her where she is now. That's what love learns to do.'",
// CHOICE POINT - P05
"text": "PLAYER_CHOICE_A4_C01: // Focus on future (e.g., 'What does this mean for us now?')",
```

---

### P08-P11 - Glyph Tier 3 Reveals
**Type:** NARRATION + GLYPH_REVEAL  
**File:** RN_Act4_Resolution.json  

```json
"content": "NARRATION_A4_P08: // The glyphs activate. Tier 3 meanings begin to surface.",
"content": "GLYPH_REVEAL_SORROW_T3: // [Plaintext meaning - the breaking that teaches]",
"content": "GLYPH_REVEAL_REMEMBRANCE_T3: // [Plaintext meaning - what you refuse to forget]",
"content": "GLYPH_REVEAL_LEGACY_T3: // [Plaintext meaning - what you choose to leave behind]",
```

**Glyph Tier 3 Meanings:** These should be poetic but clear. The emotional truth of each glyph's full layer.

---

### P12-P15 - Gratitude, Partnership, Closure
**Type:** RAVI_DIALOGUE, NIMA_DIALOGUE, PLAYER_CHOICE, NARRATION  
**File:** RN_Act4_Resolution.json  

```json
"content": "RAVI_LINE_15_GRATITUDE: // Ravi: 'You helped us. But more than that—you helped her.'",
"content": "NIMA_LINE_15_PARTNERSHIP: // Nima: 'We want to study this more. Will you help us? Or walk your own path?'",
// CHOICE POINT - P14
"text": "PLAYER_CHOICE_A4_C02: // Commit to partnership (e.g., 'I'm with you')",
"content": "NARRATION_A4_P15: // Final narration. The arc closes. Player is transformed. Influence locked.",
```

---

## Summary: Find Your Sections

| Act | File | Passages | Placeholders | Key Moments |
|-----|------|----------|--------------|------------|
| 1 | RN_Act1_Introduction.json | 14 | 12 | Market intro, Ravi opens, Nima arrives, commit to act 2 |
| 2 | RN_Act2_OphinaReveal.json | 13 | 10 | Ophina's story, guilt vs acceptance, the ask |
| 3 | RN_Act3_Chamber.json | 25 | 18 | Journey, boss encounter (3 paths), Velinor reveal |
| 4 | RN_Act4_Resolution.json | 15 | 12 | Return, transformation, glyph tier 3, partnership offer |
| **TOTAL** | 4 files | **67** | **~61** | **Full arc** |

---

## Search Shortcuts (VS Code)

- **Find All Act 1 narration:** `Ctrl+F` → type `NARRATION_A1_`
- **Find All Act 3 choices:** `Ctrl+F` → type `PLAYER_CHOICE_A3_`
- **Find All Ravi lines:** `Ctrl+F` → type `RAVI_LINE_`
- **Find All glyphs:** `Ctrl+F` → type `GLYPH_REVEAL_`

Each search highlights every occurrence across all open files. Use `Ctrl+G` or the down arrow to navigate to next match.

---

## When You Finish an Act

1. **Open terminal** in VS Code
2. **Type:**
   ```bash
   git add RN_Act1_Introduction.json
   git commit -m "story: write Act 1 dialogue and narration

   - All 14 passages completed
   - Ravi voice established (vulnerable, guilty, reaching out)
   - Nima introduced (analytical, protective, clear-eyed)
   - 3 player choice branches (empathy/skeptic/neutral)
   - Marketplace atmosphere set
   - Ready to move to Act 2"
   git push origin main
   ```

3. **Move to Act 2**, repeat.

---

Done. You now know exactly where every placeholder is. Go fill them in.
