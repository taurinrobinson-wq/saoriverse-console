using System;
using System.Collections.Generic;
using UnityEngine;

namespace Velinor.Core
{
    /// <summary>
    /// Represents a single mind log entry (memory/diary entry).
    /// This is the authoritative data structure for all mind log UI.
    /// </summary>
    [Serializable]
    public class MindLogEntry
    {
        public string LogID;                    // Unique identifier (e.g., "memory_saori_desert_encounter")
        public Sprite Icon;                     // Grid icon displayed in primary view
        public string SummaryText;              // Short synopsis (2-3 words, shown on single-click)
        public string FullText;                 // Expanded memory text (shown in secondary view)

        public List<string> CombineTags;        // Metadata tags for combination logic
        public string CombinationResultID;      // Optional: ID of resulting combined log

        /// <summary>
        /// Create a new mind log entry.
        /// </summary>
        public MindLogEntry(string logID, Sprite icon, string summaryText, string fullText)
        {
            LogID = logID;
            Icon = icon;
            SummaryText = summaryText;
            FullText = fullText;
            CombineTags = new List<string>();
            CombinationResultID = null;
        }

        /// <summary>
        /// Add a tag that can be used for combination matching.
        /// </summary>
        public void AddCombineTag(string tag)
        {
            if (!CombineTags.Contains(tag))
            {
                CombineTags.Add(tag);
            }
        }

        /// <summary>
        /// Check if this entry has a specific tag.
        /// </summary>
        public bool HasTag(string tag)
        {
            return CombineTags.Contains(tag);
        }
    }
}
