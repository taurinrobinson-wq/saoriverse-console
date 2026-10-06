using UnityEngine;
using Velinor.Core;
using Velinor.Management;
using System.Collections.Generic;

namespace Velinor.Testing
{
    /// <summary>
    /// Initializes the MindLogManager with real memory data from MemoryFragment assets.
    /// This bridges the existing MemoryFragment system with the new MindLogManager.
    /// </summary>
    public class MindLogInitializer : MonoBehaviour
    {
        [SerializeField] private List<MemoryFragment> memoryFragments = new List<MemoryFragment>();
        [SerializeField] private bool autoInitializeOnStart = true;

        private void Start()
        {
            if (autoInitializeOnStart)
            {
                InitializeFromFragments();
            }
        }

        /// <summary>
        /// Load all assigned MemoryFragments into the MindLogManager.
        /// </summary>
        public void InitializeFromFragments()
        {
            if (MindLogManager.Instance == null)
            {
                Debug.LogError("[MindLogInitializer] MindLogManager instance not found!");
                return;
            }

            if (memoryFragments.Count == 0)
            {
                Debug.LogWarning("[MindLogInitializer] No memory fragments assigned!");
                return;
            }

            MindLogManager.Instance.ClearAllLogs();

            foreach (var fragment in memoryFragments)
            {
                if (fragment == null)
                {
                    Debug.LogWarning("[MindLogInitializer] Null fragment in list!");
                    continue;
                }

                if (!fragment.IsValid())
                {
                    Debug.LogWarning($"[MindLogInitializer] Invalid fragment: {fragment.name}");
                    continue;
                }

                // Convert MemoryFragment to MindLogEntry
                var entry = new MindLogEntry(
                    fragment.fragmentID,
                    fragment.icon,
                    fragment.shortSynopsis,
                    fragment.expandedText
                );

                // Add tags from fragment
                foreach (var tag in fragment.tags)
                {
                    entry.AddCombineTag(tag);
                }

                // Add combination result if defined
                if (fragment.combinesWith.Count > 0)
                {
                    // For now, store the first combinable fragment as the result
                    // In a real system, you'd define this in the MemoryFragment itself
                    entry.CombinationResultID = fragment.combinesWith.Count > 0 ? fragment.combinesWith[0] : null;
                }

                MindLogManager.Instance.AddLog(entry);
                Debug.Log($"[MindLogInitializer] Added memory: {fragment.fragmentID}");
            }

            Debug.Log($"[MindLogInitializer] Initialized {memoryFragments.Count} memories from fragments.");
        }

        /// <summary>
        /// Add a single fragment to the manager.
        /// </summary>
        public void AddFragment(MemoryFragment fragment)
        {
            if (fragment == null || !fragment.IsValid())
            {
                Debug.LogWarning("[MindLogInitializer] Cannot add invalid fragment!");
                return;
            }

            if (MindLogManager.Instance == null)
            {
                Debug.LogError("[MindLogInitializer] MindLogManager instance not found!");
                return;
            }

            var entry = new MindLogEntry(
                fragment.fragmentID,
                fragment.icon,
                fragment.shortSynopsis,
                fragment.expandedText
            );

            foreach (var tag in fragment.tags)
            {
                entry.AddCombineTag(tag);
            }

            MindLogManager.Instance.AddLog(entry);
            Debug.Log($"[MindLogInitializer] Added memory: {fragment.fragmentID}");
        }

        /// <summary>
        /// Remove a fragment from the manager by ID.
        /// </summary>
        public void RemoveFragment(string fragmentID)
        {
            if (MindLogManager.Instance == null)
            {
                Debug.LogError("[MindLogInitializer] MindLogManager instance not found!");
                return;
            }

            MindLogManager.Instance.RemoveLog(fragmentID);
            Debug.Log($"[MindLogInitializer] Removed memory: {fragmentID}");
        }
    }
}
