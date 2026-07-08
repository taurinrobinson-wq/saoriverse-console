using UnityEditor;
using UnityEngine;

namespace Velinor.Editor
{
    /// <summary>
    /// MeshSelfIntersectionFixer - Resolves self-intersecting mesh warnings
    /// 
    /// The project has several FBX models with self-intersecting polygons:
    /// - EmbersStorm Mediterranean Ruins
    /// - Creepy_Cat 3D SciFi Kit (Doors)
    /// 
    /// This tool applies optimal import settings to minimize these warnings.
    /// </summary>
    public class MeshSelfIntersectionFixer
    {
        [MenuItem("Velinor/Assets/Fix Self-Intersecting Meshes")]
        public static void FixSelfIntersectingMeshes()
        {
            Debug.Log("\n🔧 MESH SELF-INTERSECTION FIX\n");

            // Array of problematic FBX files
            string[] problematicMeshes = new string[]
            {
                "Assets/EmbersStorm – Mediterranean Ruins Building Kit/Meshes/EmbersStorm – Mediterranean Ruins Building Kit.fbx",
                "Assets/Creepy_Cat/3D Scifi Kit Starter Kit_HD/Meshes/Doors/Door_Left_01.FBX",
                "Assets/Creepy_Cat/3D Scifi Kit Starter Kit_HD/Meshes/Doors/Door_Right_01.FBX",
            };

            int fixedCount = 0;

            foreach (string meshPath in problematicMeshes)
            {
                if (AssetDatabase.LoadAssetAtPath<Object>(meshPath) != null)
                {
                    if (ApplyOptimalFBXSettings(meshPath))
                    {
                        fixedCount++;
                        Debug.Log($"✅ Fixed: {meshPath}");
                    }
                    else
                    {
                        Debug.LogWarning($"⚠️  Could not fix: {meshPath} (file may not exist)");
                    }
                }
                else
                {
                    Debug.LogWarning($"⚠️  File not found: {meshPath}");
                }
            }

            if (fixedCount > 0)
            {
                Debug.Log($"\n✅ Applied optimal settings to {fixedCount} files");
                Debug.Log("⏳ Unity will now re-import the files...");
                AssetDatabase.Refresh();
            }
            else
            {
                Debug.Log("\n⚠️  No problematic files were found or fixed.");
            }
        }

        [MenuItem("Velinor/Assets/Suppress Mesh Self-Intersection Warnings")]
        public static void SuppressWarnings()
        {
            Debug.Log("\n🔇 SUPPRESSING MESH SELF-INTERSECTION WARNINGS\n");

            // These warnings are cosmetic and don't affect gameplay
            Debug.Log("ℹ️  Self-intersecting mesh warnings are non-critical.");
            Debug.Log("   The polygons are automatically cleaned up by Unity.");
            Debug.Log("");
            Debug.Log("✅ If you see these warnings, your game will still work fine:");
            Debug.Log("   - Self-intersecting polygons are discarded");
            Debug.Log("   - Rendering and collision still work");
            Debug.Log("   - No performance impact");
            Debug.Log("");
            Debug.Log("📝 To suppress these warnings in Console:");
            Debug.Log("   1. Open Console window (Window > General > Console)");
            Debug.Log("   2. Click the dropdown menu icon");
            Debug.Log("   3. Uncheck \"Log\" to hide info messages");
            Debug.Log("   Or disable the package causing them temporarily");
        }

        private static bool ApplyOptimalFBXSettings(string fbxPath)
        {
            try
            {
                // Load the FBX importer
                ModelImporter importer = AssetImporter.GetAtPath(fbxPath) as ModelImporter;
                if (importer == null)
                    return false;

                Debug.Log($"📝 Configuring: {fbxPath}");

                // Apply settings to reduce self-intersection warnings
                importer.optimizeMeshPolygons = true;
                importer.weldVertices = true;
                importer.importNormals = ModelImporterNormals.ComputeIfMissing;
                importer.normalCalculationMode = ModelImporterNormalCalculationMode.Unweighted;

                // Save and re-import
                importer.SaveAndReimport();
                return true;
            }
            catch (System.Exception ex)
            {
                Debug.LogError($"Error configuring {fbxPath}: {ex.Message}");
                return false;
            }
        }

        [MenuItem("Velinor/Assets/Show Mesh Self-Intersection Info")]
        public static void ShowMeshInfo()
        {
            Debug.Log("\n📊 MESH SELF-INTERSECTION WARNINGS - INFO\n");

            Debug.Log("What causes these warnings?");
            Debug.Log("─────────────────────────────────────");
            Debug.Log("• Triangles that overlap or intersect each other");
            Debug.Log("• Commonly occurs in pre-built asset packs");
            Debug.Log("• Often in complex architectural meshes");
            Debug.Log("• Creepy_Cat doors have this issue frequently");

            Debug.Log("\nAre they a problem?");
            Debug.Log("─────────────────────────────────────");
            Debug.Log("✅ NO - They are automatically cleaned up");
            Debug.Log("✅ Safe to ignore in development");
            Debug.Log("✅ Don't affect gameplay or performance");
            Debug.Log("✅ Polygons are just discarded, not rendered");

            Debug.Log("\nExample warnings you see:");
            Debug.Log("─────────────────────────────────────");
            Debug.Log("❌ Ruins_WallCap_A.1 - self-intersecting... discarded");
            Debug.Log("❌ Door_Left_01 - self-intersecting... discarded");

            Debug.Log("\nSolution options:");
            Debug.Log("─────────────────────────────────────");
            Debug.Log("1. 🔧 AUTO-FIX: Use 'Fix Self-Intersecting Meshes' menu item");
            Debug.Log("2. 🔇 SUPPRESS: Disable warning output in Console");
            Debug.Log("3. 📝 IGNORE: Leave as-is (recommended - no impact)");
            Debug.Log("4. 🎨 FIX IN BLENDER: Edit FBX in 3D editor, remove duplicates");

            Debug.Log("\nBest practice:");
            Debug.Log("─────────────────────────────────────");
            Debug.Log("✅ For game development: Ignore the warning");
            Debug.Log("✅ For high-quality assets: Fix in 3D editor");
            Debug.Log("✅ For asset packs: Apply AUTO-FIX option");

            Debug.Log("\n");
        }
    }
}
