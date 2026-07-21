using UnityEngine;
using System.Collections;

/// <summary>
/// Animates cable/conduit glow effects.
/// Pulses with a continuous glow and supports strong pulse activation.
/// Add to any cable sprite to show energy flowing through conduits.
/// </summary>
public class CableGlow : MonoBehaviour
{
    [Header("Glow Settings")]
    [SerializeField] private SpriteRenderer cableSprite;
    [SerializeField] private Color glowColor = Color.cyan;
    [SerializeField] private float pulseSpeed = 2f;
    [SerializeField] private float intensity = 0.5f;

    private Color baseColor;
    private bool isInitialized = false;

    private void Start()
    {
        if (cableSprite != null)
        {
            baseColor = cableSprite.color;
            isInitialized = true;
        }
        else
        {
            Debug.LogWarning($"[CableGlow] No SpriteRenderer assigned to {gameObject.name}");
        }
    }

    private void Update()
    {
        if (!isInitialized) return;

        // Continuous pulsing glow
        float t = (Mathf.Sin(Time.time * pulseSpeed) + 1f) / 2f;
        cableSprite.color = Color.Lerp(baseColor, glowColor, t * intensity);
    }

    /// <summary>
    /// Trigger a strong pulse (activation effect).
    /// </summary>
    public void ActivateStrongPulse()
    {
        StartCoroutine(StrongPulseRoutine());
    }

    private IEnumerator StrongPulseRoutine()
    {
        float time = 0f;
        float duration = 0.5f;

        while (time < duration)
        {
            float t = Mathf.PingPong(time * 8f, 1f);
            cableSprite.color = Color.Lerp(baseColor, glowColor, t);
            time += Time.deltaTime;
            yield return null;
        }

        cableSprite.color = baseColor;
    }
}
