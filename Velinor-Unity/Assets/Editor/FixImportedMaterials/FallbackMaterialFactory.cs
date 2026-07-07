#if UNITY_EDITOR
using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

public static class FallbackMaterialFactory
{
    public static Material CreateFallbackMaterialForSlot(string prefabPath, int slotIndex, bool srpActive)
    {
        string prefabFolder = Path.GetDirectoryName(prefabPath).Replace("\\", "/");
        string autofixFolder = Path.Combine(prefabFolder, "AutoFixedMaterials").Replace("\\", "/");

        if (!AssetDatabase.IsValidFolder(autofixFolder))
        {
            AssetDatabase.CreateFolder(prefabFolder, "AutoFixedMaterials");
        }

        string guid = AssetDatabase.AssetPathToGUID(prefabPath);
        string matAssetPath = Path.Combine(autofixFolder, guid + "_slot" + slotIndex + ".mat").Replace("\\", "/");

        var rp = GraphicsSettings.currentRenderPipeline;
        bool isURP = rp != null && rp.GetType().Name.Contains("Universal");
        Shader fallbackShader = srpActive && isURP ? Shader.Find("Universal Render Pipeline/Lit") : Shader.Find("Standard");
        if (fallbackShader == null) fallbackShader = Shader.Find("Standard");

        Material newMat = new Material(fallbackShader);

        var texPaths = FolderCache.GetTextures(prefabFolder);
        foreach (var tpath in texPaths)
        {
            string tname = Path.GetFileNameWithoutExtension(tpath).ToLower();
            var tex = AssetDatabase.LoadAssetAtPath<Texture>(tpath);
            if (tex == null) continue;

            if (tname.Contains("albedo") || tname.Contains("diffuse") || tname.Contains("base"))
            {
                if (newMat.HasProperty("_MainTex")) newMat.SetTexture("_MainTex", tex);
                if (newMat.HasProperty("_BaseMap")) newMat.SetTexture("_BaseMap", tex);
            }
            else if (tname.Contains("normal") || tname.Contains("nrm"))
            {
                if (newMat.HasProperty("_BumpMap")) newMat.SetTexture("_BumpMap", tex);
            }
            else if (tname.Contains("metal") || tname.Contains("metallic") || tname.Contains("roughness") || tname.Contains("spec"))
            {
                if (newMat.HasProperty("_MetallicGlossMap")) newMat.SetTexture("_MetallicGlossMap", tex);
                if (newMat.HasProperty("_MetallicMap")) newMat.SetTexture("_MetallicMap", tex);
                if (newMat.HasProperty("_SpecGlossMap")) newMat.SetTexture("_SpecGlossMap", tex);
                if (newMat.HasProperty("_SpecularMap")) newMat.SetTexture("_SpecularMap", tex);
            }
            else if (tname.Contains("mask") || tname.Contains("ao"))
            {
                if (newMat.HasProperty("_OcclusionMap")) newMat.SetTexture("_OcclusionMap", tex);
            }
        }

        AssetDatabase.CreateAsset(newMat, matAssetPath);
        AssetDatabase.SaveAssets();
        return newMat;
    }

    public static Material CreateStandardFallback(string prefabPath, int slotIndex)
    {
        string prefabFolder = Path.GetDirectoryName(prefabPath).Replace("\\", "/");
        string autofixFolder = Path.Combine(prefabFolder, "AutoFixedMaterials").Replace("\\", "/");

        if (!AssetDatabase.IsValidFolder(autofixFolder))
        {
            AssetDatabase.CreateFolder(prefabFolder, "AutoFixedMaterials");
        }

        string guid = AssetDatabase.AssetPathToGUID(prefabPath);
        string matAssetPath = Path.Combine(autofixFolder, guid + "_std_slot" + slotIndex + ".mat").Replace("\\", "/");

        Material newMat = new Material(Shader.Find("Standard"));
        AssetDatabase.CreateAsset(newMat, matAssetPath);
        AssetDatabase.SaveAssets();
        return newMat;
    }
}
#endif
