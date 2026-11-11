using UnityEngine;
using Velinor.Core;

/// <summary>
/// GlyphDepthAdjuster: Manages Z-position of glyphs during scene transitions.
/// 
/// Problem: When glyphs are behind the player (z=1), they're not interactable.
/// When they're at player z (z=0), they clip through debris.
/// 
/// Solution: Update glyph z-position to match player during transitions,
/// then back to background position when interaction is complete.
/// 
/// Usage: Attach to the GlyphPickup object you want to adjust.
/// Configure the target Z positions in the Inspector.
/// </summary>
public class GlyphDepthAdjuster : MonoBehaviour
{
    [Header("Position Configuration")]
    [SerializeField] private float backgroundDepth = 1f;      // Z position when glyph should be behind player
    [SerializeField] private float interactionDepth = 0f;     // Z position when player can interact with it
    
    [Header("References")]
    [SerializeField] private Transform playerTransform;       // Auto-find if not assigned
    [SerializeField] private GlyphPickup glyphPickup;        // The glyph this adjusts
    
    [Header("Timing")]
    [SerializeField] private bool adjustZDuringTransition = true;  // Enable/disable this feature
    [SerializeField] private float delayAfterFadeIn = 0.3f;   // Delay after fade-in before updating Z
    
    private bool hasBeenAdjustedToInteraction = false;
    private bool isCurrentlyInteractable = false;

    private void Start()
    {
        // Auto-find player if not assigned
        if (playerTransform == null)
        {
            GameObject playerObj = GameObject.FindGameObjectWithTag("Player");
            if (playerObj != null)
            {
                playerTransform = playerObj.transform;
            }
            else
            {
                Debug.LogWarning($"[GlyphDepthAdjuster] Player not found for {gameObject.name}");
            }
        }

        // Auto-find GlyphPickup if not assigned
        if (glyphPickup == null)
        {
            glyphPickup = GetComponent<GlyphPickup>();
            if (glyphPickup == null)
            {
                Debug.LogWarning($"[GlyphDepthAdjuster] GlyphPickup not found on {gameObject.name}");
            }
        }

        // Start with glyph at background depth
        if (adjustZDuringTransition)
        {
            SetDepth(backgroundDepth);
            Debug.Log($"[GlyphDepthAdjuster] {gameObject.name} initialized at depth={backgroundDepth}");
        }
    }

    /// <summary>
    /// Call this when the debris fade transition starts (screen goes black)
    /// The glyph is hidden during the fade, so we can safely adjust position
    /// </summary>
    public void OnTransitionStart()
    {
        if (!adjustZDuringTransition) return;
        
        Debug.Log($"[GlyphDepthAdjuster] {gameObject.name}: Transition started");
        // At this point, screen is black - we can adjust position unseen
    }

    /// <summary>
    /// Call this when the debris fade transition completes (screen fades back in)
    /// This is when the glyph's sphere collider is enabled and needs to be interactable
    /// </summary>
    public void OnTransitionComplete()
    {
        if (!adjustZDuringTransition) return;
        
        // Wait for fade to finish, then update position to be interactable
        StartCoroutine(AdjustZAfterDelay());
    }

    private System.Collections.IEnumerator AdjustZAfterDelay()
    {
        // Wait for fade-in animation to complete
        yield return new WaitForSeconds(delayAfterFadeIn);
        
        // Now update Z to match player's Z position so glyph is interactable
        SetDepth(interactionDepth);
        isCurrentlyInteractable = true;
        hasBeenAdjustedToInteraction = true;
        
        Debug.Log($"[GlyphDepthAdjuster] {gameObject.name}: Adjusted to interaction depth={interactionDepth}");
    }

    /// <summary>
    /// Set the Z position of this glyph
    /// </summary>
    private void SetDepth(float zValue)
    {
        Vector3 pos = transform.position;
        pos.z = zValue;
        transform.position = pos;
    }

    /// <summary>
    /// Get current depth
    /// </summary>
    public float GetCurrentDepth()
    {
        return transform.position.z;
    }

    /// <summary>
    /// Check if glyph is currently at interaction depth
    /// </summary>
    public bool IsAtInteractionDepth()
    {
        return isCurrentlyInteractable && hasBeenAdjustedToInteraction;
    }

    #region Public API for Scene Events

    /// <summary>
    /// Public method: Reposition glyph to background (when hidden/collected)
    /// </summary>
    public void MoveToBackground()
    {
        SetDepth(backgroundDepth);
        isCurrentlyInteractable = false;
        Debug.Log($"[GlyphDepthAdjuster] {gameObject.name}: Moved to background depth={backgroundDepth}");
    }

    /// <summary>
    /// Public method: Reposition glyph to interaction layer
    /// </summary>
    public void MoveToInteraction()
    {
        SetDepth(interactionDepth);
        isCurrentlyInteractable = true;
        Debug.Log($"[GlyphDepthAdjuster] {gameObject.name}: Moved to interaction depth={interactionDepth}");
    }

    #endregion
}
