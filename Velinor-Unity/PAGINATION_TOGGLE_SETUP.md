# Glyph Grid Pagination - Simple Toggle Setup

Your approach is perfect! Just toggle between two identical grids.

---

## Current Setup

```
CodexPanel
├── GlyphGrid_Pg1 (9 slots - VISIBLE)
│   ├── Slot_0 through Slot_8
│   └── Navigation (Btn_Next, etc.)
│
└── GlyphGrid_Pg2 (9 slots - DISABLED)
    ├── Slot_0 through Slot_8
    └── Navigation (hidden when disabled)
```

---

## Step 1: Add GlyphSlot Component to All Slots

For each slot in **both** GlyphGrid_Pg1 and GlyphGrid_Pg2:

1. Select the slot (e.g., Slot_0 in Page 1)
2. **Add Component** → Search for `GlyphSlot`
3. Click to add

Do this for all 18 slots (9 per page).

**Note:** Each grid's slots are independent, so you'll be adding 18 components total.

---

## Step 2: Wire CodexController Slot Lists

CodexController still needs to know about ALL slots for collecting glyphs:

1. Select **CodexController** in hierarchy
2. **Slots Page 1** - Assign the 9 slots from **GlyphGrid_Pg1**
3. **Slots Page 2** - Assign the 9 slots from **GlyphGrid_Pg2**

This way:
- Glyphs 1-9 fill slots in Page 1
- Glyphs 10-18 fill slots in Page 2

---

## Step 3: Add Pagination Script to CodexPanel

1. Select **CodexPanel** (or any manager object in your hierarchy)
2. **Add Component** → Search for `GlyphGridPagination`
3. In Inspector:
   - **Glyph Grid Page 1**: Drag `GlyphGrid_Pg1`
   - **Glyph Grid Page 2**: Drag `GlyphGrid_Pg2`

---

## Step 4: Wire Buttons

### For Btn_Next:
1. Select **Btn_Next** in hierarchy
2. In Inspector, find **Button** component
3. Under **On Click ()**, click **+**
4. Drag the object with **GlyphGridPagination** component into the field
5. From the function dropdown, select:
   - **GlyphGridPagination** → **NextPage()**

### For Btn_Prev:
1. Select **Btn_Prev**
2. Repeat above, but select **PreviousPage()** instead

---

## How It Works

1. **Play scene** → Glyphs fill slots in Page 1
2. **Press Next** → Page 1 disabled, Page 2 enabled (shows glyphs 10-18)
3. **Press Prev** → Page 2 disabled, Page 1 enabled (shows glyphs 1-9)
4. **Click glyph** → Name displays correctly

---

## Key Advantage of This Approach

- ✅ Simple toggle logic (just SetActive on/off)
- ✅ Each page is a complete, independent grid
- ✅ No complex state management
- ✅ Easy to debug (just look at which grid is enabled)
- ✅ Scales easily (add Page 3, Page 4, etc. later)

---

## Checklist

- [ ] Added GlyphSlot component to all 18 slots
- [ ] Assigned Page 1 slots to CodexController
- [ ] Assigned Page 2 slots to CodexController
- [ ] Added GlyphGridPagination component to CodexPanel
- [ ] Wired Btn_Next → NextPage()
- [ ] Wired Btn_Prev → PreviousPage()
- [ ] Test: Toggle between pages, glyphs persist correctly
