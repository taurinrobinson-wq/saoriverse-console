# System Architecture & Data Flow

## High-Level Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PLAYER INTERACTION                          │
└──────────────┬──────────────────────────────────────────────────────┘
               │
        ┌──────┴──────┬──────────────┬──────────────┐
        │             │              │              │
        ▼             ▼              ▼              ▼
   [E: Pickup]  [E: Break Rock] [E: Trade]  [I: Inventory]
        │             │              │              │
        ▼             ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌────────────┐ ┌──────────────┐
│WorldItemPickup│ │BreakableDebris│ │NPCTrader │ │InventoryUI  │
│   (Collect)   │ │  (Mine/Break) │ │ (Trade)  │ │  (Display)  │
└──────────────┘ └──────────────┘ └────────────┘ └──────────────┘
        │             │              │              │
        └─────────────┴──────────────┴──────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │  InventoryService (Core)    │
        │  Dictionary<id, quantity>   │
        │  Fires: OnInventoryChanged  │
        └─────────────────────────────┘
                      │
                      │ Uses:
        ┌─────────────┴──────────────┐
        │                            │
        ▼                            ▼
┌─────────────────────────┐   ┌──────────────┐
│  ItemDatabase.asset     │   │ GameFlags    │
│  (Scriptable Objects)   │   │ (Persistence)│
│  - ItemDefinition[5]    │   │              │
│  - Lookup by itemId     │   │ pickup_XX    │
└─────────────────────────┘   │ debris_XX    │
                               └──────────────┘

        ┌────────────────────────────────────────┐
        │ PARALLEL SYSTEMS (Independent)         │
        │                                        │
        │  ┌──────────────────────────────────┐  │
        │  │   CurrencySystem (Singleton)     │  │
        │  │   - CurrentBits (PlayerPrefs)    │  │
        │  │   - OnBitsEarned/Spent events    │  │
        │  └──────────────────────────────────┘  │
        │                                        │
        │  ┌──────────────────────────────────┐  │
        │  │   ToolSystem (Singleton)         │  │
        │  │   - EquippedToolId tracking      │  │
        │  │   - Checks inventory for tools   │  │
        │  └──────────────────────────────────┘  │
        │                                        │
        └────────────────────────────────────────┘
                      │
                      │ UI Updates:
        ┌─────────────┴──────────────┐
        │                            │
        ▼                            ▼
┌──────────────────────┐  ┌──────────────────────┐
│  BitsDisplayUI       │  │ InventoryUIPanel     │
│  Top-right corner    │  │ Left side panel      │
│  Shows: "Bits: 42"   │  │ Lists all items      │
└──────────────────────┘  └──────────────────────┘
```

---

## State & Persistence Layer

```
RUNTIME STATE (Memory)
─────────────────────────────────────────────────────

InventoryService.Instance
├── quantities: Dictionary<string, int>
│   ├── copper_wire: 3
│   ├── glass_fragments: 1
│   └── sheet_metal: 2
└── Events:
    └── OnInventoryChanged (fired on Add/Remove)

CurrencySystem.Instance
├── currentBits: 42
└── Events:
    ├── OnBitsEarned
    ├── OnBitsSpent
    └── OnBitsChanged

ToolSystem.Instance
├── equippedToolId: "pickaxe"
├── equippedToolDefinition: ToolDefinition
└── Events:
    ├── OnToolEquipped
    └── OnToolUnequipped


PERSISTENT STATE (PlayerPrefs + GameFlags)
─────────────────────────────────────────────────────

PlayerPrefs:
  velinor_bits_total: "42"     ← CurrencySystem reads/writes

GameFlags (Internal Dictionary):
  pickup_collected_copper_wire_market_01: true
  debris_cleared_rock_debris_market_01: true
  [Other game state flags...]


STATIC DATA (Asset/Scriptable Objects)
─────────────────────────────────────────────────────

ItemDatabase.asset
├── items: ItemDefinition[]
│   ├── ItemDefinition (copper_wire)
│   │   ├── itemId: "copper_wire"
│   │   ├── displayName: "Copper Wire"
│   │   ├── tags: ["Metal", "Electrical"]
│   │   ├── baseValue: 2
│   │   └── maxStackSize: 99
│   ├── ItemDefinition (glass_fragments)
│   ├── ItemDefinition (sheet_metal)
│   ├── ItemDefinition (light_bulb)
│   └── ItemDefinition (tool_fragment)

NPCTradeProfile.asset (Willy)
├── npcId: "willy"
├── displayName: "Willy"
├── preferredTags:
│   ├── "Electrical": 1.25
│   └── "Mechanical": 1.25
├── highlySoughtItems:
│   ├── "copper_wire": 1.5
│   └── "sheet_metal": 1.3
└── defaultMultiplier: 1.0
```

---

## Trade Calculation Example

```
PLAYER OFFERS:
  2x copper_wire (BaseValue: 2 each)
  1x glass_fragments (BaseValue: 1 each)

WILLY'S PREFERENCES:
  - Highly seeks copper_wire: 1.5x
  - Default multiplier: 1.0x

CALCULATION:
  copper_wire:
    base_value: 2
    multiplier: 1.5 (highly sought)
    price_per_unit: 2 × 1.5 = 3
    total: 3 × 2 = 6 bits
  
  glass_fragments:
    base_value: 1
    multiplier: 1.0 (default, no preference)
    price_per_unit: 1 × 1.0 = 1
    total: 1 × 1 = 1 bit
  
  TOTAL OFFER: 7 bits

AFTER TRADE:
  Inventory: -2 copper_wire, -1 glass_fragments
  Currency: +7 bits
  Events: OnBitsEarned(7, "Traded with Willy")
```

---

## Dialogue Integration Points

```
DIALOGUE BEAT FLOW:

┌─────────────────────┐
│  Display Dialogue   │
│  "Want to trade?"   │
└────────┬────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Check Condition                │
│  Has player 2x copper_wire?     │
│  InventoryService.Contains()    │
└────────┬────────────┬───────────┘
         │ YES        │ NO
         ▼            ▼
    [Trade]      [Alt Dialogue]
         │            │
         ▼            └─────┐
┌──────────────────┐        │
│  Show Options:   │        │
│  Give items? (Y/N)        │
└────────┬────────┘        │
         │                  │
         ▼                  │
┌──────────────────────────┐│
│  Player Accepts (Y)      ││
│  NPCTrader.ExecuteTrade()││
│  - Remove items          ││
│  - Award bits            ││
│  - Fire OnTradeAccepted  ││
│  - Continue dialogue     ││
└──────────────────────────┘│
         │                  │
         └──────┬───────────┘
                │
                ▼
        ┌─────────────────┐
        │  Next Beat...   │
        └─────────────────┘
```

---

## Singleton Initialization Sequence

```
SCENE LOAD:
1. InventoryService.Awake()
   ├── Singleton check
   ├── Load ItemDatabase reference
   ├── Mark DontDestroyOnLoad
   └── Log: "[InventoryService] Initialized and marked persistent"

2. CurrencySystem.Awake()
   ├── Singleton check
   ├── Mark DontDestroyOnLoad
   └── CurrencySystem.Start()
       └── LoadBits() from PlayerPrefs

3. ToolSystem.Awake()
   ├── Singleton check
   ├── Mark DontDestroyOnLoad
   └── Ready to track equipped tool

4. UI Elements.OnEnable()
   ├── InventoryUIPanel subscribes to InventoryService.OnInventoryChanged
   ├── BitsDisplayUI subscribes to CurrencySystem.OnBitsChanged
   └── Both listen for updates


SCENE-TO-SCENE TRANSITION:
- InventoryService persists (DontDestroyOnLoad)
- CurrencySystem persists (DontDestroyOnLoad)
- ToolSystem persists (DontDestroyOnLoad)
- PlayerPrefs automatically synced
- GameFlags state maintained
- UI elements recreated/reconnected in new scene
```

---

## Event Subscription Pattern

```
SUBSCRIBING TO EVENTS:

// InventoryService events
InventoryService.Instance.OnInventoryChanged += (itemId, quantity) =>
{
    Debug.Log($"Inventory changed: {itemId} = {quantity}");
    // Update UI, trigger animations, etc.
};

// CurrencySystem events
CurrencySystem.Instance.OnBitsEarned += (amount, reason) =>
{
    Debug.Log($"+{amount} bits ({reason})");
    // Flash UI, play sound, etc.
};

CurrencySystem.Instance.OnBitsSpent += (amount, reason) =>
{
    Debug.Log($"-{amount} bits ({reason})");
    // Flash red, play debit sound, etc.
};

CurrencySystem.Instance.OnBitsChanged += (total) =>
{
    bitsLabel.text = $"Bits: {total}";
};

// ToolSystem events
ToolSystem.Instance.OnToolEquipped += (toolId) =>
{
    Debug.Log($"Equipped: {toolId}");
    // Update tool sprite, enable tool-specific interactions, etc.
};

ToolSystem.Instance.OnToolUnequipped += () =>
{
    Debug.Log("Tool unequipped");
};


UNSUBSCRIBING (OnDisable):

private void OnDisable()
{
    if (InventoryService.Instance != null)
        InventoryService.Instance.OnInventoryChanged -= OnInventoryChanged;
    
    if (CurrencySystem.Instance != null)
    {
        CurrencySystem.Instance.OnBitsChanged -= OnBitsChanged;
        CurrencySystem.Instance.OnBitsEarned -= OnBitsEarned;
        CurrencySystem.Instance.OnBitsSpent -= OnBitsSpent;
    }
}
```

---

## Dependency Graph

```
UI LAYER:
├── InventoryUIPanel (reads InventoryService)
├── InventoryItemEntryUI (displays ItemDefinition data)
├── BitsDisplayUI (reads CurrencySystem)
└── (Future) ToolStatusUI (reads ToolSystem)

INTERACTION LAYER:
├── WorldItemPickup
│   ├── Reads: ItemDatabase (via InventoryService)
│   ├── Writes: InventoryService.Add()
│   └── Persists: GameFlags
├── BreakableDebris
│   ├── Reads: ToolSystem (check equipped)
│   ├── Writes: InventoryService.Add()
│   └── Persists: GameFlags
└── NPCTrader
    ├── Reads: NPCTradeProfile, ItemDatabase
    ├── Writes: InventoryService.Remove(), CurrencySystem.Earn()
    └── Events: OnTradeAccepted

DIALOGUE INTEGRATION:
├── Condition: InventoryService.Contains()
├── Action: InventoryService.Remove()
├── Action: CurrencySystem.Earn()
└── Event Hook: OnTradeAccepted → Next dialogue beat

PERSISTENCE LAYER:
├── InventoryService → (Uses GameFlags internally)
├── CurrencySystem → PlayerPrefs["velinor_bits_total"]
├── WorldItemPickup → GameFlags["pickup_collected_*"]
└── BreakableDebris → GameFlags["debris_cleared_*"]

CORE SERVICES:
├── InventoryService (Singleton)
│   ├── ItemDatabase (ScriptableObject)
│   └── Dictionary<string, int>
├── CurrencySystem (Singleton)
│   └── PlayerPrefs persistence
├── ToolSystem (Singleton)
│   └── ToolDefinition list
└── GameFlags (Singleton)
    └── Dialogue system persistence
```

---

## Common Workflow Examples

### Workflow 1: Collect Item

```csharp
// 1. Player walks over WorldItemPickup (copper_wire_01)
// 2. Collider trigger/E key fires Interact()
// 3. WorldItemPickup.Collect() called:

public void Collect()
{
    // Add to inventory
    if (InventoryService.Instance.Add(itemDefinition.ItemId, quantity))
    {
        // Mark collected in persistent state
        GameFlags.Set($"pickup_collected_{pickupId}", true);
        // Hide from world
        gameObject.SetActive(false);
        // Fire event (UI listens)
        // OnInventoryChanged triggers InventoryUIPanel update
    }
}

// RESULT:
// - Inventory: copper_wire += 3
// - GameFlags: pickup_collected_copper_wire_01 = true
// - UI: Shows "Copper Wire x3"
```

### Workflow 2: Trade with NPC

```csharp
// 1. Dialogue option: "Trade copper wire to Willy"
// 2. Player accepts
// 3. NPCTrader.ExecuteTrade() called:

public bool ExecuteTrade(NPCTradeOffer offer)
{
    var inventory = InventoryService.Instance;
    var currency = CurrencySystem.Instance;
    
    // Verify player still has items
    foreach (var kvp in offer.offeredItems)
    {
        if (!inventory.Contains(kvp.Key, kvp.Value))
        {
            Debug.LogWarning("Player no longer has items");
            return false;
        }
    }
    
    // Remove items
    foreach (var kvp in offer.offeredItems)
    {
        inventory.Remove(kvp.Key, kvp.Value);
        // OnInventoryChanged fires → UI updates
    }
    
    // Award Bits
    currency.Earn(offer.totalBitsOffered, $"Traded with {offer.npcDisplayName}");
    // OnBitsEarned fires → BitsDisplayUI flashes
    
    // Fire events
    OnTradeAccepted?.Invoke(offer);
    
    return true;
}

// RESULT:
// - Inventory: copper_wire -= 2
// - Currency: Bits += 6
// - UI: Updates inventory and bits display
// - Dialogue: Continue to next beat
```

### Workflow 3: Check & Break Debris

```csharp
// 1. Player approaches rock debris
// 2. ToolSystem has equipped pickaxe
// 3. Player presses E to interact
// 4. BreakableDebris.Interact() called:

public void Interact(GameObject player)
{
    if (isCleared) return;
    
    // Check if tool required
    if (!string.IsNullOrEmpty(requiredToolId))
    {
        var toolSystem = ToolSystem.Instance;
        if (!toolSystem.HasTool(requiredToolId))
        {
            Debug.Log($"Requires {requiredToolId}");
            return; // Show UI error message
        }
    }
    
    BreakDebris();
}

public void BreakDebris()
{
    // Play VFX
    Instantiate(breakEffectPrefab, transform.position, Quaternion.identity);
    
    // Add materials to inventory
    var inventory = InventoryService.Instance;
    foreach (var material in materials)
    {
        inventory.Add(material.itemId, material.quantity);
        // OnInventoryChanged fires × 2 → UI updates
    }
    
    // Mark cleared
    isCleared = true;
    GameFlags.Set(clearedFlagKey, true);
    
    // Update visuals
    spriteRenderer.color = brokenColor;
    debrisCollider.enabled = false;
}

// RESULT:
// - Inventory: sheet_metal += 2, glass_fragments += 1
// - GameFlags: debris_cleared_rock_debris_01 = true
// - UI: Shows new items
// - Scene: Debris grayed out and uninteractable
// - Persistence: Debris remains broken after reload
```

---

## Performance Considerations

```
INVENTORY CHECKS (O(1) via Dictionary):
- InventoryService.Contains("copper_wire", 2) → Fast
- InventoryService.Get("copper_wire") → Fast

ITEM LOOKUPS (O(1) via ItemDatabase lookup):
- ItemDatabase.Get("copper_wire") → Fast
- Built-in dictionary caching

NPC TRADE CALCULATION:
- Loop through offered items (typically 2-5 items)
- O(n) where n = items offered (acceptable)
- Done only once per trade (not every frame)

UI UPDATES:
- OnInventoryChanged fired per item change
- InventoryUIPanel rebuilds list (lazy refresh)
- Can optimize with incremental updates if needed

PERSISTENCE:
- PlayerPrefs write on Earn/Spend (minimal)
- GameFlags write on pickup/debris clear (minimal)
- No per-frame overhead

OVERALL: No performance bottlenecks at current scale
```

---

**Architecture Status:** Ready for implementation and integration with dialogue system.
