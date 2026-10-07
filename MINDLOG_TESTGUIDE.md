# Mind Log System - Complete Test Guide ✅

## What Was Fixed

### 1. **Container Visibility Toggle** ✅
- **Problem**: MindLogPrimaryContainer stayed visible even when switching to Glyphs view
- **Solution**: MindLogPersistence now only protects containers when they're actively being viewed
  - When switching from Mind Log → Glyphs: Container is unprotected, then disabled
  - When switching from Glyphs → Mind Log: Container is protected, then enabled

### 2. **Codex Lock System** ✅
- **Problem**: Mind Log was accessible anytime by pressing C, bypassing the story gate
- **Solution**: Codex starts LOCKED and only unlocks when player obtains it from Saori
  - Game start: Codex LOCKED (Mind Log button inaccessible)
  - Complete Saori dialogue: Codex UNLOCKED (Mind Log button accessible)
  - Attempting access while locked: Shows warning, blocks access

---

## System Architecture

```
Game Start
   ↓
[CodexViewController.Start()] → MindLogPersistence.LockCodex()
   ↓
Player presses C (Codex button)
   ├→ If Codex LOCKED: Shows Glyphs view only, Mind Log blocked
   └→ If Codex UNLOCKED: Can switch between Glyphs and Mind Log
   ↓
Complete Saori Dialogue with mind_log_unlocks
   ↓
[DialogueManager.ProcessMindLogUnlocks()]
   ├→ Load MindLogAsset ("MindLogs/MindLog_Saori_Desert_Encounter")
   ├→ Add to MindLogManager
   └→ MindLogPersistence.UnlockCodex() ← CODEX NOW ACCESSIBLE
   ↓
Player can now access Mind Log from Codex
```

---

## Step-by-Step Test

### **Test 1: Codex is Locked at Start**

**Setup**: Start a new game without completing Saori dialogue

**Expected Results**:
```
Console Output:
[CodexViewController] Codex LOCKED at start - player must obtain it from Saori
```

**Player Test**:
1. Press C to open Codex
2. See Glyphs view (glyph grid)
3. Press Impressions/Mind Log button → Should NOT work, stays on Glyphs
4. Check console for: `[CodexViewController] BLOCKED: Cannot access Mind Log - Codex is LOCKED!`

✅ **PASS**: Mind Log is completely inaccessible
❌ **FAIL**: Mind Log button works or shows container

---

### **Test 2: Complete Saori Dialogue**

**Setup**: In Desert scene with Saori

**Expected Results**:
1. Start dialogue with Saori (click on NPC)
2. Progress through dialogue to end (all beats complete)
3. Dialogue closes, check console for:
   ```
   [DialogueManager] Attempting to load Mind Log asset: MindLogs/MindLog_Saori_Desert_Encounter
   [DialogueManager] Added Mind Log: memory_saori_desert_encounter
   [DialogueManager] CODEX UNLOCKED - Player can now access the Mind Log!
   [MindLogPersistence] Codex UNLOCKED
   ```

✅ **PASS**: All three unlock messages appear
❌ **FAIL**: Messages don't appear or contain errors

---

### **Test 3: Codex is Now Accessible**

**Setup**: Just completed Saori dialogue (Codex should be UNLOCKED)

**Expected Results**:
1. Press C to open Codex
2. See Glyphs view
3. Click Impressions button (or press corresponding key)
4. View switches to Mind Log Primary
5. Check console:
   ```
   [CodexViewController] Switching to view: mind_log_primary
   [MindLogPersistence] Primary container protection ENABLED
   ```

✅ **PASS**: Switched to Mind Log Primary view successfully
❌ **FAIL**: Still blocked, or container not visible

---

### **Test 4: Container Visibility Toggle**

**Setup**: Codex open, viewing Mind Log Primary (with memory visible in grid)

**Test A - Switch to Glyphs**:
1. Click Glyphs button
2. Should see Glyphs view (glyph grid)
3. Mind Log container should be GONE
4. Check console:
   ```
   [CodexViewController] Switching to view: glyphs
   [MindLogPersistence] Primary container protection DISABLED - can now be deactivated
   ```

✅ **PASS**: Container hidden, switched to Glyphs
❌ **FAIL**: Both views visible at same time, or container stays

**Test B - Switch back to Mind Log**:
1. Click Impressions/Mind Log button
2. Should see Mind Log Primary view again
3. Memory grid visible
4. Check console:
   ```
   [CodexViewController] Switching to view: mind_log_primary
   [MindLogPersistence] Primary container protection ENABLED
   ```

✅ **PASS**: Container visible again
❌ **FAIL**: Container doesn't appear or error logged

---

### **Test 5: Memory Displays in Grid**

**Setup**: Codex open, viewing Mind Log Primary

**Expected Grid State**:
- 3×3 grid visible
- Position [0,0] (top-left): Saori memory icon (illustration of older woman)
- Remaining 8 cells: Empty (grayed out)
- Memory icon should be clickable

**Test**:
1. Look at grid - should show 1 icon
2. Console should show:
   ```
   [MemoryGridController] Retrieved 1 logs from manager
   [MemoryGridController] ✓ Added to slot 0
   [MemoryGridUI] PopulateGrid received 1 fragments
   ```

✅ **PASS**: 1 icon visible in grid
❌ **FAIL**: Grid empty, or multiple icons showing

---

### **Test 6: Single-Click Display (Synopsis)**

**Setup**: Codex open, Mind Log Primary, grid visible with memory icon

**Action**: Click ONCE on the Saori memory icon

**Expected Results**:
1. Icon becomes highlighted (golden tint)
2. MindLogName field displays: `Mysterious Encounter`
3. No view switch (stays on primary)
4. Waits 0.25 seconds for potential double-click
5. Console shows:
   ```
   [MemoryGridUI] RegisterGridCellClick called with Saori memory
   [MemoryGridController] Synopsis updated: Mysterious Encounter
   ```

✅ **PASS**: Synopsis appears, highlight visible
❌ **FAIL**: No synopsis shown, wrong text, or switched views

---

### **Test 7: Double-Click Opens Secondary View**

**Setup**: Codex open, Mind Log Primary, grid visible

**Action**: Double-click on the Saori memory icon (2 clicks within 0.25s)

**Expected Results**:
1. View switches to Mind Log Secondary (expanded view)
2. Full memory text displays:
   ```
   I met an older woman on the way to the marketplace. 
   I didn't get her name, but she handed me this strange device 
   without much explanation.
   
   There was something knowing in her eyes—as if she recognized me, 
   or perhaps knew something about me that I didn't know myself.
   
   The device she gave me feels important, though I can't explain why.
   ```
3. Back button visible and clickable
4. Console shows:
   ```
   [MemoryGridUI] Double-click detected for Saori memory
   [CodexViewController] Switching to view: mind_log_secondary
   [MindLogPersistence] Secondary container protection ENABLED
   [MemoryExpandedUI] DisplayMemory called with Saori memory
   ```

✅ **PASS**: Expanded view shows, full text visible
❌ **FAIL**: Single-click triggered instead, view didn't switch, or text missing

---

### **Test 8: Back Button Returns to Primary**

**Setup**: In Mind Log Secondary (expanded view) with Saori memory

**Action**: Click Back button

**Expected Results**:
1. View switches back to Mind Log Primary
2. Grid visible again with Saori icon
3. Console shows:
   ```
   [CodexViewController] Switching to view: mind_log_primary
   [MindLogPersistence] Primary container protection ENABLED
   ```

✅ **PASS**: Returned to primary view
❌ **FAIL**: Back button doesn't work or wrong view shown

---

### **Test 9: Memory Persists Across Scenes**

**Setup**: Memory in grid, viewing Mind Log Primary

**Action**:
1. Close Codex (press C or click outside)
2. Travel to different scene (e.g., marketplace)
3. Return to same scene
4. Open Codex again (press C)
5. Navigate to Mind Log Primary

**Expected Results**:
- Saori memory still visible in grid
- No duplicate memories
- Console shows successful persistence

✅ **PASS**: Memory persists across scenes
❌ **FAIL**: Memory disappears, duplicates, or shows errors

---

## Console Log Reference

### Good Signs ✅
```
[CodexViewController] Codex LOCKED at start
[DialogueManager] CODEX UNLOCKED - Player can now access the Mind Log!
[CodexViewController] Switching to view: mind_log_primary
[MindLogPersistence] Primary container protection ENABLED
[MemoryGridUI] PopulateGrid received 1 fragments
[MemoryGridController] ✓ Added to slot 0
```

### Warning Signs ⚠️
```
[CodexViewController] BLOCKED: Cannot access Mind Log - Codex is LOCKED!
[MindLogPersistence] not found - container may become invisible!
[DialogueManager] Failed to load Mind Log asset
[MemoryGridUI] Unable to configure cell at index X - Button reference is missing
[MemoryGridController] SKIPPING log - Icon is NULL
```

### Concerning Messages 🔴
```
[CodexViewController] FATAL: MindLogPrimaryContainer not found in scene!
[MindLogManager] Failed to get or create
[DialogueManager] Added Mind Log: (but no unlock message follows)
```

---

## Debugging Checklist

### Container Not Visible When Clicking Mind Log Button
- [ ] Check Codex lock status: `MindLogPersistence.IsCodexUnlocked()` should be `true` after dialogue
- [ ] Check container was unprotected: Look for "Primary container protection DISABLED"
- [ ] Verify container exists in scene: Search for "MindLogPrimaryContainer" in hierarchy
- [ ] Check CanvasGroup is set to interactive: Should see "CanvasGroup configured" in logs

### Grid Empty (No Memory Icons)
- [ ] Check memory loaded to manager: `MindLogManager.GetAllLogs().Count` should be > 0
- [ ] Check PopulateFromManager was called: Look for "Retrieved X logs" message
- [ ] Verify memory has icon: MindLog_Saori_Desert_Encounter.asset should have icon assigned
- [ ] Check grid cells have buttons: "Unable to configure cell" warning means missing button

### Click Handlers Not Working
- [ ] Verify MemoryGridCellRelay attached to buttons: Check scene hierarchy
- [ ] Check RegisterGridCellClick being called: Look for log output on click
- [ ] Verify MemoryGridUI reference set: Check CodexViewController inspector

### Memory Disappears When Switching Views
- [ ] Check UnprotectPrimaryContainer being called: Look for "protection DISABLED" message
- [ ] Verify DisableMindLogPrimary is called: Check console for view switch messages
- [ ] Check DontDestroyOnLoad marked: Root parent should persist

---

## Performance Notes

- **MindLogPersistence.Update()**: Runs every frame, but only checks 2 containers (lightweight)
- **Grid population**: Only happens when switching to Mind Log view (cached after first load)
- **Memory objects**: Temporary ScriptableObject instances created on-demand, auto-cleaned by GC
- **No coroutines on update**: Only starts when needed (test/diagnostic logging)

---

## Next Steps if Issues Persist

1. **Check for compilation errors**: Open Console window, look for red errors
2. **Verify all files exist**: MindLogPersistence.cs, MindLogAsset, MindLogManager
3. **Check Inspector assignments**: CodexViewController should have all fields assigned
4. **Review dialogue JSON**: Verify mind_log_unlocks array is properly formatted
5. **Test MindLogManager in isolation**: Use PlayMode console to check `MindLogManager.GetOrCreate().GetAllLogs().Count`

---

## Related Files

- [MindLogPersistence.cs](C:\saoriverse-console\Velinor-Unity\Assets\Scripts\UI\MindLogPersistence.cs) - Codex lock + container protection
- [CodexViewController.cs](C:\saoriverse-console\Velinor-Unity\Assets\Scripts\UI\CodexViewController.cs) - View switching + lock checks
- [DialogueManager.cs](C:\saoriverse-console\Velinor-Unity\Assets\Scripts\Core\DialogueManager.cs) - Unlock trigger
- [MindLogManager.cs](C:\saoriverse-console\Velinor-Unity\Assets\Management\MindLogManager.cs) - Memory storage
- [MemoryGridController.cs](C:\saoriverse-console\Velinor-Unity\Assets\Scripts\Testing\MemoryGridController.cs) - Grid population
- [MindLog_Saori_Desert_Encounter.asset](C:\saoriverse-console\Velinor-Unity\Assets\Resources\MindLogs\MindLog_Saori_Desert_Encounter.asset) - Test memory with icon ✓

---

## Success Criteria Summary

| Feature | Status | Test |
|---------|--------|------|
| Codex locked at start | ✅ | Mind Log button blocked |
| Codex unlocks on dialogue | ✅ | Console shows unlock message |
| Glyphs/Mind Log toggle | ✅ | Views switch cleanly |
| Container visibility | ✅ | No overlap between views |
| Memory displays | ✅ | Icon appears in grid |
| Single-click synopsis | ⏳ | Shows text in field |
| Double-click expansion | ⏳ | Shows full text |
| Back button works | ⏳ | Returns to primary |
| Memory persistence | ⏳ | Survives scene changes |

All features should now work! Test and report any issues. 🎮
