using UnityEngine;

/// <summary>
/// Debug utility to manually control dialogue completion flags from the Inspector.
/// Allows toggling dialogue state without restarting the game.
/// Remove or disable this script in production builds.
/// </summary>
public class DialogueDebugger : MonoBehaviour
{
    [Header("Conversation Completion Flags")]
    [SerializeField] private bool saoriEncounter01Completed = false;

    private string saoriEncounter01FlagKey = "saori_encounter_01_completed";

    private void OnEnable()
    {
        // Load current flag state into the Inspector display
        RefreshFlagDisplay();
    }

    private void OnValidate()
    {
        // When inspector values change, sync them to GameFlags
        SyncFlagsToGameFlags();
    }

    /// <summary>
    /// Refresh Inspector display to show current GameFlags state
    /// </summary>
    private void RefreshFlagDisplay()
    {
        saoriEncounter01Completed = GameFlags.Get(saoriEncounter01FlagKey, false);
    }

    /// <summary>
    /// Sync all Inspector toggles to GameFlags
    /// </summary>
    private void SyncFlagsToGameFlags()
    {
        GameFlags.Set(saoriEncounter01FlagKey, saoriEncounter01Completed);
        Debug.Log($"[DialogueDebugger] Synced flags to GameFlags. {saoriEncounter01FlagKey} = {saoriEncounter01Completed}");
    }

    /// <summary>
    /// Button method to clear all dialogue completion flags at once
    /// </summary>
    public void ClearAllDialogueFlags()
    {
        saoriEncounter01Completed = false;
        SyncFlagsToGameFlags();
        Debug.Log("[DialogueDebugger] All dialogue completion flags cleared!");
    }
}
