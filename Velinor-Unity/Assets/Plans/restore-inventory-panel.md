# Project Overview
- Game Title: Velinor
- High-Level Concept: Sci-fi exploration and crafting game set in a remnant-filled world.
- Players: Single player
- Render Pipeline: URP (Ultra)
- Target Platform: PC (StandaloneWindows64)

# Game Mechanics
## Core Gameplay Loop
The player explores the environment, gathers materials, finds schematics, and assembles tools or items to progress. The inventory system is central to managing these resources and crafting new items.

## Controls and Input Methods
- Keyboard/Mouse: 'I' key toggles the inventory.
- UI: On-screen tabs and buttons for navigating inventory and performing actions (Equip/Assemble).

# UI
## Inventory Panel
A multi-tab UI panel:
1. **Materials/Schematics Tab**:
   - Left list: Materials (e.g., Scrap Metal, Glass Fragments).
   - Right list: Schematics (e.g., Scanner Schematic, Welder Schematic).
   - Bottom: "Assemble" button (enabled when a schematic and its required materials are selected).
2. **Tools/Items Tab**:
   - Left list: Tools (e.g., Hand Scanner, Flashlight).
   - Right list: Items (e.g., Stimpack, Survival Ration).
   - Bottom: "Equip" or "Use" button.

# Key Asset & Context
- `Assets/Prefabs/UI/UI_Canvas.prefab`: Contains the `InventoryPanel`.
- `Assets/Scripts/UI/InventoryManagerUI.cs`: Main logic for the inventory UI.
- `Assets/Scripts/Inventory/InventoryService.cs`: Runtime inventory data.

# Implementation Steps

## 1. Clean up InventoryPanel Hierarchy
The current `InventoryPanel` has duplicated children and redundant components.
- **Description**: Remove `InventoryPanelUI` component from `InventoryPanel`. Delete the redundant `Content` and `ToolsItemsTab` GameObjects.
- **Assigned role**: developer
- **Dependencies**: None
- **Parallelizable**: No

## 2. Rewire InventoryManagerUI
Ensure the script references point to the correct UI elements.
- **Description**: Update `InventoryManagerUI` serializable fields on the `UI_Canvas` prefab to point to the correct containers and buttons.
- **Assigned role**: developer
- **Dependencies**: Step 1
- **Parallelizable**: No

## 3. Restore Test Data in InventoryManagerUI
Update the test data population to match the state from November 11, 2026.
- **Description**: Modify `InventoryManagerUI.PopulateInitialTestItems()` to include Tools and Items (Hand Scanner, Flashlight, Micro-Welder, Stimpack, Survival Ration) with specific quantities as seen in the reference images.
- **Assigned role**: developer
- **Dependencies**: None
- **Parallelizable**: Yes

## 4. Fix Tab Switching Logic
Ensure the UI correctly transitions between tabs.
- **Description**: Verify and fix `InventoryManagerUI.SwitchTab()` to ensure it correctly toggles the `CanvasGroup` visibility and interactivity for the respective tab objects.
- **Assigned role**: developer
- **Dependencies**: Step 2
- **Parallelizable**: No

# Verification & Testing
- **Play Mode Test**: Press 'I' to open the inventory.
- **Visual Check**: Compare the open inventory with the provided screenshots (Items 1-5).
- **Tab Selection**: Switch between "Materials/Schematics" and "Tools/Items" tabs.
- **Functional Test**: 
  - Ensure "Hand Scanner", "Flashlight", etc., appear in the Tools list.
  - Ensure "Scrap Metal", "Glass Fragments", etc., appear with correct quantities.
  - Ensure the "Equip" and "Assemble" buttons behave correctly based on selection.
