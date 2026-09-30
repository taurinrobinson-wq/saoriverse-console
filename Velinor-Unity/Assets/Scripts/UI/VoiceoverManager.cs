using UnityEngine;
using System.Collections;
using System.Collections.Generic;

/// <summary>
/// Manages loading and playing dialogue voiceover audio clips.
/// Loads .ogg files from Resources/Audio/Voiceover/{scene_id}/{clip_name}.ogg
/// Gracefully skips missing files without errors or warnings.
/// 
/// Naming convention for audio files:
/// {speaker}_{dialogue_id}_{beat_id}[_{tone}][_npc].ogg
/// 
/// Examples:
/// - Saori_desert_encounter_01_1.ogg (Saori's dialogue in beat 1)
/// - Saori_desert_encounter_01_1_T_npc.ogg (Saori's response to Trust tone)
/// - Lioren_desert_encounter_01_1_T.ogg (Player's Trust choice)
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
            voiceoverAudioSource = GetComponent<AudioSource>();
            if (voiceoverAudioSource == null)
            {
                voiceoverAudioSource = gameObject.AddComponent<AudioSource>();
            }
        }

        DontDestroyOnLoad(gameObject);
    }

    /// <summary>
    /// Play a pre-loaded voiceover clip directly (fastest method).
    /// Use this when clips are pre-cached by NPCDialogueDriver.
    /// </summary>
    public void PlayVoiceoverClip(AudioClip clip)
    {
        if (clip == null)
        {
            return;
        }

        // Stop any existing fade
        if (fadeCoroutine != null)
        {
            StopCoroutine(fadeCoroutine);
            fadeCoroutine = null;
        }

        voiceoverAudioSource.clip = clip;
        voiceoverAudioSource.volume = 1f;
        voiceoverAudioSource.Play();
        Debug.Log($"[VoiceoverManager] Playing voiceover clip: {clip.name}");
    }

    /// <summary>
    /// Play a voiceover clip for a dialogue beat.
    /// Gracefully skips if file doesn't exist.
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
        // If clip is null (file doesn't exist), we just skip silently
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
    /// Returns null if file not found (graceful degradation - no warnings, just skip).
    /// </summary>
    private AudioClip LoadVoiceoverClip(string sceneId, string clipName)
    {
        string key = $"{sceneId}_{clipName}";

        // Check cache first
        if (voiceoverCache.ContainsKey(key))
        {
            AudioClip cached = voiceoverCache[key];
            if (cached != null)
            {
                Debug.Log($"[VoiceoverManager] Loaded voiceover (cached): {clipName}");
            }
            return cached;
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
            // Cache null so we don't keep trying to load non-existent files
            voiceoverCache[key] = null;
            // Silently skip - this is expected when voiceover hasn't been recorded yet
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
