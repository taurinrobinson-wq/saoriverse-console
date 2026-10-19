using UnityEngine;

/// <summary>
/// Replaces SceneStateController.
/// Runs when a scene loads and ensures all NPCs in the scene have their state applied.
/// 
/// This is lightweight: just finds all NPCState components and tells them to sync with GameState.
/// Much simpler than the old per-scene actions system.
/// </summary>
public class SceneStateApplier : MonoBehaviour
{
    [SerializeField] private bool debugMode = false;

    private void Start()
    {
        ApplyAllNPCStates();
    }

    /// <summary>
    /// Find all NPCState components in this scene and apply their state
    /// </summary>
    private void ApplyAllNPCStates()
    {
        if (GameState.Instance == null)
        {
            Debug.LogError("[SceneStateApplier] GameState.Instance not found!");
            return;
        }

        NPCState[] allNPCs = FindObjectsOfType<NPCState>();

        if (debugMode)
        {
            Debug.Log($"[SceneStateApplier] Found {allNPCs.Length} NPCs in scene, applying state...");
        }

        foreach (var npc in allNPCs)
        {
            npc.ApplyState();

            if (debugMode)
            {
                Debug.Log($"[SceneStateApplier] Applied state to {npc.GetNPCID()}");
            }
        }

        if (debugMode)
        {
            Debug.Log($"[SceneStateApplier] State application complete");
        }
    }

    /// <summary>
    /// Public method to manually reapply state (useful for testing or runtime changes)
    /// </summary>
    public void RefreshAllStates()
    {
        ApplyAllNPCStates();
    }
}
