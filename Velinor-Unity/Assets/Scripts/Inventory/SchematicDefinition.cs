using UnityEngine;
using System.Collections.Generic;

namespace Velinor.Inventory
{
    [CreateAssetMenu(menuName = "Velinor/Inventory/Schematic Definition")]
    public class SchematicDefinition : ScriptableObject
    {
        [SerializeField] private ItemDefinition schematicItem;
        [SerializeField] private List<Ingredient> ingredients;
        [SerializeField] private ItemDefinition resultItem;
        [SerializeField] private int resultQuantity = 1;

        public ItemDefinition SchematicItem => schematicItem;
        public IReadOnlyList<Ingredient> Ingredients => ingredients;
        public ItemDefinition ResultItem => resultItem;
        public int ResultQuantity => resultQuantity;

        [System.Serializable]
        public class Ingredient
        {
            public ItemDefinition item;
            public int quantity = 1;
        }

        public bool CanAssemble(Dictionary<string, int> availableMaterials)
        {
            foreach (var ingredient in ingredients)
            {
                if (!availableMaterials.TryGetValue(ingredient.item.ItemId, out int qty) || qty < ingredient.quantity)
                    return false;
            }
            return true;
        }
    }
}
