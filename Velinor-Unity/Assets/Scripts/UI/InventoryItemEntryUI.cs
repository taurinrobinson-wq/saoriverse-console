using UnityEngine;
using UnityEngine.UI;
using TMPro;
using Velinor.Core;

namespace Velinor.UI
{
    /// <summary>
    /// Single inventory item display in the inventory panel.
    /// Shows item icon, name, and quantity.
    /// </summary>
    public class InventoryItemEntryUI : MonoBehaviour
    {
        [SerializeField] private Image itemIcon;
        [SerializeField] private TextMeshProUGUI itemName;
        [SerializeField] private TextMeshProUGUI quantityLabel;
        [SerializeField] private LayoutElement layoutElement;
        [SerializeField] private bool showQuantityPrefix = true;
        [SerializeField] private string quantityPrefix = "x";

        private ItemDefinition currentItem;
        private int currentQuantity;

        private void Awake()
        {
            if (layoutElement == null)
                layoutElement = GetComponent<LayoutElement>();
        }

        public void SetItem(ItemDefinition item, int quantity)
        {
            currentItem = item;
            currentQuantity = quantity;

            if (itemName != null)
                itemName.text = item.displayName;

            if (quantityLabel != null)
                quantityLabel.text = showQuantityPrefix ? $"{quantityPrefix}{quantity}" : $"{quantity}";

            if (itemIcon != null && item.icon != null)
                itemIcon.sprite = item.icon;
        }

        public void SetQuantity(int quantity)
        {
            currentQuantity = quantity;

            if (quantityLabel != null)
                quantityLabel.text = showQuantityPrefix ? $"{quantityPrefix}{quantity}" : $"{quantity}";
        }

        public ItemDefinition GetItem() => currentItem;
        public int GetQuantity() => currentQuantity;

        public void Highlight(bool highlight)
        {
            var canvasGroup = GetComponent<CanvasGroup>();
            if (canvasGroup != null)
            {
                canvasGroup.alpha = highlight ? 1f : 0.6f;
            }
        }
    }
}
