# Glyph System - Simple Setup Guide

**Good news:** The hard parts are already done! You just need to do two quick things in the Unity editor.

---

## ✅ Status: What's Already Done

- ✅ **Glyph data objects created:** 
  - `Assets/Resources/Glyphs/GlyphOfSorrow.asset`
  - `Assets/Resources/Glyphs/GlyphOfRemembrance.asset`
  - `Assets/Resources/Glyphs/GlyphOfLegacy.asset`

- ✅ **All scripts working:**
  - GlyphData.cs
  - GlyphUI.cs
  - GlyphSlot.cs
  - TriglyphSlot.cs
  - GlyphTestingController.cs
  - CodexController.cs

---

## 🎯 What You Need To Do (5 minutes total)

### Step 1: Create Testing Panel in Scene (3 minutes)

This is a manual process in the Unity editor - it's simpler and cleaner than prefabs.

1. Open **MachinesCave_00** scene
2. Find the **UI_Canvas** in hierarchy (or create a Canvas if needed)
3. Right-click on Canvas → **UI → Panel**
4. Name it **`GlyphTestingPanel`**
5. Set its position/size:
   - Anchor Preset: **Bottom-Left**
   - Pos X: 0, Y: 0
   - Width: 200, Height: 300
   - Background color: Dark semi-transparent (e.g., black alpha 200)

### Step 2: Add Three Toggles (2 minutes)

For each glyph (Sorrow, Remembrance, Legacy):

1. Right-click **GlyphTestingPanel** → **UI → Toggle**
2. Rename to `SorrowToggle` (or Remembrance/Legacy)
3. Position them:
   - First: Y = 250
   - Second: Y = 200  
   - Third: Y = 150

### Step 3: Add Labels to Each Toggle (1 minute)

For each toggle:

1. Right-click the toggle → **UI → Text - TextMeshPro**
2. Set text to glyph name ("Sorrow", "Remembrance", "Legacy")
3. Adjust text color to white
4. Resize to fit nicely

### Step 4: Add Script & Wire References (1 minute)

1. Select **GlyphTestingPanel** (root)
2. **Add Component** → Search for `GlyphTestingController`
3. In Inspector, drag these into the fields:
   - **Sorrow Toggle**: Drag `SorrowToggle` component
   - **Remembrance Toggle**: Drag `RemembranceToggle` component
   - **Legacy Toggle**: Drag `LegacyToggle` component
   - **Sorrow Data**: Drag `Assets/Resources/Glyphs/GlyphOfSorrow.asset`
   - **Remembrance Data**: Drag `Assets/Resources/Glyphs/GlyphOfRemembrance.asset`
   - **Legacy Data**: Drag `Assets/Resources/Glyphs/GlyphOfLegacy.asset`
   - **Codex Controller**: Drag from hierarchy (find CodexController, or leave blank - it auto-finds at runtime)

### Step 5: Test! (Play the scene)

1. Press Play
2. Toggle the switches ON/OFF
3. Watch glyphs appear/disappear in the Codex panel
4. Select a glyph - see name display at top

✅ **That's it!**

---

## 📋 Expected Behavior

- Toggle **ON** → Glyph appears in Codex, takes first available slot
- Toggle **OFF** → Glyph disappears
- **Click glyph** → Name displays at top of Codex
- **Multiple glyphs** → Automatically fill slots across 2 pages (9 slots each)

---

## 🐛 Troubleshooting

**Nothing appears when I toggle?**
- Check Codex panel is visible (press E to toggle if using that mechanism)
- Verify CodexController reference is assigned
- Check Console for errors

**Script references show as missing?**
- Make sure you're assigning the actual Toggle components (not the GameObjects)
- Make sure you're dragging the .asset files from Project folder

**Panel doesn't show?**
- Verify it's on a Canvas
- Check Canvas is enabled
- Try moving panel or resizing it

---

## 💾 Saving This Setup

Once it's working and you're happy with it:

1. Select **GlyphTestingPanel** in hierarchy
2. Right-click → **Prefab** → **Create Original**
3. Choose folder: `Assets/Resources/Prefabs/`
4. This saves the prefab for future use

---

## ✨ Clean & Simple

No complex automation, no mysterious errors. Just straightforward Unity editor work that you can see and understand every step of the way.

**Questions?** Check the logic in each script - they're well-commented!
