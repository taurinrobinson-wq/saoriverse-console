using UnityEngine;
using System.Collections.Generic;

namespace Velinor.Inventory
{
    /// <summary>
    /// Defines a single type of item in Velinor.
    /// Immutable, reusable ScriptableObject describing what an item *is*.
    /// Does not track quantity or state - that's in InventoryService at runtime.
    /// </summary>
    [CreateAssetMenu(menuName = "Velinor/Inventory/Item Definition")]
    public class ItemDefinition : ScriptableObject
    {
        [SerializeField] private string itemId;
        [SerializeField] private string displayName;
        [TextArea(2, 4)] [SerializeField] private string description;
        [SerializeField] private Sprite icon;
        [SerializeField] private GameObject worldPrefab;  // Optional: 3D model for world pickup

        [Header("Classification")]
        [SerializeField] private ItemCategory category;
        [SerializeField] private ItemTag[] tags;

        [Header("Inventory")]
        [Min(1)] [SerializeField] private int maxStackSize = 99;
        [Min(0)] [SerializeField] private int baseValue;

        public string ItemId => itemId;
        public string DisplayName => displayName;
        public string Description => description;
        public Sprite Icon => icon;
        public GameObject WorldPrefab => worldPrefab;
        public ItemCategory Category => category;
        public IReadOnlyList<ItemTag> Tags => tags;
        public int MaxStackSize => maxStackSize;
        public int BaseValue => baseValue;

        /// <summary>
        /// Check if this item has a specific tag (for NPC preferences, crafting, etc.)
        /// </summary>
        public bool HasTag(ItemTag tag)
        {
            foreach (var t in tags)
            {
                if (t == tag)
                    return true;
            }
            return false;
        }

        private void OnValidate()
        {
            // Auto-generate itemId from filename if empty
            if (string.IsNullOrWhiteSpace(itemId))
            {
                itemId = name.ToLower().Replace(" ", "_");
            }
        }
    }

    /// <summary>
    /// Item categories for filtering and organization
    /// </summary>
    public enum ItemCategory
    {
        Material,
        Tool,
        CraftedItem,
        Food,
        PersonalItem,
        KeyItem
    }

    /// <summary>
    /// Item tags for NPC preferences, crafting requirements, and system queries
    /// Tags allow NPCs to request items without hard-coding itemIds
    /// </summary>
    public enum ItemTag
    {
        Metal,           // Copper, steel, aluminum, etc.
        Electrical,      // Wires, circuits, batteries
        Mechanical,      // Gears, springs, mechanisms
        Glass,          // Transparent or translucent materials
        Fabric,         // Cloth, leather, synthetic
        Organic,        // Plant matter, biological materials
        Medical,        // Health-related items
        Culinary,       // Food-related materials
        OldVelharan,    // From the ancient civilization
        Sentimental     // Emotionally significant items
    }
}
