using UnityEditor;
using UnityEngine;

public class PrefabMaterialReset : EditorWindow
{
    [MenuItem("URP Tools/Strip HDRP Materials From Prefabs")]
    public static void StripHDRPMaterials()
    {
        string[] prefabGuids = AssetDatabase.FindAssets("t:Prefab");

        foreach (string guid in prefabGuids)
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);

            if (prefab == null) continue;

            bool modified = false;

            Renderer[] renderers = prefab.GetComponentsInChildren<Renderer>(true);
            foreach (Renderer r in renderers)
            {
                for (int i = 0; i < r.sharedMaterials.Length; i++)
                {
                    Material m = r.sharedMaterials[i];
                    if (m == null) continue;

                    string shaderName = m.shader.name;

                    if (shaderName.Contains("HDRP"))
                    {
                        r.sharedMaterials[i] = null;
                        modified = true;
                        Debug.Log($"Removed HDRP material from {path}");
                    }
                }
            }

            if (modified)
            {
                PrefabUtility.SavePrefabAsset(prefab);
            }
        }

        Debug.Log("Prefab material stripping complete.");
    }
}
