# Velinor → Unity: Quick Migration Reference

**One-page summary for stakeholders & developers**

---

## 📊 KEY METRICS AT A GLANCE

| Metric | Value | Notes |
|--------|-------|-------|
| **Total Game Files** | 60+ Python files | All in `velinor/` directory |
| **Game Logic** | ~4,000 LOC | Core mechanics, systems, state |
| **Glyph Count** | 118 unique glyphs | Across 7 emotional domains |
| **NPC Count** | 21+ characters | Each with unique profiles & arcs |
| **Story Endings** | 6 distinct paths | Based on TONE trajectory |
| **Background Images** | 45+ assets | 200 MB PNG/JPG files |
| **Character Sprites** | 40+ assets | 150 MB PNG with transparency |
| **Glyph Artwork** | 118+ assets | 300 MB PNG illustrations |
| **Game Data Files** | 50+ JSON/CSV | All directly portable |
| **Documentation** | 100+ pages | Complete design specs |

---

## ✅ WHAT'S READY TODAY

### Data (100% Portable)
- 118 glyph definitions (JSON)
- 21+ NPC profiles (JSON)
- Story structure files (JSON)
- Emotional lexicon (13,000+ words)
- Trait & stat system definitions

### Graphics (100% Portable)
- 45 background images
- 40 character sprites
- 118 glyph illustrations
- UI overlay assets
- 3D entrance model (needs conversion)

### Game Logic (90% Portable)
- TONE trait system (4 dimensions)
- Coherence calculator
- Glyph cipher engine
- NPC response system
- Story/ending system
- Skill system

### Documentation (100% Portable)
- Complete game specification
- All system mechanics defined
- Character arcs documented
- Story structure defined
- Integration contracts

---

## 🔄 WHAT NEEDS CONVERSION

### Format Conversion
| Source | Target | Effort |
|--------|--------|--------|
| SVG overlays | PNG | Low |
| OBJ 3D model | FBX | Low |
| SQLite DB | JSON | Low |
| CSV data | JSON | Low |
| WebM video | MP4 | Low |

### Framework Adaptation
| Component | Current | Target | Effort |
|-----------|---------|--------|--------|
| UI system | Streamlit | Canvas | 3-4 weeks |
| State mgmt | st.session_state | GameState/Events | 1-2 weeks |
| Save/load | JSON files | PlayerPrefs/JSON | 1 week |
| Scene mgmt | Page routing | Unity Scene Manager | 1 week |
| Game loop | Callbacks | Update/Coroutines | 1 week |

---

## 🔴 WHAT REQUIRES REWRITING

### Game Engine Rewrite
```
Current (Streamlit):        New (Unity):
─────────────────────       ────────────
Callback-based              Update-based game loop
Button interactions         Input system
Streamlit state mgmt        Unity state/persistence
Image display               Sprite rendering
Scene routing               Scene Manager
```

### UI System Rewrite
```
Streamlit Components        Unity Canvas UI
─────────────────────       ────────────────
st.sidebar                  Sidebar panel
st.columns()                Layout groups
st.button()                 Button components
st.image()                  Image components
st.write()                  Text display
```

---

## 📈 EFFORT ESTIMATE

### Total Project: 20-30 Weeks (1 Developer)

```
Data Layer              2 weeks  ▓░░░░░░░░░░░░░░░░░░░░░░░░
Core Logic             3 weeks  ▓▓▓░░░░░░░░░░░░░░░░░░░░░
Glyph/Cipher System    1 week   ▓░░░░░░░░░░░░░░░░░░░░░░░
NPC/Dialogue System    2 weeks  ▓▓░░░░░░░░░░░░░░░░░░░░░░
Story/Ending System    2 weeks  ▓▓░░░░░░░░░░░░░░░░░░░░░░
Game Loop/Scene Mgmt   3 weeks  ▓▓▓░░░░░░░░░░░░░░░░░░░░░░
UI/Canvas System       4 weeks  ▓▓▓▓░░░░░░░░░░░░░░░░░░░░░
Graphics Integration   1 week   ▓░░░░░░░░░░░░░░░░░░░░░░░
Audio System           1 week   ▓░░░░░░░░░░░░░░░░░░░░░░░
Testing & Polish       3 weeks  ▓▓▓░░░░░░░░░░░░░░░░░░░░░░
                       ─────────
TOTAL                  22 weeks
```

### With 2 Developers (Parallel Work)
- **Data Layer + Logic:** Person A (6 weeks)
- **UI + Graphics:** Person B (8 weeks)
- **Integration & Polish:** Both (2 weeks)
- **Total Project Time:** 8-10 weeks

---

## 🎯 CRITICAL DECISIONS

### 1. Dialogue System
**Current:** LLM-based dynamic dialogue (OpenAI/Claude API)

**Options for Unity:**
| Option | Pros | Cons | Effort |
|--------|------|------|--------|
| **Keep API** | Same dialogue engine | Network dependency, API cost | 1 week |
| **Local LLM** | Offline, no cost | Complex setup | 2-3 weeks |
| **Pre-written Trees** | Simple, deterministic | Labor-intensive | 3-4 weeks |

**Recommendation:** Keep API (minimal work, proven system)

### 2. Audio System
**Current:** Not implemented (MIDI files exist as prototypes)

**Options:**
| Option | Impact | Effort |
|--------|--------|--------|
| **Add music only** | Polish | 1 week |
| **Add music + SFX** | High polish | 2 weeks |
| **Skip audio** | Minimal impact | 0 weeks |

**Recommendation:** Add music at least

### 3. Graphics Quality
**Current:** Mixed resolutions, PNG sprites

**Options:**
| Option | Impact | Effort |
|--------|--------|--------|
| **Use existing** | Functional | 0 weeks |
| **Upscale/improve** | Polish | 1-2 weeks |
| **New art direction** | Fresh look | 4-6 weeks |

**Recommendation:** Use existing (ship faster)

---

## 📦 DELIVERABLES CHECKLIST

### Phase 1: Foundation
- [ ] C# project setup
- [ ] JSON → C# data models
- [ ] Game data imported
- [ ] Graphics assets organized

### Phase 2: Mechanics
- [ ] TONE trait system working
- [ ] Coherence calculator functional
- [ ] NPC system operational
- [ ] Glyph cipher engine working

### Phase 3: Game Loop
- [ ] Game loop running
- [ ] Scene transitions working
- [ ] Choice system functional
- [ ] State persistence working

### Phase 4: UI
- [ ] Dialogue display working
- [ ] Choice buttons responsive
- [ ] Sidebar UI complete
- [ ] Glyph codex overlay done

### Phase 5: Polish
- [ ] All assets integrated
- [ ] Audio system complete
- [ ] Save/load working
- [ ] Cross-platform tested

---

## 🚨 KEY RISKS & MITIGATION

| Risk | Severity | Mitigation |
|------|----------|-----------|
| LLM dialogue dependency | HIGH | Decide approach early (Week 1) |
| Complex story branching bugs | HIGH | Implement comprehensive tests (Phase 2) |
| Asset organization issues | MEDIUM | Use consistent naming from start |
| Performance on target platform | MEDIUM | Profile frequently, optimize early |
| Save file compatibility | MEDIUM | Design versioning system (Week 1) |
| UI responsiveness | MEDIUM | Use Canvas optimization patterns |

---

## 📋 PRE-MIGRATION CHECKLIST

- [ ] **Review** VELINOR_MASTER_DOC.md (understand all systems)
- [ ] **Decide** on dialogue approach (API/local/pre-written)
- [ ] **Decide** on audio scope
- [ ] **Decide** on graphics approach
- [ ] **Setup** Unity project (2021 LTS or 2022+)
- [ ] **Setup** version control
- [ ] **Create** data models from JSON schemas
- [ ] **Organize** graphics assets by category
- [ ] **Plan** UI mockups from Streamlit reference
- [ ] **Identify** external dependencies (LLM API, etc.)

---

## 🔗 KEY FILE REFERENCES

### Must-Read Documentation
1. **VELINOR_MASTER_DOC.md** — All game systems
2. **02_SIX_ENDINGS_EXPLICIT_MAP.md** — Ending conditions
3. **TONE_STAT_SYSTEM.md** — TONE mechanics
4. **CHARACTER_CREATION_MASTER_REFERENCE.md** — Player system

### Must-Have Data
1. **glyph_lexicon_rows.json** — All glyphs
2. **npc_profiles.json** — All NPCs
3. **cipher_seeds.json** — Unlock conditions
4. **Glyph_Organizer.json** — Structured glyph data

### Must-Reference Code
1. **trait_system.py** — TONE logic (translate as-is)
2. **coherence_calculator.py** — Coherence formula (identical)
3. **glyph_cipher_engine.py** — Cipher logic (translate as-is)
4. **npc_response_engine.py** — Response selection (translate as-is)

---

## 💡 PRO TIPS

### Asset Pipeline
```
Raw PNG/JPG
    ↓ (Organize by type)
Sprite Atlas/Texture Atlas
    ↓ (Import to Unity)
Sprite Renderers
    ↓ (Layer in scene)
Composed Scene
```

### Data Pipeline
```
JSON files
    ↓ (Parse with JSON.NET or Unity's JsonUtility)
C# Data Models
    ↓ (Store as ScriptableObjects or runtime)
Game Access
```

### Code Translation
```
Python logic (algorithm)
    ↓ (Don't change algorithm)
C# translation (identical logic)
    ↓ (Only change syntax/framework)
Unity integration
```

---

## 📞 DECISION MATRIX

**Quick-look table for implementation choices:**

```
DECISION              | IMPACT  | DECIDE BY | EFFORT IF...
─────────────────────┼─────────┼──────────┼─────────────
Dialogue System      | CRITICAL| Week 1   | API: 1wk | Local: 3wk | Pre: 4wk
Audio System         | MEDIUM  | Week 1   | Yes: 1-2wk | No: 0wk
Graphics Upgrades    | LOW     | Week 2   | Yes: 2-4wk | No: 0wk
Target Platform      | HIGH    | Week 1   | Affects optimization
Art Direction        | MEDIUM  | Week 2   | Affects asset pipeline
Save System Design   | HIGH    | Week 1   | Affects architecture
```

---

## 🎓 LEARNING RESOURCES

### For Understanding the Game
- Read VELINOR_MASTER_DOC.md (2-3 hours)
- Play through current Streamlit version
- Review story documentation
- Understand 6 endings

### For C# Implementation
- Review trait_system.py (easy translation)
- Understand JSON parsing in C#
- Learn Unity Canvas UI
- Learn ScriptableObjects

### For Game Loop
- Understand Update-based game loops
- Learn coroutines in C#
- Understand state machine patterns
- Scene management in Unity

---

## 🏁 SUCCESS CRITERIA

**Game is ready to ship when:**
1. All 118 glyphs unlock-able
2. All 21 NPCs respond appropriately
3. All 6 endings reachable
4. TONE system tracking correctly
5. Save/load working reliably
6. All assets displaying correctly
7. UI fully responsive
8. No gameplay-blocking bugs
9. Performance acceptable on target device
10. Cross-platform tested

---

## 📚 RELATED DOCUMENTS

- **UNITY_MIGRATION_ANALYSIS.md** — Comprehensive analysis
- **UNITY_MIGRATION_FILE_INVENTORY.md** — File-by-file breakdown
- **VELINOR_MASTER_DOC.md** — Game specification
- **VELINOR_INTEGRATION_CONTRACT.md** — System interfaces

---

**Last Updated:** 2026-06-12  
**Status:** Pre-migration planning complete  
**Next Step:** Begin Phase 1 (Data layer setup)

