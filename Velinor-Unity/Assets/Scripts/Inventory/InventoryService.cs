using UnityEngine;
using System.Collections.Generic;
using System;

namespace Velinor.Inventory
{
    /// <summary>
    /// Lightweight runtime inventory system.
    /// Stores only item IDs and quantities (no per-instance data).
    /// Separate concerns: definitions (ItemDatabase), state (this), UI (InventoryUIPanel).
    /// </summary>
    public class InventoryService : MonoBehaviour
    {
        [SerializeField] private ItemDatabase itemDatabase;
        
        // Core inventory state: itemId → quantity
        private Dictionary<string, int> quantities = new Dictionary<string, int>();

        // Events for UI and other systems
        public event Action<string, int> OnInventoryChanged;  // (itemId, newQuantity)
        public event Action OnInventoryCleared;

        private static InventoryService instance;
        public static InventoryService Instance
        {
            get
            {
                if (instance == null)
                {
                    instance = FindAnyObjectByType<InventoryService>();
                    if (instance == null)
                    {
                        Debug.LogError("[InventoryService] No InventoryService found in scene!");
                    }
                }
                return instance;
            }
        }

        public ItemDatabase ItemDatabase => itemDatabase;

        private void Awake()
        {
            // Singleton pattern with duplicate prevention
            if (instance == null)
            {
                instance = this;
                DontDestroyOnLoad(gameObject);
                Debug.Log("[InventoryService] Initialized and marked persistent");
            }
            else if (instance != this)
            {
                Debug.LogWarning("[InventoryService] Duplicate instance destroyed");
                Destroy(gameObject);
                return;
            }

            if (itemDatabase == null)
            {
                Debug.LogError("[InventoryService] ItemDatabase not assigned!");
            }
        }

        /// <summary>
        /// Add items to inventory
        /// </summary>
        public bool Add(string itemId, int amount = 1)
        {
            if (!ValidateItem(itemId))
                return false;

            ItemDefinition item = itemDatabase.Get(itemId);
            if (item == null)
                return false;

            // Get current quantity
            quantities.TryGetValue(itemId, out int current);

            // Check if adding would exceed max stack
            int newQuantity = current + amount;
            if (newQuantity > item.MaxStackSize)
            {
                Debug.LogWarning($"[InventoryService] Cannot add {amount} {itemId}: would exceed max stack of {item.MaxStackSize}");
                return false;
            }

            quantities[itemId] = newQuantity;
            Debug.Log($"[InventoryService] Added {amount}x {itemId} (total: {newQuantity})");
            OnInventoryChanged?.Invoke(itemId, newQuantity);
            return true;
        }

        /// <summary>
        /// Remove items from inventory
        /// </summary>
        public bool Remove(string itemId, int amount = 1)
        {
            if (!ValidateItem(itemId))
                return false;

            quantities.TryGetValue(itemId, out int current);

            if (current < amount)
            {
                Debug.LogWarning($"[InventoryService] Cannot remove {amount} {itemId}: only have {current}");
                return false;
            }

            int newQuantity = current - amount;
            if (newQuantity <= 0)
            {
                quantities.Remove(itemId);
                Debug.Log($"[InventoryService] Removed last {itemId}");
            }
            else
            {
                quantities[itemId] = newQuantity;
                Debug.Log($"[InventoryService] Removed {amount}x {itemId} (remaining: {newQuantity})");
            }

            OnInventoryChanged?.Invoke(itemId, newQuantity);
            return true;
        }

        /// <summary>
        /// Get quantity of an item
        /// </summary>
        public int GetQuantity(string itemId)
        {
            if (quantities.TryGetValue(itemId, out int qty))
                return qty;
            return 0;
        }

        /// <summary>
        /// Check if inventory contains an item (with optional minimum quantity)
        /// </summary>
        public bool Contains(string itemId, int minQuantity = 1)
        {
            return GetQuantity(itemId) >= minQuantity;
        }

        /// <summary>
        /// Get all items currently in inventory
        /// Returns copy to prevent external modification
        /// </summary>
        public Dictionary<string, int> GetAll()
        {
            return new Dictionary<string, int>(quantities);
        }

        /// <summary>
        /// Get all items of a specific category
        /// </summary>
        public Dictionary<string, int> GetByCategory(ItemCategory category)
        {
            Dictionary<string, int> result = new Dictionary<string, int>();

            foreach (var kvp in quantities)
            {
                ItemDefinition item = itemDatabase.Get(kvp.Key);
                if (item != null && item.Category == category)
                {
                    result[kvp.Key] = kvp.Value;
                }
            }

            return result;
        }

        /// <summary>
        /// Get all items with a specific tag
        /// </summary>
        public Dictionary<string, int> GetByTag(ItemTag tag)
        {
            Dictionary<string, int> result = new Dictionary<string, int>();

            foreach (var kvp in quantities)
            {
                ItemDefinition item = itemDatabase.Get(kvp.Key);
                if (item != null && item.HasTag(tag))
                {
                    result[kvp.Key] = kvp.Value;
                }
            }

            return result;
        }

        /// <summary>
        /// Get item definition by ID (for UI and external queries)
        /// </summary>
        public ItemDefinition GetItemDefinition(string itemId)
        {
            if (itemDatabase == null)
                return null;
            return itemDatabase.Get(itemId);
        }

        /// <summary>
        /// Clear entire inventory (for testing or scene resets)
        /// </summary>
        public void Clear()
        {
            quantities.Clear();
            OnInventoryCleared?.Invoke();
            Debug.Log("[InventoryService] Inventory cleared");
        }

        /// <summary>
        /// Validate item exists in database
        /// </summary>
        private bool ValidateItem(string itemId)
        {
            if (itemDatabase == null)
            {
                Debug.LogError("[InventoryService] ItemDatabase is not assigned!");
                return false;
            }

            if (!itemDatabase.Contains(itemId))
            {
                Debug.LogError($"[InventoryService] Item not found in database: {itemId}");
                return false;
            }

            return true;
        }

        #region Save/Load Support

        /// <summary>
        /// Convert inventory to serializable format for saving
        /// </summary>
        public List<InventoryEntryData> GetSaveData()
        {
            List<InventoryEntryData> data = new List<InventoryEntryData>();

            foreach (var kvp in quantities)
            {
                data.Add(new InventoryEntryData { itemId = kvp.Key, quantity = kvp.Value });
            }

            return data;
        }

        /// <summary>
        /// Load inventory from save data
        /// </summary>
        public void LoadSaveData(List<InventoryEntryData> data)
        {
            Clear();

            if (data == null)
                return;

            foreach (var entry in data)
            {
                Add(entry.itemId, entry.quantity);
            }

            Debug.Log($"[InventoryService] Loaded {data.Count} inventory entries");
        }

        #endregion
    }

    /// <summary>
    /// Serializable inventory entry for save/load
    /// </summary>
    [System.Serializable]
    public class InventoryEntryData
    {
        public string itemId;
        public int quantity;
    }
}
