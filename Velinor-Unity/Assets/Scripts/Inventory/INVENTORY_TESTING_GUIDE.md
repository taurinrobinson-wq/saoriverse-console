# Velinor Inventory System – Integration Testing Guide

## Pre-Integration Checklist

Before connecting to dialogue or NPC systems, verify the core inventory works:

### ✅ Compilation Check
```
File → Open C# Project
Build → Rebuild Solution
Look for: "Build succeeded" (no CS0* errors)
```

**Expected:** All 6 .cs files compile without errors.

---

## Test 1: Basic Inventory Operations (Standalone)

**Create a test scene with manual inspector testing:**

1. **Scene Setup:**
   - Empty scene: `Assets/Scenes/TestInventory.unity`
   - Add empty GameObject: `InventoryManager`
   - Add component: `InventoryService`

2. **Create ItemDatabase:**
   - Project root: `Create → Velinor/Inventory/Item Database`
   - Name: `TestDatabase`
   - Create 3 items:
     ```
     copper_wire (Metal, Electrical tags)
     glass (Glass tag)
     sheet_metal (Metal tag)
     ```
   - Add all 3 to database's `items` list
   - Assign to InventoryService inspector field

3. **Play scene:**
   ```
   Console output should show:
   "[ItemDatabase] Initialized with 3 items"
   "[InventoryService] Initialized and marked persistent"
   ```

4. **Use Console to test:**
   ```csharp
   // In any script Update():
   if (Input.GetKeyDown(KeyCode.A))
       InventoryService.Instance.Add("copper_wire", 1);
   
   if (Input.GetKeyDown(KeyCode.R))
       InventoryService.Instance.Remove("copper_wire", 1);
   
   if (Input.GetKeyDown(KeyCode.Q))
       Debug.Log($"Copper wire qty: {InventoryService.Instance.GetQuantity("copper_wire")}");
   
   if (Input.GetKeyDown(KeyCode.T))
   {
       var tags = InventoryService.Instance.GetByTag(ItemTag.Metal);
       Debug.Log($"Metal items: {tags.Count}");
   }
   ```

5. **Expected Console Output:**
   ```
   [InventoryService] Added 1x copper_wire (total: 1)
   [InventoryService] Added 1x copper_wire (total: 2)
   Copper wire qty: 2
   Metal items: 2  (copper_wire and sheet_metal)
   ```

---

## Test 2: World Item Pickup

**In same test scene:**

1. **Create a pickup:**
   - New GameObject: `TestWire`
   - Add SpriteRenderer (any sprite)
   - Add component: `WorldItemPickup`
   - Set:
     - **pickupId**: `test_wire_01`
     - **itemDefinition**: Drag `copper_wire` ItemDefinition
     - **quantity**: `3`
   - Add BoxCollider (mark as trigger)

2. **Add basic player movement:**
   - New GameObject: `Player`
   - Add Rigidbody + Collider
   - Add simple movement script (or use existing PlayerController)

3. **Play & Test:**
   - Walk over pickup → Should disappear
   - Console: `[WorldItemPickup] Collected 3x copper_wire`
   - Verify qty: `InventoryService.Instance.GetQuantity("copper_wire")` = 3

4. **Stop & Replay:**
   - Press Stop
   - Play again
   - Pickup should NOT respawn (GameFlags persisted it)
   - Console: `[WorldItemPickup] test_wire_01 already collected, hiding`

---

## Test 3: Inventory UI Panel

**Add to test scene:**

1. **Create Canvas:**
   - Add UI Canvas to scene
   - Create child Panel: `InventoryPanel`
   - Position: Left side (x ≈ -200)
   - Size: 300×600

2. **Set up panel:**
   - Add component: `InventoryUIPanel`
   - Create CanvasGroup on same GameObject
   - Create child VerticalLayoutGroup
   - Assign to panel fields

3. **Create ItemEntry prefab:**
   - Create child: HorizontalLayoutGroup
   - Add children: Image, VerticalLayoutGroup
     - VerticalLayoutGroup contains: Text (name), Text (qty)
   - Add component: `InventoryItemEntryUI`
   - Save as prefab
   - Delete from scene

4. **Assign prefab to panel:**
   - Select InventoryPanel
   - Inspector → itemEntryPrefab field
   - Drag the prefab

5. **Add toggle script:**
   ```csharp
   if (Input.GetKeyDown(KeyCode.I))
   {
       var panel = FindObjectOfType<InventoryUIPanel>();
       panel?.ToggleVisibility();
   }
   ```

6. **Play & Test:**
   - Press I → Panel should fade in
   - Press A (from Test 1) → Item appears in list
   - Press A again → Quantity updates to x2
   - Panel shows "Copper Wire x2" or similar
   - Press I → Panel fades out

---

## Test 4: Persistence Across Scenes

**Create two test scenes:**

**Scene 1 (Market):**
- InventoryService
- Multiple WorldItemPickup objects
- Test collecting 3 items

**Scene 2 (Ruins):**
- Empty scene
- Button that loads Scene 1
- Display current inventory via debug text

**Test Flow:**
1. Play Scene 1
2. Collect 2× copper_wire, 1× glass
3. Load Scene 2
4. Inventory unchanged (InventoryService survived)
5. Load Scene 1 again
6. Pickups are gone (GameFlags remembered)

**Expected Console:**
```
[InventoryService] Initialized and marked persistent
[WorldItemPickup] market_wire_01 already collected, hiding
[WorldItemPickup] market_glass_01 already collected, hiding
```

---

## Test 5: Save/Load Cycle

**Add save/load to test:**

```csharp
// Save button handler
void SaveInventory()
{
    var data = InventoryService.Instance.GetSaveData();
    string json = JsonUtility.ToJson(new SaveContainer { inventory = data });
    PlayerPrefs.SetString("inventory_save", json);
    Debug.Log("Inventory saved");
}

// Load button handler
void LoadInventory()
{
    string json = PlayerPrefs.GetString("inventory_save", "");
    if (!string.IsNullOrEmpty(json))
    {
        SaveContainer data = JsonUtility.FromJson<SaveContainer>(json);
        InventoryService.Instance.LoadSaveData(data.inventory);
        Debug.Log("Inventory loaded");
    }
}

[System.Serializable]
public class SaveContainer
{
    public List<InventoryEntryData> inventory;
}
```

**Test:**
1. Collect items
2. Click "Save"
3. Stop play mode
4. Play again
5. Click "Load"
6. Inventory restored

---

## Test 6: Tag-Based Queries

**Simulate NPC dialogue:**

```csharp
public class TestNPCPreference : MonoBehaviour
{
    void Start()
    {
        // Tala likes Metal items
        var metalItems = InventoryService.Instance.GetByTag(ItemTag.Metal);
        
        Debug.Log($"Tala can accept {metalItems.Count} items:");
        foreach (var kvp in metalItems)
        {
            ItemDefinition item = InventoryService.Instance.GetItemDefinition(kvp.Key);
            Debug.Log($"  - {item.DisplayName} (qty: {kvp.Value})");
        }
    }
}
```

**Expected Output:**
```
Tala can accept 2 items:
  - Copper Wire (qty: 2)
  - Sheet Metal (qty: 1)
```

---

## Integration Checklist

| Test | Pass | Notes |
|------|------|-------|
| **Compilation** | ☐ | No CS0* errors |
| **ItemDatabase creation** | ☐ | 3+ items registered |
| **Add/Remove/Query** | ☐ | Console shows updates |
| **WorldItemPickup collection** | ☐ | Item disappears, qty increases |
| **Pickup persistence** | ☐ | Pickup doesn't respawn after Stop/Play |
| **UI Panel display** | ☐ | Shows item names and quantities |
| **UI updates on add** | ☐ | New item row appears; qty updates |
| **Inventory persists across scenes** | ☐ | InventoryService survives scene load |
| **Pickup visibility across scenes** | ☐ | Collected pickups stay gone |
| **Save/Load cycle** | ☐ | Inventory data persists in PlayerPrefs |
| **Tag-based queries** | ☐ | GetByTag returns correct items |

---

## Known Limitations & Next Steps

### ⚠️ Limitations

1. **IInteractable requires GameObject player parameter**
   - WorldItemPickup receives player reference but doesn't use it
   - Could log interaction details later if needed

2. **No input handling in WorldItemPickup**
   - Relies on PlayerController's E-key detection
   - Make sure PlayerController calls Interact() on raycasted objects

3. **InventoryUIPanel requires manual setup**
   - Must create ItemEntry prefab and assign manually
   - Could auto-generate in future iteration

4. **No tooltip/detail panel**
   - Clicking inventory item does nothing (placeholder)
   - Add detail view in Phase 2

### ✅ Ready for Integration

- [x] Dialogue system → Query by tag
- [x] NPC requests → Check inventory
- [x] Save/load system → Persist itemIds
- [x] Crafting system → Query ingredients
- [x] Codex system → Track discovered items

---

## Debugging Tips

### Console Not Showing [InventoryService] Logs?

1. Check InventoryService is in scene
2. Check ItemDatabase is assigned (Inspector)
3. Check scene is playing (not paused)
4. Filter console: "InventoryService"

### WorldItemPickup Not Collecting?

1. Check BoxCollider is marked "isTrigger"
2. Check ItemDefinition is assigned
3. Check PlayerController's E-key handler calls Interact()
4. Check console for error messages

### Inventory Not Persisting Between Scenes?

1. Check InventoryService has `DontDestroyOnLoad` (Start logs it)
2. Verify ItemDatabase assigned in Inspector
3. Check GameFlags working (separate system)

### UI Panel Not Showing Items?

1. CanvasGroup assigned?
2. VerticalLayoutGroup created and assigned?
3. ItemEntry prefab assigned and valid?
4. Call `InventoryUIPanel.SetVisibility(true)` or press I key

---

## Test Data (Copy/Paste Asset Setup)

**If you want to reuse this test data:**

```
ItemDatabase (root of project)
├── ItemDefinition: copper_wire
│   ├── itemId: copper_wire
│   ├── displayName: Copper Wire
│   ├── category: Material
│   ├── tags: [Metal, Electrical]
│   ├── maxStackSize: 99
│
├── ItemDefinition: glass
│   ├── itemId: glass
│   ├── displayName: Glass Fragments
│   ├── category: Material
│   ├── tags: [Glass]
│   ├── maxStackSize: 99
│
└── ItemDefinition: sheet_metal
    ├── itemId: sheet_metal
    ├── displayName: Sheet Metal
    ├── category: Material
    ├── tags: [Metal, Mechanical]
    ├── maxStackSize: 99
```

---

**After passing all tests, inventory is ready for NPC dialogue integration.**
