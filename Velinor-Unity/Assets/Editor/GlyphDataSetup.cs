using UnityEngine;
using UnityEditor;
using Velinor.Core;
using System.IO;

namespace Velinor.Editor
{
    /// <summary>
    /// Editor script to auto-generate the three core glyph data objects.
    /// Run from menu: Velinor → Setup → Create Glyph Data Objects
    /// </summary>
    public class GlyphDataSetup
    {
        private static readonly string GlyphsFolder = "Assets/Resources/Glyphs";

        [MenuItem("Velinor/Setup/Create Glyph Data Objects")]
        public static void CreateGlyphDataObjects()
        {
            // Ensure folder exists
            if (!AssetDatabase.IsValidFolder(GlyphsFolder))
            {
                AssetDatabase.CreateFolder("Assets/Resources", "Glyphs");
            }

            // Create Sorrow glyph
            CreateGlyphData(
                $"{GlyphsFolder}/GlyphOfSorrow.asset",
                "Sorrow",
                "The glyph of loss and mourning"
            );

            // Create Remembrance glyph
            CreateGlyphData(
                $"{GlyphsFolder}/GlyphOfRemembrance.asset",
                "Remembrance",
                "The glyph of cherished memories"
            );

            // Create Legacy glyph
            CreateGlyphData(
                $"{GlyphsFolder}/GlyphOfLegacy.asset",
                "Legacy",
                "The glyph of lasting impact"
            );

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            Debug.Log("✓ Glyph data objects created successfully!");
            Debug.Log($"  Location: {GlyphsFolder}/");
            EditorUtility.DisplayDialog("Success",
                "Glyph Data Objects created!\n\nLocation: Assets/Resources/Glyphs/",
                "OK");
        }

        private static void CreateGlyphData(string path, string name, string description)
        {
            // Check if already exists
            if (AssetDatabase.LoadAssetAtPath<GlyphData>(path) != null)
            {
                Debug.Log($"⚠ Glyph already exists: {path}");
                return;
            }

            // Create new glyph data
            GlyphData glyphData = ScriptableObject.CreateInstance<GlyphData>();
            glyphData.glyphName = name;
            glyphData.description = description;
            // icon left null - can be assigned manually or via resources if needed

            // Save as asset
            AssetDatabase.CreateAsset(glyphData, path);
            Debug.Log($"✓ Created: {name} → {path}");
        }

        [MenuItem("Velinor/Setup/Delete Glyph Data Objects")]
        public static void DeleteGlyphDataObjects()
        {
            if (EditorUtility.DisplayDialog("Confirm Deletion",
                "Delete all glyph data objects?\n\nThis cannot be undone.",
                "Delete", "Cancel"))
            {
                AssetDatabase.DeleteAsset($"{GlyphsFolder}/GlyphOfSorrow.asset");
                AssetDatabase.DeleteAsset($"{GlyphsFolder}/GlyphOfRemembrance.asset");
                AssetDatabase.DeleteAsset($"{GlyphsFolder}/GlyphOfLegacy.asset");
                AssetDatabase.Refresh();
                Debug.Log("Glyph data objects deleted.");
            }
        }
    }
}
