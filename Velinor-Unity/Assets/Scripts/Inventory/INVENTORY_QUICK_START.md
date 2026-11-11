# Velinor Inventory System – Quick Start Guide

## What You Have

A **lightweight, tag-based inventory system** designed specifically for Velinor's salvage and NPC-interaction gameplay.

### Core Components

| Component | Role | Location |
|-----------|------|----------|
| **ItemDefinition** | Defines what an item *is* (name, icon, description, tags) | Assets/Resources/Items/ |
| **ItemDatabase** | Central registry; O(1) lookup by itemId | Project root asset |
| **InventoryService** | Runtime inventory state; Add/Remove/Query operations | DontDestroyOnLoad singleton |
| **WorldItemPickup** | Placed in scenes; collected items vanish and enter inventory | Per-item GameObject component |
| **InventoryUIPanel** | Left-side UI panel showing all items | Part of UI_Canvas prefab |
| **InventoryItemEntryUI** | Single row in inventory list | Instantiated as needed |

---

## 5-Minute Setup

### Step 1: Create ItemDatabase

1. **Right-click** in Project (Assets folder)
2. **Create → Velinor/Inventory/Item Database**
3. Name it `ItemDatabase`
4. Keep it at the project root or in `Assets/Resources/Items/`
5. **Assign to InventoryService** (Inspector → itemDatabase field)

### Step 2: Create Sample Items

Create 3–4 items to test:

```
Right-click → Create → Velinor/Inventory/Item Definition
```

| Name | ItemId | Category | Tags | MaxStackSize | Icon |
|------|--------|----------|------|--------------|------|
| Copper Wire | copper_wire | Material | Metal, Electrical | 99 | (any sprite) |
| Glass Fragments | glass_fragments | Material | Glass | 99 | (any sprite) |
| Sheet Metal | sheet_metal | Material | Metal, Mechanical | 99 | (any sprite) |
| Light Bulb | light_bulb | Material | Electrical, Glass | 5 | (any sprite) |

### Step 3: Add Items to ItemDatabase

1. Select `ItemDatabase` asset
2. In Inspector, expand `items` list
3. **Add 4 entries** (set size to 4)
4. Drag your 4 ItemDefinition assets into the slots

**Verify:** Select ItemDatabase → Inspector should show all 4 items

### Step 4: Add InventoryService to Scene

1. Create empty GameObject: `InventoryService`
2. **Add component → InventoryService**
3. Assign your `ItemDatabase` to the inspector field
4. Verify it says "Initialized with 4 items" in console on Play

### Step 5: Create WorldItemPickup in Scene

1. Create a GameObject with a **SpriteRenderer** (or 3D model)
2. **Add component → WorldItemPickup**
3. Set:
   - **pickupId**: `test_wire_01` (auto-fills if empty)
   - **itemDefinition**: Select `Copper Wire`
   - **quantity**: `3`
4. **Add Box Collider** and mark as trigger
5. **Add component → IInteractable** interface stub (if not already present)

**Test:** Play scene, walk over pickup, check console for "Collected 3x Copper Wire"

### Step 6: Add UI Panel to UI_Canvas

1. Select **UI_Canvas**
2. Create child Panel: **GameObject → UI → Panel**
   - Name: `InventoryPanel`
   - Position: Left side (x = -200 or similar)
   - Size: 300×600
3. **Add component → InventoryUIPanel**
4. Assign fields:
   - **CanvasGroup**: Drag self or create new
   - **itemListLayout**: Create child VerticalLayoutGroup
   - **itemEntryPrefab**: Create prefab (see below)

### Step 7: Create InventoryItemEntryUI Prefab

1. Create child of InventoryPanel:
   - **GameObject → UI → Horizontal Layout Group**
   - Name: `ItemEntryTemplate`
2. Add children:
   - **Image** (left) – for item icon
   - **Vertical Layout Group** (center)
     - **Text** – for item name
     - **Text** – for quantity
3. **Add component → InventoryItemEntryUI**
   - Assign Image, Text fields
4. **Drag this onto Assets as prefab**
5. **Delete from hierarchy** (only keep template as asset)

---

## Testing Checklist

- [ ] Can you collect the wire pickup? (Console: "Collected 3x Copper Wire")
- [ ] Does InventoryPanel appear when toggled?
- [ ] Does UI show "Copper Wire x3"?
- [ ] Can you collect multiple items?
- [ ] Does collecting item2 add row to UI?
- [ ] Reload scene → pickup gone? (pickupId persistence)
- [ ] Reload scene → inventory persists? (InventoryService.DontDestroyOnLoad)

---

## Common First Steps

### Add an Inventory Toggle Button

```csharp
// In InputManager or PlayerController
private void Update()
{
    if (Input.GetKeyDown(KeyCode.I))
    {
        InventoryService.Instance.GetComponentInParent<InventoryUIPanel>()?.ToggleVisibility();
    }
}
```

### Query Inventory by Tag (for NPCs)

```csharp
// Find all items with "Electrical" tag that player has
var electricalItems = InventoryService.Instance.GetByTag(ItemTag.Electrical);

foreach (var kvp in electricalItems)
{
    Debug.Log($"Has {kvp.Value}x {kvp.Key}");
}
```

### Remove Item When NPC Takes It

```csharp
// In dialogue or NPC interaction code
if (InventoryService.Instance.Contains("copper_wire", 2))
{
    InventoryService.Instance.Remove("copper_wire", 2);
    Debug.Log("Gave 2x Copper Wire to NPC");
}
```

---

## What NOT to Do

❌ **Don't create durability mechanics** – They're commented as deferred  
❌ **Don't add weight/capacity limits** – Not in this vertical slice  
❌ **Don't make items unique instances** – Stack them as quantities  
❌ **Don't hard-code NPC item preferences** – Use tags instead  
❌ **Don't use slots/grid layout** – Use the simple list  

---

## Next: NPC Dialogue Integration

Once inventory is working:

1. Add `WorldItemPickup` to Willy's scene
2. In dialogue, check **if player has required item by tag**
3. Show dialogue option: "Give Copper Wire to Tala?"
4. Call `InventoryService.Instance.Remove("copper_wire", 1)`
5. Unlock next dialogue stage

---

## File Locations

```
Assets/Scripts/Inventory/
├── ItemDefinition.cs           ← Define item types
├── ItemDatabase.cs             ← Central registry
├── InventoryService.cs         ← Runtime state (DontDestroyOnLoad)
├── WorldItemPickup.cs          ← Scene pickups
├── InventoryUIPanel.cs         ← Left panel
└── InventoryItemEntryUI.cs     ← Single row

Assets/Resources/Items/
├── ItemDatabase.asset          ← Created via menu
├── CopperWire.asset
├── GlassFragments.asset
├── SheetMetal.asset
└── LightBulb.asset
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Unknown item ID" error | Item not in ItemDatabase list |
| Inventory is null | InventoryService not in scene |
| UI doesn't update | InventoryUIPanel.OnEnable not firing; check Canvas |
| Pickup respawns | pickupId not saved in GameFlags; check WorldItemPickup.Start() |
| Can't interact with pickup | Missing Box Collider or IInteractable interface |

---

**Status:** ✅ Ready to use. Test with 3–4 items, then expand.
