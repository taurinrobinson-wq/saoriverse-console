#if UNITY_EDITOR
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

/// <summary>
/// ComprehensiveAssetRepair: Manually repairs ALL broken materials across asset packs
/// by directly examining prefabs, finding textures, and creating new working materials.
/// 
/// Root cause: Hidden/InternalErrorShader = GUID references to shaders that don't exist
/// Solution: Load actual prefabs, extract broken materials, locate textures manually,
/// create new materials with Standard shader, reassign to MeshRenderers
/// </summary>
public static class ComprehensiveAssetRepair
{
    private static readonly string[] AFFECTED_PACKS = new[]
    {
        "Assets/Kyle's Rock Pack",
        "Assets/Medieval Props Pack 01",
        "Assets/DreamTree2",
        "Assets/Dry_Trees",
        "Assets/EmbersStorm",
        "Assets/URP_Tree_Pak",
        "Assets/Modular 3D Metallic Building Kit"
    };

    [MenuItem("Tools/Asset Repair/[MANUAL] Comprehensive Asset Repair - All Packs")]
    public static void RepairAllAssetPacks()
    {
        var report = new System.Text.StringBuilder();
        report.AppendLine("========================================");
        report.AppendLine("COMPREHENSIVE ASSET REPAIR REPORT");
        report.AppendLine("========================================");
        report.AppendLine($"Time: {System.DateTime.Now}");
        report.AppendLine();

        int totalPrefabsScanned = 0;
        int totalMaterialsFixed = 0;
        int totalTexturesAssigned = 0;

        foreach (var packPath in AFFECTED_PACKS)
        {
            if (!AssetDatabase.IsValidFolder(packPath)) continue;

            report.AppendLine($"\n[PACK] {packPath}");
            report.AppendLine("─────────────────────────────────");

            // Scan all prefabs in this pack
            string[] prefabGuids = AssetDatabase.FindAssets("t:Prefab", new[] { packPath });

            foreach (var guid in prefabGuids)
            {
                string prefabPath = AssetDatabase.GUIDToAssetPath(guid);
                
                // Load prefab and scan for broken materials
                var prefabRoot = PrefabUtility.LoadPrefabContents(prefabPath);
                bool prefabChanged = false;

                var renderers = prefabRoot.GetComponentsInChildren<MeshRenderer>(true);

                foreach (var renderer in renderers)
                {
                    var mats = renderer.sharedMaterials;

                    for (int i = 0; i < mats.Length; i++)
                    {
                        totalPrefabsScanned++;

                        if (mats[i] == null)
                        {
                            // Create fallback material
                            var newMat = CreateStandardMaterial($"Fallback_{renderer.gameObject.name}_{i}");
                            mats[i] = newMat;
                            totalMaterialsFixed++;
                            prefabChanged = true;
                            report.AppendLine($"  [NULL-MAT-FIXED] {renderer.gameObject.name} slot {i}");
                        }
                        else if (mats[i].shader != null && mats[i].shader.name.Contains("Hidden/InternalError"))
                        {
                            // Replace broken shader with Standard
                            mats[i].shader = Shader.Find("Standard");
                            
                            // Try to find and assign textures
                            int texAssigned = TryAssignTexturesFromPack(mats[i], packPath);
                            if (texAssigned > 0)
                            {
                                totalTexturesAssigned += texAssigned;
                                report.AppendLine($"  [BROKEN-SHADER-FIXED] {renderer.gameObject.name} slot {i} -> assigned {texAssigned} textures");
                            }
                            else
                            {
                                // Fallback: use white texture to avoid pink
                                if (mats[i].HasProperty("_MainTex"))
                                {
                                    mats[i].SetTexture("_MainTex", Texture2D.whiteTexture);
                                }
                                report.AppendLine($"  [BROKEN-SHADER-WHITE-FALLBACK] {renderer.gameObject.name} slot {i}");
                            }

                            totalMaterialsFixed++;
                            prefabChanged = true;
                        }
                        else if (mats[i].shader != null && (mats[i].name == "Default-Material" || mats[i].shader.name == ""))
                        {
                            // Default material - replace
                            mats[i].shader = Shader.Find("Standard");
                            int texAssigned = TryAssignTexturesFromPack(mats[i], packPath);
                            totalMaterialsFixed++;
                            prefabChanged = true;
                            report.AppendLine($"  [DEFAULT-MAT-FIXED] {renderer.gameObject.name} slot {i}");
                        }
                    }

                    if (prefabChanged)
                    {
                        renderer.sharedMaterials = mats;
                    }
                }

                if (prefabChanged)
                {
                    PrefabUtility.SaveAsPrefabAsset(prefabRoot, prefabPath);
                    EditorUtility.SetDirty(prefabRoot);
                }

                PrefabUtility.UnloadPrefabContents(prefabRoot);
            }
        }

        report.AppendLine();
        report.AppendLine("========================================");
        report.AppendLine("SUMMARY");
        report.AppendLine("========================================");
        report.AppendLine($"Prefabs Scanned:       {totalPrefabsScanned}");
        report.AppendLine($"Materials Fixed:       {totalMaterialsFixed}");
        report.AppendLine($"Textures Assigned:     {totalTexturesAssigned}");

        string reportText = report.ToString();
        Debug.Log(reportText);

        // Write report to file
        var reportPath = Path.Combine(Application.dataPath, "..", "ComprehensiveRepairReport.txt");
        try
        {
            File.WriteAllText(reportPath, reportText);
            Debug.Log($"Report written to: {reportPath}");
        }
        catch (System.Exception ex)
        {
            Debug.LogWarning($"Failed to write report: {ex.Message}");
        }

        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();

        EditorUtility.DisplayDialog("Asset Repair Complete", 
            $"Fixed {totalMaterialsFixed} broken materials across {AFFECTED_PACKS.Length} asset packs.\n\n" +
            $"Assigned {totalTexturesAssigned} textures.\n\n" +
            $"Report: {reportPath}", 
            "OK");
    }

    /// <summary>
    /// Try to automatically find and assign textures to a material based on pack folder structure
    /// </summary>
    private static int TryAssignTexturesFromPack(Material mat, string packPath)
    {
        if (mat == null || mat.shader == null) return 0;

        int assigned = 0;
        var textureProps = new[] { "_MainTex", "_BumpMap", "_MetallicGlossMap", "_OcclusionMap" };

        // Search for textures in the pack folder
        string[] textureGuids = AssetDatabase.FindAssets("t:Texture", new[] { packPath });

        // Group textures by type
        var textureMap = new Dictionary<string, List<string>>();

        foreach (var guid in textureGuids)
        {
            string texPath = AssetDatabase.GUIDToAssetPath(guid);
            string texName = Path.GetFileNameWithoutExtension(texPath).ToLower();

            // Categorize by name patterns
            if (texName.Contains("diffuse") || texName.Contains("albedo") || texName.Contains("base") || texName.Contains("color"))
            {
                if (!textureMap.ContainsKey("diffuse")) textureMap["diffuse"] = new List<string>();
                textureMap["diffuse"].Add(texPath);
            }
            if (texName.Contains("normal") || texName.Contains("bump"))
            {
                if (!textureMap.ContainsKey("normal")) textureMap["normal"] = new List<string>();
                textureMap["normal"].Add(texPath);
            }
            if (texName.Contains("metallic") || texName.Contains("metal") || texName.Contains("specular"))
            {
                if (!textureMap.ContainsKey("metallic")) textureMap["metallic"] = new List<string>();
                textureMap["metallic"].Add(texPath);
            }
            if (texName.Contains("occlusion") || texName.Contains("ao") || texName.Contains("ambient"))
            {
                if (!textureMap.ContainsKey("occlusion")) textureMap["occlusion"] = new List<string>();
                textureMap["occlusion"].Add(texPath);
            }
        }

        // Assign textures to material properties
        if (textureMap.ContainsKey("diffuse") && mat.HasProperty("_MainTex"))
        {
            var tex = AssetDatabase.LoadAssetAtPath<Texture>(textureMap["diffuse"][0]);
            if (tex != null)
            {
                mat.SetTexture("_MainTex", tex);
                assigned++;
            }
        }

        if (textureMap.ContainsKey("normal") && mat.HasProperty("_BumpMap"))
        {
            var tex = AssetDatabase.LoadAssetAtPath<Texture>(textureMap["normal"][0]);
            if (tex != null)
            {
                mat.SetTexture("_BumpMap", tex);
                assigned++;
            }
        }

        if (textureMap.ContainsKey("metallic") && mat.HasProperty("_MetallicGlossMap"))
        {
            var tex = AssetDatabase.LoadAssetAtPath<Texture>(textureMap["metallic"][0]);
            if (tex != null)
            {
                mat.SetTexture("_MetallicGlossMap", tex);
                assigned++;
            }
        }

        if (textureMap.ContainsKey("occlusion") && mat.HasProperty("_OcclusionMap"))
        {
            var tex = AssetDatabase.LoadAssetAtPath<Texture>(textureMap["occlusion"][0]);
            if (tex != null)
            {
                mat.SetTexture("_OcclusionMap", tex);
                assigned++;
            }
        }

        EditorUtility.SetDirty(mat);
        return assigned;
    }

    /// <summary>
    /// Create a simple Standard material with white color
    /// </summary>
    private static Material CreateStandardMaterial(string name)
    {
        var mat = new Material(Shader.Find("Standard"));
        mat.name = name;
        mat.color = Color.white;
        return mat;
    }
}
#endif
