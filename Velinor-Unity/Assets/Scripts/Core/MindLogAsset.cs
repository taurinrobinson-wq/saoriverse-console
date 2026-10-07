using UnityEngine;
using System.Collections.Generic;

namespace Velinor.Core
{
    /// <summary>
    /// Scriptable object asset for a Mind Log entry.
    /// Used in dialogue JSON to reference and load mind logs.
    /// Similar to GlyphData, this is the authoritative asset definition.
    /// </summary>
    [CreateAssetMenu(menuName = "Codex/Mind Log", fileName = "MindLog_NewEntry")]
    public class MindLogAsset : ScriptableObject
    {
        [Header("Identity")]
        public string logID = "memory_unknown";
        public string displayName = "Unnamed Memory";

        [Header("Display")]
        public Sprite icon;
        
        [TextArea(2, 3)]
        public string summaryText = "A memory";

        [Header("Content")]
        [TextArea(5, 10)]
        public string fullText = "Full memory text goes here.";

        [Header("Metadata")]
        public List<string> combineTags = new List<string>();

        /// <summary>
        /// Convert this asset to a MindLogEntry for use in the manager.
        /// </summary>
        public MindLogEntry ToEntry()
        {
            var entry = new MindLogEntry(logID, icon, summaryText, fullText);
            entry.CombineTags = new List<string>(combineTags);
            return entry;
        }

        /// <summary>
        /// Validate that this asset has all required fields.
        /// </summary>
        public bool IsValid()
        {
            return !string.IsNullOrEmpty(logID) 
                && icon != null 
                && !string.IsNullOrEmpty(summaryText)
                && !string.IsNullOrEmpty(fullText);
        }
    }
}
