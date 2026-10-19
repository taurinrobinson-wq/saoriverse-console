# GameState System - Complete Implementation Guide

## Overview

This guide shows you how to implement a **persistent world state system** that survives across all scene transitions. It replaces the per-scene `SceneStateController` with a **global GameState singleton** that tracks all NPC visibility, dialogue completion, and quest state throughout your entire game world.

### Key Benefits

✅ **Cross-scene state** - Set NPC visibility in one scene, it persists in another  
✅ **Multiple triggers** - Same NPC can be hidden by dialogue + collider + quest completion  
✅ **Scalable** - Easy to add new NPCs, flags, and state without modifying core logic  
✅ **Clean separation** - State lives in GameState, behavior lives in NPCState components  
✅ **No magic despawns** - NPCs fade naturally during dialogue, stay gone on return visits  

---

## Architecture Overview

```
GameState (Singleton - DontDestroyOnLoad)
├─ Dictionary<string, bool> npcVisibility
├─ Dictionary<string, bool> dialogueFlags
├─ Dictionary<string, bool> glyphFlags
└─ Dictionary<string, string> questStates

↓

Each Scene:
├─ SceneStateApplier (runs on Start, applies all NPC states)
└─ NPC GameObjects
   ├─ NPCState component (syncs with GameState)
   └─ ...more NPCs...

↓

Dialogue/Events:
├─ DialogueManager calls GameState.SetNPCVisibility()
├─ Colliders call GameState.SetNPCVisibility()
└─ Quests call GameState.SetDialogueFlag() or SetQuestState()
```

---

## Step 1: Create GameState Singleton

Create a new GameObject in one of your always-loaded scenes (like a Bootstrap or StartMenu scene):

**Inspector Setup:**
1. Create empty GameObject named "GameState"
2. Add Component → GameState (script)
3. This will automatically DontDestroyOnLoad itself
4. Only one instance will ever exist (singleton pattern)

**Verification:**
- Scene loads
- Console shows: `[GameState] Initialized as persistent singleton`
- Play mode continues
- Load another scene
- GameState persists ✓

---

## Step 2: Add NPCState to Every NPC

For **every NPC GameObject** in your scenes:

**Inspector Setup:**
1. Select the NPC GameObject (e.g., "Ravi", "Nima", "Kaelen")
2. Add Component → NPCState (script)
3. Set **npcID** field to exact name (e.g., "Ravi", "Nima")
4. Optionally enable **debugMode** for detailed logs
5. Save scene

**Example NPC Setup:**
```
Ravi (GameObject)
├─ Transform
├─ NPCDialogueDriver
└─ NPCState
   └─ npcID: "Ravi"
   └─ debugMode: false
```

**Important:** The npcID must match the NPC's GameObject name exactly (case-sensitive).

### Do this for:
- Ravi
- Nima
- Kaelen
- Willy
- Any future NPCs

---

## Step 3: Add SceneStateApplier to Every Scene

For **every scene** with NPCs:

**Inspector Setup:**
1. Select your scene's **SceneManager** GameObject (or create one if needed)
2. Add Component → SceneStateApplier (script)
3. Optionally enable **debugMode** for detailed logs
4. Save scene

**Example Scene Setup:**
```
SceneManager (GameObject)
├─ SceneTransitionManager
├─ SceneSpawnManager
└─ SceneStateApplier
   └─ debugMode: false
```

When the scene loads, `SceneStateApplier.Start()` runs and:
1. Finds all NPCState components in the scene
2. Calls their ApplyState() method
3. Each NPC syncs with GameState

---

## Step 4: Update DialogueManager

Modify the **disable_npc** trigger handler in DialogueManager.cs:

**Before (immediate disable):**
```csharp
if (trigger.type == "disable_npc")
{
    string npcName = trigger.key ?? (trigger.data?[0] ?? null);
    if (!string.IsNullOrEmpty(npcName))
    {
        GameObject npcObj = GameObject.Find(npcName);
        if (npcObj != null)
        {
            npcObj.SetActive(false);  // ← Direct disable
            Debug.Log($"[DialogueManager] NPC disabled: {npcName}");
        }
    }
}
```

**After (GameState integration):**
```csharp
if (trigger.type == "disable_npc")
{
    string npcName = trigger.key ?? (trigger.data?[0] ?? null);
    if (!string.IsNullOrEmpty(npcName))
    {
        // Set state in GameState (persists across scenes)
        GameState.Instance.SetNPCVisibility(npcName, false);
        
        // Optionally: disable immediately for visual feedback during dialogue
        GameObject npcObj = GameObject.Find(npcName);
        if (npcObj != null)
        {
            npcObj.SetActive(false);
            Debug.Log($"[DialogueManager] NPC marked hidden: {npcName}");
        }
    }
}
```

**Alternatively (fade out smoothly):**
If you have a fade component, you could fade the NPC instead of immediate SetActive(false).

---

## Step 5: Verify Each Piece Works

### Test 1: GameState Persists Across Scenes

1. Play game
2. Enter a scene with NPCs (e.g., InsideMarket_00)
3. Open Console
4. Type in Console (paste and press Enter):
   ```
   GameState.Instance.DebugPrintState()
   ```
5. You should see:
   ```
   === GAME STATE DEBUG ===
   --- NPC Visibility ---
     Ravi: True
     Nima: True
     Kaelen: True
     ...
   ```
6. Transition to another scene
7. Run DebugPrintState() again
8. State should be identical ✓

### Test 2: NPCState Component Syncs

1. Play game, enter scene with NPCs
2. Console should show:
   ```
   [NPCState] Ravi: Applied state -> VISIBLE
   [NPCState] Nima: Applied state -> VISIBLE
   ```
3. Open Console and run:
   ```
   GameState.Instance.SetNPCVisibility("Ravi", false)
   ```
4. Watch the scene:
   - Ravi should immediately disappear
5. Console should show:
   ```
   [GameState] NPC visibility changed: Ravi -> HIDDEN
   [NPCState] Ravi: Applied state -> HIDDEN
   ```

### Test 3: SceneStateApplier Reapplies on Scene Load

1. Hide an NPC: `GameState.Instance.SetNPCVisibility("Ravi", false)`
2. Transition to another scene and back
3. On return, Console should show:
   ```
   [SceneStateApplier] Found 2 NPCs in scene, applying state...
   [SceneStateApplier] Applied state to Ravi
   [SceneStateApplier] Applied state to Nima
   [SceneStateApplier] State application complete
   ```
4. Ravi should still be hidden ✓

### Test 4: Full Dialogue → Hide Flow

1. Start game, enter dialogue with Ravi/Nima
2. Complete dialogue (trigger disable_npc)
3. Console should show:
   ```
   [GameState] NPC visibility changed: Ravi -> HIDDEN
   [GameState] NPC visibility changed: Nima -> HIDDEN
   ```
4. NPCs disappear in scene
5. Transition to another scene
6. Return to InsideMarket_00
7. Ravi/Nima should still be gone ✓

---

## How It Works: The Flow

### First Visit to InsideMarket_00

```
Scene loads
  ├─ SceneStateApplier.Start() runs
  ├─ Finds all NPCState components
  ├─ For each NPC:
  │  ├─ Calls NPCState.ApplyState()
  │  ├─ Checks GameState.GetNPCVisibility("Ravi")
  │  ├─ Gets: true (default)
  │  └─ NPC stays visible ✓
  └─ Scene fully loaded with all NPCs visible

Player starts dialogue
  └─ Dialogue completes (triggers disable_npc)
      └─ DialogueManager calls:
          └─ GameState.Instance.SetNPCVisibility("Ravi", false)
              └─ Sets state: npcVisibility["Ravi"] = false
                  └─ Ravi immediately disappears ✓
```

### Return Visit to InsideMarket_00

```
Player transitions away, then comes back

Scene loads
  ├─ SceneStateApplier.Start() runs
  ├─ Finds all NPCState components
  ├─ For each NPC:
  │  ├─ Calls NPCState.ApplyState()
  │  ├─ Checks GameState.GetNPCVisibility("Ravi")
  │  ├─ Gets: false (was set during dialogue)
  │  └─ NPC is SetActive(false) ✓
  └─ Scene loaded with Ravi hidden ✓
```

---

## Multiple Triggers Example

Let's say you want Kaelen to appear only after:
1. Player obtains Sorrow Glyph (in InsideMarket_02)
2. Player completes Ravi/Nima dialogue (in InsideMarket_00)

### Trigger 1: Obtain Glyph (in InsideMarket_02)

```csharp
// Some trigger system (collider, quest, etc.) calls:
GameState.Instance.SetGlyphFlag("glyph_sorrow", true);
GameState.Instance.SetNPCVisibility("Kaelen", true);  // Make Kaelen visible
```

### Trigger 2: Complete Dialogue (in InsideMarket_00)

```csharp
// In dialogue system, after Ravi/Nima dialogue ends:
GameState.Instance.SetDialogueFlag("ravi_nima_market_discovery_complete", true);

// Some logic checks if conditions are met:
if (GameState.Instance.GetGlyphFlag("glyph_sorrow") && 
    GameState.Instance.GetDialogueFlag("ravi_nima_market_discovery_complete"))
{
    GameState.Instance.SetNPCVisibility("Kaelen", true);
}
```

### Result:
- Kaelen appears in InsideMarket_00 only after **both** triggers fire
- State persists across all scenes
- No scene-specific configuration needed ✓

---

## Migration: Keep Old System or Replace?

### Option A: Keep SceneStateController (Safe, Gradual)

If you want to keep your existing system working:
1. Leave SceneStateController as-is
2. Add GameState + NPCState alongside it
3. NPCState will override any scene state (last one wins)
4. Gradually migrate scenes one at a time

### Option B: Replace SceneStateController (Clean, Faster)

1. Remove all SceneStateController components from scenes
2. Replace with SceneStateApplier
3. Make sure every NPC has NPCState component
4. Delete SceneStateController.cs when done

**Recommendation:** Use Option B. It's cleaner and the new system is simpler.

---

## Checklist: Ensuring Everything Works

Before considering this complete:

- [ ] GameState.cs created in Assets/Scripts/GameState/
- [ ] NPCState.cs created in Assets/Scripts/GameState/
- [ ] SceneStateApplier.cs created in Assets/Scripts/GameState/
- [ ] GameState GameObject exists in a scene that always loads
- [ ] Every NPC has NPCState component with correct npcID
- [ ] Every scene with NPCs has SceneStateApplier component
- [ ] DialogueManager updated to call GameState.SetNPCVisibility()
- [ ] Test 1 passed: GameState persists across scenes
- [ ] Test 2 passed: NPCState syncs with GameState
- [ ] Test 3 passed: SceneStateApplier reapplies on scene load
- [ ] Test 4 passed: Full dialogue → hide → persistence works
- [ ] SceneStateController removed (or marked deprecated)

---

## Debugging

### Console commands (paste and press Enter):

```csharp
// Print all current state
GameState.Instance.DebugPrintState()

// Hide an NPC
GameState.Instance.SetNPCVisibility("Ravi", false)

// Show an NPC
GameState.Instance.SetNPCVisibility("Ravi", true)

// Set a dialogue flag
GameState.Instance.SetDialogueFlag("ravi_nima_market_discovery_complete", true)

// Get a dialogue flag
GameState.Instance.GetDialogueFlag("ravi_nima_market_discovery_complete")

// Reset all state to defaults
GameState.Instance.ResetAllState()
```

### Common Issues

**Issue:** NPCs reappear after scene transition
- **Cause:** NPCState component missing or npcID wrong
- **Fix:** Add NPCState to NPC, set npcID to exact GameObject name

**Issue:** State changes don't persist
- **Cause:** GameState not DontDestroyOnLoad
- **Fix:** Ensure GameState.Awake() runs before any scene change

**Issue:** SceneStateApplier logs say "Found 0 NPCs"
- **Cause:** No NPCState components in scene
- **Fix:** Add NPCState component to all NPCs

**Issue:** Ravi stays visible after dialogue
- **Cause:** disable_npc trigger not calling GameState.SetNPCVisibility()
- **Fix:** Update DialogueManager's disable_npc handler

---

## Next Steps

Once this system is working:

1. **Create a separate Nima variant:** If Nima needs to appear alone in future scenes, create a separate GameObject (e.g., "Nima_Alone") with its own NPCState
2. **Add quest state tracking:** Use GameState.SetQuestState() for quest progression
3. **Implement save/load:** Add JSON serialization to save/load GameState
4. **Optimize for large worlds:** Cache NPC references if you have 50+ NPCs

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│         GameState (DontDestroyOnLoad)           │
│  ┌─────────────────────────────────────────┐    │
│  │ npcVisibility = {                       │    │
│  │   "Ravi": false,                        │    │
│  │   "Nima": false,                        │    │
│  │   "Kaelen": true,                       │    │
│  │   ...                                   │    │
│  │ }                                       │    │
│  │ dialogueFlags = {...}                   │    │
│  │ glyphFlags = {...}                      │    │
│  │ questStates = {...}                     │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
             ↑              ↑              ↑
        reads/writes   reads/writes   reads/writes
             |              |              |
   ┌─────────┴──────┐  ┌────┴──────┐  ┌───┴────────┐
   │ SceneStateApplier│ DialogueManager│ OtherSystems│
   │ (Apply on load) │ (Set on event) │ (Set state) │
   └─────────────────┘  └────────────┘  └────────────┘
             |
             v
   ┌─────────────────┐
   │ NPCState (Ravi) │ → checks GameState → SetActive()
   │ NPCState (Nima) │ → checks GameState → SetActive()
   │ NPCState (Kaelen)│ → checks GameState → SetActive()
   └─────────────────┘
```

