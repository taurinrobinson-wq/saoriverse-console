using UnityEngine;

/// <summary>
/// Manages the Triglyph Projector visuals:
/// 1. Synchronizes the rich spectral color cycle across:
///    - Upward 3D Spot Light (beam illumination)
///    - 3D Aperture Proximity Light (casts shifting colors onto player & projector rings)
///    - Volumetric Cone Beam Material
///    - Metallic Rings Emissive Properties
///    - Dust Particles Color
/// </summary>
[ExecuteAlways]
public class ProjectorEffectController : MonoBehaviour
{
    [Header("Core Lights")]
    [SerializeField] private Light projectorSpotLight;
    [SerializeField] private Light projectorGlowLight;

    [Header("Visual Elements")]
    [SerializeField] private MeshRenderer beamRenderer;
    [SerializeField] private Renderer[] ringRenderers;
    [SerializeField] private ParticleSystem dustParticles;

    [Header("Spectral Cycle Settings")]
    [SerializeField] private float cycleSpeed = 0.20f; // Smooth ~5 sec full cycle
    [SerializeField, Range(0f, 1f)] private float spectrumAmount = 0.75f; // Rich spectral color with high luminosity
    [SerializeField, Range(0f, 1f)] private float spectrumSaturation = 0.85f;
    [SerializeField] private float spotLightIntensity = 18f;
    [SerializeField] private float glowLightIntensity = 22f;

    [Header("Spot Constraints")]
    [SerializeField] private float baseSpotAngle = 50f;
    [SerializeField] private float baseSpotRange = 8.5f;

    private float hue = 0f;
    private Material beamMaterial;
    private MaterialPropertyBlock propBlock;
    private Color currentLightColor = Color.white;

    private static readonly int EmissionColorId = Shader.PropertyToID("_EmissionColor");
    private static readonly int GraphEmissionId = Shader.PropertyToID("Color_488DF21D");
    private static readonly int BaseColorId = Shader.PropertyToID("_BaseColor");

    private void Awake()
    {
        InitializeComponents();
    }

    private void OnEnable()
    {
        InitializeComponents();
    }

    private void InitializeComponents()
    {
        if (propBlock == null)
            propBlock = new MaterialPropertyBlock();

        if (projectorSpotLight == null)
        {
            var slObj = transform.Find("ProjectorLight");
            if (slObj != null) projectorSpotLight = slObj.GetComponent<Light>();
        }

        if (projectorGlowLight == null)
        {
            var glObj = transform.Find("ProjectorGlowLight");
            if (glObj != null) projectorGlowLight = glObj.GetComponent<Light>();
        }

        if (beamRenderer != null)
        {
            beamMaterial = Application.isPlaying ? beamRenderer.material : beamRenderer.sharedMaterial;
        }
    }

    private void Update()
    {
        // 1. Advance Spectral Hue
        float delta = Application.isPlaying ? Time.deltaTime : 0.016f;
        hue += delta * cycleSpeed;
        if (hue > 1f) hue -= 1f;

        Color hsvColor = Color.HSVToRGB(hue, spectrumSaturation, 1f);
        currentLightColor = Color.Lerp(Color.white, hsvColor, spectrumAmount);

        // 2. Synchronize Spot Light (Upward cone)
        if (projectorSpotLight != null)
        {
            projectorSpotLight.type = LightType.Spot;
            projectorSpotLight.spotAngle = baseSpotAngle;
            projectorSpotLight.range = baseSpotRange;
            projectorSpotLight.color = currentLightColor;
            projectorSpotLight.intensity = spotLightIntensity;
        }

        // 3. Synchronize Proximity Glow Light (Shines onto player and rings)
        if (projectorGlowLight != null)
        {
            projectorGlowLight.type = LightType.Point;
            projectorGlowLight.color = currentLightColor;
            projectorGlowLight.intensity = glowLightIntensity;
        }

        // 4. Synchronize Volumetric Cone Beam Material
        if (beamMaterial != null)
        {
            Color beamCol = new Color(currentLightColor.r, currentLightColor.g, currentLightColor.b, 0.25f);
            beamMaterial.SetColor(BaseColorId, beamCol);
        }

        // 5. Synchronize Emissive Rings (both standard URP Lit and Graph IDs)
        if (ringRenderers != null && ringRenderers.Length > 0)
        {
            Color hdrEmissive = currentLightColor * 2.5f;
            for (int i = 0; i < ringRenderers.Length; i++)
            {
                if (ringRenderers[i] == null) continue;
                ringRenderers[i].GetPropertyBlock(propBlock);
                propBlock.SetColor(EmissionColorId, hdrEmissive);
                propBlock.SetColor(GraphEmissionId, hdrEmissive);
                ringRenderers[i].SetPropertyBlock(propBlock);
            }
        }

        // 6. Synchronize Dust Particle Color
        if (dustParticles != null)
        {
            var main = dustParticles.main;
            Color pCol = currentLightColor;
            pCol.a = 0.6f;
            main.startColor = pCol;
        }
    }

    /// <summary>
    /// Checks if a world position (e.g. player) is within the conical beam radius.
    /// </summary>
    public bool CheckPlayerInsideBeam(Vector3 playerPosition, out float factor, out Color lightColor)
    {
        factor = 0f;
        lightColor = currentLightColor;

        Vector3 localOffset = playerPosition - transform.position;
        float horizontalDist = new Vector2(localOffset.x, localOffset.z).magnitude;

        if (horizontalDist <= 2.5f)
        {
            factor = Mathf.Clamp01(1f - (horizontalDist / 2.5f));
            return true;
        }

        return false;
    }

    public Color GetCurrentColor() => currentLightColor;
}




