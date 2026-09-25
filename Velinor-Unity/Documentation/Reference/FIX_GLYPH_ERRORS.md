# Fix Glyph System - 3 Simple Steps

Your glyph system is working, but needs 2 configuration assignments in the Inspector. Takes 2 minutes.

---

## The Problem

When you toggle glyphs, you're getting errors:
- `glyphUIPrefab is not assigned!`
- `Glyph Sorrow not found in active list!`

**Why:** CodexController needs to know:
1. What prefab to use when creating glyph UI elements
2. Which slots in the grid to fill

---

## Fix: 2 Inspector Assignments

### Step 1: Assign GlyphUI Prefab

1. In Hierarchy, select the **CodexController** (or find it via searching)
2. In Inspector, scroll to **CodexController** component
3. Find field: **Glyph UI Prefab**
4. Drag this file onto it: `Assets/Resources/Prefabs/GlyphUI.prefab`

✅ **Done!** CodexController can now create glyph UI elements.

---

### Step 2: Assign Glyph Slots

This tells CodexController which slots to fill when glyphs are added.

1. Keep CodexController selected in Inspector
2. Scroll down to find: **Slots Page 1** (list field)
3. Set **Size** to **9** (for a 3x3 grid)
4. Now you have 9 empty fields labeled Element 0-8

5. **In your GlyphGrid hierarchy**, find your slot GameObjects:
   - Slot_0, Slot_1, Slot_2, etc. (or however you named them)

6. **Drag and drop each slot** into the corresponding Element field:
   - Drag Slot_0 → Element 0
   - Drag Slot_1 → Element 1
   - Drag Slot_2 → Element 2
   - ... and so on for all 9 slots

7. (**Optional**) If you have a second page of slots, do the same for **Slots Page 2**

✅ **Done!** CodexController knows which slots to use.

---

## That's It!

Now test:
1. Play the scene
2. Toggle glyphs ON/OFF
3. They should appear in Slot_0, Slot_1, etc.
4. Click to select
5. Should show glyph name at top

---

## Quick Checklist

- [ ] GlyphUI Prefab assigned to CodexController
- [ ] All 9 slots from GlyphGrid added to Slots Page 1 (Elements 0-8)
- [ ] Toggles work without errors
- [ ] Glyphs appear in slots
- [ ] Glyph names display when selected

---

## If Still Not Working

**Check Console for specific error messages** - they'll tell you exactly what's missing.

Common issues:
- Slots assigned but not the **GlyphSlot** component (make sure you're dragging the slot GameObjects that have GlyphSlot script)
- GlyphUI Prefab still empty (make sure it's pointing to `Assets/Resources/Prefabs/GlyphUI.prefab`)
- Glyph data not loaded (the .asset files should be at `Assets/Resources/Glyphs/`)
