using UnityEngine;
using UnityEngine.UI;

namespace Velinor.Inventory
{
    /// <summary>
    /// InventoryItemEntryUI: Single row in inventory list.
    /// Shows item icon, name, quantity, and description on hover.
    /// 
    /// Expected hierarchy:
    /// - HorizontalLayoutGroup (root)
    ///   - Image (icon)
    ///   - VerticalLayoutGroup
    ///     - Text (name)
    ///     - Text (quantity)
    ///   - (optional) Tooltip or inspector panel for details
    /// </summary>
    public class InventoryItemEntryUI : MonoBehaviour
    {
        [SerializeField] private Image itemIcon;
        [SerializeField] private Text itemNameText;
        [SerializeField] private Text itemQuantityText;
        [SerializeField] private Button entryButton;

        private ItemDefinition itemDefinition;
        private int currentQuantity;

        private void Start()
        {
            if (entryButton != null)
            {
                entryButton.onClick.AddListener(OnEntryClicked);
            }
        }

        /// <summary>
        /// Initialize this entry with item data
        /// </summary>
        public void Initialize(ItemDefinition item, int quantity)
        {
            itemDefinition = item;
            currentQuantity = quantity;

            // Set icon
            if (itemIcon != null && item.Icon != null)
            {
                itemIcon.sprite = item.Icon;
            }

            // Set name
            if (itemNameText != null)
            {
                itemNameText.text = item.DisplayName;
            }

            // Set quantity
            UpdateQuantityDisplay();

            Debug.Log($"[InventoryItemEntryUI] Initialized: {item.DisplayName} x{quantity}");
        }

        /// <summary>
        /// Update quantity display
        /// </summary>
        public void SetQuantity(int quantity)
        {
            currentQuantity = quantity;
            UpdateQuantityDisplay();
        }

        /// <summary>
        /// Internal helper to update quantity text
        /// </summary>
        private void UpdateQuantityDisplay()
        {
            if (itemQuantityText != null)
            {
                if (currentQuantity > 1)
                {
                    itemQuantityText.text = $"x{currentQuantity}";
                }
                else
                {
                    itemQuantityText.text = "";  // Hide for single item
                }
            }
        }

        /// <summary>
        /// Called when player clicks this inventory entry
        /// </summary>
        private void OnEntryClicked()
        {
            if (itemDefinition == null)
                return;

            Debug.Log($"[InventoryItemEntryUI] Selected: {itemDefinition.DisplayName}");

            // TODO: Show item details panel or tooltip
            // For now, just log for debugging
        }

        /// <summary>
        /// Get the item definition for external queries
        /// </summary>
        public ItemDefinition GetItemDefinition()
        {
            return itemDefinition;
        }

        /// <summary>
        /// Get current quantity
        /// </summary>
        public int GetQuantity()
        {
            return currentQuantity;
        }
    }
}
