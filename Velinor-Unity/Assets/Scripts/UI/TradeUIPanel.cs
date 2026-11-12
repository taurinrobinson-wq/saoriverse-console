using UnityEngine;
using TMPro;
using UnityEngine.UI;
using System.Collections.Generic;
using Velinor.Inventory;
using Velinor.Core;
using Velinor.Economy;

namespace Velinor.UI
{
    /// <summary>
    /// Displays NPC trading interface.
    /// Shows what items NPC wants and what they offer.
    /// Handles trade execution.
    /// </summary>
    public class TradeUIPanel : MonoBehaviour
    {
        [SerializeField] private TextMeshProUGUI npcNameLabel;
        [SerializeField] private Transform wantedItemsContainer;
        [SerializeField] private Transform offeredItemsContainer;
        [SerializeField] private GameObject tradeItemEntryPrefab;
        [SerializeField] private Button tradeButton;
        [SerializeField] private TextMeshProUGUI tradeButtonLabel;
        [SerializeField] private TextMeshProUGUI statusLabel;
        [SerializeField] private CanvasGroup panelCanvasGroup;

        private NPCTrader currentNPC;
        private InventoryService inventoryService;
        private CurrencySystem currencySystem;

        private void OnEnable()
        {
            inventoryService = InventoryService.Instance;
            currencySystem = CurrencySystem.Instance;

            if (tradeButton != null)
                tradeButton.onClick.AddListener(ExecuteTrade);

            gameObject.SetActive(false);
        }

        private void OnDisable()
        {
            if (tradeButton != null)
                tradeButton.onClick.RemoveListener(ExecuteTrade);
        }

        public void ShowTradeUI(NPCTrader npc)
        {
            currentNPC = npc;
            gameObject.SetActive(true);

            if (npcNameLabel != null)
                npcNameLabel.text = npc.gameObject.name;

            PopulateWantedItems();
            PopulateOfferedItems();
            UpdateTradeButtonState();
        }

        public void HideTradeUI()
        {
            gameObject.SetActive(false);
            currentNPC = null;
        }

        private void PopulateWantedItems()
        {
            if (wantedItemsContainer == null || currentNPC == null)
                return;

            // Clear
            foreach (Transform child in wantedItemsContainer)
            {
                Destroy(child.gameObject);
            }

            // Show items NPC wants
            var wantedItems = currentNPC.GetWantedItems();
            foreach (var item in wantedItems)
            {
                CreateTradeEntryDisplay(item.itemId, item.quantity, wantedItemsContainer, false);
            }
        }

        private void PopulateOfferedItems()
        {
            if (offeredItemsContainer == null || currentNPC == null)
                return;

            // Clear
            foreach (Transform child in offeredItemsContainer)
            {
                Destroy(child.gameObject);
            }

            // Show items NPC offers (their payment)
            var trade = currentNPC.GetTradeProfile();
            var itemDB = inventoryService.ItemDatabase;
            
            // Show Bits payment
            int bitsOffered = currentNPC.CalculatePayment();
            var bitsEntry = Instantiate(tradeItemEntryPrefab, offeredItemsContainer);
            var bitsEntryUI = bitsEntry.GetComponent<TradeItemEntryUI>();
            if (bitsEntryUI != null)
            {
                bitsEntryUI.SetBits(bitsOffered);
            }
        }

        private void CreateTradeEntryDisplay(string itemId, int quantity, Transform container, bool isOffered)
        {
            var itemDef = inventoryService.ItemDatabase.GetItem(itemId);
            if (itemDef == null)
                return;

            var entryGO = Instantiate(tradeItemEntryPrefab, container);
            var entry = entryGO.GetComponent<TradeItemEntryUI>();

            if (entry != null)
            {
                entry.SetItem(itemDef, quantity);
            }
        }

        private void UpdateTradeButtonState()
        {
            if (currentNPC == null || tradeButton == null)
                return;

            bool canTrade = CanExecuteTrade();
            tradeButton.interactable = canTrade;

            if (tradeButtonLabel != null)
            {
                tradeButtonLabel.text = canTrade ? "Trade" : "Cannot Trade";
            }

            if (statusLabel != null)
            {
                if (!canTrade)
                {
                    var missing = currentNPC.GetMissingItems();
                    if (missing.Count > 0)
                    {
                        statusLabel.text = $"Need: {missing[0].itemId} (x{missing[0].quantity})";
                    }
                }
                else
                {
                    statusLabel.text = "Ready to trade!";
                }
            }
        }

        private bool CanExecuteTrade()
        {
            if (currentNPC == null || inventoryService == null)
                return false;

            var wantedItems = currentNPC.GetWantedItems();
            var playerInventory = inventoryService.GetInventoryData();

            foreach (var wanted in wantedItems)
            {
                if (!playerInventory.ContainsKey(wanted.itemId) || 
                    playerInventory[wanted.itemId] < wanted.quantity)
                {
                    return false;
                }
            }

            return true;
        }

        private void ExecuteTrade()
        {
            if (!CanExecuteTrade() || currentNPC == null)
                return;

            // Remove wanted items from inventory
            var wantedItems = currentNPC.GetWantedItems();
            foreach (var wanted in wantedItems)
            {
                inventoryService.RemoveItem(wanted.itemId, wanted.quantity);
            }

            // Add bits payment
            int bitsEarned = currentNPC.CalculatePayment();
            currencySystem.AddBits(bitsEarned, $"Trade with {currentNPC.gameObject.name}");

            // Update UI
            UpdateTradeButtonState();

            if (statusLabel != null)
            {
                statusLabel.text = $"Trade complete! +{bitsEarned} Bits";
            }
        }
    }
}
