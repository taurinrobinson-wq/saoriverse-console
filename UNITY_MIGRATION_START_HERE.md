# Unity Migration: START HERE

**Created:** 2026-06-12  
**Status:** Ready to begin Phase 1

---

## What Was Created For You

Three analysis documents are now in your repo root:

### 📊 **UNITY_MIGRATION_QUICK_REFERENCE.md**
One-page overview with metrics and key decisions. Start here for a bird's-eye view.

### 📋 **UNITY_MIGRATION_ANALYSIS.md** 
Deep technical analysis: what exists, what's portable, what needs rewriting. ~5,000 words. Reference when you need details.

### 📦 **UNITY_MIGRATION_FILE_INVENTORY.md**
Exhaustive file listing: every Python file, data file, asset, doc organized by portability level. Use this when you need to know "where is X?"

### 🗺️ **UNITY_MIGRATION_STRATEGY.md** (NEW - This week)
Phased rollout plan: 6 phases, 24-30 weeks total, with decision points and risk mitigation.

---

## Quick Stats

| Metric | Count |
|--------|-------|
| **Lines of Game Code** | ~15,000 lines Python |
| **Data Records** | 118 glyphs, 21+ NPCs, 50+ dialogue trees |
| **Graphics Assets** | 200+ files (500+ MB) |
| **Story Content** | 6 endings, 4+ acts, 70+ glyphs per playthrough |
| **Design Documentation** | 100+ pages complete specs |

---

## This Week: Phase 1 Checklist

### Phase 1 Goal
Get Unity project set up with assets and data ready to load, **without touching game logic**.

### Tasks (Est. 3-5 hours)

- [ ] **Download & setup:**
  - [ ] Create new Unity 6.4 project
  - [ ] Initialize Git in project (same repo or fork?)

- [ ] **Folder structure:**
  - [ ] Create `Assets/Scenes/`
  - [ ] Create `Assets/Scripts/` (Core, UI, Data, NPCs subdirs)
  - [ ] Create `Assets/Graphics/` (Backgrounds, Characters, Glyphs, UI subdirs)
  - [ ] Create `Assets/Audio/`
  - [ ] Create `Assets/Data/` for JSON files
  - [ ] Create `Assets/Resources/` for prefabs

- [ ] **Copy graphics (45 min):**
  - [ ] All background PNG files → `Assets/Graphics/Backgrounds/`
  - [ ] All character sprites → `Assets/Graphics/Characters/`
  - [ ] All 118 glyph images → `Assets/Graphics/Glyphs/`
  - [ ] UI assets → `Assets/Graphics/UI/`
  - [ ] Configure import settings (Texture Type: Sprite, Filter Mode: Bilinear)

- [ ] **Copy data files (15 min):**
  - [ ] All JSON/CSV files → `Assets/Data/`
  - [ ] Glyph definitions → `Assets/Data/glyphs.json`
  - [ ] NPC data → `Assets/Data/npcs.json`
  - [ ] Dialogue trees → `Assets/Data/dialogue.json`
  - [ ] Story/ending definitions → `Assets/Data/story.json`

- [ ] **Copy documentation (15 min):**
  - [ ] All `.md` files from `velinor/markdowngameinstructions/` → project as text assets
  - [ ] Create a "DESIGN_REFERENCE" folder in project with specs
  - [ ] This is your game design bible during development

- [ ] **Test data loading:**
  - [ ] Write small test script: `JsonUtility.FromJson<GlyphData>(jsonText)`
  - [ ] Verify at least one glyph loads without errors
  - [ ] Verify one NPC loads without errors

- [ ] **Commit to repo:**
  - [ ] `git commit -m "Phase 1: Unity project structure, assets imported, data organized"`

---

## Week 1 Decision Meetings

Schedule these **before** Phase 2 starts:

### Decision 1: Dialogue System (1 hour)
- Keep OpenAI API generating dialogue dynamically? (1 week setup)
- Use pre-written dialogue trees from existing data? (0 weeks setup)
- **Recommendation:** Pre-written. You have tons of content. Add dynamic layer in Phase 5.

### Decision 2: Audio Strategy (30 min)
- Full music + sound design? (2-4 weeks)
- Minimal ambient loops? (1 week)
- Ship silent, add later? (0 weeks)
- **Recommendation:** Minimal. Launch complete, enhance post-release.

### Decision 3: Graphics Quality (30 min)
- Use existing 2D assets as-is? (0 weeks)
- Enhance/upscale existing art? (2-4 weeks)
- Commission new art? (4+ weeks)
- **Recommendation:** As-is. Ship complete, not perfect.

---

## Phase 2 Preview (Weeks 2-4)

Once Phase 1 is done, you'll port game logic to C#:

```csharp
// Example: GameState class (port from Python)
public class GameState {
    public string playerVariant;     // Lior, Lioren, or Lior(en)
    public int coherenceStat;        // 0-100
    public float[] toneStats;        // T, O, N, E
    public List<string> unlockedGlyphs;
    public Dictionary<string, float> npcAttunement;
}

// Example: NPC interaction (port from Python logic)
public class NPCInteractionManager {
    public string GetNPCResponse(string npcId, string action, GameState state) {
        // Load pre-written dialogue from JSON
        // Apply stat gates (e.g., "only show if T > 50")
        // Replace tokens: {player_name}, {player_she_he}, etc.
        // Return dialogue string
    }
}
```

**Key insight:** The logic is straightforward. You're mostly just moving Python dictionaries/classes to C# structs/classes. Very little algorithmic complexity.

---

## Success Criteria for Phase 1

- [ ] Unity project compiles without errors
- [ ] All graphics imported and visible in project
- [ ] All JSON data files load without parse errors
- [ ] Documentation accessible in project
- [ ] Git repo clean and committed

**Expected time:** 3-5 hours  
**Expected completion:** This week

---

## Questions to Answer Before Phase 2

1. **Dialogue:** Dynamic or pre-written?
2. **Audio:** Full, minimal, or none?
3. **Graphics:** Keep, enhance, or commission?
4. **Scope:** Do you want stretch goals (3D characters, animations, voice acting)?
5. **Timeline:** Can you dedicate 20-30 weeks, or is a faster MVPneeded?

---

## Resources

- `UNITY_MIGRATION_STRATEGY.md` — Your roadmap
- `UNITY_MIGRATION_ANALYSIS.md` — Technical details
- `UNITY_MIGRATION_FILE_INVENTORY.md` — Find any file in the repo
- Unity 6.4 documentation — https://docs.unity.com/6.4/
- JsonUtility docs — https://docs.unity3d.com/ScriptReference/JsonUtility.html

---

## Next Contact Point

Once Phase 1 is **complete and committed**, we can:
1. Make the three strategic decisions
2. Create C# class stubs for Phase 2
3. Start porting game logic
4. Have first "hello world" game state working in Unity by end of Week 2

**This is a significant pivot, but very manageable.** The game is data-driven, assets exist, and design is complete. You're mostly reorganizing and porting, not creating from scratch.

Let's ship this. 🚀
