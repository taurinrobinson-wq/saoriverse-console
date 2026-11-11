using Velinor.Core;
using UnityEngine;

namespace Velinor.Scenes
{
    /// <summary>
    /// SceneAudioController - Attach to a game object in any scene to control audio behavior
    /// 
    /// This component demonstrates the recommended pattern for handling persistent audio
    /// across scene transitions. Use this as a template for your scene-specific audio logic.
    /// </summary>
    public class SceneAudioController : MonoBehaviour
    {
        [SerializeField] private AudioClip sceneAmbientMusic;
        [SerializeField] private bool forceMusicChange = false;
        [SerializeField] private bool stopMusicOnEntry = false;
        [SerializeField] private float fadeOutDuration = 1.5f;
        [SerializeField] private string sceneName = "";

        private void Start()
        {
            if (string.IsNullOrEmpty(sceneName))
                sceneName = gameObject.scene.name;

            // Handle music for this scene
            HandleSceneAudio();
        }

        private void HandleSceneAudio()
        {
            // Option 1: Silence this scene
            if (stopMusicOnEntry)
            {
                AudioManager.Instance.StopMusic(fadeOutDuration);
                Debug.Log($"🎵 [{sceneName}] Stopping music");
                return;
            }

            // Option 2: Continue existing music from previous scene
            if (AudioManager.Instance.IsMusicContinuing() && !forceMusicChange)
            {
                Debug.Log($"🎵 [{sceneName}] Continuing music from previous scene");
                return;
            }

            // Option 3: Play this scene's music
            if (sceneAmbientMusic != null)
            {
                if (AudioManager.Instance.IsPlaying())
                {
                    // Smooth transition to new track
                    AudioManager.Instance.CrossfadeToTrack(sceneAmbientMusic, $"{sceneName} Ambience");
                    Debug.Log($"🎵 [{sceneName}] Crossfading to scene music");
                }
                else
                {
                    // No music playing, start immediately
                    AudioManager.Instance.PlayMusicTrack(sceneAmbientMusic, $"{sceneName} Ambience");
                    Debug.Log($"🎵 [{sceneName}] Starting scene music");
                }
            }
        }

        /// <summary>
        /// Public method to override music mid-scene
        /// </summary>
        public void ChangeSceneMusic(AudioClip newClip, string trackName = "")
        {
            if (newClip == null)
            {
                Debug.LogWarning("Cannot change to null audio clip");
                return;
            }

            AudioManager.Instance.CrossfadeToTrack(newClip, trackName);
        }

        /// <summary>
        /// Fade out and stop music
        /// </summary>
        public void FadeOutMusic(float duration = 1.5f)
        {
            AudioManager.Instance.StopMusic(duration);
        }

        /// <summary>
        /// Immediately stop music
        /// </summary>
        public void StopMusic()
        {
            AudioManager.Instance.StopMusic(0);
        }

        /// <summary>
        /// Check if music from previous scene is still playing
        /// </summary>
        public bool IsBackgroundMusicPlaying()
        {
            return AudioManager.Instance.IsMusicContinuing();
        }
    }
}
