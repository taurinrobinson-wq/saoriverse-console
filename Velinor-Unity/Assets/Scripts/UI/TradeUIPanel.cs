using UnityEngine;
using TMPro;
using UnityEngine.UI;
using System.Collections.Generic;
using Velinor.Inventory;
using Velinor.Economy;
using Velinor.Interactions;

namespace Velinor.UI
{
    /// <summary>
    /// Displays NPC trading interface.
    /// Shows what items NPC wants and what they offer in return.
    /// Handles trade execution through NPCTrader.CreateTradeOffer and ExecuteTrade.
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
        private NPCTradeOffer currentOffer;
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

            if (npcNameLabel != null && npc.TradeProfile != null)
                npcNameLabel.text = npc.TradeProfile.NpcDisplayName;

            UpdateTradeDisplay();
        }

        public void HideTradeUI()
        {
            gameObject.SetActive(false);
            currentNPC = null;
            currentOffer = null;
        }

        private void UpdateTradeDisplay()
        {
            if (currentNPC == null || currentNPC.TradeProfile == null)
                return;

            // Clear existing displays
            foreach (Transform child in wantedItemsContainer)
            {
                Destroy(child.gameObject);
            }
            foreach (Transform child in offeredItemsContainer)
            {
                Destroy(child.gameObject);
            }

            // Display what NPC wants (their preferences)
            var profile = currentNPC.TradeProfile;
            var itemDb = inventoryService.ItemDatabase;

            // Show preferred items NPC wants
            foreach (var preferredItem in profile.PreferredItems)
            {
                var itemDef = itemDb.Get(preferredItem);
                if (itemDef != null)
                {
                    CreateWantedItemDisplay(itemDef, 1);
                }
            }

            // Show what NPC would pay for the wanted items
            // This is calculated based on profile preferences
            // For simplicity, we'll show a fixed bits amount for demonstration
            CreateOfferedBitsDisplay(50); // This would be calculated by profile.CalculateOfferedPrice()

            UpdateTradeButtonState();
        }

        private void CreateWantedItemDisplay(ItemDefinition itemDef, int quantity)
        {
            var entryGO = Instantiate(tradeItemEntryPrefab, wantedItemsContainer);
            var entry = entryGO.GetComponent<TradeItemEntryUI>();

            if (entry != null)
            {
                entry.SetItem(itemDef, quantity);
            }
        }

        private void CreateOfferedBitsDisplay(int amount)
        {
            var entryGO = Instantiate(tradeItemEntryPrefab, offeredItemsContainer);
            var entry = entryGO.GetComponent<TradeItemEntryUI>();

            if (entry != null)
            {
                entry.SetBits(amount);
            }
        }

        private void UpdateTradeButtonState()
        {
            if (currentNPC == null || tradeButton == null)
                return;

            // For now, always allow trade button to be clicked
            // The actual trade will fail if items aren't available
            tradeButton.interactable = true;

            if (tradeButtonLabel != null)
            {
                tradeButtonLabel.text = "Trade";
            }

            if (statusLabel != null)
            {
                statusLabel.text = "Ready to trade!";
            }
        }

        private void ExecuteTrade()
        {
            if (currentNPC == null || inventoryService == null || currencySystem == null)
                return;

            // Create a trade offer - for simplicity, we'll offer all items the player has
            // In a real implementation, you'd have a UI to select which items to offer
            var itemsToOffer = new Dictionary<string, int>();

            // Get player's inventory (via reflection)
            var inventoryField = typeof(InventoryService).GetField("quantities", 
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            
            if (inventoryField != null && inventoryField.GetValue(inventoryService) is Dictionary<string, int> inventory)
            {
                // Offer all items (or filter based on NPC preferences)
                foreach (var kvp in inventory)
                {
                    itemsToOffer[kvp.Key] = kvp.Value;
                }
            }

            if (itemsToOffer.Count == 0)
            {
                if (statusLabel != null)
                    statusLabel.text = "You have nothing to trade!";
                return;
            }

            // Create trade offer
            currentOffer = currentNPC.CreateTradeOffer(itemsToOffer);

            if (currentOffer == null)
            {
                if (statusLabel != null)
                    statusLabel.text = "Trade failed!";
                return;
            }

            // Execute the trade
            bool success = currentNPC.ExecuteTrade(currentOffer);

            if (success)
            {
                if (statusLabel != null)
                    statusLabel.text = $"Trade complete! +{currentOffer.totalBitsOffered} Bits";
                
                // Optionally close the panel after successful trade
                // HideTradeUI();
            }
            else
            {
                if (statusLabel != null)
                    statusLabel.text = "Trade execution failed!";
            }
        }
    }
}

