# Mind Log System - Comprehensive Testing Instructions

## Overview
You've implemented a Mind Log memory system with a 3×3 grid that displays memory icons. We've identified that the logs show the container as "active" but you report it's not visually appearing. I've added extensive diagnostic logging to track down the exact issue.

## What Changed (Latest Commits)
1. **CodexViewController.cs**: Added logging AFTER CanvasGroup alpha is set to 1
   - Logs: `[CodexViewController] CanvasGroup VERIFIED AFTER SET: alpha=X, interactable=X, blocksRaycasts=X`

2. **MindLogPersistence.cs**: Enhanced Update() to monitor CanvasGroup alpha changes
   - NEW: If alpha gets reset to <0.5, logs a WARNING and re-enables it
   - Logs: `[MindLogPersistence] ALERT: MindLogPrimaryContainer CanvasGroup alpha=0 (should be 1)! Re-showing...`

3. **MemorySlot.cs**: Enhanced SetMemory() to log sprite assignment details
   - Logs: `[MemorySlot] ✓ Set sprite 'Saori_Gives_Codex_Desert' on MemorySlot(0)`
   - Logs: `[MemorySlot] ✗ CANNOT SET SPRITE: slotImage is null on MemorySlot(0)!`

## Test Execution (Step-by-Step)

### BEFORE YOU START
1. Open Unity Editor
2. Load the scene with the Codex and Dialogue
3. Open the Console window (Window → General → Console)
4. You'll see LOTS of debug logs - this is normal!
5. Filter to see only messages from: CodexViewController, MindLogPersistence, MemoryGridController, MemorySlot

### TEST #1: Basic Container Visibility
**Objective**: Verify the container appears when clicking Mind Log button

**Steps**:
1. Start game (Play mode)
2. Go through dialogue with Saori until you get the Codex
3. Open Codex by pressing C
4. Click the "Mind Log" button (should be the second button)

**Expected Results**:
- Container appears with 3×3 grid
- Saori memory icon visible in one of the grid slots
- No error logs about missing components

**Watch For in Logs**:
```
[CodexViewController] Switching to view: mind_log_primary
[CodexViewController] ShowMindLogPrimaryView - SUCCESS
[CodexViewController] CanvasGroup VERIFIED AFTER SET: alpha=1.0
[CodexViewController] Mind Log Primary view enabled
[MemoryGridController] Found 9 memory slots
[MemoryGridController] Populated grid with 1 memories from MindLogManager
```

**Troubleshooting if grid doesn't appear**:
- Look for any `[MindLogPersistence] ALERT` messages - this means alpha is being reset
- Look for `[MemorySlot] ✗ CANNOT SET SPRITE` messages - icon issue
- Look for errors about "MindLogPrimaryContainer not found"

---

### TEST #2: Icon Rendering
**Objective**: Verify memory icons are properly rendered

**Steps**:
1. Complete Test #1 until grid is visible
2. Look at the grid carefully

**Expected Results**:
- See a square icon with Saori's codex icon (should look like a book/device)
- Icon should be in one of the 9 slots
- 8 other slots should appear empty/greyed out

**Watch For in Logs**:
```
[MemoryGridController] Log 0: ID=memory_saori_desert_encounter, Icon=Saori_Gives_Codex_Desert (UnityEngine.Sprite), Summary=Mysterious Encounter
[MemoryGridController] ✓ Added to slot 0
[MemorySlot] ✓ Set sprite 'Saori_Gives_Codex_Desert' on MemorySlot(0)
```

**Troubleshooting if icons don't show but grid container is visible**:
- Look for `[MemoryGridController] ✗ SKIPPING log 'memory_saori_desert_encounter' - Icon is NULL`
  - This means the Saori asset is missing its icon
- Look for `[MemorySlot] ✗ CANNOT SET SPRITE: slotImage is null`
  - This means the Image component isn't assigned to the MemorySlot

---

### TEST #3: Single-Click Handler
**Objective**: Verify clicking a memory icon displays its name

**Steps**:
1. Complete Test #1-2 until grid is visible with icon
2. Single-click (one quick click) on the Saori memory icon
3. Look at the "MindLogName" text field at the top of the grid

**Expected Results**:
- MindLogName field shows: "memory_saori_desert_encounter" or a formatted name
- Icon gets highlighted (yellow-tinted)
- No errors in console

**Watch For in Logs**:
```
[MemorySlot] Single-clicked memory 'memory_saori_desert_encounter'
[MemorySlot] MemorySlot highlighted
[MemoryGridController] Single-clicked memory slot with fragment: memory_saori_desert_encounter
```

**Troubleshooting if click doesn't register**:
- Look for `OnMemorySingleClicked` in logs
- If no logs appear, the button might not be working
- Verify the MemoryGridController is in the scene

---

### TEST #4: Double-Click Handler
**Objective**: Verify double-clicking opens the expanded memory view

**Steps**:
1. Complete Test #1-2 until grid is visible
2. Double-click (two quick clicks within 0.3 seconds) on the Saori memory icon
3. Watch for the secondary view to open

**Expected Results**:
- Grid disappears (primary view hides)
- Secondary view appears showing full memory text
- Can read full memory: "I met an older woman on the way to the marketplace..."

**Watch For in Logs**:
```
[MemorySlot] Double-clicked memory 'memory_saori_desert_encounter'
[MemoryGridController] Double-clicked memory slot
[CodexViewController] Switching to view: mind_log_secondary
[CodexViewController] Mind Log Secondary view enabled
```

**Troubleshooting if double-click doesn't open secondary view**:
- Ensure you're clicking fast enough (< 0.3 seconds between clicks)
- Check logs for double-click detection: `Double-clicked memory`
- If secondary view is opening but appears black/empty, check secondary container visibility

---

### TEST #5: Back Button (Return from Secondary)
**Objective**: Verify returning to primary view from expanded view

**Steps**:
1. Complete Test #4 until secondary view is open
2. Look for a "Back" button and click it
3. Should return to the grid view

**Expected Results**:
- Secondary view disappears
- Primary view (grid) reappears with Saori memory still selected

**Watch For in Logs**:
```
[CodexViewController] Switching to view: mind_log_primary
[CodexViewController] Mind Log Primary view enabled
```

---

### TEST #6: Switch to Different View
**Objective**: Verify switching away from Mind Log doesn't break it

**Steps**:
1. Complete Test #1 until grid is visible
2. Click the "Glyphs" button to switch to glyphs view
3. Verify grid disappears
4. Click "Mind Log" button again
5. Verify grid reappears in the same state

**Expected Results**:
- Switching to Glyphs makes Mind Log invisible (but doesn't destroy it)
- Clicking Mind Log again shows the grid again
- Same memory is still displayed

**Watch For in Logs**:
```
[CodexViewController] Switching to view: glyphs
[CodexViewController] MindLogPrimaryContainer hidden via CanvasGroup (kept active)
[CodexViewController] Switching to view: mind_log_primary
[CodexViewController] MindLogPrimaryContainer set to active
```

---

## Log Collection for Debugging

If something isn't working, please collect the logs by:

1. **In Console, filter for the component**:
   - Type in the search box: "CodexViewController|MindLogPersistence|MemoryGridController|MemorySlot"

2. **Copy all logs from Test Execution**:
   - Ctrl+A to select all logs
   - Ctrl+C to copy
   - Paste into a text editor

3. **Include the full log output when reporting issues**:
   - Especially if you see any `[MindLogPersistence] ALERT` messages
   - These indicate alpha is being reset and need investigation

## Critical Log Keywords to Search For

| Keyword | Meaning | Status |
|---------|---------|--------|
| `✓` | Success - this worked as expected | GOOD |
| `✗` | Failure - something went wrong | BAD |
| `ALERT` | Container property changed unexpectedly | BAD |
| `Cannot find` | A reference is missing | BAD |
| `null` | Variable/component is not assigned | BAD |
| `ERROR` | Fatal issue, system won't work | BAD |
| `WARNING` | Non-critical issue, but be aware | CAUTION |

## Quick Diagnostics Checklist

After each test, verify:
- [ ] No ERROR logs in console
- [ ] No `Cannot SET SPRITE` messages
- [ ] No `alpha=0` ALERT messages after primary view shown
- [ ] Memory icon visible in at least one grid slot
- [ ] Click handlers working (see logs when clicking)
- [ ] View transitions smooth (no flickering or disappearing containers)

## Next Steps Based on Results

### If Tests 1-2 Pass but 3-4 Fail:
→ Click handlers aren't working
→ Check: MemorySlot.OnSlotClicked(), MemoryGridController methods

### If Tests 1-2 Fail (no visible grid):
→ Container disappears or is invisible
→ Check: CanvasGroup settings, parent visibility, Update() logs

### If Test 6 Fails (view switching breaks):
→ CanvasGroup alpha not being restored properly
→ Check: MindLogPersistence protection logic, ProtectPrimaryContainer() calls

### If all tests pass:
🎉 **The Mind Log system is working!**
→ Now you can add more memories and test the combination system

## Files Modified in This Fix
- `Assets/Scripts/UI/CodexViewController.cs` - Container visibility verification
- `Assets/Scripts/UI/MindLogPersistence.cs` - CanvasGroup alpha monitoring
- `Assets/Scripts/Core/MemorySlot.cs` - Sprite assignment logging
- `MINDLOG_CONTAINER_DEBUGGING_PLAN.md` - Architecture analysis
- `MINDLOG_TESTING_INSTRUCTIONS.md` - This file

## Questions to Answer After Testing
1. When you click Mind Log button, do you see the grid container?
2. If yes, do you see any memory icons in the grid?
3. If icons appear, can you single-click to see the memory name?
4. If single-click works, can you double-click to see the full memory?
5. Are there any ERROR or ALERT messages in the console?

**Please run through all tests and share the console output!** 🔍
