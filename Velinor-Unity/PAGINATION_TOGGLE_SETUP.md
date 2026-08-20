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
3. In Inspector, drag these references:
   - **Glyph Grid Page 1**: Drag `GlyphGrid_Pg1`
   - **Glyph Grid Page 2**: Drag `GlyphGrid_Pg2`
   - **Btn Next**: Drag the Next button (Btn_Next)
   - **Btn Prev**: Drag the Prev button (Btn_Prev)

**Why the buttons?** The script automatically disables them at the boundaries:
- On Page 1: Btn_Prev is disabled (grayed out)
- On Page 2: Btn_Next is disabled (grayed out)

---

## Step 4: Wire Buttons to Script

The buttons call the pagination methods AND are managed by the script for state.

### For Btn_Next:
1. Select **Btn_Next** in hierarchy
2. In Inspector, find **Button** component
3. Under **On Click ()**, click **+**
4. Drag the object with **GlyphGridPagination** component
5. Dropdown → **GlyphGridPagination** → **NextPage()**

### For Btn_Prev:
1. Select **Btn_Prev**
2. Repeat above, but select **PreviousPage()** instead

---

## Button Behavior (Automatic)

The script automatically handles button states:
- **Page 1**: Btn_Prev appears disabled/grayed out (can't go back)
- **Page 2**: Btn_Next appears disabled/grayed out (can't go forward)

This prevents the player from clicking buttons that don't do anything.

---

## How It Works

1. **Play scene** → Glyphs fill slots in Page 1, Btn_Prev is disabled
2. **Press Next** → Page 1 hidden, Page 2 shown (glyphs 10-18), Btn_Next now disabled
3. **Press Prev** → Page 2 hidden, Page 1 shown (glyphs 1-9), Btn_Prev disabled again
4. **Click glyph** → Name displays correctly
5. **Buttons respect boundaries** → Can't go before Page 1 or after Page 2

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
- [ ] Assigned button references (Btn_Next and Btn_Prev) to GlyphGridPagination
- [ ] Wired Btn_Next → NextPage()
- [ ] Wired Btn_Prev → PreviousPage()
- [ ] Test: Buttons disable at page boundaries
- [ ] Test: Toggle between pages, glyphs persist correctly
