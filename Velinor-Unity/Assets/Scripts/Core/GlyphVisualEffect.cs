using UnityEngine;

/// <summary>
/// Adds a glowing particle effect to glyph pickups.
/// Creates a blue fireball/orb appearance with swirling particles.
/// OPTIMIZED: Uses static shader references, cached materials, and reduced particle counts
/// </summary>
public class GlyphVisualEffect : MonoBehaviour
{
    [Header("Particle Emission")]
    [SerializeField] private float emissionRate = 30f; // Reduced from 60 for better performance
    [SerializeField] private float particleLifetime = 2f;
    [SerializeField] private float particleSize = 0.15f;

    [Header("Particle Speed")]
    [SerializeField] private float particleSpeed = 3f;

    [Header("Glyph Appearance")]
    [SerializeField] private Color glyphColor = new Color(0.2f, 0.6f, 1f, 1f); // Bright blue
    // [SerializeField] private float glowIntensity = 3f; // TODO: Apply to material emission intensity

    [Header("Rotation")]
    [SerializeField] private float rotationSpeed = 60f;

    private ParticleSystem glyphParticles;
    
    // Cache these as static to avoid redundant Shader.Find() calls
    private static Shader unlitShader;
    private static Shader particleShader;
    private static Material cachedGlyphMaterial;
    private static Gradient cachedColorGradient;

    private void Start()
    {
        // Cache shaders once (static, so only once per app lifecycle)
        if (unlitShader == null)
            unlitShader = Shader.Find("Universal Render Pipeline/Unlit");
        if (particleShader == null)
            particleShader = Shader.Find("Universal Render Pipeline/Particles/Unlit");

        // Color the sphere blue
        CreateGlowingMaterial();

        // Create particle system
        CreateParticleSystem();
    }

    private void CreateGlowingMaterial()
    {
        Renderer renderer = GetComponent<Renderer>();
        if (renderer == null)
            return;

        // Reuse cached material if available (massive optimization if many glyphs!)
        if (cachedGlyphMaterial == null)
        {
            cachedGlyphMaterial = new Material(unlitShader);
            cachedGlyphMaterial.name = "GlyphGlowMaterial_Shared";

            // Set to TRANSPARENT rendering mode
            cachedGlyphMaterial.SetFloat("_Surface", 1f); // 1 = Transparent
            cachedGlyphMaterial.SetFloat("_Blend", 0f); // 0 = Alpha blend
            cachedGlyphMaterial.SetFloat("_SrcBlend", 5f); // SrcAlpha
            cachedGlyphMaterial.SetFloat("_DstBlend", 10f); // OneMinusSrcAlpha
            cachedGlyphMaterial.SetFloat("_ZWrite", 0f); // Disable ZWrite for transparency
            cachedGlyphMaterial.renderQueue = 3000; // Transparent render queue

            // Base color: semi-transparent bright blue
            Color transparentBlue = new Color(glyphColor.r, glyphColor.g, glyphColor.b, 0.3f);
            cachedGlyphMaterial.SetColor("_BaseColor", transparentBlue);
        }

        // Apply the cached material
        renderer.material = cachedGlyphMaterial;

        Debug.Log($"[GlyphVisualEffect] Glyph configured as transparent blue orb for {gameObject.name}");
    }

    private void CreateParticleSystem()
    {
        // Get or create ParticleSystem
        glyphParticles = GetComponent<ParticleSystem>();
        if (glyphParticles == null)
        {
            glyphParticles = gameObject.AddComponent<ParticleSystem>();
        }

        // STOP the system before modifying it
        glyphParticles.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear);

        // Main module
        var main = glyphParticles.main;
        main.duration = 10f;
        main.loop = true;
        main.startLifetime = particleLifetime;
        main.startSize = particleSize;
        main.startColor = new ParticleSystem.MinMaxGradient(glyphColor);
        main.maxParticles = 150; // Reduced from 500 (major performance gain)

        // Emission module
        var emission = glyphParticles.emission;
        emission.rateOverTime = emissionRate;

        // Shape (emit from sphere surface)
        var shape = glyphParticles.shape;
        shape.enabled = true;
        shape.shapeType = ParticleSystemShapeType.Sphere;
        shape.radius = 0.6f;

        // Velocity over lifetime
        var velocityOverLifetime = glyphParticles.velocityOverLifetime;
        velocityOverLifetime.enabled = true;
        velocityOverLifetime.x = new ParticleSystem.MinMaxCurve(-particleSpeed * 0.3f, particleSpeed * 0.3f);
        velocityOverLifetime.y = new ParticleSystem.MinMaxCurve(-particleSpeed * 0.3f, particleSpeed * 0.3f);
        velocityOverLifetime.z = new ParticleSystem.MinMaxCurve(-particleSpeed * 0.3f, particleSpeed * 0.3f);

        // Size over lifetime (fade out)
        var sizeOverLifetime = glyphParticles.sizeOverLifetime;
        sizeOverLifetime.enabled = true;
        AnimationCurve sizeCurve = AnimationCurve.EaseInOut(0, 1, 1, 0.2f);
        sizeOverLifetime.size = new ParticleSystem.MinMaxCurve(1f, sizeCurve);

        // Color over lifetime (fade to transparent) - cache gradient
        var colorOverLifetime = glyphParticles.colorOverLifetime;
        colorOverLifetime.enabled = true;
        if (cachedColorGradient == null)
        {
            cachedColorGradient = new Gradient();
            cachedColorGradient.SetKeys(
                new GradientColorKey[] { new GradientColorKey(glyphColor, 0f), new GradientColorKey(glyphColor, 1f) },
                new GradientAlphaKey[] { new GradientAlphaKey(1f, 0f), new GradientAlphaKey(0f, 1f) }
            );
        }
        colorOverLifetime.color = new ParticleSystem.MinMaxGradient(cachedColorGradient);

        // Renderer
        var psRenderer = glyphParticles.GetComponent<ParticleSystemRenderer>();
        if (psRenderer != null)
        {
            psRenderer.renderMode = ParticleSystemRenderMode.Billboard;
            psRenderer.material = new Material(particleShader);
        }

        // Play the system now that it's configured
        glyphParticles.Play();

        Debug.Log($"[GlyphVisualEffect] Particle system configured for {gameObject.name}");
    }

    private void Update()
    {
        // Rotate the glyph
        transform.Rotate(0, rotationSpeed * Time.deltaTime, 0);
    }
}


