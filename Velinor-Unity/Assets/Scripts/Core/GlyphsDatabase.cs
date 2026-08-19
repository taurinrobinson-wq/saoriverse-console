using UnityEngine;
using System.Collections.Generic;

/// <summary>
/// Simple glyph database that loads glyph sprites for the codex system
/// Edit this to add/remove glyphs for testing
/// </summary>
public class GlyphsDatabase : MonoBehaviour
{
    [System.Serializable]
    public class GlyphData
    {
        public string name;
        public Sprite sprite;
        public string description;
    }

    private static GlyphsDatabase _instance;

    [SerializeField]
    private List<GlyphData> availableGlyphs = new List<GlyphData>();

    private void Awake()
    {
        if (_instance == null)
        {
            _instance = this;
            DontDestroyOnLoad(gameObject);
            LoadGlyphsFromResources();
        }
        else
        {
            Destroy(gameObject);
        }
    }

    /// <summary>
    /// Loads glyphs from Resources folder - you can add them manually in Inspector instead
    /// </summary>
    private void LoadGlyphsFromResources()
    {
        // Try to load from Resources/Glyphs folder if it exists
        Sprite[] loadedSprites = Resources.LoadAll<Sprite>("Glyphs");
        
        if (loadedSprites.Length == 0)
        {
            Debug.LogWarning("[Glyphs] No glyphs found in Resources/Glyphs! Assign them manually in Inspector.");
        }
        else
        {
            foreach (Sprite sprite in loadedSprites)
            {
                availableGlyphs.Add(new GlyphData
                {
                    name = sprite.name,
                    sprite = sprite,
                    description = "A glyph from your collection"
                });
            }
            Debug.Log($"[Glyphs] Loaded {availableGlyphs.Count} glyphs from Resources");
        }
    }

    public static List<GlyphData> GetAllGlyphs()
    {
        if (_instance == null)
        {
            Debug.LogError("[Glyphs] GlyphsDatabase not found in scene!");
            return new List<GlyphData>();
        }
        return _instance.availableGlyphs;
    }

    public static Sprite GetGlyphSprite(string glyphName)
    {
        foreach (var glyph in GetAllGlyphs())
        {
            if (glyph.name == glyphName)
                return glyph.sprite;
        }
        return null;
    }

    [ContextMenu("Print Available Glyphs")]
    public void PrintGlyphs()
    {
        Debug.Log($"[Glyphs] Total glyphs available: {availableGlyphs.Count}");
        foreach (var glyph in availableGlyphs)
        {
            Debug.Log($"  - {glyph.name}");
        }
    }
}
