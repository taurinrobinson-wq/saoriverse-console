using UnityEngine;
using System.Collections;

/// <summary>
/// Visual effects for glyph activation: glow, particles, sound.
/// </summary>
public class GlyphVFX : MonoBehaviour
{
    [Header("Glow Settings")]
    [SerializeField] private SpriteRenderer glyphSprite;
    [SerializeField] private Color activatedColor = Color.cyan;
    [SerializeField] private float glowDuration = 0.4f;

    [Header("Particles")]
    [SerializeField] private ParticleSystem activationParticles;

    [Header("Sound")]
    [SerializeField] private AudioSource activationSound;

    public void PlayVFX()
    {
        // Particle burst
        if (activationParticles != null)
            activationParticles.Play();

        // Sound effect
        if (activationSound != null)
            activationSound.Play();

        // Glow animation
        if (glyphSprite != null)
            StartCoroutine(GlowRoutine());
    }

    private IEnumerator GlowRoutine()
    {
        Color original = glyphSprite.color;
        float time = 0f;

        while (time < glowDuration)
        {
            glyphSprite.color = Color.Lerp(original, activatedColor, time / glowDuration);
            time += Time.deltaTime;
            yield return null;
        }

        glyphSprite.color = activatedColor;
    }
}
