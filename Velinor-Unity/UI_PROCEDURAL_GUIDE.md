# Unity UI Implementation - Procedural Guide for AI Editor

This guide is structured as explicit procedural steps for AI/Agent execution.

---

## PHASE 1: CREATE INVENTORYITEMENTRY PREFAB

### Step 1.1: Create Base Panel
- **Action:** Right-click on "UI_Canvas" in Hierarchy
- **Select:** UI → Panel
- **Action:** Rename to: `InventoryItemEntry`
- **Action:** In Inspector, find RectTransform
  - Set Width: 100
  - Set Height: 100
  - Set Anchor Preset: Center
  - Set Position X: 0, Y: 0

### Step 1.2: Add Icon Image
- **Action:** Right-click on "InventoryItemEntry" in Hierarchy
- **Select:** UI → Image
- **Action:** Rename to: `ItemIcon`
- **Action:** In Inspector, find RectTransform
  - Set Width: 80
  - Set Height: 80
  - Set Anchor Preset: Top-Left
  - Set Pos X: 10, Pos Y: -10
- **Action:** In Inspector, find Image component
  - Leave Color as default (white)

### Step 1.3: Add Item Name Text
- **Action:** Right-click on "InventoryItemEntry" in Hierarchy
- **Select:** TextMeshPro - Text
- **Action:** Rename to: `ItemName`
- **Action:** In Inspector, find TextMeshProUGUI component
  - Set Text: "Item Name"
  - Set Font Size: 16
- **Action:** In Inspector, find RectTransform
  - Set Width: 120
  - Set Height: 30
  - Set Anchor Preset: Top-Left
  - Set Pos X: 90, Pos Y: -10

### Step 1.4: Add Quantity Label
- **Action:** Right-click on "InventoryItemEntry" in Hierarchy
- **Select:** TextMeshPro - Text
- **Action:** Rename to: `Quantity`
- **Action:** In Inspector, find TextMeshProUGUI component
  - Set Text: "x1"
  - Set Font Size: 14
  - Set Color: (Yellow - pick yellow in color picker)
- **Action:** In Inspector, find RectTransform
  - Set Width: 60
  - Set Height: 30
  - Set Anchor Preset: Bottom-Right
  - Set Pos X: -10, Pos Y: 10

### Step 1.5: Add InventoryItemEntryUI Script Component
- **Action:** Select "InventoryItemEntry" in Hierarchy
- **Action:** In Inspector, click "Add Component"
- **Action:** Search for: `InventoryItemEntryUI`
- **Action:** Click to add it
- **Action:** In the InventoryItemEntryUI component fields:
  - Drag "ItemIcon" from Hierarchy → **Item Icon** field
  - Drag "ItemName" from Hierarchy → **Item Name** field
  - Drag "Quantity" from Hierarchy → **Quantity Label** field
  - Leave **Show Quantity Prefix** checked
  - Leave **Quantity Prefix** as "x"

### Step 1.6: Save as Prefab
- **Action:** Drag "InventoryItemEntry" from Hierarchy to Assets/Prefabs/UI/ folder
- **Result:** File created: `Assets/Prefabs/UI/InventoryItemEntry.prefab`
- **Action:** Delete "InventoryItemEntry" from Hierarchy (prefab saved, instance no longer needed)

---

## PHASE 2: CREATE TRADEITEMENTRY PREFAB

### Step 2.1: Create Base Panel
- **Action:** Right-click on "UI_Canvas" in Hierarchy
- **Select:** UI → Panel
- **Action:** Rename to: `TradeItemEntry`
- **Action:** In Inspector, find RectTransform
  - Set Width: 150
  - Set Height: 60
  - Set Position X: 0, Y: 0

### Step 2.2: Add Icon Image
- **Action:** Right-click on "TradeItemEntry" in Hierarchy
- **Select:** UI → Image
- **Action:** Rename to: `ItemIcon`
- **Action:** In Inspector, find RectTransform
  - Set Width: 50
  - Set Height: 50
  - Set Anchor Preset: Left
  - Set Pos X: 5, Pos Y: 0

### Step 2.3: Add Item Name Text
- **Action:** Right-click on "TradeItemEntry" in Hierarchy
- **Select:** TextMeshPro - Text
- **Action:** Rename to: `ItemName`
- **Action:** In Inspector, find TextMeshProUGUI component
  - Set Text: "Item Name"
  - Set Font Size: 14
- **Action:** In Inspector, find RectTransform
  - Set Width: 200
  - Set Height: 40
  - Set Anchor Preset: Center
  - Set Pos X: 0, Pos Y: 0

### Step 2.4: Add Quantity Label
- **Action:** Right-click on "TradeItemEntry" in Hierarchy
- **Select:** TextMeshPro - Text
- **Action:** Rename to: `Quantity`
- **Action:** In Inspector, find TextMeshProUGUI component
  - Set Text: "x1"
  - Set Font Size: 12
  - Set Color: Green
- **Action:** In Inspector, find RectTransform
  - Set Width: 60
  - Set Height: 40
  - Set Anchor Preset: Right
  - Set Pos X: -10, Pos Y: 0

### Step 2.5: Add TradeItemEntryUI Script Component
- **Action:** Select "TradeItemEntry" in Hierarchy
- **Action:** In Inspector, click "Add Component"
- **Action:** Search for: `TradeItemEntryUI`
- **Action:** Click to add it
- **Action:** In the TradeItemEntryUI component fields:
  - Drag "ItemIcon" from Hierarchy → **Item Icon** field
  - Drag "ItemName" from Hierarchy → **Item Name Label** field
  - Drag "Quantity" from Hierarchy → **Quantity Label** field

### Step 2.6: Save as Prefab
- **Action:** Drag "TradeItemEntry" from Hierarchy to Assets/Prefabs/UI/ folder
- **Result:** File created: `Assets/Prefabs/UI/TradeItemEntry.prefab`
- **Action:** Delete "TradeItemEntry" from Hierarchy

---

## PHASE 3: CREATE INVENTORYPANEL IN CANVAS

### Step 3.1: Create Main Panel
- **Action:** Right-click on "UI_Canvas" in Hierarchy
- **Select:** UI → Panel
- **Action:** Rename to: `InventoryPanel`
- **Action:** In Inspector, find RectTransform
  - Set Width: 400
  - Set Height: 600
  - Set Anchor Preset: Left
  - Set Pos X: 0, Pos Y: 0
  - Set Pivot X: 0, Y: 1
- **Action:** In Inspector, find Image component
  - Set Color: (Semi-transparent dark) → R: 0, G: 0, B: 0, A: 0.7

### Step 3.2: Create Header Panel
- **Action:** Right-click on "InventoryPanel" in Hierarchy
- **Select:** UI → Panel
- **Action:** Rename to: `Header`
- **Action:** In Inspector, find RectTransform
  - Set Width: 400
  - Set Height: 50
  - Set Anchor Preset: Top-Stretch
- **Action:** In Inspector, find Image component
  - Set Color: (Dark gray) → R: 0.2, G: 0.2, B: 0.2, A: 1

### Step 3.3: Add Header Text
- **Action:** Right-click on "Header" in Hierarchy
- **Select:** TextMeshPro - Text
- **Action:** Rename to: `HeaderLabel`
- **Action:** In Inspector, find TextMeshProUGUI component
  - Set Text: "Inventory"
  - Set Font Size: 20
  - Set Alignment: Center
- **Action:** In Inspector, find RectTransform
  - Set Anchor Preset: Center

### Step 3.4: Create Scroll View for Items
- **Action:** Right-click on "InventoryPanel" in Hierarchy
- **Select:** UI → Scroll View
- **Action:** Rename to: `ItemsScroll`
- **Action:** In Inspector, find RectTransform
  - Set Width: 380
  - Set Height: 500
  - Set Anchor Preset: Bottom-Stretch
  - Set Pos Y: 50
  - Set Offset Left: 10, Right: 10, Bottom: 10
- **Note:** Scroll View automatically creates "Viewport" and "Content" children

### Step 3.5: Setup Scroll View Content
- **Action:** Select the "Content" object under ItemsScroll in Hierarchy
- **Action:** Rename it to: `ItemsContainer`
- **Action:** In Inspector, find RectTransform
  - Set Anchor Preset: Top-Center
  - Set Pivot: 0.5, 1
- **Action:** In Inspector, click "Add Component"
- **Action:** Search for: `Grid Layout Group`
- **Action:** Click to add it
- **Action:** In the Grid Layout Group component:
  - Set Cell Size X: 100, Y: 100
  - Set Spacing X: 10, Y: 10
  - Set Child Force Expand Width: OFF
  - Set Child Force Expand Height: OFF
  - Set Constraint: Flexible

### Step 3.6: Create Empty State Label
- **Action:** Right-click on "InventoryPanel" in Hierarchy
- **Select:** TextMeshPro - Text
- **Action:** Rename to: `EmptyLabel`
- **Action:** In Inspector, find TextMeshProUGUI component
  - Set Text: "Inventory Empty"
  - Set Font Size: 18
  - Set Color: Gray
  - Set Alignment: Center
- **Action:** In Inspector, find RectTransform
  - Set Anchor Preset: Center
  - Set Width: 300
  - Set Height: 100

### Step 3.7: Add InventoryPanelUI Script Component
- **Action:** Select "InventoryPanel" in Hierarchy
- **Action:** In Inspector, click "Add Component"
- **Action:** Search for: `InventoryPanelUI`
- **Action:** Click to add it
- **Action:** In the InventoryPanelUI component fields:
  - Drag "ItemsContainer" from Hierarchy → **Item Container** field
  - Drag "InventoryItemEntry.prefab" from Assets/Prefabs/UI/ → **Item Entry Prefab** field
  - Drag "EmptyLabel" from Hierarchy → **Empty Inventory Label** field
  - Check **Auto Hide When Empty**: enabled

### Step 3.8: Add Canvas Group (for fading)
- **Action:** Select "InventoryPanel" in Hierarchy
- **Action:** In Inspector, click "Add Component"
- **Action:** Search for: `Canvas Group`
- **Action:** Click to add it
- **Action:** Leave default values

---

## PHASE 4: CREATE TRADEPANEL IN CANVAS

### Step 4.1: Create Main Trade Panel
- **Action:** Right-click on "UI_Canvas" in Hierarchy
- **Select:** UI → Panel
- **Action:** Rename to: `TradePanel`
- **Action:** In Inspector, find RectTransform
  - Set Width: 400
  - Set Height: 600
  - Set Anchor Preset: Right
  - Set Pos X: -200, Pos Y: 0
  - Set Pivot X: 1, Y: 1
- **Action:** In Inspector, find Image component
  - Set Color: (Semi-transparent dark) → R: 0, G: 0, B: 0, A: 0.7
- **Action:** In Inspector, find Canvas Group component (if missing, Add Component)
  - **Alpha**: 1
  - **Blocks Raycasts**: checked

### Step 4.2: Create Header
- **Action:** Right-click on "TradePanel" in Hierarchy
- **Select:** UI → Panel
- **Action:** Rename to: `Header`
- **Action:** In Inspector, find RectTransform
  - Set Width: 400
  - Set Height: 50
  - Set Anchor Preset: Top-Stretch

### Step 4.3: Add Header Text
- **Action:** Right-click on "Header" in Hierarchy
- **Select:** TextMeshPro - Text
- **Action:** Rename to: `NPCNameLabel`
- **Action:** In Inspector, find TextMeshProUGUI component
  - Set Text: "Trade with NPC"
  - Set Font Size: 20
  - Set Alignment: Center
- **Action:** In Inspector, find RectTransform
  - Set Anchor Preset: Center

### Step 4.4: Create Wanted Section
- **Action:** Right-click on "TradePanel" in Hierarchy
- **Select:** UI → Panel
- **Action:** Rename to: `WantedSection`
- **Action:** In Inspector, find RectTransform
  - Set Width: 380
  - Set Height: 150
  - Set Anchor Preset: Top-Center
  - Set Pos Y: -60
  - Set Offset Left: 10, Right: 10
- **Action:** Add child TextMeshPro - Text
  - Rename to: `WantedLabel`
  - Set Text: "NPC Wants:"
  - Set Font Size: 14
  - Set Anchor Preset: Top-Left
  - Set Pos X: 5, Pos Y: -5

### Step 4.5: Create Wanted Items Scroll View
- **Action:** Right-click on "WantedSection" in Hierarchy
- **Select:** UI → Scroll View
- **Action:** Rename to: `WantedItemsScroll`
- **Action:** In Inspector, find RectTransform
  - Set Anchor Preset: Bottom-Stretch
  - Set Pos Y: 30
  - Set Offset Left: 0, Right: 0, Bottom: 0, Top: 30
- **Action:** Select the "Content" child under WantedItemsScroll
- **Action:** Rename to: `WantedItemsContainer`
- **Action:** In Inspector, click "Add Component"
- **Action:** Search for: `Vertical Layout Group`
- **Action:** Click to add it
- **Action:** In the Vertical Layout Group:
  - Set Spacing: 5
  - Set Child Force Expand Width: OFF
  - Set Child Force Expand Height: OFF

### Step 4.6: Create Offered Section
- **Action:** Right-click on "TradePanel" in Hierarchy
- **Select:** UI → Panel
- **Action:** Rename to: `OfferedSection`
- **Action:** In Inspector, find RectTransform
  - Set Width: 380
  - Set Height: 150
  - Set Anchor Preset: Center
  - Set Pos Y: 0
  - Set Offset Left: 10, Right: 10
- **Action:** Add child TextMeshPro - Text
  - Rename to: `OfferedLabel`
  - Set Text: "NPC Offers:"
  - Set Font Size: 14
  - Set Anchor Preset: Top-Left
  - Set Pos X: 5, Pos Y: -5

### Step 4.7: Create Offered Items Scroll View
- **Action:** Right-click on "OfferedSection" in Hierarchy
- **Select:** UI → Scroll View
- **Action:** Rename to: `OfferedItemsScroll`
- **Action:** In Inspector, find RectTransform
  - Set Anchor Preset: Bottom-Stretch
  - Set Pos Y: 30
  - Set Offset Left: 0, Right: 0, Bottom: 0, Top: 30
- **Action:** Select the "Content" child under OfferedItemsScroll
- **Action:** Rename to: `OfferedItemsContainer`
- **Action:** In Inspector, click "Add Component"
- **Action:** Search for: `Vertical Layout Group`
- **Action:** Click to add it
- **Action:** In the Vertical Layout Group:
  - Set Spacing: 5
  - Set Child Force Expand Width: OFF
  - Set Child Force Expand Height: OFF

### Step 4.8: Create Status Label
- **Action:** Right-click on "TradePanel" in Hierarchy
- **Select:** TextMeshPro - Text
- **Action:** Rename to: `StatusLabel`
- **Action:** In Inspector, find TextMeshProUGUI component
  - Set Text: "Ready to trade!"
  - Set Font Size: 14
- **Action:** In Inspector, find RectTransform
  - Set Width: 350
  - Set Height: 40
  - Set Anchor Preset: Bottom-Center
  - Set Pos Y: 60

### Step 4.9: Create Trade Button
- **Action:** Right-click on "TradePanel" in Hierarchy
- **Select:** UI → Button
- **Action:** Rename to: `TradeButton`
- **Action:** In Inspector, find RectTransform
  - Set Width: 200
  - Set Height: 50
  - Set Anchor Preset: Bottom-Center
  - Set Pos Y: 10
- **Action:** Select the "Text" child under TradeButton
- **Action:** In Inspector, find TextMeshProUGUI component
  - Set Text: "Trade"
  - Set Font Size: 16

### Step 4.10: Add TradeUIPanel Script Component
- **Action:** Select "TradePanel" in Hierarchy
- **Action:** In Inspector, click "Add Component"
- **Action:** Search for: `TradeUIPanel`
- **Action:** Click to add it
- **Action:** In the TradeUIPanel component fields:
  - Drag "NPCNameLabel" from Hierarchy → **NPC Name Label** field
  - Drag "WantedItemsContainer" from Hierarchy → **Wanted Items Container** field
  - Drag "OfferedItemsContainer" from Hierarchy → **Offered Items Container** field
  - Drag "TradeItemEntry.prefab" from Assets/Prefabs/UI/ → **Trade Item Entry Prefab** field
  - Drag "TradeButton" from Hierarchy → **Trade Button** field
  - Drag the "Text" child of TradeButton from Hierarchy → **Trade Button Label** field
  - Drag "StatusLabel" from Hierarchy → **Status Label** field
  - Drag "TradePanel" itself from Hierarchy → **Panel Canvas Group** field

### Step 4.11: Disable TradePanel Initially
- **Action:** Select "TradePanel" in Hierarchy
- **Action:** In Inspector, find checkbox next to component name
- **Action:** Uncheck the box (to disable it - it will enable when trade starts)

---

## PHASE 5: VERIFY BITSDISPLAY EXISTS

### Step 5.1: Check for BitsDisplay
- **Action:** In Hierarchy, search for "BitsDisplay" or "Bits"
- **If found:** Go to Step 6
- **If NOT found:** Create it:
  - Right-click on "UI_Canvas" in Hierarchy
  - Select: TextMeshPro - Text
  - Rename to: `BitsDisplay`
  - Set Text: "Bits: 0"
  - Set Font Size: 20
  - Set Anchor Preset: Top-Right
  - Set Position X: -20, Y: -20
  - In Inspector, click "Add Component"
  - Search for: `BitsDisplayUI`
  - Click to add it
  - Drag "BitsDisplay" (the TextMeshPro) → **Bits Label** field
  - Leave other settings as default

---

## PHASE 6: TESTING

### Step 6.1: Play Scene
- **Action:** Click Play button in Unity Editor
- **Expected Result:** Scene starts playing
- **Check Console:** Should see messages like "[InventoryService] Initialized"

### Step 6.2: Test Inventory Display
- **Expected:** InventoryPanel shows "Inventory Empty"
- **If not:** Check that EmptyLabel is visible and ItemsContainer is empty

### Step 6.3: Add Item via Console
- **Action:** Open Unity Console (Window → General → Console)
- **Action:** In console, type:
  ```
  InventoryService.Instance.AddItem("copper_wire", 1);
  ```
- **Action:** Press Enter
- **Expected:** InventoryPanel shows "1x Copper Wire" with icon

### Step 6.4: Test Trade Panel
- **Action:** In console, add multiple items:
  ```
  InventoryService.Instance.AddItem("copper_wire", 2);
  InventoryService.Instance.AddItem("glass_fragments", 3);
  ```
- **Action:** Click on any NPC in scene (if they have TradeUIPanel integration)
- **Expected:** TradePanel appears showing wanted/offered items

### Step 6.5: Test Currency
- **Action:** In console:
  ```
  CurrencySystem.Instance.AddBits(100, "Test");
  ```
- **Expected:** BitsDisplay updates to show "Bits: 100"

---

## PHASE 7: WIRE UP NPCTRADER (OPTIONAL - FOR NOW)

Skip this for now, do it after testing UI display works.

---

## CHECKLIST - VERIFY ALL COMPONENTS

- [ ] InventoryItemEntry.prefab exists in Assets/Prefabs/UI/
- [ ] TradeItemEntry.prefab exists in Assets/Prefabs/UI/
- [ ] InventoryPanel exists in UI_Canvas
- [ ] InventoryPanel has InventoryPanelUI component
- [ ] InventoryPanel.ItemsContainer has Grid Layout Group
- [ ] TradePanel exists in UI_Canvas
- [ ] TradePanel has TradeUIPanel component
- [ ] TradePanel is DISABLED (unchecked in Inspector)
- [ ] BitsDisplay exists and shows "Bits: 0"
- [ ] BitsDisplay has BitsDisplayUI component
- [ ] All prefab references assigned in Inspector
- [ ] Console shows no errors on Play

---

**TOTAL TIME:** 30-45 minutes
