using UnityEngine;
using Velinor.Inventory;
using System.Collections.Generic;

namespace Velinor.Economy
{
    /// <summary>
    /// Defines an NPC's trade preferences.
    /// 
    /// This is NOT about monetary value simulation.
    /// This is about *who values what* in a post-collapse community.
    /// 
    /// Example:
    /// - Willy (scrapper) pays well for electrical/mechanical salvage
    /// - Tala (cook) pays well for food, containers, fuel
    /// - An electrician pays well for copper wire specifically
    /// 
    /// The price difference reflects preference, not currency denomination.
    /// A copper wire has a base value of 4 bits, but Willy gives 6 because
    /// *he personally wants it more*. Someone who doesn't care gives less.
    /// </summary>
    [CreateAssetMenu(menuName = "Velinor/Economy/NPC Trade Profile")]
    public class NPCTradeProfile : ScriptableObject
    {
        [SerializeField] private string npcId;
        [SerializeField] private string npcDisplayName;

        [Header("Preferred Tags & Multipliers")]
        [SerializeField] private List<TagMultiplier> preferredTags = new();

        [Header("Highly Preferred Specific Items")]
        [Tooltip("Specific items this NPC especially values (e.g., copper_wire for Willy)")]
        [SerializeField] private List<SpecificItemValue> highlySoughtItems = new();

        [Header("Disliked Categories")]
        [Tooltip("Categories this NPC doesn't want (empty = accepts all)")]
        [SerializeField] private List<ItemCategory> refusedCategories = new();

        [SerializeField] [Min(0.1f)] private float defaultMultiplier = 1.0f;

        public string NpcId => npcId;
        public string NpcDisplayName => npcDisplayName;

        [System.Serializable]
        public class TagMultiplier
        {
            [SerializeField] public ItemTag tag;
            [SerializeField] [Min(0.1f)] public float multiplier = 1.0f;
        }

        [System.Serializable]
        public class SpecificItemValue
        {
            [SerializeField] public string itemId;
            [SerializeField] [Min(0.1f)] public float multiplier = 1.5f;
        }

        /// <summary>
        /// Calculate what this NPC will pay for an item.
        /// 
        /// This is NOT objective item value. This is what THIS NPC wants.
        /// The same wire might be worth more to Willy than to someone else.
        /// </summary>
        public int CalculateOfferedPrice(ItemDefinition item, int baseValue)
        {
            if (item == null)
            {
                Debug.LogWarning($"NPCTradeProfile.CalculateOfferedPrice: item is null");
                return baseValue;
            }

            // Check if NPC refuses this item's category
            if (refusedCategories.Contains(item.Category))
            {
                return 0; // Won't buy this category
            }

            float multiplier = defaultMultiplier;

            // Check for highly-sought specific item first
            // (This NPC especially wants this particular thing)
            foreach (var specificItem in highlySoughtItems)
            {
                if (specificItem.itemId == item.ItemId)
                {
                    multiplier = specificItem.multiplier;
                    break;
                }
            }

            // If no specific item match, check tags
            // (This NPC generally wants things like this)
            if (multiplier == defaultMultiplier)
            {
                foreach (var tagMult in preferredTags)
                {
                    if (item.HasTag(tagMult.tag))
                    {
                        multiplier = tagMult.multiplier;
                        break;
                    }
                }
            }

            int finalPrice = Mathf.Max(1, Mathf.RoundToInt(baseValue * multiplier));
            return finalPrice;
        }

        /// <summary>
        /// Check if this NPC will accept this item at all.
        /// </summary>
        public bool WillAccept(ItemDefinition item)
        {
            if (item == null)
                return false;

            return !refusedCategories.Contains(item.Category);
        }

        /// <summary>
        /// Get readable explanation of why this price was offered.
        /// Useful for UI tooltips or dialogue context.
        /// </summary>
        public string GetPriceExplanation(ItemDefinition item)
        {
            if (!WillAccept(item))
                return $"{NpcDisplayName} doesn't want this.";

            // Check specific item (highest priority)
            foreach (var specificItem in highlySoughtItems)
            {
                if (specificItem.itemId == item.ItemId)
                {
                    return $"{NpcDisplayName} especially wants this.";
                }
            }

            // Check tags (second priority)
            foreach (var tagMult in preferredTags)
            {
                if (item.HasTag(tagMult.tag))
                {
                    return $"{NpcDisplayName} wants {tagMult.tag} items.";
                }
            }

            // Default (lowest priority)
            return $"{NpcDisplayName} will take this.";
        }
    }
}
