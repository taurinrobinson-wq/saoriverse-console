# Inventory System Workflow - Complete Guide

## UI Structure Overview

The inventory system in [UI_Canvas.prefab](../Velinor-Unity/Assets/Prefabs/UI/UI_Canvas.prefab) consists of two main tabs that toggle visibility via CanvasGroup alpha:

### Default State
- **MaterialsSchematicsTab**: Visible (alpha = 1) - PRIMARY CRAFTING INTERFACE
- **ToolsItemsTab**: Hidden (alpha = 0)

---

## Crafting Workflow

### Step 1: Materials Selection (MaterialsSchematicsTab)
**Default State on Inventory Open**

The player sees the Materials/Schematics panel with:
- **Materials Container**: Vertical scrollable list of available materials
  - Single-click on a material to select it
  - Multiple materials can be selected to form a recipe

**Interaction Model:**
- Single-click selects/deselects materials
- Selected materials are highlighted/indicated visually
- When player selects a valid material combination:
  - The associated **Schematic** is activated/displayed
  - The **Assemble Button** becomes active/visible

### Step 2: Schematic Activation
When the correct material combo is selected:
1. Associated schematic displays
2. Recipe details show (materials needed, result item/tool)
3. **Assemble Button** appears and becomes interactive

### Step 3: Assembly/Crafting
**Clicking Assemble:**
1. ✓ Decreases material amounts in the Materials container by recipe amounts
2. ✓ Adds the crafted tool/item to the appropriate container (ToolsItemsTab)
3. ✓ Clears the selection
4. ✓ Schematic and Assemble button return to inactive state

---

## Item Management Workflow

### Tab Switching
Player clicks tab buttons to switch between:
- **MaterialsSchematicsTab** (Crafting interface)
- **ToolsItemsTab** (Inventory/Equipment interface)

Tab switching works via:
- Setting new tab CanvasGroup alpha to 1 (visible)
- Setting old tab CanvasGroup alpha to 0 (hidden)

### Tools & Items Container (ToolsItemsTab)
**Interface:**
- Vertical scrollable list of crafted items and equipped tools

**Single-Click Interaction:**
When player single-clicks an item/tool:
- **For Tools**: "Equip" button appears
  - Tools are persistent (not consumed on use)
  - Player can switch between different tools
  - Equipped tool remains in inventory

- **For Items**: "Use" button appears
  - Items are consumable (single-use)
  - Using an item decreases the count in the container
  - When count reaches 0, item is removed from container

**Quantity Tracking:**
- Each item/tool slot shows current quantity
- Tools: Quantity remains constant
- Items: Quantity decreases when used

---

## CanvasGroup Configuration

### MaterialsSchematicsTab (Default Visible)
```
CanvasGroup:
  m_Alpha: 1              // Fully visible
  m_Interactable: 1       // Can receive input
  m_BlocksRaycasts: 1     // Can be interacted with
  m_IgnoreParentGroups: 0
```

### ToolsItemsTab (Hidden by Default)
```
CanvasGroup:
  m_Alpha: 0              // Fully hidden
  m_Interactable: 1       // Settings maintained for toggle
  m_BlocksRaycasts: 0     // Cannot receive input while hidden
  m_IgnoreParentGroups: 0
```

---

## Layout Configuration

### Containers: VerticalLayoutGroup
All item containers use **VerticalLayoutGroup** for consistent list display:

```
VerticalLayoutGroup:
  m_Padding: 10px (all sides)
  m_Spacing: 10px (between items)
  m_ChildAlignment: Top (or Center for some)
  m_ChildForceExpandWidth: 1    // Items fill width
  m_ChildForceExpandHeight: 0   // Items use content height
  m_ChildControlSize: 1         // Layout manages sizing
  m_ChildLayoutWidth: 1
  m_ChildLayoutHeight: 0 or 1   // Depends on container
```

This ensures:
- ✓ Items display in a clean vertical list
- ✓ Proper scrolling behavior with ScrollRect
- ✓ Responsive layout that adapts to content
- ✓ No overlapping or grid-based layout issues

---

## Open Inventory Hotkey

**Key Input: "I"**
- Press "I" to toggle entire InventoryPanel visibility
- InventoryPanel contains both tabs
- When opened, displays the active tab (MaterialsSchematicsTab by default)

---

## Related Files

- **Prefab**: [UI_Canvas.prefab](../Velinor-Unity/Assets/Prefabs/UI/UI_Canvas.prefab)
- **Tab Scripts**: ToolsItemsTab.cs, MaterialsSchematicsTab.cs
- **Controller**: InventoryUIController.cs or similar

---

## Recent Changes (Session: Nov 23, 2026)

### Commit 746bf10ee
Fixed inventory UI structure:
- Added CanvasGroup components to both tab GameObjects
- Converted GridLayoutGroup to VerticalLayoutGroup (3 Content containers)
- Enabled both tabs (IsActive: 1) with alpha controlling visibility

### Commit 0c608ed44
Set correct default state:
- MaterialsSchematicsTab alpha: 0 → 1 (visible by default)
- ToolsItemsTab alpha: 0 (hidden by default)
- BlocksRaycasts properly configured for each state

---

## Notes

- Both tabs remain **enabled in the editor** (IsActive: 1)
- **Visibility is controlled exclusively via CanvasGroup alpha**
- Tab buttons trigger alpha changes to swap visibility
- No grid layout overlapping issues
- Clean vertical list display for all containers
