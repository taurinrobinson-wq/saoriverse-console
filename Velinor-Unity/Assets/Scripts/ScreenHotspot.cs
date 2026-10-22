using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

/// <summary>
/// Clickable hotspot on screen image for interactive comic-strip sequences
/// 
/// Features:
/// - Click detection via pointer events
/// - Triggers animations and Mind Log events
/// - One-time or repeatable clicks (configurable)
/// - Visual feedback (highlighting on hover)
/// - Click sound effects
/// </summary>
public class ScreenHotspot : MonoBehaviour, IPointerClickHandler, IPointerEnterHandler, IPointerExitHandler
{
    [Header("Hotspot Configuration")]
    [SerializeField] private string hotspotID;
    [SerializeField] private bool oneTimeOnly = true;
    
    [Header("Visual Feedback")]
    [SerializeField] private Graphic highlightGraphic;  // Shows on hover (Image, RawImage, or Text)
    [SerializeField] private Color highlightColor = new Color(1f, 1f, 1f, 0.5f);
    
    [Header("Audio")]
    [SerializeField] private AudioClip clickSound;
    
    [Header("Animation")]
    [SerializeField] private ScreenPanelAnimator linkedAnimator;
    
    private bool alreadyClicked = false;
    private ScreenSequenceController screenController;
    private Color originalHighlightColor;

    private void Start()
    {
        // Find ScreenSequenceController in parent hierarchy
        if (screenController == null)
        {
            screenController = GetComponentInParent<ScreenSequenceController>();
            if (screenController == null)
                screenController = FindAnyObjectByType<ScreenSequenceController>();
        }
        
        // Get linked animator if not assigned
        if (linkedAnimator == null)
            linkedAnimator = GetComponent<ScreenPanelAnimator>();
        
        // Store original highlight color
        if (highlightGraphic != null)
            originalHighlightColor = highlightGraphic.color;
    }

    public void OnPointerClick(PointerEventData eventData)
    {
        // Prevent clicking if already clicked (one-time only)
        if (oneTimeOnly && alreadyClicked)
        {
            Debug.Log($"[Screen Hotspot] {hotspotID} already clicked (one-time only)");
            return;
        }
        
        // Prevent clicking if sequence not in progress
        if (screenController != null && !screenController.IsSequenceInProgress)
        {
            Debug.Log($"[Screen Hotspot] {hotspotID} clicked but sequence not in progress");
            return;
        }
        
        alreadyClicked = true;
        
        // Play click sound
        if (clickSound != null)
        {
            AudioSource.PlayClipAtPoint(clickSound, transform.position);
        }
        
        // Notify controller
        if (screenController != null)
            screenController.OnHotspotClicked(hotspotID);
        
        // Play linked animation
        if (linkedAnimator != null)
            linkedAnimator.PlayHotspotAnimation();
        
        Debug.Log($"[Screen Hotspot] Clicked: {hotspotID}");
    }

    public void OnPointerEnter(PointerEventData eventData)
    {
        if (highlightGraphic != null)
        {
            highlightGraphic.color = highlightColor;
        }
    }

    public void OnPointerExit(PointerEventData eventData)
    {
        if (highlightGraphic != null)
        {
            highlightGraphic.color = originalHighlightColor;
        }
    }
    
    /// <summary>
    /// Returns the hotspot ID
    /// </summary>
    public string GetHotspotID() => hotspotID;
    
    /// <summary>
    /// Returns whether this hotspot has been clicked
    /// </summary>
    public bool HasBeenClicked() => alreadyClicked;
    
    /// <summary>
    /// Reset the clicked state (useful for testing or replay scenarios)
    /// </summary>
    public void ResetClickState()
    {
        alreadyClicked = false;
        Debug.Log($"[Screen Hotspot] Reset click state for {hotspotID}");
    }
}
