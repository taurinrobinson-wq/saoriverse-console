using UnityEngine;

/// <summary>
/// Elegant holographic particle effect for glyph projections.
/// Creates a sleek technological appearance with organized particle flow.
/// Suggests "projection" from a Corelink node.
/// </summary>
public class GlyphVisualEffect : MonoBehaviour
{
    [Header("Particle Emission")]
    [SerializeField] private float emissionRate = 15f; // Subtle, not overwhelming
    [SerializeField] private float particleLifetime = 3f;
    [SerializeField] private float particleSize = 0.08f; // Smaller for elegance

    [Header("Particle Movement")]
    // Spiral animation is updated in Update() - see UpdateParticleAnimation()

    [Header("Glyph Appearance")]
    [SerializeField] private Color coreColor = new Color(0.0f, 0.9f, 1f, 1f); // Cyan
    [SerializeField] private Color outerColor = new Color(1f, 0.0f, 0.8f, 0.8f); // Magenta

    [Header("Core Node")]
    [SerializeField] private float coreScale = 0.3f;
    [SerializeField] private float coreGlowIntensity = 2f;

    [Header("Pulsing")]
    [SerializeField] private float pulseSpeed = 2f;
    [SerializeField] private float pulseAmplitude = 0.3f;

    private ParticleSystem glyphParticles;
    private Renderer coreRenderer;
    
    // Cache these as static to avoid redundant Shader.Find() calls
    private static Shader unlitShader;
    private static Shader particleShader;
    private static Material cachedCoreMaterial;
    private static Material cachedParticleMaterial;
    private static Gradient cachedColorGradient;

    private void Start()
    {
        // Cache shaders once
        if (unlitShader == null)
            unlitShader = Shader.Find("Universal Render Pipeline/Unlit");
        if (particleShader == null)
            particleShader = Shader.Find("Universal Render Pipeline/Particles/Unlit");

        // Create the core node visual
        CreateCoreNode();

        // Create elegant particle system
        CreateParticleSystem();
    }

    private void CreateCoreNode()
    {
        // Get or create a small sphere as the core
        Renderer renderer = GetComponent<Renderer>();
        if (renderer == null)
            return;

        // Create glowing core material
        if (cachedCoreMaterial == null)
        {
            cachedCoreMaterial = new Material(unlitShader);
            cachedCoreMaterial.name = "GlyphCoreMaterial_Shared";

            // Transparent rendering
            cachedCoreMaterial.SetFloat("_Surface", 1f);
            cachedCoreMaterial.SetFloat("_Blend", 0f);
            cachedCoreMaterial.SetFloat("_SrcBlend", 5f);
            cachedCoreMaterial.SetFloat("_DstBlend", 10f);
            cachedCoreMaterial.SetFloat("_ZWrite", 0f);
            cachedCoreMaterial.renderQueue = 3000;

            // Bright cyan core
            cachedCoreMaterial.SetColor("_BaseColor", new Color(coreColor.r, coreColor.g, coreColor.b, 0.8f));
        }

        renderer.material = cachedCoreMaterial;

        // Scale down the core node
        transform.localScale = Vector3.one * coreScale;

        Debug.Log($"[GlyphVisualEffect] Holographic core node created for {gameObject.name}");
    }

    private void CreateParticleSystem()
    {
        // Get or create ParticleSystem
        glyphParticles = GetComponent<ParticleSystem>();
        if (glyphParticles == null)
        {
            glyphParticles = gameObject.AddComponent<ParticleSystem>();
        }

        glyphParticles.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear);

        // Main module - long-lived particles for flowing effect
        var main = glyphParticles.main;
        main.duration = 10f;
        main.loop = true;
        main.startLifetime = particleLifetime;
        main.startSize = particleSize;
        main.startColor = new ParticleSystem.MinMaxGradient(coreColor);
        main.maxParticles = 100; // Smaller, more controlled
        main.gravityModifier = -0.1f; // Slight upward drift

        // Emission module - subtle
        var emission = glyphParticles.emission;
        emission.rateOverTime = emissionRate;

        // Shape - emit from core point (not sphere surface)
        var shape = glyphParticles.shape;
        shape.enabled = true;
        shape.shapeType = ParticleSystemShapeType.Sphere;
        shape.radius = 0.1f; // Very small emission radius

        // Initial velocity - minimal
        var initialVel = glyphParticles.velocityOverLifetime;
        initialVel.enabled = true;
        initialVel.x = new ParticleSystem.MinMaxCurve(-0.5f, 0.5f);
        initialVel.y = new ParticleSystem.MinMaxCurve(0.3f, 0.8f); // Slight upward
        initialVel.z = new ParticleSystem.MinMaxCurve(-0.5f, 0.5f);

        // Size over lifetime - elegant fade
        var sizeOverLifetime = glyphParticles.sizeOverLifetime;
        sizeOverLifetime.enabled = true;
        AnimationCurve sizeCurve = AnimationCurve.EaseInOut(0, 1, 1, 0.3f);
        sizeOverLifetime.size = new ParticleSystem.MinMaxCurve(1f, sizeCurve);

        // Color over lifetime - fade to transparent with color gradient
        var colorOverLifetime = glyphParticles.colorOverLifetime;
        colorOverLifetime.enabled = true;
        if (cachedColorGradient == null)
        {
            cachedColorGradient = new Gradient();
            // Cyan to Magenta color shift
            cachedColorGradient.SetKeys(
                new GradientColorKey[] 
                { 
                    new GradientColorKey(coreColor, 0f),
                    new GradientColorKey(Color.Lerp(coreColor, outerColor, 0.5f), 0.5f),
                    new GradientColorKey(outerColor, 1f)
                },
                new GradientAlphaKey[] 
                { 
                    new GradientAlphaKey(1f, 0f),
                    new GradientAlphaKey(0.5f, 0.7f),
                    new GradientAlphaKey(0f, 1f) 
                }
            );
        }
        colorOverLifetime.color = new ParticleSystem.MinMaxGradient(cachedColorGradient);

        // Renderer
        var psRenderer = glyphParticles.GetComponent<ParticleSystemRenderer>();
        if (psRenderer != null)
        {
            psRenderer.renderMode = ParticleSystemRenderMode.Billboard;
            
            if (cachedParticleMaterial == null)
            {
                cachedParticleMaterial = new Material(particleShader);
            }
            psRenderer.material = cachedParticleMaterial;
        }

        // Play
        glyphParticles.Play();

        Debug.Log($"[GlyphVisualEffect] Holographic particle system configured for {gameObject.name}");
    }

    private void Update()
    {
        // Pulsing glow effect on the core
        float pulse = 1f + (Mathf.Sin(Time.time * pulseSpeed) * pulseAmplitude);
        if (coreRenderer != null)
        {
            Color pulseColor = coreColor * new Color(1, 1, 1, pulse * coreGlowIntensity);
            coreRenderer.material.SetColor("_BaseColor", new Color(pulseColor.r, pulseColor.g, pulseColor.b, 0.8f));
        }

        // Gentle rotation for dynamic feel
        transform.Rotate(0, 20f * Time.deltaTime, 0, Space.Self);
    }
}


