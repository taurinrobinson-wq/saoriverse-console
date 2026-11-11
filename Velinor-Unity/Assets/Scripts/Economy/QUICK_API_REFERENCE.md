# Trading System – Quick API Reference

## Fast Lookup Guide

All trading, currency, and tool systems ready for integration.

---

## CurrencySystem – Player Economy

**File:** `Assets/Scripts/Economy/CurrencySystem.cs`

### Basic Usage
```csharp
// Earn Bits from trade
CurrencySystem.Instance.Earn(6, "Traded with Willy");

// Spend Bits on purchase
if (CurrencySystem.Instance.CanAfford(12))
{
    CurrencySystem.Instance.Spend(12, "Purchased tool recipe");
}

// Check balance
int balance = CurrencySystem.Instance.CurrentBits;
Debug.Log($"You have {balance} bits");
```

### Events
```csharp
CurrencySystem.Instance.OnBitsEarned += (amount, reason) =>
{
    Debug.Log($"+{amount} bits ({reason})");
    // Show "+6 bits" popup
};

CurrencySystem.Instance.OnBitsSpent += (amount, reason) =>
{
    Debug.Log($"-{amount} bits ({reason})");
};

CurrencySystem.Instance.OnBitsChanged += (total) =>
{
    bitsLabel.text = $"Bits: {total}";
};
```

### Save/Load
```csharp
// Auto-saves to PlayerPrefs after Earn/Spend
// Auto-loads from PlayerPrefs on Start()

// Manual reset (testing)
CurrencySystem.Instance.ResetToInitial();
```

---

## NPCTradeProfile – NPC Preferences

**File:** `Assets/Scripts/Economy/NPCTradeProfile.cs`

### ScriptableObject
Create in Editor: Right-click → Create → Velinor/Economy/NPC Trade Profile

### Configuration Example: Willy
```yaml
NPC ID: willy
Display Name: Willy

Preferred Tags:
  - Electrical: 1.25
  - Mechanical: 1.25
  - Salvage: 1.10

Highly Sought Items:
  - copper_wire: 1.5
  - motor_parts: 1.3

Default Multiplier: 1.0
```

### Calculate Price
```csharp
var profile = willy_TradeProfile; // Assigned in editor
var itemDef = itemDB.Get("copper_wire");

// Calculate: 4 (base) × 1.5 (specific) = 6 bits
int offerPrice = profile.CalculateOfferedPrice(itemDef, 4);
Debug.Log($"Willy offers {offerPrice} bits for copper wire");
```

---

## ToolSystem – Tool Equipping

**File:** `Assets/Scripts/Interactions/ToolSystem.cs`

### Basic Usage
```csharp
// Check if player knows the tool (has it in inventory)
bool canUse = ToolSystem.Instance.HasTool("pry_bar");

if (canUse)
{
    // Make it the active tool
    ToolSystem.Instance.EquipTool("pry_bar");
    
    // Check if it's active
    bool isActive = ToolSystem.Instance.IsToolEquipped("pry_bar");
}

// Switch back to bare hands
ToolSystem.Instance.UnequipTool();
```

### Get Equipped Tool Info
```csharp
var tool = ToolSystem.Instance.EquippedTool;
if (tool != null)
{
    Debug.Log($"Equipped: {tool.DisplayName}");
    Debug.Log($"Can break: {string.Join(", ", tool.CanBreakDebrisTypes)}");
    
    // Use in UI
    toolIcon.sprite = tool.Icon;
    toolName.text = tool.DisplayName;
}
```

### Events
```csharp
ToolSystem.Instance.OnToolEquipped += (toolId) =>
{
    Debug.Log($"Equipped {toolId}");
    // Show visual indicator, highlight breakable debris
};

ToolSystem.Instance.OnToolUnequipped += () =>
{
    Debug.Log("Tool unequipped");
    // Hide visual indicator, remove debris highlights
};
```

---

## ToolDefinition – Tool Definitions

**File:** `Assets/Scripts/Interactions/ToolSystem.cs`

### ScriptableObject
Create in Editor: Right-click → Create → Velinor/Tools/Tool Definition

### Configuration Example: Pry Bar
```yaml
Tool ID: pry_bar
Display Name: Pry Bar
Description: A salvager's trusty pry bar...

Can Break Debris Types:
  - sealed_panel
  - rusted_bolt
  - lodged_components

Equip Highlight Color: Yellow
Highlight Intensity: 1.2
Icon: (sprite)
```

### Usage
```csharp
var toolDef = ToolSystem.Instance.EquippedTool;

// Check what this tool can break
if (toolDef.CanBreak("sealed_panel"))
{
    Debug.Log("This tool can break sealed panels!");
}
```

---

## BreakableDebris – Breakable Materials

**File:** `Assets/Scripts/Interactions/BreakableDebris.cs`

### Scene Setup
1. Create GameObject with SpriteRenderer + Collider2D
2. Add BreakableDebris component
3. Configure in Inspector:
   - Debris ID: unique identifier
   - Required Tool ID: (empty = free to break, or "pry_bar")
   - Materials Yielded: list of items and quantities
   - Visual settings: colors, collider reference

### Programmatic Usage
```csharp
var debris = GetComponent<BreakableDebris>();

// Check if cleared
if (debris.IsCleared)
{
    Debug.Log("This debris was already broken");
}

// Check requirements
if (debris.RequiresTool)
{
    Debug.Log($"Requires: {debris.RequiredToolId}");
}

// Restore state after load (auto-done in OnEnable)
GameFlags.Get($"debris_cleared_{debris.DebrisId}", false);
```

### Player Interaction (Auto-handled)
```csharp
// When player interacts (via raycast → Interact(player))
// BreakableDebris automatically:
// 1. Checks tool requirement
// 2. Plays VFX/SFX
// 3. Adds materials to inventory
// 4. Marks cleared in GameFlags
// 5. Updates visuals
```

---

## NPCTrader – Trade Negotiations

**File:** `Assets/Scripts/Interactions/NPCTrader.cs`

### Scene Setup
1. Add NPCTrader component to NPC GameObject
2. Configure in Inspector:
   - NPC ID: matches NPC system
   - Trade Profile: assigned NPCTradeProfile asset

### Create Trade Offer
```csharp
var trader = willysGameObject.GetComponent<NPCTrader>();

var itemsOffered = new Dictionary<string, int>
{
    { "copper_wire", 3 },
    { "motor_parts", 1 }
};

var offer = trader.CreateTradeOffer(itemsOffered);

// Show to player
Debug.Log(offer.ToString());
// "Trade Offer from Willy:
//   copper_wire x3
//   motor_parts x1
//   Total: 18 bits"
```

### Execute Trade
```csharp
if (trader.ExecuteTrade(offer))
{
    Debug.Log("Trade successful!");
    // InventoryService: items removed
    // CurrencySystem: +18 bits added
}
else
{
    Debug.Log("Trade failed (insufficient items?)");
}
```

### Events
```csharp
trader.OnTradeOfferCreated += (offer) =>
{
    // Show trade UI panel
    tradePanel.Show(offer);
};

trader.OnTradeAccepted += (offer) =>
{
    // Play success sound/animation
    successEffect.Play();
};

trader.OnTradeCancelled += () =>
{
    // Close trade UI
    tradePanel.Hide();
};
```

---

## BitsDisplayUI – Balance Display

**File:** `Assets/Scripts/UI/BitsDisplayUI.cs`

### Scene Setup
1. Create TextMeshPro label on Canvas
2. Add BitsDisplayUI component
3. Configure in Inspector:
   - Bits Label: TextMeshPro reference
   - Show Prefix: true
   - Prefix: "Bits: "
   - Normal/Earn/Spend colors

### Auto-Updates
```csharp
// Automatically subscribes to CurrencySystem events
// Updates text when balance changes
// Flashes green on earn, red on spend
// No additional code needed!
```

---

## Integration Patterns

### Pattern 1: Collecting & Trading
```csharp
// Player collects items
InventoryService.Instance.Add("copper_wire", 3);

// Later, trades with NPC
var offer = npcTrader.CreateTradeOffer(
    new() { { "copper_wire", 3 } }
);
// offer.totalBitsOffered = 18

npcTrader.ExecuteTrade(offer);
// copper_wire -3, bits +18
```

### Pattern 2: Learning & Using Tools
```csharp
// From dialogue: player learns pry bar recipe
InventoryService.Instance.Add("pry_bar", 1);

// Player equips tool
ToolSystem.Instance.EquipTool("pry_bar");

// Player interacts with sealed panel
breakableDebris.Interact(player);  // ToolSystem checks HasTool internally
// Panel breaks if has tool, adds materials to inventory
```

### Pattern 3: Persistent State
```csharp
// Break debris in scene
breakableDebris.Interact(player);
// Automatically sets: GameFlags.Set("debris_cleared_X", true)

// Exit scene, return later
// OnEnable checks GameFlags and restores cleared state

// Close game, reopen
// GameFlags persists via InventoryService/save system
// Debris still cleared!
```

---

## Common Dialogue Integration

### Beat 2: Inventory Unlock (Willy Scenario)
```json
{
  "beat_id": 2,
  "npc_prompt": "That metal could be useful to someone like me.",
  "system_triggers": [
    {
      "type": "unlock_system",
      "data": ["inventory"]
    },
    {
      "type": "unlock_npc_preference",
      "data": ["Willy", "copper_wire", "motor_parts"]
    }
  ]
}
```

### Beat 3+: Trading Encounter
```json
{
  "beat_id": 3,
  "npc_prompt": "Hold on, that wire you're carrying... you using that?",
  "system_triggers": [
    {
      "type": "start_npc_trade",
      "data": ["willy"]
    }
  ]
}
```

### Recipe Unlock
```json
{
  "beat_id": 4,
  "npc_prompt": "Tell you what, I'll teach you how to build a pry bar.",
  "system_triggers": [
    {
      "type": "inventory_add",
      "data": ["pry_bar", "1"]
    },
    {
      "type": "system_notification",
      "data": ["Learned: Pry Bar"]
    }
  ]
}
```

---

## Testing Commands

### Console Debugging
```csharp
// Check bits
Debug.Log(CurrencySystem.Instance.CurrentBits);

// Earn bits
CurrencySystem.Instance.Earn(100, "Debug");

// Check inventory
var inv = InventoryService.Instance;
Debug.Log(inv.GetQuantity("copper_wire"));

// Check tool
Debug.Log(ToolSystem.Instance.EquippedToolId);

// Check debris
var debris = GetComponent<BreakableDebris>();
Debug.Log(debris.IsCleared);

// Check GameFlags
Debug.Log(GameFlags.Get("debris_cleared_X", false));
```

---

## Performance Checklist

✓ CurrencySystem: O(1) – single integer  
✓ NPCTradeProfile: O(n) – tags (typically < 10)  
✓ BreakableDebris: O(m) – materials (typically < 5)  
✓ ToolSystem: O(n) – tools (typically < 5)  
✓ GameFlags: O(1) – static dictionary  

No performance bottlenecks expected.

---

## Next Steps

1. **Create GameManager with EconomyManager & ToolSystemManager**
2. **Create Willy_TradeProfile asset**
3. **Create PryBar_ToolDef asset**
4. **Set up debris in Willy scene**
5. **Create willy_trading_encounter.json dialogue**
6. **Test full end-to-end flow**
7. **Integrate into game save system (optional)**

---

## Questions?

Refer to:
- `TRADING_SYSTEM_GUIDE.md` – Full architecture & decisions
- `SETUP_CHECKLIST.md` – Step-by-step setup
- `IMPLEMENTATION_SUMMARY.md` – Overview & context
