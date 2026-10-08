# Mind Log Test Instructions

## What Was Changed

I've updated `CodexViewController.cs` to **automatically create test memory entries** when you open the Mind Log view. This allows you to test the single-click and double-click functionality without needing to manually set up data.

### Key Changes:
- Added `EnsureTestMemoriesExist()` method that creates 3 test memories if the manager is empty
- Test memories have distinct colored icons (blue, orange, purple squares)
- Called automatically when you open the Mind Log Primary view

## Testing Steps

### Setup
1. Open the Desert_Saori_Meeting scene in Unity
2. Press Play

### Test Single-Click Functionality
1. Press **C** to open the Codex
2. Click the **Mind Log** button (should see 3×3 grid with colored squares)
3. **Single-click** any colored square
4. **Expected**: The square should highlight (yellow tint) and a summary should appear below the grid

### Test Double-Click Functionality
1. From the same grid view, **double-click** any colored square
2. **Expected**: 
   - The view should switch to the expanded mind log display
   - You should see the full text of the memory
   - There should be a "Back" button to return to the grid

### Test View Switching
1. Click Back to return to the 3×3 grid
2. Single-click a different square
3. Double-click it to open expanded view
4. Click Back again
5. **Expected**: View switching should be smooth and stable

## What to Check

### ✓ Grid Display
- [ ] Can you see 3 colored squares in the 3×3 grid?
- [ ] Do the squares have different colors (blue, orange, purple)?

### ✓ Single-Click
- [ ] Does clicking a square highlight it (yellow)?
- [ ] Does a summary text appear (e.g., "Mysterious Encounter")?
- [ ] Does clicking a different square change the highlighted square?

### ✓ Double-Click
- [ ] Does double-clicking open the expanded view?
- [ ] Can you see the full memory text?
- [ ] Does the Back button work and return you to the grid?

### ✓ Container Stability
- [ ] Does the container disappear after clicking?
- [ ] Does the container stay visible when switching between views?
- [ ] Can you open and close the Mind Log multiple times?

## Troubleshooting

### Grid is Empty
- **Problem**: You see a 3×3 grid but no colored squares
- **Solution**: 
  1. Check the Console for errors
  2. Verify MindLogInitializer or SaoriMemorySetup hasn't disabled auto-creation
  3. Restart the scene

### Summary Doesn't Appear
- **Problem**: Single-click works (square highlights) but no text appears
- **Solution**:
  1. Check if synopsisText in MemoryGridController is assigned in the Inspector
  2. Verify the TextMeshProUGUI component is active in the scene

### Double-Click Opens Wrong View
- **Problem**: Double-click opens a different view or shows no data
- **Solution**:
  1. Check that MemoryExpandedUI is assigned to MemoryGridController in the Inspector
  2. Verify Mind Log Secondary Container exists in the hierarchy

### Container Disappears
- **Problem**: Everything works until you click a button, then the UI vanishes
- **Solution**: This is the known destruction blocker (see below)

## Known Issues

### Container Destruction (Prior Issue)
The prior investigation found that the entire UI_Canvas hierarchy is being destroyed moments after the view shows successfully. This is indicated by **DestructionTracker logs**:
```
[DESTRUCTION] MindLogPrimaryContainer was DESTROYED!
[DESTRUCTION] CodexPanel parent was DESTROYED!
[DESTRUCTION] UI_Canvas was DESTROYED!
```

**If this is happening:**
1. Note the time and frame number in the logs
2. Check what happens between "Mind Log Primary view enabled" and the destruction logs
3. Search for any `LoadScene`, `UnloadScene`, or scene transition code that might be triggering

### Manual Testing Can Work Around This
If the container disappears, you can still test the click handlers by:
1. Adding more debug logging to OnMemorySingleClicked()
2. Checking if the methods are called before the container is destroyed
3. Testing in OnEnable() before PopulateFromManager() returns

## Files to Check in Inspector

Make sure these are assigned in the CodexViewController or MemoryGridController in the Inspector:

### CodexViewController
- **glyphsButton**: Button that switches to glyphs view
- **impressionsButton**: Button that switches to mind log primary view
- **mindLogBackground**: Background image for mind log view
- **mindLogPrimaryContainer**: The 3×3 grid container
- **useTestMemories**: Should be TRUE to auto-create test data

### MemoryGridController (child of mindLogPrimaryContainer)
- **synopsisText**: TextMeshProUGUI for showing memory summary
- **expandedView**: Reference to MemoryExpandedUI for displaying full text

## Next Steps After Testing

1. **If single-click works**: Verify the synopsisText location is visible to the user
2. **If double-click works**: Verify the expanded view layout matches your design
3. **If container doesn't disappear**: The prior blocker might be fixed!
4. **If everything works**: Can start adding real memory entries when Saori encounter ends

## Need Help?

If you encounter issues:
1. Check the Console for error messages
2. Look for logs starting with `[CodexViewController]`, `[MemorySlot]`, or `[MemoryGridController]`
3. Check if the referenced GameObjects/Components are missing in the hierarchy
4. Share the relevant error logs for debugging
