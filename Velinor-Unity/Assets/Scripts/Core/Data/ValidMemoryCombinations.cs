using UnityEngine;
using System.Collections.Generic;

namespace Velinor.Core
{
    /// <summary>
    /// Stores metadata about valid memory combinations.
    /// A ScriptableObject list of these defines all possible memory combinations.
    /// </summary>
    [System.Serializable]
    public class MemoryCombinationPair
    {
        public string firstFragmentID;
        public string secondFragmentID;
        public string resultFragmentID;              // The new deduction fragment to create
        
        [TextArea(2, 3)]
        public string combinationLogic;              // Why they combine (for developer reference)

        /// <summary>
        /// Check if this combination matches the given pair (order-independent).
        /// </summary>
        public bool Matches(string id1, string id2)
        {
            return (firstFragmentID == id1 && secondFragmentID == id2)
                || (firstFragmentID == id2 && secondFragmentID == id1);
        }
    }

    /// <summary>
    /// Container for all valid memory combinations in the game.
    /// Create as: Assets/Resources/Data/ValidMemoryCombinations.asset
    /// </summary>
    [CreateAssetMenu(menuName = "Codex/Valid Memory Combinations")]
    public class ValidMemoryCombinations : ScriptableObject
    {
        [SerializeField]
        public List<MemoryCombinationPair> combinations = new List<MemoryCombinationPair>();

        /// <summary>
        /// Find a valid combination for two memory fragments.
        /// Returns null if no combination exists.
        /// </summary>
        public MemoryCombinationPair FindCombination(string fragmentID1, string fragmentID2)
        {
            foreach (var combo in combinations)
            {
                if (combo.Matches(fragmentID1, fragmentID2))
                {
                    return combo;
                }
            }
            return null;
        }

        /// <summary>
        /// Check if two fragments can be combined.
        /// </summary>
        public bool CanCombine(string fragmentID1, string fragmentID2)
        {
            return FindCombination(fragmentID1, fragmentID2) != null;
        }
    }
}
