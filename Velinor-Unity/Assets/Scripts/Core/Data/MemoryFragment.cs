using UnityEngine;
using System.Collections.Generic;

namespace Velinor.Core
{
    /// <summary>
    /// Represents a single memory fragment in the Codex Mind Log system.
    /// Used for both raw memories and combined deductions.
    /// </summary>
    [CreateAssetMenu(menuName = "Codex/Memory Fragment")]
    public class MemoryFragment : ScriptableObject
    {
        [Header("Identity")]
        public string fragmentID;                    // Unique identifier (e.g., "memory_ravi_daughter")
        public string displayName;                   // Display name in UI

        [Header("Display")]
        public Sprite icon;                          // Grid icon (256x256 recommended)
        public string shortSynopsis;                 // 2-3 word summary shown on single-click
        
        [Header("Content")]
        [TextArea(3, 5)]
        public string expandedText;                  // Full memory description shown when double-clicked

        [Header("Metadata")]
        public List<string> tags = new List<string>();  // For combination logic
        public bool isDeduction = false;             // True if this is a combined fragment
        
        [Header("Combination")]
        public List<string> combinesWith = new List<string>();  // Valid partner IDs
        
        [Header("Source")]
        public string linkedScene;                   // Which scene triggered this memory
        public float unlockCondition = 0f;           // Gate/flag requirement (0 = always available)

        /// <summary>
        /// Validates that this fragment has all required fields filled.
        /// </summary>
        public bool IsValid()
        {
            return !string.IsNullOrEmpty(fragmentID) 
                && icon != null 
                && !string.IsNullOrEmpty(shortSynopsis)
                && !string.IsNullOrEmpty(expandedText);
        }

        /// <summary>
        /// Check if this fragment can combine with another.
        /// </summary>
        public bool CanCombineWith(string otherFragmentID)
        {
            return combinesWith.Contains(otherFragmentID);
        }
    }
}
