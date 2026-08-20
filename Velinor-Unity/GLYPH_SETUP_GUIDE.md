# Glyph System Scene Setup Guide

This guide covers the final two tasks to get the glyph system fully functional in your MachinesCave_00 scene.

## Task 1: Create GlyphData Objects

The core glyph definitions that your system will display and place.

### Step 1.1: Create Folder Structure
1. In Project window, navigate to `Assets/Resources/`
2. If `Glyphs` folder doesn't exist, right-click → Create Folder → Name it `Glyphs`

### Step 1.2: Create First Glyph Data Object
1. Inside `Assets/Resources/Glyphs/`, right-click → Create → Velinor → Glyph Data
2. Name it `GlyphOfSorrow.asset`
3. In Inspector, fill in:
   - **Glyph Name**: "Sorrow"
   - **Icon**: (Select a sprite - any gray/blue-toned icon works, or leave blank for now)
   - **Description**: "The glyph of loss and mourning"

### Step 1.3: Create Second Glyph Data Object
1. Right-click in Glyphs folder → Create → Velinor → Glyph Data
2. Name it `GlyphOfRemembrance.asset`
3. In Inspector, fill in:
   - **Glyph Name**: "Remembrance"
   - **Icon**: (Select a sprite - any warm-toned icon works)
   - **Description**: "The glyph of cherished memories"

### Step 1.4: Create Third Glyph Data Object
1. Right-click in Glyphs folder → Create → Velinor → Glyph Data
2. Name it `GlyphOfLegacy.asset`
3. In Inspector, fill in:
   - **Glyph Name**: "Legacy"
   - **Icon**: (Select a sprite - any gold/warm-toned icon works)
   - **Description**: "The glyph of lasting impact"

### Result
You should now have three `.asset` files in `Assets/Resources/Glyphs/`:
- GlyphOfSorrow.asset
- GlyphOfRemembrance.asset
- GlyphOfLegacy.asset

---

## Task 2: Create Testing UI Panel in Scene

This panel allows you to toggle glyphs on/off dynamically to test the system.

### Step 2.1: Create Testing Panel GameObject
1. Open **MachinesCave_00** scene
2. In Hierarchy, find or create a Canvas for testing (can use existing UI_Canvas)
3. Right-click on Canvas → UI → Panel
4. Rename it to `GlyphTestingPanel`
5. In Inspector:
   - Set Anchor Preset to **Bottom-Left**
   - Set Position: X=0, Y=0
   - Set Size: Width=200, Height=300
   - Set Background Color to semi-transparent dark (e.g., black with alpha 200)

### Step 2.2: Add Three Toggles
Repeat this 3 times (for Sorrow, Remembrance, Legacy):

1. Right-click on GlyphTestingPanel → UI → Toggle
2. Rename to `SorrowToggle` (or `RemembranceToggle`, `LegacyToggle`)
3. Position them vertically:
   - SorrowToggle: Y=250
   - RemembranceToggle: Y=200
   - LegacyToggle: Y=150

### Step 2.3: Add Labels
For each toggle, add a label so you know what each one controls:

1. Right-click on each Toggle → UI → Text - TextMeshPro
2. Set the text to the glyph name:
   - "Sorrow"
   - "Remembrance"
   - "Legacy"
3. Adjust text color to white/light for visibility

### Step 2.4: Add GlyphTestingController Script
1. Right-click on GlyphTestingPanel → Add Component
2. Search for and add the `GlyphTestingController` script

### Step 2.5: Wire Up References in Inspector
1. Select GlyphTestingPanel (which now has GlyphTestingController)
2. In Inspector, scroll to GlyphTestingController section
3. Set these fields:
   - **Sorrow Toggle**: Drag `SorrowToggle` component here
   - **Remembrance Toggle**: Drag `RemembranceToggle` component here
   - **Legacy Toggle**: Drag `LegacyToggle` component here
   - **Sorrow Data**: Drag `GlyphOfSorrow.asset` from Project window
   - **Remembrance Data**: Drag `GlyphOfRemembrance.asset` from Project window
   - **Legacy Data**: Drag `GlyphOfLegacy.asset` from Project window
   - **Codex Controller**: Drag the CodexController from hierarchy or use FindAnyObjectByType

### Step 2.6: Test It!
1. Play the scene
2. Toggle each switch on/off
3. Watch glyphs appear/disappear in the Codex panel
4. The Codex should automatically fill slots and display glyph names

### Expected Behavior
- When toggle ON: Glyph appears in Codex grid, starting from first available slot
- When toggle OFF: Glyph disappears from Codex grid
- Glyph name displays at top of Codex when selected
- Multiple glyphs show across two pages (9 slots per page)

---

## Troubleshooting

### Glyphs not appearing?
- Check that CodexController has glyphUIPrefab assigned
- Verify GlyphSlots are added to CodexController.slotsPage1/2 lists
- Check Console for errors

### Toggles not working?
- Verify GlyphTestingController has all toggle and data references assigned
- Check that toggle event listeners are properly connected (check Inspector → Toggle → On Value Changed)
- Look for Console errors when toggling

### Codex panel not visible?
- Ensure UI_Canvas and CodexPanel are active/enabled
- Press E near the triglyph panel to toggle Codex visibility
- Check Canvas sorting order if layering issue

---

## Next Steps After Testing

Once you verify the system works:
1. Commit these test objects to git
2. Can integrate GlyphTestingPanel as a permanent debug panel or remove it for production
3. Implement actual glyph discovery/collection logic in your game flow
4. Add glyph placement verification to the triglyph puzzle system

---

**Last Updated**: Session - Glyph System Implementation  
**Status**: Ready for editor setup
