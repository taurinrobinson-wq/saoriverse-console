#if UNITY_EDITOR
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

public static class MaterialConverter
{
    public static void ProcessMaterialsInFolder(string rootFolder, bool dryRun, ReportBuilder report)
    {
        bool srpActive = GraphicsSettings.currentRenderPipeline != null;
        var rp = GraphicsSettings.currentRenderPipeline;
        bool isURP = rp != null && rp.GetType().Name.Contains("Universal");
        Shader urpLit = isURP ? Shader.Find("Universal Render Pipeline/Lit") : null;

        var matPaths = FolderCache.GetMaterials(rootFolder);
        int total = matPaths.Count;
        int index = 0;

        foreach (var mPath in matPaths)
        {
            EditorUtility.DisplayProgressBar("Fix Imported Materials - Materials", mPath, (float)index / (total > 0 ? total : 1));
            index++;

            var mat = AssetDatabase.LoadAssetAtPath<Material>(mPath);
            if (mat == null) continue;

            // If shader is missing or broken, apply a safe fallback shader and attempt to rebind textures
            if (mat.shader == null || (mat.shader.name != null && mat.shader.name.Contains("Hidden/InternalError")))
            {
                Shader fallback = urpLit != null ? urpLit : Shader.Find("Standard");
                if (fallback != null)
                {
                    mat.shader = fallback;
                    if (!dryRun) EditorUtility.SetDirty(mat);
                    report.LogMaterialFallback(mPath, mat.shader != null ? mat.shader.name : "(null)");
                }
            }

            Texture mainTex = null, bump = null, metallic = null, occ = null;
            if (mat.HasProperty("_MainTex")) mainTex = mat.GetTexture("_MainTex");
            if (mat.HasProperty("_BumpMap")) bump = mat.GetTexture("_BumpMap");
            if (mat.HasProperty("_MetallicGlossMap")) metallic = mat.GetTexture("_MetallicGlossMap");
            if (mat.HasProperty("_OcclusionMap")) occ = mat.GetTexture("_OcclusionMap");

            if (IsBuiltInStandard(mat))
            {
                if (srpActive && urpLit != null && isURP)
                {
                    mat.shader = urpLit;
                    if (mainTex != null)
                    {
                        if (mat.HasProperty("_BaseMap")) mat.SetTexture("_BaseMap", mainTex);
                        else if (mat.HasProperty("_MainTex")) mat.SetTexture("_MainTex", mainTex);
                    }
                    if (bump != null && mat.HasProperty("_BumpMap")) mat.SetTexture("_BumpMap", bump);
                    if (metallic != null)
                    {
                        if (mat.HasProperty("_MetallicGlossMap")) mat.SetTexture("_MetallicGlossMap", metallic);
                        else if (mat.HasProperty("_MetallicMap")) mat.SetTexture("_MetallicMap", metallic);
                    }
                    if (occ != null && mat.HasProperty("_OcclusionMap")) mat.SetTexture("_OcclusionMap", occ);

                    if (!dryRun) EditorUtility.SetDirty(mat);
                    report.LogConvert(mPath, mat.shader.name);
                }
                else
                {
                    report.LogSkipConvert(mPath);
                }
            }

            bool changed = false;
            if ((mainTex == null || mainTex == Texture2D.whiteTexture) &&
                TextureAutoAssigner.TryAutoAssignTexture(mat, mPath, new[] { "_MainTex", "_BaseMap" }, new[] { "_albedo", "_diffuse", "_base", "_roughness" }))
                changed = true;

            if (bump == null &&
                TextureAutoAssigner.TryAutoAssignTexture(mat, mPath, new[] { "_BumpMap" }, new[] { "_normal", "_nrm" }))
                changed = true;

            if (metallic == null &&
                TextureAutoAssigner.TryAutoAssignTexture(mat, mPath, new[] { "_MetallicGlossMap", "_MetallicMap", "_SpecGlossMap", "_SpecularMap" }, new[] { "_metal", "_metallic", "_roughness", "_spec" }))
                changed = true;

            if (occ == null &&
                TextureAutoAssigner.TryAutoAssignTexture(mat, mPath, new[] { "_OcclusionMap" }, new[] { "_mask", "_masks", "_ao" }))
                changed = true;

            // Fallback: if still no _MainTex, assign white to prevent pink rendering
            if (mat.HasProperty("_MainTex") && mat.GetTexture("_MainTex") == null)
            {
                mat.SetTexture("_MainTex", Texture2D.whiteTexture);
                changed = true;
            }
            if (mat.HasProperty("_BaseMap") && mat.GetTexture("_BaseMap") == null && !mat.HasProperty("_MainTex"))
            {
                mat.SetTexture("_BaseMap", Texture2D.whiteTexture);
                changed = true;
            }

            if (changed)
            {
                if (!dryRun) EditorUtility.SetDirty(mat);
                report.LogPatch(mPath);
            }
        }

        EditorUtility.ClearProgressBar();
    }

    private static bool IsBuiltInStandard(Material m)
    {
        if (m.shader == null) return false;
        var std = Shader.Find("Standard");
        if (m.shader == std) return true;
        return m.shader.name.Contains("Standard");
    }
}
#endif
