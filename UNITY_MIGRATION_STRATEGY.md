# Velinor: Remnants of the Tone — Streamlit → Unity Migration Strategy

**Status:** MIGRATION INITIATED  
**Target Engine:** Unity 6.4  
**Current Platform:** Streamlit + Python  
**Timeline:** Phased approach, ~20-30 weeks (can compress with parallel work)  
**Priority:** Establish 3D core first, gradually add systems

---

## Phase 1: Foundation & Asset Preparation (Week 1-2)

### Goal
Get Unity project structure set up and assets ready without touching game logic yet.

### Tasks

#### 1.1 Unity Project Setup
- [ ] Create new Unity 6.4 project
- [ ] Set up folder structure:
  ```
  Assets/
  ├── Scenes/
  ├── Scripts/
  │   ├── Core/
  │   ├── UI/
  │   ├── Data/
  │   └── NPCs/
  ├── Graphics/
  │   ├── Backgrounds/
  │   ├── Characters/
  │   ├── UI/
  │   └── Glyphs/
  ├── Audio/
  ├── Data/
  │   └── JSON/ (copy from repo)
  └── Resources/
  ```
- [ ] Configure import settings (textures, sprites)
- [ ] Set up version control (same repo or separate?)

#### 1.2 Asset Migration (NON-PAINFUL)
- [ ] **Copy all graphics directly** (PNG → Unity):
  - 45 backgrounds → `Assets/Graphics/Backgrounds/`
  - 40 character sprites → `Assets/Graphics/Characters/`
  - 118 glyph images → `Assets/Graphics/Glyphs/`
  - UI elements → `Assets/Graphics/UI/`
- [ ] Create sprite atlases for performance
- [ ] Set up canvas & UI scaling (target resolution: 1920×1080)
- [ ] **No code changes needed** — just file organization

#### 1.3 Data File Migration (NON-PAINFUL)
- [ ] Copy all JSON/CSV data files → `Assets/Data/`:
  - Glyph definitions (118 glyphs, 7 domains)
  - NPC character data (21+ characters)
  - Dialogue trees (pre-written scenes)
  - Story/ending definitions
- [ ] Create `JsonUtility` loader scripts (Unity reads native JSON easily)
- [ ] Validate that all data loads without errors

#### 1.4 Documentation Anchoring
- [ ] Copy **all Velinor game documentation** into Unity project (as text assets):
  - CHARACTER_CREATION_MASTER_REFERENCE.md
  - malrik_and_elenya_complete_arc.md
  - player_character_complete_arc.md
  - intimate_tension_framework.md
  - All glyph/NPC specifications
- [ ] This is your **source of truth** during development

### Deliverable
- Unity project with organized assets & data ready to load
- No gameplay yet, but visual foundations complete
- **Time investment:** 3-5 hours

---

## Phase 2: Core Systems Architecture (Week 2-4)

### Goal
Port the **game logic and data structures** from Python to C# without worrying about UI presentation yet.

### Tasks

#### 2.1 Game State Manager (1 week)
Create core classes that mirror Python logic:

```csharp
// Core data structures (port from Python)
[System.Serializable]
public class CharacterVariant {
    public string name;           // Lior/Lioren/Lior(en)
    public int coherenceBaseline;
    public float[] toneStats;     // T, O, N, E
}

[System.Serializable]
public class NPCData {
    public string id;
    public string name;
    public float[] personalityTraits;
    public Dictionary<string, float> attunement; // by player variant
}

[System.Serializable]
public class GlyphData {
    public string id;
    public string domain;         // Legacy, Ache, Sovereignty, etc.
    public string description;
    public int unlockRequirement;
    public float[] statModifiers;
}

public class GameState {
    public CharacterVariant playerVariant;
    public int coherenceStat;
    public Dictionary<string, float> toneStats; // T, O, N, E
    public List<string> unlockedGlyphs;
    public Dictionary<string, float> npcAttunement;
    public int currentScene;
}
```

**Key:** This is **minimal refactoring** of existing Python code to C# classes. Logic stays nearly identical.

#### 2.2 Dialogue & NPC Response System (1 week)
Port the "NPC Response System" that evaluates player stat thresholds:

```csharp
public class NPCInteractionManager {
    public string GetNPCResponse(string npcId, string playerAction, GameState state) {
        // This is your Python logic verbatim, just in C#
        float attunement = state.npcAttunement[npcId];
        float playerEmpathy = state.toneStats[3]; // E stat
        
        // Apply token replacement: {player_name}, {player_she_he}, etc.
        string dialogue = npcData.GetDialogue(playerAction, attunement);
        dialogue = TokenReplacer.Replace(dialogue, state.playerVariant);
        
        return dialogue;
    }
}
```

**Key:** Use your **existing dialogue trees** (stored in JSON). No new dialogue writing needed yet.

#### 2.3 Glyph Unlock & Discovery System (1 week)
Port the glyph cipher engine:

```csharp
public class GlyphSystem {
    public bool CanUnlock(string glyphId, GameState state) {
        GlyphData glyph = glyphDatabase[glyphId];
        // Check stat gates, scene progression, etc.
        return state.coherenceStat >= glyph.unlockRequirement;
    }
    
    public void UnlockGlyph(string glyphId, GameState state) {
        // Add to player inventory
        // Trigger memory unlock
        // Update stats
    }
}
```

**Key:** This is almost pure data-driven; minimal logic rewrite.

#### 2.4 Story/Ending System (1 week)
Port the branching path logic:

```csharp
public class StoryManager {
    public int GetEnding(GameState state) {
        // Your 6 endings are deterministic based on stats
        // Evaluate rules from ending definitions
        return ending;
    }
    
    public void ProgressStory(string choice) {
        // Update game state
        // Trigger next scene
        // Check for new glyph unlocks
    }
}
```

### Deliverable
- All game logic ported to C# classes
- Game state saves/loads correctly
- **No UI yet** — just console logs to verify logic works
- **Time investment:** 2-3 weeks

---

## Phase 3: Basic UI & First Playable (Week 4-8)

### Goal
Create **minimum viable UI** to test that game logic works in Unity, then gradually enhance.

### Tasks

#### 3.1 Bare-Bones Scene System (1 week)
- [ ] Create 2D canvas for dialogue/choices
- [ ] Text display for NPC dialogue
- [ ] Button system for player choices
- [ ] Basic stat display (visual debug at first)
- [ ] **Aesthetic:** Simple, functional; pretty it up later

#### 3.2 Character Selection Screen (3 days)
- [ ] 3 character portraits (use existing assets)
- [ ] Name display (Lior / Lioren / Lior(en))
- [ ] Stat readouts
- [ ] "Start Game" button

#### 3.3 First Playable Scene (3 days)
- [ ] Pick your **first 3 NPCs** to implement:
  - **Malrik** (archive, formal mentor)
  - **Elenya** (ritual, spiritual mentor)
  - **Velinor** (knowledge keeper)
- [ ] Create one simple conversation flow for each
- [ ] Show dialogue, show stat changes, show glyph unlocks
- [ ] Test on different character variants

#### 3.4 Save/Load (1 week)
- [ ] Serialize game state to JSON
- [ ] Load on game start
- [ ] Test data persistence

### Deliverable
- **First playable vertical slice** in Unity
- Character selection works
- Can talk to 3 NPCs
- Glyphs unlock
- Game is playable end-to-end (albeit minimal)
- **Time investment:** 3-4 weeks

---

## Phase 4: Expand & Polish (Week 8-16)

### Goal
Add more content, improve visuals, create game feel.

### Tasks

#### 4.1 NPC Roster Expansion (2 weeks)
- [ ] Implement remaining 18+ NPCs
- [ ] Add their unique dialogue trees
- [ ] Test attunement mechanics
- [ ] Verify intimate moment triggers

#### 4.2 Glyph Library (2 weeks)
- [ ] Implement all 118 glyphs
- [ ] Create unlock conditions
- [ ] Add glyph display/inventory UI
- [ ] Memory unlock sequences

#### 4.3 Scene Progression (1 week)
- [ ] Map out scene graph (marketplace → archive → rituals → collapse → endgame)
- [ ] Implement scene transitions
- [ ] Add location descriptions
- [ ] Environment mood/atmosphere

#### 4.4 Ending Implementation (1 week)
- [ ] Implement all 6 ending paths
- [ ] Final choice mechanic (Restart vs. Abandon Corelink)
- [ ] Ending narration/epilogue

#### 4.5 Visual Polish (1 week)
- [ ] Backgrounds on scenes
- [ ] Character portraits in dialogue
- [ ] Glyph artwork on unlock
- [ ] UI polish (fonts, colors, spacing)

### Deliverable
- Feature-complete game
- All NPCs, glyphs, scenes playable
- All 6 endings accessible
- **Time investment:** 7-8 weeks

---

## Phase 5: 3D Enhancement (Week 16-24)

### Goal
Leverage Unity's **3D capabilities** to make the game world feel richer.

### Tasks

#### 5.1 3D Marketplace Environment (2 weeks)
- [ ] Simple modular 3D marketplace
- [ ] NPC positioning in 3D space
- [ ] Camera control (pan/zoom)
- [ ] Lighting mood

#### 5.2 Character Models (optional, 2-3 weeks)
- [ ] Simple 3D character models (or enhanced 2D sprites)
- [ ] Character animation (idle, speaking, emoting)
- [ ] Dialogue camera angles

#### 5.3 Glyph Visualization (1 week)
- [ ] Animated glyph unlock sequences
- [ ] Glyph floating/glowing effects
- [ ] Cinematic glyph discovery moments

#### 5.4 Sound & Music (1-2 weeks)
- [ ] Ambient marketplace audio
- [ ] NPC voice readiness (if dialogue is added)
- [ ] Glyph unlock sound design
- [ ] Ending music/narration

### Deliverable
- Immersive 3D game world
- Rich audio landscape
- Enhanced visual storytelling
- **Time investment:** 6-8 weeks

---

## Phase 6: Refinement & Release (Week 24+)

### Goal
Polish, test, optimize, ship.

### Tasks
- [ ] Cross-device testing (PC, Mac, Linux initially)
- [ ] Performance optimization
- [ ] Accessibility pass (text sizing, color contrast, subtitles)
- [ ] Beta testing with early players
- [ ] Final content pass (dialogue tweak, pacing adjustments)
- [ ] Release prep (build, docs, update repo)

---

## Critical Path (What Can't Be Skipped)

1. **Game State Architecture** (Week 2-3) — If this is wrong, everything else breaks
2. **First Playable Scene** (Week 4-8) — Proves the core game loop works
3. **Scene Progression** (Week 9-10) — Connects dialogue to story progression
4. **Character/NPC System** (Week 11-13) — The heart of the game

**Parallel work that can happen simultaneously:**
- Graphics refinement (while coding Phase 2-3)
- 3D environment design (while coding Phase 4)
- Audio design (any time after Phase 3)

---

## Decision Points

### Week 1: Dialogue System
**Choice 1: Keep using OpenAI API for dynamic dialogue?**
- **YES** (1 week): Game generates contextual responses
  - Pros: Natural, reactive dialogue
  - Cons: Requires API, latency, moderation
- **NO** (0 weeks): Use pre-written dialogue trees
  - Pros: Controlled, performant, thematic
  - Cons: Less organic, requires writing/tuning

**Recommendation:** Start with pre-written (you have tons already), add dynamic layer later.

### Week 2: Audio
**Choice 2: Add music & sound design?**
- **YES** (2-4 weeks): Full soundscape, composer if budget allows
- **NO** (0 weeks): Ship silent, add sound post-launch
- **MINIMAL** (1 week): Placeholder audio, ambient loops

**Recommendation:** Minimal for launch, enhance post-release.

### Week 3: Graphics Quality
**Choice 3: Enhance existing 2D assets or use as-is?**
- **USE AS-IS** (0 weeks): Launch with current art
- **ENHANCE** (2-4 weeks): Upscale, recolor, add effects
- **HYBRID** (1 week): Use as-is for launch, roadmap improvements

**Recommendation:** As-is for launch. Better to ship complete than perfect.

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Game logic porting bugs | Write unit tests for each system before UI integration |
| Data file format mismatches | Validate JSON schema during load |
| Performance with 118 glyphs | Use object pooling, lazy loading |
| Dialogue tree complexity | Use visual dialogue editor (or stay JSON-based if working) |
| 3D environment scope creep | Define MVP environment before 3D phase starts |

---

## Success Criteria

- [ ] Character selection works (3 variants)
- [ ] Can talk to ≥3 NPCs
- [ ] Glyphs unlock based on stats
- [ ] At least 1 complete ending playable
- [ ] Game saves/loads correctly
- [ ] Runs on Windows/Mac/Linux
- [ ] No crashes on feature-complete flow

---

## Estimated Timeline

| Phase | Weeks | Effort | Status |
|-------|-------|--------|--------|
| 1: Foundation | 2 | Low | Ready to start |
| 2: Architecture | 3 | High | Foundational |
| 3: First Playable | 4 | High | Proves concept |
| 4: Expand | 8 | Medium | Content-heavy |
| 5: 3D Enhance | 8 | Medium | Quality-of-life |
| 6: Polish & Release | 4+ | Medium | Ongoing |
| **Total** | **~24-30** | | **5-7 months** |

**Can compress to 16-20 weeks with 2 developers working in parallel on Phase 2 (architecture) while Phase 1 completes.**

---

## Next Step

1. **This week:** Complete Phase 1 (Unity setup, assets in, data files organized)
2. **Decision meeting:** Choose dialogue strategy, audio approach, graphics quality
3. **Week 2:** Start Phase 2 (port game logic to C#)
4. **Week 4:** First playable scene in Unity
5. **Ongoing:** Test, iterate, report metrics

---

## Resources to Keep Handy

- `UNITY_MIGRATION_ANALYSIS.md` — Detailed technical breakdown
- `UNITY_MIGRATION_FILE_INVENTORY.md` — Every file in the repo organized
- `velinor/markdowngameinstructions/` — Your design specs (copy into Unity project)
- `CHARACTER_CREATION_MASTER_REFERENCE.md` — System definitions
- All glyph/NPC/story data (JSON/CSV files)

**This is a substantial project, but very manageable. The key is: don't rewrite anything that works. Port what exists, test methodically, add 3D flourish last.**
