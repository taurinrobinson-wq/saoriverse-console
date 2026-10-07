using UnityEngine;

/// <summary>
/// Manages Codex unlock state and protects Mind Log containers during view transitions.
/// ONLY protects containers while they're being viewed. Allows proper disable when switching views.
/// </summary>
public class MindLogPersistence : MonoBehaviour
{
    [SerializeField] private GameObject mindLogPrimaryContainer;
    [SerializeField] private GameObject mindLogSecondaryContainer;
    
    private bool isPrimaryProtected = false;
    private bool isSecondaryProtected = false;
    
    // Codex lock system - determines if Codex is accessible at all
    private static bool isCodexUnlocked = false;

    private void OnEnable()
    {
        // Find containers if not assigned
        if (mindLogPrimaryContainer == null)
            mindLogPrimaryContainer = GameObject.Find("MindLogPrimaryContainer");
        if (mindLogSecondaryContainer == null)
            mindLogSecondaryContainer = GameObject.Find("MindLogSecondaryContainer");

        // Mark as DontDestroyOnLoad
        if (mindLogPrimaryContainer != null)
            DontDestroyOnLoad(mindLogPrimaryContainer.transform.root.gameObject);
        if (mindLogSecondaryContainer != null)
            DontDestroyOnLoad(mindLogSecondaryContainer.transform.root.gameObject);
    }

    private void Update()
    {
        // Re-find containers if they become null
        if (mindLogPrimaryContainer == null)
            mindLogPrimaryContainer = GameObject.Find("MindLogPrimaryContainer");
        if (mindLogSecondaryContainer == null)
            mindLogSecondaryContainer = GameObject.Find("MindLogSecondaryContainer");

        // ONLY protect containers if they're currently being viewed (isPrimaryProtected/isSecondaryProtected is true)
        // This allows them to be disabled when switching views
        if (mindLogPrimaryContainer != null && isPrimaryProtected)
        {
            if (!mindLogPrimaryContainer.activeSelf)
            {
                Debug.LogWarning("[MindLogPersistence] MindLogPrimaryContainer was deactivated while protected! Re-activating...");
                mindLogPrimaryContainer.SetActive(true);
            }
        }

        if (mindLogSecondaryContainer != null && isSecondaryProtected)
        {
            if (!mindLogSecondaryContainer.activeSelf)
            {
                Debug.LogWarning("[MindLogPersistence] MindLogSecondaryContainer was deactivated while protected! Re-activating...");
                mindLogSecondaryContainer.SetActive(true);
            }
        }
    }

    /// <summary>
    /// Unlocks the Codex - called when player receives it from Saori or other dialogue trigger.
    /// </summary>
    public static void UnlockCodex()
    {
        isCodexUnlocked = true;
        Debug.Log("[MindLogPersistence] Codex UNLOCKED - player can now access it");
    }

    /// <summary>
    /// Locks the Codex - called at game start to prevent access before trigger.
    /// </summary>
    public static void LockCodex()
    {
        isCodexUnlocked = false;
        Debug.Log("[MindLogPersistence] Codex LOCKED - player cannot access it");
    }

    /// <summary>
    /// Checks if Codex is unlocked and accessible.
    /// </summary>
    public static bool IsCodexUnlocked()
    {
        return isCodexUnlocked;
    }

    /// <summary>
    /// Called by CodexViewController to enable protection for the primary container.
    /// This prevents it from being deactivated during view transitions.
    /// </summary>
    public void ProtectPrimaryContainer()
    {
        if (!isCodexUnlocked)
        {
            Debug.LogWarning("[MindLogPersistence] Cannot show Mind Log - Codex is LOCKED!");
            return;
        }
        
        isPrimaryProtected = true;
        if (mindLogPrimaryContainer == null)
            mindLogPrimaryContainer = GameObject.Find("MindLogPrimaryContainer");
        if (mindLogPrimaryContainer != null)
            mindLogPrimaryContainer.SetActive(true);
        Debug.Log("[MindLogPersistence] Primary container protection ENABLED");
    }

    /// <summary>
    /// Called by CodexViewController when switching away from primary view.
    /// Allows the container to be disabled.
    /// </summary>
    public void UnprotectPrimaryContainer()
    {
        isPrimaryProtected = false;
        Debug.Log("[MindLogPersistence] Primary container protection DISABLED - can now be deactivated");
    }

    /// <summary>
    /// Called by CodexViewController to enable protection for the secondary container.
    /// This prevents it from being deactivated during view transitions.
    /// </summary>
    public void ProtectSecondaryContainer()
    {
        if (!isCodexUnlocked)
        {
            Debug.LogWarning("[MindLogPersistence] Cannot show Mind Log - Codex is LOCKED!");
            return;
        }
        
        isSecondaryProtected = true;
        if (mindLogSecondaryContainer == null)
            mindLogSecondaryContainer = GameObject.Find("MindLogSecondaryContainer");
        if (mindLogSecondaryContainer != null)
            mindLogSecondaryContainer.SetActive(true);
        Debug.Log("[MindLogPersistence] Secondary container protection ENABLED");
    }

    /// <summary>
    /// Called by CodexViewController when switching away from secondary view.
    /// Allows the container to be disabled.
    /// </summary>
    public void UnprotectSecondaryContainer()
    {
        isSecondaryProtected = false;
        Debug.Log("[MindLogPersistence] Secondary container protection DISABLED - can now be deactivated");
    }
}
