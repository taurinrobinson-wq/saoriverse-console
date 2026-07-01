using UnityEngine;

namespace Velinor.Core
{
    /// <summary>
    /// MarketSceneAudioSetup - Integrates AudioManager with MarketSceneSetup
    /// 
    /// This script automatically starts Glass Horizon music when the market scene loads
    /// Call this from Awake/Start or manually trigger PlayMarketSoundscape()
    /// </summary>
    public class MarketSceneAudioSetup : MonoBehaviour
    {
        private AudioManager audioManager;

        private void Awake()
        {
            // Find or create AudioManager in scene
            audioManager = FindAnyObjectByType<AudioManager>();
            
            if (audioManager == null)
            {
                // Create new if not found
                GameObject audioManagerObj = new GameObject("AudioManager");
                audioManager = audioManagerObj.AddComponent<AudioManager>();
                Debug.LogWarning("⚠️ AudioManager not found in scene. Creating new one.");
            }
            else
            {
                Debug.Log("✅ AudioManager found in scene");
            }
        }

        private void Start()
        {
            // Start Glass Horizon as market atmosphere
            if (audioManager != null)
            {
                Debug.Log("🎵 MarketSceneAudioSetup.Start() - Calling StartMarketSoundscape()...");
                StartMarketSoundscape();
            }
            else
            {
                Debug.LogError("❌ AudioManager is null! Cannot start market soundscape");
            }
        }

        /// <summary>
        /// Begin playing Glass Horizon for market scene
        /// This is called automatically on Start()
        /// </summary>
        public void StartMarketSoundscape()
        {
            if (audioManager != null)
            {
                Debug.Log("🎵 Calling AudioManager.PlayMarketSoundscape()...");
                audioManager.PlayMarketSoundscape();
                Debug.Log("🎵 Market soundscape started: Glass Horizon (looping)");
            }
            else
            {
                Debug.LogError("❌ Cannot start soundscape - AudioManager is null");
            }
        }

        /// <summary>
        /// Transition to dialogue music (e.g., Simple.ogg for Malrik/Elenya reveal)
        /// </summary>
        public void TransitionToDialogueMusic(string dialogueType = "malrik_elenya")
        {
            switch (dialogueType)
            {
                case "malrik_elenya":
                    // Simple.ogg - charming, out of tune lo-fi for love revelation
                    audioManager.CrossfadeToTrack(
                        Resources.Load<AudioClip>("Music/Simple"),
                        "Simple - Malrik & Elenya Love Revelation"
                    );
                    break;

                case "sorrow":
                    audioManager.CrossfadeToTrack(
                        Resources.Load<AudioClip>("Music/Sorrow-walks"),
                        "Sorrow Walks - Emotional Moment"
                    );
                    break;

                case "mystery":
                    audioManager.CrossfadeToTrack(
                        Resources.Load<AudioClip>("Music/Into-the-codex"),
                        "Into the Codex - Mysterious Discovery"
                    );
                    break;

                case "travel":
                    audioManager.CrossfadeToTrack(
                        Resources.Load<AudioClip>("Music/Traveling-along"),
                        "Traveling Along - Journey"
                    );
                    break;
            }
        }

        /// <summary>
        /// Return to Glass Horizon market soundscape
        /// </summary>
        public void ReturnToMarketSoundscape()
        {
            audioManager.CrossfadeToTrack(
                Resources.Load<AudioClip>("Music/Glass-Horizon"),
                "Glass Horizon - Returning to Market"
            );
        }

        /// <summary>
        /// Access the audio manager directly for advanced control
        /// </summary>
        public AudioManager GetAudioManager() => audioManager;
    }
}
