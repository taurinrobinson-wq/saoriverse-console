using UnityEngine;
using UnityEngine.UI;
using TMPro;
using Velinor.Inventory;

namespace Velinor.UI
{
    /// <summary>
    /// Single item entry in a trade display.
    /// Shows item icon, name, and quantity needed/offered.
    /// </summary>
    public class TradeItemEntryUI : MonoBehaviour
    {
        [SerializeField] private Image itemIcon;
        [SerializeField] private TextMeshProUGUI itemNameLabel;
        [SerializeField] private TextMeshProUGUI quantityLabel;

        public void SetItem(ItemDefinition item, int quantity)
        {
            if (itemNameLabel != null)
                itemNameLabel.text = item.DisplayName;

            if (quantityLabel != null)
                quantityLabel.text = $"x{quantity}";

            if (itemIcon != null && item.Icon != null)
                itemIcon.sprite = item.Icon;
        }

        public void SetBits(int amount)
        {
            if (itemNameLabel != null)
                itemNameLabel.text = "Bits";

            if (quantityLabel != null)
                quantityLabel.text = $"+{amount}";

            // Bits icon could be set here if you have one
            if (itemIcon != null)
            {
                // Clear icon or set to a bits icon
                itemIcon.sprite = null;
            }
        }
    }
}

