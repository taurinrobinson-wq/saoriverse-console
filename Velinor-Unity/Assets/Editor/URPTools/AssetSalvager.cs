using UnityEditor;
using UnityEngine;
using System.IO;

public class AssetSalvager : EditorWindow
{
    private static readonly string salvageRoot = "Assets/Salvaged";

    [MenuItem("URP Tools/Run Full Asset Salvage")]
    public static void RunSalvage()
    {
        EnsureSalvageFolders();

        SalvageMeshes();
        SalvageTextures();
        SalvageHeightmaps();
        SalvagePrefabs();

        Debug.Log("Asset salvage complete. Safe assets moved to /Assets/Salvaged/");
    }

    private static void EnsureSalvageFolders()
    {
        string[] folders = new string[]
        {
            salvageRoot,
            salvageRoot + "/Meshes",
            salvageRoot + "/Textures",
            salvageRoot + "/Prefabs",
            salvageRoot + "/Terrain",
            salvageRoot + "/Misc"
        };

        foreach (string folder in folders)
        {
            if (!AssetDatabase.IsValidFolder(folder))
            {
                string parent = Path.GetDirectoryName(folder);
                string name = Path.GetFileName(folder);
                AssetDatabase.CreateFolder(parent, name);
            }
        }
    }

    private static void SalvageMeshes()
    {
        string[] guids = AssetDatabase.FindAssets("t:Model");

        foreach (string guid in guids)
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);

            if (IsHDRPPath(path)) continue;

            string dest = salvageRoot + "/Meshes/" + Path.GetFileName(path);
            AssetDatabase.MoveAsset(path, dest);
            Debug.Log("Salvaged mesh: " + path);
        }
    }

    private static void SalvageTextures()
    {
        string[] guids = AssetDatabase.FindAssets("t:Texture");

        foreach (string guid in guids)
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);

            if (IsHDRPPath(path)) continue;

            string dest = salvageRoot + "/Textures/" + Path.GetFileName(path);
            AssetDatabase.MoveAsset(path, dest);
            Debug.Log("Salvaged texture: " + path);
        }
    }

    private static void SalvageHeightmaps()
    {
        string[] guids = AssetDatabase.FindAssets("t:TerrainData");

        foreach (string guid in guids)
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);

            if (IsHDRPPath(path)) continue;

            string dest = salvageRoot + "/Terrain/" + Path.GetFileName(path);
            AssetDatabase.MoveAsset(path, dest);
            Debug.Log("Salvaged terrain data: " + path);
        }
    }

    private static void SalvagePrefabs()
    {
        string[] guids = AssetDatabase.FindAssets("t:Prefab");

        foreach (string guid in guids)
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);

            if (IsHDRPPath(path)) continue;

            string dest = salvageRoot + "/Prefabs/" + Path.GetFileName(path);
            AssetDatabase.MoveAsset(path, dest);
            Debug.Log("Salvaged prefab: " + path);
        }
    }

    private static bool IsHDRPPath(string path)
    {
        string lower = path.ToLower();

        return lower.Contains("hdrp") ||
               lower.Contains("diffusionprofile") ||
               lower.Contains("hdrenderpipeline") ||
               lower.Contains("lookdev") ||
               lower.Contains("volumeprofile") ||
               lower.Contains("defaultsettings") ||
               lower.Contains("hdrpdefaultresources");
    }
}
