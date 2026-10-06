using System.Collections.Generic;
using UnityEngine;
using Velinor.Core;
using Velinor.UI.Codex;

namespace Velinor.Testing
{
    /// <summary>
    /// Manual test initialization button for Mind Log testing.
    /// Attach this to a button in your scene to manually load test memories.
    /// </summary>
    public class ManualMemoryTestInitializer : MonoBehaviour
    {
        [SerializeField] private MemoryGridUI memoryGridUI;
        
        private List<MemoryFragment> testFragments = new List<MemoryFragment>();

        /// <summary>
        /// Call this method to manually populate the grid with test data.
        /// Attach this to a button's OnClick event.
        /// </summary>
        public void LoadTestMemories()
        {
            if (memoryGridUI == null)
            {
                Debug.LogError("[ManualMemoryTestInitializer] MemoryGridUI reference is not set. Cannot load test memories.");
                return;
            }

            Debug.Log("[ManualMemoryTestInitializer] Loading test memories...");
            
            testFragments.Clear();
            
            // Create the Saori meeting test fragment
            MemoryFragment saoriMemory = CreateMemoryFragment(
                fragmentID: "memory_saori_desert_encounter",
                displayName: "Desert Encounter",
                shortSynopsis: "A mysterious meeting",
                expandedText: "In the vast desert expanse, you encountered Saori. Her presence was both " +
                              "enigmatic and captivating, marked by an air of quiet determination. The conversation " +
                              "revealed layers of complexity—ancient knowledge intertwined with personal struggle. " +
                              "As the sun cast long shadows across the sand, you felt the weight of unspoken truths " +
                              "passing between you. This meeting would prove to be a turning point in your understanding " +
                              "of the world and the forces that shape it."
            );
            testFragments.Add(saoriMemory);

            // Add more test memories
            MemoryFragment testMemory2 = CreateMemoryFragment(
                fragmentID: "memory_ravi_encounter",
                displayName: "Ravi's Story",
                shortSynopsis: "Burden and legacy",
                expandedText: "Ravi spoke of the weight that familial duty places upon the shoulders. " +
                              "Their words carried the echo of sacrifice, of choices made not for oneself but for those who came before. " +
                              "In the marketplace, surrounded by the chaos of daily life, you found yourself understanding the quiet strength " +
                              "required to bear such responsibility."
            );
            testFragments.Add(testMemory2);

            MemoryFragment testMemory3 = CreateMemoryFragment(
                fragmentID: "memory_nima_insight",
                displayName: "Nima's Wisdom",
                shortSynopsis: "The path forward",
                expandedText: "Nima's guidance illuminated aspects of your journey you hadn't yet considered. " +
                              "With the clarity of someone who has walked many paths, they offered perspective on the choices " +
                              "that lay before you. Their words were a compass in the fog of uncertainty."
            );
            testFragments.Add(testMemory3);

            // Additional test memories to fill the grid
            MemoryFragment testMemory4 = CreateMemoryFragment(
                fragmentID: "memory_moment_of_clarity",
                displayName: "Moment of Clarity",
                shortSynopsis: "A profound realization",
                expandedText: "In a quiet moment, everything suddenly made sense. The pieces of your journey " +
                              "fell into place, revealing a pattern you hadn't noticed before. This clarity, though fleeting, " +
                              "would shape every decision that followed."
            );
            testFragments.Add(testMemory4);

            MemoryFragment testMemory5 = CreateMemoryFragment(
                fragmentID: "memory_ancient_code",
                displayName: "Ancient Code",
                shortSynopsis: "Symbols and secrets",
                expandedText: "The ancient symbols hold meaning beyond the words inscribed upon stone. " +
                              "Each glyph is a key to understanding, a bridge between worlds and times. To decode them " +
                              "is to touch the very fabric of reality itself."
            );
            testFragments.Add(testMemory5);

            // Populate the grid
            memoryGridUI.PopulateGrid(testFragments);
            Debug.Log($"[ManualMemoryTestInitializer] Successfully loaded {testFragments.Count} test memory fragments!");
        }

        private MemoryFragment CreateMemoryFragment(string fragmentID, string displayName, 
                                                     string shortSynopsis, string expandedText)
        {
            MemoryFragment fragment = ScriptableObject.CreateInstance<MemoryFragment>();
            
            fragment.fragmentID = fragmentID;
            fragment.displayName = displayName;
            fragment.shortSynopsis = shortSynopsis;
            fragment.expandedText = expandedText;
            fragment.tags = new List<string> { "encounter", "npc" };
            fragment.isDeduction = false;
            fragment.linkedScene = "test_scene";
            
            fragment.icon = CreatePlaceholderIcon(displayName);
            
            return fragment;
        }

        private Sprite CreatePlaceholderIcon(string label)
        {
            Texture2D texture = new Texture2D(256, 256, TextureFormat.RGBA32, false);
            
            // Different colors for different memories
            Color testColor = GetColorForMemory(label);
            Color[] pixels = new Color[256 * 256];
            
            for (int i = 0; i < pixels.Length; i++)
            {
                pixels[i] = testColor;
            }
            
            texture.SetPixels(pixels);
            texture.Apply();
            
            Sprite sprite = Sprite.Create(texture, new Rect(0, 0, 256, 256), new Vector2(0.5f, 0.5f), 100);
            sprite.name = $"Icon_{label}";
            
            return sprite;
        }

        private Color GetColorForMemory(string label)
        {
            // Return different colors for visual variety
            return label switch
            {
                "Desert Encounter" => new Color(0.8f, 0.5f, 0.2f, 1f),      // Orange-brown for desert
                "Ravi's Story" => new Color(0.6f, 0.2f, 0.2f, 1f),          // Dark red for burden
                "Nima's Wisdom" => new Color(0.2f, 0.6f, 0.8f, 1f),         // Blue for wisdom
                "Moment of Clarity" => new Color(1f, 0.9f, 0.3f, 1f),       // Gold for clarity
                "Ancient Code" => new Color(0.4f, 0.2f, 0.6f, 1f),          // Purple for mystery
                _ => new Color(0.5f, 0.5f, 0.5f, 1f)                        // Gray default
            };
        }
    }
}
