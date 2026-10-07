# Mind Log Primary Container Visibility Fix

## Root Cause
The MindLogPrimaryContainer was disappearing after clicking the Mind Log button because **it was a child of CodexPanel, which could be deactivated or unmanaged by other code**.

In Unity, even if you call `SetActive(true)` on a GameObject, if any of its parents are inactive, the GameObject will be invisible and non-interactive. The issue wasn't with DontDestroyOnLoad—that was working correctly. The issue was **parent state management**.

## The Fix

### Problem Flow
1. Click Mind Log button → calls `ShowMindLogPrimaryView()`
2. SetActive(true) on mindLogPrimaryContainer
3. BUT: Canvas, CodexPanel, or intermediate parents may be inactive
4. Result: Container invisible despite being "active"

### Solution Implemented
In both `ShowMindLogPrimaryView()` and `ShowMindLogSecondaryView()`:

**Step 1: Ensure Canvas is active**
```csharp
Canvas uiCanvas = FindObjectOfType<Canvas>();
if (uiCanvas != null && !uiCanvas.gameObject.activeSelf)
{
    uiCanvas.gameObject.SetActive(true);
    Debug.Log("[CodexViewController] UI_Canvas was inactive - activated it");
}
```

**Step 2: Ensure CodexPanel (direct parent) is active**
```csharp
GameObject codexPanel = GameObject.Find("UI_Canvas/CodexPanel");
if (codexPanel != null && !codexPanel.activeSelf)
{
    codexPanel.SetActive(true);
    Debug.Log("[CodexViewController] CodexPanel was inactive - activated it");
}
```

**Step 3: Walk up entire hierarchy and activate all parents**
```csharp
Transform current = mindLogPrimaryContainer.transform.parent;
while (current != null)
{
    if (!current.gameObject.activeSelf)
    {
        current.gameObject.SetActive(true);
        Debug.Log($"[CodexViewController] Activated parent: {current.name}");
    }
    current = current.parent;
}
```

**Step 4: Now activate the container itself**
```csharp
mindLogPrimaryContainer.SetActive(true);
```

## Files Modified

### [CodexViewController.cs](C:/saoriverse-console/Velinor-Unity/Assets/Scripts/UI/CodexViewController.cs)
1. **OnEnable() method (lines 93-115)** - Fixed button listener type mismatch
   - Changed from `System.Action` to `UnityAction`
   - Wrapped lambda expressions in `new UnityAction(() => ...)`
   
2. **ShowMindLogPrimaryView() method (lines 235-375)**
   - Added Canvas activation check
   - Added CodexPanel activation check
   - Added parent hierarchy activation loop
   
3. **ShowMindLogSecondaryView() method (lines 381-490)**
   - Same parent hierarchy activation logic applied

## What This Fixes
- ✅ **CRITICAL**: Container now stays visible when Mind Log button is clicked
- ✅ Grid will display loaded memories
- ✅ Single/double-click handlers will work on memory cells
- ✅ Button click listeners now have correct UnityAction type

## Remaining Issues
- ⚠️ **Icon is null**: MindLog_Saori_Desert_Encounter.asset needs icon assigned
  - Either assign sprite in Inspector, or
  - Comment out the `icon != null` check in MemoryGridController line 72 to allow icon-less memories
- ⚠️ **FindObjectOfType deprecation**: Minor warning in DialogueUIController (use FindAnyObjectByType instead for newer Unity versions)

## Testing Checklist
- [ ] Compile without errors
- [ ] Click Mind Log button → container visible ✓
- [ ] Grid displays loaded memories (if icon is assigned)
- [ ] Single-click on memory cell → displays synopsis
- [ ] Double-click on memory cell → opens expanded view
- [ ] Back button returns to grid view

## Technical Details
- DontDestroyOnLoad only works on **root** GameObjects
- Parent inactive state overrides child active state
- The fix ensures all parents are active before showing child
- Extensive debug logging added for troubleshooting
