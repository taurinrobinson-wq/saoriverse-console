using System.Collections.Generic;
using UnityEngine;
using Velinor.Core;
using Velinor.UI.Codex;

namespace Velinor.Testing
{
    /// <summary>
    /// Helper script to generate test memory fragments for testing the Mind Log UI.
    /// This creates test data at runtime for development/testing purposes.
    /// 
    /// Usage: Attach this to a GameObject in your scene and call InitializeTestMemories()
    /// from the CodexViewController or another initialization script.
    /// </summary>
    public class MemoryFragmentTestSetup : MonoBehaviour
    {
        [SerializeField] private MemoryGridUI memoryGridUI;
        
        private List<MemoryFragment> testFragments = new List<MemoryFragment>();

        /// <summary>
        /// Initializes test memory fragments and populates the grid.
        /// Call this when you want to load test data into the Mind Log Primary view.
        /// </summary>
        public void InitializeTestMemories()
        {
            if (memoryGridUI == null)
            {
                Debug.LogError("[MemoryFragmentTestSetup] MemoryGridUI reference is not set.");
                return;
            }

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

            // Add a few more test memories so the grid looks populated
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

            // Populate the grid
            if (memoryGridUI != null)
            {
                memoryGridUI.PopulateGrid(testFragments);
                Debug.Log($"[MemoryFragmentTestSetup] Populated grid with {testFragments.Count} test memory fragments.");
            }
        }

        /// <summary>
        /// Creates a MemoryFragment instance with the specified properties.
        /// Note: This creates the fragment in memory only. For persistent storage,
        /// you would need to save this as a ScriptableObject asset.
        /// </summary>
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
            fragment.linkedScene = "desert_encounter";
            
            // Create a placeholder icon (white square)
            fragment.icon = CreatePlaceholderIcon(displayName);
            
            Debug.Log($"[MemoryFragmentTestSetup] Created test fragment: {fragmentID}");
            
            return fragment;
        }

        /// <summary>
        /// Creates a simple placeholder icon texture.
        /// In production, you would use actual sprite assets.
        /// </summary>
        private Sprite CreatePlaceholderIcon(string label)
        {
            // Create a simple 256x256 white square texture
            Texture2D texture = new Texture2D(256, 256, TextureFormat.RGBA32, false);
            
            // Fill with a light blue color to indicate test data
            Color testColor = new Color(0.3f, 0.7f, 1f, 1f);
            Color[] pixels = new Color[256 * 256];
            
            for (int i = 0; i < pixels.Length; i++)
            {
                pixels[i] = testColor;
            }
            
            texture.SetPixels(pixels);
            texture.Apply();
            
            // Create a sprite from the texture
            Sprite sprite = Sprite.Create(texture, new Rect(0, 0, 256, 256), new Vector2(0.5f, 0.5f), 100);
            sprite.name = $"Icon_{label}";
            
            return sprite;
        }
    }
}
