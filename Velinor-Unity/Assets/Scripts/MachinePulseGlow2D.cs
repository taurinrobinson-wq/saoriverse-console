using UnityEngine;

/// <summary>
/// Optimized glow animation for sprites and 3D lights.
/// Provides a smooth, rhythmic non-random pulse.
/// </summary>
public class MachinePulseGlow2D : MonoBehaviour
{
    public enum LightTypeMode { SmoothPulse, FluorescentFlicker }

    [Header("Settings")]
    public LightTypeMode mode = LightTypeMode.SmoothPulse;
    public float minIntensity = 0.5f;
    public float maxIntensity = 2.0f;
    public float pulsePeriod = 2.0f; // Seconds for one full cycle
    public Color glowColor = Color.cyan;

    [Header("Fluorescent Settings (Optional)")]
    public float flickerFreq = 25f;
    public float buzzChance = 0.05f;

    [Header("References")]
    public Light glowLight;
    public SpriteRenderer spriteRenderer;

    private float currentBuzzTime = 0f;
    private float elapsedTime;

    private void Start()
    {
        if (spriteRenderer == null) spriteRenderer = GetComponent<SpriteRenderer>();
        // Add some random offset so not all lights pulse at the exact same moment
        elapsedTime = Random.Range(0f, pulsePeriod);
    }

    private void Update()
    {
        elapsedTime += Time.deltaTime;
        float factor = 0f;

        if (mode == LightTypeMode.SmoothPulse)
        {
            // Rhythmic sine wave pulse
            // pulsePeriod determines the speed (2.0s period = 0.5Hz)
            float freq = (Mathf.PI * 2f) / pulsePeriod;
            factor = (Mathf.Sin(elapsedTime * freq) + 1f) / 2f;
        }
        else
        {
            // High frequency flicker (kept as secondary mode)
            float noise = Mathf.PerlinNoise(elapsedTime * flickerFreq, 0f);
            factor = Mathf.Lerp(0.6f, 1.0f, noise);

            if (currentBuzzTime > 0)
            {
                currentBuzzTime -= Time.deltaTime;
                factor *= Random.Range(0.2f, 0.4f);
            }
            else if (Random.value < buzzChance)
            {
                currentBuzzTime = Random.Range(0.05f, 0.12f);
            }
        }

        float currentInt = Mathf.Lerp(minIntensity, maxIntensity, factor);

        if (spriteRenderer != null)
        {
            Color c = glowColor;
            c.a = factor; 
            spriteRenderer.color = c;
        }

        if (glowLight != null)
        {
            glowLight.intensity = currentInt;
            glowLight.color = glowColor;
        }
    }
}


