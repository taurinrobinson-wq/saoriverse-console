using UnityEngine;
using Velinor.Core;

namespace Velinor.Inventory
{
    /// <summary>
    /// WorldItemPickup: Represents a collectible item placed in a scene.
    /// 
    /// Uses ItemPickupData for modular configuration:
    /// - pickupId: Stable identifier for persistence
    /// - itemDefinition: Which item type this is
    /// - quantity: How many to add when collected
    /// - spriteVariants: Environment-specific sprite options (can be different per pickup location)
    /// - Collected status: Prevents respawn after scene reload
    /// </summary>
    public class WorldItemPickup : MonoBehaviour, IInteractable
    {
        [SerializeField] private ItemPickupData pickupData;

        private string pickupCollectionFlag;  // GameFlags key for persistence

        private void Start()
        {
            if (pickupData == null)
            {
                Debug.LogError($"[WorldItemPickup] No ItemPickupData assigned to {gameObject.name}!");
                return;
            }

            // Generate persistence flag
            pickupCollectionFlag = $"pickup_collected_{pickupData.PickupId}";

            // Check if already collected
            if (GameFlags.Get(pickupCollectionFlag))
            {
                Debug.Log($"[WorldItemPickup] {pickupData.PickupId} already collected, hiding");
                gameObject.SetActive(false);
                return;
            }

            // Apply random sprite variant for scrappy aesthetic
            SpriteRenderer spriteRenderer = GetComponent<SpriteRenderer>();
            if (spriteRenderer != null)
            {
                spriteRenderer.sprite = pickupData.GetDisplaySprite();
                Debug.Log($"[WorldItemPickup] {pickupData.PickupId} assigned sprite variant");
            }

            Debug.Log($"[WorldItemPickup] {pickupData.PickupId} ready for collection ({pickupData.Quantity}x {pickupData.ItemDefinition.DisplayName})");
        }

        /// <summary>
        /// Collect this item (called by player interaction or trigger)
        /// </summary>
        public void Collect()
        {
            if (pickupData == null)
            {
                Debug.LogError($"[WorldItemPickup] No ItemPickupData assigned!");
                return;
            }

            if (GameFlags.Get(pickupCollectionFlag))
            {
                Debug.LogWarning($"[WorldItemPickup] {pickupData.PickupId} was already collected");
                return;
            }

            if (pickupData.ItemDefinition == null)
            {
                Debug.LogError($"[WorldItemPickup] {pickupData.PickupId} has no ItemDefinition assigned!");
                return;
            }

            // Add to inventory
            if (InventoryService.Instance.Add(pickupData.ItemDefinition.ItemId, pickupData.Quantity))
            {
                Debug.Log($"[WorldItemPickup] Collected {pickupData.Quantity}x {pickupData.ItemDefinition.DisplayName}");

                // Mark as collected in persistent state
                GameFlags.Set(pickupCollectionFlag, true);

                // Hide from world
                gameObject.SetActive(false);
            }
            else
            {
                Debug.LogWarning($"[WorldItemPickup] Failed to add {pickupData.ItemDefinition.DisplayName} to inventory");
            }
        }

        /// <summary>
        /// IInteractable implementation: Allow player to interact via E key
        /// </summary>
        public void Interact(GameObject player)
        {
            Collect();
        }

        /// <summary>
        /// Editor validation
        /// </summary>
        private void OnValidate()
        {
            // Validation happens in ItemPickupData
        }
    }
}
