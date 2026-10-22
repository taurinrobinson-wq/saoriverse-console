using UnityEngine;
using System.Collections;

/// <summary>
/// Handles animations for screen panels during interactive sequences
/// 
/// Supported Animations:
/// - FadeIn: Panel appears with alpha fade
/// - SplitApart: Panels move left/right to reveal center (for comic panel reveals)
/// - SlideIn: Panel slides in from edge
/// - ScaleIn: Panel scales from zero to full size
/// - Custom: Extensible for other animation types
/// </summary>
public class ScreenPanelAnimator : MonoBehaviour
{
    [Header("Animation Type")]
    [SerializeField] private AnimationType animationType = AnimationType.FadeIn;
    
    [Header("Animation Timing")]
    [SerializeField] private float duration = 1f;
    [SerializeField] private float delay = 0f;
    [SerializeField] private AnimationCurve easeType = AnimationCurve.EaseInOut(0, 0, 1, 1);
    
    [Header("Split Animation Settings")]
    [SerializeField] private float splitDistance = 100f;  // How far panels move apart
    
    [Header("Slide Animation Settings")]
    [SerializeField] private SlideDirection slideDirection = SlideDirection.Up;
    [SerializeField] private float slideDistance = 100f;  // How far to slide
    
    public enum AnimationType
    {
        FadeIn,
        SplitApart,
        SlideIn,
        ScaleIn,
        Custom
    }
    
    public enum SlideDirection
    {
        Up,
        Down,
        Left,
        Right
    }
    
    private CanvasGroup canvasGroup;
    private RectTransform rectTransform;
    private Vector2 startPosition;
    private Vector3 startScale;
    private float startAlpha;

    private void Awake()
    {
        InitializeComponents();
    }

    private void InitializeComponents()
    {
        // Get or create CanvasGroup
        canvasGroup = GetComponent<CanvasGroup>();
        if (canvasGroup == null)
            canvasGroup = gameObject.AddComponent<CanvasGroup>();
        
        // Get RectTransform
        rectTransform = GetComponent<RectTransform>();
        if (rectTransform == null)
        {
            Debug.LogError($"[ScreenPanelAnimator] {gameObject.name} must have RectTransform component");
            return;
        }
        
        // Store initial state
        startPosition = rectTransform.anchoredPosition;
        startScale = rectTransform.localScale;
        startAlpha = canvasGroup.alpha;
    }

    /// <summary>
    /// Play the animation associated with this hotspot being clicked
    /// </summary>
    public void PlayHotspotAnimation()
    {
        StopAllCoroutines();
        StartCoroutine(PlayAnimation());
    }

    private IEnumerator PlayAnimation()
    {
        yield return new WaitForSeconds(delay);
        
        switch (animationType)
        {
            case AnimationType.FadeIn:
                yield return StartCoroutine(AnimateFadeIn());
                break;
            case AnimationType.SplitApart:
                yield return StartCoroutine(AnimateSplitApart());
                break;
            case AnimationType.SlideIn:
                yield return StartCoroutine(AnimateSlideIn());
                break;
            case AnimationType.ScaleIn:
                yield return StartCoroutine(AnimateScaleIn());
                break;
            case AnimationType.Custom:
                // TODO: Implement custom animation logic here
                yield return new WaitForSeconds(duration);
                break;
        }
    }

    /// <summary>
    /// Fade in animation: Panel appears with alpha fade
    /// </summary>
    private IEnumerator AnimateFadeIn()
    {
        float elapsed = 0f;
        canvasGroup.alpha = 0f;
        
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float t = easeType.Evaluate(elapsed / duration);
            canvasGroup.alpha = Mathf.Lerp(0f, startAlpha, t);
            yield return null;
        }
        
        canvasGroup.alpha = startAlpha;
        Debug.Log($"[ScreenPanelAnimator] FadeIn complete on {gameObject.name}");
    }

    /// <summary>
    /// Split apart animation: Panels move left/right to reveal center
    /// Used for revealing hidden panels between comic strips
    /// </summary>
    private IEnumerator AnimateSplitApart()
    {
        // This panel moves away (left or right based on position)
        // Determine direction: if left of center, move further left; if right, move further right
        float centerX = 0f;  // Assuming 0 is center of canvas
        bool moveLeft = startPosition.x < centerX;
        float targetX = startPosition.x + (moveLeft ? -splitDistance : splitDistance);
        
        float elapsed = 0f;
        
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float t = easeType.Evaluate(elapsed / duration);
            float newX = Mathf.Lerp(startPosition.x, targetX, t);
            rectTransform.anchoredPosition = new Vector2(newX, startPosition.y);
            yield return null;
        }
        
        rectTransform.anchoredPosition = new Vector2(targetX, startPosition.y);
        Debug.Log($"[ScreenPanelAnimator] SplitApart complete on {gameObject.name}");
    }

    /// <summary>
    /// Slide in animation: Panel slides in from edge
    /// </summary>
    private IEnumerator AnimateSlideIn()
    {
        Vector2 startSlidePosition = startPosition;
        
        // Calculate start position based on slide direction
        switch (slideDirection)
        {
            case SlideDirection.Up:
                startSlidePosition += Vector2.down * slideDistance;
                break;
            case SlideDirection.Down:
                startSlidePosition += Vector2.up * slideDistance;
                break;
            case SlideDirection.Left:
                startSlidePosition += Vector2.right * slideDistance;
                break;
            case SlideDirection.Right:
                startSlidePosition += Vector2.left * slideDistance;
                break;
        }
        
        float elapsed = 0f;
        rectTransform.anchoredPosition = startSlidePosition;
        
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float t = easeType.Evaluate(elapsed / duration);
            rectTransform.anchoredPosition = Vector2.Lerp(startSlidePosition, startPosition, t);
            yield return null;
        }
        
        rectTransform.anchoredPosition = startPosition;
        Debug.Log($"[ScreenPanelAnimator] SlideIn complete on {gameObject.name}");
    }

    /// <summary>
    /// Scale in animation: Panel scales from zero to full size
    /// Creates a "pop" or "expand" effect
    /// </summary>
    private IEnumerator AnimateScaleIn()
    {
        float elapsed = 0f;
        rectTransform.localScale = Vector3.zero;
        
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float t = easeType.Evaluate(elapsed / duration);
            rectTransform.localScale = Vector3.Lerp(Vector3.zero, startScale, t);
            yield return null;
        }
        
        rectTransform.localScale = startScale;
        Debug.Log($"[ScreenPanelAnimator] ScaleIn complete on {gameObject.name}");
    }

    /// <summary>
    /// Stop all animations and return to start state
    /// Useful for resetting during testing
    /// </summary>
    public void StopAndResetAnimation()
    {
        StopAllCoroutines();
        rectTransform.anchoredPosition = startPosition;
        rectTransform.localScale = startScale;
        canvasGroup.alpha = startAlpha;
        Debug.Log($"[ScreenPanelAnimator] Animation reset on {gameObject.name}");
    }

    /// <summary>
    /// Get current animation type
    /// </summary>
    public AnimationType GetAnimationType() => animationType;

    /// <summary>
    /// Set animation type (useful for dynamic configuration)
    /// </summary>
    public void SetAnimationType(AnimationType newType)
    {
        animationType = newType;
    }

    /// <summary>
    /// Set animation duration
    /// </summary>
    public void SetDuration(float newDuration)
    {
        duration = Mathf.Max(0.1f, newDuration);
    }

    /// <summary>
    /// Set animation delay
    /// </summary>
    public void SetDelay(float newDelay)
    {
        delay = Mathf.Max(0f, newDelay);
    }
}
