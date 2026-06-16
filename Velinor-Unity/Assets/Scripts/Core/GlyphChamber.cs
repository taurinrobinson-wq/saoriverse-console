using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Velinor.Core
{
    /// <summary>
    /// Manages glyph chamber transitions and sequences.
    /// When a pedestal is activated, this system transitions the player into the chamber,
    /// plays the emotional sequence, and returns them to the world changed.
    /// </summary>
    public class GlyphChamberManager : MonoBehaviour
    {
        [SerializeField] private string chamberScenePrefix = "GlyphChamber_";
        [SerializeField] private float transitionDuration = 2f;
        [SerializeField] private CanvasGroup fadeCanvasGroup; // For fade transitions

        private string currentChamberGlyphId;
        private bool isInChamber = false;

        public static GlyphChamberManager Instance { get; private set; }

        // Events
        public event Action<string> OnChamberEntered;
        public event Action<string> OnChamberExited;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
        }

        /// <summary>
        /// Initiates a glyph chamber sequence.
        /// </summary>
        public void EnterChamber(string glyphId)
        {
            if (isInChamber)
                return;

            currentChamberGlyphId = glyphId;
            StartCoroutine(ChamberTransitionCoroutine(glyphId));
        }

        /// <summary>
        /// Coroutine that handles the chamber transition sequence.
        /// </summary>
        private IEnumerator ChamberTransitionCoroutine(string glyphId)
        {
            isInChamber = true;
            OnChamberEntered?.Invoke(glyphId);

            // Fade out the world
            yield return StartCoroutine(FadeOut(transitionDuration * 0.5f));

            // Load chamber scene additively
            string chamberSceneName = chamberScenePrefix + glyphId;
            AsyncOperation asyncLoad = SceneManager.LoadSceneAsync(chamberSceneName, LoadSceneMode.Additive);
            yield return new WaitUntil(() => asyncLoad.isDone);

            // Fade in the chamber
            yield return StartCoroutine(FadeIn(transitionDuration * 0.5f));

            // Play chamber sequence (configurable)
            yield return StartCoroutine(PlayChamberSequence(glyphId));

            // Fade out chamber
            yield return StartCoroutine(FadeOut(transitionDuration * 0.5f));

            // Unload chamber scene
            SceneManager.UnloadSceneAsync(chamberSceneName);
            yield return new WaitForSeconds(0.5f);

            // Fade in the world
            yield return StartCoroutine(FadeIn(transitionDuration * 0.5f));

            isInChamber = false;
            OnChamberExited?.Invoke(glyphId);
        }

        /// <summary>
        /// Plays the chamber-specific sequence (walking, witnessing, Codex pulse).
        /// Can be overridden per chamber or data-driven.
        /// </summary>
        private IEnumerator PlayChamberSequence(string glyphId)
        {
            // This is a placeholder. In production, you'd have per-chamber logic:
            // - Move camera along a path
            // - Trigger emotional audio cues
            // - Display glyph symbolism
            // - Update player emotional state

            Debug.Log($"Playing chamber sequence for glyph: {glyphId}");

            // Simulate chamber duration (2-5 seconds typically)
            yield return new WaitForSeconds(3f);

            // Add emotional resonance effect (visual/audio feedback)
            // This would trigger the Codex UI to show the glyph meaning
        }

        /// <summary>
        /// Fade out world/chamber
        /// </summary>
        private IEnumerator FadeOut(float duration)
        {
            if (fadeCanvasGroup == null)
                yield break;

            float elapsed = 0f;
            while (elapsed < duration)
            {
                elapsed += Time.deltaTime;
                fadeCanvasGroup.alpha = Mathf.Clamp01(elapsed / duration);
                yield return null;
            }
            fadeCanvasGroup.alpha = 1f;
        }

        /// <summary>
        /// Fade in world/chamber
        /// </summary>
        private IEnumerator FadeIn(float duration)
        {
            if (fadeCanvasGroup == null)
                yield break;

            float elapsed = 0f;
            while (elapsed < duration)
            {
                elapsed += Time.deltaTime;
                fadeCanvasGroup.alpha = 1f - Mathf.Clamp01(elapsed / duration);
                yield return null;
            }
            fadeCanvasGroup.alpha = 0f;
        }

        /// <summary>
        /// Exit chamber prematurely (optional for cancellation)
        /// </summary>
        public void ExitChamber()
        {
            if (isInChamber)
            {
                StopAllCoroutines();
                isInChamber = false;
                OnChamberExited?.Invoke(currentChamberGlyphId);
            }
        }
    }

    /// <summary>
    /// Per-chamber controller. Each glyph chamber scene can have one of these
    /// to customize the sequence and emotional beats.
    /// </summary>
    public class ChamberController : MonoBehaviour
    {
        [SerializeField] private string glyphId;
        [SerializeField] private float sequenceDuration = 3f;
        [SerializeField] private List<ChamberBeat> emotionalBeats = new List<ChamberBeat>();

        public string GlyphId => glyphId;

        [System.Serializable]
        public class ChamberBeat
        {
            public float timing; // Time in sequence
            public string description; // What happens at this beat
            public string emotionalTag; // Tag to add or reinforce
        }

        private void Start()
        {
            StartCoroutine(PlaySequence());
        }

        private IEnumerator PlaySequence()
        {
            foreach (var beat in emotionalBeats)
            {
                yield return new WaitForSeconds(beat.timing);
                ExecuteBeat(beat);
            }

            yield return new WaitForSeconds(sequenceDuration);
        }

        private void ExecuteBeat(ChamberBeat beat)
        {
            Debug.Log($"Chamber beat: {beat.description} ({beat.emotionalTag})");
            // Add visual/audio effects here
        }
    }
}
