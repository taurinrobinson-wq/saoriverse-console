# Velinor Inventory Architecture – Design Rationale

## Why This Approach?

Your game has unique needs that most "generic inventory" systems don't address:

1. **Salvage-focused gameplay** – Items matter because NPCs *want* them, not because you need them for quests
2. **NPC preferences** – Tala likes metal; someone else likes electrical components
3. **Simple, discoverable progression** – Listening matters; remembering matters
4. **No busy-work** – No durability; no weight; no inventory tetris

This system answers **one core question:**
> **What has Lioren found, what can she do with it, and who might care that she found it?**

---

## Component Roles

### ItemDefinition (Inspector-Editable)

**Role:** "What is this item?"

```csharp
public class ItemDefinition : ScriptableObject
{
    public string ItemId;           // copper_wire
    public string DisplayName;      // "Copper Wire"
    public string Description;      // "Flexible conductive material..."
    public Sprite Icon;
    public ItemCategory Category;   // Material, Tool, Food, etc.
    public ItemTag[] Tags;          // Metal, Electrical, etc.
    public int MaxStackSize = 99;
}
```

**Why ScriptableObject?**
- Reusable definitions; multiple copies of "copper wire" all reference same ItemDefinition
- Inspector-editable without code changes
- Stable across scene reloads
- Easy to add art (icon sprite) or description changes later

**Why not in InventoryService?**
- Separation of concerns: definitions ≠ state
- Multiple systems query items (UI, crafting, NPC dialogue) without needing the full inventory

---

### ItemDatabase (Singleton Asset)

**Role:** "Which items exist? Give me an item by ID."

```csharp
public class ItemDatabase : ScriptableObject
{
    private List<ItemDefinition> items;
    private Dictionary<string, ItemDefinition> lookup;  // O(1) by ID

    public ItemDefinition Get(string itemId);
    public bool Contains(string itemId);
}
```

**Why separate from InventoryService?**
- Database is **immutable** (doesn't change at runtime)
- InventoryService should only manage **state** (quantities)
- Crafting, NPC dialogue, and other systems query definitions without touching inventory
- Save/load only stores itemIds + quantities, not asset references
  - Load game → `InventoryService.LoadSaveData(itemIds)` → `ItemDatabase.Get(itemId)` → restore complete ItemDefinition

**Example: NPC Request Dialogue**
```csharp
// In dialogue code, NO dependency on inventory state:
List<ItemDefinition> electricalItems = itemDatabase.GetAll()
    .Where(x => x.HasTag(ItemTag.Electrical))
    .ToList();

foreach (var item in electricalItems)
{
    DialogueOption($"Give {item.DisplayName}?", () => {
        InventoryService.Instance.Remove(item.ItemId, 1);
    });
}
```

---

### InventoryService (DontDestroyOnLoad Singleton)

**Role:** "What does Lioren currently have?"

```csharp
public class InventoryService : MonoBehaviour
{
    private Dictionary<string, int> quantities;  // itemId → count

    public bool Add(string itemId, int amount = 1);
    public bool Remove(string itemId, int amount = 1);
    public int GetQuantity(string itemId);
    public Dictionary<string, int> GetAll();
}
```

**Why Dictionary instead of List?**
- Ten pieces of wire = `"copper_wire": 10`
- Not ten separate InventoryItem objects with individual metadata
- O(1) lookup, O(1) add/remove
- Simple serialization: save `List<(itemId, quantity)>`

**Why DontDestroyOnLoad singleton?**
- Inventory persists across scenes (player leaves market, goes to ruins, comes back with full inventory)
- No manual scene-to-scene passing
- Automatic cleanup if two InventoryServices try to exist (second is destroyed)

**Why NOT in a fixed singleton method?**
- Allows editor testing: can add/remove multiple InventoryServices and see which is used
- More compatible with scene loading patterns
- Easier to unit test

**Events for UI/Dialogue:**
```csharp
public event Action<string, int> OnInventoryChanged;  // (itemId, newQuantity)
public event Action OnInventoryCleared;

// Usage: UI panel subscribes and redraw on event
```

---

### WorldItemPickup (Per-Placed Item)

**Role:** "This is a collectible in the world."

```csharp
public class WorldItemPickup : MonoBehaviour, IInteractable
{
    public string pickupId;              // market_wire_01 (stable)
    public ItemDefinition itemDefinition;
    public int quantity = 1;

    public void Collect()
    {
        InventoryService.Instance.Add(itemDefinition.ItemId, quantity);
        GameFlags.Set($"pickup_collected_{pickupId}", true);
        gameObject.SetActive(false);
    }
}
```

**Two IDs, not one:**
- `itemId` = "copper_wire" (what it is) → goes to inventory
- `pickupId` = "market_wire_01" (where it was) → prevents respawn

**Why GameFlags?**
- Persistent state already exists in your codebase
- Pickup collected in market → scene reload → pickup is gone
- No need for a separate "collected items" list

---

### InventoryUIPanel (Left-Side UI)

**Role:** "Show what Lioren has."

**Design:**
- **Not a grid.** Simple vertical list of items
- **Not draggable.** Clicking shows description (placeholder for now)
- **Alpha visibility.** CanvasGroup.alpha 0 (hidden) → 1 (shown)
  - No destroy/instantiate; just toggle visibility
  - Smooth fade in/out optional
- **Real-time updates.** Subscribes to `InventoryService.OnInventoryChanged`

**Why this simple design?**
- Meaningful gameplay: Lioren finds things and remembers who wants them
- Not: random clicking to arrange inventory
- Categories could be added later if useful, but aren't needed for vertical slice

**Expected workflow:**
```
Player: "I found copper wire"
Lioren: "I'll keep this"
Panel shows: [Copper Wire] x3
Later: NPC "Do you have any electrical components?"
Lioren: [Opens inventory, sees Copper Wire tagged Electrical]
Lioren: "Yes, I have this"
```

---

### InventoryItemEntryUI (Row Component)

**Role:** "Display one item in the list."

- Shows: icon, name, quantity
- On click: could show details or availability-to-NPCs
- Placeholder for future tooltip/detail panel

---

## Why NOT Included (Yet)

### ❌ Durability
- Your instinct is correct: most players hate this
- Reserved for tools if/when tools behave differently
- Easy to add later if gameplay demands it

### ❌ Weight/Capacity
- Doesn't support "find cool salvage" gameplay
- Would need UI/UX for weight management
- Add only if you need resource scarcity

### ❌ Drag-and-Drop UI
- Adds complexity: swapping, empty slots, navigation
- Velinor doesn't need inventory organization
- Dynamic stacked list is simpler

### ❌ Item Rarity Tiers
- Don't drive Velinor's narrative
- All items have equal value: "Does someone want this?"

### ❌ Per-Item Instance State
- "This copper wire is different from that copper wire" – not needed yet
- 10× copper wire = `"copper_wire": 10` in dictionary, not 10 object instances
- Tools might need individual tracking later (acquired/used), but not now

---

## Save/Load

**Save:**
```csharp
// Get inventory data
List<InventoryEntryData> data = InventoryService.Instance.GetSaveData();
// Serialize to JSON/binary
SaveGameData.inventory = data;
```

**Load:**
```csharp
// Get data from save file
List<InventoryEntryData> data = LoadGameData().inventory;
// Restore via InventoryService
InventoryService.Instance.LoadSaveData(data);
// Each itemId resolves through ItemDatabase automatically
```

**Why this works:**
- ItemDatabase contains all possible items (doesn't change per-playthrough)
- Save file contains only `itemId` + `quantity` (small, stable)
- At load time, resolve itemIds to ItemDefinitions automatically
- Players can't "lose" items by renaming ItemDefinitions

---

## NPC Integration Example

### Tala likes metal items:

**In dialogue:**
```csharp
var metalItems = InventoryService.Instance.GetByTag(ItemTag.Metal);

if (metalItems.Count > 0)
{
    foreach (var kvp in metalItems)
    {
        ItemDefinition item = InventoryService.Instance.GetItemDefinition(kvp.Key);
        
        DialogueOption($"Give {item.DisplayName} to Tala?", () =>
        {
            InventoryService.Instance.Remove(kvp.Key, 1);
            TalaPreference.metalGivenCount++;
            UnlockDialogue("tala_reacts_to_metal");
        });
    }
}
else
{
    DialogueOption("I don't have any metal items for you.");
}
```

**No hard-coding of itemIds.** Tala's preference is `ItemTag.Metal`. Add 50 new metal items later; dialogue still works.

---

## Vertical Slice (This Implementation)

✅ **Included:**
- ItemDefinition (5 fields: name, icon, category, tags, stack size)
- ItemDatabase (lookup, no-duplicate detection)
- InventoryService (Add, Remove, GetQuantity, GetAll, GetByTag)
- WorldItemPickup (scene collectibles with persistent tracking)
- InventoryUIPanel (simple list, alpha visibility)
- Save/Load support (itemId + quantity)

❓ **Next Phase (When Needed):**
- Tool durability or condition tracking
- Crafting system (query inventory for ingredients)
- Storage chests or multiple inventories
- Item-specific animations or lore unlocks
- Detailed item inspector panel

---

## Design Principles

1. **Keep definitions and state separate**
   - ItemDefinition = what it is (immutable)
   - InventoryService = what Lioren has (mutable)
   - Don't store ItemDefinition references in saves

2. **Avoid hard-coded relationships**
   - Use tags for NPC preferences
   - Dialogue queries by tag, not by itemId

3. **Simple UI, meaningful gameplay**
   - List, not grid
   - No optimization games (weight, durability)
   - Inventory is a *tool for storytelling*, not a *minigame*

4. **Persist collection state separately**
   - pickupId in GameFlags (not in inventory data)
   - Prevents items from respawning when you reload

5. **Lazy initialization**
   - ItemDatabase lookup builds once on first Get()
   - InventoryService finds itself via singleton pattern
   - No redundant loading

---

**This design scales from 4 items to 100+ without code changes. Add items, add tags, connect to dialogue. Done.**
