#if UNITY_EDITOR
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

public static class TextureAutoAssigner
{
    public static bool TryAutoAssignTexture(Material mat, string matPath, string[] propsToTry, string[] namePatterns)
    {
        string folder = Path.GetDirectoryName(matPath).Replace("\\", "/");
        var textures = new System.Collections.Generic.List<string>();
        
        // Add textures from immediate folder
        textures.AddRange(FolderCache.GetTextures(folder));
        
        // Also search in sibling folders (e.g., if materials are in Materials/, look in Textures/)
        string parentFolder = Path.GetDirectoryName(folder).Replace("\\", "/");
        if (!string.IsNullOrEmpty(parentFolder) && AssetDatabase.IsValidFolder(parentFolder))
        {
            var subFolders = AssetDatabase.GetSubFolders(parentFolder);
            foreach (var sub in subFolders)
            {
                if (sub != folder)
                {
                    textures.AddRange(FolderCache.GetTextures(sub));
                }
            }
        }
        
        Texture bestTex = null;
        int bestScore = 0;

        foreach (var p in textures)
        {
            string name = Path.GetFileNameWithoutExtension(p).ToLower();
            int score = ScoreTextureName(name, namePatterns);
            if (score > bestScore)
            {
                var tex = AssetDatabase.LoadAssetAtPath<Texture>(p);
                if (tex != null)
                {
                    bestTex = tex;
                    bestScore = score;
                }
            }
        }

        if (bestTex == null)
            return false;

        foreach (var prop in propsToTry)
        {
            if (mat.HasProperty(prop))
            {
                mat.SetTexture(prop, bestTex);
                TryNormalizeNormalMapIfNeeded(mat, prop, bestTex);
                return true;
            }
        }

        return false;
    }

    public static bool TryAssignTexturesFromFolder(Material mat, string folder)
    {
        if (string.IsNullOrEmpty(folder) || !AssetDatabase.IsValidFolder(folder)) return false;

        var textures = new System.Collections.Generic.List<string>();
        textures.AddRange(FolderCache.GetTextures(folder.Replace("\\", "/")));
        
        // Also search in sibling folders
        string parentFolder = Path.GetDirectoryName(folder).Replace("\\", "/");
        if (!string.IsNullOrEmpty(parentFolder) && AssetDatabase.IsValidFolder(parentFolder))
        {
            var subFolders = AssetDatabase.GetSubFolders(parentFolder);
            foreach (var sub in subFolders)
            {
                if (sub != folder)
                {
                    textures.AddRange(FolderCache.GetTextures(sub));
                }
            }
        }
        
        bool assigned = false;

        foreach (var p in textures)
        {
            string name = Path.GetFileNameWithoutExtension(p).ToLower();
            var tex = AssetDatabase.LoadAssetAtPath<Texture>(p);
            if (tex == null) continue;

            // Albedo / base
            if (name.EndsWith("_albedo") || name.EndsWith("_diffuse") || name.EndsWith("_base") ||
                name.Contains("albedo") || name.Contains("diffuse") || name.Contains("base") || name.Contains("roughness"))
            {
                if (mat.HasProperty("_MainTex")) { mat.SetTexture("_MainTex", tex); assigned = true; }
                if (mat.HasProperty("_BaseMap")) { mat.SetTexture("_BaseMap", tex); assigned = true; }
            }

            // Normal
            if (name.EndsWith("_normal") || name.EndsWith("_nrm") || name.Contains("normal") || name.Contains("nrm"))
            {
                if (mat.HasProperty("_BumpMap"))
                {
                    mat.SetTexture("_BumpMap", tex);
                    TryNormalizeNormalMapIfNeeded(mat, "_BumpMap", tex);
                    assigned = true;
                }
            }

            // Metallic / roughness / spec
            if (name.EndsWith("_metallic") || name.EndsWith("_metal") || name.Contains("metal") || name.Contains("metallic"))
            {
                if (mat.HasProperty("_MetallicGlossMap")) { mat.SetTexture("_MetallicGlossMap", tex); assigned = true; }
                if (mat.HasProperty("_MetallicMap")) { mat.SetTexture("_MetallicMap", tex); assigned = true; }
                if (mat.HasProperty("_SpecGlossMap")) { mat.SetTexture("_SpecGlossMap", tex); assigned = true; }
                if (mat.HasProperty("_SpecularMap")) { mat.SetTexture("_SpecularMap", tex); assigned = true; }
            }

            // AO / mask
            if (name.EndsWith("_ao") || name.EndsWith("_mask") || name.Contains("ao") || name.Contains("mask"))
            {
                if (mat.HasProperty("_OcclusionMap")) { mat.SetTexture("_OcclusionMap", tex); assigned = true; }
            }
        }

        return assigned;
    }

    private static int ScoreTextureName(string name, string[] patterns)
    {
        int score = 0;
        foreach (var pat in patterns)
        {
            if (name.EndsWith(pat)) score += 10;
            else if (name.Contains(pat)) score += 5;
        }
        return score;
    }

    private static void TryNormalizeNormalMapIfNeeded(Material mat, string propName, Texture tex)
    {
        if (!mat.HasProperty(propName)) return;
        if (!(tex is Texture2D)) return;

        string path = AssetDatabase.GetAssetPath(tex);
        var importer = AssetImporter.GetAtPath(path) as TextureImporter;
        if (importer == null) return;

        if (importer.textureType != TextureImporterType.NormalMap)
        {
            importer.textureType = TextureImporterType.NormalMap;
            importer.SaveAndReimport();
        }
    }
}
#endif
