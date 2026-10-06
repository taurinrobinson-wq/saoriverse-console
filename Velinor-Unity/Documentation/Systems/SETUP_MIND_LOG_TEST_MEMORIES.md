# Mind Log Test Setup Guide - Saori Meeting Encounter

## Overview
This guide walks you through setting up test memory fragments for the Mind Log UI, specifically for testing the Saori desert encounter diary entry.

## What's Been Created

### 1. MemoryFragmentTestSetup.cs
- Location: `Assets/Scripts/Testing/MemoryFragmentTestSetup.cs`
- Purpose: Generates test memory fragments at runtime
- Creates the following test memories:
  - **Desert Encounter** (Saori meeting) - Primary test memory
  - **Ravi's Story** - Secondary test memory
  - **Nima's Wisdom** - Tertiary test memory

### 2. Modified CodexViewController.cs
- Added test setup configuration
- Automatically initializes test memories on first load when the Mind Log Primary view is accessed

## Setup Instructions

### Step 1: Add MemoryFragmentTestSetup to Your Scene
1. In your scene, find the Codex Canvas or create an empty GameObject
2. Add the `MemoryFragmentTestSetup` script component to this GameObject
3. In the Inspector, drag the `MemoryGridUI` GameObject into the "Memory Grid UI" field
4. Save the scene

### Step 2: Wire Up CodexViewController
1. Select the GameObject with the `CodexViewController` script
2. In the Inspector, expand the **Testing** section:
   - Drag the GameObject with `MemoryFragmentTestSetup` into the "Test Setup" field
   - Toggle "Use Test Memories" to **True** (enabled by default)
   - Save the scene

### Step 3: Test the Functionality
1. Play the scene
2. Click the "Mind Log" or "Impressions" button to switch to the Mind Log Primary view
3. You should see three grid cells with blue square placeholder icons

### Testing Single-Click Functionality
1. **Single-click** on the first grid cell (Desert Encounter)
2. Observe: The synopsis text field should display **"A mysterious meeting"**
3. The cell should highlight in gold/yellow to show it's selected

### Testing Double-Click Functionality
1. **Double-click** on the Desert Encounter cell (first cell in grid)
2. Observe:
   - The Mind Log Secondary view should open (expanded memory display)
   - The expanded view should show:
     - Title: "Desert Encounter"
     - Full text describing the Saori meeting
     - A light blue square icon (placeholder)
   - A Back button should be visible

### Testing Back Button
1. Click the Back button to return to the Mind Log Primary view
2. Observe: The grid view should become active again with the previous selection maintained

## Memory Fragment Details

### Desert Encounter (Saori Meeting)
- **Fragment ID**: `memory_saori_desert_encounter`
- **Display Name**: Desert Encounter
- **Short Synopsis**: "A mysterious meeting"
- **Expanded Text**: Full narrative describing the Saori encounter
- **Icon**: Light blue placeholder square (256x256)

## Future Enhancements

### Creating Persistent Memory Fragments
Currently, test memories are generated at runtime. To create persistent memory fragments:

1. Create a ScriptableObject asset:
   - Right-click in Project → Create → Codex → Memory Fragment
   - Fill in the fields (fragmentID, displayName, shortSynopsis, expandedText)
   - Add your custom sprite/icon
   - Save to `Assets/Resources/MemoryFragments/`

2. Modify `MemoryFragmentTestSetup` to load these persistent assets instead of creating them at runtime

### Adding More Test Memories
To add additional test memories:

1. Open `MemoryFragmentTestSetup.cs`
2. Add more `CreateMemoryFragment()` calls in the `InitializeTestMemories()` method
3. Add the created fragment to `testFragments.Add()`

Example:
```csharp
MemoryFragment testMemory4 = CreateMemoryFragment(
    fragmentID: "memory_custom_encounter",
    displayName: "Custom Encounter",
    shortSynopsis: "A test summary",
    expandedText: "Full narrative text..."
);
testFragments.Add(testMemory4);
```

### Creating Custom Icons
The current system creates placeholder blue squares. To use custom icons:

1. Create or import your sprite (recommended 256x256 PNG)
2. Modify the `CreatePlaceholderIcon()` method or replace it with:
   ```csharp
   fragment.icon = Resources.Load<Sprite>("Path/To/Your/Icon");
   ```

## Troubleshooting

### Test Memories Don't Appear
- Check that "Use Test Memories" is enabled in CodexViewController Inspector
- Verify MemoryFragmentTestSetup reference is assigned
- Check the Console for error messages (search for "[MemoryFragmentTestSetup]")

### Click Handlers Not Working
- Ensure MemoryGridUI reference is properly assigned in MemoryFragmentTestSetup
- Verify each grid cell button is properly configured (check Scene Hierarchy)
- Confirm all cell buttons have the MemoryGridCellRelay component (added automatically)

### Synopsis Text Not Updating
- Check that the `synopsisText` field in MemoryGridUI Inspector is assigned to a TextMeshProUGUI component
- Verify the text field is visible and not hidden behind other UI elements
- Check Console for "[MemoryGridUI]" log messages to see if single-clicks are being registered

### Expanded View Not Opening
- Verify the `expandedView` field in MemoryGridUI Inspector is assigned to the MemoryExpandedUI GameObject
- Check that the MemoryExpandedUI has all required fields assigned (icon, title text, expanded text, etc.)
- Confirm the mindLogSecondaryContainer is properly set up in CodexViewController

## Testing Checklist

- [ ] Test memories appear in the grid with blue icons
- [ ] Single-click displays "A mysterious meeting" in synopsis
- [ ] Selected cell highlights in gold/yellow
- [ ] Double-click opens the expanded view
- [ ] Expanded view shows correct title and full text
- [ ] Back button returns to grid view
- [ ] Multiple selections work (can select multiple cells)
- [ ] View switching between Glyphs and Mind Log works smoothly
