using UnityEngine;

/// <summary>
/// 2D-optimized pulsing glow animation for sprite overlays.
/// Works directly with SpriteRenderer and optional Point Light.
/// No materials or emission properties required.
/// </summary>
public class MachinePulseGlow2D : MonoBehaviour
{
    [Header("Pulse Settings")]
    public Light glowLight;
    public SpriteRenderer spriteRenderer;

    [SerializeField] private float minIntensity = 0.5f;
    [SerializeField] private float maxIntensity = 2.0f;
    [SerializeField] private float pulseSpeed = 2f;

    [Header("Color Settings")]
    [SerializeField] private Color glowColor = Color.cyan;

    private float elapsedTime = 0f;

    private void Start()
    {
        if (spriteRenderer == null)
            spriteRenderer = GetComponent<SpriteRenderer>();

        elapsedTime = Random.Range(0f, 1f / pulseSpeed);
    }

    private void Update()
    {
        elapsedTime += Time.deltaTime;

        float pulse = Mathf.Sin(elapsedTime * pulseSpeed * Mathf.PI) * 0.5f + 0.5f;

        // Animate light intensity
        if (glowLight != null)
            glowLight.intensity = Mathf.Lerp(minIntensity, maxIntensity, pulse);

        // Animate sprite color and alpha
        if (spriteRenderer != null)
        {
            float alpha = Mathf.Lerp(minIntensity, maxIntensity, pulse);
            Color c = glowColor;
            c.a = alpha;
            spriteRenderer.color = c;
        }
    }
}
