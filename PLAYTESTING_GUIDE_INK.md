# Velinor Ink Playtesting Guide

**Last Updated:** February 24, 2026  
**Purpose:** How to play and iterate on the Ink-based story  
**Status:** Ready to use

---

## 1. Quick Start (5 minutes)

### 1.1 Installation

**Option A: Inky Desktop App (Recommended)**

1. Visit: https://github.com/inkle/inky/releases
2. Download latest release for your OS (Windows/Mac/Linux)
3. Install and launch
4. Open `velinor-story/main.ink`
5. Click "Build" in the toolbar
6. Click "Play" to start story

**Option B: Web-Based Ink Editor**

1. Visit: https://www.inklestudios.com/ink/web-editor/
2. Create new file or import `main.ink`
3. Click "Build"
4. Click "Play"

**Option C: VS Code**

1. Install "Ink" extension by Inkle (search in Extensions)
2. Open `main.ink` in VS Code
3. Right-click → "Run Story"
4. Story plays in panel on right

### 1.2 First Playthrough (30-45 minutes)

1. Open main.ink in Inky/editor
2. Click Build (if needed)
3. Click Play
4. Read opening dialogue with Saori
5. Make choices (they'll affect TONE stats)
6. Navigate to marketplace
7. Meet Ravi and Nima
8. Explore different locations
9. At end, check final TONE stats

**Expected Flow:**
- Saori intro (5 min) → Marketplace exploration (20 min) → NPC encounters (15 min) → Final stats (5 min)

---

## 2. How TONE Stats Work

### 2.1 Understanding Your Choices

Every choice affects your TONE stats:

```
Choice A: "I want to help you rebuild, together"
  → Empathy +8
  → Integration +5
  → Awareness +3
  → Coherence recalculated
  
Choice B: "Why should I believe you?"
  → Skepticism +8
  → Awareness +3
  → Coherence recalculated
```

### 2.2 Coherence Calculation

```
Formula: Coherence = 100 - average_deviation(E, S, I, A)

Example:
  Empathy: 60
  Skepticism: 40
  Integration: 50
  Awareness: 55
  
  Average: 51.25
  Deviations: |60-51.25| + |40-51.25| + |50-51.25| + |55-51.25| = 24.5
  Average Deviation: 24.5 / 4 = 6.125
  Coherence: 100 - 6.125 = 93.875 ≈ 94
```

**High Coherence (80+):** You can hold multiple truths. Deep NPC dialogue unlocks.  
**Medium Coherence (50-80):** Balanced state. Standard gameplay.  
**Low Coherence (0-50):** Fragmented. Some NPC dialogue restricted.

### 2.3 Tracking During Playthrough

**Check stats:**
- Use `TEST_SCENE_SELECT` → `View Stats` to see current values
- At story end, final stats are automatically displayed
- Watch coherence change as you make choices

---

## 3. Testing Gates & Dialogue

### 3.1 Testing Emotional Gates

**Coherence Gate Example:**

Scene requires coherence >= 70.

```
Test by:
1. Make choices that increase coherence (e.g., integration choices +10)
2. Navigate to gated scene
3. If coherence >= 70: Deep dialogue unlocks
4. If coherence < 70: Alternative dialogue appears
```

**TONE Stat Gate Example:**

Scene requires empathy >= 70.

```
Test by:
1. Make empathy-raising choices ("I showed care")
2. Keep skepticism low (avoid questioning)
3. Navigate to scene
4. Verify correct dialogue branch
```

### 3.2 Testing NPC Influence

**Ravi Trust Gate:**

Influence >= 0.6 unlocks personal dialogue.

```
Test by:
1. Interact with Ravi twice
2. Make choices that increase influence (+0.1, +0.15)
3. Check if influence[ravi] >= 0.6
4. Verify dialogue changes based on trust level
```

**How Influence Works:**

- Default: 0.5 (neutral)
- Increases when: You align with NPC's values
- Decreases when: You contradict NPC's stance
- Cascade: When Ravi's influence increases, Nima's increases partially (0.7 multiplier)

### 3.3 Fast-Testing Individual Scenes

**Use TEST_SCENE_SELECT:**

```
In main.ink, uncomment this line (at very end):
// -> TEST_SCENE_SELECT

Becomes:
-> TEST_SCENE_SELECT

Now when you play:
- Main menu doesn't appear
- You jump to testing menu
- Choose any scene to test
- Test dialogues without replaying full story
```

**Recommended Testing Order:**

1. Saori encounter (foundation)
2. Ravi dialogue (influence testing)
3. Nima dialogue (more complex gating)
4. Promise Held glyph (glyph tier system)
5. Full marketplace exploration (integration)

---

## 4. Glyph Tier Testing

### 4.1 Tier 1 (Always Visible)

Appears whenever player encounters the glyph.

```
Testing:
1. Play through story normally
2. When glyph appears: Check Tier 1 text
3. Verify symbol (◈), color (soft blue), emotional signal
```

### 4.2 Tier 2 (Context Layer)

Appears after meeting relevant NPC.

```
Testing: Promise Held glyph
1. Start story
2. Meet Ravi (dialogue branch)
3. Return to glyph scene
4. Verify Tier 2 context appears (Ravi's dialogue about promise)
```

### 4.3 Tier 3 (Plaintext Layer)

Appears only if gates are passed.

**Promise Held requires:**
- Coherence >= 70
- Empathy >= 70
- Influence[Ravi] >= 0.6

```
Testing:
1. Make empathy + integration choices (raise both stats)
2. Build trust with Ravi (multiple interactions)
3. When these gates pass: Tier 3 unlocks
4. Verify full plaintext meaning appears
5. If gates not passed: Verify fallback message
```

### 4.4 Glyph Summary at End

```
In story: "Check my emotional state" → View Glyphs

Shows all glyphs revealed + which tiers unlocked
```

---

## 5. Common Testing Scenarios

### Scenario A: High Coherence Playthrough

**Goal:** Test deep NPC dialogue by maintaining high coherence

```
Strategy:
1. Saori: Choose integration-friendly option
2. Marketplace: Balance empathy with skepticism
3. Ravi: Show consistent care (empathy +8 choices)
4. Nima: Balance skepticism and empathy (appears tough at first, then opens)

Expected Result:
- Coherence stays 65-75 throughout
- Deep dialogue unlocks in final encounters
- All glyphs reach Tier 3
- NPCs express deep trust
```

### Scenario B: Fragmented Playthrough

**Goal:** Test low-coherence dialogue to verify gates work correctly

```
Strategy:
1. Saori: Question everything (skepticism +8)
2. Marketplace: Show no empathy (avoid caring choices)
3. Ravi: Be detached and cold
4. Nima: Challenge her authority

Expected Result:
- Coherence drops to 30-40
- NPC dialogue becomes surface-level
- Glyphs stuck at Tier 1
- NPCs remain cautious/distant
```

### Scenario C: Empathy-Focused Playthrough

**Goal:** Test stat dominance by maxing one TONE stat

```
Strategy:
1. Every choice: Pick empathy option
2. Avoid skepticism, integration, awareness choices
3. Give all NPCs maximum care and attention

Expected Result:
- Empathy reaches 80+
- Other stats lag (skepticism ~30)
- Coherence moderate (50-60)
- Ravi/Nima deeply connected
- Saori feels understood but mistrusted
```

### Scenario D: Skepticism-Focused Playthrough

**Goal:** Test skeptical/questioning path

```
Strategy:
1. Every choice: Question, probe, demand evidence
2. Challenge Saori's motives
3. Test Ravi & Nima's stories
4. Don't build trust easily

Expected Result:
- Skepticism 80+
- Empathy low (~30)
- Coherence low (40-50)
- NPCs wary but respect your thinking
- Deep dialogue locked
```

---

## 6. Editing & Iterating

### 6.1 Editing in Inky

1. Open `main.ink` in Inky
2. Left panel: Knots + stitches (structure)
3. Center panel: Edit dialogue text
4. Edit any dialogue or choice
5. Save (Ctrl+S)
6. Click "Build" to recompile
7. Click "Play" to test changes

**Note:** If you change structure (add/rename knots), you must rebuild.

### 6.2 Editing in VS Code

1. Open `main.ink` in VS Code
2. Edit dialogue directly
3. Save (Ctrl+S)
4. Right-click → "Run Story" to test
5. Story auto-rebuilds on save

### 6.3 Rapid Iteration Loop

**Total time per edit: 2-5 minutes**

```
1. Edit dialogue in editor (30 sec)
2. Save (1 sec)
3. Build (automatic or manual, 5 sec)
4. Play button to start story (2 sec)
5. Navigate to changed scene (30 sec - 2 min)
6. Test the change (1-2 min)
7. Return to edit (10 sec)

Total: 2-5 minutes per iteration
```

**Example: Change Ravi's opening dialogue**

```
1. Open npc_profiles.ink
2. Find === ravi_first_meeting ===
3. Edit dialogue text
4. Save
5. Test → Open main.ink → Play → Navigate to Ravi → See change

Total: 3 minutes
```

### 6.4 Common Edits

**Add a choice:**
```ink
* [New choice text]
    ~ adjust_tone("empathy", 5)
    -> destination_knot
```

**Change TONE impact:**
```ink
// Old:
~ adjust_tone("empathy", 8)

// New:
~ adjust_tone("empathy", 12)
```

**Edit NPC dialogue:**
```ink
=== nima_dialogue ===
OLD: "I'm still deciding about you."
NEW: "I'm trying to understand you."
```

**Add glyph reveal:**
```ink
* [Glyph appears]
    ~ glyphs_revealed = glyphs_revealed + 1
    -> promise_held
```

---

## 7. Playtesting Checklist

Use this to verify all systems are working:

### Core Systems
- [ ] TONE stats track correctly (check at end)
- [ ] Coherence calculates properly (should change each choice)
- [ ] Dialogue branches appear/disappear based on gates
- [ ] NPC influence tracks and cascades

### Story Flow
- [ ] Saori opening makes sense and onboards player
- [ ] Marketplace feels like real hub with real choice
- [ ] Ravi dialogue feels emotionally authentic
- [ ] Nima dialogue tests player's authenticity
- [ ] Each location offers meaningful decisions

### Glyphs
- [ ] Promise Held appears at right moment
- [ ] Tier 1 always visible
- [ ] Tier 2 appears after Ravi dialogue
- [ ] Tier 3 unlocks only when gates pass
- [ ] Other glyphs (2) functional

### UI/Flow
- [ ] No broken links (choices that lead nowhere)
- [ ] Stats visible when requested
- [ ] Final summary appears at story end
- [ ] Testing menu works (if enabled)

### Edge Cases
- [ ] Low coherence dialogue appears correctly
- [ ] High influence dialogue differs from low influence
- [ ] Influence cascade works (Ravi increases → Nima slightly increases)
- [ ] No gates are impossible (all should be passable with right choices)

---

## 8. Debugging

### 8.1 If Story Won't Build

**Error:** "Unexpected token" or "Syntax error"

```
Solution:
1. Check for unclosed { } brackets
2. Check for mismatched - else blocks
3. Check for undefined variables
4. Check knot names (no spaces, only letters/underscores)
```

Example error:
```ink
{tone_empathy > 70
    ~ return true  // Missing closing }
}
```

### 8.2 If Choice Doesn't Work

**Issue:** Choice selected but nothing happens

```
Solution:
1. Check that -> destination_knot exists
2. Check knot name spelling (case-sensitive)
3. Verify the knot is not empty
4. Look for broken variable names
```

Example:
```ink
* [Go to Ravi] -> ravi_dialogue  // Check ravi_dialogue EXISTS
```

### 8.3 If Stats Don't Update

**Issue:** Make choice but TONE stat doesn't change

```
Solution:
1. Check `adjust_tone()` is called
2. Verify stat name is correct ("empathy", not "empath")
3. Verify delta is number (not string)
4. Check statement is not inside a condition

Example:
{empathy > 70:
    ~ adjust_tone("empathy", 5)  // This won't fire if empathy NOT > 70
}
```

### 8.4 If Coherence Doesn't Change

**Issue:** Coherence stays same despite TONE changes

```
Solution:
Make sure to recalculate:
    ~ coherence = calculate_coherence()

Add this after any tone adjustment.
```

### 8.5 Viewing Compiled JSON

**To see the JSON that gets exported to Python:**

In Inky:
1. File → Play → Settings
2. Enable "Export JSON"
3. Build story
4. Open generated `.json` file
5. See game state structure

---

## 9. Next Steps After Playtesting

### When Act I Is Solid

1. **Export to JSON:**
   - In Inky: Build → Export JSON
   - Save as `velinor_act_i.json`

2. **Integrate with Backend:**
   - Drop JSON in Python's `stories/` folder
   - Update API to load this story
   - Test API endpoints with new story

3. **Test Full Stack:**
   - Start Python API server
   - Load story in React frontend
   - Verify game state syncs correctly
   - Check glyph tiers render properly

4. **Prepare Act II:**
   - Start new Ink file or new `marketplace` section
   - Structure: Archive rebuild arc, Malrik & Elenya romance
   - Test in parallel with Act I

---

## 10. Ink Syntax Quick Reference

```ink
// Variables (Declare at top)
VAR tone_empathy = 50
VAR glyphs_revealed = 0

// Knots (Major sections)
=== saori_encounter ===
Text here.

// Stitches (Subsections)
=== knot_name ===
= sub_section
Text here.

// Choices
* [Choice text] -> destination

// Conditionals
{condition: true text | false text}

// If-else blocks
{some_var > 50:
    -> high_path
- else:
    -> low_path
}

// Variables in text
You have {tone_empathy} empathy.

// Math operations
~ temp result = (a + b) / 2

// Function calls
~ adjust_tone("empathy", 8)

// Tunnels (like subroutine, returns)
-> knot_name

// Diverts (jump to knot)
-> DONE  // Ends story
-> knot  // Continues story
```

---

## Summary: Your Development Loop

**Every iteration:**

1. **Edit:** Change dialogue, TONE values, choices (5 min)
2. **Test:** Play in Inky, make choice, check result (5 min)
3. **Iterate:** Adjust until satisfied (10 min)
4. **Verify:** Run playtesting checklist (10 min)

**Total per feature:** 30-45 minutes

**Act I complete:** 4 weeks of focused writing

---

**Good luck, storyteller. The work is ahead, but the tools are ready.**
