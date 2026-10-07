# Mind Log Container Disappearance - Diagnostic Plan

## Problem Statement
When user clicks the Mind Log button, the Codex switches to the primary mind_log view. Console logs show the container is `activeSelf: True` and `activeInHierarchy: True`, but the container appears invisible in the game (no grid visible).

## Root Cause Analysis

### What We Know Works
1. ✅ Mind Log button click is detected
2. ✅ `SwitchView("mind_log_primary")` is called
3. ✅ `ShowMindLogPrimaryView()` executes
4. ✅ Container is re-found if reference was null
5. ✅ Container is set to `SetActive(true)`
6. ✅ CanvasGroup is configured: alpha=1, interactable=true, blocksRaycasts=true
7. ✅ Final diagnostics show: activeSelf=True, activeInHierarchy=True
8. ✅ Memory grid is populated with 1 entry

### What Could Cause Invisibility Despite Active State
1. **CanvasGroup alpha being reset to 0 after initial setup**
   - Some other code path calling SetActive(false) on a parent
   - MindLogPersistence Update() not catching alpha changes (FIXED - now monitoring alpha)
   - Timing issue where CanvasGroup is hidden after logs complete

2. **Parent hierarchy becoming inactive**
   - UI_Canvas or CodexPanel parent deactivating
   - Already have checks to activate parents, but might need stronger validation

3. **Canvas rendering issue**
   - RectTransform positioning off-screen
   - Canvas layer/sorting issue
   - Scale set to 0

4. **Multiple competing implementations**
   - MemoryGridUI vs MemoryGridController both trying to manage grid
   - Could cause visual conflicts

## New Diagnostic Logging Added

### CodexViewController.cs
```csharp
// After CanvasGroup alpha=1 is set:
Debug.Log($"[CodexViewController] CanvasGroup VERIFIED AFTER SET: alpha={cgPrimary.alpha}, interactable={cgPrimary.interactable}, blocksRaycasts={cgPrimary.blocksRaycasts}");
```

### MindLogPersistence.cs
```csharp
// In Update(), now monitoring both SetActive and CanvasGroup alpha:
if (cgPrimary != null && cgPrimary.alpha < 0.5f)
{
    Debug.LogWarning($"[MindLogPersistence] ALERT: MindLogPrimaryContainer CanvasGroup alpha={cgPrimary.alpha} (should be 1)! Re-showing...");
    cgPrimary.alpha = 1f;  // Re-enable if it gets reset
}
```

## Test Sequence

### Test 1: Initial Load & Click Mind Log Button
1. Start game
2. Complete dialogue with Saori (this unlocks Codex and creates memory)
3. Press C to open Codex
4. Click Mind Log button
5. **Expected**: Grid with Saori memory icon appears
6. **Check logs for**:
   - `[CodexViewController] CanvasGroup VERIFIED AFTER SET: alpha=1.0`
   - `[CodexViewController] Mind Log Primary view enabled`
   - `[MindLogPersistence]` warnings about alpha changes (should NOT appear if working)

### Test 2: Monitor for Alpha Resets
1. Perform Test 1
2. Look for any `ALERT: MindLogPrimaryContainer CanvasGroup alpha=` warnings in logs
3. If warnings appear, note the timing and what action preceded them
4. **If logs show alpha being reset**: This identifies the culprit code

### Test 3: Parent Hierarchy Check
1. Perform Test 1
2. In Unity Inspector while playing, expand and check:
   - UI_Canvas: should be activeSelf=true
   - CodexPanel: should be activeSelf=true
   - MindLogPrimaryContainer: should be activeSelf=true
   - Check CanvasGroup component alpha value visually
3. **If any parent is false**: Parent hierarchy issue needs fixing

### Test 4: Switch Between Views
1. Perform Test 1 until grid is visible
2. Click Glyphs button
3. Verify Mind Log Primary becomes invisible (alpha=0)
4. Click Mind Log button again
5. **Expected**: Grid reappears
6. **Check logs for**: Proper enable/disable sequence

### Test 5: Click to Select Memory
1. Perform Test 1 until grid is visible
2. Single-click on the Saori memory icon
3. **Expected**: Memory name appears in MindLogName field (shows "Saori - Desert Encounter" or similar)
4. Double-click on the Saori memory icon
5. **Expected**: Secondary view opens showing full memory details

## Key Files to Watch
- `Assets/Scripts/UI/CodexViewController.cs` - Main view switcher (NEW: enhanced logging)
- `Assets/Scripts/UI/MindLogPersistence.cs` - Container protection (NEW: alpha monitoring)
- `Assets/Scripts/Testing/MemoryGridController.cs` - Grid population
- `Assets/Scripts/Core/MemorySlot.cs` - Click handlers

## Next Actions Based on Test Results

### If CanvasGroup alpha resets to 0 repeatedly:
- Identify which code path is calling SetActive(false) or directly setting alpha
- Add prevention logic or refactor the problematic code

### If parent becomes inactive:
- Strengthen the parent activation logic in ShowMindLogPrimaryView()
- Add persistent parent protection to MindLogPersistence

### If tests pass but visual still doesn't show:
- Check RectTransform position/scale
- Check Canvas settings (render mode, layers)
- Check if there's a UI overlay blocking input/rendering

### If click handlers don't work:
- Verify MemorySlot.OnSlotClicked() is being called
- Check DOUBLE_CLICK_THRESHOLD timing
- Verify MindLogName field reference exists

## Success Criteria
- ✅ Container appears visually when Mind Log button clicked
- ✅ Grid displays Saori memory icon
- ✅ Single-click displays memory name in MindLogName field
- ✅ Double-click opens secondary view with full memory text
- ✅ Back button returns to primary view
- ✅ No orphaned or invisible containers left behind
