# UI Implementation Guide - Inventory/Currency/Trading

Complete this guide to add all UI components to your UI_Canvas prefab. **Estimated time: 15-20 minutes.**

---

## 📋 Overview

Three UI systems need to be added to your UI_Canvas:

1. **BitsDisplayUI** (showing player's Bits balance) — Already exists ✓
2. **InventoryPanelUI** (showing items player has)
3. **TradeUIPanel** (showing NPC trade interface)

---

## ✅ STEP 1: Create UI Prefabs

### Create InventoryItemEntry Prefab

1. **Create new GameObject**
   - Right-click in Hierarchy → 2D Object → Panel
   - Name: `InventoryItemEntry`
   - Position: (0, 0, 0)
   - Size: (100, 100)

2. **Add child elements:**
   - Image (Icon)
     - Name: `ItemIcon`
     - Size: (80, 80)
     - Anchor: top-left
     - Offset: (10, -10)
   
   - TextMeshPro (Item Name)
     - Name: `ItemName`
     - Text: "Item Name"
     - Size: (200, 30)
     - Anchor: top-left
     - Offset: (100, -10)
     - Font Size: 16
   
   - TextMeshPro (Quantity)
     - Name: `Quantity`
     - Text: "x1"
     - Size: (60, 30)
     - Anchor: bottom-right
     - Offset: (-10, 10)
     - Font Size: 14
     - Color: Yellow

3. **Add Component**
   - Click "Add Component"
   - Search for `InventoryItemEntryUI`
   - Assign:
     - **Item Icon** → ItemIcon (Image)
     - **Item Name** → ItemName (TextMeshProUGUI)
     - **Quantity Label** → Quantity (TextMeshProUGUI)

4. **Save as Prefab**
   - Drag from Hierarchy to `Assets/Prefabs/UI/`
   - Name: `InventoryItemEntry.prefab`

---

### Create TradeItemEntry Prefab

1. **Create new GameObject**
   - Right-click in Hierarchy → 2D Object → Panel
   - Name: `TradeItemEntry`
   - Size: (150, 60)

2. **Add child elements:**
   - Image (Icon)
     - Name: `ItemIcon`
     - Size: (50, 50)
     - Anchor: left
   
   - TextMeshPro (Item Name)
     - Name: `ItemName`
     - Text: "Item Name"
     - Size: (200, 30)
     - Anchor: center
     - Font Size: 14
   
   - TextMeshPro (Quantity)
     - Name: `Quantity`
     - Text: "x1"
     - Size: (60, 30)
     - Anchor: right
     - Font Size: 12
     - Color: Green

3. **Add Component**
   - Click "Add Component"
   - Search for `TradeItemEntryUI`
   - Assign:
     - **Item Icon** → ItemIcon
     - **Item Name Label** → ItemName
     - **Quantity Label** → Quantity

4. **Save as Prefab**
   - Drag to `Assets/Prefabs/UI/`
   - Name: `TradeItemEntry.prefab`

---

## ✅ STEP 2: Setup Inventory Panel UI

### In Your UI_Canvas Prefab

1. **Create a Panel for Inventory**
   - Right-click in Hierarchy → 2D Object → Panel
   - Name: `InventoryPanel`
   - Parent: UI_Canvas
   - Position: (0, 0, 0)
   - Size: (400, 600)
   - Anchor: left (or customize as needed)
   - Color: Semi-transparent dark (e.g., rgba 0,0,0,0.7)

2. **Add child containers:**

   **A. Header**
   - Create Panel
   - Name: `Header`
   - Size: (400, 50)
   - Anchor: top-stretch
   - Add TextMeshPro ("Inventory")
   - Font Size: 24
   - Alignment: Center

   **B. Scroll View (for items)**
   - Create Scroll View
   - Name: `ItemsScroll`
   - Parent: InventoryPanel
   - Size: (400, 550)
   - Anchor: fill
   - Offset: (0, 0, 0, -50)
   - **In Viewport/Content:**
     - Create Layout Group
     - Name: `ItemsContainer`
     - Component: Grid Layout Group
       - Cell Size: (100, 100)
       - Spacing: (10, 10)
       - Constraint: Flexible (or fixed columns = 3)

   **C. Empty Label (shown when inventory is empty)**
   - Create TextMeshPro
   - Name: `EmptyLabel`
   - Text: "Inventory Empty"
   - Size: (400, 100)
   - Anchor: center
   - Font Size: 18
   - Alignment: Center
   - Color: Gray

3. **Add InventoryPanelUI Component**
   - Select InventoryPanel
   - Click "Add Component"
   - Search for `InventoryPanelUI`
   - Assign:
     - **Item Container** → ItemsContainer (the Layout Group)
     - **Item Entry Prefab** → InventoryItemEntry.prefab (drag from Assets)
     - **Empty Inventory Label** → EmptyLabel
     - **Auto Hide When Empty** → ✓ (checked)

4. **Test Connection**
   - Play scene
   - Check console for "[InventoryPanelUI]" messages
   - Should show 0 items initially

---

## ✅ STEP 3: Setup Trade UI Panel

### In Your UI_Canvas Prefab

1. **Create a Panel for Trading**
   - Right-click in Hierarchy → 2D Object → Panel
   - Name: `TradePanel`
   - Parent: UI_Canvas
   - Position: (400, 0, 0) (offset to the right)
   - Size: (400, 600)
   - Color: Semi-transparent dark
   - **Initially deactivated** (should be invisible until trade starts)

2. **Add child components:**

   **A. Header**
   - Panel
   - Name: `Header`
   - Size: (400, 50)
   - TextMeshPro ("Trade with NPC")
   - Name: `NPCNameLabel`
   - Font Size: 20

   **B. Wanted Items Section**
   - Panel
   - Name: `WantedSection`
   - Size: (400, 200)
   - Position: (0, 400, 0)
   - TextMeshPro Label ("NPC Wants:")
   - Scroll View with ItemsContainer
     - Component: Vertical Layout Group
     - Child Force Expand: Width checked
     - Spacing: 5

   **C. Offered Items Section**
   - Panel
   - Name: `OfferedSection`
   - Size: (400, 200)
   - Position: (0, 150, 0)
   - TextMeshPro Label ("NPC Offers:")
   - Scroll View with ItemsContainer
     - Component: Vertical Layout Group

   **D. Status & Trade Button**
   - TextMeshPro ("Ready to trade!")
   - Name: `StatusLabel`
   - Button ("Trade")
   - Name: `TradeButton`
   - Size: (200, 50)
   - Anchor: bottom-center

3. **Add TradeUIPanel Component**
   - Select TradePanel
   - Click "Add Component"
   - Search for `TradeUIPanel`
   - Assign:
     - **NPC Name Label** → NPCNameLabel
     - **Wanted Items Container** → (WantedSection's ItemsContainer)
     - **Offered Items Container** → (OfferedSection's ItemsContainer)
     - **Trade Item Entry Prefab** → TradeItemEntry.prefab
     - **Trade Button** → TradeButton
     - **Trade Button Label** → TradeButton's TextMeshPro
     - **Status Label** → StatusLabel
     - **Panel Canvas Group** → (the TradePanel's CanvasGroup - add if missing)

---

## ✅ STEP 4: Wire Up BitsDisplay

BitsDisplayUI already exists, but verify it's set up:

1. **Find BitsDisplay in hierarchy** (or create if missing)
   - Position: top-right corner
   - Component: BitsDisplayUI
   - Assigned TextMeshProUGUI: Shows current Bits balance

2. **Verify Assignment:**
   - **Bits Label** → TextMeshPro showing "Bits: 0"
   - **Show Prefix** → ✓ checked
   - **Prefix** → "Bits: "
   - **Normal Color** → White
   - **Earn Color** → Green
   - **Spend Color** → Red

---

## ✅ STEP 5: Wire NPCTrader to TradePanel

### In NPCTrader.cs Script

The TradeUIPanel needs to be told to show when an NPC is interacted with.

1. **Find NPCTrader.cs**
   - Path: `Assets/Scripts/Interactions/NPCTrader.cs`

2. **Add this code to the Interact method:**

```csharp
public void Interact(GameObject player)
{
    // ... existing code ...

    // Show trade UI
    var tradePanel = FindObjectOfType<TradeUIPanel>();
    if (tradePanel != null)
    {
        tradePanel.ShowTradeUI(this);
    }
}
```

3. **Add a way to close the panel** (e.g., ESC key or a close button)

```csharp
private void Update()
{
    if (Input.GetKeyDown(KeyCode.Escape))
    {
        var tradePanel = FindObjectOfType<TradeUIPanel>();
        if (tradePanel != null)
        {
            tradePanel.HideTradeUI();
        }
    }
}
```

---

## ✅ STEP 6: Testing

### Test Inventory Display

1. **Play scene**
2. **Console should show:**
   ```
   [InventoryPanelUI] Initialized
   [InventoryService] Initialized and marked persistent
   ```
3. **Inventory panel should show "Inventory Empty"**

### Test Adding Items

1. **In Play mode, add item via console:**
   - Open Debug Console
   - Run: `InventoryService.Instance.AddItem("copper_wire", 3);`
   - **Inventory panel should show 3x Copper Wire**

2. **Test quantity update:**
   - Run: `InventoryService.Instance.AddItem("copper_wire", 2);`
   - **Should show 5x Copper Wire**

3. **Test removal:**
   - Run: `InventoryService.Instance.RemoveItem("copper_wire", 2);`
   - **Should show 3x Copper Wire**

### Test Trading

1. **Navigate to NPC (e.g., Willy)**
2. **Interact with NPC**
3. **Trade panel should appear showing:**
   - NPC name
   - Items they want
   - Bits they offer
   - Trade button (disabled until you have items)

4. **Add required items:**
   - Run: `InventoryService.Instance.AddItem("copper_wire", 1);`
   - **Trade button should become enabled**

5. **Click Trade**
   - **Items removed from inventory**
   - **Bits added to balance**
   - **Status shows "Trade complete!"**

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "InventoryPanelUI not found" in console | Make sure InventoryPanelUI component is added to InventoryPanel GameObject |
| Items not showing | Verify ItemsContainer is assigned correctly (should be the Content inside Scroll View) |
| Trade panel doesn't appear | Check that TradeUIPanel component is on TradePanel, and NPCTrader calls `ShowTradeUI()` in Interact() |
| "ItemDatabase is null" | Verify InventoryService has ItemDatabase assigned in Inspector |
| Items show but no icon | Add icon sprites to ItemDefinition assets (Icon field) |

---

## 📁 Files Created

- `InventoryPanelUI.cs` — Main inventory panel controller
- `InventoryItemEntryUI.cs` — Individual item display
- `TradeUIPanel.cs` — NPC trading interface
- `TradeItemEntryUI.cs` — Individual trade item display
- `InventoryItemEntry.prefab` — Prefab for inventory items
- `TradeItemEntry.prefab` — Prefab for trade items

---

## 🎯 Next Steps

1. ✅ Create all prefabs as described in STEP 1
2. ✅ Setup InventoryPanel in UI_Canvas
3. ✅ Setup TradePanel in UI_Canvas
4. ✅ Verify BitsDisplay is working
5. ✅ Wire NPCTrader to TradePanel
6. ✅ Run all tests from STEP 6
7. → Proceed to **Scene Setup** (create singleton GameObjects in InsideMarket_02)

---

**Time estimate to complete: 15-20 minutes**

For detailed troubleshooting, see SYSTEM_IMPLEMENTATION_GUIDE.md Phase 4 (UI Setup).
