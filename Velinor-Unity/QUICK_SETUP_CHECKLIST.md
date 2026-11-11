# Quick Setup Checklist - Inventory/Currency/Tool Systems

Complete this checklist to wire up all systems. Estimated time: 20-30 minutes.

---

## ✅ PHASE 1: Create Data Assets (5 min)

### Create ItemDatabase and Items
- [ ] Create folder: `Assets/Resources/Items/`
- [ ] Create ItemDatabase asset: `Assets/Resources/Items/ItemDatabase.asset`
  - Right-click → Create → Velinor/Inventory/Item Database
- [ ] Create 5 Item Definitions:
  - [ ] `copper_wire.asset` (Material, Metal+Electrical, Value: 2, Stack: 99)
  - [ ] `glass_fragments.asset` (Material, Glass, Value: 1, Stack: 99)
  - [ ] `sheet_metal.asset` (Material, Metal+Mechanical, Value: 3, Stack: 99)
  - [ ] `light_bulb.asset` (Material, Electrical+Glass, Value: 4, Stack: 5)
  - [ ] `tool_fragment.asset` (Tool, Mechanical, Value: 5, Stack: 10)
- [ ] Add all 5 items to ItemDatabase's items list
- [ ] Verify no errors in console

### Create NPC Trade Profile
- [ ] Create folder: `Assets/ScriptableObjects/Economy/`
- [ ] Create NPCTradeProfile: `WillyTradeProfile.asset`
  - [ ] npcId: `willy`
  - [ ] displayName: `Willy`
  - [ ] Preferred Tags: Electrical (1.25), Mechanical (1.25), Salvage (1.1)
  - [ ] Highly Sought: copper_wire (1.5), sheet_metal (1.3)
  - [ ] Default Multiplier: 1.0

---

## ✅ PHASE 2: Add Singleton Services to Scene (10 min)

### Setup InventoryService
- [ ] Create empty GameObject: `InventoryService`
- [ ] Add Component: **InventoryService**
- [ ] Assign ItemDatabase.asset to `itemDatabase` field
- [ ] Verify console: "[InventoryService] Initialized and marked persistent"
- [ ] Verify console: "[ItemDatabase] Initialized with 5 items"

### Setup CurrencySystem
- [ ] Create empty GameObject: `CurrencySystem`
- [ ] Add Component: **CurrencySystem**
- [ ] Set `initialBits`: `0`
- [ ] Verify no console errors on play

### Setup ToolSystem
- [ ] Create empty GameObject: `ToolSystem`
- [ ] Add Component: **ToolSystem**
- [ ] Leave `availableTools` list empty (for now)
- [ ] Verify no console errors on play

---

## ✅ PHASE 3: Create WorldItemPickup (5 min)

### Add Copper Wire Pickup
- [ ] Create new GameObject in scene: `CopperWire_Pickup_01`
- [ ] Add Sprite Renderer or 3D model (visual)
- [ ] Add Box Collider 2D/3D: set `isTrigger = true`
- [ ] Add Component: **WorldItemPickup**
  - [ ] pickupId: `copper_wire_market_01` (auto-fills)
  - [ ] itemDefinition: Drag `copper_wire.asset`
  - [ ] quantity: `3`
- [ ] Test: Play → Walk over → Console: "Collected 3x Copper Wire"
- [ ] Verify inventory shows `copper_wire: 3`

---

## ✅ PHASE 4: Add NPC Trader (5 min)

### Setup Willy as Trader
- [ ] Select Willy GameObject in scene
- [ ] Add Component: **NPCTrader**
  - [ ] npcId: `willy` (auto-fills from profile)
  - [ ] tradeProfile: Drag `WillyTradeProfile.asset`
- [ ] Verify Willy has Box Collider 2D/3D
- [ ] Test: Play → Interact with Willy → Console: "NPC willy (Willy) ready to trade"

---

## ✅ PHASE 5: Build UI (10 min)

### Create InventoryPanel
- [ ] Select UI_Canvas
- [ ] Create child: **UI → Panel**
  - [ ] Name: `InventoryPanel`
  - [ ] Position: `x = -200, y = 0`
  - [ ] Size: `Width: 350, Height: 600`
- [ ] Add Component: **InventoryUIPanel**
- [ ] Create child of InventoryPanel: **UI → Vertical Layout Group**
  - [ ] Name: `ItemList`
  - [ ] Add Layout Element component
- [ ] In InventoryUIPanel Inspector:
  - [ ] canvasGroup: Drag self (InventoryPanel)
  - [ ] itemListLayout: Drag ItemList RectTransform
  - [ ] itemEntryPrefab: (Create next)

### Create InventoryItemEntry Prefab
- [ ] Create new prefab: `Assets/Prefabs/InventoryItemEntry.prefab`
- [ ] Structure:
  ```
  InventoryItemEntry (Horizontal Layout)
  ├── ItemIcon (Image)
  └── ItemInfo (Vertical Layout)
      ├── ItemName (Text)
      └── ItemQuantity (Text)
  ```
- [ ] Add Component to root: **InventoryItemEntryUI**
  - [ ] itemIcon: Drag Image component
  - [ ] itemNameText: Drag ItemName Text
  - [ ] itemQuantityText: Drag ItemQuantity Text
- [ ] Back in InventoryUIPanel:
  - [ ] itemEntryPrefab: Drag the prefab

### Create BitsDisplay
- [ ] Select UI_Canvas
- [ ] Create child: **UI → Text - TextMeshPro**
  - [ ] Name: `BitsDisplay`
  - [ ] Position: `x = -100, y = -50` (top-right)
  - [ ] Text: "Bits: 0"
- [ ] Add Component: **BitsDisplayUI**
  - [ ] bitsLabel: Drag Text component
  - [ ] showPrefix: true
  - [ ] prefix: "Bits: "
  - [ ] normalColor: white, earnColor: green, spendColor: red

---

## ✅ PHASE 6: Test All Systems (5 min)

### Test Inventory
- [ ] Play scene
- [ ] Console: InventoryService initialized messages ✓
- [ ] Walk over copper_wire pickup → Collected ✓
- [ ] InventoryPanel shows: "Copper Wire x3" ✓
- [ ] (Code in console): `InventoryService.Instance.Add("glass_fragments", 2);`
- [ ] InventoryPanel updates → Shows both items ✓

### Test Currency
- [ ] (Code in console): `CurrencySystem.Instance.Earn(10, "Test");`
- [ ] BitsDisplay updates to "Bits: 10" ✓
- [ ] BitsDisplay flashes green ✓
- [ ] (Code): `CurrencySystem.Instance.Spend(3, "Test");`
- [ ] BitsDisplay updates to "Bits: 7" ✓
- [ ] BitsDisplay flashes red ✓

### Test Trade
- [ ] (Code): `InventoryService.Instance.Add("copper_wire", 2);`
- [ ] Interact with Willy (E key)
- [ ] Console: "NPC willy ready to trade" ✓
- [ ] (Code): 
  ```csharp
  var willy = GameObject.Find("Willy").GetComponent<NPCTrader>();
  var offer = willy.CreateTradeOffer(new Dictionary<string, int> { 
    { "copper_wire", 2 } 
  });
  Debug.Log($"Offer: {offer.totalBitsOffered} bits");
  ```
- [ ] Console shows calculated bits (should be 6: 2 × 2 base × 1.5 multiplier) ✓
- [ ] (Code): `willy.ExecuteTrade(offer);`
- [ ] Inventory: copper_wire removed ✓
- [ ] Currency: +6 bits ✓
- [ ] BitsDisplay: Updates and flashes green ✓

### Test Persistence
- [ ] Play scene
- [ ] Add copper_wire: 5 bits
- [ ] Close/reload scene
- [ ] Inventory persists: copper_wire still there ✓
- [ ] Bits persists: Still shows 5 ✓
- [ ] Walk over pickup again → Not there (persisted as collected) ✓

---

## ✅ PHASE 7: Optional - Add BreakableDebris (5 min)

### Setup Rock Debris
- [ ] Create GameObject: `Rock_Debris_01` (rock sprite/model)
- [ ] Add Box Collider 2D: `isTrigger = true`
- [ ] Add Component: **BreakableDebris**
  - [ ] debrisId: `rock_debris_market_01`
  - [ ] spriteRenderer: Drag sprite renderer
  - [ ] requiredToolId: (leave empty for free debris)
  - [ ] materials: Size 2
    - [ ] [0]: itemId = `sheet_metal`, quantity = 2
    - [ ] [1]: itemId = `glass_fragments`, quantity = 1
  - [ ] debrisCollider: Drag Box Collider 2D

### Test Debris
- [ ] Play scene
- [ ] Interact with rock (E key)
- [ ] Console: "Breaking debris" ✓
- [ ] Inventory: +2 sheet_metal, +1 glass_fragments ✓
- [ ] Debris: Grayed out, uninteractable ✓
- [ ] Reload scene: Debris remains broken ✓

---

## ✅ COMPLETE!

You now have a fully functional:
- ✅ Inventory system (collect items, persist across scenes)
- ✅ Currency system (earn/spend bits, persist in PlayerPrefs)
- ✅ Tool system (equip tools, track equipped state)
- ✅ NPC trading (calculate prices based on preferences)
- ✅ World item pickups (collect items from scene)
- ✅ Breakable debris (mine materials with tools)
- ✅ UI panels (display inventory and currency)

---

## 🚀 Next: Dialogue Integration

Once all systems are confirmed working, integrate with dialogue:

1. **Check inventory in dialogue conditions:**
   ```
   "conditions": ["InventoryService.Instance.Contains(\"copper_wire\", 2)"]
   ```

2. **Remove items in dialogue actions:**
   ```csharp
   InventoryService.Instance.Remove("copper_wire", 2);
   ```

3. **Execute trades in dialogue callbacks:**
   ```csharp
   var offer = npcTrader.CreateTradeOffer(...);
   npcTrader.ExecuteTrade(offer);
   ```

See `SYSTEM_IMPLEMENTATION_GUIDE.md` Phase 6 for detailed dialogue integration.

---

## 📋 Troubleshooting

| Problem | Quick Fix |
|---------|-----------|
| "InventoryService is null" | Add InventoryService GameObject to scene |
| "Unknown item ID" error | Verify item in ItemDatabase.items list |
| Inventory UI blank | Assign itemListLayout in InventoryUIPanel |
| Bits don't persist | CurrencySystem auto-saves (check PlayerPrefs) |
| Pickup respawns | Verify pickupId is unique and set |
| Trade gives 0 bits | Check NPCTradeProfile and ItemDefinition.BaseValue |

---

**Time: ~30 minutes | Complexity: Medium | Status: Ready to go!**
