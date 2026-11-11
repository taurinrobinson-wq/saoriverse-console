using UnityEngine;
using System.Collections.Generic;

namespace Velinor.Inventory
{
    /// <summary>
    /// ItemDatabase: Central registry of all item definitions.
    /// 
    /// Provides:
    /// - Fast O(1) lookup by itemId
    /// - Duplicate ID detection
    /// - Stable save/load (via itemId, not asset references)
    /// - Freedom to rename/reorganize items without breaking saves
    /// </summary>
    [CreateAssetMenu(menuName = "Velinor/Inventory/Item Database")]
    public class ItemDatabase : ScriptableObject
    {
        [SerializeField] private List<ItemDefinition> items;

        private Dictionary<string, ItemDefinition> lookup;
        private bool isInitialized = false;

        /// <summary>
        /// Get an item definition by ID
        /// </summary>
        public ItemDefinition Get(string itemId)
        {
            BuildLookupIfNeeded();

            if (!lookup.TryGetValue(itemId, out ItemDefinition item))
            {
                Debug.LogError($"[ItemDatabase] Unknown item ID: {itemId}");
                return null;
            }

            return item;
        }

        /// <summary>
        /// Check if an item exists
        /// </summary>
        public bool Contains(string itemId)
        {
            BuildLookupIfNeeded();
            return lookup.ContainsKey(itemId);
        }

        /// <summary>
        /// Get all item definitions
        /// </summary>
        public IReadOnlyList<ItemDefinition> GetAll()
        {
            return items.AsReadOnly();
        }

        /// <summary>
        /// Build lookup dictionary from items list (lazy initialization)
        /// </summary>
        private void BuildLookupIfNeeded()
        {
            if (isInitialized)
                return;

            lookup = new Dictionary<string, ItemDefinition>();

            foreach (ItemDefinition item in items)
            {
                if (item == null || string.IsNullOrWhiteSpace(item.ItemId))
                    continue;

                if (!lookup.TryAdd(item.ItemId, item))
                    Debug.LogError($"[ItemDatabase] Duplicate item ID: {item.ItemId}");
            }

            isInitialized = true;
            Debug.Log($"[ItemDatabase] Initialized with {lookup.Count} items");
        }

        /// <summary>
        /// Editor-only validation
        /// </summary>
        private void OnValidate()
        {
            // Reset lookup on changes so it rebuilds with new data
            isInitialized = false;
            lookup = null;
        }
    }
}
