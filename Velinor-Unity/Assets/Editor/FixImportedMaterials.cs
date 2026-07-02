using System.IO;
using System.Linq;
using System.Text;
using UnityEngine;
using UnityEditor;

#if UNITY_EDITOR
public static class FixImportedMaterials
{
    [MenuItem("Tools/Fix Imported Materials")]
    public static void FixMaterialsMenu()
    {
        FixImportedMaterialsInFolder("Assets/ImportedAssets");
    }

    [MenuItem("Tools/Fix Imported Materials/Run on Diagnosed Packs")]
    public static void FixOnDiagnosedPacks()
    {
        string[] folders = new string[] {
            "Assets/Kyle's Rock Pack",
            "Assets/DreamTree2",
            "Assets/Dry_Trees",
            "Assets/Medieval Props Pack 01",
            "Assets/EmbersStorm – Mediterranean Ruins Building Kit",
            "Assets/3 English Oak Set"
        };

        foreach (var f in folders)
        {
            if (AssetDatabase.IsValidFolder(f))
            {
                FixImportedMaterialsInFolder(f);
            }
            else
            {
                Debug.Log($"[FixImportedMaterials] Folder not found: {f}");
            }
        }
    }

    public static void FixImportedMaterialsInFolder(string rootFolder)
    {
        var report = new StringBuilder();
        report.AppendLine("Material Fix Report");
        report.AppendLine(System.DateTime.Now.ToString());
        report.AppendLine("Project SRP active: " + (UnityEngine.Rendering.GraphicsSettings.currentRenderPipeline != null));

        bool srpActive = UnityEngine.Rendering.GraphicsSettings.currentRenderPipeline != null;
        Shader urpLit = Shader.Find("Universal Render Pipeline/Lit");

        // 1) Convert materials using Built-in Standard to URP/Lit when SRP active
        var matGuids = AssetDatabase.FindAssets("t:Material", new[] { rootFolder });
        foreach (var mg in matGuids)
        {
            string mPath = AssetDatabase.GUIDToAssetPath(mg);
            var mat = AssetDatabase.LoadAssetAtPath<Material>(mPath);
            if (mat == null) continue;

            // collect existing texture references before changing shader
            Texture mainTex = null, bump = null, metallic = null, occ = null;
            if (mat.HasProperty("_MainTex")) mainTex = mat.GetTexture("_MainTex");
            if (mat.HasProperty("_BumpMap")) bump = mat.GetTexture("_BumpMap");
            if (mat.HasProperty("_MetallicGlossMap")) metallic = mat.GetTexture("_MetallicGlossMap");
            if (mat.HasProperty("_OcclusionMap")) occ = mat.GetTexture("_OcclusionMap");

            if (mat.shader != null && mat.shader.name == "Standard")
            {
                if (srpActive && urpLit != null)
                {
                    // switch shader and remap textures
                    mat.shader = urpLit;
                    if (mainTex != null)
                    {
                        if (mat.HasProperty("_BaseMap")) mat.SetTexture("_BaseMap", mainTex);
                        else if (mat.HasProperty("_MainTex")) mat.SetTexture("_MainTex", mainTex);
                    }
                    if (bump != null)
                    {
                        if (mat.HasProperty("_BumpMap")) mat.SetTexture("_BumpMap", bump);
                    }
                    if (metallic != null)
                    {
                        if (mat.HasProperty("_MetallicGlossMap")) mat.SetTexture("_MetallicGlossMap", metallic);
                        else if (mat.HasProperty("_MetallicMap")) mat.SetTexture("_MetallicMap", metallic);
                    }
                    if (occ != null && mat.HasProperty("_OcclusionMap")) mat.SetTexture("_OcclusionMap", occ);

                    EditorUtility.SetDirty(mat);
                    report.AppendLine($"[CONVERT] {mPath} -> shader set to '{mat.shader.name}'");
                    Debug.Log($"[FixImportedMaterials] Converted material shader: {mPath} -> {mat.shader.name}");
                }
                else
                {
                    report.AppendLine($"[SKIP-CONVERT] {mPath} (SRP inactive or URP shader not found)");
                }
            }

            // 2) For any material missing textures, search same folder for likely candidates
            bool changed = false;
            if ((mainTex == null || mainTex == Texture2D.whiteTexture) && TryAutoAssignTexture(mat, mPath, new[] { "_MainTex", "_BaseMap" }, new[] { "_albedo", "_diffuse" })) changed = true;
            if (bump == null && TryAutoAssignTexture(mat, mPath, new[] { "_BumpMap" }, new[] { "_normal", "_nrm" })) changed = true;
            if (metallic == null && TryAutoAssignTexture(mat, mPath, new[] { "_MetallicGlossMap", "_MetallicMap" }, new[] { "_metal", "_metallic" })) changed = true;
            if (occ == null && TryAutoAssignTexture(mat, mPath, new[] { "_OcclusionMap" }, new[] { "_mask", "_masks", "_ao" })) changed = true;

            if (changed)
            {
                EditorUtility.SetDirty(mat);
                report.AppendLine($"[PATCH] {mPath} - assigned missing textures");
                Debug.Log($"[FixImportedMaterials] Assigned missing textures for {mPath}");
            }
        }

        // 3) For prefabs whose MeshRenderer has default/broken materials, reassign from prefab's Materials folder
        var prefabGuids = AssetDatabase.FindAssets("t:Prefab", new[] { rootFolder });
        foreach (var pg in prefabGuids)
        {
            var pPath = AssetDatabase.GUIDToAssetPath(pg);
            var prefabRoot = PrefabUtility.LoadPrefabContents(pPath);
            bool prefabChanged = false;

            var renderers = prefabRoot.GetComponentsInChildren<Renderer>(true);
            foreach (var r in renderers)
            {
                var mats = r.sharedMaterials;
                bool anyDefault = false;
                for (int i = 0; i < mats.Length; i++)
                {
                    var mat = mats[i];
                    if (mat == null || mat.shader == null || mat.shader.name == "Hidden/InternalErrorShader" || mat.name.ToLower().Contains("default"))
                    {
                        anyDefault = true;
                        // try to find a matching material in the prefab folder
                        string folder = Path.GetDirectoryName(pPath);
                        var candidates = AssetDatabase.FindAssets("t:Material", new[] { folder })
                            .Select(g => AssetDatabase.GUIDToAssetPath(g))
                            .Select(p => new { path = p, name = Path.GetFileNameWithoutExtension(p) })
                            .ToList();

                        Material pick = null;
                        // try match by renderer or mesh name
                        string rendererName = r.gameObject.name.ToLower();
                        foreach (var c in candidates)
                        {
                            if (rendererName.Contains(c.name.ToLower()))
                            {
                                pick = AssetDatabase.LoadAssetAtPath<Material>(c.path);
                                break;
                            }
                        }

                        // fallback: use first material in a 'Materials' subfolder
                        if (pick == null && candidates.Count > 0)
                        {
                            var matEntry = candidates.FirstOrDefault(c => Path.GetDirectoryName(c.path).ToLower().EndsWith("materials"));
                            if (matEntry.path != null) pick = AssetDatabase.LoadAssetAtPath<Material>(matEntry.path);
                        }

                        if (pick != null)
                        {
                            mats[i] = pick;
                            prefabChanged = true;
                            report.AppendLine($"[REASSIGN] {pPath} - renderer '{r.gameObject.name}' slot {i} -> {AssetDatabase.GetAssetPath(pick)}");
                            Debug.Log($"[FixImportedMaterials] Reassigned material on {pPath} -> {AssetDatabase.GetAssetPath(pick)}");
                        }
                        else if (mat != null && (mat.shader == null || mat.shader.name.Contains("Hidden/InternalError")))
                        {
                            // Create a fallback material in an AutoFixedMaterials folder next to the prefab
                            string prefabFolder = folder;
                            string autofixFolder = Path.Combine(prefabFolder, "AutoFixedMaterials").Replace("\\", "/");
                            if (!AssetDatabase.IsValidFolder(autofixFolder))
                            {
                                // create folder under prefabFolder
                                AssetDatabase.CreateFolder(prefabFolder, "AutoFixedMaterials");
                            }

                            string baseName = Path.GetFileNameWithoutExtension(pPath);
                            string matAssetPath = Path.Combine(autofixFolder, baseName + "_slot" + i + ".mat").Replace("\\", "/");

                            Shader fallbackShader = srpActive ? Shader.Find("Universal Render Pipeline/Lit") : Shader.Find("Standard");
                            Material newMat = new Material(fallbackShader != null ? fallbackShader : Shader.Find("Standard"));

                            // attempt to assign textures from nearby textures
                            var texGuids = AssetDatabase.FindAssets("t:Texture2D", new[] { prefabFolder });
                            foreach (var tg in texGuids)
                            {
                                string tpath = AssetDatabase.GUIDToAssetPath(tg);
                                string tname = Path.GetFileNameWithoutExtension(tpath).ToLower();
                                var tex = AssetDatabase.LoadAssetAtPath<Texture>(tpath);
                                if (tex == null) continue;
                                if (tname.Contains("albedo") || tname.Contains("diffuse"))
                                {
                                    if (newMat.HasProperty("_MainTex")) newMat.SetTexture("_MainTex", tex);
                                    if (newMat.HasProperty("_BaseMap")) newMat.SetTexture("_BaseMap", tex);
                                }
                                else if (tname.Contains("normal") || tname.Contains("nrm"))
                                {
                                    if (newMat.HasProperty("_BumpMap")) newMat.SetTexture("_BumpMap", tex);
                                }
                                else if (tname.Contains("metal") || tname.Contains("metallic"))
                                {
                                    if (newMat.HasProperty("_MetallicGlossMap")) newMat.SetTexture("_MetallicGlossMap", tex);
                                }
                                else if (tname.Contains("mask") || tname.Contains("ao"))
                                {
                                    if (newMat.HasProperty("_OcclusionMap")) newMat.SetTexture("_OcclusionMap", tex);
                                }
                            }

                            AssetDatabase.CreateAsset(newMat, matAssetPath);
                            AssetDatabase.SaveAssets();
                            mats[i] = newMat;
                            prefabChanged = true;
                            report.AppendLine($"[AUTO-FALLBACK] {pPath} - renderer '{r.gameObject.name}' slot {i} -> {matAssetPath}");
                            Debug.Log($"[FixImportedMaterials] Created fallback material {matAssetPath} for {pPath}");
                        }
                    }
                }

                if (anyDefault)
                {
                    r.sharedMaterials = mats;
                }
            }

            if (prefabChanged)
            {
                PrefabUtility.SaveAsPrefabAsset(prefabRoot, pPath);
            }

            PrefabUtility.UnloadPrefabContents(prefabRoot);
        }

        AssetDatabase.SaveAssets();

        // write report file
        var outPath = Path.Combine(Application.dataPath, "..", "MaterialFixReport.txt");
        try
        {
            File.WriteAllText(outPath, report.ToString());
            Debug.Log($"Material fixes complete. Report written to: {outPath}");
        }
        catch (System.Exception ex)
        {
            Debug.LogWarning("Failed to write MaterialFixReport.txt: " + ex.Message);
        }
    }

    static bool TryAutoAssignTexture(Material mat, string matPath, string[] propsToTry, string[] namePatterns)
    {
        string folder = Path.GetDirectoryName(matPath);
        var texGuids = AssetDatabase.FindAssets("t:Texture2D", new[] { folder });
        var textures = texGuids.Select(g => AssetDatabase.GUIDToAssetPath(g)).ToList();
        foreach (var p in textures)
        {
            string name = Path.GetFileNameWithoutExtension(p).ToLower();
            foreach (var pat in namePatterns)
            {
                if (name.EndsWith(pat) || name.Contains(pat))
                {
                    var tex = AssetDatabase.LoadAssetAtPath<Texture>(p);
                    foreach (var prop in propsToTry)
                    {
                        if (mat.HasProperty(prop))
                        {
                            mat.SetTexture(prop, tex);
                            return true;
                        }
                    }
                }
            }
        }

        // no candidate found
        return false;
    }
}
#endif
