using System.Text;
using System.IO;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;

public static class MaterialDiagnostics
{
    [MenuItem("Velinor/Diagnostics/Scan Materials (Asset Packs)")]
    public static void ScanMaterialsInPacks()
    {
        // Folders to scan (common packs used by the marketplace)
        string[] folders = new string[] {
            "Assets/Kyle's Rock Pack",
            "Assets/DreamTree2",
            "Assets/Dry_Trees",
            "Assets/Medieval Props Pack 01",
            "Assets/EmbersStorm – Mediterranean Ruins Building Kit",
            "Assets/3 English Oak Set"
        };

        var sb = new StringBuilder();
        sb.AppendLine("Material Diagnostics Report");
        sb.AppendLine(System.DateTime.Now.ToString());
        sb.AppendLine();

        int prefabCount = 0;
        int problemCount = 0;

        bool usingSRP = UnityEngine.Rendering.GraphicsSettings.currentRenderPipeline != null;
        sb.AppendLine($"Project SRP active: {usingSRP}");
        sb.AppendLine();

        foreach (var folder in folders)
        {
            if (!AssetDatabase.IsValidFolder(folder))
                continue;

            string[] guids = AssetDatabase.FindAssets("t:prefab", new string[] { folder });
            foreach (var g in guids)
            {
                string path = AssetDatabase.GUIDToAssetPath(g);
                GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
                if (prefab == null) continue;
                prefabCount++;

                var renderers = new List<Renderer>();
                renderers.AddRange(prefab.GetComponentsInChildren<MeshRenderer>(true));
                renderers.AddRange(prefab.GetComponentsInChildren<SkinnedMeshRenderer>(true));

                foreach (var r in renderers)
                {
                    Material[] mats = r.sharedMaterials;
                    if (mats == null || mats.Length == 0)
                    {
                        sb.AppendLine($"[NO_MATERIALS] {path} -> Renderer: {r.gameObject.name}");
                        problemCount++;
                        continue;
                    }

                    for (int i = 0; i < mats.Length; i++)
                    {
                        Material m = mats[i];
                        if (m == null)
                        {
                            sb.AppendLine($"[MISSING_MATERIAL] {path} -> Renderer: {r.gameObject.name} Slot:{i}");
                            problemCount++;
                            continue;
                        }

                        string sname = m.shader != null ? m.shader.name : "<no-shader>";
                        bool isProblem = false;
                        var notes = new List<string>();

                        if (sname.Contains("Hidden/InternalError") || sname == "<no-shader>")
                        {
                            notes.Add("broken shader");
                            isProblem = true;
                        }

                        // SRP material in built-in project
                        if (!usingSRP && (sname.Contains("Universal Render Pipeline") || sname.Contains("URP") || sname.Contains("High Definition") || sname.Contains("HDRP") || sname.Contains("HDRenderPipeline")))
                        {
                            notes.Add("SRP shader in non-SRP project");
                            isProblem = true;
                        }

                        // Built-in Standard in SRP project
                        if (usingSRP && sname.Contains("Standard"))
                        {
                            notes.Add("Standard shader in SRP project (may render incorrectly)");
                            isProblem = true;
                        }

                        // Missing main texture
                        if (!m.HasProperty("_MainTex") || m.GetTexture("_MainTex") == null)
                        {
                            notes.Add("no _MainTex texture");
                        }

                        if (isProblem)
                        {
                            sb.AppendLine($"[PROBLEM] {path} -> Renderer: {r.gameObject.name} Slot:{i} Shader: {sname} Notes: {string.Join(", ", notes)}");
                            problemCount++;
                        }
                    }
                }
            }
        }

        sb.AppendLine();
        sb.AppendLine($"Scanned prefabs: {prefabCount}");
        sb.AppendLine($"Problems found: {problemCount}");

        string reportPath = Path.Combine(Application.dataPath, "../MaterialDiagnosticsReport.txt");
        try
        {
            File.WriteAllText(reportPath, sb.ToString());
            Debug.Log($"Material diagnostics complete. Report written to: {reportPath}");
        }
        catch (System.Exception ex)
        {
            Debug.LogError($"Failed to write material diagnostics report: {ex.Message}");
        }

        Debug.Log(sb.ToString());
    }
}
