# Creating Additional Assets - Duplication Guide

## Folder Structure Created ✓

```
Assets/
├── Resources/
│   └── Items/
│       ├── CopperWire.asset (SAMPLE - duplicate this)
│       └── ItemDatabase.asset (MAIN - you'll add duplicates to this)
└── ScriptableObjects/
    └── Economy/
        └── WillyTradeProfile.asset (SAMPLE - duplicate this)
```

---

## How to Add More ItemDefinitions

### Method 1: Duplicate in Unity Editor (Easiest)

1. **Right-click** `CopperWire.asset` in Project window
2. **Select "Duplicate"**
3. **Rename** the new file (e.g., `GlassFragments.asset`)
4. **Double-click** to edit
5. **Change these fields:**
   - **Item Id**: `glass_fragments` (must be unique, lowercase, no spaces)
   - **Display Name**: `Glass Fragments`
   - **Description**: Your description
   - **Category**: `Material` or `Tool`
   - **Tags**: Add relevant tags (Metal, Electrical, Glass, Mechanical, Salvage)
   - **Base Value**: Price in bits (1-5 typical)
   - **Max Stack Size**: How many can stack (99 for materials, 5 for bulky items)

6. **Save** (Ctrl+S)

### Method 2: Duplicate via File System

1. Copy `CopperWire.asset` in Windows Explorer
2. Paste and rename (e.g., `GlassFragments.asset`)
3. Open in text editor and change the itemId and names
4. Save

---

## How to Add the New Item to ItemDatabase

### Step 1: Find ItemDatabase in Inspector

1. **Open** `Assets/Resources/Items/ItemDatabase.asset`
2. **In Inspector**, see the "Items" list

### Step 2: Add New Items

1. **Click the "+" button** to add a new slot
2. **Drag your new asset** into the empty slot
3. **Repeat** for each new item

### Example ItemDefinition Fields

```
itemId: copper_wire
displayName: Copper Wire
description: Salvaged copper electrical wire
category: Material
icon: (leave empty for now)
tags: [Metal, Electrical]
baseValue: 2
maxStackSize: 99
```

**Available Tags to Use:**
- Metal
- Electrical
- Mechanical
- Glass
- Salvage
- Tool

---

## How to Create More NPC Trade Profiles

### Method 1: Duplicate in Unity Editor

1. **Right-click** `WillyTradeProfile.asset`
2. **Select "Duplicate"**
3. **Rename** (e.g., `TalaTradeProfile.asset`)
4. **Double-click** to edit
5. **Change these fields:**
   - **NPC ID**: `tala` (unique, lowercase)
   - **Display Name**: `Tala`
   - **Preferred Tags**: What this NPC likes (adjust multipliers)
   - **Highly Sought Items**: What this NPC REALLY wants (higher multipliers)
   - **Default Multiplier**: Catch-all for items without preferences

### Step 2: Configure Preferences

**Example - Tala (values different items than Willy):**

```yaml
npcId: tala
displayName: Tala
preferredTags:
  - tag: Glass
    multiplier: 1.4
  - tag: Salvage
    multiplier: 1.2
highlySoughtItems:
  - itemId: light_bulb
    multiplier: 1.6
  - itemId: glass_fragments
    multiplier: 1.4
defaultMultiplier: 1.0
```

---

## Complete Item Creation Workflow

### Add 5 Items in 5 Minutes

1. **Start with CopperWire.asset** as template
2. **Duplicate 4 times** (Ctrl+D or right-click)
3. **Rename each:**
   - GlassFragments.asset
   - SheetMetal.asset
   - LightBulb.asset
   - ToolFragment.asset

4. **Edit each one** (double-click to open):
   - Change itemId, displayName, description, baseValue, tags

5. **Add all to ItemDatabase:**
   - Open ItemDatabase.asset
   - Click "+" five times
   - Drag each item into slots

**Total time: ~5 minutes**

---

## Asset Template Reference

### ItemDefinition Template Fields

| Field | Value | Example |
|-------|-------|---------|
| Item Id | Unique ID (snake_case) | `copper_wire` |
| Display Name | User-friendly name | `Copper Wire` |
| Description | What it is | `Salvaged copper wire` |
| Category | Material or Tool | `Material` |
| Icon | Sprite (optional) | Leave empty |
| Tags | List of tags | Metal, Electrical |
| Base Value | Bits worth | 2-5 |
| Max Stack Size | Stack limit | 99 |

### NPCTradeProfile Template Fields

| Field | Value | Example |
|-------|-------|---------|
| NPC ID | Unique ID (snake_case) | `willy` |
| Display Name | NPC name | `Willy` |
| Preferred Tags | Tag + multiplier pairs | Electrical: 1.25 |
| Highly Sought Items | Item ID + multiplier | copper_wire: 1.5 |
| Default Multiplier | Fallback multiplier | 1.0 |

---

## Quick Reference - ItemIds to Create

Use these itemIds when duplicating:

```
copper_wire ✓ (already created)
glass_fragments
sheet_metal
light_bulb
tool_fragment
```

---

## Validation Checklist

After creating new assets:

- [ ] Item ID is unique and lowercase (no spaces)
- [ ] Display Name is user-friendly
- [ ] Base Value is 1-5 (or higher for rare items)
- [ ] Max Stack Size is appropriate (99 for common, 5-10 for rare)
- [ ] Tags are chosen from available list
- [ ] Item added to ItemDatabase
- [ ] Console shows no errors on Play

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Asset won't open in editor | Right-click → Open With → Text Editor, check YAML syntax |
| Item not in ItemDatabase | Add via Inspector, not by editing YAML |
| itemId has spaces | Change to snake_case (copper_wire not copper wire) |
| Duplicate didn't work | Use right-click in Project window, not file explorer |
| Changes don't show | Save (Ctrl+S) and refresh (F5) if needed |

---

## Next Steps

1. **Duplicate CopperWire.asset** 4 times to create all 5 items
2. **Edit each one** with unique itemId and values
3. **Add all to ItemDatabase** via Inspector
4. **Duplicate WillyTradeProfile.asset** for other NPCs (Tala, Ravi, etc.)
5. **Play and test** - console should show "Initialized with 5 items"

---

**You're all set! Duplicate as needed and the system will work perfectly. 🚀**
