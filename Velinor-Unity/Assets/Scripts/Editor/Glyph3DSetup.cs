using UnityEngine;
using UnityEditor;

namespace Velinor.Core.Editor
{
    /// <summary>
    /// Master setup for 3D glyph creation - runs all configuration and generation in sequence.
    /// </summary>
    public class Glyph3DSetup
    {
        [MenuItem("Window/Velinor/Setup 2D Glyphs (Complete)")]
        public static void SetupAll()
        {
            Debug.Log("════════════════════════════════════════════════════════════");
            Debug.Log("  [2D Glyph Setup] Starting complete 2D glyph setup...");
            Debug.Log("════════════════════════════════════════════════════════════");

            // Step 1: Configure textures (already done during prefab creation)
            Debug.Log("\n[Setup Step 1/1] Creating 2D glyph sprite prefabs...");
            Glyph3DPrefabCreator.CreateGlyphPrefabs();

            Debug.Log("\n════════════════════════════════════════════════════════════");
            Debug.Log("  [2D Glyph Setup] ✓ Setup complete!");
            Debug.Log("  Prefabs created in: Assets/Prefabs/Glyphs2D/");
            Debug.Log("════════════════════════════════════════════════════════════\n");
        }
    }
}
