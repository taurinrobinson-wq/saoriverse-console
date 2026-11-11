# Trading, Currency, and Tool System – Implementation Complete

## What Was Built

The complete foundation for Velinor's economy, including currency, NPC trading, tool mechanics, and persistent debris management.

### 1. CurrencySystem.cs (Economy folder)

**Purpose:** Tracks player currency ("Bits") across scenes with PlayerPrefs persistence.

**Key API:**
```csharp
CurrencySystem.Instance.Earn(6, "Traded with Willy");
bool canBuy = CurrencySystem.Instance.CanAfford(12);
CurrencySystem.Instance.Spend(12, "Tool recipe");
```

**Events:**
- `OnBitsEarned(amount, reason)` – When player gains bits
- `OnBitsSpent(amount, reason)` – When player loses bits
- `OnBitsChanged(totalAmount)` – Total balance changed

**Persistence:**
- Uses PlayerPrefs key: `velinor_bits_total`
- Auto-saves after every Earn/Spend
- Loads on Start()
- Can be reset with `ResetToInitial()`

---

### 2. NPCTradeProfile.cs (Economy folder)

**Purpose:** ScriptableObject defining what each NPC values and pays.

**Configuration:**
- NPC ID and display name
- Preferred item tags with multipliers (e.g., Electrical: 1.25x)
- Highly-sought specific items (e.g., copper_wire: 1.5x)
- Refused categories (items NPC won't buy)

**Price Calculation:**
```
offered_price = base_value × (specific_item_bonus OR tag_bonus OR default_multiplier)
```

**Example: Willy's Profile**
- Electrical: 1.25x
- copper_wire specifically: 1.5x
- Default: 1.0x

**To create:** Right-click in Assets → Create → Velinor/Economy/NPC Trade Profile

---

### 3. BreakableDebris.cs (Interactions folder)

**Purpose:** Debris that yields materials when broken with the right tool.

**Key Features:**
- Tool requirement (optional – can be free-to-break)
- Material rewards (multiple items/quantities)
- Visual feedback (intact white → cleared dim gray)
- Persistent state via GameFlags

**Persistence:**
```csharp
// Automatically checked on OnEnable()
GameFlags.Get("debris_cleared_{debrisId}", false)
// Automatically set on break
GameFlags.Set("debris_cleared_{debrisId}", true)
```

**Usage in scene:**
1. Add BreakableDebris component to GameObject
2. Configure:
   - Debris ID (unique identifier)
   - Required Tool ID (leave empty for free)
   - Materials Yielded (itemId + quantity list)
   - Visual settings (colors, collider reference)
   - Optional VFX/SFX

**Breaking flow:**
1. Player interacts
2. System checks tool requirement
3. If satisfied: play effects → add materials to inventory → mark cleared in GameFlags

---

### 4. ToolSystem.cs & ToolDefinition.cs (Interactions folder)

**ToolSystem:** Singleton managing equipped tools.

**Key API:**
```csharp
ToolSystem.Instance.HasTool("pry_bar");           // In inventory?
ToolSystem.Instance.EquipTool("pry_bar");         // Make active
ToolSystem.Instance.UnequipTool();                // Switch off
ToolSystem.Instance.IsToolEquipped("pry_bar");    // Currently active?
```

**Events:**
- `OnToolEquipped(toolId)` – Tool became active
- `OnToolUnequipped` – Tool deactivated

**ToolDefinition:** ScriptableObject (one per tool type).

**Configuration:**
- Tool ID and display name
- Can break debris types (list of debris types this tool affects)
- Visual settings (highlight color, intensity)
- Icon and description

**To create:** Right-click in Assets → Create → Velinor/Tools/Tool Definition

**Tool Lifecycle:**
1. Player learns recipe → pry_bar added to inventory
2. Player equips tool → ToolSystem.Instance.EquipTool("pry_bar")
3. Player interacts with sealed_panel
4. BreakableDebris checks: ToolSystem.Instance.HasTool("pry_bar") ✓
5. Debris breaks, materials added

---

### 5. NPCTrader.cs (Interactions folder)

**Purpose:** Handles NPC trade negotiations and exchanges.

**Key API:**
```csharp
var trader = npcGameObject.GetComponent<NPCTrader>();

// Step 1: Create offer
var itemsOffered = new Dictionary<string, int>
{
    { "copper_wire", 3 },
    { "motor_parts", 1 }
};
var offer = trader.CreateTradeOffer(itemsOffered);
// offer.totalBitsOffered = 18 bits

// Step 2: Execute trade
if (trader.ExecuteTrade(offer))
{
    // Items removed from inventory, Bits added to CurrencySystem
}
```

**Events:**
- `OnTradeOfferCreated(offer)` – Show trade UI
- `OnTradeAccepted(offer)` – Trade completed, show success
- `OnTradeCancelled` – Player declined

**How it works:**
1. Player selects items to trade
2. NPCTrader calculates price using NPC's TradeProfile
3. Shows offer to player
4. On accept: removes items, adds Bits via CurrencySystem

---

### 6. BitsDisplayUI.cs (UI folder)

**Purpose:** Simple UI to show current Bits balance.

**Features:**
- Auto-updates when balance changes
- Flash color on earn (green) / spend (red)
- Configurable prefix and colors
- Subscribes to CurrencySystem events

**Setup:**
1. Create TextMeshPro label on canvas
2. Add BitsDisplayUI component
3. Assign label reference
4. Configure colors/prefix as desired

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│ PLAYER INTERACTION FLOW                                 │
└─────────────────────────────────────────────────────────┘

COLLECT ITEMS
├─ WorldItemPickup (free) → Inventory
├─ BreakableDebris (no tool) → Inventory
└─ BreakableDebris (requires tool)
   └─ Requires ToolSystem.Instance.HasTool()
   └─ When satisfied → Inventory

LEARN TOOLS
├─ Dialogue system adds "pry_bar" to inventory
├─ InventoryService.Add("pry_bar", 1)
└─ ToolSystem.Instance.HasTool("pry_bar") → true

EQUIP TOOLS
├─ ToolSystem.Instance.EquipTool("pry_bar")
└─ EquippedTool = pry_bar definition

USE TOOLS
├─ Player interacts with sealed_panel
├─ BreakableDebris checks: ToolSystem.HasTool("pry_bar")
├─ Confirms: debris type in tool's breakable list
└─ Breaks → materials to inventory

TRADE ITEMS
├─ NPCTrader.CreateTradeOffer(itemsOffered)
├─ Price = base × NPC preference multiplier
├─ Show UI with offer
├─ Player accepts
├─ NPCTrader.ExecuteTrade()
│  ├─ Remove items from InventoryService
│  └─ Add bits to CurrencySystem
└─ Update UI display
```

## Key Design Decisions

### Why Bits Persist with PlayerPrefs, Not Full GameState
- For single-session play, PlayerPrefs is simpler
- If implementing full save/load, add Bits to GameState JSON alongside inventory
- Bits are *earned* from trades (not set directly), so save data can be simple

### Why BreakableDebris Uses GameFlags (Boolean), Not Inventory
- Debris state is binary (cleared or not)
- Using debris IDs prevents re-breaking without separate tracking
- Same pattern as item pickups – persists across scene transitions

### Why Tools Are Stored as Inventory Items
- Tools are "known" (in inventory) vs "equipped" (active)
- Same inventory system handles all stackable/unstackable items
- Recipe unlocks simply add tool to inventory
- Separates "do I know this tool?" from "am I using it right now?"

### Why NPCTrader Doesn't Hold Inventory
- Inventory is player's state (InventoryService)
- Trader queries inventory, removes items on trade
- Follows single-responsibility principle
- Makes NPC trading swappable (different trade profiles easily)

### Why Tool Requirements Are Strings (IDs), Not References
- Avoids hard dependencies between debris and tools
- String matching is resilient to prefab reorganization
- Enables data-driven design (no drag-and-drop setup required)

## What's Still Needed

### Phase A: UI & UX (1-2 hours)
1. **Trade UI Panel**
   - Show NPC's offer (items → Bits)
   - Accept/Decline buttons
   - Show Bits earned/lost preview
   
2. **Tool Equipping UI**
   - Inventory panel "Equip" button for tools
   - Visual indicator of equipped tool
   - Unequip option

3. **Debris Visual Feedback**
   - Glow effect for breakable (tool-locked) debris when player has tool
   - Different glow color vs free pickups
   - Highlight on hover

### Phase B: Willy Integration (2-3 hours)
1. **Second Encounter Dialogue**
   - willy_trading_encounter.json
   - Triggers trade UI when Willy notices player's items
   - Unlocks pry_bar recipe in system_triggers
   
2. **First Recipe: Pry Bar**
   - Create PryBar_ToolDef asset
   - Configure breakable debris types
   - Add to ToolSystem.availableTools

### Phase C: Testing & Polish (1-2 hours)
1. Full end-to-end testing
2. Edge cases (insufficient Bits, tool doesn't match debris, etc.)
3. Performance profiling (should be O(1) operations)

## File Locations

**Core System:**
- [x] `Assets/Scripts/Economy/CurrencySystem.cs` – Bits tracking
- [x] `Assets/Scripts/Economy/NPCTradeProfile.cs` – NPC preferences
- [x] `Assets/Scripts/Economy/TRADING_SYSTEM_GUIDE.md` – Full docs

**Interactions:**
- [x] `Assets/Scripts/Interactions/BreakableDebris.cs` – Tool-gated materials
- [x] `Assets/Scripts/Interactions/ToolSystem.cs` – Tool equipping
- [x] `Assets/Scripts/Interactions/NPCTrader.cs` – Trade negotiations

**UI:**
- [x] `Assets/Scripts/UI/BitsDisplayUI.cs` – Balance display

**Dependencies (Already Exist):**
- `Assets/Scripts/Inventory/InventoryService.cs` – Item management
- `Assets/Scripts/Core/GameFlags.cs` – Persistent state
- `Assets/Scripts/Interactions/WorldItemPickup.cs` – Free pickups

## Testing Checklist

### Unit Tests
- [ ] CurrencySystem.Earn() adds correct amount
- [ ] CurrencySystem.Spend() rejects insufficient funds
- [ ] CurrencySystem saves/loads correctly
- [ ] NPCTradeProfile.CalculateOfferedPrice() returns correct multiplier
- [ ] BreakableDebris.GameFlags persistence works
- [ ] ToolSystem.EquipTool() sets EquippedToolId

### Integration Tests
- [ ] Collect 3x copper_wire → trade with Willy → +18 bits
- [ ] Receive pry_bar recipe → can break sealed_panel
- [ ] Break sealed_panel → 2x motor_parts + 1x copper_wire to inventory
- [ ] Save game, close, reopen → Bits and debris state persist

### Edge Cases
- [ ] Try to trade items you don't have → offer creation succeeds but trade fails
- [ ] Try to break tool-locked debris without tool → interaction rejected
- [ ] Try to equip tool you don't have → HasTool() returns false
- [ ] NPC refuses category → CalculateOfferedPrice() returns 0

## Quick Start for Developers

### To Use CurrencySystem:
```csharp
CurrencySystem.Instance.Earn(10, "Sold copper wire");
if (CurrencySystem.Instance.CanAfford(5))
{
    CurrencySystem.Instance.Spend(5, "Bought water");
}
```

### To Use BreakableDebris:
```
1. Add BreakableDebris component to GameObject
2. Set debrisId = "unique_id_here"
3. Set requiredToolId = "pry_bar" (or empty)
4. Add materials to "Materials Yielded" list
5. Assign SpriteRenderer and Collider2D references
```

### To Use NPCTrader:
```csharp
var trader = npcGO.GetComponent<NPCTrader>();
var offer = trader.CreateTradeOffer(
    new() { { "copper_wire", 3 } }
);
trader.ExecuteTrade(offer);
```

### To Use ToolSystem:
```csharp
// Equip tool (player has learned recipe)
ToolSystem.Instance.EquipTool("pry_bar");

// Check if player can break specific debris
if (ToolSystem.Instance.HasTool("pry_bar"))
{
    debris.Interact(player); // Will succeed
}
```

## Performance Notes

- **CurrencySystem:** O(1) – single integer
- **NPCTradeProfile:** O(n) tags checked per item (n < 10 typical)
- **BreakableDebris:** O(m) materials added (m < 5 typical)
- **ToolSystem:** O(n) tools checked (n < 5 typical)
- **GameFlags persistence:** O(1) per debris

**Estimated memory footprint:**
- CurrencySystem: ~100 bytes
- Per NPC trader: ~500 bytes (profile + rules)
- Per debris: ~1 KB (state + materials)
- Per tool: ~200 bytes (definition)

No performance concerns for typical game scale.

## Architecture Diagram

```
       ┌──────────────────────────────────────────┐
       │      PLAYER INTERACTION (Willy Scene)    │
       └──────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
    Dialogue         Interaction      Tool Usage
    System           Handler          Handler
        │                 │                 │
        ├─────────────────┼─────────────────┤
        │                 │                 │
        ▼                 ▼                 ▼
   ╔════════════╗  ╔════════════╗  ╔════════════╗
   │  Dialogue  │  │ BreakableΦ │  │   ToolΦ   │
   │  Triggers  │  │   Debris   │  │   System   │
   ║════════════║  ║════════════║  ║════════════║
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                ┌─────────┴─────────┐
                │                   │
                ▼                   ▼
           ╔═════════════╗  ╔═════════════╗
           │ Inventory Φ │  │  GameFlagsΦ │
           ║═════════════║  ║═════════════║
           │   Add Item  │  │ Mark Debris │
           │             │  │   Cleared   │
           └─────────────┘  └─────────────┘
                │                   │
                └─────────┬─────────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
         ▼                ▼                ▼
    ╔═════════════╗ ╔════════════╗ ╔════════════╗
    │  CurrencyΦ  │ │NPCTraderΦ  │ │   Bits UI  │
    ║═════════════║ ║════════════║ ║════════════║
    │ OnBitsEarn  │ │ Trade Flow │ │  Display   │
    │ OnBitsSpent │ │            │ │   Balance  │
    └─────────────┘ └────────────┘ └────────────┘

Legend: Φ = Can be multiple instances
