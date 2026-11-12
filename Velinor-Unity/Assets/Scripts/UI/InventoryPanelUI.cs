using UnityEngine;
using TMPro;
using System.Collections.Generic;
using Velinor.Inventory;
using Velinor.Core;

namespace Velinor.UI
{
    /// <summary>
    /// Displays inventory grid with items and quantities.
    /// Updates when inventory changes.
    /// </summary>
    public class InventoryPanelUI : MonoBehaviour
    {
        [SerializeField] private Transform itemContainer;
        [SerializeField] private GameObject itemEntryPrefab;
        [SerializeField] private TextMeshProUGUI emptyInventoryLabel;
        [SerializeField] private bool autoHideWhenEmpty = true;

        private InventoryService inventoryService;
        private Dictionary<string, InventoryItemEntryUI> displayedItems = new();
        private CanvasGroup canvasGroup;

        private void OnEnable()
        {
            inventoryService = InventoryService.Instance;
            if (inventoryService != null)
            {
                inventoryService.OnItemAdded += OnItemAdded;
                inventoryService.OnItemRemoved += OnItemRemoved;
                inventoryService.OnInventoryChanged += OnInventoryChanged;
                
                // Initial population
                RefreshDisplay();
            }

            canvasGroup = GetComponent<CanvasGroup>();
        }

        private void OnDisable()
        {
            if (inventoryService != null)
            {
                inventoryService.OnItemAdded -= OnItemAdded;
                inventoryService.OnItemRemoved -= OnItemRemoved;
                inventoryService.OnInventoryChanged -= OnInventoryChanged;
            }
        }

        private void OnItemAdded(string itemId, int quantity)
        {
            UpdateItemDisplay(itemId, quantity);
        }

        private void OnItemRemoved(string itemId, int quantity)
        {
            var inventory = inventoryService.GetInventoryData();
            if (inventory.ContainsKey(itemId))
            {
                UpdateItemDisplay(itemId, inventory[itemId]);
            }
            else
            {
                RemoveItemDisplay(itemId);
            }
        }

        private void OnInventoryChanged()
        {
            RefreshDisplay();
        }

        private void UpdateItemDisplay(string itemId, int quantity)
        {
            if (displayedItems.TryGetValue(itemId, out var entry))
            {
                entry.SetQuantity(quantity);
            }
            else
            {
                CreateItemDisplay(itemId, quantity);
            }

            UpdateEmptyState();
        }

        private void CreateItemDisplay(string itemId, int quantity)
        {
            if (itemEntryPrefab == null)
            {
                Debug.LogError("[InventoryPanelUI] Item entry prefab not assigned!");
                return;
            }

            var itemDef = inventoryService.ItemDatabase.GetItem(itemId);
            if (itemDef == null)
            {
                Debug.LogWarning($"[InventoryPanelUI] Item definition not found: {itemId}");
                return;
            }

            var entryGO = Instantiate(itemEntryPrefab, itemContainer);
            var entry = entryGO.GetComponent<InventoryItemEntryUI>();

            if (entry != null)
            {
                entry.SetItem(itemDef, quantity);
                displayedItems[itemId] = entry;
            }
        }

        private void RemoveItemDisplay(string itemId)
        {
            if (displayedItems.TryGetValue(itemId, out var entry))
            {
                Destroy(entry.gameObject);
                displayedItems.Remove(itemId);
            }

            UpdateEmptyState();
        }

        private void RefreshDisplay()
        {
            // Clear existing displays
            foreach (var entry in displayedItems.Values)
            {
                Destroy(entry.gameObject);
            }
            displayedItems.Clear();

            // Repopulate from inventory
            var inventory = inventoryService.GetInventoryData();
            foreach (var kvp in inventory)
            {
                CreateItemDisplay(kvp.Key, kvp.Value);
            }

            UpdateEmptyState();
        }

        private void UpdateEmptyState()
        {
            bool isEmpty = displayedItems.Count == 0;

            if (emptyInventoryLabel != null)
            {
                emptyInventoryLabel.gameObject.SetActive(isEmpty);
            }

            if (autoHideWhenEmpty && canvasGroup != null)
            {
                canvasGroup.alpha = isEmpty ? 0f : 1f;
                canvasGroup.blocksRaycasts = !isEmpty;
            }
        }

        public void ClearInventoryDisplay()
        {
            foreach (var entry in displayedItems.Values)
            {
                Destroy(entry.gameObject);
            }
            displayedItems.Clear();
            UpdateEmptyState();
        }
    }
}
