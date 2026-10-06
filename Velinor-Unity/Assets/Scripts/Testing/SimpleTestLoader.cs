using System.Collections.Generic;
using UnityEngine;
using Velinor.Core;
using Velinor.Testing;

/// <summary>
/// Simple test memory loader - attach to a button to load test data into the memory slot grid.
/// Works with the slot-based system (MemorySlot).
/// </summary>
public class SimpleTestLoader : MonoBehaviour
{
    public void LoadTestMemories()
    {
        Debug.Log("[SimpleTestLoader] Starting to load test memories...");
        
        MemoryGridController gridController = FindObjectOfType<MemoryGridController>();
        if (gridController == null)
        {
            Debug.LogError("[SimpleTestLoader] Could not find MemoryGridController in scene!");
            return;
        }

        List<MemoryFragment> fragments = new List<MemoryFragment>();
        
        // Saori encounter
        var saori = ScriptableObject.CreateInstance<MemoryFragment>();
        saori.fragmentID = "memory_saori_desert_encounter";
        saori.displayName = "Desert Encounter";
        saori.shortSynopsis = "A mysterious meeting";
        saori.expandedText = "In the vast desert expanse, you encountered Saori. Her presence was both enigmatic and captivating, marked by an air of quiet determination. The conversation revealed layers of complexity—ancient knowledge intertwined with personal struggle. As the sun cast long shadows across the sand, you felt the weight of unspoken truths passing between you. This meeting would prove to be a turning point in your understanding of the world and the forces that shape it.";
        saori.icon = CreatePlaceholderIcon(new Color(0.8f, 0.5f, 0.2f, 1f));
        fragments.Add(saori);
        
        // Ravi encounter
        var ravi = ScriptableObject.CreateInstance<MemoryFragment>();
        ravi.fragmentID = "memory_ravi_encounter";
        ravi.displayName = "Ravi's Story";
        ravi.shortSynopsis = "Burden and legacy";
        ravi.expandedText = "Ravi spoke of the weight that familial duty places upon the shoulders. Their words carried the echo of sacrifice, of choices made not for oneself but for those who came before. In the marketplace, surrounded by the chaos of daily life, you found yourself understanding the quiet strength required to bear such responsibility.";
        ravi.icon = CreatePlaceholderIcon(new Color(0.6f, 0.2f, 0.2f, 1f));
        fragments.Add(ravi);
        
        // Nima encounter
        var nima = ScriptableObject.CreateInstance<MemoryFragment>();
        nima.fragmentID = "memory_nima_insight";
        nima.displayName = "Nima's Wisdom";
        nima.shortSynopsis = "The path forward";
        nima.expandedText = "Nima's guidance illuminated aspects of your journey you hadn't yet considered. With the clarity of someone who has walked many paths, they offered perspective on the choices that lay before you. Their words were a compass in the fog of uncertainty.";
        nima.icon = CreatePlaceholderIcon(new Color(0.2f, 0.6f, 0.8f, 1f));
        fragments.Add(nima);

        gridController.PopulateGrid(fragments);
        Debug.Log("[SimpleTestLoader] Successfully loaded " + fragments.Count + " test memories!");
    }

    private Sprite CreatePlaceholderIcon(Color color)
    {
        Texture2D texture = new Texture2D(256, 256, TextureFormat.RGBA32, false);
        Color[] pixels = new Color[256 * 256];
        for (int i = 0; i < pixels.Length; i++)
            pixels[i] = color;
        texture.SetPixels(pixels);
        texture.Apply();
        return Sprite.Create(texture, new Rect(0, 0, 256, 256), new Vector2(0.5f, 0.5f), 100);
    }
}
