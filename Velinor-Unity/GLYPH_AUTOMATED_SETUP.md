# Glyph System - Automated Setup Guide

## Quick Start (2 minutes!)

Instead of manually creating everything, just run the automated setup scripts from the Unity menu.

---

## Step 1: Create Glyph Data Objects (30 seconds)

1. In Unity Editor, go to menu: **Velinor → Setup → Create Glyph Data Objects**
2. Check Console for confirmation
3. Three files are now created:
   - `Assets/Resources/Glyphs/GlyphOfSorrow.asset`
   - `Assets/Resources/Glyphs/GlyphOfRemembrance.asset`
   - `Assets/Resources/Glyphs/GlyphOfLegacy.asset`

✅ **Done!** The glyphs are ready to use.

---

## Step 2: Create Testing Panel Prefab (30 seconds)

1. In Unity Editor, go to menu: **Velinor → Setup → Create Testing Panel Prefab**
2. Check Console for confirmation
3. A prefab is created:
   - `Assets/Resources/Prefabs/GlyphTestingPanel.prefab`
   - Already contains three toggles (Sorrow, Remembrance, Legacy)
   - Already wired with GlyphTestingController
   - Auto-wired to glyph data objects

✅ **Done!** The panel is ready to add to your scene.

---

## Step 3: Add Prefab to Scene (1 minute)

1. Open **MachinesCave_00** scene
2. In Project window, navigate to `Assets/Resources/Prefabs/`
3. Drag **GlyphTestingPanel.prefab** into the scene hierarchy
4. Done! The panel appears in bottom-left corner

---

## Step 4: Verify and Test (1 minute)

1. Select the GlyphTestingPanel in hierarchy
2. In Inspector, scroll to **GlyphTestingController** component
3. Check that these are auto-filled:
   - ✓ Sorrow Toggle
   - ✓ Remembrance Toggle
   - ✓ Legacy Toggle
   - ✓ Sorrow Data
   - ✓ Remembrance Data
   - ✓ Legacy Data

4. **If Codex Controller is empty:**
   - Drag **CodexController** from the scene hierarchy into that field
   - (It will auto-find it at runtime if left empty, but manual assignment is safer)

5. Play the scene and toggle switches to test!

---

## What You'll See

**Panel appears in bottom-left corner of screen with:**
- ✓ Title "Glyph Testing"
- ✓ Three toggles (Sorrow, Remembrance, Legacy)
- ✓ Semi-transparent dark background

**When you toggle ON/OFF:**
- Toggle ON → Glyph appears in Codex grid, takes first available slot
- Toggle OFF → Glyph disappears from Codex
- Glyph name displays when selected
- Multiple glyphs automatically paginate across two pages

---

## Troubleshooting

### "Create Glyph Data Objects" menu item not showing?
- Make sure you're in Unity (not VS Code)
- Project must be loaded
- Try: Assets menu → Reimport All

### Prefab not creating?
- Check Console for errors
- Make sure Assets/Resources folder exists
- Try creating folder manually: Right-click Assets → Create Folder → Resources

### Panel doesn't show toggles?
- Verify it's on a Canvas
- Check that Canvas is active
- Try moving panel around or resizing

### Toggles not working?
- Verify CodexController is assigned in Inspector
- Check Console for errors when clicking toggles
- Verify GlyphData objects are loaded (check Inspector references)

---

## Cleanup (If Needed)

Want to start over?

**Delete Glyph Data Objects:**
- Menu: **Velinor → Setup → Delete Glyph Data Objects**

**Delete Testing Panel Prefab:**
- Menu: **Velinor → Setup → Delete Testing Panel Prefab**

Then re-run creation steps.

---

## Next Steps

Once testing works:
1. **Commit to git** - The glyph data and panel are ready to ship
2. **Adjust appearance** - Modify panel colors, toggle sizes, etc. as needed
3. **Implement gameplay** - Wire this into your actual glyph discovery/collection system
4. **Keep or remove panel** - Can be a permanent debug tool or removed for production

---

**Editor Scripts Location:**
- `Assets/Editor/GlyphDataSetup.cs`
- `Assets/Editor/GlyphTestingPanelSetup.cs`

These can be modified or deleted if you want to change the setup process.
