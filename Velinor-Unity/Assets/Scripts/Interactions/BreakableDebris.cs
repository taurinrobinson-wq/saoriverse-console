using UnityEngine;
using Velinor.Core;
using Velinor.Inventory;
using Velinor.Interactions;
using System.Collections.Generic;

namespace Velinor.Interactions
{
    /// <summary>
    /// A debris object that can be broken with the right tool to yield materials.
    /// Different from WorldItemPickup in that it requires interaction with a tool.
    /// Persists state via GameFlags so debris doesn't respawn after clearing.
    /// </summary>
    public class BreakableDebris : MonoBehaviour, IInteractable
    {
        [SerializeField] private string debrisId;
        [SerializeField] private SpriteRenderer spriteRenderer;

        [Header("Tool Requirement")]
        [Tooltip("Leave empty for no tool requirement (free debris)")]
        [SerializeField] private string requiredToolId;

        [Header("Materials Yielded")]
        [SerializeField] private List<DebrisMaterial> materials = new();

        [Header("Visual Feedback")]
        [SerializeField] private Color intactColor = Color.white;
        [SerializeField] private Color brokenColor = new Color(0.5f, 0.5f, 0.5f, 0.5f);
        [SerializeField] private Collider2D debrisCollider;

        [Header("Optional VFX")]
        [SerializeField] private GameObject breakEffectPrefab;
        [SerializeField] private AudioClip breakSound;

        private bool isCleared = false;
        private string clearedFlagKey;

        [System.Serializable]
        public class DebrisMaterial
        {
            public string itemId;
            [Min(1)] public int quantity = 1;
        }

        private void OnEnable()
        {
            clearedFlagKey = $"debris_cleared_{debrisId}";
            
            // Check if this debris was already cleared and restore state
            if (GameFlags.Get(clearedFlagKey, false))
            {
                isCleared = true;
            }

            UpdateVisuals();
        }

        private void UpdateVisuals()
        {
            if (isCleared)
            {
                spriteRenderer.color = brokenColor;
                spriteRenderer.sortingOrder = -10; // Push behind other objects
                if (debrisCollider != null)
                    debrisCollider.enabled = false;
            }
            else
            {
                spriteRenderer.color = intactColor;
                if (debrisCollider != null)
                    debrisCollider.enabled = true;
            }
        }

        public void Interact(GameObject player)
        {
            if (isCleared)
            {
                Debug.Log("This debris has already been cleared.");
                return;
            }

            // Check if tool is required and if player has it
            if (!string.IsNullOrEmpty(requiredToolId))
            {
                var toolSystem = ToolSystem.Instance;
                if (toolSystem == null || !toolSystem.HasTool(requiredToolId))
                {
                    Debug.Log($"This debris requires a {requiredToolId} to break.");
                    return;
                }
            }

            // Clear the debris and add materials to inventory
            BreakDebris();
        }

        private void BreakDebris()
        {
            Debug.Log($"Breaking debris: {debrisId}");

            // Play VFX if available
            if (breakEffectPrefab != null)
            {
                Instantiate(breakEffectPrefab, transform.position, Quaternion.identity);
            }

            // Play SFX if available
            if (breakSound != null)
            {
                AudioSource.PlayClipAtPoint(breakSound, transform.position);
            }

            // Add all materials to inventory
            var inventory = InventoryService.Instance;
            if (inventory != null)
            {
                foreach (var material in materials)
                {
                    if (inventory.Add(material.itemId, material.quantity))
                    {
                        Debug.Log($"Added {material.quantity}x {material.itemId} to inventory");
                    }
                    else
                    {
                        Debug.LogWarning($"Failed to add {material.itemId} to inventory");
                    }
                }
            }

            // Mark as cleared and persist via GameFlags
            isCleared = true;
            GameFlags.Set(clearedFlagKey, true);
            UpdateVisuals();

            // Disable interaction
            if (debrisCollider != null)
                debrisCollider.enabled = false;
        }

        /// <summary>
        /// Check if debris has been cleared (for restoration after load).
        /// </summary>
        public bool IsCleared
        {
            get => isCleared;
            set
            {
                isCleared = value;
                if (isCleared)
                {
                    GameFlags.Set(clearedFlagKey, true);
                }
                UpdateVisuals();
            }
        }

        public string DebrisId => debrisId;

        /// <summary>
        /// Check if this debris requires a specific tool.
        /// </summary>
        public bool RequiresTool => !string.IsNullOrEmpty(requiredToolId);
        public string RequiredToolId => requiredToolId;
    }
}
