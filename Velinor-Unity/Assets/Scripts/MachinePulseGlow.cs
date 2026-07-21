using UnityEngine;

/// <summary>
/// Creates a pulsing glow animation on machine orbs.
/// Animates both the light intensity and emission material.
/// </summary>
public class MachinePulseGlow : MonoBehaviour
{
    [Header("Pulse Settings")]
    public Light glowLight;
    public Material glowMaterial;
    [SerializeField] private float minIntensity = 0.5f;
    [SerializeField] private float maxIntensity = 2.0f;
    [SerializeField] private float pulseSpeed = 2f;

    [Header("Emission Settings")]
    [SerializeField] private float minEmission = 0.5f;
    [SerializeField] private float maxEmission = 2.0f;
    [SerializeField] private Color glowColor = Color.cyan;

    private float elapsedTime = 0f;
    private Material emissionMaterialInstance;

    private void Start()
    {
        // Create a material instance to avoid affecting other objects
        if (glowMaterial != null)
        {
            emissionMaterialInstance = new Material(glowMaterial);
            Renderer renderer = GetComponent<Renderer>();
            if (renderer != null)
            {
                renderer.material = emissionMaterialInstance;
            }
        }

        // Randomize start time for natural variation
        elapsedTime = Random.Range(0f, 1f / pulseSpeed);
    }

    private void Update()
    {
        elapsedTime += Time.deltaTime;

        // Use sine wave for smooth pulsing
        float pulse = Mathf.Sin(elapsedTime * pulseSpeed * Mathf.PI) * 0.5f + 0.5f;

        // Animate light intensity
        if (glowLight != null)
        {
            glowLight.intensity = Mathf.Lerp(minIntensity, maxIntensity, pulse);
        }

        // Animate emission
        if (emissionMaterialInstance != null)
        {
            float emissionValue = Mathf.Lerp(minEmission, maxEmission, pulse);
            emissionMaterialInstance.SetColor("_EmissionColor", glowColor * emissionValue);
        }
    }

    /// <summary>
    /// Allows runtime adjustment of pulse speed
    /// </summary>
    public void SetPulseSpeed(float newSpeed)
    {
        pulseSpeed = newSpeed;
    }
}
