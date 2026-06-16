using System;
using System.Collections.Generic;
using UnityEngine;

namespace Velinor.Core
{
    /// <summary>
    /// Represents a pedestal in the world — the physical manifestation of a glyph chamber.
    /// Pedestals can be dormant, flickering (partly resonant), or active (fully resonant).
    /// </summary>
    public class Pedestal : MonoBehaviour
    {
        public string pedestalId = "pedestal_001";
        public string linkedGlyphId = "glyph_001";
        public List<string> requiredTags = new List<string>();
        public float activationRadius = 5f;
        [SerializeField] private PedestalState currentState = PedestalState.Dormant;

        // Visual references
        [SerializeField] private Transform glyphDisplay; // Where the glyph symbol appears
        public Light pedestalLight;
        public ParticleSystem activationParticles;

        // Audio
        [SerializeField] private AudioSource resonanceAudio;

        private CodexManager codexManager;
        private float distanceToPlayer;
        private bool hasBeenActivated = false;

        public string PedestalId => pedestalId;
        public string LinkedGlyphId => linkedGlyphId;
        public List<string> RequiredTags => requiredTags;
        public PedestalState CurrentState => currentState;
        public bool HasBeenActivated => hasBeenActivated;

        // Events
        public event Action<Pedestal> OnActivated;
        public event Action<Pedestal> OnFlickered;

        public enum PedestalState
        {
            Dormant,  // No resonance, no glyph visible
            Flickering, // Partial resonance, faint glyph
            Active,   // Full resonance, glyph bright and interactive
            Spent     // Glyph resolved, pedestal stable
        }

        private void OnEnable()
        {
            codexManager = CodexManager.Instance;
            if (codexManager != null)
            {
                codexManager.OnTagAdded += HandleTagAdded;
                codexManager.OnGlyphResolved += HandleGlyphResolved;
            }
            UpdateState();
        }

        private void OnDisable()
        {
            if (codexManager != null)
            {
                codexManager.OnTagAdded -= HandleTagAdded;
                codexManager.OnGlyphResolved -= HandleGlyphResolved;
            }
        }

        private void Update()
        {
            UpdateDistanceToPlayer();
            UpdateVisualState();
        }

        /// <summary>
        /// Calculates distance to player and checks if within activation radius.
        /// </summary>
        private void UpdateDistanceToPlayer()
        {
            var player = GameObject.FindGameObjectWithTag("Player");
            if (player != null)
            {
                distanceToPlayer = Vector3.Distance(transform.position, player.transform.position);
            }
        }

        /// <summary>
        /// Updates the pedestal's state based on Codex resonance.
        /// </summary>
        private void UpdateState()
        {
            if (hasBeenActivated)
            {
                SetState(PedestalState.Spent);
                return;
            }

            if (codexManager == null || codexManager.State.ResolvedGlyphIds.Contains(linkedGlyphId))
            {
                SetState(PedestalState.Spent);
                return;
            }

            // Check if player can activate
            bool canActivate = codexManager.CanActivatePedestal(this);

            if (canActivate && distanceToPlayer < activationRadius)
            {
                SetState(PedestalState.Active);
            }
            else if (canActivate && distanceToPlayer < activationRadius * 1.5f)
            {
                SetState(PedestalState.Flickering);
            }
            else
            {
                SetState(PedestalState.Dormant);
            }
        }

        /// <summary>
        /// Sets the pedestal state and triggers visual updates.
        /// </summary>
        private void SetState(PedestalState newState)
        {
            if (currentState == newState)
                return;

            currentState = newState;

            switch (currentState)
            {
                case PedestalState.Dormant:
                    SetDormantVisuals();
                    break;
                case PedestalState.Flickering:
                    SetFlickeringVisuals();
                    OnFlickered?.Invoke(this);
                    break;
                case PedestalState.Active:
                    SetActiveVisuals();
                    OnActivated?.Invoke(this);
                    break;
                case PedestalState.Spent:
                    SetSpentVisuals();
                    break;
            }
        }

        /// <summary>
        /// Dormant: dim, no particles, faint audio
        /// </summary>
        private void SetDormantVisuals()
        {
            if (pedestalLight != null)
                pedestalLight.intensity = 0.2f;

            if (glyphDisplay != null)
                glyphDisplay.gameObject.SetActive(false);

            if (activationParticles != null)
                activationParticles.Stop();
        }

        /// <summary>
        /// Flickering: pulsing light, faint glyph, soft audio
        /// </summary>
        private void SetFlickeringVisuals()
        {
            if (pedestalLight != null)
                pedestalLight.intensity = Mathf.PingPong(Time.time * 2f, 0.5f) + 0.3f;

            if (glyphDisplay != null)
            {
                glyphDisplay.gameObject.SetActive(true);
                glyphDisplay.GetComponent<CanvasGroup>().alpha = 0.5f;
            }

            if (resonanceAudio != null && !resonanceAudio.isPlaying)
            {
                resonanceAudio.volume = 0.3f;
                resonanceAudio.Play();
            }
        }

        /// <summary>
        /// Active: bright light, full glyph, strong audio, particles
        /// </summary>
        private void SetActiveVisuals()
        {
            if (pedestalLight != null)
                pedestalLight.intensity = 1f;

            if (glyphDisplay != null)
            {
                glyphDisplay.gameObject.SetActive(true);
                glyphDisplay.GetComponent<CanvasGroup>().alpha = 1f;
            }

            if (activationParticles != null)
                activationParticles.Play();

            if (resonanceAudio != null && !resonanceAudio.isPlaying)
            {
                resonanceAudio.volume = 0.8f;
                resonanceAudio.Play();
            }
        }

        /// <summary>
        /// Spent: stable, warm glow, no particles
        /// </summary>
        private void SetSpentVisuals()
        {
            if (pedestalLight != null)
            {
                pedestalLight.intensity = 0.5f;
                pedestalLight.color = new Color(0.8f, 0.7f, 0.5f); // Warm tone
            }

            if (glyphDisplay != null)
                glyphDisplay.gameObject.SetActive(true);

            if (activationParticles != null)
                activationParticles.Stop();

            if (resonanceAudio != null)
                resonanceAudio.Stop();
        }

        /// <summary>
        /// Continuously update visual based on state.
        /// </summary>
        private void UpdateVisualState()
        {
            if (currentState == PedestalState.Dormant || currentState == PedestalState.Spent)
                return;

            // Update flickering pulsing
            if (currentState == PedestalState.Flickering && pedestalLight != null)
            {
                pedestalLight.intensity = Mathf.PingPong(Time.time * 2f, 0.5f) + 0.3f;
            }
        }

        /// <summary>
        /// Called when player interacts with the pedestal.
        /// </summary>
        public void Activate()
        {
            if (currentState != PedestalState.Active)
                return;

            hasBeenActivated = true;
            SetState(PedestalState.Spent);

            // Trigger glyph chamber transition
            var glyphChamberManager = FindAnyObjectByType<GlyphChamberManager>();
            if (glyphChamberManager != null)
            {
                glyphChamberManager.EnterChamber(linkedGlyphId);
            }

            // Update Codex
            CodexManager.Instance.ResolveGlyph(linkedGlyphId);
            CodexManager.Instance.State.SetLastTriggeredPedestal(pedestalId);
        }

        /// <summary>
        /// Called when a tag is added to the Codex.
        /// Updates state in case this pedestal is now activatable.
        /// </summary>
        private void HandleTagAdded(string tag)
        {
            UpdateState();
        }

        /// <summary>
        /// Called when a glyph is resolved elsewhere.
        /// Updates state in case this is the resolved glyph.
        /// </summary>
        private void HandleGlyphResolved(string glyphId)
        {
            if (glyphId == linkedGlyphId)
            {
                UpdateState();
            }
        }

        /// <summary>
        /// Draws debug gizmos in the editor.
        /// </summary>
        private void OnDrawGizmosSelected()
        {
            Gizmos.color = Color.yellow;
            Gizmos.DrawWireSphere(transform.position, activationRadius);

            Gizmos.color = Color.red;
            Gizmos.DrawWireSphere(transform.position, activationRadius * 1.5f);
        }
    }
}
