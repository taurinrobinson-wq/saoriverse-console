using UnityEngine;
using UnityEditor;
using System.IO;
using Velinor.Core;

public class Glyph3DPrefabCreator
{
    private static readonly string[] GlyphNames = new string[]
    {
            "Ancestral_Record",
            "Covenant_Flame",
            "Echo_Communion",
            "Echoed_Breath",
            "Infrasensory_Oblivion"
    };

    private static readonly string[] TexturePaths = new string[]
    {
            "Assets/Graphics/Glyphs/archived_full-color_glyphs/Glyph_Ancestral_Record_nobg_noped.png",
            "Assets/Graphics/Glyphs/archived_full-color_glyphs/glyph_Covenant_Flame_nobg_new.png",
            "Assets/Graphics/Glyphs/archived_full-color_glyphs/glyph_Echo_Communion_nobg_new.png",
            "Assets/Graphics/Glyphs/archived_full-color_glyphs/glyph_Echoed_Breath_nobg.png",
            "Assets/Graphics/Glyphs/archived_full-color_glyphs/Glyph_Infrasensory_Oblivion_nobg_new2.png"
    };

    private const string PrefabOutputPath = "Assets/Prefabs/Glyphs2D";
    private const string GlyphDataOutputPath = "Assets/Data/Glyphs/2D";

    [MenuItem("Window/Velinor/Create 2D Glyph Prefabs")]
    public static void CreateGlyphPrefabs()
    {
        // Create output directories if they don't exist
        if (!Directory.Exists(PrefabOutputPath))
        {
            Directory.CreateDirectory(PrefabOutputPath);
            AssetDatabase.Refresh();
        }

        if (!Directory.Exists(GlyphDataOutputPath))
        {
            Directory.CreateDirectory(GlyphDataOutputPath);
            AssetDatabase.Refresh();
        }

        Debug.Log("[Glyph2D] Starting prefab creation for 5 glyphs...");

        for (int i = 0; i < GlyphNames.Length; i++)
        {
            CreateSingleGlyphPrefab(GlyphNames[i], TexturePaths[i]);
        }

        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
        Debug.Log("[Glyph2D] Completed creating 5 glyph prefabs!");
    }

    private static void CreateSingleGlyphPrefab(string glyphName, string texturePath)
    {
        Debug.Log($"[Glyph2D] Creating prefab for {glyphName}...");

        // Load the texture
        Texture2D texture = AssetDatabase.LoadAssetAtPath<Texture2D>(texturePath);
        if (texture == null)
        {
            Debug.LogError($"[Glyph2D] Failed to load texture: {texturePath}");
            return;
        }

        // Create GlyphData asset
        GlyphData glyphData = CreateGlyphDataAsset(glyphName, texture);
        if (glyphData == null)
        {
            Debug.LogError($"[Glyph2D] Failed to create GlyphData for {glyphName}");
            return;
        }

        // Create a new GameObject
        GameObject glyphObject = new GameObject($"Glyph2D_{glyphName}");
        glyphObject.layer = LayerMask.NameToLayer("Default");

        // Add SpriteRenderer for 2D sprite display
        SpriteRenderer spriteRenderer = glyphObject.AddComponent<SpriteRenderer>();

        // Create and save sprite asset so it persists in the prefab
        Sprite glyphSprite = CreateAndSaveSpriteAsset(glyphName, texture);
        if (glyphSprite != null)
        {
            spriteRenderer.sprite = glyphSprite;
        }
        spriteRenderer.sortingOrder = 5;  // Ensure visibility over background

        // Add 3D SphereCollider as trigger for pickup detection (invisible, handles physics)
        SphereCollider sphereCollider = glyphObject.AddComponent<SphereCollider>();
        // Collider radius should match sprite size: sprite is texture.width / PPU units wide
        // PPU = texture.width / 3, so sprite width = 3 units, radius should be ~1.5f for proper coverage
        sphereCollider.radius = 1.5f;
        sphereCollider.isTrigger = true;

        // Add GlyphObject2D component and assign GlyphData using reflection
        System.Type glyphType = System.Type.GetType("Velinor.Core.GlyphObject2D, Assembly-CSharp");
        if (glyphType != null)
        {
            var glyphComponent = glyphObject.AddComponent(glyphType);

            // Use SerializedObject to assign the GlyphData reference
            SerializedObject so = new SerializedObject(glyphComponent);
            so.FindProperty("glyphData").objectReferenceValue = glyphData;
            so.ApplyModifiedProperties();
        }
        else
        {
            Debug.LogError("Could not find GlyphObject2D type. Ensure it exists in Velinor.Core namespace.");
        }

        // Set scale to 1f for normal sprite size
        glyphObject.transform.localScale = Vector3.one;

        // Create prefab
        string prefabPath = $"{PrefabOutputPath}/Glyph2D_{glyphName}.prefab";
        PrefabUtility.SaveAsPrefabAsset(glyphObject, prefabPath);

        // Clean up temporary GameObject
        Object.DestroyImmediate(glyphObject);

        Debug.Log($"[Glyph2D] Created prefab: {prefabPath}");
    }

    private static GlyphData CreateGlyphDataAsset(string glyphName, Texture2D texture)
    {
        // Create GlyphData asset
        GlyphData glyphData = ScriptableObject.CreateInstance<GlyphData>();
        glyphData.glyphName = glyphName;
        glyphData.description = $"A mysterious glyph: {glyphName.Replace("_", " ")}";

        // Try to convert texture to sprite for icon
        if (texture != null)
        {
            glyphData.icon = CreateAndSaveSpriteAsset(glyphName, texture);
            if (glyphData.icon != null)
            {
                Debug.Log($"[Glyph2D] Assigned icon sprite for {glyphName}");
            }
            else
            {
                Debug.LogWarning($"[Glyph2D] Could not create icon sprite for {glyphName}");
            }
        }

        // Save as asset
        string glyphDataPath = $"{GlyphDataOutputPath}/Glyph_{glyphName}.asset";
        AssetDatabase.CreateAsset(glyphData, glyphDataPath);

        return glyphData;
    }

    private static Sprite CreateAndSaveSpriteAsset(string glyphName, Texture2D texture)
    {
        // Get the texture path
        string texturePath = AssetDatabase.GetAssetPath(texture);

        if (string.IsNullOrEmpty(texturePath))
        {
            Debug.LogError($"[Glyph2D] Could not find texture path for {glyphName}");
            return null;
        }

        // First, try loading as existing sprite (if already imported as sprite type)
        Sprite existingSprite = AssetDatabase.LoadAssetAtPath<Sprite>(texturePath);
        if (existingSprite != null)
        {
            Debug.Log($"[Glyph2D] Loaded existing sprite for {glyphName}");
            return existingSprite;
        }

        Debug.LogWarning($"[Glyph2D] Texture '{texturePath}' is NOT imported as Sprite type.");
        Debug.Log($"[Glyph2D] To fix: Select texture in Project, set TextureType to 'Sprite (2D and UI)', click Apply");

        // Create a runtime sprite from the texture as fallback
        // This won't serialize perfectly but is better than nothing
        Sprite runtimeSprite = Sprite.Create(
            texture,
            new Rect(0, 0, texture.width, texture.height),
            new Vector2(0.5f, 0.5f),
            texture.width / 3f
        );
        runtimeSprite.name = $"Sprite_{glyphName}";

        return runtimeSprite;
    }

    /// <summary>
    /// Clears all generated 2D glyph prefabs (for cleanup/regeneration).
    /// </summary>
    [MenuItem("Window/Velinor/Clear 2D Glyph Prefabs")]
    public static void ClearGlyphPrefabs()
    {
        // Clear prefabs
        if (Directory.Exists(PrefabOutputPath))
        {
            Directory.Delete(PrefabOutputPath, true);
            File.Delete(PrefabOutputPath + ".meta");
        }

        // Clear glyph data
        if (Directory.Exists(GlyphDataOutputPath))
        {
            Directory.Delete(GlyphDataOutputPath, true);
            File.Delete(GlyphDataOutputPath + ".meta");
        }

        // Clear sprite assets
        string spriteDir = "Assets/Graphics/Glyphs/Generated2D";
        if (Directory.Exists(spriteDir))
        {
            Directory.Delete(spriteDir, true);
            File.Delete(spriteDir + ".meta");
        }

        AssetDatabase.Refresh();
        Debug.Log("[Glyph2D] Cleared all 2D glyph assets (prefabs, data, and sprites).");
    }
}
