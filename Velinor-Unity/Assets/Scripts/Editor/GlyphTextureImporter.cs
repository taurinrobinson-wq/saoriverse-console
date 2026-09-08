using UnityEngine;
using UnityEditor;

namespace Velinor.Core.Editor
{
    /// <summary>
    /// Configures texture import settings for glyph textures to support transparency.
    /// </summary>
    public class GlyphTextureImporter
    {
        [MenuItem("Window/Velinor/Configure Glyph Textures")]
        public static void ConfigureGlyphTextures()
        {
            string[] texturePaths = new string[]
            {
                "Assets/Graphics/Glyphs/archived_full-color_glyphs/Glyph_Ancestral_Record_nobg_noped.png",
                "Assets/Graphics/Glyphs/archived_full-color_glyphs/glyph_Covenant_Flame_nobg_new.png",
                "Assets/Graphics/Glyphs/archived_full-color_glyphs/glyph_Echo_Communion_nobg_new.png",
                "Assets/Graphics/Glyphs/archived_full-color_glyphs/glyph_Echoed_Breath_nobg.png",
                "Assets/Graphics/Glyphs/archived_full-color_glyphs/Glyph_Infrasensory_Oblivion_nobg_new2.png"
            };

            Debug.Log("[GlyphTextureImporter] Configuring texture import settings...");

            foreach (string texturePath in texturePaths)
            {
                TextureImporter importer = AssetImporter.GetAtPath(texturePath) as TextureImporter;

                if (importer == null)
                {
                    Debug.LogWarning($"[GlyphTextureImporter] Could not find texture: {texturePath}");
                    continue;
                }

                // Configure for transparency
                importer.textureType = TextureImporterType.Default;
                importer.alphaSource = TextureImporterAlphaSource.FromInput;
                importer.alphaIsTransparency = true;
                importer.wrapMode = TextureWrapMode.Clamp;
                importer.filterMode = FilterMode.Bilinear;

                // Ensure compression allows alpha
                TextureImporterPlatformSettings platformSettings = importer.GetDefaultPlatformTextureSettings();
                platformSettings.format = TextureImporterFormat.RGBA32;
                importer.SetPlatformTextureSettings(platformSettings);

                EditorUtility.SetDirty(importer);
                importer.SaveAndReimport();

                Debug.Log($"[GlyphTextureImporter] Configured: {texturePath}");
            }

            AssetDatabase.Refresh();
            Debug.Log("[GlyphTextureImporter] Texture configuration complete!");
        }
    }
}
