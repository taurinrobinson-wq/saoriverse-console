using UnityEngine;
using Velinor.Core;
using Velinor.Inventory;
using Velinor.Economy;
using System;
using System.Collections.Generic;

namespace Velinor.Interactions
{
    /// <summary>
    /// Handles trading interaction with NPCs.
    /// Allows player to give items in exchange for Bits.
    /// </summary>
    public class NPCTrader : MonoBehaviour, IInteractable
    {
        [SerializeField] private string npcId;
        [SerializeField] private NPCTradeProfile tradeProfile;

        public event Action<NPCTradeOffer> OnTradeOfferCreated;
        public event Action<NPCTradeOffer> OnTradeAccepted;
        public event Action OnTradeCancelled;

        public string NpcId => npcId;
        public NPCTradeProfile TradeProfile => tradeProfile;

        private void OnValidate()
        {
            if (tradeProfile != null && string.IsNullOrEmpty(npcId))
            {
                npcId = tradeProfile.NpcId;
            }
        }

        public void Interact(GameObject player)
        {
            Debug.Log($"NPC {npcId} ({tradeProfile?.NpcDisplayName}) ready to trade");
            // This would trigger a dialogue or UI panel
            // For now, just log that interaction is possible
        }

        /// <summary>
        /// Generate a trade offer based on items player wants to give.
        /// </summary>
        public NPCTradeOffer CreateTradeOffer(Dictionary<string, int> itemsOffered)
        {
            if (tradeProfile == null)
            {
                Debug.LogError($"NPCTrader {npcId} has no trade profile assigned");
                return null;
            }

            var inventory = InventoryService.Instance;
            if (inventory == null)
            {
                Debug.LogError("InventoryService.Instance is null");
                return null;
            }

            var itemDb = inventory.ItemDatabase;
            if (itemDb == null)
            {
                Debug.LogError("ItemDatabase is null");
                return null;
            }

            var offer = new NPCTradeOffer();
            offer.npcId = npcId;
            offer.npcDisplayName = tradeProfile.NpcDisplayName;
            offer.offeredItems = new Dictionary<string, int>(itemsOffered);

            int totalBitsOffered = 0;

            foreach (var kvp in itemsOffered)
            {
                var itemDef = itemDb.Get(kvp.Key);
                if (itemDef == null)
                {
                    Debug.LogWarning($"Unknown item: {kvp.Key}");
                    continue;
                }

                int quantity = kvp.Value;
                int baseValue = itemDef.BaseValue;
                int pricePerUnit = tradeProfile.CalculateOfferedPrice(itemDef, baseValue);
                int totalPrice = pricePerUnit * quantity;

                offer.itemPrices[kvp.Key] = pricePerUnit;
                totalBitsOffered += totalPrice;
            }

            offer.totalBitsOffered = totalBitsOffered;

            OnTradeOfferCreated?.Invoke(offer);
            return offer;
        }

        /// <summary>
        /// Execute a trade agreement.
        /// </summary>
        public bool ExecuteTrade(NPCTradeOffer offer)
        {
            if (offer == null || offer.npcId != npcId)
            {
                Debug.LogError("Invalid trade offer");
                return false;
            }

            var inventory = InventoryService.Instance;
            var currency = CurrencySystem.Instance;

            if (inventory == null || currency == null)
            {
                Debug.LogError("InventoryService or CurrencySystem not initialized");
                return false;
            }

            // Verify player still has all items
            foreach (var kvp in offer.offeredItems)
            {
                if (!inventory.Contains(kvp.Key, kvp.Value))
                {
                    Debug.LogWarning($"Player no longer has {kvp.Value}x {kvp.Key}");
                    return false;
                }
            }

            // Remove items from inventory
            foreach (var kvp in offer.offeredItems)
            {
                if (!inventory.Remove(kvp.Key, kvp.Value))
                {
                    Debug.LogError($"Failed to remove {kvp.Key} from inventory during trade");
                    return false;
                }
            }

            // Award Bits
            currency.Earn(offer.totalBitsOffered, $"Traded with {offer.npcDisplayName}");

            OnTradeAccepted?.Invoke(offer);
            Debug.Log($"Trade completed with {offer.npcDisplayName}: gave items for {offer.totalBitsOffered} bits");

            return true;
        }

        /// <summary>
        /// Cancel an offer without executing.
        /// </summary>
        public void CancelTrade()
        {
            OnTradeCancelled?.Invoke();
        }
    }

    /// <summary>
    /// Data structure for a trade offer.
    /// </summary>
    public class NPCTradeOffer
    {
        public string npcId;
        public string npcDisplayName;
        public Dictionary<string, int> offeredItems = new(); // itemId -> quantity
        public Dictionary<string, int> itemPrices = new(); // itemId -> bits per unit
        public int totalBitsOffered;

        public override string ToString()
        {
            string itemsList = "";
            foreach (var kvp in offeredItems)
            {
                itemsList += $"\n  {kvp.Key} x{kvp.Value}";
            }
            return $"Trade Offer from {npcDisplayName}:{itemsList}\n Total: {totalBitsOffered} bits";
        }
    }
}
