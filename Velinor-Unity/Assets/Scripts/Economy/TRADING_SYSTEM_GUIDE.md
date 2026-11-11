# Trading, Currency, and Tool System – Implementation Guide

## Overview

This system enables the complete gameplay loop: collect items → trade with NPCs → earn Bits (abstract currency) → learn tools → use tools on debris → collect more materials.

**Key Principle:** Bits are simple, abstract money. The interesting economy comes from *who values what*, not from currency simulation.

**Key Components:**
- `CurrencySystem.cs` – Tracks Bits as a simple integer
- `NPCTradeProfile.cs` – Defines what each NPC values and pays (preference-driven, not simulation)
- `BreakableDebris.cs` – Debris that yields materials when broken with tools
- `ToolSystem.cs` & `ToolDefinition.cs` – Equip/unequip tools, check requirements
- `NPCTrader.cs` – Handle trade negotiations and exchanges

## What Are Bits?

From Willy's dialogue:

> **Willy:** "Got any bits?"
> 
> **Lioren:** "Bits?"
> 
> **Willy:** "Yeah. Bits. Money. You seriously got nothin'?"

That's the complete explanation. Bits are:
- The unit of exchange in the marketplace
- What NPCs accept in payment
- How Lioren earns money through salvage and work

Bits are NOT:
- Physical coins with denominations
- Tied to any historical origin
- Subject to inflation, supply chains, or banking systems
- Something the game ever explains in detail

**See [BITS_PHILOSOPHY.md](BITS_PHILOSOPHY.md) for the full design rationale.**

---

## Architecture Decisions

### 1. Currency System (Simple, Persistent Integer)

```csharp
CurrencySystem.Instance.Earn(6, "Traded with Willy");
bool canBuy = CurrencySystem.Instance.CanAfford(12);
CurrencySystem.Instance.Spend(12, "Purchased item");
```

**Key features:**
- DontDestroyOnLoad singleton (persists across scenes)
- PlayerPrefs-backed save/load (survives game restart)
- Event-driven (`OnBitsEarned`, `OnBitsSpent`, `OnBitsChanged`)
- Includes reason tracking for player feedback
- One data type: `int bits`

**Why this design:**
- Bits don't occupy inventory slots
- No denomination tracking
- No "find coins" pickups
- Bits come from trading, not looting

### 2. NPC Trade Profiles (Preference-Driven, Not Economics)

Each NPC has a `NPCTradeProfile` that defines:
- Base multipliers for ItemTags (e.g., Willy pays 1.25x for Electrical items because he's a scrapper)
- Specific item multipliers (e.g., Willy pays 1.5x for copper_wire specifically)
- Refused categories (items the NPC won't buy at all)
- Display name and NPC ID

**This is NOT objective item value.**

Same copper wire:
- **Willy:** 6 bits (he wants electrical salvage)
- **Tala:** 2 bits (she's a cook, not useful to her)
- **Random stranger:** 4 bits (neutral rate)

**Price calculation:**
```
offered_price = base_value × (specific_item_multiplier OR tag_multiplier OR default_multiplier)
```

**Example: Willy's Profile**
```yaml
Willy Trade Profile
  Preferred Tags:
    - Electrical: 1.25x
    - Mechanical: 1.25x
    - Salvage: 1.10x
  Highly Sought Items:
    - copper_wire: 1.5x
    - motor_parts: 1.3x
    - old_circuitry: 1.2x
  Refused Categories: (none)
  Default Multiplier: 1.0x
```

**Why this design:**
- Multipliers express NPC personality and needs
- Same item can mean different things to different people
- No need for global "item values" list
- Extensible to new NPCs without changing existing prices

### 3. BreakableDebris (Tool-Gated Materials)

Debris can be:
- **Free pickups** (no tool required) – interact to collect materials immediately
- **Tool-locked** (requires specific tool) – can only break after learning/equipping tool
- **Persistent** – cleared debris stays cleared via GameFlags

**Visual feedback:**
- Intact: bright white color, collider enabled
- Cleared: dim gray, push to background (-10 sorting order), collider disabled

**Persistence via GameFlags:**
```csharp
GameFlags.Set("debris_cleared_{debrisId}", true);
// On scene load, BreakableDebris checks this flag and restores state
```

### 4. Tool System (Learn → Equip → Use)

Tools are learned via recipes (unlocked through dialogue or NPC teaching).

**Three-state tool lifecycle:**
1. **Unknown** – Player hasn't learned the recipe
2. **Known** (in inventory) – Player has the tool as a "knowledge item"
3. **Equipped** – Player can use this tool on debris

**Note:** Tools are stored in inventory like any other item. Having `pry_bar` in inventory means player knows how to use it. Equipping makes it the active tool.

```csharp
ToolSystem.Instance.EquipTool("pry_bar");  // Enable interaction with pry-bar-breakable debris
ToolSystem.Instance.UnequipTool();         // Switch back to bare hands
bool hasIt = ToolSystem.Instance.HasTool("pry_bar");  // Check if in inventory
bool active = ToolSystem.Instance.IsToolEquipped("pry_bar");
```

---

## Implementation Checklist

### Phase 1: Currency Foundation (30-45 min)
- [x] Create `CurrencySystem.cs` – tracks Bits with PlayerPrefs persistence
- [x] Test: Earn, Spend, CanAfford, Save/Load

### Phase 2: NPC Trade Profiles (30 min)
- [x] Create `NPCTradeProfile.cs` ScriptableObject
- [x] Implement price calculation (specific item → tag → default)
- [x] Test: Create Willy profile, calculate prices for different items

### Phase 3: Tool System (30-45 min)
- [x] Create `ToolSystem.cs` singleton
- [x] Create `ToolDefinition.cs` ScriptableObject
- [x] Implement equip/unequip, HasTool, IsToolEquipped
- [x] Test: Learn tool (add to inventory), equip, interact with debris

### Phase 4: Breakable Debris (45 min)
- [x] Create `BreakableDebris.cs` with tool gating
- [x] Implement persistence via GameFlags
- [x] Implement visual feedback (intact → cleared states)
- [x] Test: Break debris without tool, break with tool, reload scene and verify cleared state

### Phase 5: NPC Trader Component (45 min)
- [ ] Create `NPCTrader.cs` – handles trade UI flow
- [ ] Implement CreateTradeOffer (items → calculated Bits)
- [ ] Implement ExecuteTrade (remove items, add Bits, fire events)
- [ ] Test: Trade 3x copper_wire with Willy, verify receive 18 bits (3 × 6)

### Phase 6: Willy Second Encounter Dialogue (1-2 hr)
- [ ] Create `willy_trading_encounter.json` dialogue
- [ ] Integrate NPCTrader into dialogue triggers
- [ ] Add system_triggers for tool recipe unlock
- [ ] Test: Complete dialogue, receive pry_bar in inventory, equip it

### Phase 7: Integration Testing (1-2 hr)
- [ ] Test full flow: collect copper_wire → trade with Willy → earn bits → receive pry_bar recipe
- [ ] Verify persistence: save game, close, reload, debris still cleared, bits still earned
- [ ] Edge cases: try using pry bar on non-breakable debris, try trading items you don't have

---

## Setup Instructions

### Step 1: Create Economy Manager Scene GameObject

1. In any persistent scene (or a new Economy scene that loads first)
2. Create empty GameObject "EconomyManager"
3. Add `CurrencySystem.cs` as component
4. Set Initial Bits = 0 (first trade will be Willy's 6 bits)
5. Verify DontDestroyOnLoad is applied

### Step 2: Create Willy Trade Profile Asset

1. Right-click in Assets/Resources/Data/ (or similar)
2. Create → Velinor/Economy/NPC Trade Profile
3. Name it "Willy_TradeProfile"
4. Configure:
   - NPC ID: "willy"
   - Display Name: "Willy"
   - Preferred Tags:
     - Electrical: 1.25x
     - Mechanical: 1.25x
   - Highly Sought Items:
     - copper_wire: 1.5x (base 4 → 6 bits)
     - motor_parts: 1.3x
     - old_circuitry: 1.2x
   - Default Multiplier: 1.0x

### Step 3: Create Pry Bar Tool Definition

1. Right-click in Assets/Resources/Data/
2. Create → Velinor/Tools/Tool Definition
3. Name it "PryBar_ToolDef"
4. Configure:
   - Tool ID: "pry_bar"
   - Display Name: "Pry Bar"
   - Description: "A salvager's trusty pry bar. Useful for breaking sealed panels and extracting components."
   - Can Break Debris Types: "sealed_panel", "rusted_bolt", "lodged_components"
   - Icon: (optional sprite)

### Step 4: Add ToolSystem to Scene

1. Create empty GameObject "ToolSystemManager"
2. Add `ToolSystem.cs` component
3. Set Available Tools list to include PryBar_ToolDef
4. Verify DontDestroyOnLoad is applied

### Step 5: Set Up Debris in Willy Scene

Example: sealed panel near Willy

```
GameObject: WillyScenePanel
├─ SpriteRenderer (bright white sprite)
├─ Collider2D
└─ BreakableDebris.cs
    - Debris ID: "willy_concourse_sealed_panel_01"
    - Required Tool ID: "pry_bar"
    - Materials Yielded:
      - motor_parts (qty 2)
      - copper_wire (qty 1)
    - Visual feedback configured
```

### Step 6: Add NPCTrader to Willy NPC

1. Select Willy NPC GameObject
2. Add `NPCTrader.cs` component
3. Set NPC ID: "willy"
4. Set Trade Profile: Willy_TradeProfile

---

## Usage Examples

### Collecting Items (Player Interaction)

```csharp
// Player interacts with free pickup
var pickup = GetComponent<WorldItemPickup>();
pickup.Interact(playerObject);  // Adds 2x copper_wire to inventory

// Player interacts with debris (no tool required)
var debris = GetComponent<BreakableDebris>();
debris.Interact(playerObject);  // Breaks immediately, adds materials

// Player interacts with tool-locked debris (without tool)
debris.Interact(playerObject);  // Debug: "Requires pry_bar"

// Player equips tool
ToolSystem.Instance.EquipTool("pry_bar");

// Player interacts with tool-locked debris (with tool)
debris.Interact(playerObject);  // Breaks! Adds materials, updates GameFlags
```

### Trading with NPC

```csharp
var trader = willysGameObject.GetComponent<NPCTrader>();

// Player selects items to trade
var itemsOffered = new Dictionary<string, int>
{
    { "copper_wire", 3 },
    { "motor_parts", 1 }
};

// Create trade offer
var offer = trader.CreateTradeOffer(itemsOffered);
// offer.totalBitsOffered = 18 (3×6 + 1×4)

// Show player the offer
Debug.Log(offer.ToString());

// Player confirms
if (trader.ExecuteTrade(offer))
{
    Debug.Log("Trade successful!");
    // Inventory: copper_wire -3, motor_parts -1
    // Currency: +18 bits
}
```

### Learning a Recipe

When Willy dialogue ends with recipe unlock:

```csharp
// From willy_trading_encounter.json system_triggers:
{
    "type": "inventory_add",
    "data": ["pry_bar", "1"]  // Adds pry_bar to inventory = "learned recipe"
}
```

Player can now equip and use the pry bar.

---

## Event System Integration

### CurrencySystem Events

```csharp
CurrencySystem.Instance.OnBitsEarned += (amount, reason) =>
{
    Debug.Log($"+{amount} bits ({reason})");
};

CurrencySystem.Instance.OnBitsSpent += (amount, reason) =>
{
    Debug.Log($"-{amount} bits ({reason})");
};

CurrencySystem.Instance.OnBitsChanged += (total) =>
{
    bitsUILabel.text = $"Bits: {total}";
};
```

### NPCTrader Events

```csharp
var trader = GetComponent<NPCTrader>();

trader.OnTradeOfferCreated += (offer) =>
{
    // Show offer UI, highlight items in inventory
};

trader.OnTradeAccepted += (offer) =>
{
    // Play success audio, show +bits popup
};

trader.OnTradeCancelled += () =>
{
    // Close trade UI
};
```

### BreakableDebris Persistence

Cleared debris automatically persists via GameFlags. On scene load:

```csharp
private void OnEnable()
{
    clearedFlagKey = $"debris_cleared_{debrisId}";
    if (GameFlags.Get(clearedFlagKey, false))
    {
        isCleared = true;
    }
    UpdateVisuals();
}
```

---

## Testing Checklist

### Currency System
- [ ] Earn bits, verify OnBitsEarned fires
- [ ] Spend bits, verify OnBitsSpent fires and subtraction is correct
- [ ] Try to spend more than available, verify failure
- [ ] Close game, reopen, verify bits persisted

### NPC Trade Profiles
- [ ] Copper wire base price 4, Willy multiplier 1.5x → 6 bits ✓
- [ ] Motor parts base price 3, tag multiplier 1.25x → 4 bits
- [ ] Unknown item, default multiplier 1.0x → base value

### Debris Persistence
- [ ] Break debris in scene
- [ ] Leave scene and return, verify debris still broken
- [ ] Close game and reopen, verify debris still broken

### Tool System
- [ ] Add pry_bar to inventory (simulate recipe unlock)
- [ ] Equip pry_bar, verify EquippedToolId = "pry_bar"
- [ ] Try to interact with sealed_panel without tool, verify message
- [ ] Equip pry_bar, interact, verify debris breaks

### Full Integration
- [ ] Collect 3x copper_wire from pickups
- [ ] Trade with Willy: 3x copper_wire → 18 bits
- [ ] Receive pry_bar recipe in dialogue
- [ ] Equip pry_bar
- [ ] Break sealed_panel, receive 2x motor_parts + 1x copper_wire
- [ ] Save game, reload, verify:
  - Bits still 18
  - Inventory unchanged
  - Sealed panel still broken

---

## Common Issues & Solutions

### "Player doesn't have tool" when trying to break debris

**Symptom:** Can't break sealed panel even after getting pry_bar

**Solution:**
1. Check that pry_bar was added to inventory via dialogue trigger
2. Verify ToolSystem.Instance exists in scene
3. Call `ToolSystem.Instance.EquipTool("pry_bar")` before interacting
4. Verify BreakableDebris.requiredToolId = "pry_bar" (exact string match)

### Debris respawns after reload

**Symptom:** Broken debris becomes intact after save/load

**Solution:**
1. Verify GameFlags is being set: Check console logs "[GameFlags] debris_cleared_X = true"
2. Verify debrisId is unique and consistent (not randomly generated)
3. Verify OnEnable() is called and checks GameFlags before UpdateVisuals()
4. Test with simple Save/Load scenario (no full game state load)

### Bits not persisting after game close

**Symptom:** Start with 0 bits, trade and get 18, close game, reopen → back to 0

**Solution:**
1. Verify CurrencySystem has SaveBits() called in Earn/Spend methods
2. Verify PlayerPrefs.Save() is called (not just SetInt)
3. Check that BITS_SAVE_KEY is correct ("velinor_bits_total")
4. Debug: PlayerPrefs.HasKey("velinor_bits_total") should return true after trade

### NPC won't trade items

**Symptom:** Trade offer shows 0 bits, NPC refuses

**Solution:**
1. Verify NPCTradeProfile.WillAccept(item) returns true
2. Check that item category isn't in refusedCategories
3. Verify baseValue > 0 on ItemDefinition
4. Test with known good item (copper_wire for Willy)

---

## Performance Notes

- **CurrencySystem:** O(1) – stores single int
- **NPCTradeProfile:** O(n) where n = number of preferred tags + specific items (typically < 10)
- **BreakableDebris:** O(1) per debris, O(m) where m = materials yielded
- **ToolSystem:** O(n) where n = available tools (typically < 5)

No performance bottlenecks expected for typical game scale.

---

## Next Steps

1. Create Willy's second encounter dialogue (willy_trading_encounter.json)
2. Build trading UI panel (show offer, confirm/cancel buttons)
3. Add visual feedback for tool-locked vs tool-unlocked debris
4. Create first recipe (pry bar) and integrate into dialogue
5. Test full flow with real dialogue system


### 1. Currency System (Lightweight, Persistent)

```csharp
CurrencySystem.Instance.Earn(6, "Traded with Willy");
bool canBuy = CurrencySystem.Instance.CanAfford(12);
CurrencySystem.Instance.Spend(12, "Purchased item");
```

**Key features:**
- DontDestroyOnLoad singleton (persists across scenes)
- PlayerPrefs-backed save/load (survives game restart)
- Event-driven (`OnBitsEarned`, `OnBitsSpent`, `OnBitsChanged`)
- Includes reason tracking for player feedback

**Why no Bits counter in save data:**
- Bits are derived from what NPCs have been traded with
- If needed for full persistence, use same pattern as Inventory (save to JSON with GameState)
- For now, PlayerPrefs is sufficient for single-session play

### 2. NPC Trade Profiles (ScriptableObject-Based)

Each NPC has a `NPCTradeProfile` that defines:
- Base multipliers for ItemTags (e.g., Willy pays 1.25x for Electrical items)
- Specific item multipliers (e.g., Willy pays 1.5x for copper_wire specifically)
- Refused categories (items the NPC won't buy at all)
- Display name and NPC ID

**Example: Willy's Profile**
```yaml
Willy Trade Profile
  Preferred Tags:
    - Electrical: 1.25x
    - Mechanical: 1.25x
    - Salvage: 1.10x
  Highly Sought Items:
    - copper_wire: 1.5x
    - motor_parts: 1.4x
    - old_circuitry: 1.3x
  Refused Categories: (none)
  Default Multiplier: 1.0x
```

**Price calculation:**
```
offered_price = base_value × (specific_multiplier OR tag_multiplier OR default_multiplier)
```

If item matches a specific item entry, use that. Otherwise check tags. Otherwise use default.

### 3. BreakableDebris (Tool-Gated Materials)

Debris can be:
- **Free pickups** (no tool required) – just interact to collect materials immediately
- **Tool-locked** (requires specific tool) – can only break after learning/equipping tool
- **Persistent** – cleared debris stays cleared via GameFlags

**Visual feedback:**
- Intact: bright white color, collider enabled
- Cleared: dim gray, push to background (-10 sorting order), collider disabled

**Persistence via GameFlags:**
```csharp
GameFlags.Set("debris_cleared_willy_panel_01", true);
// On scene load, BreakableDebris checks this flag and restores state
```

### 4. Tool System (Learn → Equip → Use)

Tools are learned via recipes (unlocked through dialogue or NPC teaching).

**Three-state tool lifecycle:**
1. **Unknown** – Player hasn't learned the recipe
2. **Known** (in inventory) – Player has the tool as a "knowledge item"
3. **Equipped** – Player can use this tool on debris

**Note:** Tools are stored in inventory like any other item. Having `pry_bar` in inventory means player knows how to use it. Equipping makes it the active tool.

```csharp
ToolSystem.Instance.EquipTool("pry_bar");  // Enable interaction with pry-bar-breakable debris
ToolSystem.Instance.UnequipTool();         // Switch back to bare hands
bool hasIt = ToolSystem.Instance.HasTool("pry_bar");  // Check if in inventory
bool active = ToolSystem.Instance.IsToolEquipped("pry_bar");
```

## Implementation Checklist

### Phase 1: Currency Foundation (30-45 min)
- [x] Create `CurrencySystem.cs` – tracks Bits with PlayerPrefs persistence
- [x] Test: Earn, Spend, CanAfford, Save/Load

### Phase 2: NPC Trade Profiles (30 min)
- [x] Create `NPCTradeProfile.cs` ScriptableObject
- [x] Implement price calculation (specific item → tag → default)
- [x] Test: Create Willy profile, calculate prices for different items

### Phase 3: Tool System (30-45 min)
- [x] Create `ToolSystem.cs` singleton
- [x] Create `ToolDefinition.cs` ScriptableObject
- [x] Implement equip/unequip, HasTool, IsToolEquipped
- [x] Test: Learn tool (add to inventory), equip, interact with debris

### Phase 4: Breakable Debris (45 min)
- [x] Create `BreakableDebris.cs` with tool gating
- [x] Implement persistence via GameFlags
- [x] Implement visual feedback (intact → cleared states)
- [x] Test: Break debris without tool, break with tool, reload scene and verify cleared state

### Phase 5: NPC Trader Component (45 min)
- [ ] Create `NPCTrader.cs` – handles trade UI flow
- [ ] Implement CreateTradeOffer (items → calculated Bits)
- [ ] Implement ExecuteTrade (remove items, add Bits, fire events)
- [ ] Test: Trade 3x copper_wire with Willy, verify receive 18 bits (3 × 6)

### Phase 6: Willy Second Encounter Dialogue (1-2 hr)
- [ ] Create `willy_trading_encounter.json` dialogue
- [ ] Integrate NPCTrader into dialogue triggers
- [ ] Add system_triggers for tool recipe unlock
- [ ] Test: Complete dialogue, receive pry_bar in inventory, equip it

### Phase 7: Integration Testing (1-2 hr)
- [ ] Test full flow: collect copper_wire → trade with Willy → earn bits → receive pry_bar recipe
- [ ] Verify persistence: save game, close, reload, debris still cleared, bits still earned
- [ ] Edge cases: try using pry bar on non-breakable debris, try trading items you don't have

## Setup Instructions

### Step 1: Create Economy Manager Scene GameObject

1. In any persistent scene (or a new Economy scene that loads first)
2. Create empty GameObject "EconomyManager"
3. Add `CurrencySystem.cs` as component
4. Set Initial Bits = 0 (first trade will be Willy's 6 bits)
5. Verify DontDestroyOnLoad is applied

### Step 2: Create Willy Trade Profile Asset

1. Right-click in Assets/Resources/Data/ (or similar)
2. Create → Velinor/Economy/NPC Trade Profile
3. Name it "Willy_TradeProfile"
4. Configure:
   - NPC ID: "willy"
   - Display Name: "Willy"
   - Preferred Tags:
     - Electrical: 1.25x
     - Mechanical: 1.25x
   - Highly Sought Items:
     - copper_wire: 1.5x (base 4 → 6 bits)
     - motor_parts: 1.3x
     - old_circuitry: 1.2x
   - Default Multiplier: 1.0x

### Step 3: Create Pry Bar Tool Definition

1. Right-click in Assets/Resources/Data/
2. Create → Velinor/Tools/Tool Definition
3. Name it "PryBar_ToolDef"
4. Configure:
   - Tool ID: "pry_bar"
   - Display Name: "Pry Bar"
   - Description: "A salvager's trusty pry bar. Useful for breaking sealed panels and extracting components."
   - Can Break Debris Types: "sealed_panel", "rusted_bolt", "lodged_components"
   - Icon: (optional sprite)

### Step 4: Add ToolSystem to Scene

1. Create empty GameObject "ToolSystemManager"
2. Add `ToolSystem.cs` component
3. Set Available Tools list to include PryBar_ToolDef
4. Verify DontDestroyOnLoad is applied

### Step 5: Set Up Debris in Willy Scene

Example: sealed panel near Willy

```
GameObject: WillyScenePanel
├─ SpriteRenderer (bright white sprite)
├─ Collider2D
└─ BreakableDebris.cs
    - Debris ID: "willy_concourse_sealed_panel_01"
    - Required Tool ID: "pry_bar"
    - Materials Yielded:
      - motor_parts (qty 2)
      - copper_wire (qty 1)
    - Visual feedback configured
```

### Step 6: Add NPCTrader to Willy NPC

1. Select Willy NPC GameObject
2. Add `NPCTrader.cs` component
3. Set NPC ID: "willy"
4. Set Trade Profile: Willy_TradeProfile

## Usage Examples

### Collecting Items (Player Interaction)

```csharp
// Player interacts with free pickup
var pickup = GetComponent<WorldItemPickup>();
pickup.Interact(playerObject);  // Adds 2x copper_wire to inventory

// Player interacts with debris (no tool required)
var debris = GetComponent<BreakableDebris>();
debris.Interact(playerObject);  // Breaks immediately, adds materials

// Player interacts with tool-locked debris (without tool)
debris.Interact(playerObject);  // Debug: "Requires pry_bar"

// Player equips tool
ToolSystem.Instance.EquipTool("pry_bar");

// Player interacts with tool-locked debris (with tool)
debris.Interact(playerObject);  // Breaks! Adds materials, updates GameFlags
```

### Trading with NPC

```csharp
var trader = willysGameObject.GetComponent<NPCTrader>();

// Player selects items to trade
var itemsOffered = new Dictionary<string, int>
{
    { "copper_wire", 3 },
    { "motor_parts", 1 }
};

// Create trade offer
var offer = trader.CreateTradeOffer(itemsOffered);
// offer.totalBitsOffered = 18 (3×6 + 1×4)

// Show player the offer
Debug.Log(offer.ToString());
// "Trade Offer from Willy:
//   copper_wire x3
//   motor_parts x1
//   Total: 18 bits"

// Player confirms
if (trader.ExecuteTrade(offer))
{
    Debug.Log("Trade successful!");
    // Inventory: copper_wire -3, motor_parts -1
    // Currency: +18 bits
}
```

### Learning a Recipe

When Willy dialogue ends with recipe unlock:

```csharp
// From willy_trading_encounter.json system_triggers:
{
    "type": "inventory_add",
    "data": ["pry_bar", "1"]  // Adds pry_bar to inventory = "learned recipe"
}
```

Player can now equip and use the pry bar.

## Event System Integration

### CurrencySystem Events

```csharp
CurrencySystem.Instance.OnBitsEarned += (amount, reason) =>
{
    Debug.Log($"+{amount} bits ({reason})");
};

CurrencySystem.Instance.OnBitsSpent += (amount, reason) =>
{
    Debug.Log($"-{amount} bits ({reason})");
};

CurrencySystem.Instance.OnBitsChanged += (total) =>
{
    bitsUILabel.text = $"Bits: {total}";
};
```

### NPCTrader Events

```csharp
var trader = GetComponent<NPCTrader>();

trader.OnTradeOfferCreated += (offer) =>
{
    // Show offer UI, highlight items in inventory
};

trader.OnTradeAccepted += (offer) =>
{
    // Play success audio, show +bits popup
};

trader.OnTradeCancelled += () =>
{
    // Close trade UI
};
```

### BreakableDebris Persistence

Cleared debris automatically persists via GameFlags. On scene load:

```csharp
private void OnEnable()
{
    clearedFlagKey = $"debris_cleared_{debrisId}";
    if (GameFlags.Get(clearedFlagKey, false))
    {
        isCleared = true;
    }
    UpdateVisuals();
}
```

## Testing Checklist

### Currency System
- [ ] Earn bits, verify OnBitsEarned fires
- [ ] Spend bits, verify OnBitsSpent fires and subtraction is correct
- [ ] Try to spend more than available, verify failure
- [ ] Close game, reopen, verify bits persisted

### NPC Trade Profiles
- [ ] Copper wire base price 4, Willy multiplier 1.5x → 6 bits ✓
- [ ] Motor parts base price 3, tag multiplier 1.25x → 4 bits
- [ ] Unknown item, default multiplier 1.0x → base value

### Debris Persistence
- [ ] Break debris in scene
- [ ] Leave scene and return, verify debris still broken
- [ ] Close game and reopen, verify debris still broken

### Tool System
- [ ] Add pry_bar to inventory (simulate recipe unlock)
- [ ] Equip pry_bar, verify EquippedToolId = "pry_bar"
- [ ] Try to interact with sealed_panel without tool, verify message
- [ ] Equip pry_bar, interact, verify debris breaks

### Full Integration
- [ ] Collect 3x copper_wire from pickups
- [ ] Trade with Willy: 3x copper_wire → 18 bits
- [ ] Receive pry_bar recipe in dialogue
- [ ] Equip pry_bar
- [ ] Break sealed_panel, receive 2x motor_parts + 1x copper_wire
- [ ] Save game, reload, verify:
  - Bits still 18
  - Inventory unchanged
  - Sealed panel still broken

## Common Issues & Solutions

### "Player doesn't have tool" when trying to break debris

**Symptom:** Can't break sealed panel even after getting pry_bar

**Solution:**
1. Check that pry_bar was added to inventory via dialogue trigger
2. Verify ToolSystem.Instance exists in scene
3. Call `ToolSystem.Instance.EquipTool("pry_bar")` before interacting
4. Verify BreakableDebris.requiredToolId = "pry_bar" (exact string match)

### Debris respawns after reload

**Symptom:** Broken debris becomes intact after save/load

**Solution:**
1. Verify GameFlags is being set: Check console logs "GameFlags] debris_cleared_X = true"
2. Verify debrisId is unique and consistent (not randomly generated)
3. Verify OnEnable() is called and checks GameFlags before UpdateVisuals()
4. Test with simple Save/Load scenario (no full game state load)

### Bits not persisting after game close

**Symptom:** Start with 0 bits, trade and get 18, close game, reopen → back to 0

**Solution:**
1. Verify CurrencySystem has SaveBits() called in Earn/Spend methods
2. Verify PlayerPrefs.Save() is called (not just SetInt)
3. Check that BITS_SAVE_KEY is correct ("velinor_bits_total")
4. Debug: PlayerPrefs.HasKey("velinor_bits_total") should return true after trade

### NPC won't trade items

**Symptom:** Trade offer shows 0 bits, NPC refuses

**Solution:**
1. Verify NPCTradeProfile.WillAccept(item) returns true
2. Check that item category isn't in refusedCategories
3. Verify baseValue > 0 on ItemDefinition
4. Test with known good item (copper_wire for Willy)

## Performance Notes

- **CurrencySystem:** O(1) – stores single int
- **NPCTradeProfile:** O(n) where n = number of preferred tags + specific items (typically < 10)
- **BreakableDebris:** O(1) per debris, O(m) where m = materials yielded
- **ToolSystem:** O(n) where n = available tools (typically < 5)

No performance bottlenecks expected for typical game scale (1000s of debris, 10s of NPCs, 100s of items).

## Next Steps

1. Create Willy's second encounter dialogue (willy_trading_encounter.json)
2. Build trading UI panel (show offer, confirm/cancel buttons)
3. Add visual feedback for tool-locked vs tool-unlocked debris
4. Create first recipe (pry bar) and integrate into dialogue
5. Test full flow with real dialogue system
