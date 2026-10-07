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
        // Find CodexController for container references
        if (codexController == null)
            codexController = FindObjectOfType<CodexController>();
        
        if (codexController == null)
        {
            Debug.LogError("[MindLogPersistence] CodexController not found in scene! Cannot access container references.");
            return;
        }

        // Mark containers as DontDestroyOnLoad if they exist
        if (codexController.mindLogPrimaryContainer != null)
            DontDestroyOnLoad(codexController.mindLogPrimaryContainer.transform.root.gameObject);
        if (codexController.mindLogSecondaryContainer != null)
            DontDestroyOnLoad(codexController.mindLogSecondaryContainer.transform.root.gameObject);
        if (codexController.glyphsBackground != null)
            DontDestroyOnLoad(codexController.glyphsBackground.transform.root.gameObject);
    }

    private void Update()
    {
        // Ensure CodexController reference is valid
        if (codexController == null)
        {
            codexController = FindObjectOfType<CodexController>();
            if (codexController == null)
                return;
        }

        // ONLY protect containers if they're currently being viewed (isPrimaryProtected/isSecondaryProtected is true)
        // This allows them to be disabled when switching views
        if (codexController.mindLogPrimaryContainer != null && isPrimaryProtected)
        {
            if (!codexController.mindLogPrimaryContainer.activeSelf)
            {
                Debug.LogWarning("[MindLogPersistence] MindLogPrimaryContainer was deactivated while protected! Re-activating...");
                codexController.mindLogPrimaryContainer.SetActive(true);
            }
        }

        if (codexController.mindLogSecondaryContainer != null && isSecondaryProtected)
        {
            if (!codexController.mindLogSecondaryContainer.activeSelf)
            {
                Debug.LogWarning("[MindLogPersistence] MindLogSecondaryContainer was deactivated while protected! Re-activating...");
                codexController.mindLogSecondaryContainer.SetActive(true);
            }
        }
    }

    /// <summary>
    /// Unlocks the Codex - called when player receives it from Saori or other dialogue trigger.
    /// Enables the CodexPanel UI and CodexViewController button access, but does NOT auto-show it.
    /// User must press C to open it. Alpha stays at 0 so ToggleCodex() can properly detect it's closed.
    /// </summary>
    public static void UnlockCodex()
    {
        isCodexUnlocked = true;
        Debug.Log("[MindLogPersistence] Codex UNLOCKED - player can now press C to access it");

        // Try to find and unlock CodexController
        var codexController = FindObjectOfType<CodexController>();
        if (codexController != null)
        {
            codexController.UnlockCodex();
            Debug.Log("[MindLogPersistence] ✓ CodexController found and unlocked");
        }
        else
        {
            Debug.LogError("[MindLogPersistence] ✗ CodexController not found via FindObjectOfType! Trying fallback...");
            
            // Fallback: Try to find CodexPanel and get controller from it
            GameObject codexPanel = GameObject.Find("UI_Canvas/CodexPanel");
            if (codexPanel != null)
            {
                CodexController controller = codexPanel.GetComponent<CodexController>();
                if (controller != null)
                {
                    controller.UnlockCodex();
                    Debug.Log("[MindLogPersistence] ✓ CodexController found on CodexPanel and unlocked!");
                }
                else
                {
                    Debug.LogError("[MindLogPersistence] ✗ CodexPanel has no CodexController component!");
                }
            }
            else
            {
                Debug.LogError("[MindLogPersistence] ✗ CodexPanel not found at UI_Canvas/CodexPanel!");
            }
        }

        // Enable CodexPanel interactivity but KEEP alpha at 0
        // ToggleCodex() uses (alpha < 0.5f) to detect if Codex is closed
        // If we set alpha=1, it will think Codex is open and try to close it on first C press!
        GameObject codexPanel2 = GameObject.Find("UI_Canvas/CodexPanel");
        if (codexPanel2 != null)
        {
            CanvasGroup cg = codexPanel2.GetComponent<CanvasGroup>();
            if (cg != null)
            {
                // Keep alpha at 0 (hidden) but enable interaction
                cg.interactable = true;
                cg.blocksRaycasts = true;
                Debug.Log("[MindLogPersistence] CodexPanel unlocked (alpha stays 0, will open on first C press)");
            }
        }
    }

    /// <summary>
    /// Locks the Codex - called at game start to prevent access before trigger.
    /// Also hides the CodexPanel UI.
    /// </summary>
    public static void LockCodex()
    {
        isCodexUnlocked = false;
        Debug.Log("[MindLogPersistence] Codex LOCKED - player cannot access it");

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
            codexController = FindObjectOfType<CodexController>();
        
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
            codexController = FindObjectOfType<CodexController>();
        
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
