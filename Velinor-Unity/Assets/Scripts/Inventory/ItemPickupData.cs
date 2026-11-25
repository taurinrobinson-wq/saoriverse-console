using UnityEngine;

namespace Velinor.Inventory
{
    /// <summary>
    /// ItemPickupData: Modular configuration for world item pickups.
    /// 
    /// Separates environment-specific sprite variations from ItemDefinition.
    /// Allows drag-and-drop of sprite variants and configuration of pickup properties.
    /// 
    /// Usage: Create one ItemPickupData per item type or per pickup location.
    /// Reference it in WorldItemPickup prefab to get different appearances.
    /// </summary>
    [CreateAssetMenu(menuName = "Velinor/Inventory/Item Pickup Data")]
    public class ItemPickupData : ScriptableObject
    {
        [SerializeField] private string pickupId;
        [SerializeField] private ItemDefinition itemDefinition;
        [Min(1)] [SerializeField] private int quantity = 1;

        [Header("Sprite Variants (for environment display)")]
        [SerializeField] private Sprite[] spriteVariants;

        public string PickupId => pickupId;
        public ItemDefinition ItemDefinition => itemDefinition;
        public int Quantity => quantity;

        /// <summary>
        /// Get a random sprite variant for display in the world.
        /// If variants are defined here, uses them. Otherwise falls back to ItemDefinition.Icon.
        /// </summary>
        public Sprite GetDisplaySprite()
        {
            if (spriteVariants != null && spriteVariants.Length > 0)
            {
                int randomIndex = Random.Range(0, spriteVariants.Length);
                Sprite selected = spriteVariants[randomIndex];
                if (selected != null)
                    return selected;
            }

            if (itemDefinition != null)
                return itemDefinition.Icon;

            return null;
        }

        private void OnValidate()
        {
            // Auto-generate pickupId from asset name if empty
            if (string.IsNullOrWhiteSpace(pickupId))
            {
                pickupId = name.ToLower().Replace(" ", "_");
            }
        }
    }
}
