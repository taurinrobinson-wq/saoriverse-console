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
using System.Collections;

/// <summary>
/// Manages dynamic ambient audio layers.
/// Fades different audio layers in/out based on player location and chamber state.
/// Creates atmospheric depth and environmental responsiveness.
/// </summary>
public class AmbientLayerController : MonoBehaviour
{
    [Header("Audio Layers")]
    [SerializeField] private AudioSource baseAmbience;
    [SerializeField] private AudioSource machineHum;
    [SerializeField] private AudioSource chamberTone;
    [SerializeField] private AudioSource glyphWhisper;

    [Header("Layer Settings")]
    [SerializeField] private float fadeSpeed = 1f;

    private void Awake()
    {
        // Ensure base ambience always plays
        if (baseAmbience != null && !baseAmbience.isPlaying)
            baseAmbience.Play();
    }

    public void SetLayer(string layerName, bool active)
    {
        AudioSource layer = null;

        switch (layerName)
        {
            case "Machine":
                layer = machineHum;
                break;
            case "Chamber":
                layer = chamberTone;
                break;
            case "Glyph":
                layer = glyphWhisper;
                break;
            default:
                Debug.LogWarning($"[AmbientLayerController] Unknown layer: {layerName}");
                return;
        }

        if (layer != null)
            StartCoroutine(FadeLayer(layer, active));
    }

    private IEnumerator FadeLayer(AudioSource layer, bool active)
    {
        float target = active ? 1f : 0f;
        float originalVolume = layer.volume;

        // Start playing if activating
        if (active && !layer.isPlaying)
            layer.Play();

        while (Mathf.Abs(layer.volume - target) > 0.01f)
        {
            layer.volume = Mathf.MoveTowards(layer.volume, target, fadeSpeed * Time.deltaTime);
            yield return null;
        }

        layer.volume = target;

        // Stop audio if deactivated
        if (!active && layer.isPlaying)
            layer.Stop();
    }

    public void ResetAllLayers()
    {
        StopAllCoroutines();
        if (machineHum != null) machineHum.volume = 0;
        if (chamberTone != null) chamberTone.volume = 0;
        if (glyphWhisper != null) glyphWhisper.volume = 0;
    }
}
