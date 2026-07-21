using UnityEngine;

/// <summary>
/// Adds a shimmering/flickering effect to machine materials.
/// Combines Perlin noise for organic motion with periodic spikes.
/// </summary>
public class MachineShimmer : MonoBehaviour
{
    [Header("Shimmer Settings")]
    public Material[] shimmerMaterials;
    [SerializeField] private float shimmerSpeed = 2f;
    [SerializeField] private float shimmerIntensity = 0.3f;
    [SerializeField] private float baseEmissionValue = 1.0f;

    [Header("Flicker Settings")]
    [SerializeField] private bool enableFlicker = true;
    [SerializeField] private float flickerChance = 0.15f;
    [SerializeField] private float flickerIntensity = 0.5f;

    [Header("Color Settings")]
    [SerializeField] private Color baseColor = Color.cyan;
    [SerializeField] private Color shimmerColor = Color.white;

    private Material[] materialInstances;
    private float[] noiseOffsets;
    private float flickerTimer = 0f;
    private float flickerDuration = 0.1f;
    private bool isFlickering = false;

    private void Start()
    {
        // Ensure shimmerMaterials array is valid
        if (shimmerMaterials == null || shimmerMaterials.Length == 0)
        {
            Debug.LogWarning("MachineShimmer: No shimmer materials assigned!");
            return;
        }

        // Create material instances to avoid affecting other objects
        materialInstances = new Material[shimmerMaterials.Length];
        noiseOffsets = new float[shimmerMaterials.Length];

        Renderer renderer = GetComponent<Renderer>();
        if (renderer != null)
        {
            for (int i = 0; i < shimmerMaterials.Length; i++)
            {
                if (shimmerMaterials[i] != null)
                {
                    materialInstances[i] = new Material(shimmerMaterials[i]);
                    noiseOffsets[i] = Random.Range(0f, 100f);
                }
            }
            renderer.materials = materialInstances;
        }
    }

    private void Update()
    {
        // Handle flickering
        if (enableFlicker)
        {
            flickerTimer -= Time.deltaTime;
            if (flickerTimer <= 0f)
            {
                if (Random.value < flickerChance)
                {
                    isFlickering = true;
                    flickerTimer = flickerDuration;
                }
                else
                {
                    flickerTimer = Random.Range(0.3f, 1f);
                }
            }
        }

        // Update shimmer for each material
        for (int i = 0; i < materialInstances.Length; i++)
        {
            UpdateMaterialShimmer(materialInstances[i], i);
        }
    }

    private void UpdateMaterialShimmer(Material mat, int index)
    {
        // Use Perlin noise for smooth, organic shimmer
        float noiseValue = Mathf.PerlinNoise(
            Time.time * shimmerSpeed + noiseOffsets[index],
            noiseOffsets[index]
        );

        // Map noise to shimmer range
        float shimmer = Mathf.Lerp(
            baseEmissionValue - shimmerIntensity,
            baseEmissionValue + shimmerIntensity,
            noiseValue
        );

        // Apply flicker spike if active
        if (isFlickering)
        {
            shimmer *= (1f - flickerIntensity);
        }

        // Blend between base color and shimmer color
        float colorBlend = (noiseValue - 0.5f) * 2f * shimmerIntensity;
        Color finalColor = Color.Lerp(baseColor, shimmerColor, Mathf.Clamp01(colorBlend + 0.5f));

        mat.SetColor("_EmissionColor", finalColor * shimmer);
    }

    /// <summary>
    /// Allows runtime adjustment of shimmer effect
    /// </summary>
    public void SetShimmerIntensity(float intensity)
    {
        shimmerIntensity = Mathf.Clamp01(intensity);
    }
}
