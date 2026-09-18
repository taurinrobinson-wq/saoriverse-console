using UnityEngine;
using System.Collections;
using System.Collections.Generic;

/// <summary>
/// Manages loading and playing dialogue voiceover audio clips.
/// Loads .ogg files from Resources/Audio/Voiceover/{scene_id}/{clip_name}.ogg
/// Handles audio playback, caching, and fade-out when player makes choices.
/// Gracefully handles missing audio files without errors.
/// </summary>
public class VoiceoverManager : MonoBehaviour
{
    [SerializeField] private AudioSource voiceoverAudioSource;
    private Dictionary<string, AudioClip> voiceoverCache = new Dictionary<string, AudioClip>();
    private Coroutine fadeCoroutine;

    private void Awake()
    {
        if (voiceoverAudioSource == null)
        {
            // Try to find or create an AudioSource for voiceover
            voiceoverAudioSource = GetComponent<AudioSource>();
            if (voiceoverAudioSource == null)
            {
                voiceoverAudioSource = gameObject.AddComponent<AudioSource>();
            }
        }

        DontDestroyOnLoad(gameObject);
    }

    /// <summary>
    /// Play a voiceover clip for a dialogue beat.
    /// </summary>
    public void PlayVoiceover(string sceneId, string clipName)
    {
        if (string.IsNullOrEmpty(sceneId) || string.IsNullOrEmpty(clipName))
        {
            return;
        }

        // Stop any existing fade
        if (fadeCoroutine != null)
        {
            StopCoroutine(fadeCoroutine);
            fadeCoroutine = null;
        }

        AudioClip clip = LoadVoiceoverClip(sceneId, clipName);
        if (clip != null)
        {
            voiceoverAudioSource.clip = clip;
            voiceoverAudioSource.volume = 1f;
            voiceoverAudioSource.Play();
            Debug.Log($"[VoiceoverManager] Playing: {sceneId}/{clipName}");
        }
    }

    /// <summary>
    /// Stop current voiceover with fade-out to prevent clipping.
    /// Called when player makes a choice.
    /// </summary>
    public void FadeOutAndStop(float fadeDuration = 0.3f)
    {
        if (voiceoverAudioSource.isPlaying)
        {
            if (fadeCoroutine != null)
            {
                StopCoroutine(fadeCoroutine);
            }
            fadeCoroutine = StartCoroutine(FadeOutCoroutine(fadeDuration));
        }
    }

    private IEnumerator FadeOutCoroutine(float duration)
    {
        float elapsedTime = 0f;
        float startVolume = voiceoverAudioSource.volume;

        while (elapsedTime < duration)
        {
            elapsedTime += Time.deltaTime;
            voiceoverAudioSource.volume = Mathf.Lerp(startVolume, 0f, elapsedTime / duration);
            yield return null;
        }

        voiceoverAudioSource.Stop();
        voiceoverAudioSource.volume = 1f;
        fadeCoroutine = null;
    }

    /// <summary>
    /// Stop voiceover immediately (e.g., when dialogue ends).
    /// </summary>
    public void StopVoiceover()
    {
        if (fadeCoroutine != null)
        {
            StopCoroutine(fadeCoroutine);
            fadeCoroutine = null;
        }

        if (voiceoverAudioSource.isPlaying)
        {
            voiceoverAudioSource.Stop();
        }

        voiceoverAudioSource.volume = 1f;
    }

    /// <summary>
    /// Load a voiceover clip from Resources, using cache if available.
    /// Loads from: Resources/Audio/Voiceover/{sceneId}/{clipName}.ogg
    /// Returns null if file not found (graceful degradation).
    /// </summary>
    private AudioClip LoadVoiceoverClip(string sceneId, string clipName)
    {
        string key = $"{sceneId}_{clipName}";

        // Check cache first
        if (voiceoverCache.ContainsKey(key))
        {
            return voiceoverCache[key];
        }

        // Try to load from Resources
        string resourcePath = $"Audio/Voiceover/{sceneId}/{clipName}";
        AudioClip clip = Resources.Load<AudioClip>(resourcePath);

        if (clip != null)
        {
            voiceoverCache[key] = clip;
            Debug.Log($"[VoiceoverManager] Loaded voiceover: {resourcePath}");
        }
        else
        {
            Debug.LogWarning($"[VoiceoverManager] Voiceover not found at: {resourcePath} (file may not exist yet)");
        }

        return clip;
    }

    /// <summary>
    /// Clear the voiceover cache (useful for memory management between scenes).
    /// </summary>
    public void ClearCache()
    {
        voiceoverCache.Clear();
        Debug.Log("[VoiceoverManager] Voiceover cache cleared");
    }
}
