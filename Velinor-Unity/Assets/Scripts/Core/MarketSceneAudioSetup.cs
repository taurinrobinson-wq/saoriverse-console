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
            audioManager = FindObjectOfType<AudioManager>();
            
            if (audioManager == null)
            {
                // Create new if not found
                GameObject audioManagerObj = new GameObject("AudioManager");
                audioManager = audioManagerObj.AddComponent<AudioManager>();
                Debug.LogWarning("⚠️ AudioManager not found in scene. Creating new one.");
            }
        }

        private void Start()
        {
            // Start Glass Horizon as market atmosphere
            StartMarketSoundscape();
        }

        /// <summary>
        /// Begin playing Glass Horizon for market scene
        /// This is called automatically on Start()
        /// </summary>
        public void StartMarketSoundscape()
        {
            audioManager.PlayMarketSoundscape();
            Debug.Log("🎵 Market soundscape started: Glass Horizon (looping)");
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
