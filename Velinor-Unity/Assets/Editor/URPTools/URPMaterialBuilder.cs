using UnityEditor;
using UnityEngine;
using System.IO;

public class URPMaterialBuilder : EditorWindow
{
    [MenuItem("URP Tools/Auto-Rebuild URP Materials")]
    public static void BuildURPMaterials()
    {
        string[] textureGuids = AssetDatabase.FindAssets("t:Texture");

        foreach (string guid in textureGuids)
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);

            if (!path.ToLower().Contains("albedo") &&
                !path.ToLower().Contains("diffuse"))
                continue;

            Texture2D albedo = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            if (albedo == null) continue;

            string baseName = Path.GetFileNameWithoutExtension(path)
                .Replace("_albedo", "")
                .Replace("_diffuse", "");

            string folder = Path.GetDirectoryName(path);
            string matPath = folder + "/" + baseName + "_URP.mat";

            Material mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
            mat.SetTexture("_BaseMap", albedo);

            string normalPath = folder + "/" + baseName + "_normal.png";
            if (File.Exists(normalPath))
            {
                Texture2D normal = AssetDatabase.LoadAssetAtPath<Texture2D>(normalPath);
                mat.SetTexture("_BumpMap", normal);
                mat.EnableKeyword("_NORMALMAP");
            }

            string maskPath = folder + "/" + baseName + "_mask.png";
            if (File.Exists(maskPath))
            {
                Texture2D mask = AssetDatabase.LoadAssetAtPath<Texture2D>(maskPath);
                mat.SetTexture("_MaskMap", mask);
            }

            AssetDatabase.CreateAsset(mat, matPath);
            Debug.Log("Created URP material: " + matPath);
        }

        AssetDatabase.Refresh();
        Debug.Log("URP material rebuild complete.");
    }
}
