using System.Collections.Generic;
using UnityEngine;
using Velinor.Core;

namespace Velinor.Management
{
    /// <summary>
    /// Central manager for all mind log entries.
    /// All UI reads from this manager — it is the single source of truth.
    /// </summary>
    public class MindLogManager : MonoBehaviour
    {
        public static MindLogManager Instance { get; private set; }

        private Dictionary<string, MindLogEntry> logs = new();

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }

            Instance = this;
            DontDestroyOnLoad(gameObject);
            Debug.Log("[MindLogManager] Initialized as singleton.");
        }

        private void OnEnable()
        {
            // Ensure singleton is set even if this object is enabled after another instance
            if (Instance == null)
            {
                Instance = this;
            }
        }

        /// <summary>
        /// Get or create the MindLogManager singleton.
        /// </summary>
        public static MindLogManager GetOrCreate()
        {
            if (Instance == null)
            {
                GameObject obj = new GameObject("MindLogManager");
                Instance = obj.AddComponent<MindLogManager>();
                DontDestroyOnLoad(obj);
                Debug.Log("[MindLogManager] Auto-created singleton instance.");
            }
            return Instance;
        }

        /// <summary>
        /// Add or update a log entry.
        /// </summary>
        public void AddLog(MindLogEntry entry)
        {
            if (entry == null)
            {
                Debug.LogError("[MindLogManager] Cannot add null entry!");
                return;
            }

            logs[entry.LogID] = entry;
            Debug.Log($"[MindLogManager] Added/updated log: {entry.LogID}");
        }

        /// <summary>
        /// Retrieve a log by ID.
        /// </summary>
        public MindLogEntry GetLog(string logID)
        {
            if (logs.TryGetValue(logID, out var entry))
            {
                return entry;
            }

            Debug.LogWarning($"[MindLogManager] Log not found: {logID}");
            return null;
        }

        /// <summary>
        /// Get all current logs.
        /// </summary>
        public IEnumerable<MindLogEntry> GetAllLogs()
        {
            return logs.Values;
        }

        /// <summary>
        /// Get the count of all logs.
        /// </summary>
        public int GetLogCount()
        {
            return logs.Count;
        }

        /// <summary>
        /// Check if a log exists.
        /// </summary>
        public bool HasLog(string logID)
        {
            return logs.ContainsKey(logID);
        }

        /// <summary>
        /// Check if two logs can be combined (share at least one tag).
        /// </summary>
        public bool CanCombine(string logIDA, string logIDB)
        {
            var logA = GetLog(logIDA);
            var logB = GetLog(logIDB);

            if (logA == null || logB == null)
            {
                return false;
            }

            // Logs can combine if they share at least one tag
            foreach (string tag in logA.CombineTags)
            {
                if (logB.HasTag(tag))
                {
                    return true;
                }
            }

            return false;
        }

        /// <summary>
        /// Combine two logs and return the resulting entry.
        /// Returns null if combination is not possible.
        /// </summary>
        public MindLogEntry CombineLogs(string logIDA, string logIDB)
        {
            var logA = GetLog(logIDA);
            var logB = GetLog(logIDB);

            if (!CanCombine(logIDA, logIDB))
            {
                Debug.LogWarning($"[MindLogManager] Cannot combine {logIDA} and {logIDB} — no shared tags.");
                return null;
            }

            // Use the result ID from whichever log has one
            string resultID = logA.CombinationResultID ?? logB.CombinationResultID;

            if (string.IsNullOrEmpty(resultID))
            {
                Debug.LogWarning($"[MindLogManager] No combination result ID defined for {logIDA} + {logIDB}.");
                return null;
            }

            var result = GetLog(resultID);
            if (result == null)
            {
                Debug.LogError($"[MindLogManager] Combination result log not found: {resultID}");
            }

            Debug.Log($"[MindLogManager] Combined {logIDA} + {logIDB} → {resultID}");
            return result;
        }

        /// <summary>
        /// Remove a log by ID.
        /// </summary>
        public void RemoveLog(string logID)
        {
            if (logs.Remove(logID))
            {
                Debug.Log($"[MindLogManager] Removed log: {logID}");
            }
        }

        /// <summary>
        /// Clear all logs.
        /// </summary>
        public void ClearAllLogs()
        {
            logs.Clear();
            Debug.Log("[MindLogManager] Cleared all logs.");
        }
    }
}
