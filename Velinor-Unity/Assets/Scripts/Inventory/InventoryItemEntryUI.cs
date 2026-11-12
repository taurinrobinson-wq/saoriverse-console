using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections.Generic;

namespace Velinor.Inventory
{
    /// <summary>
    /// InventoryItemEntryUI: Single row in inventory list.
    /// Shows item icon, name, quantity, and demand info.
    /// </summary>
    public class InventoryItemEntryUI : MonoBehaviour
    {
        [Header("Main Display")]
        [SerializeField] private Image itemIcon;
        [SerializeField] private TextMeshProUGUI itemNameText;
        [SerializeField] private TextMeshProUGUI itemQuantityText;
        [SerializeField] private Button entryButton;
        [SerializeField] private Image selectionHighlight;

        [Header("Demand Info")]
        [SerializeField] private GameObject demandRoot;
        [SerializeField] private Button demandToggleCarrot;
        [SerializeField] private Transform demandContainer;
        [SerializeField] private GameObject demandEntryPrefab;

        [Header("Ingredients")]
        [SerializeField] private GameObject ingredientRoot;
        [SerializeField] private Transform ingredientContainer;
        [SerializeField] private GameObject ingredientEntryPrefab;

        private ItemDefinition itemDefinition;
        private int currentQuantity;
        private bool isSelected = false;
        private System.Action<InventoryItemEntryUI> onClickedCallback;

        private void Start()
        {
            if (entryButton != null)
            {
                entryButton.onClick.AddListener(OnEntryClicked);
            }
            if (demandToggleCarrot != null)
            {
                demandToggleCarrot.onClick.AddListener(ToggleDemandPanel);
            }
            if (demandRoot != null)
            {
                demandRoot.SetActive(false);
            }
            if (ingredientRoot != null)
            {
                ingredientRoot.SetActive(false);
            }
            UpdateSelectionVisual();
        }

        public void Initialize(ItemDefinition item, int quantity, System.Action<InventoryItemEntryUI> onClicked = null)
        {
            itemDefinition = item;
            currentQuantity = quantity;
            onClickedCallback = onClicked;

            if (itemIcon != null && item.Icon != null)
            {
                itemIcon.sprite = item.Icon;
            }

            if (itemNameText != null)
            {
                itemNameText.text = item.DisplayName;
            }

            UpdateQuantityDisplay();
        }

        public void ClearIngredients()
        {
            if (ingredientContainer == null) return;
            foreach (Transform child in ingredientContainer) Destroy(child.gameObject);
            if (ingredientRoot != null) ingredientRoot.SetActive(false);
        }

        public void AddIngredient(string name, int qty, bool satisfied)
        {
            if (ingredientEntryPrefab == null || ingredientContainer == null) return;
            if (ingredientRoot != null) ingredientRoot.SetActive(true);
            
            var entry = Instantiate(ingredientEntryPrefab, ingredientContainer);
            var texts = entry.GetComponentsInChildren<TextMeshProUGUI>();
            if (texts.Length >= 2)
            {
                texts[0].text = name;
                texts[1].text = $"x{qty}";
                texts[1].color = satisfied ? Color.green : Color.red;
            }
        }

        public void SetQuantity(int quantity)
        {
            currentQuantity = quantity;
            UpdateQuantityDisplay();
        }

        public void SetSelected(bool selected)
        {
            isSelected = selected;
            UpdateSelectionVisual();
        }

        public void SetGrayedOut(bool grayed)
        {
            if (itemIcon != null) itemIcon.color = grayed ? new Color(0.5f, 0.5f, 0.5f, 0.5f) : Color.white;
            if (itemNameText != null) itemNameText.color = grayed ? Color.gray : Color.white;
        }

        public void AddDemand(string npcName, int bitsOffered)
        {
            if (demandEntryPrefab == null || demandContainer == null) return;
            
            var entry = Instantiate(demandEntryPrefab, demandContainer);
            var texts = entry.GetComponentsInChildren<TextMeshProUGUI>();
            // Assume 0 is NPC Name, 1 is Bits
            if (texts.Length >= 2)
            {
                texts[0].text = npcName;
                texts[1].text = $"{bitsOffered} Bits";
            }
        }

        private void UpdateQuantityDisplay()
        {
            if (itemQuantityText != null)
            {
                itemQuantityText.text = currentQuantity > 1 ? $"x{currentQuantity}" : "";
            }
        }

        private void UpdateSelectionVisual()
        {
            if (selectionHighlight != null)
            {
                selectionHighlight.enabled = isSelected;
            }
        }

        private void OnEntryClicked()
        {
            onClickedCallback?.Invoke(this);
        }

        private void ToggleDemandPanel()
        {
            if (demandRoot != null)
            {
                demandRoot.SetActive(!demandRoot.activeSelf);
                // Rotate carrot if needed
                if (demandToggleCarrot != null)
                {
                    demandToggleCarrot.transform.localRotation = Quaternion.Euler(0, 0, demandRoot.activeSelf ? -90 : 0);
                }
            }
        }

        public ItemDefinition Item => itemDefinition;
        public int Quantity => currentQuantity;
        public bool IsSelected => isSelected;
    }
}
