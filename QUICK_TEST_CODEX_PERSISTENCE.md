# Quick Testing Guide - Codex Persistence Fix

## Quick Start
1. Open the Velinor-Unity project in Unity
2. Build the project (no C# errors expected)
3. Navigate to the Desert_Saori_Meeting scene and start a play session

## Test Workflow

### Step 1: Get the Codex Device
- Play through the Saori dialogue encounter in Desert_Saori_Meeting
- Watch for log message: `[Codex] ========== CODEX UNLOCKED ==========`
- Watch for: `[Codex] Persisted to GameFlags: codex_unlocked = true`

### Step 2: Verify Codex Opens in Current Scene
- Press **C** key
- **Expected**: Codex should open and show the Glyphs/Mind Log interface
- If it opens, Codex is working in the current scene ✓

### Step 3: Transition to Another Scene
- Close the Codex (press C again or click back)
- Navigate to the Ravi & Nima market scene (or any other scene)
- Wait for scene to fully load

### Step 4: Verify Codex Persists After Scene Change
- Once in the new scene, press **C** key
- **Expected**: Codex should open exactly like it did in the previous scene ✓
- **If working correctly**, you'll see console logs like:
  ```
  [MindLogPersistence] LoadPersistedState: Restored isCodexUnlocked from GameFlags = true
  [Codex] Restored playerHasCodex=true from GameFlags (persisted from previous scene)
  [Codex] C key pressed! playerHasCodex=true, requiresCodexDevice=true
  ```

### Step 5: Verify Multiple Transitions
- Close Codex
- Transition to yet another scene
- Press C in the new scene
- **Expected**: Codex should still be accessible ✓

## Console Output Indicators

### ✅ Success Indicators (Look for these in Console)
```
[Codex] ========== CODEX UNLOCKED ==========
[Codex] Persisted to GameFlags: codex_unlocked = true
[Codex] Player can now press C to open Codex
[MindLogPersistence] LoadPersistedState: Restored isCodexUnlocked from GameFlags = true
[Codex] Restored playerHasCodex=true from GameFlags (persisted from previous scene)
```

### ❌ Failure Indicators (If you see these, something is wrong)
```
[Codex] C key pressed! playerHasCodex=false  ← playerHasCodex not restored!
[MindLogPersistence] Codex LOCKED            ← State not persisted
playerHasCodex=false requiresCodexDevice=true ← Codex access blocked
```

## What Each Change Does

### CodexController.Start() Change
- When a new scene loads with CodexController, it checks if "codex_unlocked" is stored in GameFlags
- If true, it automatically sets `playerHasCodex = true` so C key works
- **Why**: Without this, each new scene would have `playerHasCodex = false` by default

### CodexController.UnlockCodex() Change
- When Codex is unlocked, it now saves this state to GameFlags
- **Why**: So the state survives scene transitions

### MindLogPersistence Changes
- On scene load, `LoadPersistedState()` reads GameFlags and restores the Codex unlock state
- Also reconfigures the CodexPanel to allow interaction
- **Why**: Ensures both the internal flags AND the UI are properly configured

## Troubleshooting

### Codex Still Won't Open in New Scene
1. Check Console for error messages
2. Verify you received Codex in previous scene (look for "CODEX UNLOCKED" message)
3. Check that `GameFlags.Get("codex_unlocked")` returns true in the new scene
4. Ensure `requiresCodexDevice = true` in CodexController inspector

### Console Shows "playerHasCodex=false" Even After Unlock
1. Check if `GameFlags.Get("codex_unlocked", false)` is returning false
2. Verify GameFlags wasn't cleared between scenes
3. Check GlobalStateManager is properly initialized as DontDestroyOnLoad

### Codex Works in First Scene But Not After Transition
1. This is the main bug being fixed
2. Verify all code changes were applied (especially CodexController.Start())
3. Check Unity build has the latest compiled DLLs

## Test Scenarios

| Scenario | Expected Behavior | Status |
|----------|------------------|--------|
| Get Codex in Desert_Saori, Press C | Codex opens | ✓ |
| Close Codex, Press C again | Codex opens/closes toggle works | ✓ |
| Get Codex, transition scene, Press C | Codex opens in new scene | ✓ |
| Get Codex, transition multiple times, Press C | Codex still works | ✓ |
| New game, press C before getting Codex | Codex does NOT open | ✓ |

## Notes
- The fix uses the existing `GameFlags` system which already handles cross-scene persistence
- The Codex state is stored with key `"codex_unlocked"` (bool)
- This is NOT saved to disk (game save files) - only persists during current play session
- On New Game, GameFlags is cleared, so Codex access resets
