# Velinor Ink Migration: Evaluation & Strategy

**Date:** February 24, 2026  
**Purpose:** Shift Velinor development to Ink as primary narrative engine  
**Status:** Ready to execute

---

## 1. Ink Capabilities Assessment

### 1.1 Core Requirements vs. Ink Support

| Feature | Required? | Ink Support | Confidence |
|---------|-----------|-------------|------------|
| **Variables** | ✅ Yes | ✅ Full support (VAR, LIST, CONST) | 100% |
| **Conditionals** | ✅ Yes | ✅ `{condition: text A | text B}` | 100% |
| **TONE Stats** | ✅ Yes | ✅ VAR empathy/skepticism/integration/awareness | 100% |
| **Coherence Formula** | ✅ Yes | ✅ Math operations & stored value | 95% |
| **Emotional Gates** | ✅ Yes | ✅ Conditional knot access | 100% |
| **Influence Tracking** | ✅ Yes | ✅ VAR for each NPC (21 vars) | 100% |
| **Dynamic Text** | ✅ Yes | ✅ Glue operator & interpolation | 100% |
| **Branching Logic** | ✅ Yes | ✅ Knots, stitches, diverts | 100% |
| **Glyph Tiers** | ✅ Yes | ✅ Conditional lines per tier | 100% |
| **JSON Export** | ✅ Yes | ✅ Ink compiler exports .json | 100% |
| **Multiplayer Support** | 🟡 Partial | ⚠️ Single-player focus, feasible for state export | 70% |

**Verdict:** ✅ **Ink is fully capable** of implementing Velinor's core mechanics.

### 1.2 Advantages Over Current Twine Approach

| Aspect | Twine 2 | Ink | Winner |
|--------|--------|-----|--------|
| **Writing Experience** | Visual UI (bloat) | Plain text (focused) | **Ink** |
| **Story-First** | Code-second approach | Story-first approach | **Ink** |
| **Branching Visibility** | Graph view (nice but slow) | Knot/stitch mental model (cleaner) | **Ink** |
| **Dialogue Management** | Scattered across JSON | Centralized in .ink files | **Ink** |
| **Version Control** | JSON diffs (binary-like) | Text diffs (clean) | **Ink** |
| **Rapid Iteration** | Reload JSON (tedious) | Save .ink → Open Inky (instant) | **Ink** |
| **Integration** | REST API required | Compile → JSON → Python | **Ink** |
| **Learning Curve** | Medium (visual) | Low (text-based) | **Ink** |

**Verdict:** ✅ **Ink is superior for narrative development.**

### 1.3 Architecture Compatibility

**Current Flow:**
```
Twine 2 JSON → Python backend → REST API → React frontend
```

**New Flow (Ink-First):**
```
.ink files → Inky (playtest) → Ink compiler → .json → Python backend → REST API → React frontend
```

**Impact:**
- ✅ Backend/frontend unchanged
- ✅ Ink is intermediate layer (like Twine, but better)
- ✅ Same API contracts, same integration points
- ✅ No breaking changes to system architecture

---

## 2. Act I Migration Plan

### 2.1 What's Being Migrated

**Current Act I State:**
- ✅ Saori encounter (opening passage + tone intro)
- ✅ Marketplace arrival (setting, NPC introduction)
- ✅ Ravi & Nima encounter (emotional calibration, grief introduction)
- 🟡 Marketplace expansion (outlined, not written)
- ❌ All NPC dialogue (<10 lines total for 21 NPCs)

**Migration Scope (Phase 1):**
1. Saori encounter → main.ink knot
2. Marketplace arrival → marketplace.ink
3. Ravi & Nima → npc_profiles.ink
4. Glyph reveals (2-3) → glyph_reveals.ink
5. Emotional gates (2-3 examples) → tone_system.ink
6. Influence shifts → tracked in npc_profiles.ink
7. TONE stat adjustments → all scenes

**Not Migrating Yet:**
- Acts II-V (can migrate after Act I is solid)
- Multiplayer layer (built after single-player works)
- UI animations (React handles separately)

### 2.2 Timeline & Milestones

**Week 1: Ink Project Setup & Act I Skeleton**
- Create .ink file structure
- Implement TONE stat system in tone_system.ink
- Create knots for Saori, marketplace, Ravi/Nima
- Test in Inky (compile, play through once)

**Week 2: Narrative Content & Glyph Integration**
- Write full Saori dialogue (2-3 paths)
- Write marketplace discovery scenes (4-5 locations)
- Write Ravi base dialogue (10-15 lines)
- Write Nima base dialogue (10-15 lines)
- Embed 2-3 glyphs with tier system

**Week 3: Gating & Influence**
- Implement emotional gates (require coherence >= 70)
- Implement influence shifts (Ravi +0.1, Nima -0.05, etc.)
- Test branching variations (low empathy vs. high empathy paths)
- Verify TONE stat calculations

**Week 4: Export & Backend Integration**
- Export Ink as JSON
- Integrate with Python backend
- Test API endpoints with new story
- Playtest end-to-end

### 2.3 Success Criteria

- ✅ Act I playable in Inky (30-45 min playtime)
- ✅ All TONE stats trackable + visible at end
- ✅ 2-3 gates functional (show different dialogue based on coherence)
- ✅ 2-3 glyphs revealing with tiers
- ✅ Influence map updating per NPC
- ✅ JSON exports cleanly to backend
- ✅ API returns coherent game state

---

## 3. Recommended Ink File Structure

```
velinor-story/
├── main.ink                    # Root, includes everything
├── tone_system.ink            # TONE vars, coherence formula, shared functions
├── npc_profiles.ink           # Saori, Ravi, Nima dialogue blocks
├── glyph_reveals.ink          # Glyph tier logic, unlock conditions
├── marketplace.ink            # Hub scenes, NPC encounters
├── gates.ink                  # Emotional gate helper functions
├── utilities.ink              # Math helpers, string functions
└── README.ink                 # Documentation knot (playable notes)
```

### 3.1 File Responsibilities

**main.ink** (Entry point)
```ink
INCLUDE tone_system.ink
INCLUDE npc_profiles.ink
INCLUDE glyph_reveals.ink
INCLUDE gates.ink
INCLUDE utilities.ink
INCLUDE marketplace.ink

=== STORY_START ===
[Entry point, routes to first scene]
-> saori_encounter
```

**tone_system.ink** (Game mechanics)
```ink
VAR tone_empathy = 50
VAR tone_skepticism = 50
VAR tone_integration = 50
VAR tone_awareness = 50
VAR coherence = 100

// Functions for TONE adjustments, coherence calc
=== adjust_tone(stat, delta) ===
```

**npc_profiles.ink** (NPC dialogue pools)
```ink
=== saori_encounter ===
[Saori intro, branches based on TONE]

=== ravi_dialogue ===
[Ravi base, multiple variations]

=== nima_dialogue ===
[Nima base, multiple variations]
```

**glyph_reveals.ink** (Glyph system)
```ink
=== reveal_glyph(glyph_id) ===
[Return appropriate tier based on gates]

=== promise_held_tier_1 ===
[Hint layer - always visible]

=== promise_held_tier_2 ===
[Context layer - after meeting Ravi]

=== promise_held_tier_3 ===
[Plaintext layer - requires coherence >= 70]
```

**marketplace.ink** (Hub & locations)
```ink
=== marketplace_hub ===
[Central location, choose where to go]

=== market_stalls ===
=== shrine_area ===
=== collapsed_building ===
```

**gates.ink** (Helper functions)
```ink
=== check_coherence_gate(threshold) ===
[Returns true if coherence >= threshold]

=== check_tone_gate(stat, threshold) ===
[Returns true if TONE[stat] >= threshold]

=== check_influence_gate(npc, threshold) ===
[Returns true if influence[npc] >= threshold]
```

**utilities.ink** (Shared logic)
```ink
=== calculate_coherence() ===
[Formula: 100 - avg_deviation(e, s, i, a)]

=== round(value) ===
[Math helper]
```

---

## 4. Sample Ink Implementation (Promise Held Glyph)

**Demonstrates:** Variables, conditionals, glyph tiers, dynamic text

```ink
// In glyph_reveals.ink
=== promise_held ===
~ temp tier = get_glyph_tier("promise_held")

{tier:
  - 1:
    -> promise_held_tier_1
  - 2:
    -> promise_held_tier_2
  - 3:
    -> promise_held_tier_3
}

=== promise_held_tier_1 ===
A soft glow appears: ◈ (interlocking circles, soft blue)

Something constant is present here.

-> DONE

=== promise_held_tier_2 ===
The glyph from before returns, clearer now.

Ravi says: "This is what we hold onto when everything else shifts."

You understand—the promise of companionship held true, steadily.

-> DONE

=== promise_held_tier_3 ===
{coherence >= 70 and tone_empathy >= 70 and influence_ravi >= 0.6:
  "To be held in another's attention, steadily, even as the world cracks open—this is the most sacred promise. Not to fix what's broken, but to witness it, together, and choose to remain."
  
  "This is what Velinor forgot she had."
  
  ~ glyph_promise_held_unlocked = true
  
  -> DONE
- else:
  This truth isn't yet accessible to you.
  -> DONE
}

=== get_glyph_tier(glyph_id) ===
{glyph_id:
  - "promise_held":
    {player_has_met_ravi:
      {coherence >= 70 and tone_empathy >= 70:
        ~ return 3
      - else:
        ~ return 2
      }
    - else:
      ~ return 1
    }
}
```

---

## 5. Competitive Analysis: Twine vs. Ink

### Why Ink Wins for Velinor

**Twine is for:**
- Visual designers who want to see branching tree
- Non-programmers building simple choice-based games
- Games with heavily interconnected passages

**Ink is for:**
- Writers who think in prose first
- Narrative systems with complex logic
- Games with many branching variations
- Teams that want clean version control

**Velinor's Fit:** ✅ **Ink** (logic-heavy, prose-focused, many variations)

### Migration Cost Assessment

**Low-Cost Migration:**
- Ink syntax is simpler than Twine markup
- No visual design to redo
- Same backend integration points
- ~1-2 weeks to convert existing Act I

**No Lock-In:**
- Ink compiles to JSON (same as Twine)
- Can revert to Twine anytime
- Architecture remains unchanged

---

## 6. Playtesting Workflow

### 6.1 Development Loop

```
1. Edit main.ink in VS Code or Inky
2. Save file
3. Open Inky → Click "Build"
4. Play through story in Inky UI
5. Check TONE stats at end
6. Return to step 1
```

**Time per iteration:** 5-10 minutes (vs. 30-60 min with backend reload)

### 6.2 Inky Setup (5 minutes)

```bash
# Install Inky (all platforms)
https://github.com/inkle/inky/releases

# OR use web-based: https://www.inklestudios.com/ink/web-editor/

# Open main.ink in Inky
# Build (auto-compiles)
# Play button starts story

# Check variables panel to see TONE values after each choice
```

### 6.3 Rapid Iteration Checklist

- [ ] Change dialogue → Save → Build → Play (30 sec)
- [ ] Adjust TONE modifier → Save → Build → Play (30 sec)
- [ ] Test coherence gate → Save → Build → Test path (1 min)
- [ ] Add new glyph → Save → Build → Play to unlock (2 min)

**Total iteration:** <5 minutes from edit to playtest

---

## 7. Next Steps to Execute

**Immediate (Next 2 hours):**
1. ✅ Review this evaluation (you're reading it)
2. ⏭️ I'll create: `velinor-story/main.ink` starter project
3. ⏭️ I'll create: All 7 supporting .ink files with structure
4. ⏭️ I'll create: PLAYTESTING_GUIDE.md

**This Week:**
1. Clone/download Ink starter
2. Install Inky
3. Open main.ink in Inky
4. Run through existing structure
5. Start adding Act I narrative content

**By End of Week 1:**
- Act I skeleton complete in Ink
- Saori encounter fully written
- Marketplace scenes drafted
- Ravi/Nima base dialogue written

**By End of Week 2:**
- 2-3 glyphs fully implemented with tiers
- Emotional gates working
- Influence tracking functional
- Full Act I playtestable in Inky

**By End of Week 3:**
- Export to JSON
- Integrate with backend
- Full E2E test (Inky → API → frontend)

---

## 8. Risk Mitigation

**Risk:** Ink has different syntax than Twine
**Mitigation:** Syntax is actually simpler; learning curve is <1 hour

**Risk:** Existing Twine content is lost
**Mitigation:** Keep Twine files; Ink is parallel development path

**Risk:** Backend integration fails
**Mitigation:** JSON export from Ink is standard; fallback to Twine parser

**Risk:** Multiplayer becomes complex in Ink
**Mitigation:** Single-player in Ink first; multiplayer logic in Python backend

---

## 9. Recommendation

**Strategy:** ✅ **YES, migrate to Ink. Here's why:**

1. **Narrative First:** Shift focus from engineering to writing
2. **Speed:** 5-10x faster iteration cycle
3. **Clarity:** .ink files are readable (Twine JSON is not)
4. **Simplicity:** No backend changes needed during Act I writing
5. **Quality:** Authors can focus on story, not mechanics

**Not a Permanent Lock:**
- Ink exports to JSON (same as Twine)
- Can migrate back to Twine anytime
- Backend is unchanged

**Expected Outcome:**
- Complete, playable Act I in Ink by Week 4
- Full vertical slice playable end-to-end
- Ready to decide on Acts II-V approach

---

## Appendix: Ink Syntax Quick Reference

```ink
// Variables
VAR tone_empathy = 50
VAR glyphs_revealed = 0

// Conditionals
{tone_empathy > 70: You feel empathy | You feel detached}

// Choices
* [Say something kind] -> kind_dialogue
* [Stay silent] -> silent_dialogue

// Knots (major sections)
=== marketplace ===
You arrive at the marketplace.

// Stitches (subsections)
= stalls
The stalls are busy.

// Diverts (jumps)
-> marketplace.stalls

// Functions (subroutines)
=== adjust_empathy(delta) ===
~ tone_empathy = tone_empathy + delta

// Tunnel back (like subroutine)
{tone_empathy > 70: [You're ready] -> next_scene}
```

Done! Ready to build the starter project now.
