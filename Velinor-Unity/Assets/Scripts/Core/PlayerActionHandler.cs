using UnityEngine;

/// <summary>
/// Handles player actions triggered from dialogue (e.g., posture changes, movement, animations).
/// Called by DialogueManager when processing player choices with result_text.
/// </summary>
public class PlayerActionHandler : MonoBehaviour
{
    public static PlayerActionHandler Instance { get; private set; }

    private PlayerController2D5 playerController;
    private Animator playerAnimator;

    private void Awake()
    {
        if (Instance != null && Instance != this) { Destroy(gameObject); return; }
        Instance = this;

        playerController = FindAnyObjectByType<PlayerController2D5>();
        if (playerController != null)
        {
            playerAnimator = playerController.GetComponent<Animator>();
        }
    }

    /// <summary>
    /// Execute a player action based on dialogue choice result_text.
    /// Examples:
    /// - "You approach with open body language..." → Approach animation
    /// - "You maintain space, watching carefully..." → Stay posture
    /// - "You stop completely..." → Freeze animation
    /// - "You wander the marketplace..." → Wander animation
    /// </summary>
    public void ExecutePlayerAction(string actionDescription)
    {
        if (string.IsNullOrEmpty(actionDescription)) return;

        Debug.Log($"[PlayerActionHandler] Executing action: {actionDescription}");

        string lowerAction = actionDescription.ToLower();

        // Posture/approach actions
        if (lowerAction.Contains("approach") || lowerAction.Contains("step toward"))
        {
            PlayPlayerAnimation("Approach");
        }
        else if (lowerAction.Contains("distance") || lowerAction.Contains("maintain space") || lowerAction.Contains("keep"))
        {
            PlayPlayerAnimation("StayBack");
        }
        else if (lowerAction.Contains("freeze") || lowerAction.Contains("stop completely"))
        {
            PlayPlayerAnimation("Freeze");
        }
        else if (lowerAction.Contains("wander") || lowerAction.Contains("explore"))
        {
            PlayPlayerAnimation("Wander");
        }
        else if (lowerAction.Contains("circle") || lowerAction.Contains("avoiding"))
        {
            PlayPlayerAnimation("Circle");
        }
        else if (lowerAction.Contains("silent") || lowerAction.Contains("stillness"))
        {
            PlayPlayerAnimation("Observe");
        }
        else
        {
            // Default: play Idle for unknown actions
            PlayPlayerAnimation("Idle");
        }
    }

    /// <summary>
    /// Trigger a player animation by name.
    /// </summary>
    private void PlayPlayerAnimation(string triggerName)
    {
        if (playerAnimator == null)
        {
            Debug.LogWarning("[PlayerActionHandler] Player animator not found");
            return;
        }

        // Set a trigger or bool parameter depending on animation setup
        try
        {
            playerAnimator.SetTrigger(triggerName);
            Debug.Log($"[PlayerActionHandler] Triggered animation: {triggerName}");
        }
        catch
        {
            Debug.LogWarning($"[PlayerActionHandler] Animation trigger '{triggerName}' not found or invalid");
        }
    }

    /// <summary>
    /// Simple posture change without full animation (useful for quick stance changes).
    /// </summary>
    public void SetPlayerPosture(string postureName)
    {
        if (playerAnimator == null) return;

        try
        {
            // Set a bool parameter for sustained postures
            playerAnimator.SetBool(postureName, true);
            Debug.Log($"[PlayerActionHandler] Set posture: {postureName}");
        }
        catch
        {
            Debug.LogWarning($"[PlayerActionHandler] Posture '{postureName}' not found");
        }
    }

    /// <summary>
    /// Clear player postures (reset to idle).
    /// </summary>
    public void ClearPlayerPosture()
    {
        if (playerAnimator == null) return;

        try
        {
            // Reset common posture parameters
            playerAnimator.SetBool("Approach", false);
            playerAnimator.SetBool("StayBack", false);
            playerAnimator.SetBool("Freeze", false);
            Debug.Log("[PlayerActionHandler] Cleared player postures");
        }
        catch { }
    }
}
