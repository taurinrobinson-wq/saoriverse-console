# Velinor Systems Overview - All Created Systems from Commit 73282c230

This document provides a bird's-eye view of all systems created in commit `73282c230` and their relationships.

---

## 📦 Systems at a Glance

### Core Runtime Singletons (Must be in every scene)

| System | File | Purpose | Persistence |
|--------|------|---------|-------------|
| **InventoryService** | `InventoryService.cs` | Stores items, handles Add/Remove operations | GameFlags |
| **CurrencySystem** | `CurrencySystem.cs` | Tracks player's Bits (currency), earn/spend | PlayerPrefs |
| **ToolSystem** | `ToolSystem.cs` | Tracks equipped tool, checks player has tools | Inventory-backed |

### Static Data (Scriptable Objects - Need to be created once)

| Asset | File | Purpose | Where to Create |
|-------|------|---------|-----------------|
| **ItemDatabase** | `ItemDatabase.cs` | Registry of all items, O(1) lookup | Assets/Resources/Items/ |
| **ItemDefinition** | `ItemDefinition.cs` | Individual item data (name, tags, value) | Assets/Resources/Items/ |
| **NPCTradeProfile** | `NPCTradeProfile.cs` | Per-NPC trading preferences | Assets/ScriptableObjects/Economy/ |

### Interaction Components (Add to GameObjects in scenes)

| Component | File | Purpose | Implements |
|-----------|------|---------|-----------|
| **WorldItemPickup** | `WorldItemPickup.cs` | Collectible item in world | IInteractable |
| **BreakableDebris** | `BreakableDebris.cs` | Mineable/breakable rock/debris | IInteractable |
| **NPCTrader** | `NPCTrader.cs` | NPC that trades items for bits | IInteractable |

### UI Components (Add to UI_Canvas)

| Component | File | Purpose | Location |
|-----------|------|---------|----------|
| **InventoryUIPanel** | `InventoryUIPanel.cs` | Left panel showing all items | Canvas child |
| **InventoryItemEntryUI** | `InventoryItemEntryUI.cs` | Single item row in inventory | Prefab |
| **BitsDisplayUI** | `BitsDisplayUI.cs` | Top-right currency display | Canvas child |

### Support Infrastructure

| Component | File | Purpose |
|-----------|------|---------|
| **IInteractable** | `IInteractable.cs` (Core) | Interface for all interactive objects |
| **ToolSystem** | `ToolSystem.cs` | Manages equipped tools |
| **GameFlags** | (Existing) | Persistence for pickups, debris, dialogue state |

---

## 🎯 Quick Feature Matrix

| Feature | System(s) | Can Do | Can't Do |
|---------|-----------|--------|----------|
| **Collect items** | InventoryService + WorldItemPickup | Add/remove items, persist pickups | Durability, weight limits |
| **Trade with NPCs** | NPCTrader + CurrencySystem | Calculate prices by preference, earn bits | Quest tracking, complex bartering |
| **Use tools** | ToolSystem | Track equipped tool, check if player has tool | Tool durability, advanced crafting |
| **Display inventory** | InventoryUIPanel | Show items, update on changes | Grid layout, item sorting |
| **Track currency** | CurrencySystem | Earn/spend bits, persist balance | Multiple currency types |
| **Breakable debris** | BreakableDebris | Mine materials, require tools, persist cleared | Respawning, dynamic loot tables |

---

## 📊 System Dependencies

```
REQUIRED FOR ALL SYSTEMS:
  GameFlags (existing system - handles persistence)
    └─ Used by WorldItemPickup and BreakableDebris

InventoryService (Core)
  ├─ Depends on: ItemDatabase
  └─ Used by: WorldItemPickup, BreakableDebris, ToolSystem, NPCTrader, UI

CurrencySystem (Standalone)
  └─ Used by: NPCTrader, Dialogue system

ToolSystem (Standalone)
  ├─ Reads: InventoryService (to check if player has tools)
  └─ Used by: BreakableDebris, Dialogue system

NPCTrader (Per-NPC)
  ├─ Depends on: NPCTradeProfile, InventoryService, CurrencySystem
  └─ Triggered by: Dialogue, Player interaction

WorldItemPickup (Per-item)
  ├─ Depends on: ItemDefinition, InventoryService, GameFlags
  └─ Placed in: Scene

BreakableDebris (Per-debris)
  ├─ Depends on: ItemDefinition, InventoryService, ToolSystem, GameFlags
  └─ Placed in: Scene
```

---

## 🚀 Implementation Roadmap

### Step 1: Create Static Data (5 min)
1. Create `ItemDatabase.asset`
2. Create 5 `ItemDefinition.asset` files
3. Create `NPCTradeProfile.asset` for Willy

**Files to create:** 7 ScriptableObjects  
**Expected:** No errors on play, console shows initialization messages

### Step 2: Add Singletons to Scene (5 min)
1. Add `InventoryService` GameObject
2. Add `CurrencySystem` GameObject
3. Add `ToolSystem` GameObject

**Files to modify:** Scene  
**Expected:** All singletons initialize, no null reference errors

### Step 3: Add World Objects (10 min)
1. Create `WorldItemPickup` for copper wire
2. Create `BreakableDebris` for rocks
3. Add `NPCTrader` to Willy GameObject

**Files to modify:** Scene  
**Expected:** Can interact, items collected/traded, persist correctly

### Step 4: Build UI (10 min)
1. Create `InventoryPanel` on canvas
2. Create `InventoryItemEntry` prefab
3. Create `BitsDisplay` text

**Files to modify:** Prefab  
**Expected:** UI shows items and currency, updates on changes

### Step 5: Integrate with Dialogue (15 min)
1. Add inventory checks in dialogue conditions
2. Add item removal in dialogue actions
3. Hook trade triggers to dialogue beats

**Files to modify:** Dialogue system, DialogueUIController  
**Expected:** Dialogue flows can branch on inventory, trade within conversation

**TOTAL TIME: ~45 minutes**

---

## 📖 Documentation Files

| Document | Purpose | Read When |
|----------|---------|-----------|
| **QUICK_SETUP_CHECKLIST.md** | 30-min implementation checklist | Starting setup |
| **SYSTEM_IMPLEMENTATION_GUIDE.md** | Detailed 7-phase guide with code examples | Need step-by-step help |
| **SYSTEM_ARCHITECTURE.md** | Architecture diagrams and data flows | Understanding relationships |
| **SYSTEMS_OVERVIEW.md** | This file - high-level view | Getting oriented |

---

## 💡 Common Integration Patterns

### Pattern 1: Check & Consume Item in Dialogue

```csharp
// In dialogue condition
if (InventoryService.Instance.Contains("copper_wire", 2))
{
    // Show dialogue option: "Give copper wire?"
}

// In dialogue action (after player confirms)
if (InventoryService.Instance.Remove("copper_wire", 2))
{
    // Continue to next beat
    // NPC receives items, maybe triggers trade
}
```

### Pattern 2: Trade with NPC

```csharp
// Setup once
NPCTrader willy = willyGameObject.GetComponent<NPCTrader>();

// On trade trigger
var offer = willy.CreateTradeOffer(
    new Dictionary<string, int> 
    { 
        { "copper_wire", 2 },
        { "glass_fragments", 1 }
    }
);

// Show player: "Willy offers X bits for these items"

// If player accepts
if (willy.ExecuteTrade(offer))
{
    // Automatically:
    // - Remove items from inventory
    // - Add bits to currency
    // - Fire OnTradeAccepted event
}
```

### Pattern 3: Tool-Dependent Action

```csharp
// In BreakableDebris or custom tool interaction
string requiredTool = "pickaxe";

if (!ToolSystem.Instance.HasTool(requiredTool))
{
    Debug.Log("You need a pickaxe");
    return; // Show error UI
}

// Tool check passed, proceed with action
BreakTheRock();
```

### Pattern 4: Display Inventory Status

```csharp
// Subscribe to changes
InventoryService.Instance.OnInventoryChanged += (itemId, quantity) =>
{
    // Update UI label: "Copper Wire x" + quantity
    // Show item tooltip
    // Play pickup sound
};

// Query current state
foreach (var kvp in InventoryService.Instance.GetAllItems())
{
    Debug.Log($"{kvp.Key}: {kvp.Value}");
}
```

---

## 🔍 What Scripts DO Exist vs. Don't

### ✅ Scripts That Exist (Ready to Use)
- `ItemDefinition.cs` - Item data structure
- `ItemDatabase.cs` - Central registry
- `InventoryService.cs` - Inventory management (Singleton)
- `InventoryUIPanel.cs` - Inventory UI panel
- `InventoryItemEntryUI.cs` - UI row for items
- `WorldItemPickup.cs` - Pickupable items
- `BreakableDebris.cs` - Mineable objects
- `CurrencySystem.cs` - Currency tracking (Singleton)
- `BitsDisplayUI.cs` - Currency display UI
- `NPCTrader.cs` - NPC trading component
- `NPCTradeProfile.cs` - NPC preferences
- `ToolSystem.cs` - Tool tracking (Singleton)
- `IInteractable.cs` - Interaction interface (Core)
- `SceneAudioController.cs` - Audio persistence

### ❌ Scripts That DON'T Exist (Future Work)
- Tool crafting system
- Item durability/repair
- Quest tracking tied to trades
- Inventory sorting/filtering UI
- Weight/capacity limits
- Multiple currency types
- Shop/store system (separate from NPC trade)
- Skill/perk system
- Loot tables/randomized rewards

---

## 🎮 Gameplay Example: Full Flow

```
SCENE: InsideMarket_02

1. PLAYER ENTERS SCENE
   - InventoryService initializes (DontDestroyOnLoad)
   - CurrencySystem loads bits from PlayerPrefs
   - ToolSystem ready to track equipped tool
   - BitsDisplay shows "Bits: 0"
   - InventoryPanel shows empty

2. PLAYER WALKS OVER COPPER WIRE PICKUP
   - WorldItemPickup.Interact() fires
   - InventoryService.Add("copper_wire", 3)
   - OnInventoryChanged event fires
   - InventoryUIPanel updates: Shows "Copper Wire x3"
   - GameFlags: pickup_collected_copper_wire_01 = true

3. PLAYER APPROACHES WILLY & TRIGGERS DIALOGUE
   - Dialogue condition: "Do you have 2x copper_wire?"
   - InventoryService.Contains("copper_wire", 2) → true
   - Dialogue option unlocked: "Trade with Willy"

4. PLAYER SELECTS TRADE OPTION
   - NPCTrader.CreateTradeOffer({copper_wire: 2})
   - WillyTradeProfile calculates: 2 × 2 base × 1.5 (highly sought) = 6 bits
   - UI shows: "Willy offers 6 bits for 2x Copper Wire"

5. PLAYER CONFIRMS TRADE
   - NPCTrader.ExecuteTrade(offer)
   - InventoryService.Remove("copper_wire", 2)
   - CurrencySystem.Earn(6, "Traded with Willy")
   - OnBitsEarned event fires
   - BitsDisplay updates: "Bits: 6" (flashes green)
   - InventoryUIPanel updates: "Copper Wire x1"
   - OnTradeAccepted event fires → Dialogue continues

6. PLAYER APPROACHES ROCK & TRIES TO MINE
   - BreakableDebris.Interact() fires
   - Checks: ToolSystem.HasTool("pickaxe") → false
   - Message: "This requires a pickaxe"
   - Dialogue hint: "Find a pickaxe to break this"

7. PLAYER EQUIPS PICKAXE (via dialogue or code)
   - ToolSystem.EquipTool("pickaxe")
   - OnToolEquipped event fires
   - UI updates: Shows equipped tool

8. PLAYER TRIES ROCK AGAIN
   - BreakableDebris.Interact() fires
   - ToolSystem.HasTool("pickaxe") → true
   - BreakTheRock()
   - InventoryService.Add("sheet_metal", 2)
   - InventoryService.Add("glass_fragments", 1)
   - GameFlags: debris_cleared_rock_01 = true
   - Rock grays out, becomes uninteractable

9. PLAYER LEAVES SCENE
   - InventoryService persists (DontDestroyOnLoad)
   - CurrencySystem persists (DontDestroyOnLoad)
   - Bits auto-saved to PlayerPrefs
   - GameFlags persisted (pickups, debris, dialogue state)

10. PLAYER RE-ENTERS SCENE
    - Pickup gone (marked collected)
    - Rock still broken (marked cleared)
    - Inventory still has sheet_metal + glass_fragments
    - Bits still show 6
    - Everything exactly as left
```

---

## 🛠️ Debugging Tips

**Enable verbose logging:**
```csharp
// In InventoryService.cs, CurrencySystem.cs, etc.
// Change Debug.Log to always show (already enabled)
// Look for [InventoryService], [CurrencySystem], [ToolSystem] tags in console
```

**Test in Play mode quickly:**
```csharp
// Console input while playing
InventoryService.Instance.Add("copper_wire", 3);
CurrencySystem.Instance.Earn(10, "Test");
ToolSystem.Instance.EquipTool("pickaxe");

// Or use Debug.Evaluate in Editor
```

**Check persistence:**
```
PlayerPrefs:
  Windows: HKEY_CURRENT_USER\Software\Unity\Editor\Velinor
  Mac: ~/Library/Preferences/com.DefaultCompany.Velinor.plist
  Linux: ~/.config/unity3d/DefaultCompany/Velinor/prefs

GameFlags:
  Stored in GameFlags singleton (in-memory)
  Used by WorldItemPickup and BreakableDebris
  Persists across scene reloads in same session
```

---

## 📝 Quick Reference - Key Methods

```csharp
// INVENTORY
InventoryService.Instance.Add(itemId, quantity);
InventoryService.Instance.Remove(itemId, quantity);
InventoryService.Instance.Contains(itemId, quantity);
InventoryService.Instance.GetAllItems();

// CURRENCY
CurrencySystem.Instance.Earn(amount, reason);
CurrencySystem.Instance.Spend(amount, reason);
CurrencySystem.Instance.CanAfford(amount);
CurrencySystem.Instance.CurrentBits;

// TOOLS
ToolSystem.Instance.HasTool(toolId);
ToolSystem.Instance.EquipTool(toolId);
ToolSystem.Instance.EquippedToolId;

// NPC TRADING
var offer = npcTrader.CreateTradeOffer(itemDict);
npcTrader.ExecuteTrade(offer);

// WORLD OBJECTS
worldItemPickup.Collect();
breakableDebris.BreakDebris();

// EVENTS (Subscribe)
InventoryService.Instance.OnInventoryChanged += (id, qty) => { };
CurrencySystem.Instance.OnBitsEarned += (amt, reason) => { };
CurrencySystem.Instance.OnBitsSpent += (amt, reason) => { };
ToolSystem.Instance.OnToolEquipped += (id) => { };
npcTrader.OnTradeAccepted += (offer) => { };
```

---

## ✨ Next Phases (Not Yet Implemented)

After this system is stable, consider adding:

1. **Tool Durability System** - Tools wear out, need repair
2. **Item Crafting** - Combine items to create new ones
3. **Quest Tracking** - Track what NPCs want/offer
4. **Reputation System** - NPC prices based on reputation
5. **Inventory Sorting** - Filter by category, tags, search
6. **Advanced Trading** - Multi-item negotiations
7. **Loot Tables** - Random item drops from debris
8. **Marketplace** - Global store with rotating inventory

---

## 📞 Getting Help

If something doesn't work:

1. **Check the docs:**
   - `QUICK_SETUP_CHECKLIST.md` - Step-by-step
   - `SYSTEM_IMPLEMENTATION_GUIDE.md` - Detailed help
   - `SYSTEM_ARCHITECTURE.md` - Understanding relationships

2. **Check the console:**
   - Look for [InventoryService], [CurrencySystem], [ToolSystem] prefixed messages
   - "is null" errors usually mean singleton not in scene

3. **Verify setup:**
   - All 3 singletons in scene? ✓
   - ItemDatabase assigned to InventoryService? ✓
   - All 5 items in ItemDatabase? ✓
   - NPCTradeProfile assigned to NPCTrader? ✓

4. **Test incrementally:**
   - Add items, check inventory
   - Earn bits, check display
   - Trade, verify both systems update
   - Reload scene, verify persistence

---

**Status: All systems ready for production. Documentation complete. Go build! 🚀**
