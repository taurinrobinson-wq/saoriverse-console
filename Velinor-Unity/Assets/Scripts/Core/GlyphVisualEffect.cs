using UnityEngine;

/// <summary>
/// Adds a glowing particle effect to glyph pickups.
/// Creates a blue fireball/orb appearance with swirling particles.
/// </summary>
public class GlyphVisualEffect : MonoBehaviour
{
    [Header("Particle Emission")]
    [SerializeField] private float emissionRate = 60f;
    [SerializeField] private float particleLifetime = 2f;
    [SerializeField] private float particleSize = 0.15f;

    [Header("Particle Speed")]
    [SerializeField] private float particleSpeed = 3f;

    [Header("Glyph Appearance")]
    [SerializeField] private Color glyphColor = new Color(0.2f, 0.6f, 1f, 1f); // Bright blue
    [SerializeField] private float glowIntensity = 3f;

    [Header("Rotation")]
    [SerializeField] private float rotationSpeed = 60f;

    private ParticleSystem glyphParticles;

    private void Start()
    {
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

        // Use Unlit shader which handles transparency better than Lit
        Material mat = new Material(Shader.Find("Universal Render Pipeline/Unlit"));
        mat.name = "GlyphGlowMaterial";

        // Set to TRANSPARENT rendering mode
        mat.SetFloat("_Surface", 1f); // 1 = Transparent
        mat.SetFloat("_Blend", 0f); // 0 = Alpha blend
        mat.SetFloat("_SrcBlend", 5f); // SrcAlpha
        mat.SetFloat("_DstBlend", 10f); // OneMinusSrcAlpha
        mat.SetFloat("_ZWrite", 0f); // Disable ZWrite for transparency
        mat.renderQueue = 3000; // Transparent render queue

        // Base color: semi-transparent bright blue (let's see if this works better)
        Color transparentBlue = new Color(glyphColor.r, glyphColor.g, glyphColor.b, 0.3f);
        mat.SetColor("_BaseColor", transparentBlue);

        // Apply the material
        renderer.material = mat;

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
        main.maxParticles = 500;

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

        // Color over lifetime (fade to transparent)
        var colorOverLifetime = glyphParticles.colorOverLifetime;
        colorOverLifetime.enabled = true;
        Gradient gradient = new Gradient();
        gradient.SetKeys(
            new GradientColorKey[] { new GradientColorKey(glyphColor, 0f), new GradientColorKey(glyphColor, 1f) },
            new GradientAlphaKey[] { new GradientAlphaKey(1f, 0f), new GradientAlphaKey(0f, 1f) }
        );
        colorOverLifetime.color = new ParticleSystem.MinMaxGradient(gradient);

        // Renderer
        var psRenderer = glyphParticles.GetComponent<ParticleSystemRenderer>();
        if (psRenderer != null)
        {
            psRenderer.renderMode = ParticleSystemRenderMode.Billboard;
            psRenderer.material = new Material(Shader.Find("Universal Render Pipeline/Particles/Unlit"));
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


