using UnityEngine;
using Velinor.Core;

namespace Velinor.Inventory
{
    /// <summary>
    /// WorldItemPickup: Represents a collectible item placed in a scene.
    /// 
    /// Tracks:
    /// - pickupId: Stable identifier for persistence
    /// - itemId: Which item type this is
    /// - quantity: How many to add when collected
    /// - Collected status: Prevents respawn after scene reload
    /// </summary>
    public class WorldItemPickup : MonoBehaviour, IInteractable
    {
        [SerializeField] private string pickupId;  // Unique ID in this scene (e.g., "market_wire_01")
        [SerializeField] private ItemDefinition itemDefinition;
        [Min(1)] [SerializeField] private int quantity = 1;

        private string pickupCollectionFlag;  // GameFlags key for persistence

        private void Start()
        {
            // Generate persistence flag
            pickupCollectionFlag = $"pickup_collected_{pickupId}";

            // Check if already collected
            if (GameFlags.Get(pickupCollectionFlag))
            {
                Debug.Log($"[WorldItemPickup] {pickupId} already collected, hiding");
                gameObject.SetActive(false);
                return;
            }

            Debug.Log($"[WorldItemPickup] {pickupId} ready for collection ({quantity}x {itemDefinition.DisplayName})");
        }

        /// <summary>
        /// Collect this item (called by player interaction or trigger)
        /// </summary>
        public void Collect()
        {
            if (GameFlags.Get(pickupCollectionFlag))
            {
                Debug.LogWarning($"[WorldItemPickup] {pickupId} was already collected");
                return;
            }

            if (itemDefinition == null)
            {
                Debug.LogError($"[WorldItemPickup] {pickupId} has no ItemDefinition assigned!");
                return;
            }

            // Add to inventory
            if (InventoryService.Instance.Add(itemDefinition.ItemId, quantity))
            {
                Debug.Log($"[WorldItemPickup] Collected {quantity}x {itemDefinition.DisplayName}");

                // Mark as collected in persistent state
                GameFlags.Set(pickupCollectionFlag, true);

                // Hide from world
                gameObject.SetActive(false);
            }
            else
            {
                Debug.LogWarning($"[WorldItemPickup] Failed to add {itemDefinition.DisplayName} to inventory");
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
            // Auto-generate pickupId if empty
            if (string.IsNullOrWhiteSpace(pickupId))
            {
                pickupId = gameObject.name.ToLower().Replace(" ", "_");
            }
        }
    }
}
