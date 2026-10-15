# Velinor System Architecture Overview

## High-Level Flow: Player Progression & State

```
┌─────────────────────────────────────────────────────────────┐
│ Player Gameplay                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Enter Scene (e.g., InsideMarket_00)                    │
│     ↓                                                       │
│  2. SceneManager runs at scene start                       │
│     ├─ SceneTransitionManager: Fade in              │
│     ├─ SceneSpawnManager: Spawn NPCs               │
│     └─ SceneStateController: Apply state           │
│          └─ Check GameFlags                         │
│             └─ Disable/enable objects per flags    │
│     ↓                                                       │
│  3. Scene is ready, NPCs visible (or disabled per flags) │
│     ↓                                                       │
│  4. Player interacts with NPC                             │
│     ├─ DialogueManager loads dialogue JSON               │
│     ├─ Plays dialogue beats                              │
│     ├─ Shows player choices (tone system)                │
│     ├─ Updates tone effects on player stats              │
│     └─ At dialogue end, runs system triggers:            │
│        ├─ disable_npc: Hides NPC GameObjects             │
│        ├─ set_flag: Stores state in GameFlags            │
│        ├─ diary_append: Adds to player diary             │
│        ├─ mind_log_unlock: Adds to Codex                 │
│        └─ codex_pulse: Visual feedback                   │
│     ↓                                                       │
│  5. Leave scene                                            │
│     ├─ State persists: Codex state, NPC disabled, flags  │
│     └─ Scene unloads                                      │
│     ↓                                                       │
│  6. Load new scene                                         │
│     ├─ SceneManager runs Start()                         │
│     ├─ SceneStateController checks GameFlags             │
│     ├─ Applies saved state to new scene                  │
│     └─ Scene loads with correct NPC visibility, etc.    │
│     ↓                                                       │
│  7. Return to original scene                              │
│     └─ SceneStateController reapplies state              │
│        └─ NPCs still disabled (persisted state)          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Interaction Map

### 1. **GameFlags System** (Global State)
```
┌─ GameFlags (static Dictionary) ─────────────────────┐
│                                                      │
│ Persists ACROSS scenes during play session         │
│ Cleared on New Game / Game Over                    │
│                                                      │
│ Examples:                                           │
│ - met_saori = true                                 │
│ - obtain_codex = true                              │
│ - ravi_nima_market_discovery_complete = true       │
│ - codex_unlocked = true                            │
│                                                      │
│ Not saved to disk (would need PlayerPrefs)        │
└──────────────────────────────────────────────────────┘
        ↑                           ↑
        │                           │
   SET by:                      READ by:
   - DialogueManager           - SceneStateController
   - Dialogue triggers         - Character logic
   - Story events              - Condition checks
```

### 2. **DialogueManager** (Conversation Logic)
```
┌─ DialogueManager ─────────────────────────────────┐
│                                                    │
│ Loads dialogue JSON files                        │
│ Plays beats sequentially                         │
│ Shows player choices (tone system)               │
│                                                    │
│ On dialogue beat completion:                     │
│ ├─ ProcessBeatSystemTriggers()                   │
│ │  ├─ disable_npc → finds NPC, calls SetActive  │
│ │  ├─ set_flag → GameFlags.Set(key, value)      │
│ │  ├─ diary_append → DiaryManager.AddEntry()    │
│ │  └─ mind_log_unlock → MindLogManager          │
│ │                                                │
│ └─ Dialogue ends                                 │
│    └─ All triggers executed                      │
│       └─ Game state updated                      │
│                                                    │
└────────────────────────────────────────────────────┘
           ↓              ↓              ↓
        GameFlags    NPC Objects    MindLogManager
        (flags)      (disabled)     (memories)
```

### 3. **SceneStateController** (Scene Consistency)
```
┌─ SceneStateController (Per-Scene) ────────────────────┐
│                                                        │
│ Runs at scene START()                                │
│ Reads all GameFlags                                  │
│ For each StateAction:                                │
│   IF (GameFlags.Get(requiredFlag))                  │
│      THEN GameObject.SetActive(setActive)           │
│                                                        │
│ Example InsideMarket_00 StateActions:               │
│ ├─ Flag: ravi_nima_market_discovery_complete       │
│ │  └─ Action: Disable "Ravi" GameObject             │
│ └─ Flag: ravi_nima_market_discovery_complete       │
│    └─ Action: Disable "Nima" GameObject             │
│                                                        │
│ Result:                                              │
│ → When player returns to scene, NPCs stay disabled │
│ → No dialogue happens again                         │
│ → Scene state matches dialogue outcome             │
│                                                        │
└────────────────────────────────────────────────────────┘
        ↑                    ↑
        │                    │
   READ GameFlags       MODIFY GameObject
   (checks flags)       visibility
```

### 4. **Codex System** (Device Persistence)
```
┌─ CodexController ────────────────────────────────────┐
│                                                       │
│ playerHasCodex flag (local, per scene)              │
│ isCodexUnlocked flag (static, persists)             │
│                                                       │
│ On scene load:                                       │
│ └─ Start() checks GameFlags.Get("codex_unlocked")   │
│    └─ If true, restores playerHasCodex = true       │
│                                                       │
│ When receiving Codex:                                │
│ └─ UnlockCodex()                                     │
│    ├─ Sets playerHasCodex = true (local)            │
│    └─ Sets GameFlags("codex_unlocked", true)        │
│       └─ Persists across scenes                      │
│                                                       │
└───────────────────────────────────────────────────────┘
        ↓
   Press C to access Codex
   (if playerHasCodex == true)
```

---

## Scene Load/Unload Cycle

### New Game Start
```
① TitleScene
   └─ Click "Start Game"
      ↓
② Desert_Saori_Meeting
   └─ SceneManager.Start()
      ├─ SceneTransitionManager: fade in
      ├─ SceneSpawnManager: spawn Saori
      └─ SceneStateController: no flags set yet
         └─ Saori visible (no state to disable)
      ↓
   Dialogue with Saori
   └─ Codex received
      ├─ GameFlags.Set("obtain_codex", true)
      └─ GameFlags.Set("codex_unlocked", true)
      ↓
③ DesertToMarketTrek_00 (transition scene)
   └─ SceneManager.Start()
      ├─ SceneTransitionManager: transition effect
      ├─ SceneSpawnManager: spawn for trek
      └─ SceneStateController: no disables (no flags apply)
      ↓
④ InsideMarket_00 (Ravi & Nima meeting)
   └─ SceneManager.Start()
      ├─ SceneTransitionManager: fade in
      ├─ SceneSpawnManager: spawn Ravi + Nima
      └─ SceneStateController: checks ravi_nima_market_discovery_complete
         └─ NOT set yet → Ravi & Nima visible
      ↓
   Dialogue with Ravi & Nima
   └─ Dialogue ends
      ├─ GameFlags.Set("ravi_nima_market_discovery_complete", true)
      ├─ disable_npc Ravi
      └─ disable_npc Nima
      ↓
⑤ Leave scene to another area
   └─ GameFlags persists:
      ├─ codex_unlocked = true
      └─ ravi_nima_market_discovery_complete = true
      ↓
⑥ Return to InsideMarket_00
   └─ SceneManager.Start()
      ├─ SceneTransitionManager: fade in
      ├─ SceneSpawnManager: spawn Ravi + Nima
      └─ SceneStateController: checks ravi_nima_market_discovery_complete = true
         ├─ Flag IS set
         └─ Disables Ravi & Nima ✓
      ↓
   Ravi & Nima are gone (just like player left them)
   Dialogue cannot start again
```

---

## Data Flow Example: "Ravi & Nima Dialogue"

```
Beat 7 (Final beat): Player choices → "End dialogue and investigate codex signal"
│
└─ system_triggers fires:
   │
   ├─ diary_append
   │  └─ DiaryManager.AddEntry()
   │     └─ Diary shows "market_discovery_daughter_hint" ✓
   │
   ├─ close_dialogue
   │  └─ DialogueUIController.TriggerSystemEvent("close_dialogue")
   │     └─ Dialogue UI hides ✓
   │
   ├─ disable_npc (key: "Ravi")
   │  └─ GameObject.Find("Ravi").SetActive(false)
   │     └─ Ravi immediately disappears ✓
   │
   ├─ disable_npc (key: "Nima")
   │  └─ GameObject.Find("Nima").SetActive(false)
   │     └─ Nima immediately disappears ✓
   │
   ├─ set_flag (key: "ravi_nima_market_discovery_complete", value: "true")
   │  └─ GameFlags.Set("ravi_nima_market_discovery_complete", true)
   │     └─ Stored in static Dictionary ✓
   │
   ├─ codex_pulse (strength: 0.8)
   │  └─ Codex device glows/pulses ✓
   │
   └─ activate_proximity_tracker
      └─ Enables proximity detection for next area ✓

Result: Scene state snapshot saved in GameFlags
│
└─ Player leaves scene
   └─ GameFlags persists (not cleared)
      │
      └─ Player returns to InsideMarket_00
         └─ SceneStateController.Start() runs
            └─ Checks: ravi_nima_market_discovery_complete == true
               └─ Applies: Disable Ravi & Nima (again)
                  └─ Scene state matches saved state ✓
```

---

## Best Practices Established

1. ✅ **Centralized State**: GameFlags (one source of truth)
2. ✅ **Per-Scene State Application**: SceneStateController
3. ✅ **Persistent Codex**: Cross-scene device availability
4. ✅ **Dialogue Integration**: System triggers handle state changes
5. ✅ **Scene Consistency**: Revisiting scenes shows correct state

---

## Next Steps for Expansion

### New NPC Encounters
For each new NPC encounter, follow this pattern:

1. **Create dialogue JSON** with `disable_npc` and `set_flag` triggers
2. **Add to NPC's dialogue** the trigger to disable them:
   ```json
   "system_triggers": [
     { "type": "disable_npc", "key": "NPCName" },
     { "type": "set_flag", "key": "npc_encounter_complete", "value": "true" }
   ]
   ```
3. **Add StateAction to SceneStateController** in that scene:
   - Required Flag: `npc_encounter_complete`
   - Target: NPC GameObject
   - Set Active: FALSE
4. **Done!** NPC stays disabled on return visits ✓

### Persistent World Changes
Same pattern for ANY scene state:
- Destroy props → `set_flag`, StateAction to disable
- Unlock doors → `set_flag`, StateAction to enable door
- Reveal areas → `set_flag`, StateAction to enable map regions
- Progress mechanics → All track via GameFlags + StateActions

---

## Summary

Your architecture is **clean and scalable**:

| Component | Responsibility |
|-----------|-----------------|
| **GameFlags** | Remember what happened |
| **DialogueManager** | Make things happen |
| **SceneStateController** | Keep scenes consistent |
| **SceneManager** | Coordinate all above |

This creates a **persistent, branching world** where:
- ✅ NPCs remember if you talked to them
- ✅ Objects stay in their changed state
- ✅ Revisiting scenes shows your impact
- ✅ World feels alive and reactive
