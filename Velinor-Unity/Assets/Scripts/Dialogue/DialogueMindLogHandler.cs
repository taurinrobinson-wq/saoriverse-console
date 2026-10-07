using UnityEngine;
using Velinor.Management;
using Velinor.Core;
using System.Collections.Generic;

namespace Velinor.Dialogue
{
    /// <summary>
    /// Handles Mind Log unlocks triggered by dialogue completion.
    /// Loads Mind Log assets referenced in dialogue JSON and adds them to MindLogManager.
    /// Works similar to how glyphs are collected during dialogue.
    /// </summary>
    public class DialogueMindLogHandler : MonoBehaviour
    {
        /// <summary>
        /// Data structure for Mind Log unlock entries in dialogue JSON.
        /// </summary>
        [System.Serializable]
        public class MindLogUnlock
        {
            public string asset_guid;      // Unity GUID of the asset
            public string asset_path;      // Resources path (e.g., "MindLogs/MindLog_Saori_Desert_Encounter")
        }

        /// <summary>
        /// Process Mind Log unlocks from dialogue beat data.
        /// Call this when a dialogue beat completes.
        /// </summary>
        public static void ProcessMindLogUnlocks(List<MindLogUnlock> unlocks)
        {
            if (unlocks == null || unlocks.Count == 0)
            {
                return;
            }

            if (MindLogManager.Instance == null)
            {
                Debug.LogError("[DialogueMindLogHandler] MindLogManager not found!");
                return;
            }

            foreach (var unlock in unlocks)
            {
                LoadAndAddMindLog(unlock);
            }
        }

        /// <summary>
        /// Load a single Mind Log asset and add it to the manager.
        /// </summary>
        private static void LoadAndAddMindLog(MindLogUnlock unlock)
        {
            if (string.IsNullOrEmpty(unlock.asset_path))
            {
                Debug.LogWarning("[DialogueMindLogHandler] Mind Log asset_path is empty!");
                return;
            }

            // Load the asset from Resources
            var asset = Resources.Load<MindLogAsset>(unlock.asset_path);
            if (asset == null)
            {
                Debug.LogError($"[DialogueMindLogHandler] Failed to load Mind Log asset: {unlock.asset_path}");
                return;
            }

            // Validate the asset
            if (!asset.IsValid())
            {
                Debug.LogError($"[DialogueMindLogHandler] Mind Log asset invalid: {unlock.asset_path}");
                return;
            }

            // Convert to entry and add to manager
            var entry = asset.ToEntry();
            MindLogManager.Instance.AddLog(entry);
            Debug.Log($"[DialogueMindLogHandler] Unlocked Mind Log: {asset.logID} ({asset.displayName})");
        }
    }
}
