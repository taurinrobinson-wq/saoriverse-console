# GameState System - Quick Start (15 minutes)

## Files Already Created ✓

These files are ready to use:
- `Assets/Scripts/GameState/GameState.cs` ← Core singleton
- `Assets/Scripts/GameState/NPCState.cs` ← Attach to each NPC
- `Assets/Scripts/GameState/SceneStateApplier.cs` ← Attach to each scene

## Setup Checklist (Do This Now)

### 1. Create GameState GameObject (2 min)

Choose **any scene that always loads** (e.g., your first scene, bootstrap, main menu):

1. In that scene, create empty GameObject: **Create → Empty → name it "GameState"**
2. Drag and drop the GameState script onto it: **Add Component → GameState**
3. Make sure it's at scene root (not nested under anything)
4. Save scene

**Verify:** Play game, Console shows: `[GameState] Initialized as persistent singleton`

---

### 2. Add NPCState to All NPCs (5 min)

Find and update each NPC:

- [ ] **Ravi** (InsideMarket_00)
  1. Select GameObject "Ravi"
  2. Add Component → NPCState
  3. Set npcID: `Ravi`
  4. Save scene

- [ ] **Nima** (InsideMarket_00)
  1. Select GameObject "Nima"
  2. Add Component → NPCState
  3. Set npcID: `Nima`
  4. Save scene

- [ ] **Kaelen** (InsideMarket_00)
  1. Select GameObject "Kaelen"
  2. Add Component → NPCState
  3. Set npcID: `Kaelen`
  4. Save scene

- [ ] **Willy** (any scene)
  1. Select GameObject "Willy"
  2. Add Component → NPCState
  3. Set npcID: `Willy`
  4. Save scene

*(Add more as needed for future NPCs)*

---

### 3. Add SceneStateApplier to All Scenes with NPCs (5 min)

For each scene that has NPCs:

- [ ] **InsideMarket_00**
  1. Open scene
  2. Select **SceneManager** (or create empty GameObject at root)
  3. Add Component → SceneStateApplier
  4. Save scene

- [ ] **InsideMarket_01** (if it has NPCs)
  1. Open scene
  2. Select **SceneManager** (or create empty GameObject at root)
  3. Add Component → SceneStateApplier
  4. Save scene

- [ ] **InsideMarket_02** (if it has NPCs)
  1. Open scene
  2. Select **SceneManager** (or create empty GameObject at root)
  3. Add Component → SceneStateApplier
  4. Save scene

*(Repeat for all other scenes with NPCs)*

**Verify:** Play game, enter a scene with NPCs, Console shows:
```
[SceneStateApplier] Found X NPCs in scene, applying state...
[SceneStateApplier] Applied state to Ravi
[SceneStateApplier] Applied state to Nima
[SceneStateApplier] State application complete
```

---

## Test It (3 min)

1. Play game
2. Enter a scene with NPCs
3. Open Console
4. Paste and press Enter:
   ```
   GameState.Instance.SetNPCVisibility("Ravi", false)
   ```
5. Watch: Ravi should disappear immediately
6. Transition to another scene
7. Return to original scene
8. **Ravi should still be gone** ✓

---

## Next: Update DialogueManager (Optional Now)

**Later**, when you want NPCs to persist after dialogue:

In DialogueManager.cs, find the `disable_npc` trigger handler (~line 300-330):

**Change this:**
```csharp
if (trigger.type == "disable_npc")
{
    string npcName = trigger.key ?? (trigger.data?[0] ?? null);
    if (!string.IsNullOrEmpty(npcName))
    {
        GameObject npcObj = GameObject.Find(npcName);
        if (npcObj != null)
        {
            npcObj.SetActive(false);
        }
    }
}
```

**To this:**
```csharp
if (trigger.type == "disable_npc")
{
    string npcName = trigger.key ?? (trigger.data?[0] ?? null);
    if (!string.IsNullOrEmpty(npcName))
    {
        // Set state in GameState (persists across scenes)
        GameState.Instance.SetNPCVisibility(npcName, false);
        
        // Also disable immediately for visual feedback
        GameObject npcObj = GameObject.Find(npcName);
        if (npcObj != null)
        {
            npcObj.SetActive(false);
            Debug.Log($"[DialogueManager] NPC marked hidden: {npcName}");
        }
    }
}
```

---

## How to Use in Your Code

Anywhere you want to change NPC visibility:

```csharp
// Hide an NPC
GameState.Instance.SetNPCVisibility("Ravi", false);

// Show an NPC
GameState.Instance.SetNPCVisibility("Kaelen", true);

// Set dialogue completion flag
GameState.Instance.SetDialogueFlag("ravi_nima_dialogue_complete", true);

// Check dialogue flag
if (GameState.Instance.GetDialogueFlag("ravi_nima_dialogue_complete"))
{
    // Do something
}

// Set glyph collected flag
GameState.Instance.SetGlyphFlag("glyph_sorrow", true);

// Debug: see all state
GameState.Instance.DebugPrintState();
```

---

## Common Issues

### "GameState.Instance is null"
- **Cause:** GameState GameObject not created yet
- **Fix:** Create it in your first/bootstrap scene

### NPCs still disappear on scene reload
- **Cause:** NPCState component missing or npcID wrong
- **Fix:** Add NPCState to NPC, set npcID to exact name

### Changes don't persist across scenes
- **Cause:** GameState not DontDestroyOnLoad
- **Fix:** Verify it prints `[GameState] Initialized as persistent singleton`

### "Found 0 NPCs in scene"
- **Cause:** No NPCState components in scene
- **Fix:** Add NPCState to all NPCs in that scene

---

## That's It!

You now have persistent world state that survives across all scene transitions. Next steps:

1. ✅ Setup (15 min)
2. ⭕ Test cross-scene persistence (3 min)
3. ⭕ Update DialogueManager when ready (5 min)
4. ⭕ Use GameState from other systems (colliders, quests, etc.)

Any questions, use this command:
```
GameState.Instance.DebugPrintState()
```

It tells you exactly what state is currently stored.

