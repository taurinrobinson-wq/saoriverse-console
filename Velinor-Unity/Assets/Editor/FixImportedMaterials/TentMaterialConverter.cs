#if UNITY_EDITOR
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

public static class TentMaterialConverter
{
    public static void ConvertTentExtractedMaterials()
    {
        bool srpActive = GraphicsSettings.currentRenderPipeline != null;
        var rp = GraphicsSettings.currentRenderPipeline;
        bool isURP = rp != null && rp.GetType().Name.Contains("Universal");

        if (!srpActive || !isURP)
        {
            Debug.LogWarning("[TentMaterialConverter] URP not active. Skipping conversion.");
            return;
        }

        Shader urpLit = Shader.Find("Universal Render Pipeline/Lit");
        if (urpLit == null)
        {
            Debug.LogError("[TentMaterialConverter] Cannot find URP Lit shader.");
            return;
        }

        var report = new System.Text.StringBuilder();
        report.AppendLine("Tent Material Conversion Report");
        report.AppendLine(System.DateTime.Now.ToString());
        report.AppendLine();

        // Find all FBX models with Tent/Cloth/Rope/Wood in the name
        string[] fbxGuids = AssetDatabase.FindAssets("t:Model");
        var tentModels = new List<string>();

        foreach (var guid in fbxGuids)
        {
            string assetPath = AssetDatabase.GUIDToAssetPath(guid);
            if (assetPath.ToLower().Contains("tent") || assetPath.ToLower().Contains("cloth") || 
                assetPath.ToLower().Contains("rope") || assetPath.ToLower().Contains("wood"))
            {
                tentModels.Add(assetPath);
            }
        }

        int convertedCount = 0;
        int remappedCount = 0;

        foreach (var modelPath in tentModels)
        {
            string modelFolder = Path.GetDirectoryName(modelPath).Replace("\\", "/");
            
            // Look for extracted materials in subfolders or the same folder
            string[] matGuids = AssetDatabase.FindAssets("t:Material", new[] { modelFolder });
            
            foreach (var matGuid in matGuids)
            {
                string matPath = AssetDatabase.GUIDToAssetPath(matGuid);
                var mat = AssetDatabase.LoadAssetAtPath<Material>(matPath);
                
                if (mat == null) continue;

                // Convert Standard to URP Lit
                if (mat.shader != null && mat.shader.name.Contains("Standard"))
                {
                    mat.shader = urpLit;
                    
                    // Remap texture properties
                    if (mat.HasProperty("_MainTex"))
                    {
                        var mainTex = mat.GetTexture("_MainTex");
                        if (mainTex != null && mat.HasProperty("_BaseMap"))
                        {
                            mat.SetTexture("_BaseMap", mainTex);
                            remappedCount++;
                        }
                    }

                    if (mat.HasProperty("_BumpMap"))
                    {
                        var bumpTex = mat.GetTexture("_BumpMap");
                        if (bumpTex != null && mat.HasProperty("_BumpMap"))
                        {
                            mat.SetTexture("_BumpMap", bumpTex);
                        }
                    }

                    if (mat.HasProperty("_MetallicGlossMap"))
                    {
                        var metallicTex = mat.GetTexture("_MetallicGlossMap");
                        if (metallicTex != null)
                        {
                            if (mat.HasProperty("_MetallicMap")) mat.SetTexture("_MetallicMap", metallicTex);
                            else if (mat.HasProperty("_MetallicGlossMap")) mat.SetTexture("_MetallicGlossMap", metallicTex);
                        }
                    }

                    if (mat.HasProperty("_OcclusionMap"))
                    {
                        var occTex = mat.GetTexture("_OcclusionMap");
                        if (occTex != null && mat.HasProperty("_OcclusionMap"))
                        {
                            mat.SetTexture("_OcclusionMap", occTex);
                        }
                    }

                    EditorUtility.SetDirty(mat);
                    convertedCount++;
                    report.AppendLine($"[CONVERTED] {matPath} -> URP Lit");
                }
            }
        }

        // Reassign converted materials to Tent prefabs
        string[] tentPrefabGuids = AssetDatabase.FindAssets("t:Prefab", new[] { "Assets" });
        int reassignedCount = 0;

        foreach (var prefabGuid in tentPrefabGuids)
        {
            string prefabPath = AssetDatabase.GUIDToAssetPath(prefabGuid);
            if (!prefabPath.ToLower().Contains("tent")) continue;

            var prefabRoot = PrefabUtility.LoadPrefabContents(prefabPath);
            bool prefabChanged = false;

            var targetRenderers = new[] { "Tent_Cloth_low", "Tent_Rope_low", "Tent_Wood_low" };
            foreach (var targetName in targetRenderers)
            {
                var rendererObj = prefabRoot.transform.Find(targetName);
                if (rendererObj == null)
                {
                    // Try searching recursively
                    rendererObj = FindInChildren(prefabRoot.transform, targetName);
                }

                if (rendererObj != null)
                {
                    var renderer = rendererObj.GetComponent<MeshRenderer>();
                    if (renderer != null)
                    {
                        var mats = renderer.sharedMaterials;
                        bool matChanged = false;

                        for (int i = 0; i < mats.Length; i++)
                        {
                            if (mats[i] != null && mats[i].shader != null && mats[i].shader.name.Contains("Standard"))
                            {
                                mats[i].shader = urpLit;
                                matChanged = true;
                                reassignedCount++;
                                report.AppendLine($"[REASSIGNED] {prefabPath} -> {targetName} slot {i}");
                            }
                        }

                        if (matChanged)
                        {
                            renderer.sharedMaterials = mats;
                            prefabChanged = true;
                        }
                    }
                }
            }

            if (prefabChanged)
            {
                PrefabUtility.SaveAsPrefabAsset(prefabRoot, prefabPath);
            }

            PrefabUtility.UnloadPrefabContents(prefabRoot);
        }

        AssetDatabase.SaveAssets();

        report.AppendLine();
        report.AppendLine("=== SUMMARY ===");
        report.AppendLine($"Converted Materials: {convertedCount}");
        report.AppendLine($"Remapped Textures:   {remappedCount}");
        report.AppendLine($"Reassigned to Tents: {reassignedCount}");

        string reportText = report.ToString();
        Debug.Log(reportText);

        var outPath = Path.Combine(Application.dataPath, "..", "TentMaterialConversionReport.txt");
        try
        {
            File.WriteAllText(outPath, reportText);
            Debug.Log($"Tent conversion report written to: {outPath}");
        }
        catch (System.Exception ex)
        {
            Debug.LogWarning("Failed to write TentMaterialConversionReport.txt: " + ex.Message);
        }
    }

    private static Transform FindInChildren(Transform parent, string childName)
    {
        foreach (Transform child in parent.GetComponentsInChildren<Transform>(true))
        {
            if (child.gameObject.name == childName)
                return child;
        }
        return null;
    }
}
#endif
