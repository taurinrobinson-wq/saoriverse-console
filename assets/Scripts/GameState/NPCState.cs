using UnityEngine;

/// <summary>
/// Attach this component to every NPC GameObject.
/// On scene load, it checks GameState and applies visibility accordingly.
/// 
/// This replaces the need for per-scene state controllers.
/// One component per NPC, always syncs with global GameState.
/// </summary>
public class NPCState : MonoBehaviour
{
    [SerializeField] private string npcID = ""; // Must match exactly (e.g., "Ravi", "Nima", "Kaelen")

    [SerializeField] private bool debugMode = false; // Set to true to see detailed logs

    private void OnEnable()
    {
        // When this GameObject becomes active in the scene, apply state
        ApplyState();
    }

    private void Start()
    {
        // Also apply on Start in case GameState wasn't ready during OnEnable
        ApplyState();
    }

    /// <summary>
    /// Check GameState and apply visibility accordingly
    /// </summary>
    public void ApplyState()
    {
        if (GameState.Instance == null)
        {
            if (debugMode)
                Debug.LogWarning($"[NPCState] GameState.Instance is null for {npcID}, skipping state application");
            return;
        }

        bool shouldBeVisible = GameState.Instance.GetNPCVisibility(npcID);

        // Apply the visibility state
        gameObject.SetActive(shouldBeVisible);

        if (debugMode)
        {
            Debug.Log($"[NPCState] {npcID}: Applied state -> {(shouldBeVisible ? "VISIBLE" : "HIDDEN")}");
        }
    }

    /// <summary>
    /// Manually update this NPC's state (called by other systems)
    /// </summary>
    public void SetVisibility(bool isVisible)
    {
        GameState.Instance.SetNPCVisibility(npcID, isVisible);
        ApplyState();
    }

    public string GetNPCID()
    {
        return npcID;
    }
}
