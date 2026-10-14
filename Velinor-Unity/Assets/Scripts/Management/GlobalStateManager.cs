using UnityEngine;

namespace Velinor.Management
{
    /// <summary>
    /// Global state persistence across all scenes.
    /// 
    /// Ensures that:
    /// - GameFlags (dialogue completion, NPC state, etc.) survive scene transitions
    /// - NPCs can be shown/hidden based on dialogue tags and flags
    /// - All global singletons (MindLogManager, StatManager, etc.) are kept alive
    /// 
    /// Usage:
    /// 1. Automatically initializes on first scene load
    /// 2. Set flags via GameFlags.Set("key", true) during dialogue system triggers
    /// 3. Use SceneStateController to check flags and show/hide NPCs when scene loads
    /// </summary>
    public class GlobalStateManager : MonoBehaviour
    {
        public static GlobalStateManager Instance { get; private set; }

        private void Awake()
        {
            // Enforce singleton pattern
            if (Instance != null && Instance != this)
            {
                Debug.LogWarning("[GlobalStateManager] Duplicate instance detected. Destroying this one.");
                Destroy(gameObject);
                return;
            }

            // First initialization
            Instance = this;
            DontDestroyOnLoad(gameObject);
            Debug.Log("[GlobalStateManager] Initialized as persistent singleton. This object will survive scene changes.");
        }

        /// <summary>
        /// Get or create the GlobalStateManager singleton.
        /// Automatically called on first scene load if not already present.
        /// </summary>
        public static GlobalStateManager GetOrCreate()
        {
            if (Instance == null)
            {
                Debug.Log("[GlobalStateManager] Creating new persistent state manager...");
                GameObject obj = new GameObject("GlobalStateManager");
                Instance = obj.AddComponent<GlobalStateManager>();
                DontDestroyOnLoad(obj);
                Debug.Log("[GlobalStateManager] Auto-created singleton instance.");
            }

            return Instance;
        }

        /// <summary>
        /// Debug: Print all active game flags
        /// </summary>
        public void DebugPrintFlags()
        {
            Debug.Log("[GlobalStateManager] Active flags:");
            int count = 0;
            foreach (var flag in GameFlags.GetAllFlags())
            {
                Debug.Log($"  {flag.Key} = {flag.Value}");
                count++;
            }
            Debug.Log($"[GlobalStateManager] Total flags: {count}");
        }

        /// <summary>
        /// Reset all game state (useful for testing or new game)
        /// </summary>
        public void ResetAllState()
        {
            GameFlags.Clear();
            Debug.Log("[GlobalStateManager] All game state reset.");
        }
    }
}
