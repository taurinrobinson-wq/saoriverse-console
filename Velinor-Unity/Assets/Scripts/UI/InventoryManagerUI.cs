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

        [Header("Visual Settings")]
        [SerializeField] private Color buttonActiveColor = new Color(0.2f, 0.8f, 0.2f, 1f);
        [SerializeField] private Color buttonInactiveColor = new Color(0.3f, 0.3f, 0.3f, 1f);
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
        private bool isMaterialsTab = true;

        private void Awake()
        {
            mainCanvasGroup = GetComponent<CanvasGroup>();
            toggleAction = new InputAction("ToggleInventory", binding: "<Keyboard>/i");
        }

        private void OnEnable()
        {
            inventory = InventoryService.Instance;
            if (inventory != null)
            {
                inventory.OnInventoryChanged += HandleInventoryChanged;
                inventory.OnInventoryCleared += RefreshAll;

                // Temporary test population
                if (populateTestDataAtStart && inventory.GetAll().Count == 0)
                {
                    PopulateInitialTestItems();
                }
            }

            if (materialsTabButton != null) materialsTabButton.onClick.AddListener(() => SwitchTab(true));
            if (toolsTabButton != null) toolsTabButton.onClick.AddListener(() => SwitchTab(false));
            if (actionButton != null) actionButton.onClick.AddListener(OnActionClicked);

            var currency = CurrencySystem.Instance;
            if (currency != null)
            {
                currency.OnBitsChanged += UpdateBitsDisplay;
                UpdateBitsDisplay(currency.CurrentBits);
            }

            if (toggleAction != null) toggleAction.Enable();

            isMaterialsTab = true;
            SwitchTab(true);
            
            CloseInventory();
            RefreshAll();
        }

        private void PopulateInitialTestItems()
        {
            if (inventory == null) return;
            
            // Materials
            string[] materials = { "material_scrap", "material_glass", "material_energycell", "material_circuitry", "material_rubber" };
            foreach (var m in materials) inventory.Add(m, 10);

            // Schematics
            string[] schematics = { 
                "schematic_scanner", "schematic_welder", "schematic_flashlight", 
                "schematic_stim", "schematic_filter", "schematic_ration" 
            };
            foreach (var s in schematics) inventory.Add(s, 1);
            
            Debug.Log("[InventoryManagerUI] Auto-populated test items for Play Mode.");
        }

        private void HandleInventoryChanged(string id, int qty) => RefreshAll();

        private void OnDisable()
        {
            if (inventory != null)
            {
                inventory.OnInventoryChanged -= HandleInventoryChanged;
                inventory.OnInventoryCleared -= RefreshAll;
            }
            if (toggleAction != null) toggleAction.Disable();
        }

        private void Update()
        {
            bool iPressed = false;
            if (toggleAction != null && toggleAction.WasPressedThisFrame()) iPressed = true;
            
            var keyboard = Keyboard.current;
            if (keyboard != null && keyboard.iKey.wasPressedThisFrame) iPressed = true;

            if (iPressed) ToggleInventory();
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
            tab.SetActive(true);
            var cg = tab.GetComponent<CanvasGroup>();
            if (cg == null) cg = tab.AddComponent<CanvasGroup>();
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

            foreach (var kvp in allItems)
            {
                var def = inventory.GetItemDefinition(kvp.Key);
                if (def == null) continue;

                switch (def.Category)
                {
                    case ItemCategory.Material:
                        CreateEntry(materialsContainer, materialEntries, def, kvp.Value, OnMaterialClicked);
                        break;
                    case ItemCategory.Schematic:
                        var entry = CreateEntryWithReturn(schematicsContainer, schematicEntries, def, kvp.Value, OnSchematicClicked);
                        PopulateSchematicIngredients(entry, def, materialMap);
                        break;
                    case ItemCategory.Tool:
                        CreateEntry(toolsContainer, toolEntries, def, kvp.Value, OnToolItemClicked);
                        break;
                    case ItemCategory.CraftedItem:
                    case ItemCategory.Food:
                        CreateEntry(itemsContainer, itemEntries, def, kvp.Value, OnToolItemClicked);
                        break;
                }
            }
            
            foreach (var entry in materialEntries) if(entry != null) entry.SetSelected(selectedMaterialIds.Contains(entry.Item.ItemId));
            if (selectedSchematic != null) 
                foreach (var entry in schematicEntries) if(entry != null) entry.SetSelected(entry.Item.ItemId == selectedSchematic.SchematicItem.ItemId);
            if (selectedToolOrItem != null)
                foreach (var entry in toolEntries.Concat(itemEntries)) if(entry != null) entry.SetSelected(entry == selectedToolOrItem);

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
                bool hasEnough = available.TryGetValue(ing.item.ItemId, out int qty) && qty >= ing.quantity;
                entry.AddIngredient(ing.item.DisplayName, ing.quantity, hasEnough);
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
            if (selectedToolOrItem == entry) selectedToolOrItem = null;
            else selectedToolOrItem = entry;
            foreach (var t in toolEntries.Concat(itemEntries)) if(t != null) t.SetSelected(t == selectedToolOrItem);
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
                entry.SetGrayedOut(!canAssemble);
            }
        }

        private void UpdateActionButton()
        {
            bool active = false;
            if (isMaterialsTab) {
                actionButtonText.text = "Assemble";
                if (inventory != null) active = selectedSchematic != null && selectedSchematic.CanAssemble(selectedMaterialIds.ToDictionary(id => id, id => inventory.GetQuantity(id)));
            } else {
                if (selectedToolOrItem != null) {
                    actionButtonText.text = selectedToolOrItem.Item.Category == ItemCategory.Tool ? "Equip" : "Use";
                    active = true;
                } else {
                    actionButtonText.text = "Equip";
                    active = false;
                }
            }
            actionButton.interactable = active;
            if (actionButton.TryGetComponent<Image>(out var btnImg)) btnImg.color = active ? buttonActiveColor : buttonInactiveColor;
        }

        private void OnActionClicked()
        {
            if (isMaterialsTab) {
                if (selectedSchematic != null) {
                    foreach (var ingredient in selectedSchematic.Ingredients) inventory.Remove(ingredient.item.ItemId, ingredient.quantity);
                    inventory.Add(selectedSchematic.ResultItem.ItemId, selectedSchematic.ResultQuantity);
                    RefreshAll();
                }
            } else {
                if (selectedToolOrItem != null) Debug.Log($"Used {selectedToolOrItem.Item.DisplayName}");
            }
        }

        private void UpdateBitsDisplay(int amount)
        {
            if (bitsValueText != null) bitsValueText.text = amount.ToString();
        }
    }
}
