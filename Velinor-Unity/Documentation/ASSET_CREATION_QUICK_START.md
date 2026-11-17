# Asset Creation Quick Reference

## What Was Created For You ✓

```
Assets/Resources/Items/
├── CopperWire.asset ← DUPLICATE THIS for other items
├── ItemDatabase.asset ← Add all items here
└── DUPLICATION_GUIDE.md ← Detailed instructions

Assets/ScriptableObjects/Economy/
└── WillyTradeProfile.asset ← DUPLICATE THIS for other NPCs
```

---

## 5-Minute Setup

### Step 1: Create Remaining Item Definitions (3 min)

**In Unity Editor:**
1. Right-click `CopperWire.asset`
2. Click "Duplicate" (repeat 4 times)
3. Rename each:
   - `GlassFragments.asset`
   - `SheetMetal.asset`
   - `LightBulb.asset`
   - `ToolFragment.asset`

4. Edit each (double-click):
   - Change **Item Id** (snake_case, unique)
   - Change **Display Name**
   - Adjust **Base Value** and **Tags**

### Step 2: Add All Items to ItemDatabase (2 min)

1. Open `ItemDatabase.asset`
2. In Inspector, click "+" under Items (5 times)
3. Drag each new item into the slots
4. Save

**Done! ItemDatabase now has 5 items**

---

## Item IDs to Create

When duplicating CopperWire.asset, use these IDs:

```
copper_wire      ✓ (done)
glass_fragments  ← create
sheet_metal      ← create
light_bulb       ← create
tool_fragment    ← create
```

---

## What to Change in Each ItemDefinition

### GlassFragments.asset
```
Item Id: glass_fragments
Display Name: Glass Fragments
Description: Shards of salvaged glass
Tags: [Glass]
Base Value: 1
Max Stack Size: 99
```

### SheetMetal.asset
```
Item Id: sheet_metal
Display Name: Sheet Metal
Description: Flattened metal sheets
Tags: [Metal, Mechanical]
Base Value: 3
Max Stack Size: 99
```

### LightBulb.asset
```
Item Id: light_bulb
Display Name: Light Bulb
Description: A working light bulb
Tags: [Electrical, Glass]
Base Value: 4
Max Stack Size: 5
```

### ToolFragment.asset
```
Item Id: tool_fragment
Display Name: Tool Fragment
Description: Component for tool creation
Tags: [Mechanical]
Base Value: 5
Max Stack Size: 10
```

---

## Creating NPC Profiles (Optional)

To add more NPCs with different trading preferences:

1. Right-click `WillyTradeProfile.asset`
2. Click "Duplicate"
3. Rename (e.g., `TalaTradeProfile.asset`)
4. Edit:
   - Change **NPC ID** (e.g., `tala`)
   - Change **Display Name** (e.g., `Tala`)
   - Adjust **Preferred Tags** and multipliers
   - Adjust **Highly Sought Items**

---

## Testing

After adding all items:

1. **Play scene**
2. **Console should show:**
   ```
   [ItemDatabase] Initialized with 5 items
   [InventoryService] Initialized and marked persistent
   ```

3. **If not:**
   - Check ItemDatabase has 5 items in list
   - Check each item has unique itemId
   - Check InventoryService is assigned ItemDatabase

---

## Bonus: Folder Contents

Both folders are now ready to use:

**Assets/Resources/Items/**
- Items must be here (Resources folder)
- ItemDatabase must be here
- ✓ Automatically loadable by code

**Assets/ScriptableObjects/Economy/**
- NPC profiles stored here
- ✓ Easy to organize by type

---

**Next: Open QUICK_SETUP_CHECKLIST.md and follow Phase 1 (now complete!)**
