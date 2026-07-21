/*
 * ============================================================
 * PROPRIETARY & CONFIDENTIAL
 * 
 * © 2026 Tauri Robinson. All rights reserved.
 * This code is proprietary and may not be redistributed,
 * modified, or used without explicit written permission.
 * 
 * Unauthorized access, modification, or distribution is prohibited.
 * See LICENSE_COMMERCIAL.md and NDA_TEMPLATE.md for details.
 * ============================================================
 */

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
