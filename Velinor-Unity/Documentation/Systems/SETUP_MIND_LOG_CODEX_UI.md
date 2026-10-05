# Mind Log / Codex UI Setup Guide

## Overview
The Mind Log system is now fully implemented with three distinct views:
1. **Glyphs View** — Existing glyph grid (unchanged)
2. **Mind Log Primary** — New 3x3 memory fragment grid
3. **Mind Log Secondary** — Expanded memory view with full text

This guide walks you through wiring up the UI components in the Unity Inspector.

---

## Prerequisites
The following scripts have been created and should already be in your project:
- `CodexViewController.cs` (modified) — Main view controller
- `MemoryGridUI.cs` — Manages 3x3 grid and selections
- `MemoryExpandedUI.cs` — Displays expanded memory overlays
- `MemoryCombineSystem.cs` — Handles fragment combinations
- `MemoryFragment.cs` — Data structure for memory storage
- `ValidMemoryCombinations.cs` — Container for valid combinations

---

## Scene Setup Instructions

### Step 1: Locate the Codex Canvas
In your Unity scene, find the Canvas containing the Codex UI (typically named `CodexCanvas` or similar).

### Step 2: Find/Create Mind Log Primary Container
The Mind Log Primary view needs a container for the 3x3 grid.

#### Option A: Create a New Container (Recommended)
1. In the Scene Hierarchy, right-click under the Codex Canvas
2. Create a new empty GameObject named `MindLogPrimaryContainer`
3. Add a `RectTransform` component (should be automatic)
4. Position it to fill the codex area (same as glyph grid)
5. Add a `CanvasGroup` component
6. Set **Alpha** to 1.0, **Interactable** to true, **Blocks Raycasts** to true

#### Option B: Use Existing Glyph Grid
If you prefer to reuse the existing glyph grid GameObject:
- Right-click → Rename to `MindLogPrimaryContainer`
- Keep all positioning and layout as-is

### Step 3: Create the Memory Grid UI
Under `MindLogPrimaryContainer`:

1. Create a new Panel: `UI → Panel`
   - Rename to `MemoryGridPanel`
   - Set **Layout Group** to `GridLayoutGroup`
   - Spacing: (5, 5)
   - Cell Size: (100, 100) — adjust based on your design
   - Fit Preferred Size
   - Preferred Height: Expand

2. Create 9 grid cells as Button objects:
   - For each cell (0-8):
     - Name: `GridCell_0`, `GridCell_1`, etc.
     - Add a **Button** component
     - Add an **Image** component for the icon (set to white as default)
     - Add a **Image** component for selection highlight (set to yellow/gold, disabled by default)

   **Alternative:** Use a prefab if you have a GridCell template

3. Add the `MemoryGridUI` script to `MemoryGridPanel`:
   - Drag `MemoryGridPanel` into the Scene
   - Add Component → `MemoryGridUI`
   - In the inspector:
     - **Grid Cells**: Populate with your 9 grid cells (drag each button)
     - **Default Cell Tint**: White (1, 1, 1, 1)
     - **Selected Cell Tint**: Gold (1, 0.88, 0.45, 1)
     - **Double Click Threshold**: 0.25s
     - **Synopsis Text**: Drag a TextMeshPro label for the 2-3 word summary
     - **Expanded View**: Drag the `MemoryExpandedUI` instance (created in Step 5)
     - **Codex View Controller**: Drag the `CodexViewController` instance

### Step 4: Find/Create Mind Log Secondary Container
The Mind Log Secondary view displays the expanded memory with full text.

#### Create the Secondary Container:
1. Right-click under Codex Canvas → Create empty GameObject
2. Name it `MindLogSecondaryContainer`
3. Add a `RectTransform` component (should be automatic)
4. Add a `CanvasGroup` component
5. Set **Alpha** to 1.0, **Interactable** to true, **Blocks Raycasts** to true

### Step 5: Create the Expanded Memory UI
Under `MindLogSecondaryContainer`:

1. Create a Panel for the background (visual layout)
   - Name: `ExpandedMemoryPanel`
   - Make it fill the container

2. Inside the panel, create:
   - **Icon Display**: `UI → Image`
     - Name: `MemoryIcon`
     - Position: Upper left or center
     - Set a placeholder sprite
   
   - **Title Text**: `UI → TextMeshPro - Text`
     - Name: `TitleText`
     - Positioning: Below icon or upper area
     - Font Size: 36 or larger
   
   - **Expanded Text**: `UI → TextMeshPro - Text (Scrollable)`
     - Name: `ExpandedTextDisplay`
     - Add a `ScrollRect` component
     - Add a `VerticalLayoutGroup` for the text area
     - Font Size: 18-20
   
   - **Back Button**: `UI → Button`
     - Name: `BackButton`
     - Position: Upper left corner
     - Text: "Back"
     - Add appropriate styling (dark background, white text)

3. Add the `MemoryExpandedUI` script to the panel:
   - Add Component → `MemoryExpandedUI`
   - In the inspector:
     - **Panel Canvas Group**: Drag the CanvasGroup from this panel
     - **Memory Icon**: Drag the `MemoryIcon` image
     - **Title Text**: Drag the `TitleText` TextMeshPro object
     - **Expanded Text**: Drag the `ExpandedTextDisplay` TextMeshPro object
     - **Text Scroll Rect**: Drag the ScrollRect component
     - **Back Button**: Drag the `BackButton` button
     - **Fade Duration**: 0.2s (or your preference)
     - **Codex View Controller**: Drag the `CodexViewController` instance

### Step 6: Add Combination System
In the scene hierarchy:

1. Find or create an empty GameObject named `MemoryCombineSystem`
2. Add Component → `MemoryCombineSystem`
3. In the inspector:
   - **Valid Combinations Resource Path**: `Data/ValidMemoryCombinations` (default)
   - **Memory Grid UI**: Drag the `MemoryGridUI` instance
   - **Combination Animation Canvas Group**: Drag a CanvasGroup (or leave empty for no animation)
   - **Combination Animation Duration**: 0.35s
   - **Codex View Controller**: Drag the `CodexViewController` instance
   - **Success Notification Format**: `"New deduction discovered: {0}"` (default)

### Step 7: Wire Up CodexViewController
In the scene hierarchy, find your `CodexViewController` script instance:

#### Main Buttons:
- **Glyphs Button**: Drag the existing Glyphs button
- **Impressions Button**: Drag the existing Mind Log button (this now switches to Mind Log Primary)

#### Backgrounds:
- **Glyphs Background**: Drag the existing Glyphs background (or create one)
- **Mind Log Background**: Drag the existing impressions/Mind Log background

#### Glyphs View Elements:
- **Glyph Grid Pg1**: Drag the glyph grid page 1 container
- **Glyph Grid Pg2**: Drag the glyph grid page 2 container
- **Glyphs Navigation**: Drag the pagination controls

#### Mind Log Primary Elements:
- **Mind Log Primary Container**: Drag the `MindLogPrimaryContainer` GameObject
- **Memory Grid UI**: Drag the `MemoryGridUI` component instance

#### Mind Log Secondary Elements:
- **Mind Log Secondary Container**: Drag the `MindLogSecondaryContainer` GameObject
- **Memory Expanded UI**: Drag the `MemoryExpandedUI` component instance
- **Mind Log Back Button**: Drag the Back button from the secondary container

#### Legacy Impressions (Optional):
- If you still have old impressions elements, you can reference them here (they'll be disabled)
- **Impressions Text Display**, **Prev Button**, **Next Button**: Optional

### Step 8: Configure Backgrounds
This step is critical for the visual switch between views.

1. **Glyphs Background**:
   - This should be the `Glyph_Codex3.png` graphic
   - Ensure it's an Image component with the correct sprite
   - It should be a direct child of the Codex Canvas

2. **Mind Log Background**:
   - Rename the existing background to match (or create a new one)
   - This should be the `Glyph_Codex_Mind_log.png` graphic
   - Set this sprite in the Image component

3. **Visibility**:
   - Glyphs Background: Should be active when showing Glyphs or Mind Log Primary
   - Mind Log Background: Should be active when showing Mind Log Secondary
   - The CodexViewController will automatically manage these

---

## Creating Memory Fragment Assets

### Step 1: Create a ScriptableObject for a Memory Fragment

1. In your project, create a new folder: `Assets/Resources/Data/MemoryFragments`
2. Right-click → Create → ScriptableObject → `MemoryFragment`
3. Name it something meaningful: `memory_01_introduction.asset`
4. In the Inspector, fill in:
   - **Fragment ID**: `memory_01_introduction` (must be unique)
   - **Display Name**: "Introduction to Velhara"
   - **Icon**: Drag a sprite for the memory grid
   - **Short Synopsis**: "First encounter" (2-3 words)
   - **Expanded Text**: Full narrative text for the memory
   - **Tags**: (optional, e.g., "intro", "location")
   - **Is Deduction**: `false` (only set true for combined memories)
   - **Combines With**: (leave empty for now; will be used by ValidMemoryCombinations)
   - **Linked Scene**: (optional, name of related scene)
   - **Unlock Condition**: (optional, condition to unlock this memory)

### Step 2: Create the ValidMemoryCombinations Asset

1. Right-click in your Data folder → Create → ScriptableObject → `ValidMemoryCombinations`
2. Name it `ValidMemoryCombinations.asset`
3. In the Inspector:
   - **Combinations**: Create a list of valid pairs
   - For each combination:
     - **First Fragment ID**: (e.g., `memory_01_introduction`)
     - **Second Fragment ID**: (e.g., `memory_02_discovery`)
     - **Result Fragment ID**: (e.g., `deduction_01_understanding`)
     - **Combination Logic**: Brief description of why these combine

### Step 3: Populate Your Memory Grid

When you're ready to show memories in the grid:

1. Populate `MemoryGridUI.PopulateGrid()` with a list of `MemoryFragment` objects
2. This can be done via:
   - A manager script that loads from Resources
   - Direct assignment in the Inspector
   - Code that unlocks memories dynamically

---

## Testing the Setup

### Test Checklist:

- [ ] Click "Glyphs" button → Glyphs view shows with grid and pagination
- [ ] Click "Mind Log" button → Mind Log Primary view shows with 3x3 memory grid
- [ ] Single-click a memory → Icon highlights, synopsis text updates
- [ ] Double-click a memory → Expanded view appears with full text
- [ ] Click "Back" button → Returns to Mind Log Primary grid
- [ ] Background changes appropriately when switching views
- [ ] All UI buttons are responsive and clickable
- [ ] No console errors or warnings

### Debugging:

If something isn't working:
1. **UI not showing?** → Check `CanvasGroup.active` and `CanvasGroup.blocksRaycasts`
2. **Button not responding?** → Ensure Button component is enabled
3. **Memory grid empty?** → Verify `PopulateGrid()` is called with valid fragments
4. **Background not changing?** → Check sprite references in Image components
5. **Double-click not working?** → Verify `doubleClickThreshold` is set correctly
6. **Messages not received?** → Check CodexViewController is referenced in each UI component

---

## Next Steps

Once the UI is wired up and tested:

1. **Add Memory Fragments**:
   - Create multiple MemoryFragment assets
   - Add images/icons for each
   - Write the narrative text for expanded view

2. **Implement Unlock Triggers**:
   - Dialogue completion can trigger memory unlocks
   - NPCs can reveal memories
   - Environmental discovery unlocks memories

3. **Test Combinations**:
   - Configure valid combinations in ValidMemoryCombinations
   - Test that combine button appears/disappears appropriately
   - Verify animations play when combining

4. **Add Notifications**:
   - Wire up NotificationPanelController
   - Test "New deduction discovered" messages

---

## Troubleshooting Reference

| Issue | Solution |
|-------|----------|
| Mind Log button doesn't switch views | Verify `mindLogPrimaryContainer` is assigned in CodexViewController |
| Back button doesn't work | Ensure `mindLogBackButton` is assigned and has BackRequested listener |
| Memory grid shows no cells | Verify 9 grid cells are populated in `MemoryGridUI.gridCells` list |
| Double-click doesn't expand | Check `doubleClickThreshold` value and verify `MemoryExpandedUI` reference |
| Combine button never shows | Verify `MemoryCombineSystem` is initialized and fragment IDs match |
| Wrong background showing | Check sprite assignments and background active state in respective views |

---

## Script Summary

| Script | Purpose | Where to Add |
|--------|---------|-------------|
| `CodexViewController.cs` | Main view switcher | Existing GameObject |
| `MemoryGridUI.cs` | 3x3 grid management | Memory Grid Panel |
| `MemoryExpandedUI.cs` | Expanded memory display | Expanded Memory Panel |
| `MemoryCombineSystem.cs` | Fragment combinations | Standalone in scene |
| `MemoryFragment.cs` | Memory data structure | ScriptableObject assets |
| `ValidMemoryCombinations.cs` | Combination definitions | ScriptableObject asset |

---

## References

- Design Doc: `Codex_MindLog_System.md`
- Implementation Guide: `Codex_MindLog_Implementation.md`
- Data Structures: `MemoryFragment.cs`, `ValidMemoryCombinations.cs`
- Controller Scripts: `MemoryGridUI.cs`, `MemoryExpandedUI.cs`, `MemoryCombineSystem.cs`
