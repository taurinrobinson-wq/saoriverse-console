# Unity UI Creation - Quick Reference

## Where to Find UI Elements in Hierarchy

**IMPORTANT:** UI elements are under **UI** menu, NOT "2D Object"

---

## Creating UI Objects

### Method 1: Right-Click in Hierarchy (Recommended)

1. **If you have NO Canvas yet:**
   - Right-click in Hierarchy
   - Look for **UI** option in menu
   - Select UI → Panel
   - This creates a Canvas + Panel automatically

2. **If you already HAVE a Canvas:**
   - Right-click on the Canvas (or any child of it)
   - Select **UI** from menu
   - Pick what you want: Panel, Button, Text, Image, Scroll View, etc.

### Method 2: Top Menu

1. GameObject → UI → [Pick element]

---

## Common UI Elements You'll Need

| Element | Menu Path | Purpose |
|---------|-----------|---------|
| **Panel** | UI → Panel | Container (like a div in HTML) |
| **Text** / **TextMeshPro - Text** | UI → TextMeshPro - Text | Display text |
| **Image** | UI → Image | Display sprites/icons |
| **Button** | UI → Button | Clickable button |
| **Scroll View** | UI → Scroll View | Scrollable container |
| **Layout Group** (Grid) | Add Component → Grid Layout Group | Arrange children in grid |
| **Layout Group** (Vertical) | Add Component → Vertical Layout Group | Stack children vertically |

---

## Step-by-Step Example: Create an Inventory Item

**Goal:** Create a Panel with Icon + Name + Quantity (like in the guide)

### Step 1: Create the Panel Container
```
1. Right-click UI_Canvas in Hierarchy
2. UI → Panel
3. Rename to: InventoryItemEntry
4. Inspector → Rect Transform:
   - Width: 100
   - Height: 100
```

### Step 2: Add Icon (Image)
```
1. Right-click InventoryItemEntry
2. UI → Image
3. Rename to: ItemIcon
4. Inspector → Rect Transform:
   - Width: 80
   - Height: 80
   - Anchor Preset: Top-Left
   - Position X: 10, Y: -10
```

### Step 3: Add Name (TextMeshPro)
```
1. Right-click InventoryItemEntry
2. TextMeshPro - Text
3. Rename to: ItemName
4. Edit Text: "Item Name"
5. Inspector → Rect Transform:
   - Width: 200
   - Height: 30
   - Anchor: Top-Left
   - Position X: 100, Y: -10
6. TextMeshProUGUI Component:
   - Font Size: 16
```

### Step 4: Add Quantity (TextMeshPro)
```
1. Right-click InventoryItemEntry
2. TextMeshPro - Text
3. Rename to: Quantity
4. Edit Text: "x1"
5. Inspector → Rect Transform:
   - Width: 60
   - Height: 30
   - Anchor: Bottom-Right
   - Position X: -10, Y: 10
6. TextMeshProUGUI Component:
   - Font Size: 14
   - Color: Yellow
```

### Step 5: Add the UI Script
```
1. Select InventoryItemEntry in Hierarchy
2. Inspector → Add Component
3. Search: InventoryItemEntryUI
4. Assign References:
   - Item Icon: ItemIcon (the Image)
   - Item Name: ItemName (the TextMeshPro)
   - Quantity Label: Quantity (the TextMeshPro)
```

### Step 6: Save as Prefab
```
1. Drag InventoryItemEntry from Hierarchy
2. Drop into: Assets/Prefabs/UI/
3. Now you have: InventoryItemEntry.prefab
```

---

## The UI Hierarchy Structure You're Building

```
Canvas (UI_Canvas)  ← Your existing canvas
├── BitsDisplay     ← Already done
├── InventoryPanel  ← You'll create
│   ├── Header
│   ├── ItemsScroll
│   │   └── ItemsContainer (Grid Layout Group)
│   └── EmptyLabel
└── TradePanel      ← You'll create
    ├── Header
    ├── WantedSection
    │   └── WantedItemsContainer
    ├── OfferedSection
    │   └── OfferedItemsContainer
    ├── StatusLabel
    └── TradeButton
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "I don't see UI in the menu" | Make sure you right-click in Hierarchy (not in Scene view) |
| "UI menu is greyed out" | You might not have TextMeshPro set up. Do you see TextMeshPro option? If not, go GameObject → TextMeshPro → [element] |
| "My panel looks weird" | Check Anchor settings - often needs to be "stretch" or positioned correctly |
| "Text is tiny/huge" | Adjust Font Size in TextMeshProUGUI component |
| "Children aren't arranged properly" | Add a Layout Group component (Grid Layout or Vertical Layout) to the parent |

---

## Quick Tips 💡

1. **Always right-click on the Canvas (or a child of Canvas)** when creating UI
2. **Use Anchor Presets** (top-right corner of Rect Transform) to quickly position
3. **Layout Groups** are your friend - they auto-arrange children
4. **Grid Layout Group** = grid of items (like inventory)
5. **Vertical Layout Group** = stack items vertically (like trade list)

---

## Canvas vs World Objects

- **Canvas** = UI (buttons, inventory, HUD) - stays on screen
- **3D Objects/2D Objects** = Game objects in the world
- UI things go INSIDE a Canvas, world things don't

When in doubt: **If it's UI, right-click Canvas and use UI menu**

---

**Next:** Follow the updated **UI_IMPLEMENTATION_GUIDE.md** which now has correct menu paths!
