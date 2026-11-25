# Project Overview
- Game Title: Velinor
- High-Level Concept: Existing exploration game with dialogue, glyph/memory puzzles, inventory and crafting. This revision packages the current market-scene inventory into the canonical reusable UI canvas; it does not redesign gameplay.
- Players: Single player
- Inspiration / Reference Games: Not specified; preserve the existing project design.
- Tone / Art Direction: Preserve current sci-fi UI, fonts, colors and layouts.
- Target Platform: PC (StandaloneWindows64)
- Screen Orientation / Resolution: Landscape; existing canvas reference resolution 1920x1080.
- Render Pipeline: URP (Ultra), Unity 6000.4.11f1.

## Revision scope and selected approach
The original **Complete standalone setup** is implemented and the user confirms that the inventory works. The canonical canvas is connected to InsideMarket_02, UI_Canvas_Fixed was deleted, and loose inventory roots were removed. Historical restoration steps below are completed context, not instructions to repeat.

**Current extension: Equip / Unequip / Use action feedback.**
- Use the existing `Velinor.Interactions.ToolSystem` as the single authoritative equipped-tool state, integrated into the persistent canvas bootstrap. Its existing architecture permits one equipped tool at a time; selecting another tool replaces the previous one. Do not introduce a second competing equipment state in the UI.
- The alternative is UI-only equipment flags. Less integration effort, but they would disagree with gameplay consumers and lose coherent state across scenes; reject this approach.
- The user selected **one item per Use click**, without a new quantity selector. Only successful actions show confirmation; preserve all existing art and layouts.
- Retain the standalone prefab approach: local notification references and reused/created persistent services, never singleton components directly on the canvas root.
- This extension replaces the old Equip/Use placeholder limitation. It adds actual equipment state and consumption, not new character attachments, animations, healing, buffs or tool-specific debris capabilities.
- Runtime equipped state persists through scene transitions; new disk-save formats and session-restart equipment persistence are outside scope.

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

## Target hierarchy / wireframe
Preserve the current presentation; this is packaging and lifecycle repair, not a visual rebuild.
```text
UI_Canvas [Canvas, CanvasScaler, GraphicRaycaster, UIPersistenceManager,
           InventoryUIBootstrap]
├── DialoguePanel, CodexPanel, NotificationPanel, ScreenImagePanel_Merged
└── InventoryPanel [CanvasGroup, InventoryManagerUI]
    ├── BitsDisplay                         Bits: [value]
    ├── TabsPanel               [Materials/Schematics] [Tools/Items]
    ├── Content
    │   ├── MaterialsSchematicsTab → two existing ScrollRect lists
    │   └── ToolsItemsTab         → two existing ScrollRect lists
    └── SharedFooter                        [Assemble / Equip / Use]
Referenced assets: InventoryItemEntry.prefab → DemandEntry.prefab,
ItemDatabase_Fixed.asset, existing schematic definition assets.
Runtime dependencies: reuse or create InventoryService, CurrencySystem,
and exactly one active EventSystem with InputSystemUIInputModule.
```
Asset references are self-contained dependencies: row templates do not need to be manually placed in every scene.

# Key Asset & Context
## Observed state
- `Assets/Scenes/InsideMarket_02.unity`: UI_Canvas is currently disconnected from any prefab. It contains the latest inventory hierarchy and correctly assigned InventoryManagerUI buttons, four list contents and row-template asset references.
- `Assets/Prefabs/UI/UI_Canvas.prefab`: canonical prefab, GUID `323b337dcda54144eb4c6d0b71de20c4`, 168 objects at audit time. Preserve the asset GUID so connected instances continue referencing it.
- `Assets/Prefabs/UI/UI_Canvas_Fixed.prefab`: 212 objects; no references found in searched scenes, prefabs, assets or scripts. Delete only after canonical replacement passes validation and a final reference scan.
- Current scene contains two loose InventoryItemEntry instances, empty DemandEntry and empty Footer roots. No incoming scene component references were found. One row instance has duplicate children; these are not required by the manager, which instantiates the row asset.
- `Assets/Scripts/UI/InventoryManagerUI.cs`: consumes InventoryService in OnEnable, binds currency if present, has unbalanced button/currency subscriptions and polls the I key despite constructing an InputAction. Schematic list is empty in the current scene.
- `Assets/Scripts/Inventory/InventoryService.cs`: existing component on multi-purpose Managers root; singleton Awake currently calls Destroy(gameObject) for duplicates and persists its entire host. Do not copy Managers into the UI prefab.
- `Assets/Scripts/Economy/CurrencySystem.cs`: no instance in the current scene; duplicate handler destroys its host. Loads Bits in Start without notifying the display.
- `Assets/Scripts/UI/UIPersistenceManager.cs`: keeps one canvas across scene changes; startup/duplicate ordering must be accounted for.
- `Assets/Prefabs/UI/InventoryItemEntry.prefab` and `DemandEntry.prefab`: retain referenced row assets; verify their serialized child references and ingredient layout.
- `Assets/Resources/Items/ItemDatabase_Fixed.asset`: database currently used by the scene InventoryService. Preserve it; deletion request concerns UI_Canvas_Fixed, not this database.
- `Assets/Resources/Items/TestContent/Schematic_*.asset`: existing candidate definitions to validate against the item database before assignment.
- New `Assets/Scripts/UI/InventoryUIBootstrap.cs`: serialized database configuration and safe ensure/reuse API for required runtime dependencies.
- Ten regular scenes currently reference canonical UI_Canvas, plus one recovery scene. Disconnected canvases do not update automatically; report them separately, without blanket replacement.

# Implementation Steps
## 1. Baseline and impact checks
- Recheck dependencies/dependents for the canonical canvas, fixed canvas, scene and each script/template before edits; use project dependency tooling when available, otherwise AssetDatabase dependency scans and GUID/text searches.
- Capture scene/prefab hierarchies, serialized references, current overrides, singleton consumers and missing-script status. Review full relevant lifecycle code before implementing changes.
- Preserve a recoverable baseline via version control or backup outside the production prefab paths. Do not edit recovery scenes.
- Dependencies: none.

## 2. Implement standalone initialization safely
- Add InventoryUIBootstrap on the persistent canvas root; serialize the existing ItemDatabase_Fixed asset.
- Ensure one usable InventoryService, one CurrencySystem and one active EventSystem. Reuse existing scene/persistent instances; create only missing services on separate root GameObjects with correct database/configuration. No InventoryService or CurrencySystem directly on UI_Canvas.
- Make initialization explicit before InventoryManagerUI binds; do not rely solely on Unity's unspecified object Awake order. Avoid services created by duplicate canvases, and initialize before any test-item population.
- Update InventoryService initialization/configuration so a newly created component has its database before validation/use. Duplicate services must not destroy unrelated Managers/Canvas hosts; remove only the redundant component or a known dedicated service root. Clear static ownership on destruction only when the destroyed component owns it. Preserve existing state and consumers.
- Apply equivalent host-safe duplicate handling to CurrencySystem if needed for scenes that already contain it; preserve save keys and current balances. Notify the UI after initial Bits loading, without resetting progress.
- Bootstrap provides a New Input System EventSystem only if none is usable, with exactly one active input module. Reconcile a bootstrap-created EventSystem with subsequently loaded scene EventSystems on scene transitions; remove only bootstrap-owned duplicates, leaving scene-owned objects intact. Persistent UI must retain working input after source-scene unload.
- Inspect UIPersistenceManager and modify only if required to expose ownership/readiness and prevent duplicate bootstrap execution. Do not pull dialogue, world interactions or all Managers into the prefab.
- Dependencies: Step 1.

## 3. Stabilize InventoryManagerUI lifecycle
- Ensure dependencies then bind inventory/currency; handle enable/disable/re-enable and scene changes without stale services or multiple listeners.
- Replace anonymous tab listeners with removable handlers; symmetrically unsubscribe inventory, button, currency and input events. Dispose owned InputAction on destruction.
- Wire the existing ToggleInventory action through its performed event, remove duplicate Keyboard polling, retain I as the binding. Keep InventoryPanel active but hidden using CanvasGroup so input still works while closed.
- Preserve current test data and populate flag rather than silently changing shipped inventory quantities. Ensure test seeding occurs once only when enabled and inventory is empty, not on every scene transition.
- Validate required UI/template references and avoid silent root-level row instantiation when a content reference is missing.
- Assign valid existing schematic definitions matching the database; do not invent recipes. Preserve Equip/Use as the existing placeholder behavior; no new equipment or consumption system in this task.
- Verify ingredient rows survive their Start initialization; make a targeted InventoryItemEntryUI lifecycle correction only if tests confirm Start hides initialized ingredients.
- Dependencies: Step 2.

## 4. Consolidate the scene inventory hierarchy
- Keep InventoryPanel/Content, both existing tab objects, all four scrollviews and SharedFooter; verify ScrollRect content/viewport links and list sizing before changing properties.
- Remove only the disabled obsolete InventoryPanelUI component after checking references; keep InventoryManagerUI as the single inventory presenter.
- Preserve visual styling, 1920x1080 scaling and current layout. Correct only proven blocking scroll/layout issues, rather than rebuilding panels.
- Recheck loose InventoryItemEntry, DemandEntry and Footer roots for incoming references and meaningful unsaved template edits. Transfer any required verified template improvements to the referenced row asset with reference remapping; otherwise delete those unused loose instances. Do not blindly parent sample rows into live content or copy their duplicate children.
- Dependencies: Steps 1–3.

## 5. Publish the canonical prefab and reconnect this scene
- Save the consolidated scene UI_Canvas to the existing `Assets/Prefabs/UI/UI_Canvas.prefab`, retaining its GUID. Connect the current scene canvas to the canonical prefab.
- Preflight disconnected-root name matching: repeated sibling names elsewhere in the canvas can make overwrite matching ambiguous. Preserve/remap existing prefab local IDs and references as necessary; verify connected scene overrides after publishing. Do not replace every scene canvas or discard legitimate overrides.
- Reusable UI references must point within the prefab or to persistent asset dependencies. Any discovered world/scene-specific references remain explicit scene overrides or runtime bindings, never silently baked as broken prefab links.
- Inspect representative existing connected scenes for canonical update propagation and inventory-specific overrides that mask the new configuration; report conflicts and migrate only required inventory overrides after protecting scene-specific UI.
- Save InsideMarket_02 and canonical prefab. Recheck dialogue/codex/puzzle references because the user requested saving the entire current canvas, not only InventoryPanel.
- Dependencies: Step 4.

## 6. Retire UI_Canvas_Fixed
- Repeat project-wide GUID/path reference scan. If any references exist, migrate them safely to the canonical prefab and verify local object-reference remapping before deletion.
- Delete only `Assets/Prefabs/UI/UI_Canvas_Fixed.prefab` and its Unity-managed meta after tests pass. Retain ItemDatabase_Fixed and both row-template assets.
- Dependencies: Step 5 and successful verification.

## Current extension: implementation steps (execute these only)
### E1. Verify the existing action pipeline and preserve a baseline
- Recheck asset dependencies and consumers before edits. Preserve the working canonical prefab and relevant scripts in a recoverable backup.
- Confirm notification panel hierarchy, serialized text reference, sibling draw order and raycast settings in both scene and prefab.
- Observed: InventoryManagerUI.OnActionClicked currently only logs non-crafting actions; UpdateActionButton only offers Equip or Use. RefreshAll retains selectedToolOrItem by object identity even though it destroys/recreates rows.
- Observed: NotificationPanelController exists locally, but notificationText is currently null in the serialized scene. It uses a global canvas search in Awake; explicit local wiring should be authoritative.
- Observed: ToolSystem.cs already defines EquipTool, UnequipTool, IsToolEquipped and equipment events. No ToolSystem instance or ToolDefinition assets exist in the current project audit. BreakableDebris consumes ToolSystem.HasTool.
- Dependencies: none; the original restoration phase is already complete.

### E2. Integrate the existing tool state into standalone setup
- Modify `Assets/Scripts/Interactions/ToolSystem.cs`: safe idempotent EnsureInstance/reuse API, singleton ownership clearing and host-safe duplicate removal. Initialize against the persistent InventoryService before use, without relying on scene Awake order.
- Preserve existing ToolDefinition support for any configured interaction metadata. Permit equipping owned inventory items of ItemCategory.Tool when no separate ToolDefinition exists: retain their item ID as equipment state, with optional metadata null. Do not invent breakable-debris permissions or generate redundant tool assets.
- Ensure Equip validates possession/type, changes state only on success, and exposes the current equipped ID through the existing API. Repeated equip of the same ID is idempotent. Unequip clears it. A tool replaced by another is no longer equipped.
- Subscribe/unsubscribe safely to inventory changes/clear so a tool whose last owned copy disappears cannot remain equipped. Retain existing gameplay consumers and ownership semantics.
- Modify `Assets/Scripts/UI/InventoryUIBootstrap.cs` to ensure/reuse this service after InventoryService initialization. Do not reset an established equipped tool on canvas duplicates or transitions.
- Dependencies: E1.

### E3. Implement action state and item consumption
- Modify `Assets/Scripts/UI/InventoryManagerUI.cs`:
  - Add a serialized local NotificationPanelController reference and resolve only within its own canvas if absent.
  - Subscribe symmetrically to ToolSystem equipment changes to update action labels; preserve state across panel closing/reopening and list refreshes.
  - Track selected tools/items by stable item ID, not a destroyed row reference. After RefreshAll, restore the matching new row; if quantity reaches zero, clear selection and disable the action button.
  - For a selected owned tool, label the button **Unequip** when ToolSystem reports that ID equipped, otherwise **Equip**. Toggle the authoritative service state on the button press; equipping/unequipping must not reduce tool quantity.
  - Show exact confirmations using the item's display name: `X has been equipped`, `X has been unequipped`.
  - For a selected non-tool item displayed by the existing CraftedItem/Food list, keep **Use**. Cache its ID/display name before mutating inventory, call the existing InventoryService.Remove(id, 1), and show `Y has been used` only if removal succeeds. This is consumption of one item per click, not an assumed healing/buff effect.
  - Avoid double refreshes/callbacks and stale-row access during synchronous inventory events. Repeated clicks can consume one each only while stock remains; failed/unowned/empty actions cannot show a success notification or underflow stock.
  - Leave Assemble and other UI behavior unchanged.
- Dependencies: E2.

### E4. Wire notification feedback in the canonical prefab
- Modify `Assets/Prefabs/UI/UI_Canvas.prefab` in place, preserving GUID and existing local IDs. Assign InventoryManagerUI's notification controller to the sibling NotificationPanel; explicitly assign the panel's CanvasGroup and NotificationText component.
- Make a targeted change to `Assets/Scripts/UI/NotificationPanelController.cs` only as required: prefer serialized/local-parent references before any legacy global fallback, and prevent initial hiding from overriding an early valid notification. Preserve the existing interrupt-and-restart fade/timer behavior and public ShowNotification signature for other callers.
- Verify the notification renders above inventory while leaving controls clickable. Adjust only the relevant draw order or non-interactive raycast settings if needed; do not restyle/rebuild NotificationPanel.
- Save the canonical prefab and InsideMarket_02. Inspect a representative connected scene to ensure references are inherited with no scene-specific dependencies.
- Dependencies: E3.

### E5. Verify actions and clean up tests
- Compile with no new errors and verify serialized references in scene and prefab.
- Runtime sequence: open inventory → select a tool → Equip → verify its ID and notification text/visibility → verify button becomes Unequip → press it → verify cleared state and unequip confirmation. Reselect an already-equipped tool and confirm Unequip without equipping again.
- Equip tool A, then B: B is the only equipped tool; selecting A offers Equip, selecting B offers Unequip. Quantities remain unchanged.
- Give a displayed consumable a test quantity of 3: Use yields 2, then 1, then removes the row at 0; each successful click displays its confirmation. Once empty, no success message or further decrement. Refresh/reopen retains valid selection and correct action labels.
- Check equipment after inventory clear or removal of the final tool copy, on panel enable/disable, and on scene transition; no stale state or duplicated subscriptions.
- Capture and inspect a Play Mode screenshot of the notification while inventory remains open; verify readable, visible feedback that does not block buttons. Check fade-out and rapid successive actions using the existing notification interruption policy.
- Preserve real inventory/currency saves during tests; remove temporary runner/screenshots/fixtures and leave InsideMarket_02 loaded in Edit Mode.
- If the editor bootstrap again fails to run, stop repeated attempts, retain explicit verification limitations and never claim the new actions were runtime-tested without evidence.
- Dependencies: E2–E4.

# Verification & Testing
The historical checks below remain regression coverage. For the current extension, E5 is the acceptance test and supersedes the previous Equip/Use placeholder notes.
- Compilation: no new errors; inspect Unity Console before and after.
- Edit Mode: canonical GUID unchanged; current scene connected; InventoryPanel has one active presenter, valid tab/action/Bits references, four distinct content containers, valid row/ingredient templates and database/recipe assets.
- Fresh instance test: canonical UI_Canvas alone in a temporary test scene, with no inventory/currency/EventSystem configured, initializes dependencies and opens with I; no missing-reference errors. Dispose temporary test setup afterwards without persisting it into production scenes.
- Existing-services test: prefab reuses an existing populated InventoryService and CurrencySystem; does not reset inventory/Bits, destroy Managers or spawn extra active services/input modules.
- Reload/additive tests: transition between InsideMarket_02 and a representative canonical-prefab scene; exactly one surviving canvas and active input system, preserved player quantities/Bits, no duplicate callbacks, no whole-host destruction. Test reverse arrival order and re-enable/disable cycles.
- Inventory: switch tabs, scroll long lists, select/deselect materials and schematic, verify ingredient visibility/quantities and Assemble requirements. Check empty inventory with test population off and existing data with it on. Equip/Use remains existing behavior, explicitly not a new gameplay implementation.
- Input: one I press produces exactly one open/close transition; mouse, scroll wheel and buttons work after source scene unload.
- Currency: initial saved Bits appears after startup; earn/spend updates once. Tests must not overwrite the user's real saved balance; preserve/restore test preferences or isolate save state.
- Prefab propagation: inspect at least one existing connected scene and a newly instantiated canvas; inspect override conflicts and verify dialogue, codex and market-specific puzzle bindings were retained.
- Cleanup: loose inventory roots removed only when proven unnecessary; final fixed-prefab GUID/path scan finds no remaining references; reopen scene/prefab and confirm serialization persists.
- Record final affected files, tests performed and any untested runtime behavior. No claim of a fixed InventoryPanel without runtime interaction checks.
