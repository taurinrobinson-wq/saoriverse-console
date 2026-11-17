# Complete System Implementation & Wiring Guide

## Overview
This guide explains how to implement and wire together the Inventory, Currency, Tool, and NPC Trading systems created in commit `73282c230`.

**Architecture Overview:**
```
InventoryService (Singleton)
├── ItemDatabase (ScriptableObject reference)
└── Dictionary<itemId, quantity>

CurrencySystem (Singleton)
└── PlayerPrefs persistence (bits_total)

ToolSystem (Singleton)
├── EquippedToolId tracking
└── ToolDefinition list

NPCTrader (MonoBehaviour, Per-NPC)
├── NPCTradeProfile (ScriptableObject)
└── Uses InventoryService + CurrencySystem

WorldItemPickup (MonoBehaviour, Per-item)
├── ItemDefinition (ScriptableObject)
└── Uses InventoryService + GameFlags persistence

UI Systems:
├── InventoryUIPanel (Canvas child)
├── InventoryItemEntryUI (List entry prefab)
└── BitsDisplayUI (Currency display)
```

---

## Phase 1: Core Data Assets

### 1.1 Create ItemDefinition Assets

**Location:** `Assets/Resources/Items/`

**Steps:**
1. Create folder if missing: `Assets/Resources/Items/`
2. Right-click → Create → Velinor/Inventory/Item Definition
3. Create these 5 sample items:

| Name | ItemId | DisplayName | Category | Tags | MaxStackSize | BaseValue | Description |
|------|--------|-------------|----------|------|--------------|-----------|-------------|
| CopperWire.asset | copper_wire | Copper Wire | Material | Metal, Electrical | 99 | 2 | Salvaged copper electrical wire |
| GlassFragments.asset | glass_fragments | Glass Fragments | Material | Glass | 99 | 1 | Shards of salvaged glass |
| SheetMetal.asset | sheet_metal | Sheet Metal | Material | Metal, Mechanical | 99 | 3 | Flattened metal sheets |
| LightBulb.asset | light_bulb | Light Bulb | Material | Electrical, Glass | 5 | 4 | Working light bulb |
| ToolFragment.asset | tool_fragment | Tool Fragment | Tool | Mechanical | 10 | 5 | Component for tool creation |

**Notes:**
- **ItemId**: Used in code; must be unique, snake_case
- **Tags**: Enable NPC trading preferences (see NPCTradeProfile)
- **BaseValue**: Starting price before NPC multipliers
- **MaxStackSize**: Inventory limit per item type
- Icon field: Leave empty for now (can add sprites later)

### 1.2 Create ItemDatabase ScriptableObject

**File:** `Assets/Resources/Items/ItemDatabase.asset`

**Steps:**
1. Right-click in Items folder → Create → Velinor/Inventory/Item Database
2. Name it: `ItemDatabase`
3. In Inspector, expand "Items" list
4. Set size to 5
5. Drag your 5 ItemDefinition assets into slots 0-4
6. Save

**Verify in Console:**
When you play any scene with InventoryService, you should see:
```
[ItemDatabase] Initialized with 5 items
```

---

## Phase 2: Runtime Singleton Services

### 2.1 InventoryService Setup

**Script Location:** `Assets/Scripts/Inventory/InventoryService.cs`

**How It Works:**
- Singleton MonoBehaviour (DontDestroyOnLoad)
- Stores items as `Dictionary<itemId, quantity>`
- Fires `OnInventoryChanged` event when inventory updates
- Requires ItemDatabase reference

**Setup Steps:**

1. **Create empty GameObject in your scene:** `InventoryService`
2. **Add Component:** `InventoryService`
3. **In Inspector:**
   - **itemDatabase**: Drag `Assets/Resources/Items/ItemDatabase.asset`
4. **Verify:** Play scene → Console shows:
   ```
   [InventoryService] Initialized and marked persistent
   [ItemDatabase] Initialized with 5 items
   ```

**Key Methods:**
```csharp
// Add items to inventory
InventoryService.Instance.Add("copper_wire", 3);

// Remove items
InventoryService.Instance.Remove("copper_wire", 1);

// Query inventory
bool hasItems = InventoryService.Instance.Contains("copper_wire", 2);
Dictionary<string, int> items = InventoryService.Instance.GetAllItems();

// Listen to changes
InventoryService.Instance.OnInventoryChanged += (itemId, newQuantity) =>
{
    Debug.Log($"Inventory changed: {itemId} = {newQuantity}");
};
```

### 2.2 CurrencySystem Setup

**Script Location:** `Assets/Scripts/Economy/CurrencySystem.cs`

**How It Works:**
- Singleton MonoBehaviour (DontDestroyOnLoad)
- Persists to PlayerPrefs (key: `velinor_bits_total`)
- Auto-loads on Start()
- Fires events: `OnBitsEarned`, `OnBitsSpent`, `OnBitsChanged`

**Setup Steps:**

1. **Create empty GameObject in your scene:** `CurrencySystem`
2. **Add Component:** `CurrencySystem`
3. **In Inspector:**
   - **initialBits**: Set to `0` (starting balance)
4. **Verify:** Play scene → Console shows initial balance loading

**Key Methods:**
```csharp
// Earn bits from trades
CurrencySystem.Instance.Earn(6, "Sold copper wire to Willy");

// Spend bits on purchases
if (CurrencySystem.Instance.CanAfford(10))
{
    CurrencySystem.Instance.Spend(10, "Purchased tool recipe");
}

// Check balance
int balance = CurrencySystem.Instance.CurrentBits;

// Listen to changes
CurrencySystem.Instance.OnBitsChanged += (total) =>
{
    Debug.Log($"New balance: {total}");
};
```

### 2.3 ToolSystem Setup

**Script Location:** `Assets/Scripts/Interactions/ToolSystem.cs`

**How It Works:**
- Singleton MonoBehaviour (DontDestroyOnLoad)
- Checks if player has tools in inventory
- Tracks equipped tool
- Fires events: `OnToolEquipped`, `OnToolUnequipped`

**Setup Steps:**

1. **Create empty GameObject in your scene:** `ToolSystem`
2. **Add Component:** `ToolSystem`
3. **In Inspector:**
   - **availableTools**: Leave empty for now (can add tool definitions later)
4. **Verify:** No console errors on play

**Key Methods:**
```csharp
// Check if player has tool
bool hasPickaxe = ToolSystem.Instance.HasTool("pickaxe");

// Equip a tool (must be in inventory first)
ToolSystem.Instance.EquipTool("pickaxe");

// Get equipped tool
string equipped = ToolSystem.Instance.EquippedToolId;

// Listen to equipment changes
ToolSystem.Instance.OnToolEquipped += (toolId) =>
{
    Debug.Log($"Equipped: {toolId}");
};
```

---

## Phase 3: World Objects

### 3.1 WorldItemPickup - Item Collection

**Script Location:** `Assets/Scripts/Inventory/WorldItemPickup.cs`

**How It Works:**
- Add to any scene GameObject with collider
- When player interacts (E key), adds item to inventory
- Persists via GameFlags (won't respawn after collection)
- Must implement IInteractable

**Setup Steps per Item Pickup:**

1. **Create GameObject in scene:** `CopperWire_Pickup_01`
2. **Add Sprite Renderer or 3D Model** (visual representation)
3. **Add Collider:**
   - For 2D: **Box Collider 2D**, set `isTrigger = true`
   - For 3D: **Box Collider**, set `isTrigger = true`
4. **Add Component:** `WorldItemPickup`
5. **In Inspector:**
   - **pickupId**: `copper_wire_marketplace_01` (auto-generated from name)
   - **itemDefinition**: Drag `CopperWire.asset`
   - **quantity**: `3` (how many to give when collected)

**Test:**
- Play scene
- Walk over pickup
- Console: `[WorldItemPickup] Collected 3x Copper Wire`
- Inventory should show copper_wire: 3

### 3.2 BreakableDebris - Tool-Based Collection

**Script Location:** `Assets/Scripts/Interactions/BreakableDebris.cs`

**How It Works:**
- Requires specific tool to break
- Yields multiple material items
- Persists cleared state via GameFlags
- Must implement IInteractable

**Setup Steps:**

1. **Create GameObject in scene:** `Rock_Debris_01`
2. **Add Sprite Renderer** (rock texture from DLNK)
3. **Add Box Collider 2D**, set `isTrigger = true`
4. **Add Component:** `BreakableDebris`
5. **In Inspector:**
   - **debrisId**: `rock_debris_market_01` (unique identifier)
   - **spriteRenderer**: Drag self or the sprite renderer
   - **requiredToolId**: `pickaxe` (leave empty for free debris)
   - **materials**: Click + to add items
     - Element 0: itemId = `sheet_metal`, quantity = 2
     - Element 1: itemId = `glass_fragments`, quantity = 1
   - **intactColor**: Color.white
   - **brokenColor**: New Color(0.5, 0.5, 0.5, 0.5) (grayed out)
   - **debrisCollider**: Drag the Box Collider 2D

**Test:**
- Play scene
- Try to interact without tool → "This debris requires a pickaxe"
- Add pickaxe to inventory manually (via code or inspector)
- Equip pickaxe via ToolSystem
- Interact again → Debris breaks, materials added to inventory, visual grayed out

---

## Phase 4: NPC Trading System

### 4.1 Create NPCTradeProfile ScriptableObject

**File Location:** `Assets/ScriptableObjects/Economy/` (create folder if needed)

**Example: Willy's Trade Profile**

**Steps:**
1. Create folder: `Assets/ScriptableObjects/Economy/`
2. Right-click → Create → Velinor/Economy/NPC Trade Profile
3. Name: `WillyTradeProfile.asset`
4. **In Inspector:**
   - **NPC ID**: `willy`
   - **Display Name**: `Willy`
   - **Preferred Tags**: Click + to add
     - Element 0: `Electrical` (multiplier: 1.25)
     - Element 1: `Mechanical` (multiplier: 1.25)
     - Element 2: `Salvage` (multiplier: 1.10)
   - **Highly Sought Items**: Click + to add
     - Element 0: itemId = `copper_wire` (multiplier: 1.5)
     - Element 1: itemId = `sheet_metal` (multiplier: 1.3)
   - **Default Multiplier**: 1.0

**How It Works:**
- When player offers items, prices calculated as:
  - Base price = ItemDefinition.BaseValue
  - If item in "Highly Sought", multiply by 1.5
  - Else if item has tag in "Preferred Tags", multiply by 1.25
  - Else multiply by 1.0 (default)
  - Total = price_per_unit × quantity

**Example Trade:**
- Player offers: 2x copper_wire (BaseValue: 2 each)
- Willy highly seeks copper_wire (multiplier: 1.5)
- Price per unit: 2 × 1.5 = 3 bits
- Total for 2: 3 × 2 = 6 bits

### 4.2 Add NPCTrader to NPC GameObject

**Script Location:** `Assets/Scripts/Interactions/NPCTrader.cs`

**Setup Steps:**

1. **Select NPC GameObject** (e.g., `Willy` in scene)
2. **Add Component:** `NPCTrader`
3. **In Inspector:**
   - **npcId**: `willy` (auto-fills from tradeProfile if assigned)
   - **tradeProfile**: Drag `WillyTradeProfile.asset`
4. **Verify:**
   - Must have Box Collider 2D or 3D (for interaction)
   - Console logs: `NPC willy (Willy) ready to trade` on interaction

**Integration with Dialogue:**

In dialogue code, call:
```csharp
var npcTrader = npc.GetComponent<NPCTrader>();
if (npcTrader != null)
{
    // Create offer based on items player wants to give
    var offer = npcTrader.CreateTradeOffer(
        new Dictionary<string, int> 
        { 
            { "copper_wire", 2 },
            { "glass_fragments", 1 }
        }
    );
    
    if (offer != null)
    {
        Debug.Log($"Trade offer: {offer.totalBitsOffered} bits");
        
        // Show UI prompt to player
        // If accepted:
        if (npcTrader.ExecuteTrade(offer))
        {
            Debug.Log("Trade completed!");
            // Inventory automatically updated
            // Bits automatically awarded
        }
    }
}
```

---

## Phase 5: UI Systems

### 5.1 Add InventoryUIPanel to Canvas

**Script Location:** `Assets/Scripts/Inventory/InventoryUIPanel.cs`

**Setup Steps:**

1. **Select UI_Canvas prefab** (or canvas in scene)
2. **Create new child Panel:** Right-click → UI → Panel → Panel
   - Name: `InventoryPanel`
   - Position: x = -200, y = 0
   - Width: 350, Height: 600
3. **Add Component:** `InventoryUIPanel`
4. **Create child for list content:**
   - Select InventoryPanel
   - Right-click → UI → Vertical Layout Group
   - Name: `ItemList`
   - Add layout constrainer
5. **In InventoryUIPanel Inspector:**
   - **canvasGroup**: Drag self (the InventoryPanel)
   - **itemListLayout**: Drag the ItemList RectTransform
   - **itemEntryPrefab**: Create this next (see 5.2)

### 5.2 Create InventoryItemEntryUI Prefab

**Script Location:** `Assets/Scripts/Inventory/InventoryItemEntryUI.cs`

**Steps:**

1. **Create prefab structure:**
   - Create empty prefab: `Assets/Prefabs/InventoryItemEntry.prefab`
   - Or build in scene then drag to Assets

2. **Structure:**
   ```
   InventoryItemEntry (Horizontal Layout Group)
   ├── ItemIcon (Image)
   ├── ItemInfo (Vertical Layout Group)
   │   ├── ItemName (Text)
   │   └── ItemQuantity (Text)
   └── (Optional) SellButton (Button)
   ```

3. **Component Setup:**
   - Parent: Add `InventoryItemEntryUI` script
   - In Inspector:
     - **itemIcon**: Drag Image component
     - **itemNameText**: Drag ItemName Text
     - **itemQuantityText**: Drag ItemQuantity Text

4. **Back in InventoryUIPanel:**
   - Drag the prefab into **itemEntryPrefab** field

**Test:**
- Play scene
- Add items via code: `InventoryService.Instance.Add("copper_wire", 3);`
- UI should show "Copper Wire" and "x3"

### 5.3 Add BitsDisplayUI to Canvas

**Script Location:** `Assets/Scripts/UI/BitsDisplayUI.cs`

**Setup Steps:**

1. **Create UI Text element:**
   - Select UI_Canvas
   - Right-click → UI → Text - TextMeshPro
   - Name: `BitsDisplay`
   - Position: x = -100, y = -50 (top-right area)

2. **Add Component:** `BitsDisplayUI`

3. **In Inspector:**
   - **bitsLabel**: Drag the Text component
   - **showPrefix**: true
   - **prefix**: "Bits: "
   - **normalColor**: Color.white
   - **earnColor**: Color.green (flashes when earning)
   - **spendColor**: Color.red (flashes when spending)

**Test:**
- Play scene
- Earn bits: `CurrencySystem.Instance.Earn(6, "Test");`
- Display should update and flash green
- Spend bits: `CurrencySystem.Instance.Spend(2, "Test");`
- Display should flash red

---

## Phase 6: Dialogue Integration

### 6.1 Dialogue Conditions - Check Inventory

**In Dialogue JSON:**
```json
{
  "type": "condition",
  "conditions": [
    "InventoryService.Instance.Contains(\"copper_wire\", 2) == true"
  ],
  "beat_if_true": 10,
  "beat_if_false": 5
}
```

**In C# Dialogue Code:**
```csharp
public bool CheckInventory(string itemId, int quantity)
{
    return InventoryService.Instance.Contains(itemId, quantity);
}

// Usage in dialogue condition
if (CheckInventory("copper_wire", 2))
{
    // Show dialogue option: "Give Copper Wire to Willy"
}
```

### 6.2 Dialogue Action - Trade with NPC

**In Dialogue Code:**
```csharp
public void ExecuteNPCTrade(GameObject npcObj, string[] itemIds, int[] quantities)
{
    var npcTrader = npcObj.GetComponent<NPCTrader>();
    if (npcTrader == null)
    {
        Debug.LogError("NPC has no NPCTrader component");
        return;
    }

    // Build offer dictionary
    var offer = npcTrader.CreateTradeOffer(
        new Dictionary<string, int>
        {
            { itemIds[0], quantities[0] },
            { itemIds[1], quantities[1] }
            // etc.
        }
    );

    if (offer != null && npcTrader.ExecuteTrade(offer))
    {
        Debug.Log($"Earned {offer.totalBitsOffered} bits!");
        // Continue to next dialogue beat
    }
}
```

### 6.3 Dialogue Action - Remove Item

```csharp
public void RemoveItem(string itemId, int quantity)
{
    if (InventoryService.Instance.Remove(itemId, quantity))
    {
        Debug.Log($"Removed {quantity}x {itemId}");
        // Continue dialogue
    }
    else
    {
        Debug.LogWarning($"Failed to remove {quantity}x {itemId}");
        // Show error dialogue
    }
}
```

---

## Phase 7: Testing Checklist

### Quick Test Sequence

1. **InventoryService:**
   - [ ] Console: "InventoryService Initialized and marked persistent"
   - [ ] Console: "ItemDatabase Initialized with 5 items"
   - [ ] Add item: `InventoryService.Instance.Add("copper_wire", 3);`
   - [ ] Check: Inventory panel shows copper_wire × 3
   - [ ] Remove item: `InventoryService.Instance.Remove("copper_wire", 1);`
   - [ ] Check: UI updates to × 2

2. **CurrencySystem:**
   - [ ] Console shows initial bits loaded
   - [ ] Earn bits: `CurrencySystem.Instance.Earn(10, "Test");`
   - [ ] BitsDisplay updates and flashes green
   - [ ] Spend bits: `CurrencySystem.Instance.Spend(3, "Test");`
   - [ ] BitsDisplay updates and flashes red

3. **WorldItemPickup:**
   - [ ] Place copper_wire pickup in scene
   - [ ] Walk over it → Collected message in console
   - [ ] Inventory shows new item
   - [ ] Reload scene → Pickup gone (persisted)

4. **BreakableDebris:**
   - [ ] Place rock debris in scene
   - [ ] Try to break without tool → "Requires pickaxe" message
   - [ ] Add pickaxe to inventory manually
   - [ ] Break debris → Materials added, visual changes, persisted

5. **NPCTrader:**
   - [ ] Add NPCTrader to Willy
   - [ ] Assign WillyTradeProfile
   - [ ] Interact → Console: "NPC willy ready to trade"
   - [ ] Call CreateTradeOffer with test items
   - [ ] Check calculated bits value
   - [ ] ExecuteTrade → Bits added, items removed from inventory

6. **Full Flow:**
   - [ ] Start scene with 0 bits
   - [ ] Collect copper_wire pickup
   - [ ] Trade with Willy → Earn bits
   - [ ] BitsDisplay updates
   - [ ] PlayerPrefs persists (reload scene, bits remain)
   - [ ] Inventory persists (reload scene, no duplicates)

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "InventoryService is null" | Add InventoryService GameObject to scene with ItemDatabase assigned |
| "ItemDatabase is null" | Drag ItemDatabase.asset into InventoryService inspector field |
| "Unknown item ID" | Verify item exists in ItemDatabase list |
| Inventory UI not updating | Ensure InventoryUIPanel.itemListLayout is assigned |
| Bits not persisting | Verify CurrencySystem has DontDestroyOnLoad called (automatic in Awake) |
| Pickup respawns after reload | Verify pickupId is set and unique; check GameFlags implementation |
| NPCTrader shows 0 bits | Verify NPCTradeProfile is assigned and items have BaseValue > 0 |
| Tools not equipping | Verify tool item exists in inventory before calling EquipTool |

---

## File Structure Summary

```
Assets/
├── Resources/
│   └── Items/
│       ├── ItemDatabase.asset
│       ├── CopperWire.asset
│       ├── GlassFragments.asset
│       ├── SheetMetal.asset
│       ├── LightBulb.asset
│       └── ToolFragment.asset
├── ScriptableObjects/
│   └── Economy/
│       └── WillyTradeProfile.asset
├── Scripts/
│   ├── Inventory/
│   │   ├── ItemDefinition.cs
│   │   ├── ItemDatabase.cs
│   │   ├── InventoryService.cs (Singleton)
│   │   ├── InventoryUIPanel.cs
│   │   ├── InventoryItemEntryUI.cs
│   │   └── WorldItemPickup.cs
│   ├── Economy/
│   │   ├── CurrencySystem.cs (Singleton)
│   │   └── NPCTradeProfile.cs
│   ├── Interactions/
│   │   ├── NPCTrader.cs
│   │   ├── ToolSystem.cs (Singleton)
│   │   └── BreakableDebris.cs
│   └── UI/
│       └── BitsDisplayUI.cs
├── Prefabs/
│   ├── UI/
│   │   └── UI_Canvas.prefab (contains InventoryPanel, BitsDisplay)
│   └── InventoryItemEntry.prefab
└── Scenes/
    └── InsideMarket_02.unity (contains InventoryService, CurrencySystem, ToolSystem)
```

---

## Next Steps

After completing this setup:

1. **Expand Item Definitions**: Add tools, equipment, quest items
2. **Create NPC Profiles**: Tala, Ravi, etc. with different preferences
3. **Integrate Dialogue**: Wire inventory checks/trades into dialogue system
4. **Add Tool Mechanics**: Create tool effects (pickaxe breaks debris, etc.)
5. **Implement Durability**: (Optional) Add tool wear/repair system
6. **Trading Quests**: Create story beats around trading chains

---

**Status:** Ready to implement. Follow Phase 1-6 sequentially, test after each phase.
