using System;
using UnityEngine;

namespace Velinor.Core
{
    /// <summary>
    /// Manager for the Codex system. Singleton pattern for global access.
    /// </summary>
    public class CodexManager : MonoBehaviour
    {
        [SerializeField] private CodexState codexState = new CodexState();
        
        public static CodexManager Instance { get; private set; }
        public CodexState State => codexState;

        // Events for system integration
        public event Action<string> OnTagAdded;
        public event Action<string> OnGlyphResolved;
        public event Action<float> OnResonanceChanged;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
            if (Application.isPlaying) DontDestroyOnLoad(gameObject);
        }

        /// <summary>
        /// Public method to add emotional tag and broadcast change.
        /// </summary>
        public void AddEmotionalTag(string tag)
        {
            codexState.AddTag(tag);
            OnTagAdded?.Invoke(tag);
            OnResonanceChanged?.Invoke(codexState.ResonanceLevel);
        }

        /// <summary>
        /// Public method to resolve glyph and broadcast change.
        /// </summary>
        public void ResolveGlyph(string glyphId)
        {
            codexState.ResolveGlyph(glyphId);
            OnGlyphResolved?.Invoke(glyphId);
            OnResonanceChanged?.Invoke(codexState.ResonanceLevel);
        }

        /// <summary>
        /// Query: Can the player activate a pedestal?
        /// </summary>
        public bool CanActivatePedestal(Pedestal pedestal)
        {
            if (pedestal.RequiredTags.Count == 0)
                return true; // No gate

            return codexState.HasAllTags(pedestal.RequiredTags);
        }
    }
}
