# Glyph Grid Pagination Setup

Build a 2-page glyph system with 9 slots per page (18 total).

---

## Hierarchy Structure (Target)

```
GlyphGrid (existing parent)
├── Page1 (new group)
│   ├── Slot_0 through Slot_8 (9 slots in a 3x3 grid)
└── Page2 (new group)
    ├── Slot_9 through Slot_17 (9 slots in a 3x3 grid)
```

---

## Step 1: Create Page1 Group

1. In Hierarchy, find **GlyphGrid**
2. Right-click → **Create Empty**
3. Name it **`Page1`**
4. Make sure it's a child of GlyphGrid

---

## Step 2: Build 3x3 Grid in Page1

You need to create a 3x3 grid of slots. Here's the fastest way:

### Option A: Duplicate Your Existing Slots (if you already have 3)
1. Take one of your existing slot GameObjects (e.g., GlyphSlot_Sorrow)
2. Copy its RectTransform settings (width, height, anchor positions)
3. Create 9 new Image GameObjects under Page1 with those same settings
4. Arrange them in a 3x3 grid using anchors:
   - Row 1: Y = 0.65-0.80 (top)
   - Row 2: Y = 0.40-0.55 (middle)
   - Row 3: Y = 0.15-0.30 (bottom)
   - Col 1: X = 0.1-0.3 (left)
   - Col 2: X = 0.35-0.55 (center)
   - Col 3: X = 0.6-0.8 (right)

### Option B: Create from Scratch (Cleaner)
1. Right-click **Page1** → **UI → Image**
2. Name it **`Slot_0`**
3. Set size/anchors to ~15% of grid (approx 80x80 pixels)
4. Duplicate it 8 times (Ctrl+D)
5. Rename to Slot_1, Slot_2, ... Slot_8
6. Arrange them in the grid positions above

---

## Step 3: Add GlyphSlot Component to Each Slot

For each slot (Slot_0 through Slot_8):

1. Select the slot in hierarchy
2. **Add Component** → Search for `GlyphSlot`
3. Click to add

Now all 9 slots have the GlyphSlot script attached.

---

## Step 4: Create Page2 (Copy of Page1)

1. In Hierarchy, right-click **Page1**
2. **Duplicate** (or Copy → Paste as sibling)
3. Rename to **`Page2`**
4. The slots inside will auto-rename to Slot_9, Slot_10, etc. (or you can manually rename if needed)

Now you have 18 slots total (Page1 + Page2).

---

## Step 5: Assign to CodexController

1. Select **CodexController** in hierarchy
2. In Inspector, find **Slots Page 1**
3. Set **Size: 9**
4. Drag each slot from Page1 (Slot_0 through Slot_8) into Elements 0-8

5. Find **Slots Page 2**
6. Set **Size: 9**
7. Drag each slot from Page2 (Slot_9 through Slot_17) into Elements 0-8

---

## Step 6: Test Pagination

1. Play the scene
2. Toggle glyphs ON (you should now have multiple)
3. Press **Left Arrow** or **Right Arrow** to flip between pages
4. Page1 shows glyphs 1-9
5. Page2 shows glyphs 10-18

---

## ✅ What This Does

- **9 slots per page** = room for up to 18 glyphs
- **Arrow keys** = flip between pages
- **Auto-pagination** = as you collect more glyphs, they fill slots automatically
- **Clean hierarchy** = organized, easy to debug

---

## Quick Checklist

- [ ] Page1 group created under GlyphGrid
- [ ] 9 slots created in Page1
- [ ] GlyphSlot component added to all 9 slots
- [ ] Page2 group created (copy of Page1)
- [ ] All 18 slots have GlyphSlot components
- [ ] slotsPage1 assigned in CodexController (9 slots)
- [ ] slotsPage2 assigned in CodexController (9 slots)
- [ ] Arrow keys flip between pages when tested

---

## Notes

- The `GlyphsPerPage = 9` constant in CodexController means it expects exactly 9 slots per page
- If you want different grid sizes (4x4, 5x5), you'd need to modify that constant
- For now, stick with 3x3 (9 slots) per page
