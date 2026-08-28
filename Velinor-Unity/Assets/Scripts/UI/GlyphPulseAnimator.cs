using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Animates a glyph icon with pulsing glow, scale, and brightness effects.
/// Creates a star-like, magical appearance.
/// </summary>
public class GlyphPulseAnimator : MonoBehaviour
{
    [Header("Pulse Settings")]
    [SerializeField] private float pulseSpeed = 2f;
    [SerializeField] private float minScale = 0.9f;
    [SerializeField] private float maxScale = 1.1f;
    [SerializeField] private float minBrightness = 0.7f;
    [SerializeField] private float maxBrightness = 1f;

    [Header("Rotation Settings")]
    [SerializeField] private bool rotateIcon = true;
    [SerializeField] private float rotationSpeed = 45f; // degrees per second

    [Header("Glow Effect")]
    [SerializeField] private Image iconImage;
    [SerializeField] private bool useOutlineGlow = true;
    [SerializeField] private Image glowOutline;

    [Header("Particle Effect")]
    [SerializeField] private ParticleSystem glyphParticles;

    private RectTransform rectTransform;
    private Vector3 baseScale;
    private Color baseColor;
    private Color glowColor;

    private void OnEnable()
    {
        rectTransform = GetComponent<RectTransform>();
        if (rectTransform == null)
            rectTransform = transform as RectTransform;

        baseScale = rectTransform.localScale;

        if (iconImage != null)
        {
            baseColor = iconImage.color;
            // Derive glow color from base (brighter, more saturated)
            glowColor = new Color(
                Mathf.Min(baseColor.r * 1.2f, 1f),
                Mathf.Min(baseColor.g * 1.2f, 1f),
                Mathf.Min(baseColor.b * 1.2f, 1f),
                baseColor.a
            );
        }
    }

    private void Update()
    {
        // Pulsing animation using sine wave
        float pulse = Mathf.Sin(Time.time * pulseSpeed * Mathf.PI) * 0.5f + 0.5f; // 0 to 1

        // Apply scale pulse
        float currentScale = Mathf.Lerp(minScale, maxScale, pulse);
        rectTransform.localScale = baseScale * currentScale;

        // Apply brightness pulse
        if (iconImage != null)
        {
            float brightness = Mathf.Lerp(minBrightness, maxBrightness, pulse);
            Color pulsedColor = baseColor * brightness;
            pulsedColor.a = baseColor.a;
            iconImage.color = pulsedColor;
        }

        // Apply glow outline pulse (if enabled)
        if (useOutlineGlow && glowOutline != null)
        {
            Color pulsedGlowColor = glowColor;
            pulsedGlowColor.a = glowColor.a * pulse; // Glow fades in and out
            glowOutline.color = pulsedGlowColor;
        }

        // Rotate icon continuously (star-like effect)
        if (rotateIcon && iconImage != null)
        {
            rectTransform.Rotate(0, 0, -rotationSpeed * Time.deltaTime);
        }
    }

    /// <summary>
    /// Set the base color of the glyph (updates glow accordingly)
    /// </summary>
    public void SetGlyphColor(Color newColor)
    {
        baseColor = newColor;
        glowColor = new Color(
            Mathf.Min(newColor.r * 1.2f, 1f),
            Mathf.Min(newColor.g * 1.2f, 1f),
            Mathf.Min(newColor.b * 1.2f, 1f),
            newColor.a
        );

        if (iconImage != null)
            iconImage.color = baseColor;
    }

    /// <summary>
    /// Enable/disable the pulse animation
    /// </summary>
    public void SetPulseEnabled(bool pulseEnabled)
    {
        this.enabled = pulseEnabled;
    }

    /// <summary>
    /// Trigger a highlight/burst effect (stronger pulse for a moment)
    /// </summary>
    public void TriggerBurst()
    {
        StopAllCoroutines();
        StartCoroutine(BurstAnimation());
    }

    private System.Collections.IEnumerator BurstAnimation()
    {
        float burstDuration = 0.3f;
        float elapsedTime = 0f;

        while (elapsedTime < burstDuration)
        {
            elapsedTime += Time.deltaTime;
            float t = elapsedTime / burstDuration;

            // Expand quickly then settle
            float burstScale = Mathf.Lerp(maxScale * 1.3f, maxScale, t);
            rectTransform.localScale = baseScale * burstScale;

            // Brightness burst
            if (iconImage != null)
            {
                float burstBrightness = Mathf.Lerp(maxBrightness * 1.5f, maxBrightness, t);
                Color burstColor = baseColor * burstBrightness;
                burstColor.a = baseColor.a;
                iconImage.color = burstColor;
            }

            yield return null;
        }
    }
}
