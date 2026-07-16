# VELINOR_EXECUTION_ROADMAP.md

**Production Architecture Phase — Week-by-Week Sequencing for 3-Month, 6-Month, and 12-Month Timelines**

**Status:** Stable architecture, ready for execution  
**Current Phase:** Phase 1 (Stabilize Core)  
**Last Updated:** January 20, 2026  
**Timeline Horizon:** January — December 2026

> **Principle:** You're not inventing anymore. You're executing.  
> The architecture is coherent. The systems are stable. The emotional OS is real.  
> This roadmap is about velocity, prioritization, and ruthless sequencing.

---

## Executive Summary

| Timeline | Outcome | Scope | Risk Level | Recommendation |
|----------|---------|-------|-----------|-----------------|
| **3 months (12 weeks)** | Complete, playable, emotionally coherent Velinor | Minimal polish, lean NPC lines, simple UI | **HIGH** | Go if you commit to no scope creep |
| **6 months (24 weeks)** | Polished game with good content, all systems working | Full NPC lines, solid UI, 1 round of QA | **MEDIUM** | Recommended sweet spot |
| **12 months (48 weeks)** | Masterpiece-ready game with breathing room | All polish, content richness, multiple iterations | **LOW** | Luxury timeline; can add new systems here |

---

## Phase Overview (All Timelines)

| Phase | Duration | Focus | Output | Blocker |
|-------|----------|-------|--------|---------|
| **Phase 1: Stabilize Core** | 2–4 weeks | Foundation lock | Frozen emotional OS, glyph corpus, passing tests | None |
| **Phase 2: Build Playable Spine** | 4–8 weeks | Story + NPC logic | Complete story, all NPCs response-ready, collapse wired | Phase 1 complete |
| **Phase 3: Frontend Integration** | 3–6 weeks | API + UI | Fully playable web version | Phase 2 complete |
| **Phase 4: Content + Polish** | 4–8 weeks | Depth + shine | More lines, glyph moments, ending cinematics, sound | Phase 3 complete |
| **Phase 5: QA + Playtesting** | 2–4 weeks | Refinement | Edge cases fixed, pacing tuned, emotional arcs validated | Phase 4 complete |

---

## 🌒 PHASE 1: Stabilize the Core (2–4 weeks)

### Goal
Lock the foundation. The emotional OS, glyphs, traits, and core mechanics become frozen — this is
your physics engine now.

### Workstreams (Can Run in Parallel)

#### Workstream 1A: Generate Full Glyph Corpus (1 week)

**What:** Generate all 118 glyphs with full 3-tier cipher (hint→context→plaintext)

**Tasks:**
- [ ] Use glyph generation script: `velinor/tools/generate_glyphs.py` (or create if missing)
- [ ] Generate 75 base glyphs (comfort, crisis, growth, connection, understanding, transcendence)
- [ ] Generate 36 fragment glyphs (intensity, temporal, relational variants)
- [ ] Generate 7 transcendence glyphs (special cipher rules)
- [ ] Validate all glyphs with: `velinor/data/glyphs_complete.json`
- [ ] Run glyph tests: `pytest velinor/tests/test_glyph_cipher.py`

**Output:**
- ✅ `velinor/data/glyphs_complete.json` — 118 glyphs, all tiers defined
- ✅ Test results: 100% passing glyph cipher tests

**Owner:** Backend lead  
**Time:** 5–7 days  
**Risk:** Glyph generation incomplete or semantically weak — **Mitigation:** Pre-define glyph seeds/templates

---

#### Workstream 1B: Run Full Test Suite (1 week)

**What:** Execute all 84 tests. Fix failures. Lock in test coverage.

**Tasks:**
- [ ] Run full suite: `pytest velinor/tests/ -v`
- [ ] Categorize failures:
  - Red (breaks gameplay): Fix immediately
  - Yellow (edge cases): Log for Phase 5 QA
  - Green (passing): Maintain coverage
- [ ] Fix all Red failures
- [ ] Document Yellow issues in `PHASE_1_TEST_FAILURES.md`
- [ ] Achieve: 90%+ tests passing (Red=0)

**Output:**
- ✅ Test report: X/84 passing, Y failures categorized
- ✅ All Red failures fixed
- ✅ Yellow issues documented for Phase 5

**Owner:** QA lead  
**Time:** 3–5 days  
**Risk:** Failures reveal unstable systems — **Mitigation:** Fix highest-impact tests first (orchestrator, trait system, coherence)

---

#### Workstream 1C: Freeze Emotional OS (1 week)

**What:** Lock TONE stats, coherence formula, emotional gates, influence mechanics. No more changes.

**Tasks:**
- [ ] Review & lock: `velinor/engine/trait_system.py`
- [ ] Review & lock: `velinor/engine/coherence_calculator.py`
- [ ] Review & lock: `velinor/engine/npc_response_engine.py` (gate evaluation)
- [ ] Document in: `velinor/EMOTIONAL_OS_FROZEN.md`
  - TONE stat ranges and impact
  - Coherence formula (immutable)
  - Gate types and operators (immutable)
  - Influence calculation (immutable)
- [ ] Get stakeholder sign-off: "This is our physics engine. No changes."

**Output:**
- ✅ `EMOTIONAL_OS_FROZEN.md` — locked specification
- ✅ Stakeholder acknowledgment

**Owner:** Lead architect  
**Time:** 2–3 days  
**Risk:** Stakeholders push for changes mid-project — **Mitigation:** Document *why* each rule exists (emotional coherence principle)

---

#### Workstream 1D: Clean Dead Code (3–5 days)

**What:** Remove prototypes, failed experiments, unused modules.

**Tasks:**
- [ ] Audit: `velinor/engine/` — remove prototype files
- [ ] Audit: `velinor/data/` — remove old JSON versions
- [ ] Audit: `velinor/tools/` — remove dev-only scripts (keep clean ones)
- [ ] Audit: `tests/` — remove duplicate/legacy test files
- [ ] Verify no imports break: `pytest velinor/tests/test_import*.py`

**Output:**
- ✅ Codebase is clean (no dead weight)
- ✅ All imports verified

**Owner:** Code owner  
**Time:** 2–3 days  
**Risk:** Accidentally delete something important — **Mitigation:** Back up before, grep for imports before deletion

---

### Phase 1 Exit Criteria ✅

- [ ] 118 glyphs generated and in `glyphs_complete.json`
- [ ] 80%+ tests passing (all Red fixed, Yellow logged)
- [ ] Emotional OS frozen and documented
- [ ] Codebase cleaned of dead code
- [ ] Team alignment: "We don't invent anymore. We execute."

**Phase 1 Duration:** 2–4 weeks  
**Parallelization:** All 4 workstreams can run simultaneously → compress to 1 week if full team

---

## 🔥 PHASE 2: Build the Playable Spine (4–8 weeks)

### Goal (2)
Write the story. Wire the choices. Embed glyphs. Connect collapse to endings. The game becomes
playable end-to-end.

### Critical Path
Story Spine → NPC Responses → Collapse Event → Endings Testing (Each depends on previous)

#### Workstream 2A: Implement Full Story Spine (2–3 weeks)

**What:** Write all passages, wire all choices, map story flow.

**Files:**
- `velinor/stories/story_definitions.py` — Main content file

**Tasks:**
- [ ] Phase 1 passages (10–15): Opening, introduction, NPC meets
- [ ] Phase 2 passages (20–30): Marketplace, choices, relationship building
- [ ] Phase 3 passages (10–15): Collapse setup, emotional pressure
- [ ] Phase 4 passages (15–20): Collapse event, branching endings
- [ ] Phase 5 passages (10–15): Ending sequences (all 6 endings)
- [ ] Wire all choices with `tone_impact`, `influence_impact`, `gates`
- [ ] Embed glyphs: Each glyph appears 2–5 times in story
- [ ] Test story navigation: `pytest velinor/tests/test_passage_manager.py`

**Content Minimums:**
- Opening hook (1 passage) ✓
- 5 unique NPCs introduced with personality (5 passages) ✓
- Coherence pressure moment (1 passage) ✓
- Collapse event trigger (1 passage) ✓
- 6 unique endings (6 passages) ✓
- ~70 story passages total
- ~150 total choices (average 2–3 per passage)

**Output:**
- ✅ `story_definitions.py` — complete passage graph
- ✅ Story tests passing

**Owner:** Narrative lead  
**Time:** 10–15 days  
**Risk:** Story feels disjointed or choices don't matter — **Mitigation:** Map emotional arc before writing; make each choice meaningfully impact tone/influence

---

#### Workstream 2B: Implement All NPC Response Pools (2–3 weeks)

**What:** Write response patterns for each of 21 NPCs. Minimum viable lines per NPC.

**File:** `velinor/data/npc_profiles.json` — response pool expansion

**Per NPC, write:**
- Greeting (1–3 variants)
- Response to high empathy (2–3 lines)
- Response to high skepticism (2–3 lines)
- Trust gate response (2–3 lines, unique)
- Coherence gate response (1–2 lines)
- Collapse reaction (1 line)
- Pre-ending line (1 line)

**Math:**
- 21 NPCs × ~15 lines/NPC = ~315 lines total
- Not 1000 lines. Lean but functional.
- Each line should embed 1 trait or glyph reference

**Tasks:**
- [ ] Create response pool template for each NPC
- [ ] Write minimum viable lines per category
- [ ] Tag each line with traits/glyphs it activates
- [ ] Wire into NPC response engine
- [ ] Test: `pytest velinor/tests/test_npc_manager.py`

**Output:**
- ✅ `npc_profiles.json` — all 21 NPCs with response pools
- ✅ NPC tests passing

**Owner:** Narrative lead  
**Time:** 10–15 days  
**Risk:** NPC lines feel generic or repetitive — **Mitigation:** Define 1–2 unique "voice tags" per NPC, apply consistently

---

#### Workstream 2C: Integrate Collapse Event (1–2 weeks)

**What:** Wire the collapse — the emotional midpoint that shifts game state.

**Files:**
- `velinor/engine/event_timeline.py` — Collapse timing
- `velinor/stories/story_definitions.py` — Collapse passage
- `velinor/data/npc_profiles.json` — NPC reactions post-collapse

**Tasks:**
- [ ] Define collapse trigger: Coherence threshold + phase check
- [ ] Create collapse passage: Player forced choice (no backing out)
- [ ] Define post-collapse game state:
  - Which endings are still reachable?
  - How do NPC responses change?
  - Do glyphs behave differently?
- [ ] Wire NPC reactions to post-collapse state
- [ ] Test: `pytest velinor/tests/test_collapse_event.py`

**Output:**
- ✅ Collapse event fully implemented
- ✅ Tests passing

**Owner:** Game designer  
**Time:** 5–10 days  
**Risk:** Collapse feels arbitrary or doesn't impact gameplay — **Mitigation:** Make collapse visibly close off 2–3 endings; force player commitment

---

#### Workstream 2D: Implement All 6 Endings (1–2 weeks)

**What:** Write ending passages for all 6 endings. Make each emotionally distinct.

**File:** `velinor/stories/story_definitions.py`

**Per Ending, write:**
- Final passage (2–3 pages of text)
- Glyph revelations (3–5 glyphs fully decoded)
- TONE state reflection (how did player's choices shape them?)
- Emotional payoff (coherence-based? relationship-based? transcendent?)

**Endings:**
- Transcendence (rare, requires all gates + high coherence)
- Integration (balanced emotional growth)
- Compassion (empathy-driven)
- Wisdom (skepticism + awareness)
- Survival (low coherence, perseverance)
- Dissolution (extreme incoherence, loss of self)

**Tasks:**
- [ ] Write each ending passage
- [ ] Define ending trigger conditions in `ending_system.py`
- [ ] Add glyph reveals per ending
- [ ] Test ending paths: `pytest velinor/tests/test_ending_system.py`

**Output:**
- ✅ All 6 endings written and wired
- ✅ Ending selection tests passing

**Owner:** Narrative lead  
**Time:** 5–10 days  
**Risk:** Endings feel similar or unearned — **Mitigation:** Each ending should reflect different TONE combinations; make final passage emotionally resonant

---

### Phase 2 Exit Criteria ✅

- [ ] Story spine complete (all passages and choices)
- [ ] All NPCs have response pools
- [ ] Collapse event fully integrated
- [ ] All 6 endings written and wired
- [ ] Story tests passing (90%+)
- [ ] Full game playable end-to-end (via orchestrator)

**Phase 2 Duration:** 4–8 weeks  
**Parallelization:** Workstreams 2A + 2B can start in parallel; 2C + 2D depend on 2A completion

---

## 🌿 PHASE 3: Frontend Integration (3–6 weeks)

### Goal (3)
Velinor-web comes online. API works. UI renders glyphs, NPCs, choices. Game is playable on the web.

### Workstreams (Mostly Sequential — API first, then UI)

#### Workstream 3A: Implement API Endpoints (1–2 weeks)

**What:** Implement all 6 endpoints per `VELINOR_INTEGRATION_CONTRACT.md`

**File:** `velinor/velinor_api.py`

**Endpoints:**
- [ ] `POST /api/game/start` — Initialize session
- [ ] `POST /api/game/action` — Process choice
- [ ] `GET /api/game/status` — Get state
- [ ] `POST /api/game/save` — Save to slot
- [ ] `GET /api/game/load` — Load from slot
- [ ] `GET /api/debug` — Debug info

**Tasks:**
- [ ] Implement each endpoint per contract spec
- [ ] Validate all request/response formats
- [ ] Wire to orchestrator/game engine
- [ ] Handle errors with specified codes
- [ ] Test with cURL and Postman: `velinor/tests/test_api_import.py`

**Output:**
- ✅ All 6 endpoints working
- ✅ API tests passing

**Owner:** Backend lead  
**Time:** 5–10 days  
**Risk:** API contract misalignment with frontend — **Mitigation:** Test API before frontend starts (cURL early, often)

---

#### Workstream 3B: Implement Frontend Components (2–3 weeks)

**What:** Build React components to render game state.

**Files:**
- `src/components/GameScene.tsx` — Main orchestrator
- `src/components/DialogueBox.tsx` — Dialogue display
- `src/components/ChoiceButtons.tsx` — Choices
- `src/components/NpcPortrait.tsx` — NPC image
- `src/components/StatusHud.tsx` — TONE/coherence display
- `src/components/SaveLoadModal.tsx` — Persistence UI

**Tasks:**
- [ ] Build GameScene orchestrator (connects to store, calls API)
- [ ] Build DialogueBox (renders passage text + glyph hints)
- [ ] Build ChoiceButtons (renders choices, handles clicks)
- [ ] Build NpcPortrait (renders NPC image from assets)
- [ ] Build StatusHud (renders TONE stats, coherence)
- [ ] Build SaveLoadModal (save/load UI with slots)
- [ ] Integrate with Zustand store
- [ ] Test each component: `__tests__/components/`

**Output:**
- ✅ All core components built and rendering
- ✅ Component tests passing

**Owner:** Frontend lead  
**Time:** 10–15 days  
**Risk:** API response format mismatch with component expectations — **Mitigation:** Agree on contract first, test API before component build

---

#### Workstream 3C: Wire API Client (1 week)

**What:** Implement `GameApiClient` in velinor-web per contract.

**File:** `src/lib/api.ts`

**Tasks:**
- [ ] Create GameApiClient class with all methods
- [ ] Implement session management (store sessionId, include in requests)
- [ ] Implement error handling with retry logic
- [ ] Test each method: `__tests__/lib/api.test.ts`

**Output:**
- ✅ GameApiClient fully functional
- ✅ API tests passing

**Owner:** Frontend lead  
**Time:** 3–5 days  
**Risk:** Session handling bugs — **Mitigation:** Test session lifecycle (start → action → save → load)

---

#### Workstream 3D: Implement Save/Load UI (1 week)

**What:** Build UI for persisting game state across sessions.

**Tasks:**
- [ ] Create save slot UI (10 slots, show timestamp + game state)
- [ ] Implement save button: calls `GameApiClient.saveGame()`
- [ ] Implement load button: calls `GameApiClient.loadGame()`
- [ ] Test save/load flow end-to-end

**Output:**
- ✅ Save/load UI fully functional
- ✅ Persistence tests passing

**Owner:** Frontend lead  
**Time:** 3–5 days  
**Risk:** Save slot data loss — **Mitigation:** Test slot overwrites, persistence across browser refreshes

---

### Phase 3 Exit Criteria ✅

- [ ] All 6 API endpoints implemented and tested
- [ ] All core UI components built and rendering
- [ ] GameApiClient fully functional
- [ ] Save/load UI working
- [ ] Full game playable on web: start → play → save/load → end

**Phase 3 Duration:** 3–6 weeks

---

## 🌑 PHASE 4: Content Expansion + Polish (4–8 weeks)

### Goal (4)
The game becomes *good* — deeper characters, more glyph resonance, cinematic endings,
sound/animation polish.

### Workstreams (Non-Blocking — Can Run in Parallel)

#### Workstream 4A: Expand NPC Lines (2 weeks)

**What:** Add more response variants to make NPCs feel distinct and reactive.

**Current:** ~15 lines/NPC  
**Target:** ~30–50 lines/NPC (depth without bloat)

**Tasks:**
- [ ] Per NPC: Write 2–3 variants of each response type
- [ ] Add NPC-specific dialogue quirks (speech patterns, references, emotional tells)
- [ ] Add reactions to specific glyphs (glyph resonance)
- [ ] Add post-collapse alternative responses (different tone)

**Output:**
- ✅ NPC profiles feel alive and reactive
- ✅ 21 NPCs with 30–50 lines each

**Owner:** Narrative lead  
**Time:** 10 days  
**Risk:** Lines feel repetitive — **Mitigation:** Use "emotional voice tags" per NPC, vary sentence structure

---

#### Workstream 4B: Add Glyph Resonance Moments (1–2 weeks)

**What:** Moments in story where glyphs appear meaningfully in dialogue/choices.

**Tasks:**
- [ ] Map each glyph to 2–5 story moments
- [ ] Add choices that reference glyphs thematically
- [ ] Add NPC dialogue that triggers glyph revelations
- [ ] Embed glyphs in ending passages (final revelations)

**Output:**
- ✅ Each glyph appears 3–5 times in story
- ✅ Glyphs feel like emotional language, not decoration

**Owner:** Narrative lead  
**Time:** 5–10 days  
**Risk:** Glyph embedding feels forced — **Mitigation:** Only add glyphs where thematically relevant; less is more

---

#### Workstream 4C: Polish Endings (1 week)

**What:** Make ending passages cinematic and emotionally resonant.

**Tasks:**
- [ ] Per ending: Add sensory details (what does this emotional state *feel* like?)
- [ ] Per ending: Add final glyph revelation (what does player's journey mean?)
- [ ] Per ending: Add player reflection (how did their choices shape them?)
- [ ] Vary ending length/style to feel distinct

**Output:**
- ✅ All 6 endings feel emotionally complete
- ✅ Each ending is 2–5 pages of rich text

**Owner:** Narrative lead  
**Time:** 5 days  
**Risk:** Endings feel saccharine or incomplete — **Mitigation:** Get feedback on emotional authenticity, iterate

---

#### Workstream 4D: Add Sound & Animation (2–3 weeks)

**What:** Subtle audio and visual effects that enhance emotional impact (optional but high-value).

**Tasks:**
- [ ] Add background music per phase/emotional state
- [ ] Add sound effects: collapse event, glyph reveals, ending transitions
- [ ] Add animations: NPC portrait fades, choice highlighting, coherence meter changes
- [ ] Add transition effects between passages

**Output:**
- ✅ Audio tracks per phase
- ✅ Sound effects for key moments
- ✅ Smooth UI animations

**Owner:** Frontend lead / Audio designer  
**Time:** 10–15 days  
**Risk:** Audio/animation feels unnecessary — **Mitigation:** Keep it minimal and thematic; less is more

---

#### Workstream 4E: UI Polish (1–2 weeks)

**What:** Make UI feel polished and intuitive.

**Tasks:**
- [ ] Refine typography and spacing
- [ ] Add loading states and error handling UI
- [ ] Add tooltips for glyph tiers, gate explanations
- [ ] Add keyboard shortcuts (1–5 for choices, arrow keys for navigation)
- [ ] Add accessibility: ARIA labels, color contrast, keyboard navigation

**Output:**
- ✅ UI feels professional and accessible
- ✅ Keyboard navigation working

**Owner:** Frontend lead  
**Time:** 5–10 days  
**Risk:** Polish takes too long — **Mitigation:** Time-box to 10 days; defer minor polish to post-launch

---

### Phase 4 Exit Criteria ✅

- [ ] NPCs feel distinct and reactive (30–50 lines each)
- [ ] Glyphs embedded meaningfully (3–5 appearances each)
- [ ] All endings feel emotionally complete and distinct
- [ ] Audio/animation enhances experience
- [ ] UI feels polished and accessible

**Phase 4 Duration:** 4–8 weeks  
**Parallelization:** All workstreams can run in parallel

---

## 🌌 PHASE 5: QA + Playtesting (2–4 weeks)

### Goal (5)
Find and fix edge cases. Validate emotional arcs. Ensure pacing feels right.

### Workstreams

#### Workstream 5A: Full Playthrough Testing (1 week)

**What:** Play the game end-to-end multiple times, trying different paths.

**Tasks:**
- [ ] Playthrough 1: High empathy path → Integration ending
- [ ] Playthrough 2: High skepticism path → Wisdom ending
- [ ] Playthrough 3: Mixed path → Survival ending
- [ ] Playthrough 4: Balanced path → Transcendence attempt
- [ ] Log all bugs, pacing issues, emotional dead zones

**Output:**
- ✅ Bug list and pacing notes
- ✅ Emotional arc validated across paths

**Owner:** Lead designer  
**Time:** 3–5 days  
**Risk:** Bugs block playthroughs — **Mitigation:** Fix blocking bugs immediately, defer cosmetic bugs

---

#### Workstream 5B: Coherence Edge Cases (3–5 days)

**What:** Test edge cases in coherence calculation, emotional gates, influence system.

**Tasks:**
- [ ] Test extreme TONE values (all 100, all 0, misaligned)
- [ ] Test gate edge cases (influence exactly at threshold, coherence boundary)
- [ ] Test collapse trigger timing (early/late/at threshold)
- [ ] Test ending determination (all 6 reachable?)
- [ ] Run: `pytest velinor/tests/ -v --tb=short`

**Output:**
- ✅ Edge case bugs fixed
- ✅ Tests passing

**Owner:** QA lead  
**Time:** 3–5 days  
**Risk:** Edge cases cause game-breaking bugs — **Mitigation:** Fix highest-impact first, test combinations

---

#### Workstream 5C: Narrative Flow Refinement (3–5 days)

**What:** Smooth out story pacing and emotional beats.

**Tasks:**
- [ ] Check passage-to-passage transitions feel natural
- [ ] Validate choice consequences (player choices should be felt)
- [ ] Check NPC consistency (does character arc feel coherent?)
- [ ] Validate collapse event timing (does it surprise without feeling random?)
- [ ] Refine ending trigger conditions (are endings reachable but not trivial?)

**Output:**
- ✅ Story pacing feels right
- ✅ Emotional beats land

**Owner:** Narrative lead  
**Time:** 3–5 days  
**Risk:** Major story rewrites needed — **Mitigation:** Accept minor tweaks only; defer major rewrites to post-launch

---

#### Workstream 5D: Performance & Stability (3–5 days)

**What:** Ensure game is stable and responsive.

**Tasks:**
- [ ] Test full session lifecycle (start → 50 actions → save → load → 50 more actions)
- [ ] Test memory usage over time (no leaks?)
- [ ] Test API response times (is it snappy?)
- [ ] Test browser compatibility (Chrome, Firefox, Safari)
- [ ] Stress test: Run 10 simultaneous sessions

**Output:**
- ✅ Game stable over long sessions
- ✅ API responsive
- ✅ Cross-browser compatible

**Owner:** QA + DevOps lead  
**Time:** 3–5 days  
**Risk:** Performance issues discovered too late — **Mitigation:** Test early and often; profile before optimizing

---

### Phase 5 Exit Criteria ✅

- [ ] 5+ full playthroughs completed without blocking bugs
- [ ] All edge cases tested and fixed
- [ ] Narrative flow feels coherent and paced
- [ ] Game stable and performant over long sessions
- [ ] Cross-browser tested

**Phase 5 Duration:** 2–4 weeks

---

## 📋 Timeline Comparison

### 🚀 3-Month Timeline (12 weeks)

**Goal:** Complete, playable, emotionally coherent Velinor — not polished, but real.

| Phase | Duration | Approach |
|-------|----------|----------|
| **Phase 1** | 1 week | Minimal scope: glyph corpus only, skip polish |
| **Phase 2** | 2 weeks | Lean story: 70 passages, ~3 choices/passage, minimal NPC lines |
| **Phase 3** | 2 weeks | Simple UI: core components only, no fancy animations |
| **Phase 4** | 0 weeks | **SKIP** — Defer to post-launch |
| **Phase 5** | 1 week | Light QA: run 3 full playthroughs, fix Red bugs only |

**Total:** 6–7 weeks of execution + 1 week buffer = 7–8 weeks

**What This Gets You:**
- ✅ Full game playable end-to-end
- ✅ All systems working
- ✅ All 6 endings reachable
- ✅ Emotional OS functional
- ❌ Minimal voice variety per NPC
- ❌ Simple UI (no animations, minimal polish)
- ❌ No sound

**Launch Checklist:**
- [ ] Phase 1 done
- [ ] Phase 2 done (story complete, crude but coherent)
- [ ] Phase 3 done (API + UI working)
- [ ] Phase 5 light (no blocking bugs)

**Risks:**
- **Scope creep:** Will kill this timeline. No changes once Phase 2 starts.
- **API bugs:** Will block Phase 3. Test API early with cURL.
- **Story coherence:** Hard to fix at end. Lock story concept before writing.

---

### 🎯 6-Month Timeline (24 weeks) — RECOMMENDED

**Goal:** Polished game with good content and solid systems.

| Phase | Duration | Approach |
|-------|----------|----------|
| **Phase 1** | 2–3 weeks | Full scope: all 118 glyphs, all tests passing, full cleanup |
| **Phase 2** | 4–5 weeks | Full story: 100+ passages, all NPCs with decent response pools |
| **Phase 3** | 3–4 weeks | Solid UI: all components, basic animations, good UX |
| **Phase 4** | 3–4 weeks | Content + polish: expanded NPC lines, glyph resonance, ending refinement |
| **Phase 5** | 2–3 weeks | Full QA: 5+ playthroughs, edge case testing, performance tuning |

**Total:** 17–21 weeks of execution + 3–5 weeks buffer = 20–26 weeks

**What This Gets You:**
- ✅ Complete, playable, emotionally coherent game
- ✅ Good character voice variety (each NPC distinct)
- ✅ Polished UI with good UX
- ✅ Glyph system feels meaningful
- ✅ Endings feel earned and emotional
- ✅ Minimal but effective sound
- ✅ Stable, well-tested, cross-browser compatible

**Launch Checklist:**
- [ ] All phases complete
- [ ] 5+ full playthroughs with no blocking bugs
- [ ] All 6 endings tested and reachable
- [ ] Performance benchmarked and optimized

**Risks:**
- **Timeline creep:** Medium — allow 25–30% buffer time
- **Content quantity:** NPCs could demand more lines (mitigate: define "done" for NPC up-front)
- **Polish paralysis:** Could extend Phase 4 (mitigate: time-box to 4 weeks, defer minor polish)

---

### 👑 12-Month Timeline (48 weeks)

**Goal:** Masterpiece-ready game with breathing room for iteration.

| Phase | Duration | Approach |
|-------|----------|----------|
| **Phase 1** | 3–4 weeks | Full cleanup, full test coverage, multiple rounds of optimization |
| **Phase 2** | 6–8 weeks | Rich story: 150+ passages, 50+ lines/NPC, intricate branching |
| **Phase 3** | 4–5 weeks | Refined UI: animations, transitions, accessibility, cross-browser polish |
| **Phase 4** | 6–8 weeks | Full content + polish: multiple content passes, audio, animations, refinement |
| **Phase 5** | 3–4 weeks | Comprehensive QA: 10+ playthroughs, all edge cases, performance optimization |
| **Buffer** | 4–6 weeks | Contingency for unknowns, iteration, refinement |

**Total:** 26–35 weeks of execution + 4–6 weeks buffer = 30–41 weeks

**What This Gets You:**
- ✅ Everything from 6-month timeline, PLUS:
- ✅ Rich, branching story with multiple paths
- ✅ Deep NPC characterization (50+ lines each, consistent arcs)
- ✅ Full soundtrack (music + SFX)
- ✅ Polished animations and transitions
- ✅ Multiple rounds of playtesting + iteration
- ✅ Accessibility-first design
- ✅ Potential for post-launch DLC/updates

**Launch Checklist:**
- [ ] All phases complete with multiple iterations
- [ ] 10+ full playthroughs across diverse playstyles
- [ ] All systems stress-tested
- [ ] Accessibility audit passed
- [ ] Performance optimized for all devices

**Risks:**
- **Perfectionism:** Easy to fall into endless polish loop (mitigate: define "done" per phase, enforce deadlines)
- **Scope expansion:** Temptation to add new systems (mitigate: FREEZE emotional OS in Phase 1, no new mechanics)
- **Team fatigue:** Long timeline can drain energy (mitigate: celebrate milestones, take breaks)

---

## 🎯 Choosing Your Timeline

### Choose **3 Months** if:
- You want to ship something *real* ASAP
- You're willing to iterate post-launch
- Your audience expects a minimum viable game
- You can commit to **zero scope creep**

### Choose **6 Months** if:
- You want a polished game ready for reviews
- You have the bandwidth for sustained execution
- You want to avoid post-launch scrambles
- You can handle some scope changes (within bounds)
- **RECOMMENDATION:** This is the sweet spot

### Choose **12 Months** if:
- You want to build a masterpiece
- You have a patient audience or funding
- You want to iterate multiple times
- You can afford to be thoughtful and thorough
- You may add new systems later (post-launch)

---

## 🚨 Critical Risks & Mitigations

| Risk | 3-Month | 6-Month | 12-Month | Mitigation |
|------|---------|---------|----------|-----------|
| **Scope creep** | 🔴 CRITICAL | 🟡 HIGH | 🟢 LOW | Freeze emotional OS Day 1. No new systems. |
| **API bugs block frontend** | 🔴 CRITICAL | 🟡 HIGH | 🟢 LOW | Test API with cURL before frontend starts. |
| **Story incoherence** | 🟡 HIGH | 🟢 MEDIUM | 🟢 LOW | Write story outline + emotional arc first. |
| **NPC lines too generic** | 🟡 HIGH | 🟢 MEDIUM | 🟢 LOW | Define voice tags per NPC; enforce consistency. |
| **Test failures mid-project** | 🟡 HIGH | 🟢 MEDIUM | 🟢 LOW | Fix all tests in Phase 1. |
| **Performance issues** | 🟡 HIGH | 🟢 MEDIUM | 🟢 LOW | Benchmark early; optimize in Phase 5. |
| **Ending feels unearned** | 🔴 CRITICAL | 🟡 HIGH | 🟢 LOW | Playtesting from Phase 3 onward. |

---

## 📊 Progress Tracking Template

### Weekly Standup (Use This Template)

```
## Week X: Phase [Y]

**Completed This Week:**
- [ ] Specific task 1
- [ ] Specific task 2
- [ ] Specific task 3

**In Progress:**
- [ ] Specific task (% done)
- [ ] Specific task (% done)

**Blocked / At Risk:**
- [ ] Issue + mitigation plan

**Next Week:**
- [ ] Specific task
- [ ] Specific task
- [ ] Specific task

**Burn-Down:**
- Tasks: X completed, Y at risk, Z remaining
- Timeline: On track / Slipping by X days
```

---

## 🎬 Execution Principles

### 1. **Lock, Then Execute**
Lock emotional OS, story skeleton, and API contract *first*. Then execute without revisiting.
Revisiting kills velocity.

### 2. **Build Vertically**
Go from "start" to "end" for one path first. Then expand breadth (more NPCs, more glyphs, more
endings). Never build all features halfway.

### 3. **Test Early, Test Often**
Run full playthroughs starting Phase 3. Find issues while they're cheap to fix. Don't wait until
Phase 5 to discover game-breaking bugs.

### 4. **Defer Polish**
Phases 1–3: Functional > Beautiful Phase 4: Add beauty Phase 5: Refine In 3-month timeline: Skip
Phase 4 entirely.

### 5. **Define "Done"**
Per phase: What does success look like? Be ruthless: If it's not in "done", it's not getting done.
Defer nice-to-haves to post-launch.

---

## 🎯 Next Steps: Pick Your Timeline

1. **Read this document** ← You are here 2. **Align with stakeholders** — Which timeline? Which
scope? 3. **Lock Phase 1** — Freeze emotional OS, commit to glyph generation 4. **Start Week 1** —
Phase 1, Workstream 1A (glyph corpus) 5. **Weekly standups** — Use template above, track velocity

---

**Last Updated:** January 20, 2026  
**Next Review:** After Phase 1 completion  
**Owner:** Project lead

---

## Appendix: Detailed Task Breakdown

### Phase 1, Workstream 1A: Glyph Corpus Generation

**Subtasks:**
- [ ] Set up glyph generation script (if not exists)
- [ ] Generate 75 base glyphs:
  - [ ] 12 comfort glyphs
  - [ ] 12 crisis glyphs
  - [ ] 12 growth glyphs
  - [ ] 12 connection glyphs
  - [ ] 12 understanding glyphs
  - [ ] 3 transcendence glyphs
- [ ] Generate 36 fragment glyphs:
  - [ ] 18 intensity variants
  - [ ] 9 temporal frames
  - [ ] 9 relational contexts
- [ ] Generate 7 transcendence glyphs
- [ ] Validate all 118 glyphs in `glyphs_complete.json`
- [ ] Run glyph tests and fix failures
- [ ] Spot-check glyph semantics (do 3-tiers make sense?)

**Time Estimate:** 40–56 hours

---

### Phase 2, Workstream 2A: Story Spine Implementation

**Subtasks by Phase:**

**Phase 1 (Intro):**
- [ ] Opening passage: Welcome to Velinor
- [ ] 5 NPC intros (1 passage each)
- [ ] 5 first-choice passages (where do you go next?)
- [ ] Narrative hook: Establish mystery

**Phase 2 (Marketplace):**
- [ ] 20 choice/consequence passages
- [ ] 5 NPC deepening moments
- [ ] Relationship branching (different NPCs, different paths)

**Phase 3 (Collapse Setup):**
- [ ] Emotional pressure builds
- [ ] Foreshadowing collapse
- [ ] Coherence reaches threshold

**Phase 4 (Collapse + Branching):**
- [ ] Collapse event passage
- [ ] Post-collapse split: Which NPCs support you? Which turn away?
- [ ] 3–4 branching paths toward endings

**Phase 5 (Endings):**
- [ ] Ending passages (6 total, 2–3 pages each)
- [ ] Glyph revelations per ending
- [ ] Emotional payoff

**Time Estimate:** 80–120 hours

---

That's your roadmap. Pick your timeline, lock Phase 1, and start.

The architecture is stable. You're ready to execute.
