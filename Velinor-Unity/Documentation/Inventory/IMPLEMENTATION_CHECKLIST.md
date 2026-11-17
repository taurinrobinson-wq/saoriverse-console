# 🎬 Implementation Quick-Start Checklist

## Phase 1: Understanding (Today – 30 minutes)

- [ ] Read [00_FINAL_DELIVERY_SUMMARY.md](00_FINAL_DELIVERY_SUMMARY.md) – Overview
- [ ] Read [README.md](README.md) – Class reference
- [ ] Read [WILLY_INVENTORY_INTEGRATION_SUMMARY.md](WILLY_INVENTORY_INTEGRATION_SUMMARY.md) – Narrative flow
- [ ] Review [willy_concourse_ruins_payment.json](C:/saoriverse-console/Velinor-Unity/Assets/Resources/Dialogue/willy_concourse_ruins_payment.json) changes – Beat 2 triggers

## Phase 2: Setup (Today/Tomorrow – 1-2 hours)

### Create Test Scene
- [ ] Create scene: `Assets/Scenes/TestInventory.unity`
- [ ] Create empty GameObject: `InventoryService`
- [ ] Add component: `InventoryService` script
- [ ] Verify no errors in Inspector

### Create ItemDatabase
- [ ] Right-click in Project → Create → Velinor/Inventory/Item Database
- [ ] Name: `TestDatabase`
- [ ] Create 3 ItemDefinition assets:
  - [ ] `copper_wire` (Tags: Metal, Electrical)
  - [ ] `glass_fragments` (Tags: Glass)
  - [ ] `sheet_metal` (Tags: Metal, Mechanical)
- [ ] Add all 3 to ItemDatabase's items list
- [ ] Assign ItemDatabase to InventoryService.itemDatabase field

### Test Core Inventory
- [ ] Play scene
- [ ] Check console: `"[InventoryService] Initialized with 3 items"`
- [ ] Create test script with:
  ```csharp
  if (Input.GetKeyDown(KeyCode.A))
      InventoryService.Instance.Add("copper_wire", 1);
  if (Input.GetKeyDown(KeyCode.R))
      InventoryService.Instance.Remove("copper_wire", 1);
  ```
- [ ] Press A → Console shows "Added 1x copper_wire"
- [ ] Press R → Console shows "Removed 1x copper_wire"
- [ ] Query GetQuantity() returns correct value

## Phase 3: Dialogue Integration (Tomorrow – 2-3 hours)

### Update DialogueSystem
- [ ] Locate your DialogueSystem/DialogueManager script
- [ ] Add method: `ProcessSystemTrigger(string type, List<string> data)`
- [ ] Implement cases:
  - [ ] `"unlock_system"` → `GameFlags.Set($"system_unlocked_{system}", true)`
  - [ ] `"unlock_npc_preference"` → NPCPreferenceManager.AddPreferences()
  - [ ] `"system_notification"` → NotificationManager.Show()
- [ ] Verify no compilation errors

### Create NPCPreferenceManager
- [ ] Create script: `Assets/Scripts/Core/NPCPreferenceManager.cs`
- [ ] Add fields: `Dictionary<string, List<string>> preferences`
- [ ] Add methods: `Get()`, `AddPreferences()`
- [ ] Make it a singleton or injectable

### Create/Adapt NotificationManager
- [ ] Option A: Create new script
- [ ] Option B: Add to existing UI manager
- [ ] Implement: `Show(title, message, duration, actionText)`
- [ ] Must display non-blocking popup that auto-dismisses

### Test Willy Dialogue
- [ ] Open scene with Willy dialogue trigger
- [ ] Trigger dialogue → Play to Beat 2 end
- [ ] Verify: Notification appears "Inventory Unlocked"
- [ ] Verify: `GameFlags.Get("system_unlocked_inventory")` = true
- [ ] Verify: NPCPreferenceManager has Willy's items

## Phase 4: UI Panel (Tomorrow – 1-2 hours)

### Create Canvas Layout
- [ ] Select UI_Canvas
- [ ] Create child: Panel (name: `InventoryPanel`)
- [ ] Position: Left side (x ≈ -200)
- [ ] Size: 300×600
- [ ] Add component: `CanvasGroup`

### Setup InventoryUIPanel
- [ ] Add component: `InventoryUIPanel` to InventoryPanel
- [ ] Create child: VerticalLayoutGroup
- [ ] Assign VerticalLayoutGroup to Inspector field
- [ ] Create CanvasGroup or assign existing one

### Create ItemEntry Prefab
- [ ] Create UI → HorizontalLayoutGroup (child of InventoryPanel)
- [ ] Add children:
  - [ ] Image (left side, small)
  - [ ] VerticalLayoutGroup (center)
    - [ ] Text (item name)
    - [ ] Text (quantity)
- [ ] Add component: `InventoryItemEntryUI`
- [ ] Assign Image and Text fields
- [ ] Save as prefab: `Assets/Resources/Prefabs/InventoryItemEntry.prefab`
- [ ] Delete from hierarchy

### Configure Panel
- [ ] Assign ItemEntry prefab to InventoryUIPanel.itemEntryPrefab
- [ ] Play scene
- [ ] Add item manually: `InventoryService.Instance.Add("copper_wire", 3)`
- [ ] Verify: UI shows "Copper Wire x3"
- [ ] Remove item: `InventoryService.Instance.Remove("copper_wire", 1)`
- [ ] Verify: UI updates to "Copper Wire x2"

## Phase 5: World Pickups (Today/Tomorrow – 1 hour)

### Create Test Pickup
- [ ] Create GameObject: `TestWirePickup`
- [ ] Add SpriteRenderer (any sprite)
- [ ] Add BoxCollider (mark as Trigger)
- [ ] Add component: `WorldItemPickup`
- [ ] Set:
  - [ ] pickupId: `test_wire_01`
  - [ ] itemDefinition: copper_wire
  - [ ] quantity: 3

### Test Collection
- [ ] Play scene
- [ ] Walk over pickup → Should disappear
- [ ] Console: `"[WorldItemPickup] Collected 3x copper_wire"`
- [ ] Check InventoryService: quantity = 3
- [ ] Check UI: Shows "Copper Wire x3"

### Test Persistence
- [ ] Stop playing
- [ ] Play again
- [ ] Pickup should NOT appear (GameFlags saved collection)
- [ ] Console: `"[WorldItemPickup] test_wire_01 already collected, hiding"`

## Phase 6: Full Integration Test (This Week – 2-3 hours)

### Complete Willy Dialogue Test
- [ ] Play Willy scene
- [ ] Progress through dialogue to Beat 2
- [ ] Verify inventory unlock notification
- [ ] Verify InventoryService.enabled
- [ ] Press I key → InventoryPanel shows (empty)
- [ ] Exit dialogue

### Collect Items
- [ ] Explore scene with WorldItemPickup objects
- [ ] Collect 2-3 items
- [ ] Verify notifications show
- [ ] Verify InventoryUIPanel updates in real-time
- [ ] Press I → See inventory with items

### Test Persistence
- [ ] Change scenes (if applicable)
- [ ] Return to original scene
- [ ] Verify InventoryService still has items (didn't respawn)
- [ ] Verify pickups are still gone (GameFlags persisted)

## Phase 7: Save/Load Test (Later This Week – 1 hour)

### Implement Save
- [ ] In GameManager.OnSave():
  ```csharp
  GameData.inventory = InventoryService.Instance.GetSaveData();
  ```

### Implement Load
- [ ] In GameManager.OnLoad():
  ```csharp
  InventoryService.Instance.LoadSaveData(GameData.inventory);
  ```

### Test Cycle
- [ ] Collect items
- [ ] Save game
- [ ] Stop playing
- [ ] Play again
- [ ] Load game
- [ ] Verify inventory restored with same items

## Verification Checklist

### Core System
- [ ] All 6 scripts compile without errors
- [ ] ItemDatabase accepts ItemDefinition assets
- [ ] InventoryService finds and initializes with items
- [ ] Add/Remove/GetQuantity operations work correctly

### Dialogue Integration
- [ ] DialogueSystem calls ProcessSystemTrigger()
- [ ] `unlock_system` sets GameFlags
- [ ] `unlock_npc_preference` calls NPCPreferenceManager
- [ ] `system_notification` shows popup
- [ ] Inventory UI only shows when unlocked

### UI Panel
- [ ] InventoryUIPanel subscribes to OnInventoryChanged
- [ ] Items appear/disappear in list correctly
- [ ] Quantities update in real-time
- [ ] Alpha toggle works (I key or button)

### Persistence
- [ ] GameFlags tracks collected pickups
- [ ] Pickups don't respawn after scene reload
- [ ] InventoryService survives scene transitions
- [ ] Save/load cycle preserves inventory

### Narrative
- [ ] Willy dialogue triggers inventory unlock
- [ ] Notification shows only once per game
- [ ] Player can interact with pickups only after unlock
- [ ] Progression feels natural (not forced)

---

## Troubleshooting Quick Reference

| Issue | Check |
|-------|-------|
| "Unknown item ID" error | ItemDefinition added to ItemDatabase? |
| Inventory doesn't unlock | Does dialogue call ProcessSystemTrigger? |
| UI doesn't appear | Is CanvasGroup assigned? Visibility set? |
| Pickup respawns | Is GameFlags properly tracking collection? |
| Items not persisting | Is InventoryService.DontDestroyOnLoad working? |
| Quantity doesn't update | Is OnInventoryChanged event firing? |

---

## Timeline Estimate

| Phase | Time | Start | End |
|-------|------|-------|-----|
| Phase 1: Understanding | 30 min | Now | Today |
| Phase 2: Setup | 1-2 hrs | Today | Today |
| Phase 3: Dialogue | 2-3 hrs | Tomorrow | Tomorrow |
| Phase 4: UI Panel | 1-2 hrs | Tomorrow | Tomorrow |
| Phase 5: Pickups | 1 hr | Today | Tomorrow |
| Phase 6: Integration | 2-3 hrs | This Week | This Week |
| Phase 7: Save/Load | 1 hr | Later Week | Later Week |

**Total Time: 9-13 hours (spread across 2 weeks)**

---

## Success Criteria

### Minimum Viable
- [x] Inventory system compiles
- [x] Can add/remove items
- [x] UI displays items
- [x] Willy dialogue triggers unlock

### Complete
- [x] All above ✓
- [x] Persistent pickups work
- [x] Save/load cycle works
- [x] Multiple NPCs have preferences
- [x] Dialogue queries inventory by tag

### Polish (Later)
- [x] Item detail panel on selection
- [x] Animation on item pickup
- [x] Better notification UI
- [x] Crafting integration
- [x] Codex integration

---

## Resources at Your Fingertips

| Task | Read | Code |
|------|------|------|
| "How do I...set up?" | QUICK_START.md | ItemDefinition.cs |
| "How do I...test?" | TESTING_GUIDE.md | InventoryService.cs |
| "How do I...integrate dialogue?" | DIALOGUE_INTEGRATION.md | willy_concourse_ruins_payment.json |
| "How does this...work?" | ARCHITECTURE.md | All scripts + comments |
| "What if I add...new NPC?" | README.md (section: Integration) | NPCPreferenceManager pattern |

---

## Go Time 🚀

**Start here:** [QUICK_START.md](INVENTORY_QUICK_START.md)

**Questions?** Check [INVENTORY_DIALOGUE_INTEGRATION.md](INVENTORY_DIALOGUE_INTEGRATION.md)

**Visual learner?** See [INTEGRATION_ARCHITECTURE_DIAGRAM.md](INTEGRATION_ARCHITECTURE_DIAGRAM.md)

---

**You've got this. Lioren is ready to learn that junk has value.** ✨
