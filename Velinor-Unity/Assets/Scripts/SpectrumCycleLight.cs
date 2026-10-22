using UnityEngine;

/// <summary>
/// Cycles a light's color through the spectrum while maintaining a primarily white base.
/// </summary>
[RequireComponent(typeof(Light))]
public class SpectrumCycleLight : MonoBehaviour
{
    [Header("Cycle Settings")]
    [SerializeField] private float cycleSpeed = 0.5f;
    [SerializeField, Range(0f, 1f)] private float spectrumAmount = 0.2f; // Subtle effect
    [SerializeField] private float baseIntensity = 5f;
    [SerializeField] private float pulseAmount = 0.1f;
    [SerializeField] private float pulseSpeed = 1f;

    private Light targetLight;
    private float hue = 0f;

    private void Start()
    {
        targetLight = GetComponent<Light>();
    }

    private void Update()
    {
        // Cycle hue
        hue += Time.deltaTime * cycleSpeed;
        if (hue > 1f) hue -= 1f;

        // Calculate spectrum color
        Color spectrumColor = Color.HSVToRGB(hue, 0.7f, 1f);

        // Blend with white
        targetLight.color = Color.Lerp(Color.white, spectrumColor, spectrumAmount);

        // Subtle pulsing
        float pulse = Mathf.Sin(Time.time * pulseSpeed) * pulseAmount;
        targetLight.intensity = baseIntensity + pulse;
    }
}
