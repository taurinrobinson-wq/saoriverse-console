using System;
using System.Collections.Generic;
using UnityEngine;

namespace Velinor.Core
{
    /// <summary>
    /// Represents the player's emotional state and Codex resonance.
    /// Emotional tags drive pedestal activation and glyph chamber access.
    /// </summary>
    [System.Serializable]
    public class CodexState
    {
        [SerializeField] private List<string> activeTags = new List<string>();
        [SerializeField] private string lastTriggeredPedestalId;
        [SerializeField] private List<string> resolvedGlyphIds = new List<string>();
        [SerializeField] private float resonanceLevel = 0f; // 0-1 scale
        
        public List<string> ActiveTags => activeTags;
        public string LastTriggeredPedestalId => lastTriggeredPedestalId;
        public List<string> ResolvedGlyphIds => resolvedGlyphIds;
        public float ResonanceLevel => resonanceLevel;

        /// <summary>
        /// Adds an emotional tag to the player's Codex.
        /// Triggers resonance recalculation and pedestal checks.
        /// </summary>
        public void AddTag(string emotionalTag)
        {
            if (!activeTags.Contains(emotionalTag))
            {
                activeTags.Add(emotionalTag);
                RecalculateResonance();
            }
        }

        /// <summary>
        /// Removes an emotional tag.
        /// </summary>
        public void RemoveTag(string emotionalTag)
        {
            activeTags.Remove(emotionalTag);
            RecalculateResonance();
        }

        /// <summary>
        /// Checks if a specific emotional tag is active.
        /// </summary>
        public bool HasTag(string emotionalTag)
        {
            return activeTags.Contains(emotionalTag);
        }

        /// <summary>
        /// Checks if all required tags are present.
        /// </summary>
        public bool HasAllTags(List<string> requiredTags)
        {
            foreach (var tag in requiredTags)
            {
                if (!activeTags.Contains(tag))
                    return false;
            }
            return true;
        }

        /// <summary>
        /// Checks if any of the required tags are present.
        /// </summary>
        public bool HasAnyTag(List<string> requiredTags)
        {
            foreach (var tag in requiredTags)
            {
                if (activeTags.Contains(tag))
                    return true;
            }
            return false;
        }

        /// <summary>
        /// Marks a glyph as resolved and updates resonance.
        /// </summary>
        public void ResolveGlyph(string glyphId)
        {
            if (!resolvedGlyphIds.Contains(glyphId))
            {
                resolvedGlyphIds.Add(glyphId);
                RecalculateResonance();
            }
        }

        /// <summary>
        /// Records a pedestal interaction.
        /// </summary>
        public void SetLastTriggeredPedestal(string pedestalId)
        {
            lastTriggeredPedestalId = pedestalId;
        }

        /// <summary>
        /// Recalculates resonance based on active tags and resolved glyphs.
        /// Resonance = (resolved glyphs / total possible) * (active tags / max expected tags)
        /// </summary>
        private void RecalculateResonance()
        {
            // Simple formula: more tags and more glyphs = higher resonance
            float tagResonance = Mathf.Clamp01(activeTags.Count / 8f); // Assume ~8 max tags
            float glyphResonance = Mathf.Clamp01(resolvedGlyphIds.Count / 118f); // 118 total glyphs
            
            resonanceLevel = (tagResonance * 0.5f) + (glyphResonance * 0.5f);
        }

        /// <summary>
        /// Serializes the Codex state to JSON.
        /// </summary>
        public string Serialize()
        {
            return UnityEngine.JsonUtility.ToJson(this, prettyPrint: true);
        }

        /// <summary>
        /// Deserializes from JSON.
        /// </summary>
        public static CodexState Deserialize(string json)
        {
            return UnityEngine.JsonUtility.FromJson<CodexState>(json);
        }
    }

    }