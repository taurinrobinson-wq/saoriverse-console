using UnityEngine;
using System.Collections.Generic;

namespace Velinor.Core
{
    /// <summary>
    /// AudioManager - Handles background music and ambient soundscapes
    /// 
    /// Integrates with MarketSceneSetup for dusk atmosphere
    /// Manages looping music with crossfading support
    /// </summary>
    public class AudioManager : MonoBehaviour
    {
        [SerializeField] private AudioSource musicSource;
        [SerializeField] private AudioClip currentTrack;
        [SerializeField] private float musicVolume = 0.7f;
        [SerializeField] private bool autoLoopMusic = true;
        [SerializeField] private float crossfadeDuration = 2f;

        // Track references
        [Header("Available Tracks")]
        [SerializeField] private AudioClip glassHorizonClip;
        [SerializeField] private AudioClip strangeSerenitySfxClip;
        [SerializeField] private AudioClip intoTheCodexClip;
        [SerializeField] private AudioClip travelingAlongClip;
        [SerializeField] private AudioClip sorrowWalksClip;
        [SerializeField] private AudioClip simpleClip;
        [SerializeField] private AudioClip ambienceClip;
        [SerializeField] private AudioClip velinorFadesSfxClip;

        private float targetVolume;
        private bool isCrossfading = false;

        private void OnEnable()
        {
            InitializeAudioSource();
            LoadAudioClips();
        }

        private void InitializeAudioSource()
        {
            if (musicSource == null)
            {
                try
                {
                    musicSource = gameObject.AddComponent<AudioSource>();
                }
                catch (System.Exception ex)
                {
                    Debug.LogWarning($"AudioManager: Failed to create AudioSource - {ex.Message}. Retrying...");
                    musicSource = gameObject.AddComponent<AudioSource>();
                }
            }

            if (musicSource != null)
            {
                musicSource.loop = autoLoopMusic;
                musicSource.volume = musicVolume;
                musicSource.playOnAwake = false;
            }
        }

        private void LoadAudioClips()
        {
            // Load all music clips from Resources/Music folder
            // Files must be in Assets/Resources/Music/ (without extension in path)
            
            Debug.Log("🎵 AudioManager: Loading audio clips from Resources/Music...");
            
            if (glassHorizonClip == null)
            {
                glassHorizonClip = Resources.Load<AudioClip>("Music/Glass-Horizon");
                if (glassHorizonClip != null)
                    Debug.Log("  ✅ Glass-Horizon loaded");
                else
                    Debug.LogWarning("  ❌ Glass-Horizon NOT FOUND - check Assets/Resources/Music/");
            }
            
            if (strangeSerenitySfxClip == null)
            {
                strangeSerenitySfxClip = Resources.Load<AudioClip>("Music/A-strange-serenity-_fade_");
                if (strangeSerenitySfxClip != null)
                    Debug.Log("  ✅ A-strange-serenity loaded");
                else
                    Debug.LogWarning("  ❌ A-strange-serenity NOT FOUND");
            }
            
            if (intoTheCodexClip == null)
            {
                intoTheCodexClip = Resources.Load<AudioClip>("Music/Into-the-codex");
                if (intoTheCodexClip != null)
                    Debug.Log("  ✅ Into-the-codex loaded");
                else
                    Debug.LogWarning("  ❌ Into-the-codex NOT FOUND");
            }
            
            if (travelingAlongClip == null)
            {
                travelingAlongClip = Resources.Load<AudioClip>("Music/Traveling-along");
                if (travelingAlongClip != null)
                    Debug.Log("  ✅ Traveling-along loaded");
                else
                    Debug.LogWarning("  ❌ Traveling-along NOT FOUND");
            }
            
            if (sorrowWalksClip == null)
            {
                sorrowWalksClip = Resources.Load<AudioClip>("Music/Sorrow-walks");
                if (sorrowWalksClip != null)
                    Debug.Log("  ✅ Sorrow-walks loaded");
                else
                    Debug.LogWarning("  ❌ Sorrow-walks NOT FOUND");
            }
            
            if (simpleClip == null)
            {
                simpleClip = Resources.Load<AudioClip>("Music/Simple");
                if (simpleClip != null)
                    Debug.Log("  ✅ Simple loaded");
                else
                    Debug.LogWarning("  ❌ Simple NOT FOUND");
            }
            
            if (ambienceClip == null)
            {
                ambienceClip = Resources.Load<AudioClip>("Music/Some-ambience-");
                if (ambienceClip != null)
                    Debug.Log("  ✅ Some-ambience loaded");
                else
                    Debug.LogWarning("  ❌ Some-ambience NOT FOUND");
            }
            
            if (velinorFadesSfxClip == null)
            {
                velinorFadesSfxClip = Resources.Load<AudioClip>("Music/Velinor-fades-_effect_");
                if (velinorFadesSfxClip != null)
                    Debug.Log("  ✅ Velinor-fades loaded");
                else
                    Debug.LogWarning("  ❌ Velinor-fades NOT FOUND");
            }
        }

        /// <summary>
        /// Play Glass Horizon as market soundscape
        /// </summary>
        public void PlayMarketSoundscape()
        {
            PlayMusicTrack(glassHorizonClip, "Glass Horizon - Market Soundscape");
        }

        /// <summary>
        /// Play any track with name
        /// </summary>
        public void PlayMusicTrack(AudioClip clip, string trackName = "")
        {
            if (clip == null)
            {
                Debug.LogWarning($"AudioManager: Clip '{trackName}' is null. Cannot play.");
                Debug.LogWarning("  Make sure audio files are in Assets/Resources/Music/");
                Debug.LogWarning("  File must end in .ogg or .mp3, Resource path does NOT include extension");
                return;
            }

            if (musicSource == null)
            {
                Debug.LogError("AudioManager: musicSource is null!");
                return;
            }

            if (isCrossfading)
            {
                StopCoroutine(Crossfade(null, 0));
            }

            musicSource.clip = clip;
            musicSource.Play();
            currentTrack = clip;

            string label = string.IsNullOrEmpty(trackName) ? clip.name : trackName;
            Debug.Log($"🎵 Now playing: {label}");
        }

            if (!string.IsNullOrEmpty(trackName))
                Debug.Log($"🎵 Now playing: {trackName}");
        }

        /// <summary>
        /// Crossfade between two tracks (e.g., market music → dialogue music)
        /// </summary>
        public void CrossfadeToTrack(AudioClip newClip, string trackName = "")
        {
            if (newClip == null) return;

            StopAllCoroutines();
            StartCoroutine(Crossfade(newClip, crossfadeDuration));

            if (!string.IsNullOrEmpty(trackName))
                Debug.Log($"🎵 Crossfading to: {trackName}");
        }

        private System.Collections.IEnumerator Crossfade(AudioClip newClip, float duration)
        {
            isCrossfading = true;
            float elapsed = 0f;

            // Fade out
            while (elapsed < duration)
            {
                elapsed += Time.deltaTime;
                musicSource.volume = Mathf.Lerp(musicVolume, 0, elapsed / duration);
                yield return null;
            }

            // Switch clip
            if (newClip != null)
            {
                musicSource.clip = newClip;
                musicSource.Play();
                currentTrack = newClip;
            }

            // Fade in
            elapsed = 0f;
            while (elapsed < duration)
            {
                elapsed += Time.deltaTime;
                musicSource.volume = Mathf.Lerp(0, musicVolume, elapsed / duration);
                yield return null;
            }

            musicSource.volume = musicVolume;
            isCrossfading = false;
        }

        /// <summary>
        /// Stop music with optional fade
        /// </summary>
        public void StopMusic(float fadeOutDuration = 0)
        {
            if (fadeOutDuration > 0)
            {
                StartCoroutine(FadeOutAndStop(fadeOutDuration));
            }
            else
            {
                musicSource.Stop();
            }
        }

        private System.Collections.IEnumerator FadeOutAndStop(float duration)
        {
            float elapsed = 0f;
            float startVolume = musicSource.volume;

            while (elapsed < duration)
            {
                elapsed += Time.deltaTime;
                musicSource.volume = Mathf.Lerp(startVolume, 0, elapsed / duration);
                yield return null;
            }

            musicSource.Stop();
            musicSource.volume = musicVolume;
        }

        /// <summary>
        /// Control volume
        /// </summary>
        public void SetMusicVolume(float volume)
        {
            musicVolume = Mathf.Clamp01(volume);
            musicSource.volume = musicVolume;
        }

        public float GetMusicVolume() => musicVolume;
        public bool IsPlaying() => musicSource.isPlaying;
        public AudioClip GetCurrentTrack() => currentTrack;
    }
}
