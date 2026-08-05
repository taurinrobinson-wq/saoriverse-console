using UnityEditor;
using UnityEngine;
using System.IO;

public class HDRPPurge : EditorWindow
{
    [MenuItem("URP Tools/Purge HDRP Assets")]
    public static void PurgeHDRP()
    {
        string[] hdrpKeywords = new string[]
        {
            "HDRPDefaultResources",
            "HDRenderPipelineAsset",
            "HDRenderPipelineGlobalSettings",
            "DiffusionProfile",
            "LookDev",
            "VolumeProfile",
            "HDRP"
        };

        foreach (string keyword in hdrpKeywords)
        {
            string[] guids = AssetDatabase.FindAssets(keyword);
            foreach (string guid in guids)
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                if (!string.IsNullOrEmpty(path))
                {
                    Debug.Log("Deleting HDRP asset: " + path);
                    AssetDatabase.DeleteAsset(path);
                }
            }
        }

        AssetDatabase.Refresh();
        Debug.Log("HDRP purge complete.");
    }
}
