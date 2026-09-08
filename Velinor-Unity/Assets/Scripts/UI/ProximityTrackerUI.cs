using UnityEngine;
using UnityEngine.UI;
using System.Collections;

/// <summary>
/// Proximity tracker UI - displays a pulsing red light that increases in frequency
/// as the player approaches a target glyph collider.
/// Manages the visual feedback for hunting down glyphs.
/// </summary>
public class ProximityTrackerUI : MonoBehaviour
{
    [Header("Tracker Settings")]
    [SerializeField] private Image trackerLight;  // The pulsing red light indicator
    [SerializeField] private float maxDistance = 50f;  // Distance at which pulse is slowest
    [SerializeField] private float minDistance = 2f;   // Distance at which pulse is fastest
    [SerializeField] private float minPulseFrequency = 0.5f;  // Pulses per second at max distance
    [SerializeField] private float maxPulseFrequency = 3f;    // Pulses per second at min distance

    [Header("Visual Settings")]
    [SerializeField] private Color activeColor = Color.red;
    [SerializeField] private Color inactiveColor = new Color(1, 0, 0, 0.2f);
    [SerializeField] private AnimationCurve pulseCurve = AnimationCurve.EaseInOut(0, 0, 1, 1);

    private Collider targetGlyphCollider;
    private bool isTracking = false;
    private float currentPulseFrequency;
    private float pulseTimer = 0f;
    private CanvasGroup canvasGroup;

    private void Awake()
    {
        if (trackerLight == null)
        {
            trackerLight = GetComponent<Image>();
        }

        canvasGroup = GetComponent<CanvasGroup>();
        if (canvasGroup == null)
        {
            canvasGroup = gameObject.AddComponent<CanvasGroup>();
        }

        // Mark as persistent
        DontDestroyOnLoad(gameObject);
        Debug.Log("[ProximityTracker] ProximityTrackerUI initialized");
    }

    private void Start()
    {
        // Hide tracker initially
        SetTrackerActive(false);
    }

    private void Update()
    {
        if (!isTracking || targetGlyphCollider == null)
        {
            SetTrackerActive(false);
            return;
        }

        // Calculate distance to target glyph
        Transform player = FindAnyObjectByType<PlayerController2D5>()?.transform;
        if (player == null) return;

        Vector3 glyphCenter = targetGlyphCollider.bounds.center;
        float distance = Vector3.Distance(player.position, glyphCenter);

        // Clamp distance to min/max range
        distance = Mathf.Clamp(distance, minDistance, maxDistance);

        // Calculate pulse frequency based on distance (closer = faster pulse)
        float distanceRatio = (maxDistance - distance) / (maxDistance - minDistance);
        currentPulseFrequency = Mathf.Lerp(minPulseFrequency, maxPulseFrequency, distanceRatio);

        // Update pulse timer
        pulseTimer += Time.deltaTime * currentPulseFrequency;
        if (pulseTimer > 1f) pulseTimer -= 1f;

        // Apply pulse animation using curve
        float pulseValue = pulseCurve.Evaluate(pulseTimer);
        Color displayColor = Color.Lerp(inactiveColor, activeColor, pulseValue);

        if (trackerLight != null)
        {
            trackerLight.color = displayColor;
        }

        Debug.Log($"[ProximityTracker] Distance: {distance:F2}m, Frequency: {currentPulseFrequency:F2} Hz");
    }

    /// <summary>
    /// Activate tracking for a specific glyph collider
    /// </summary>
    public void StartTracking(Collider glyphCollider)
    {
        if (glyphCollider == null)
        {
            Debug.LogWarning("[ProximityTracker] Cannot start tracking - collider is null");
            return;
        }

        targetGlyphCollider = glyphCollider;
        isTracking = true;
        SetTrackerActive(true);
        Debug.Log($"[ProximityTracker] Started tracking glyph at {glyphCollider.name}");
    }

    /// <summary>
    /// Stop tracking and hide the tracker
    /// </summary>
    public void StopTracking()
    {
        isTracking = false;
        targetGlyphCollider = null;
        SetTrackerActive(false);
        Debug.Log("[ProximityTracker] Stopped tracking");
    }

    /// <summary>
    /// Set tracker visibility and interactability
    /// </summary>
    private void SetTrackerActive(bool active)
    {
        if (canvasGroup != null)
        {
            canvasGroup.alpha = active ? 1f : 0f;
            canvasGroup.blocksRaycasts = active;
            canvasGroup.interactable = active;
        }
    }

    /// <summary>
    /// Check if tracker is currently active
    /// </summary>
    public bool IsTracking => isTracking;
}
