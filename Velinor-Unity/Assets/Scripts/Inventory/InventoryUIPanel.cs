using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;

namespace Velinor.Inventory
{
    /// <summary>
    /// InventoryUIPanel: Left-side UI panel showing player's inventory.
    /// 
    /// Features:
    /// - Lists items by category or all items
    /// - Shows quantity for each item
    /// - Alpha-based visibility toggling
    /// - Subscribes to inventory changes and updates in real-time
    /// 
    /// Setup:
    /// 1. Parented to UI_Canvas as left panel
    /// 2. Contains VerticalLayoutGroup with InventoryItemEntryUI prefab instances
    /// 3. Toggled via CanvasGroup.alpha (not active/inactive)
    /// </summary>
    public class InventoryUIPanel : MonoBehaviour
    {
        [SerializeField] private CanvasGroup canvasGroup;  // For alpha visibility
        [SerializeField] private VerticalLayoutGroup itemListLayout;
        [SerializeField] private InventoryItemEntryUI itemEntryPrefab;

        [Header("Display Settings")]
        [SerializeField] private bool showEmptyCategories = false;
        [SerializeField] private float visibilityDuration = 0.3f;  // Alpha fade duration

        private Dictionary<string, InventoryItemEntryUI> activeEntries = new Dictionary<string, InventoryItemEntryUI>();
        private bool isVisible = false;

        private void OnEnable()
        {
            if (InventoryService.Instance != null)
            {
                InventoryService.Instance.OnInventoryChanged += HandleInventoryChanged;
                InventoryService.Instance.OnInventoryCleared += HandleInventoryClear;
                RefreshDisplay();
            }
        }

        private void OnDisable()
        {
            if (InventoryService.Instance != null)
            {
                InventoryService.Instance.OnInventoryChanged -= HandleInventoryChanged;
                InventoryService.Instance.OnInventoryCleared -= HandleInventoryClear;
            }
        }

        private void Start()
        {
            if (canvasGroup == null)
                canvasGroup = GetComponent<CanvasGroup>();

            if (canvasGroup == null)
            {
                Debug.LogError("[InventoryUIPanel] CanvasGroup not found!");
                return;
            }

            // Start hidden
            canvasGroup.alpha = 0f;
            isVisible = false;
        }

        /// <summary>
        /// Toggle inventory panel visibility (with alpha fade)
        /// </summary>
        public void ToggleVisibility()
        {
            SetVisibility(!isVisible);
        }

        /// <summary>
        /// Set visibility state
        /// </summary>
        public void SetVisibility(bool visible)
        {
            if (visible == isVisible)
                return;

            isVisible = visible;
            canvasGroup.alpha = visible ? 1f : 0f;
            canvasGroup.blocksRaycasts = visible;  // Don't intercept clicks when hidden

            Debug.Log($"[InventoryUIPanel] Visibility: {(visible ? "SHOW" : "HIDE")}");
        }

        /// <summary>
        /// Refresh entire inventory display
        /// </summary>
        private void RefreshDisplay()
        {
            // Clear existing entries
            ClearDisplay();

            if (InventoryService.Instance == null)
                return;

            Dictionary<string, int> inventory = InventoryService.Instance.GetAll();

            if (inventory.Count == 0)
            {
                CreateEmptyPlaceholder();
                return;
            }

            // Create entry for each item
            foreach (var kvp in inventory)
            {
                ItemDefinition item = InventoryService.Instance.GetItemDefinition(kvp.Key);
                if (item != null)
                {
                    CreateItemEntry(item, kvp.Value);
                }
            }

            Debug.Log($"[InventoryUIPanel] Refreshed display ({inventory.Count} items)");
        }

        /// <summary>
        /// Create a single inventory item entry in the UI
        /// </summary>
        private void CreateItemEntry(ItemDefinition item, int quantity)
        {
            if (itemEntryPrefab == null)
            {
                Debug.LogError("[InventoryUIPanel] Item entry prefab not assigned!");
                return;
            }

            InventoryItemEntryUI entry = Instantiate(itemEntryPrefab, itemListLayout.transform);
            entry.Initialize(item, quantity);
            activeEntries[item.ItemId] = entry;
        }

        /// <summary>
        /// Create placeholder when inventory is empty
        /// </summary>
        private void CreateEmptyPlaceholder()
        {
            Text placeholderText = new GameObject("Placeholder", typeof(Text)).GetComponent<Text>();
            placeholderText.transform.SetParent(itemListLayout.transform, false);
            placeholderText.text = "Empty";
            placeholderText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            placeholderText.fontSize = 14;
            placeholderText.fontStyle = FontStyle.Italic;
            placeholderText.color = new Color(0.7f, 0.7f, 0.7f);
        }

        /// <summary>
        /// Clear all item entries from display
        /// </summary>
        private void ClearDisplay()
        {
            foreach (Transform child in itemListLayout.transform)
            {
                Destroy(child.gameObject);
            }
            activeEntries.Clear();
        }

        /// <summary>
        /// Handle inventory change event
        /// </summary>
        private void HandleInventoryChanged(string itemId, int newQuantity)
        {
            // Update or create entry
            if (activeEntries.TryGetValue(itemId, out InventoryItemEntryUI entry))
            {
                if (newQuantity <= 0)
                {
                    // Remove from display
                    Destroy(entry.gameObject);
                    activeEntries.Remove(itemId);
                }
                else
                {
                    // Update quantity
                    entry.SetQuantity(newQuantity);
                }
            }
            else if (newQuantity > 0)
            {
                // Add new entry
                ItemDefinition item = InventoryService.Instance.GetItemDefinition(itemId);
                if (item != null)
                {
                    CreateItemEntry(item, newQuantity);
                }
            }
        }

        /// <summary>
        /// Handle inventory clear event
        /// </summary>
        private void HandleInventoryClear()
        {
            ClearDisplay();
            CreateEmptyPlaceholder();
        }
    }
}
