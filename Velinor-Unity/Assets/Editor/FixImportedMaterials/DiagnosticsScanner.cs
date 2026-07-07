#if UNITY_EDITOR
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

public static class DiagnosticsScanner
{
    public static void ScanAllScenesAndPrefabs()
    {
        var report = new System.Text.StringBuilder();
        report.AppendLine("=== DIAGNOSTICS SCAN ===");
        report.AppendLine(System.DateTime.Now.ToString());
        report.AppendLine();

        int missingScriptCount = 0;
        int nullMaterialCount = 0;
        int brokenShaderCount = 0;

        // Scan all scenes
        report.AppendLine("[SCENES]");
        string[] sceneGuids = AssetDatabase.FindAssets("t:Scene");
        foreach (var guid in sceneGuids)
        {
            string scenePath = AssetDatabase.GUIDToAssetPath(guid);
            report.AppendLine($"  Scene: {scenePath}");

            Scene scene = EditorSceneManager.OpenScene(scenePath, OpenSceneMode.Single);
            var rootObjects = scene.GetRootGameObjects();

            foreach (var root in rootObjects)
            {
                var allObjects = root.GetComponentsInChildren<Transform>(true);
                foreach (var obj in allObjects)
                {
                    // Check for Player with missing script
                    if (obj.gameObject.name.Contains("Player"))
                    {
                        var scripts = obj.GetComponents<MonoBehaviour>();
                        bool hasMissingScript = false;
                        foreach (var script in scripts)
                        {
                            if (script == null)
                            {
                                hasMissingScript = true;
                                break;
                            }
                        }
                        if (hasMissingScript || scripts.Length == 0)
                        {
                            missingScriptCount++;
                            report.AppendLine($"    [MISSING-SCRIPT] {obj.gameObject.name} at {GetHierarchyPath(obj.gameObject)}");
                        }
                    }

                    // Check MeshRenderer materials
                    var renderer = obj.GetComponent<MeshRenderer>();
                    if (renderer != null)
                    {
                        var mats = renderer.sharedMaterials;
                        for (int i = 0; i < mats.Length; i++)
                        {
                            if (mats[i] == null)
                            {
                                nullMaterialCount++;
                                report.AppendLine($"    [NULL-MAT] {obj.gameObject.name} slot {i}");
                            }
                            else if (mats[i].name == "Default-Material" || (mats[i].shader != null && mats[i].shader.name.Contains("Hidden/InternalError")))
                            {
                                brokenShaderCount++;
                                report.AppendLine($"    [BROKEN-SHADER] {obj.gameObject.name} slot {i} -> {mats[i].shader.name}");
                            }
                        }
                    }
                }
            }
        }

        // Scan all prefabs
        report.AppendLine();
        report.AppendLine("[PREFABS]");
        string[] prefabGuids = AssetDatabase.FindAssets("t:Prefab");
        foreach (var guid in prefabGuids)
        {
            string prefabPath = AssetDatabase.GUIDToAssetPath(guid);
            var prefabRoot = PrefabUtility.LoadPrefabContents(prefabPath);

            var allObjects = prefabRoot.GetComponentsInChildren<Transform>(true);
            foreach (var obj in allObjects)
            {
                // Check for Player with missing script
                if (obj.gameObject.name.Contains("Player"))
                {
                    var scripts = obj.GetComponents<MonoBehaviour>();
                    bool hasMissingScript = false;
                    foreach (var script in scripts)
                    {
                        if (script == null)
                        {
                            hasMissingScript = true;
                            break;
                        }
                    }
                    if (hasMissingScript || scripts.Length == 0)
                    {
                        missingScriptCount++;
                        report.AppendLine($"    [MISSING-SCRIPT] {prefabPath} -> {obj.gameObject.name}");
                    }
                }

                // Check MeshRenderer materials
                var renderer = obj.GetComponent<MeshRenderer>();
                if (renderer != null)
                {
                    var mats = renderer.sharedMaterials;
                    for (int i = 0; i < mats.Length; i++)
                    {
                        if (mats[i] == null)
                        {
                            nullMaterialCount++;
                            report.AppendLine($"    [NULL-MAT] {prefabPath} -> {obj.gameObject.name} slot {i}");
                        }
                        else if (mats[i].name == "Default-Material" || (mats[i].shader != null && mats[i].shader.name.Contains("Hidden/InternalError")))
                        {
                            brokenShaderCount++;
                            report.AppendLine($"    [BROKEN-SHADER] {prefabPath} -> {obj.gameObject.name} slot {i} -> {mats[i].shader.name}");
                        }
                    }
                }
            }

            PrefabUtility.UnloadPrefabContents(prefabRoot);
        }

        report.AppendLine();
        report.AppendLine("=== SUMMARY ===");
        report.AppendLine($"Missing Scripts: {missingScriptCount}");
        report.AppendLine($"Null Materials:  {nullMaterialCount}");
        report.AppendLine($"Broken Shaders:  {brokenShaderCount}");

        string reportText = report.ToString();
        Debug.Log(reportText);

        // Write to file
        var outPath = System.IO.Path.Combine(Application.dataPath, "..", "DiagnosticsReport.txt");
        try
        {
            System.IO.File.WriteAllText(outPath, reportText);
            Debug.Log($"Diagnostics report written to: {outPath}");
        }
        catch (System.Exception ex)
        {
            Debug.LogWarning("Failed to write DiagnosticsReport.txt: " + ex.Message);
        }
    }

    private static string GetHierarchyPath(GameObject go)
    {
        string path = go.name;
        Transform current = go.transform.parent;
        while (current != null)
        {
            path = current.gameObject.name + "/" + path;
            current = current.parent;
        }
        return path;
    }
}
#endif
