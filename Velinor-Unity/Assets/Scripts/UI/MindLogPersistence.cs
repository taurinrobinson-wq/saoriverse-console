using UnityEngine;

/// <summary>
/// Manages Codex unlock state and protects Mind Log containers during view transitions.
/// ONLY protects containers while they're being viewed. Allows proper disable when switching views.
/// Gets container references from CodexController instead of finding them independently.
/// </summary>
public class MindLogPersistence : MonoBehaviour
{
    private CodexController codexController;
    
    private bool isPrimaryProtected = false;
    private bool isSecondaryProtected = false;
    
    // Codex lock system - determines if Codex is accessible at all
    private static bool isCodexUnlocked = false;

    private void OnEnable()
    {
        // Load persisted state from GameFlags on scene load
        LoadPersistedState();

        // Find CodexController for container references
        if (codexController == null)
            codexController = FindAnyObjectByType<CodexController>();
        
        if (codexController == null)
        {
            Debug.LogError("[MindLogPersistence] CodexController not found in scene! Cannot access container references.");
            return;
        }

        // Containers persist via CodexPanel's DontDestroyOnLoad (managed by CodexController)
        // Do NOT mark them individually here - this causes conflicts with scene persistence
        Debug.Log("[MindLogPersistence] OnEnable: Using CodexPanel's persistence (managed by CodexController)");
    }

    /// <summary>
    /// Loads the persisted Codex state from GameFlags when this scene loads.
    /// This ensures the Codex unlock state carries over between scenes.
    /// Also restores CodexPanel interactivity if Codex was previously unlocked.
    /// </summary>
    private void LoadPersistedState()
    {
        bool codexUnlockedPersistedValue = GameFlags.Get("codex_unlocked", false);
        if (codexUnlockedPersistedValue != isCodexUnlocked)
        {
            isCodexUnlocked = codexUnlockedPersistedValue;
            Debug.Log($"[MindLogPersistence] LoadPersistedState: Restored isCodexUnlocked from GameFlags = {isCodexUnlocked}");
        }

        // If Codex is unlocked, ensure CodexPanel is configured for interaction
        if (isCodexUnlocked)
        {
            GameObject codexPanel = GameObject.Find("UI_Canvas/CodexPanel");
            if (codexPanel != null)
            {
                CanvasGroup cg = codexPanel.GetComponent<CanvasGroup>();
                if (cg != null)
                {
                    // Keep alpha at 0 (hidden) but enable interaction
                    cg.interactable = true;
                    cg.blocksRaycasts = true;
                    Debug.Log("[MindLogPersistence] CodexPanel configured for interaction (persisted from previous scene)");
                }
            }
        }
    }

    private void Update()
    {
        // Ensure CodexController reference is valid
        if (codexController == null)
        {
            codexController = FindAnyObjectByType<CodexController>();
            if (codexController == null)
                return;
        }

        // ONLY protect containers if they're currently being viewed (isPrimaryProtected/isSecondaryProtected is true)
        // This allows them to be disabled when switching views
        if (codexController.mindLogPrimaryContainer != null && isPrimaryProtected)
        {
            if (!codexController.mindLogPrimaryContainer.activeSelf)
            {
                Debug.LogError("[MindLogPersistence] ALERT: MindLogPrimaryContainer was deactivated while protected! Re-activating immediately...");
                codexController.mindLogPrimaryContainer.SetActive(true);
                Debug.LogError($"[MindLogPersistence] Re-activated! Now: activeSelf={codexController.mindLogPrimaryContainer.activeSelf}");
            }
            
            // Also check CanvasGroup visibility
            CanvasGroup cgPrimary = codexController.mindLogPrimaryContainer.GetComponent<CanvasGroup>();
            if (cgPrimary != null && cgPrimary.alpha < 0.5f)
            {
                Debug.LogError($"[MindLogPersistence] ALERT: MindLogPrimaryContainer CanvasGroup alpha={cgPrimary.alpha} (should be 1)! Re-showing...");
                cgPrimary.alpha = 1f;
                cgPrimary.interactable = true;
                cgPrimary.blocksRaycasts = true;
            }
        }
        
        if (codexController.mindLogSecondaryContainer != null && isSecondaryProtected)
        {
            if (!codexController.mindLogSecondaryContainer.activeSelf)
            {
                Debug.LogWarning("[MindLogPersistence] MindLogSecondaryContainer was deactivated while protected! Re-activating...");
                codexController.mindLogSecondaryContainer.SetActive(true);
            }
            
            // Also check CanvasGroup visibility
            CanvasGroup cgSecondary = codexController.mindLogSecondaryContainer.GetComponent<CanvasGroup>();
            if (cgSecondary != null && cgSecondary.alpha < 0.5f)
            {
                Debug.LogWarning($"[MindLogPersistence] ALERT: MindLogSecondaryContainer CanvasGroup alpha={cgSecondary.alpha} (should be 1)! Re-showing...");
                cgSecondary.alpha = 1f;
                cgSecondary.interactable = true;
                cgSecondary.blocksRaycasts = true;
            }
        }
    }

    /// <summary>
    /// Unlocks the Codex to open to Mind Logs view
    /// </summary>
    public static void UnlockCodex()
    {
        var codexController = FindAnyObjectByType<CodexController>();
        if (codexController != null)
        {
            codexController.UnlockCodex();
        }
        else
        {
            Debug.LogWarning("[MindLogPersistence] CodexController not found");
        }
    }
    }

    /// <summary>
    /// Locks the Codex - called at game start to prevent access before trigger.
    /// Also hides the CodexPanel UI.
    /// Persists across scenes via GameFlags.
    /// </summary>
    public static void LockCodex()
    {
        isCodexUnlocked = false;
        GameFlags.Set("codex_unlocked", false);
        Debug.Log("[MindLogPersistence] Codex LOCKED - player cannot access it (persisted to GameFlags)");

        // Hide CodexPanel entirely when locked
        GameObject codexPanel = GameObject.Find("UI_Canvas/CodexPanel");
        if (codexPanel != null)
        {
            CanvasGroup cg = codexPanel.GetComponent<CanvasGroup>();
            if (cg == null)
            {
                cg = codexPanel.AddComponent<CanvasGroup>();
            }

            // Fade out completely and disable interaction
            cg.alpha = 0f;
            cg.interactable = false;
            cg.blocksRaycasts = false;
            Debug.Log("[MindLogPersistence] CodexPanel hidden (alpha=0)");
        }
        else
        {
            Debug.LogWarning("[MindLogPersistence] CodexPanel not found - may not be fully hidden");
        }
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
        
        if (codexController == null)
            codexController = FindAnyObjectByType<CodexController>();
        
        isPrimaryProtected = true;
        if (codexController != null && codexController.mindLogPrimaryContainer != null)
        {
            codexController.mindLogPrimaryContainer.SetActive(true);
            Debug.Log("[MindLogPersistence] Primary container protection ENABLED and activated");
        }
        else
        {
            Debug.LogError("[MindLogPersistence] Cannot protect primary container - CodexController or container reference missing!");
        }
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
        
        if (codexController == null)
            codexController = FindAnyObjectByType<CodexController>();
        
        isSecondaryProtected = true;
        if (codexController != null && codexController.mindLogSecondaryContainer != null)
        {
            codexController.mindLogSecondaryContainer.SetActive(true);
            Debug.Log("[MindLogPersistence] Secondary container protection ENABLED and activated");
        }
        else
        {
            Debug.LogError("[MindLogPersistence] Cannot protect secondary container - CodexController or container reference missing!");
        }
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
