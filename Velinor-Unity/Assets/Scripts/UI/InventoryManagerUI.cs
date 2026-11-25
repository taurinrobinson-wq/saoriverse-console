using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections.Generic;
using System.Linq;
using Velinor.Inventory;
using Velinor.Economy;
using UnityEngine.InputSystem;

namespace Velinor.UI
{
    public class InventoryManagerUI : MonoBehaviour
    {
        [Header("Tabs")]
        [SerializeField] private Button materialsTabButton;
        [SerializeField] private Button toolsTabButton;
        [SerializeField] private GameObject materialsSchematicsTab;
        [SerializeField] private GameObject toolsItemsTab;

        [Header("Panels - Materials/Schematics")]
        [SerializeField] private Transform materialsContainer;
        [SerializeField] private Transform schematicsContainer;

        [Header("Panels - Tools/Items")]
        [SerializeField] private Transform toolsContainer;
        [SerializeField] private Transform itemsContainer;

        [Header("Prefabs")]
        [SerializeField] private GameObject itemEntryPrefab;
        [SerializeField] private GameObject demandEntryPrefab;

        [Header("Footer")]
        [SerializeField] private Button actionButton;
        [SerializeField] private TextMeshProUGUI actionButtonText;
        [SerializeField] private TextMeshProUGUI bitsValueText;

        [Header("Action Feedback")]
        [SerializeField] private NotificationPanelController notificationController;

        [Header("Visual Settings")]
        [SerializeField] private Color buttonActiveColor = new Color(0f, 0.9f, 0f, 1f); // Bright Green
        [SerializeField] private Color buttonInactiveColor = new Color(0.2f, 0.2f, 0.2f, 0.8f); // Dark Gray
[SerializeField] private Color tabActiveColor = new Color(0.5f, 0.5f, 0.7f, 1f);
        [SerializeField] private Color tabInactiveColor = new Color(0.2f, 0.2f, 0.2f, 1f);

        [Header("Database")]
        [SerializeField] private List<SchematicDefinition> schematicDatabase;
        [SerializeField] private bool populateTestDataAtStart = true;

        private InventoryService inventory;
        private CanvasGroup mainCanvasGroup;
private bool isInventoryOpen = false;
        private InputAction toggleAction;

        private List<InventoryItemEntryUI> materialEntries = new();
        private List<InventoryItemEntryUI> schematicEntries = new();
        private List<InventoryItemEntryUI> toolEntries = new();
        private List<InventoryItemEntryUI> itemEntries = new();
        
        private HashSet<string> selectedMaterialIds = new();
        private SchematicDefinition selectedSchematic;
        private InventoryItemEntryUI selectedToolOrItem;
        private string selectedToolOrItemId;
        private Velinor.Interactions.ToolSystem toolSystem;
        private bool isMaterialsTab = true;

        private void Awake()
        {
            mainCanvasGroup = GetComponent<CanvasGroup>();
            bootstrap = GetComponentInParent<InventoryUIBootstrap>();
            toggleAction = new UnityEngine.InputSystem.InputAction("ToggleInventory", binding: "<Keyboard>/i");
            toggleAction.performed += OnTogglePerformed;
        }

        private InventoryUIBootstrap bootstrap;
        private CurrencySystem currency;
        private bool attemptedTestPopulation;

        private void OnEnable()
        {
            if (bootstrap != null && !bootstrap.EnsureReady()) return;
            if (mainCanvasGroup == null || materialsTabButton == null || toolsTabButton == null ||
                materialsSchematicsTab == null || toolsItemsTab == null || materialsContainer == null ||
                schematicsContainer == null || toolsContainer == null || itemsContainer == null ||
                itemEntryPrefab == null || actionButton == null || actionButtonText == null)
            {
                Debug.LogError("[InventoryManagerUI] Inventory UI references are incomplete.", this);
                return;
            }
            inventory = InventoryService.Instance;
            if (inventory == null) return;
            toolSystem = Velinor.Interactions.ToolSystem.EnsureInstance(inventory);
            if (notificationController == null)
            {
                var canvas = GetComponentInParent<Canvas>();
                if (canvas != null) notificationController = canvas.GetComponentInChildren<NotificationPanelController>(true);
            }
            toolSystem.OnToolEquipped += HandleToolEquipped;
            toolSystem.OnToolUnequipped += UpdateActionButton;

            if (!attemptedTestPopulation)
            {
                attemptedTestPopulation = true;
                if (populateTestDataAtStart && inventory.GetAll().Count == 0)
                    PopulateInitialTestItems();
            }
            inventory.OnInventoryChanged += HandleInventoryChanged;
            inventory.OnInventoryCleared += RefreshAll;
            inventory.OnSchematicLearned += HandleSchematicLearned;
            materialsTabButton.onClick.AddListener(OnMaterialsTabClicked);
            toolsTabButton.onClick.AddListener(OnToolsTabClicked);
            actionButton.onClick.AddListener(OnActionClicked);

            currency = CurrencySystem.Instance;
            if (currency != null)
            {
                currency.OnBitsChanged += UpdateBitsDisplay;
                UpdateBitsDisplay(currency.CurrentBits);
            }
            toggleAction.Enable();
            CloseInventory();
            SwitchTab(true);
        }

        private void OnMaterialsTabClicked() => SwitchTab(true);
        private void OnToolsTabClicked() => SwitchTab(false);
        private void OnTogglePerformed(UnityEngine.InputSystem.InputAction.CallbackContext context) => ToggleInventory();

        private void PopulateInitialTestItems()
        {
            if (inventory == null) return;
            
            // Basic Materials
            inventory.Add("scrap_metal", 15);
            inventory.Add("wire", 10);
            inventory.Add("polymer", 8);
            inventory.Add("glass", 5);
            inventory.Add("fabric", 12);
            inventory.Add("electronic_parts", 6);
            inventory.Add("power_cell", 4);
            inventory.Add("mechanical_parts", 7);
            inventory.Add("sealant", 9);

            // Herbs & Organic
            inventory.Add("medicinal_herbs", 10);
            inventory.Add("antiseptic_herbs", 8);
            inventory.Add("soothing_herbs", 5);
            inventory.Add("plant_oil", 6);
            inventory.Add("roots", 10);
            inventory.Add("greens", 8);
            inventory.Add("vegetables", 12);
            inventory.Add("fruit", 15);
            inventory.Add("culinary_herbs", 20);

            // Some starter schematics
            inventory.Add("schematic_portable_light", 1);
            inventory.Add("schematic_pry_tool", 1);
            inventory.Add("schematic_bandage", 1);

            Debug.Log("[InventoryManagerUI] Auto-populated test items matching canonical Velinor taxonomy.");
        }

        private void HandleInventoryChanged(string id, int qty) => RefreshAll();
        private void HandleToolEquipped(string id) => UpdateActionButton();
        private void HandleSchematicLearned(string id) => RefreshAll();

        private void OnDisable()
        {
            if (inventory != null)
            {
                inventory.OnInventoryChanged -= HandleInventoryChanged;
                inventory.OnInventoryCleared -= RefreshAll;
                inventory.OnSchematicLearned -= HandleSchematicLearned;
            }
            if (currency != null) currency.OnBitsChanged -= UpdateBitsDisplay;
            if (toolSystem != null)
            {
                toolSystem.OnToolEquipped -= HandleToolEquipped;
                toolSystem.OnToolUnequipped -= UpdateActionButton;
            }
            if (materialsTabButton != null) materialsTabButton.onClick.RemoveListener(OnMaterialsTabClicked);
            if (toolsTabButton != null) toolsTabButton.onClick.RemoveListener(OnToolsTabClicked);
            if (actionButton != null) actionButton.onClick.RemoveListener(OnActionClicked);
            if (toggleAction != null) toggleAction.Disable();
        }

        private void OnDestroy()
        {
            if (toggleAction != null)
            {
                toggleAction.performed -= OnTogglePerformed;
                toggleAction.Dispose();
            }
        }

        public void ToggleInventory()
        {
            if (isInventoryOpen) CloseInventory();
            else OpenInventory();
        }

        public void OpenInventory()
        {
            isInventoryOpen = true;
            SetPanelVisibility(true);
            RefreshAll();
        }

        public void CloseInventory()
        {
            isInventoryOpen = false;
            SetPanelVisibility(false);
        }

        private void SetPanelVisibility(bool visible)
        {
            if (mainCanvasGroup != null)
            {
                mainCanvasGroup.alpha = visible ? 1f : 0f;
                mainCanvasGroup.interactable = visible;
                mainCanvasGroup.blocksRaycasts = visible;
            }
        }

        private void SwitchTab(bool toMaterials)
        {
            isMaterialsTab = toMaterials;
            SetTabVisibility(materialsSchematicsTab, toMaterials);
            SetTabVisibility(toolsItemsTab, !toMaterials);
            UpdateTabVisuals(toMaterials);
            selectedMaterialIds.Clear();
            selectedSchematic = null;
            selectedToolOrItem = null;
            RefreshAll();
        }

        private void SetTabVisibility(GameObject tab, bool visible)
        {
            if (tab == null) return;
            var cg = tab.GetComponent<CanvasGroup>();
            if (cg == null) return;
            cg.alpha = visible ? 1f : 0f;
            cg.interactable = visible;
            cg.blocksRaycasts = visible;
        }

        private void UpdateTabVisuals(bool materialsActive)
        {
            if (materialsTabButton != null && materialsTabButton.TryGetComponent<Image>(out var matImg))
                matImg.color = materialsActive ? tabActiveColor : tabInactiveColor;
            if (toolsTabButton != null && toolsTabButton.TryGetComponent<Image>(out var toolImg))
                toolImg.color = !materialsActive ? tabActiveColor : tabInactiveColor;
        }

        private void RefreshAll()
        {
            if (inventory == null) return;

            ClearContainer(materialsContainer, materialEntries);
            ClearContainer(schematicsContainer, schematicEntries);
            ClearContainer(toolsContainer, toolEntries);
            ClearContainer(itemsContainer, itemEntries);

            var allItems = inventory.GetAll();
            var materialMap = allItems.ToDictionary(kvp => kvp.Key, kvp => kvp.Value);

            // 1. Populate Materials (from inventory)
            foreach (var kvp in allItems)
            {
                var def = inventory.GetItemDefinition(kvp.Key);
                if (def == null || def.Category != ItemCategory.Material) continue;
                CreateEntry(materialsContainer, materialEntries, def, kvp.Value, OnMaterialClicked);
            }

            // 2. Populate Recipes (from learned schematics)
            // If the player has a schematic item in inventory, they should learn it
            foreach (var kvp in allItems)
            {
                var def = inventory.GetItemDefinition(kvp.Key);
                if (def != null && def.Category == ItemCategory.Schematic)
                {
                    inventory.LearnSchematic(def.ItemId);
                    inventory.Remove(def.ItemId, kvp.Value); // Consume the item to learn the knowledge
                }
            }

            foreach (var schematicId in inventory.GetLearnedSchematics())
            {
                var def = inventory.GetItemDefinition(schematicId);
                if (def == null) continue;
                var entry = CreateEntryWithReturn(schematicsContainer, schematicEntries, def, 1, OnSchematicClicked);
                PopulateSchematicIngredients(entry, def, materialMap);
            }

            // 3. Populate Tools and Items (from inventory)
            foreach (var kvp in allItems)
            {
                var def = inventory.GetItemDefinition(kvp.Key);
                if (def == null) continue;

                if (def.Category == ItemCategory.Tool)
                    CreateEntry(toolsContainer, toolEntries, def, kvp.Value, OnToolItemClicked);
                else if (def.Category == ItemCategory.Item)
                    CreateEntry(itemsContainer, itemEntries, def, kvp.Value, OnToolItemClicked);
            }
            
            foreach (var entry in materialEntries) if(entry != null) entry.SetSelected(selectedMaterialIds.Contains(entry.Item.ItemId));
            if (selectedSchematic != null) 
            {
                // Verify we still "know" the selected schematic
                if (!inventory.IsSchematicLearned(selectedSchematic.SchematicItem.ItemId))
                    selectedSchematic = null;
                else
                    foreach (var entry in schematicEntries) if(entry != null) entry.SetSelected(entry.Item.ItemId == selectedSchematic.SchematicItem.ItemId);
            }

            if (selectedToolOrItemId != null && !inventory.Contains(selectedToolOrItemId))
                selectedToolOrItemId = null;
            foreach (var entry in toolEntries.Concat(itemEntries))
                if (entry != null) entry.SetSelected(entry.Item.ItemId == selectedToolOrItemId);

            UpdateSchematicStates();
            UpdateActionButton();
        }

        private void PopulateSchematicIngredients(InventoryItemEntryUI entry, ItemDefinition schItem, Dictionary<string, int> available)
        {
            var schematic = schematicDatabase.Find(s => s.SchematicItem.ItemId == schItem.ItemId);
            if (schematic == null) return;
            entry.ClearIngredients();
            foreach (var ing in schematic.Ingredients)
            {
                int owned = available.TryGetValue(ing.item.ItemId, out int qty) ? qty : 0;
                bool hasEnough = owned >= ing.quantity;
                entry.AddIngredient(ing.item.Icon, ing.item.DisplayName, ing.quantity, owned, hasEnough);
            }
        }

        private void CreateEntry(Transform container, List<InventoryItemEntryUI> list, ItemDefinition def, int qty, System.Action<InventoryItemEntryUI> callback)
        {
            var go = Instantiate(itemEntryPrefab, container);
            var entry = go.GetComponent<InventoryItemEntryUI>();
            entry.Initialize(def, qty, callback);
            list.Add(entry);
        }

        private InventoryItemEntryUI CreateEntryWithReturn(Transform container, List<InventoryItemEntryUI> list, ItemDefinition def, int qty, System.Action<InventoryItemEntryUI> callback)
        {
            var go = Instantiate(itemEntryPrefab, container);
            var entry = go.GetComponent<InventoryItemEntryUI>();
            entry.Initialize(def, qty, callback);
            list.Add(entry);
            return entry;
        }

        private void ClearContainer(Transform container, List<InventoryItemEntryUI> list)
        {
            if (container == null) return;
            foreach (var entry in list) if (entry != null) Destroy(entry.gameObject);
            list.Clear();
        }

        private void OnMaterialClicked(InventoryItemEntryUI entry)
        {
            string id = entry.Item.ItemId;
            if (selectedMaterialIds.Contains(id)) selectedMaterialIds.Remove(id);
            else selectedMaterialIds.Add(id);
            entry.SetSelected(selectedMaterialIds.Contains(id));
            UpdateSchematicStates();
            UpdateActionButton();
        }

        private void OnSchematicClicked(InventoryItemEntryUI entry)
        {
            var schematic = schematicDatabase.Find(s => s.SchematicItem.ItemId == entry.Item.ItemId);
            if (schematic == null) return;
            if (selectedSchematic == schematic) {
                selectedSchematic = null;
                entry.SetSelected(false);
            } else {
                selectedSchematic = schematic;
                foreach (var s in schematicEntries) if(s != null) s.SetSelected(s == entry);
            }
            UpdateActionButton();
        }

        private void OnToolItemClicked(InventoryItemEntryUI entry)
        {
            string id = entry.Item.ItemId;
            selectedToolOrItemId = selectedToolOrItemId == id ? null : id;
            foreach (var row in toolEntries.Concat(itemEntries))
                if (row != null) row.SetSelected(row.Item.ItemId == selectedToolOrItemId);
            UpdateActionButton();
        }

        private void UpdateSchematicStates()
        {
            if (inventory == null) return;
            var currentSelection = selectedMaterialIds.ToDictionary(id => id, id => inventory.GetQuantity(id));
            foreach (var entry in schematicEntries) {
                if (entry == null) continue;
                var schematic = schematicDatabase.Find(s => s.SchematicItem.ItemId == entry.Item.ItemId);
                if (schematic == null) continue;
                
                bool canAssemble = schematic.CanAssemble(currentSelection);
                entry.SetReadyForAssembly(canAssemble);
                entry.SetGrayedOut(!canAssemble && selectedMaterialIds.Count > 0); // Gray out non-matching schematics if we have materials selected
            }
        }

        private void UpdateActionButton()
        {
            bool active = false;
            if (isMaterialsTab)
            {
                actionButtonText.text = "Assemble";
                if (inventory != null && selectedSchematic != null)
                {
                    var selection = selectedMaterialIds.ToDictionary(id => id, id => inventory.GetQuantity(id));
                    bool hasIngredients = selectedSchematic.CanAssemble(selection);
                    
                    // Rule: Prevent duplicate permanent tools
                    bool alreadyOwned = selectedSchematic.ResultItem.Category == ItemCategory.Tool && inventory.Contains(selectedSchematic.ResultItem.ItemId);
                    
                    if (alreadyOwned)
                    {
                        actionButtonText.text = "Already Owned";
                        active = false;
                    }
                    else
                    {
                        active = hasIngredients;
                    }
                }
            }
            else
            {
                if (!string.IsNullOrEmpty(selectedToolOrItemId))
                {
                    var def = inventory.GetItemDefinition(selectedToolOrItemId);
                    if (def != null)
                    {
                        if (def.Category == ItemCategory.Tool)
                        {
                            bool isEquipped = toolSystem != null && toolSystem.IsToolEquipped(selectedToolOrItemId);
                            actionButtonText.text = isEquipped ? "Unequip" : "Equip";
                            active = true;
                        }
                        else
                        {
                            actionButtonText.text = "Use";
                            active = true;
                        }
                    }
                }
                else
                {
                    actionButtonText.text = "Equip";
                    active = false;
                }
            }
            actionButton.interactable = active;
            if (actionButton.TryGetComponent<Image>(out var btnImg))
                btnImg.color = active ? buttonActiveColor : buttonInactiveColor;
        }

        private void OnActionClicked()
        {
            if (isMaterialsTab)
            {
                if (selectedSchematic != null)
                {
                    // Double check tool uniqueness rule
                    if (selectedSchematic.ResultItem.Category == ItemCategory.Tool && inventory.Contains(selectedSchematic.ResultItem.ItemId))
                    {
                        Notify("You already have a " + selectedSchematic.ResultItem.DisplayName);
                        return;
                    }

                    // Double check ingredients
                    var currentInventory = inventory.GetAll();
                    if (selectedSchematic.CanAssemble(currentInventory))
                    {
                        foreach (var ingredient in selectedSchematic.Ingredients)
                            inventory.Remove(ingredient.item.ItemId, ingredient.quantity);
                        
                        inventory.Add(selectedSchematic.ResultItem.ItemId, selectedSchematic.ResultQuantity);
                        Notify(selectedSchematic.ResultItem.DisplayName + " assembled");
                        RefreshAll();
                    }
                    else
                    {
                        Notify("Missing materials for " + selectedSchematic.ResultItem.DisplayName);
                    }
                }
            }
            else if (!string.IsNullOrEmpty(selectedToolOrItemId))
            {
                var def = inventory.GetItemDefinition(selectedToolOrItemId);
                if (def == null) return;

                if (def.Category == ItemCategory.Tool)
                {
                    if (toolSystem == null) return;
                    bool isEquipped = toolSystem.IsToolEquipped(selectedToolOrItemId);
                    if (isEquipped)
                    {
                        toolSystem.UnequipTool();
                        Notify(def.DisplayName + " has been unequipped");
                    }
                    else
                    {
                        if (toolSystem.EquipTool(selectedToolOrItemId))
                            Notify(def.DisplayName + " has been equipped");
                    }
                }
                else
                {
                    if (inventory.Remove(selectedToolOrItemId, 1))
                    {
                        Notify(def.DisplayName + " has been used");
                        RefreshAll();
                    }
                }
            }
        }

        private void Notify(string message)
        {
            if (notificationController != null)
                notificationController.ShowNotification(message);
            else
                Debug.Log("[Inventory] " + message);
        }

        private void UpdateBitsDisplay(int amount)
        {
            if (bitsValueText != null) bitsValueText.text = amount.ToString();
        }
    }
}
